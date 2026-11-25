#!/usr/bin/env python3
"""Fetch drawn (and replacement) article HTML with TLS verification on.

Paywalled, 404, or non-article URLs are replaced with the next unused URL
from the same outlet-week stratum in the original sort order. Certificate
and TLS errors are logged to data/collector_errors.csv and the run continues.
Bodies are written under data/fetched_articles/ (gitignored). The committed
output is a fetch-status table without article bodies.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "scripts"))
import collect
import sample_neutral_random as sampler

UA = collect.DEFAULT_UA
FETCHED = DATA / "fetched_articles" / "neutral_random_v1"
# 010 phase-2 trio status; a bare run must not overwrite the 009 pilot table.
DEFAULT_OUT = DATA / "sampling" / "neutral_random_v1_fetch_status_phase2.csv"

STATUS_FIELDS = [
    "algorithm_id",
    "seed",
    "outlet_id",
    "iso_week",
    "draw_index",
    "url",
    "original_url",
    "replacement_depth",
    "http_status",
    "final_url",
    "access",
    "headline",
    "byline",
    "published_at",
    "date_source",
    "body_chars",
    "fetch_error",
    "status",
    "fetched_at_sast",
    "text_relpath",
]


class HTMLText(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "template", "nav", "footer", "form"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self._in_title = False
        self._skip = 0
        self._body_depth = 0
        self.body_parts: list[str] = []
        self.byline_parts: list[str] = []
        self._in_byline = 0
        self.og: dict[str, str] = {}
        self._current_meta: dict[str, str] = {}

    def handle_starttag(self, tag, attrs):
        attrs = {k.lower(): (v or "") for k, v in attrs}
        if tag == "title":
            self._in_title = True
        if tag in self.SKIP:
            self._skip += 1
            return
        if self._skip:
            return
        if tag == "meta":
            key = (attrs.get("property") or attrs.get("name") or "").lower()
            if key and attrs.get("content"):
                self.og[key] = attrs["content"]
        cls = attrs.get("class", "").lower()
        if any(s in cls for s in ("article__author", "js-article-byline", "author-name", "entry-author", "byline")):
            self._in_byline += 1
        if tag in {"article"} or any(
            s in cls
            for s in (
                "entry-content",
                "article__body",
                "article__content",
                "article-content",
                "post-content",
                "story-body",
                "td-post-content",
            )
        ):
            self._body_depth += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in self.SKIP and self._skip:
            self._skip -= 1
            return
        if self._in_byline and tag in {"div", "span", "p", "a", "time", "h4", "h5"}:
            self._in_byline = max(0, self._in_byline - 1)
        if self._body_depth and tag in {"article", "div", "section"}:
            # conservative: only decrement on likely wrappers; keep text flowing
            pass

    def handle_data(self, data):
        if self._in_title:
            self.title_parts.append(data)
        if self._skip:
            return
        text = " ".join(data.split())
        if not text:
            return
        if self._in_byline:
            self.byline_parts.append(text)
        if self._body_depth:
            self.body_parts.append(text)


def visible_text(html: str) -> tuple[str, str, str, dict]:
    p = HTMLText()
    try:
        p.feed(html)
        p.close()
    except Exception:
        pass
    title = " ".join(" ".join(p.title_parts).split())
    byline = " ".join(" ".join(p.byline_parts).split())
    body = " ".join(p.body_parts)
    body = re.sub(r"\s+", " ", body).strip()
    return title, byline, body, p.og


def jsonld_articles(html: str) -> list[dict]:
    out = []
    for m in re.finditer(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.S | re.I,
    ):
        raw = m.group(1).strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        stack = [data]
        while stack:
            o = stack.pop()
            if isinstance(o, dict):
                typ = o.get("@type")
                types = typ if isinstance(typ, list) else [typ]
                types = [t for t in types if t]
                if any(t in {"NewsArticle", "Article", "ReportageNewsArticle", "OpinionNewsArticle"} for t in types) or o.get("articleBody") or "isAccessibleForFree" in o:
                    out.append(o)
                stack.extend(o.values())
            elif isinstance(o, list):
                stack.extend(o)
    return out


def is_free_access(html: str, body: str, final_url: str) -> tuple[str, str]:
    """Return (access, reason). access is full_text_curl or paywalled or not_article."""
    path = (urlparse(final_url).path or "").lower()
    if any(s in path for s in ("/tag/", "/author/", "/category/", "/page/", "/shop/", "/product")):
        return "not_article", "path looks like a taxonomy or shop page"
    ld = jsonld_articles(html)
    free_flags = []
    ld_body = 0
    for o in ld:
        if "isAccessibleForFree" in o:
            val = o.get("isAccessibleForFree")
            if isinstance(val, bool):
                free_flags.append(val)
            elif isinstance(val, str):
                free_flags.append(val.strip().lower() == "true")
        if o.get("articleBody"):
            ld_body = max(ld_body, len(o["articleBody"]))
    # Schema.org may also set a hasPart element flag; prefer the top-level
    # NewsArticle.isAccessibleForFree when present.
    if free_flags and not any(free_flags):
        return "paywalled", "JSON-LD isAccessibleForFree=false"
    if re.search(r'isAccessibleForFree["\s:=]+false', html, re.I) and not any(free_flags):
        return "paywalled", "isAccessibleForFree token is false"
    text_len = max(len(body), ld_body)
    low = html.lower()
    if text_len < 500 and any(
        s in low
        for s in (
            "subscribe to read",
            "subscribers only",
            "become a subscriber",
            "this article is for subscribers",
            "article__body--locked",
        )
    ):
        return "paywalled", f"short body ({text_len} chars) with subscribe/lock markers"
    if text_len < 400:
        return "too_short", f"extracted body only {text_len} characters"
    return "full_text_curl", f"extracted {text_len} characters"


def headline_of(html: str, title: str, og: dict, fallback: str = "") -> str:
    for o in jsonld_articles(html):
        if o.get("headline"):
            return str(o["headline"]).strip()
    if og.get("og:title"):
        return og["og:title"].strip()
    t = re.sub(r"\s+[–—|-]\s+(News24|Daily Investor|Newsday|Daily Maverick|GroundUp|The Citizen)\s*$", "", title, flags=re.I)
    return (t or fallback or title).strip()


def byline_of(html: str, byline: str, og: dict) -> str:
    for o in jsonld_articles(html):
        author = o.get("author")
        names = []
        for a in author if isinstance(author, list) else [author]:
            if isinstance(a, dict) and a.get("name"):
                names.append(str(a["name"]).strip())
            elif isinstance(a, str):
                names.append(a.strip())
        if names:
            return ", ".join(names)
    if og.get("author"):
        return og["author"].strip()
    # tidy raw byline
    b = re.sub(r"\s+", " ", byline or "").strip()
    b = re.sub(r"^(By|Written by)\s+", "", b, flags=re.I)
    return b[:200]


def published_of(html: str, fallback: str) -> str:
    for o in jsonld_articles(html):
        raw = o.get("datePublished") or o.get("dateCreated")
        if raw:
            parsed = collect.parse_any_date(str(raw))
            if parsed:
                return parsed.astimezone(collect.SAST).strftime("%Y-%m-%dT%H:%M:%S%z")
    parsed = collect.parse_any_date(fallback) if fallback else None
    return parsed.astimezone(collect.SAST).strftime("%Y-%m-%dT%H:%M:%S%z") if parsed else fallback


def remainders_by_stratum(candidates, rule, paywalled, drawn_urls: set[str]):
    """Unused candidates per (outlet, iso_week) in the original sort order."""
    start = __import__("datetime").date.fromisoformat(rule["window_start"])
    end = __import__("datetime").date.fromisoformat(rule["window_end"])
    pool = []
    for row in candidates:
        url = sampler._norm(row.get("url") or "")
        if not url or url in paywalled:
            continue
        if sampler.contains_private_name(row, sampler.load_private_name_terms()):
            continue
        d = sampler.row_date(row)
        if d is None or d < start or d > end:
            continue
        item = dict(row)
        item["_date"] = d.isoformat()
        item["_week"] = sampler.iso_week_key(d)
        item["_url_norm"] = url
        pool.append(item)
    out = {}
    for oid in sorted({r["outlet_id"] for r in pool}):
        for week in sorted({r["_week"] for r in pool if r["outlet_id"] == oid}):
            stratum = [
                r for r in pool if r["outlet_id"] == oid and r["_week"] == week
            ]
            stratum.sort(key=lambda r: ((r.get("published_at") or ""), r["_url_norm"]))
            unused = [r for r in stratum if r["_url_norm"] not in drawn_urls]
            out[(oid, week)] = unused
    return out


def slug_id(url: str) -> str:
    path = urlparse(url).path.rstrip("/").split("/")[-1] or "item"
    path = re.sub(r"[^a-zA-Z0-9-]+", "-", path).strip("-").lower()
    return path[:80] or "item"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rule", default=str(DATA / "sampling" / "neutral_random_v1.json"))
    parser.add_argument("--candidates", default=str(DATA / "sampling" / "neutral_random_candidates_v1.csv"))
    parser.add_argument("--draw", default=str(DATA / "sampling" / "neutral_random_draw_v1.csv"))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument(
        "--outlets",
        required=True,
        help="Comma-separated outlet ids. Required so a bare run cannot fetch or overwrite a locked status table.",
    )
    parser.add_argument("--errors", default=str(DATA / "collector_errors.csv"))
    parser.add_argument("--run-id", default="")
    parser.add_argument("--delay", type=float, default=0.2)
    parser.add_argument("--max-replacements", type=int, default=15)
    args = parser.parse_args(argv)

    rule = json.loads(Path(args.rule).read_text(encoding="utf-8"))
    candidates = sampler.load_candidates(Path(args.candidates))
    draw_rows = list(csv.DictReader(Path(args.draw).open(encoding="utf-8")))
    outlets = {s.strip() for s in args.outlets.split(",") if s.strip()}
    draw_rows = [r for r in draw_rows if r["outlet_id"] in outlets]
    paywalled = sampler.load_paywall_urls()
    drawn_norm = {sampler._norm(r["url"]) for r in draw_rows}
    unused = remainders_by_stratum(candidates, rule, paywalled, drawn_norm)
    all_attempts = []

    run_id = args.run_id or f"fetch-draw-{collect.fmt_sast()}"
    errors = collect.ErrorLog(Path(args.errors), run_id)
    collector = collect.Collector(
        json.loads((DATA / "collectors.json").read_text(encoding="utf-8")),
        errors,
        delay_s=args.delay,
    )
    FETCHED.mkdir(parents=True, exist_ok=True)

    status_rows = []
    used_extra: set[str] = set()

    def fetch_one(url: str, outlet_id: str) -> dict:
        result = {
            "http_status": "",
            "final_url": url,
            "access": "",
            "headline": "",
            "byline": "",
            "published_at": "",
            "body_chars": 0,
            "fetch_error": "",
            "status": "",
            "text_relpath": "",
            "html": "",
            "body": "",
        }
        raw = collector.fetch_bytes(url, outlet_id=outlet_id)
        if raw is None:
            result["access"] = "fetch_error"
            result["fetch_error"] = "logged in collector_errors.csv"
            result["status"] = "error"
            return result
        # charset
        try:
            html = raw.decode("utf-8")
        except UnicodeDecodeError:
            html = raw.decode("utf-8", "replace")
        title, byline_raw, body, og = visible_text(html)
        # prefer JSON-LD body when longer
        for o in jsonld_articles(html):
            if o.get("articleBody") and len(o["articleBody"]) > len(body):
                body = re.sub(r"\s+", " ", o["articleBody"]).strip()
        access, reason = is_free_access(html, body, url)
        result["http_status"] = "200"
        result["final_url"] = url
        result["access"] = access
        result["headline"] = headline_of(html, title, og)
        result["byline"] = byline_of(html, byline_raw, og)
        result["published_at"] = published_of(html, "")
        result["body_chars"] = len(body)
        result["html"] = html
        result["body"] = body
        if access == "full_text_curl":
            result["status"] = "fetched"
        elif access == "paywalled":
            result["status"] = "paywalled"
            result["fetch_error"] = reason
        else:
            result["status"] = access
            result["fetch_error"] = reason
        return result

    for row in draw_rows:
        oid, week, idx = row["outlet_id"], row["iso_week"], row["draw_index"]
        original = row["url"]
        current = original
        depth = 0
        chosen = None
        attempted = []
        while True:
            fr = fetch_one(current, oid)
            attempted.append((current, fr["status"], fr.get("fetch_error") or ""))
            if fr["status"] == "fetched":
                chosen = (current, fr, depth)
                break
            # replace
            pool = unused.get((oid, week), [])
            nxt = None
            while pool:
                cand = pool.pop(0)
                nu = cand["_url_norm"]
                if nu in used_extra or nu in drawn_norm:
                    continue
                nxt = cand
                break
            unused[(oid, week)] = pool
            if nxt is None or depth >= args.max_replacements:
                chosen = (current, fr, depth)
                break
            used_extra.add(nxt["_url_norm"])
            current = nxt["url"]
            depth += 1
        url, fr, depth = chosen
        for attempt_index, (aurl, astatus, aerr) in enumerate(attempted):
            accepted = aurl == url and astatus == "fetched"
            all_attempts.append({
                "algorithm_id": rule["algorithm_id"],
                "outlet_id": oid,
                "iso_week": week,
                "draw_index": idx,
                "attempt_index": attempt_index,
                "url": aurl,
                "outcome": "accepted" if accepted else "rejected",
                "reason": (fr.get("access") if accepted else (aerr or astatus or "rejected")),
                "replacement_depth_final": depth,
            })
        rel = ""
        if fr["status"] == "fetched" and fr["body"]:
            out_dir = FETCHED / oid
            out_dir.mkdir(parents=True, exist_ok=True)
            name = f"{week}_{idx}_{slug_id(url)}"
            (out_dir / f"{name}.txt").write_text(
                f"URL: {url}\nHEADLINE: {fr['headline']}\nBYLINE: {fr['byline']}\n"
                f"PUBLISHED_AT: {fr['published_at']}\nFETCHED_AT: {collect.fmt_sast()}\n"
                f"ACCESS: {fr['access']}\nBODY_CHARS: {fr['body_chars']}\n\n{fr['body']}\n",
                encoding="utf-8",
            )
            (out_dir / f"{name}.html").write_text(fr["html"], encoding="utf-8")
            rel = str((out_dir / f"{name}.txt").relative_to(DATA))
        rec = {
            "algorithm_id": rule["algorithm_id"],
            "seed": rule["seed"],
            "outlet_id": oid,
            "iso_week": week,
            "draw_index": idx,
            "url": url,
            "original_url": original if url != original else "",
            "replacement_depth": depth,
            "http_status": fr["http_status"],
            "final_url": fr["final_url"],
            "access": fr["access"],
            "headline": fr["headline"],
            "byline": fr["byline"],
            "published_at": fr["published_at"] or row.get("published_at") or "",
            "date_source": row.get("date_source") or "",
            "body_chars": fr["body_chars"],
            "fetch_error": fr.get("fetch_error") or "",
            "status": fr["status"],
            "fetched_at_sast": collect.fmt_sast(),
            "text_relpath": rel,
        }
        status_rows.append(rec)
        flag = "OK" if fr["status"] == "fetched" else fr["status"].upper()
        print(
            f"[{flag}] {oid} {week} #{idx} depth={depth} chars={fr['body_chars']} {url}",
            file=sys.stderr,
        )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=STATUS_FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(status_rows)
    ok = sum(1 for r in status_rows if r["status"] == "fetched")
    pw = sum(1 for r in status_rows if r["status"] == "paywalled")
    print(f"wrote {len(status_rows)} rows ({ok} fetched, {pw} still paywalled) to {out_path}", file=sys.stderr)
    attempts_path = Path(args.out).with_name(Path(args.out).stem.replace("_fetch_status", "") + "_replacement_attempts.csv")
    if "fetch_status" in Path(args.out).name:
        attempts_path = Path(args.out).with_name(Path(args.out).name.replace("fetch_status", "replacement_attempts"))
    with attempts_path.open("w", encoding="utf-8", newline="") as fh:
        fields = ["algorithm_id", "outlet_id", "iso_week", "draw_index", "attempt_index", "url", "outcome", "reason", "replacement_depth_final"]
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(all_attempts)
    print(f"wrote {len(all_attempts)} replacement attempts to {attempts_path}", file=sys.stderr)
    if errors.count:
        print(f"{errors.count} collector error(s) logged; exiting non-zero", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
