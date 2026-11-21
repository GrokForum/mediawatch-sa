#!/usr/bin/env python3
"""MediaWatch SA static site generator (RFC-CHG-MW-002, DEV only).

Plain Python 3 standard library; no third-party packages, no templates engine,
no JavaScript, no external assets. Reads the committed data/ files and writes a
static drill-down site into _site/ (gitignored):

    publication > writer/editor > article or public post > finding (evidence)

Hard rules enforced here (and re-checked by tests/test_site.py):
  * Primary meter only: FOR/AGAINST named actors. The secondary left/right
    meter is never read or rendered (hidden until the owner's GO).
  * No paywalled content: findings tied to a paywalled piece are excluded from
    pages and scores (owner rule, 17 Nov 2026). See data/paywall_exclusions.csv.
  * Fact labels only: Proven, Established, Alleged, Disputed, Not established.
  * Thresholds: score only when n >= 10; 5-9 provisional; under 5 findings only.
  * noindex on every page plus robots.txt Disallow: / (until a separate GO).
  * Internal working fields (evidence_notes, coder, credit, recovery URLs,
    og/standfirst teasers, post metrics, X user ids) are never rendered.

Usage: python scripts/build_site.py [--out _site]
"""
import argparse
import csv
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SITE_SRC = ROOT / "site"

ALLOWED_LABELS = ("Proven", "Established", "Alleged", "Disputed", "Not established")
PILOT = ("news24", "daily_investor", "newsday")
# Error-watch outlets logged outside the scored three-outlet pilot (findings only until n allows a score).
WATCH = ("iol", "ewn")
FINDINGS_FILES = {
    "news24": "news24_pilot_findings.json",
    "daily_investor": "dailyinvestor_pilot_findings.json",
    "newsday": "newsday_pilot_findings.json",
    "iol": "iol_watch_findings.json",
    "ewn": "ewn_watch_findings.json",
}
FULL_N, PROVISIONAL_N = 10, 5
FREE_ACCESS = {"full_text_webfetch", "full_text_curl", "partner_content_meta"}
DRIVER_NAMES = {
    "loaded_label": "Loaded label",
    "one_sided_sourcing": "One-sided sourcing",
    "missing_right_of_reply": "Missing right of reply",
    "omission": "Omission",
    "framing": "Framing",
    "headline_body_gap": "Headline vs body gap",
    "factual_error": "Factual error",
    "correction": "Correction",
}
FRAME_NOTES = {
    "keyword": "found by actor/term search",
    "neutral_random": "pre-registered seeded draw (neutral_random_v1: 2 URLs per outlet per ISO week)",
    "legacy_neutral": "older mid-week or informal 'neutral' coding, not drawn with neutral_random_v1",
    "counter_pull": "deliberate search for the opposite direction",
    "external_seed": "re-verified outside seed",
    "purposive": "judgement sample, no pre-registered random rule (frame pending owner acceptance)",
}
# METHODOLOGY 8a option (b): weight locked neutral_random highest.
# legacy_neutral is not treated as the locked v1 frame.
ROLLUP_B_WEIGHTS = {
    "neutral_random": 4.0,
    "counter_pull": 2.0,
    "keyword": 1.0,
    "purposive": 1.0,
    "external_seed": 1.0,
    "legacy_neutral": 1.0,
}
ACCESS_NOTES = {
    "full_text_webfetch": "Free to read: full text was publicly available when coded.",
    "full_text_curl": "Free to read: full text was publicly available when coded (no login).",
    "partner_content_meta": "Labelled partner/brand content; not behind a reader paywall.",
}
STATUS_NOTES = {
    "bias": "Bias finding; counts in the score.",
    "borderline": "Borderline bias finding (close to the accountability gate); counts in the score.",
    "control": "Control / contrast observation retained in the sample; counts in the score as coded.",
    "accountability_exempt": "Sourced accountability reporting; kept for audit, not counted in the score.",
}


class BuildError(Exception):
    pass


# Internal reviewer/coder notes that slipped into a few steelman strings
# (e.g. "→ Cavus: unspecified (AfriMAGA)"). Display-only removal; the data
# files are not changed (a data clean-up is a separate change).
_INTERNAL_NOTE = re.compile(r"\s*(?:;|→|->)\s*Cavus\b:?[^.;]*[.;]?", re.IGNORECASE)


def public_text(s):
    out, hits = _INTERNAL_NOTE.subn("", s or "")
    out = out.strip()
    if hits and out and out[-1] not in ".!?)\"'’”":
        out += "."
    return out


# ---------------------------------------------------------------- loading
def read_csv(name):
    with open(DATA / name, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def official_drivers():
    schema = json.loads((DATA / "schema.json").read_text(encoding="utf-8"))
    return set(schema["properties"]["findings"]["items"]["properties"]["driver"]["enum"])


def norm_url(u):
    return (u or "").strip().rstrip("/").lower()


def detect_paywalled(doc, register_urls):
    """Return {finding_id: reason} for findings that rest on a paywalled piece.

    A finding is excluded when the finding itself records an access limit, or
    its article is paywalled at source (access label, access note, or listed in
    data/paywall_register.csv), even if a body or teaser was later recovered.
    """
    arts = {a["id"]: a for a in doc.get("articles", [])}
    out = {}
    for f in doc["findings"]:
        reasons = []
        if f.get("access_limit"):
            reasons.append(f"finding access_limit={f['access_limit']}")
        a = arts.get(f.get("article_id"))
        if a:
            acc, note = a.get("access"), (a.get("access_note") or "")
            free_note = "isaccessibleforfree=true" in note.lower()
            if acc and acc not in FREE_ACCESS and not free_note:
                reasons.append(f"article access={acc}")
            if "paywall" in note.lower():
                reasons.append("article access_note mentions paywall")
            if norm_url(a.get("url")) in register_urls and not free_note:
                reasons.append("article listed in paywall_register.csv")
        if norm_url(f.get("url")) in register_urls and f.get("article_id"):
            reasons.append("finding URL listed in paywall_register.csv")
        if reasons:
            out[f["id"]] = "; ".join(dict.fromkeys(reasons))
    return out


def load():
    pubs = {r["id"]: r for r in read_csv("publications.csv")}
    people = {r["id"]: r for r in read_csv("people.csv")}
    register_urls = {norm_url(r["url"]) for r in read_csv("paywall_register.csv")}
    listed = {r["finding_id"]: r for r in read_csv("paywall_exclusions.csv")}
    docs = {p: json.loads((DATA / fn).read_text(encoding="utf-8")) for p, fn in FINDINGS_FILES.items()}
    detected = {}
    for p, doc in docs.items():
        detected.update(detect_paywalled(doc, register_urls))
    all_ids = {f["id"] for d in docs.values() for f in d["findings"]}
    unknown = set(listed) - all_ids
    if unknown:
        raise BuildError(f"paywall_exclusions.csv lists unknown findings: {sorted(unknown)}")
    excluded = set(detected) | set(listed)
    return pubs, people, docs, excluded, detected, listed


# ---------------------------------------------------------------- scoring
def flag_for(n):
    if n >= FULL_N:
        return "full"
    if n >= PROVISIONAL_N:
        return "provisional"
    return "findings_only"


def in_score(f):
    return f.get("accountability_status") != "accountability_exempt" and f.get("signed_score") is not None


def item_key(f):
    return f.get("article_id") or f.get("public_post_id") or f["id"]


def scorecards(findings, person_level=False, rollup="unweighted"):
    """Primary FOR/AGAINST scorecards per actor.

    Publication level (METHODOLOGY 6.3): mean of finding signed scores.
    Person level (6.2): mean of item-level means; suppressed when every
    counted finding is keyword-frame (8a rule 2).
    rollup='b' applies METHODOLOGY 8a option (b): weight locked
    neutral_random highest. legacy_neutral does not receive that weight.
    """
    by_actor = defaultdict(list)
    for f in findings:
        by_actor[f["actor"]].append(f)
    rows = []
    for actor, fs in by_actor.items():
        counted = [f for f in fs if in_score(f)]
        n = len(counted)
        flag = flag_for(n)
        mean = None
        if counted:
            if person_level:
                items = defaultdict(list)
                for f in counted:
                    items[item_key(f)].append(float(f["signed_score"]))
                means = [sum(v) / len(v) for v in items.values()]
                mean = sum(means) / len(means)
            else:
                if rollup == "b":
                    weights = [
                        ROLLUP_B_WEIGHTS.get(f.get("sample_frame") or "", 1.0)
                        for f in counted
                    ]
                    total_w = sum(weights)
                    mean = sum(
                        float(f["signed_score"]) * w for f, w in zip(counted, weights)
                    ) / total_w
                else:
                    mean = sum(float(f["signed_score"]) for f in counted) / n
        frames = Counter(f.get("sample_frame") or "unrecorded" for f in counted)
        suppressed = None
        if person_level and counted and set(frames) <= {"keyword"}:
            suppressed = "keyword-only sample (METHODOLOGY 8a rule 2)"
        shown = None if (flag == "findings_only" or suppressed) else round(mean, 2)
        rows.append({
            "actor": actor,
            "for": sum(1 for f in fs if f["direction"] == "FOR"),
            "against": sum(1 for f in fs if f["direction"] == "AGAINST"),
            "shown_findings": len(fs),
            "n": n,
            "flag": flag,
            "mean": mean,
            "score": shown,
            "suppressed": suppressed,
            "frames": frames,
            "pending_drivers": sum(1 for f in fs if f.get("_driver_pending")),
        })
    rows.sort(key=lambda r: (-r["n"], r["actor"].lower()))
    return rows


# ---------------------------------------------------------------- html helpers
def e(s):
    return html.escape("" if s is None else str(s), quote=True)


def slug(s):
    return re.sub(r"[^A-Za-z0-9_-]+", "-", str(s)).strip("-")


def page(title, body, depth, crumbs=(), build_meta=None):
    up = "../" * depth
    nav = (f'<nav><a href="{up}index.html">Publications</a><a href="{up}method/index.html">Method</a>'
           f'<a href="{up}coverage/index.html">Coverage plan</a>'
           f'<a href="{up}corrections/index.html">Corrections &amp; right of reply</a>'
           f'<a href="{up}privacy/index.html">Privacy</a></nav>')
    crumb_html = ""
    if crumbs:
        parts = [f'<a href="{up}{href}">{e(label)}</a>' if href else e(label) for label, href in crumbs]
        crumb_html = '<p class="crumbs">' + " &rsaquo; ".join(parts) + "</p>"
    stamp = ""
    if build_meta:
        stamp = (
            f'<p class="build-stamp">Build <code>{e(build_meta["git_sha_short"])}</code>'
            f' · {e(build_meta["built_at_sast"])} Africa/Johannesburg'
            f' · data date {e(build_meta["data_date"])}'
            f' · <a href="{up}manifest.json">manifest.json</a></p>'
        )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="referrer" content="no-referrer">
<title>{e(title)} | MediaWatch SA (draft)</title>
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body>
<header class="site"><div class="wrap"><a class="brand" href="{up}index.html">MediaWatch SA</a>{nav}</div></header>
<main class="wrap">
<p class="draft"><strong>Draft preview (DEV).</strong> Pilot data, not yet reviewed for publication. Scores are provisional and may change.</p>
{crumb_html}
{body}
</main>
<footer><div class="wrap">MediaWatch SA: bias FOR or AGAINST named actors, with the exact line, the source link and both sides' strongest case for every finding. Only free public content is judged; paywalled pieces are never scored.{stamp}
<p class="footer-nav"><a href="{up}privacy/index.html">Privacy</a></p></div></footer>
</body>
</html>
"""


def badge(flag):
    label = {"full": "score", "provisional": "provisional", "findings_only": "findings only"}[flag]
    return f'<span class="badge {flag}">{label}</span>'


def fmt_score(x):
    return f"{x:+.2f}"


def frames_text(frames):
    return ", ".join(f"{k} {v}" for k, v in sorted(frames.items())) or "-"


def scorecard_table(rows, level):
    if not rows:
        return '<p class="note">No findings shown.</p>'
    out = ['<table class="scorecard"><thead><tr><th>Named actor</th><th class="num">FOR</th>'
           '<th class="num">AGAINST</th><th class="num">n (counted)</th><th class="num">Score (&minus;2&hellip;+2)</th>'
           '<th>Status</th><th>Sample frames</th></tr></thead><tbody>']
    for r in rows:
        score_cell = fmt_score(r["score"]) if r["score"] is not None else "&ndash;"
        status = badge(r["flag"])
        if r["suppressed"]:
            status += f' <span class="badge findings_only">suppressed: {e(r["suppressed"])}</span>'
        if r["pending_drivers"]:
            status += f' <span class="badge pending">{r["pending_drivers"]} driver name(s) pending owner decision</span>'
        data_score = "" if r["score"] is None else f"{r['score']:.2f}"
        out.append(
            f'<tr class="score-row" data-level="{level}" data-actor="{e(r["actor"])}" data-n="{r["n"]}" '
            f'data-flag="{r["flag"]}" data-score="{data_score}" data-suppressed="{1 if r["suppressed"] else 0}">'
            f'<td>{e(r["actor"])}</td><td class="num">{r["for"]}</td><td class="num">{r["against"]}</td>'
            f'<td class="num">{r["n"]}</td><td class="num">{score_cell}</td><td>{status}</td>'
            f'<td>{e(frames_text(r["frames"]))}</td></tr>')
    out.append("</tbody></table>")
    out.append('<p class="note">Score shown only when n &ge; 10; 5&ndash;9 is provisional; under 5 shows findings only. '
               'Accountability-exempt findings are listed but not counted.</p>')
    return "\n".join(out)


def driver_html(f):
    d = f["driver"]
    if f.get("_driver_pending"):
        return (f'<code>{e(d)}</code> <span class="badge pending">driver name pending owner decision</span>')
    return f'{e(DRIVER_NAMES.get(d, d))} <code>{e(d)}</code>'


def finding_row(f, up):
    return (f'<tr><td><a href="{up}f/{slug(f["id"])}/index.html">{e(f["id"])}</a></td>'
            f'<td>{e(f["actor"])}</td><td class="{e(f["direction"])}">{e(f["direction"])}</td>'
            f'<td>{driver_html(f)}</td><td>{e(f["fact_label"])}</td>'
            f'<td>&ldquo;{e(trim(f["quote"], 140))}&rdquo;</td></tr>')


def findings_table(fs, up):
    head = ('<table><thead><tr><th>Finding</th><th>Actor</th><th>Direction</th><th>Driver</th>'
            '<th>Fact label</th><th>Quote</th></tr></thead><tbody>')
    return head + "\n".join(finding_row(f, up) for f in fs) + "</tbody></table>"


def trim(s, n):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def date_of(obj, *keys):
    for k in keys:
        v = obj.get(k)
        if v:
            return str(v)[:16].replace("T", " ") if "T" in str(v) else str(v)
    return ""


SAST = ZoneInfo("Africa/Johannesburg")
DATA_WINDOW = {"start": "2026-05-01", "end": "2026-10-31", "label": "May–October 2026"}
# Committed files the generator reads. Paths are relative to the repo root.
MANIFEST_INPUTS = (
    "data/publications.csv",
    "data/people.csv",
    "data/paywall_register.csv",
    "data/paywall_exclusions.csv",
    "data/schema.json",
    "data/news24_pilot_findings.json",
    "data/dailyinvestor_pilot_findings.json",
    "data/newsday_pilot_findings.json",
)


def now_sast():
    return datetime.now(SAST)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_identity():
    """Git SHA and Actions run id for the public manifest.

    SHA comes from MEDIAWATCH_GIT_SHA or GITHUB_SHA, else `git rev-parse HEAD`.
    Run id comes from MEDIAWATCH_RUN_ID or GITHUB_RUN_ID, else JSON null (local build).
    """
    sha = (os.environ.get("MEDIAWATCH_GIT_SHA") or os.environ.get("GITHUB_SHA") or "").strip()
    if not sha:
        try:
            r = subprocess.run(
                ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                capture_output=True, text=True, timeout=10,
            )
            if r.returncode == 0:
                sha = r.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            sha = ""
    run_id = (os.environ.get("MEDIAWATCH_RUN_ID") or os.environ.get("GITHUB_RUN_ID") or "").strip() or None
    return sha, run_id


def to_sast_date(value):
    """Return YYYY-MM-DD in Africa/Johannesburg, or None if the value cannot be parsed."""
    if not value:
        return None
    s = str(value).strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        try:
            return datetime.strptime(s[:10], "%Y-%m-%d").date().isoformat()
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=SAST)
    return dt.astimezone(SAST).date().isoformat()


def https_urls(text):
    """Extract unique https:// URLs from a semicolon-separated source field."""
    found = []
    for part in re.split(r"\s*;\s*", text or ""):
        m = re.search(r"https://[^\s;]+", part or "")
        if m:
            url = m.group(0).rstrip(".,)")
            if url not in found:
                found.append(url)
    return found



def editor_sources(pub):
    urls = https_urls(pub.get("editor_source_url") or "")
    if not urls:
        return ""
    links = " ".join(
        f'<a class="source-link" href="{e(u)}" rel="nofollow noopener">{e(u)}</a>'
        for u in urls
    )
    return f' <span class="note">Source: {links}</span>'



# ---------------------------------------------------------------- build
def build(out_dir):
    pubs, people, docs, excluded, detected, listed = load()
    drivers_ok = official_drivers()

    items = {}       # key -> item dict
    findings = []    # rendered findings
    excluded_counts = Counter()
    for pid in PILOT + WATCH:
        doc = docs[pid]
        arts = {a["id"]: a for a in doc.get("articles", [])}
        posts = {p["id"]: p for p in doc.get("public_posts", [])}
        for f in doc["findings"]:
            if f["id"] in excluded:
                excluded_counts[pid] += 1
                continue
            f = dict(f)
            f["publication_id"] = f.get("publication_id") or pid
            for field in ("quote", "url", "steelman_for", "steelman_against", "fact_label", "actor", "direction"):
                if not (f.get(field) or "").strip():
                    raise BuildError(f"{f['id']}: missing {field}")
            if f["fact_label"] not in ALLOWED_LABELS:
                raise BuildError(f"{f['id']}: fact label {f['fact_label']!r} not allowed")
            if f["direction"] not in ("FOR", "AGAINST"):
                raise BuildError(f"{f['id']}: direction {f['direction']!r}")
            f["_driver_pending"] = f["driver"] not in drivers_ok
            if f.get("article_id") and f["article_id"] in arts:
                a = arts[f["article_id"]]
                key = ("a", a["id"])
                items.setdefault(key, {
                    "kind": "article", "id": a["id"], "pub": pid,
                    "title": a.get("headline") or a.get("title") or a["id"],
                    "url": a["url"], "byline": a.get("byline") or "",
                    "person_id": a.get("person_id"),
                    "date": date_of(a, "published_at_sast", "published_at"),
                    "frame": a.get("sample_frame"),
                    "access": ACCESS_NOTES.get(a.get("access"), "Free to read when coded."),
                    "findings": []})
            elif f.get("public_post_id") and f["public_post_id"] in posts:
                p = posts[f["public_post_id"]]
                key = ("x", p["id"])
                items.setdefault(key, {
                    "kind": "post", "id": p["id"], "pub": pid,
                    "title": f"Public post on {p.get('platform', 'x').upper()}",
                    "url": p["url"], "byline": "", "person_id": p.get("person_id"),
                    "date": date_of(p, "posted_at_sast", "posted_at"),
                    "frame": p.get("sample_frame"),
                    "access": "Public post: free to view.", "findings": []})
            else:
                key = ("f", f["id"])
                items.setdefault(key, {
                    "kind": "item", "id": f["id"], "pub": pid, "title": "Source item",
                    "url": f["url"], "byline": f.get("byline") or "", "person_id": f.get("person_id"),
                    "date": date_of(f, "published_at_sast", "published_at"), "frame": f.get("sample_frame"),
                    "access": "Free to read when coded.", "findings": []})
            f["_item"] = key
            f["_person"] = f.get("person_id") or items[key]["person_id"]
            items[key]["findings"].append(f)
            findings.append(f)

    git_sha, run_id = build_identity()
    source_dates = []
    for f in findings:
        source_dates.append(to_sast_date(f.get("published_at_sast") or f.get("published_at")))
    for it in items.values():
        # items store a display date; recover a date prefix if it is ISO-like
        source_dates.append(to_sast_date(it.get("date")))
    source_dates = [d for d in source_dates if d]
    data_date = max(source_dates) if source_dates else DATA_WINDOW["end"]
    built_at = now_sast().isoformat(timespec="seconds")
    build_meta = {
        "git_sha": git_sha,
        "git_sha_short": (git_sha[:7] if git_sha else "unknown"),
        "run_id": run_id,
        "built_at_sast": built_at,
        "data_date": data_date,
    }

    if out_dir.exists():
        shutil.rmtree(out_dir)
    (out_dir / "assets").mkdir(parents=True)
    shutil.copy2(SITE_SRC / "assets" / "style.css", out_dir / "assets" / "style.css")
    (out_dir / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")

    def write(rel, title, body, crumbs=()):
        depth = rel.count("/")
        path = out_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(page(title, body, depth, crumbs, build_meta=build_meta), encoding="utf-8")

    def item_href(key):
        kind, iid = key
        return {"a": "a", "x": "x", "f": "i"}[kind] + f"/{slug(iid)}/index.html"

    def person_name(pid_):
        p = people.get(pid_)
        return p["full_name"] if p else None

    # ---- home
    def pub_rows(ids):
        rows = []
        for pid in ids:
            pub = pubs[pid]
            shown = [f for f in findings if f["publication_id"] == pid]
            rows.append(f'<tr><td><a href="p/{slug(pid)}/index.html">{e(pub["name"])}</a></td>'
                        f'<td>{e(pub.get("owner_group"))}</td><td class="num">{len(shown)}</td>'
                        f'<td class="num">{excluded_counts[pid]}</td></tr>')
        return "".join(rows)
    home = f"""<h1>South African media bias register (pilot)</h1>
<p>MediaWatch SA records bias <strong>for or against named actors</strong> (parties, governments, organisations and public figures in their public role). Each finding quotes the exact line, links the source, gives a fact label and sets out the strongest case on both sides.</p>
<p>The pilot covers three outlets. The register will grow in phases to cover South African media broadly; see the <a href="coverage/index.html">coverage plan</a>.</p>
<h2>Pilot publications</h2>
<table><thead><tr><th>Publication</th><th>Owner group</th><th class="num">Findings shown</th><th class="num">Excluded (paywalled)</th></tr></thead>
<tbody>{pub_rows(PILOT)}</tbody></table>
<p class="note">Window: May&ndash;October 2026. Only content the public can read free is judged. Findings that rested on a paywalled piece are excluded and not scored.</p>
<h2>Error watch (outside the pilot sample)</h2>
<p>These findings were logged against official records after the May&ndash;October 2026 pilot window. They are shown as findings only. They do not expand the scored three-outlet pilot and are not used to claim a publication score for these outlets.</p>
<table><thead><tr><th>Publication</th><th>Owner group</th><th class="num">Findings shown</th><th class="num">Excluded (paywalled)</th></tr></thead>
<tbody>{pub_rows(WATCH)}</tbody></table>"""
    write("index.html", "Publications", home)

    # ---- publication pages
    for pid in PILOT + WATCH:
        pub = pubs[pid]
        fs = [f for f in findings if f["publication_id"] == pid]
        writers = Counter(f["_person"] for f in fs if f["_person"])
        wrows = []
        for wid, cnt in sorted(writers.items(), key=lambda kv: (-kv[1], kv[0])):
            p = people.get(wid)
            byl = next((f.get("byline") or items[f["_item"]]["byline"] for f in fs if f["_person"] == wid
                        and (f.get("byline") or items[f["_item"]]["byline"])), wid)
            name = p["full_name"] if p else byl
            role = p["role"] if p else "Journalist (byline)"
            wrows.append(f'<tr><td><a href="../../w/{slug(wid)}/index.html">{e(name)}</a></td><td>{e(role)}</td><td class="num">{cnt}</td></tr>')
        unlinked = [f for f in fs if not f["_person"]]
        by_frame = defaultdict(list)
        for f in fs:
            by_frame[f.get("sample_frame") or "unrecorded"].append(f)
        frame_html = []
        for fr in sorted(by_frame):
            frame_html.append(f'<h3>{e(fr)} <span class="note">({e(FRAME_NOTES.get(fr, ""))})</span></h3>'
                              + findings_table(by_frame[fr], "../../"))
        body = f"""<h1>{e(pub['name'])}</h1>
<dl class="ev"><dt>Website</dt><dd><a href="{e(pub['url'])}" rel="nofollow noopener">{e(pub['url'])}</a></dd>
<dt>Owner group</dt><dd>{e(pub.get('owner_group'))} <span class="badge">{e(pub.get('owner_fact_label'))}</span></dd>
<dt>Editor</dt><dd>{e(pub.get('editor_in_chief'))}{editor_sources(pub)}</dd>
<dt>Excluded (paywalled)</dt><dd>{excluded_counts[pid]} finding(s) rested on paywalled pieces and are not shown or scored.</dd></dl>
<h2>Scorecard by named actor</h2>
{scorecard_table(scorecards(fs), 'publication')}
<h2>Writers and editors</h2>
<table><thead><tr><th>Name</th><th>Public role</th><th class="num">Findings</th></tr></thead><tbody>{''.join(wrows)}</tbody></table>
{('<p class="note">' + str(len(unlinked)) + ' finding(s) on items without a linked individual byline are listed below by sample frame.</p>') if unlinked else ''}
<h2>Findings by sample frame</h2>
{''.join(frame_html)}"""
        write(f"p/{slug(pid)}/index.html", pub["name"], body, [("Publications", "index.html"), (pub["name"], None)])

    # ---- writer pages
    by_person = defaultdict(list)
    for f in findings:
        if f["_person"]:
            by_person[f["_person"]].append(f)
    for wid, fs in by_person.items():
        p = people.get(wid)
        if not p:
            # Bylined journalist not yet in people.csv: use the published byline, public role only.
            byline = next((f.get("byline") or items[f["_item"]]["byline"] for f in fs
                           if f.get("byline") or items[f["_item"]]["byline"]), None)
            if not byline:
                raise BuildError(f"person {wid} not in people.csv and no byline")
            p = {"id": wid, "full_name": byline, "role": "Journalist (byline)",
                 "publication_id": fs[0]["publication_id"], "x_handle": "", "x_handle_source_url": ""}
            people[wid] = p
        pub = pubs.get(p.get("publication_id") or fs[0]["publication_id"])
        handle = (p.get("x_handle") or "").strip()
        handle_html = (f'<dt>Public X account</dt><dd><a href="https://x.com/{e(handle)}" rel="nofollow noopener">@{e(handle)}</a></dd>'
                       if handle and p.get("x_handle_source_url") else "")
        its = []
        for key in dict.fromkeys(f["_item"] for f in fs):
            it = items[key]
            its.append(f'<tr><td><a href="../../{item_href(key)}">{e(trim(it["title"], 110))}</a></td><td>{e(it["kind"])}</td>'
                       f'<td>{e(it["date"])}</td><td class="num">{sum(1 for f in fs if f["_item"] == key)}</td></tr>')
        body = f"""<h1>{e(p['full_name'])}</h1>
<dl class="ev"><dt>Public role</dt><dd>{e(p['role'])}{(' &middot; ' + e(pub['name'])) if pub else ''}</dd>{handle_html}</dl>
<h2>Scorecard by named actor</h2>
{scorecard_table(scorecards(fs, person_level=True), 'person')}
<h2>Articles and public posts</h2>
<table><thead><tr><th>Item</th><th>Type</th><th>Date (SAST)</th><th class="num">Findings</th></tr></thead><tbody>{''.join(its)}</tbody></table>
<h2>Findings</h2>
{findings_table(fs, '../../')}"""
        crumbs = [("Publications", "index.html")]
        if pub:
            crumbs.append((pub["name"], f"p/{slug(pub['id'])}/index.html"))
        crumbs.append((p["full_name"], None))
        write(f"w/{slug(wid)}/index.html", p["full_name"], body, crumbs)

    # ---- item pages
    for key, it in items.items():
        pub = pubs[it["pub"]]
        pname = person_name(it["person_id"]) if it["person_id"] else None
        who = (f'<a href="../../w/{slug(it["person_id"])}/index.html">{e(pname)}</a>' if pname else e(it["byline"] or "Not linked"))
        body = f"""<h1>{e(it['title'])}</h1>
<dl class="ev"><dt>Publication</dt><dd>{e(pub['name'])}</dd>
<dt>{'Account' if it['kind'] == 'post' else 'Byline'}</dt><dd>{who}</dd>
<dt>Date (SAST)</dt><dd>{e(it['date'])}</dd>
<dt>Source</dt><dd><a href="{e(it['url'])}" rel="nofollow noopener">{e(it['url'])}</a></dd>
<dt>Sample frame</dt><dd>{e(it['frame'] or '-')}</dd>
<dt>Access</dt><dd>{e(it['access'])}</dd></dl>
<h2>Findings on this item</h2>
{findings_table(it['findings'], '../../')}"""
        crumbs = [("Publications", "index.html"), (pub["name"], f"p/{slug(pub['id'])}/index.html")]
        if pname:
            crumbs.append((pname, f"w/{slug(it['person_id'])}/index.html"))
        crumbs.append((trim(it["title"], 60), None))
        write(item_href(key), it["title"], body, crumbs)

    # ---- finding pages
    for f in findings:
        it = items[f["_item"]]
        pub = pubs[f["publication_id"]]
        pname = person_name(f["_person"]) if f["_person"] else None
        ctx = ""
        if f.get("target_inferred") and f.get("target_context_quote"):
            ctx = (f'<dt>Context line (actor inferred)</dt><dd><blockquote class="quote context-quote">'
                   f'{e(f["target_context_quote"])}</blockquote></dd>')
        score_note = STATUS_NOTES.get(f.get("accountability_status") or "bias", "")
        signed = f.get("signed_score")
        signed_html = fmt_score(float(signed)) if signed is not None else "&ndash; (not counted)"
        body = f"""<h1>Finding {e(f['id'])}</h1>
<article class="finding" data-finding="{e(f['id'])}">
<blockquote class="quote finding-quote">{e(f['quote'])}</blockquote>
<dl class="ev">
<dt>Source</dt><dd><a class="source-link" href="{e(f['url'])}" rel="nofollow noopener">{e(f['url'])}</a></dd>
<dt>Named actor</dt><dd>{e(f['actor'])}</dd>
<dt>Direction</dt><dd class="{e(f['direction'])}">{e(f['direction'])}</dd>
<dt>Driver</dt><dd>{driver_html(f)}</dd>
<dt>Fact label</dt><dd><span class="badge fact-label">{e(f['fact_label'])}</span></dd>
<dt>Signed score</dt><dd>{signed_html}</dd>
<dt>Status</dt><dd>{e(score_note)}</dd>
<dt>Date (SAST)</dt><dd>{e(date_of(f, 'published_at_sast', 'published_at'))}</dd>
<dt>Writer / account</dt><dd>{e(pname or it['byline'] or 'Not linked')}</dd>
<dt>Item</dt><dd><a href="../../{item_href(f['_item'])}">{e(trim(it['title'], 120))}</a></dd>
<dt>Sample frame</dt><dd>{e(f.get('sample_frame') or '-')}</dd>
{ctx}
<dt>Strongest case for the outlet</dt><dd class="steelman-for">{e(public_text(f['steelman_for']))}</dd>
<dt>Strongest case for the critique</dt><dd class="steelman-against">{e(public_text(f['steelman_against']))}</dd>
</dl>
</article>
<p class="note">Disagree with this finding? See <a href="../../corrections/index.html">corrections and right of reply</a>.</p>"""
        crumbs = [("Publications", "index.html"), (pub["name"], f"p/{slug(pub['id'])}/index.html")]
        if pname:
            crumbs.append((pname, f"w/{slug(f['_person'])}/index.html"))
        crumbs += [(trim(it["title"], 50), item_href(f["_item"])), (f["id"], None)]
        write(f"f/{slug(f['id'])}/index.html", f"Finding {f['id']}", body, crumbs)

    # ---- static pages
    labels = "".join(f"<li><strong>{e(l)}</strong></li>" for l in ALLOWED_LABELS)
    drivers = "".join(f"<li>{e(v)} <code>{e(k)}</code></li>" for k, v in DRIVER_NAMES.items())
    frames = "".join(f"<li><code>{e(k)}</code>: {e(v)}</li>" for k, v in FRAME_NOTES.items())
    method = f"""<h1>Method</h1>
<h2>What is measured</h2>
<p>Each finding answers one question: relative to a <strong>named actor</strong>, does this published line (or a public post by a named newsroom figure) work <strong>FOR</strong> or <strong>AGAINST</strong> that actor, and by which driver? Signed scores run from &minus;2 to +2 per actor.</p>
<h2>Drivers</h2><ul>{drivers}</ul>
<p class="note">Daily Investor and Newsday findings use the official closed driver set. Unofficial names used in the first pilot coding were recoded in CHG-MW-008; historical weights and signed scores were not rewritten.</p>
<h2>Fact labels (closed set)</h2><ul>{labels}</ul>
<h2>Thresholds</h2>
<p>A score is shown only when <em>n</em> &ge; 10 counted findings for that outlet or writer and actor. With 5&ndash;9 it is marked provisional. Under 5, only the findings are shown. Writer scores drawn only from keyword searches are suppressed.</p>
<h2>Sample frames</h2><ul>{frames}</ul>
<h2>No paywalled content</h2>
<p>Bias is judged only on what the public can read free. Paywalled articles are out of the sample and never scored. A headline, standfirst or teaser never stands in for a paywalled body. No logins, subscriptions or paywall workarounds are used.</p>
<h2>Accountability reporting</h2>
<p>Sourced accountability reporting on those in power, with fair right of reply and no loaded driver, is not counted as bias. Such findings stay visible for audit but do not count in the score.</p>
<h2>Official wording vs media wording</h2>
<p>A SAPS or NPA charge sheet records what was charged, not what happened. The charge itself is Proven as a charge; it does not prove or disprove the acts. Each injury or act claim is labelled on its own evidence (for example Alleged if only a family member or lobby group asserts it; Established if hospital records or court testimony back it). A gap in either direction &mdash; downplaying or inflating &mdash; is a framing or omission finding once there is an exact quote and a contrary record.</p>
<p>The same rule applies to official statistics and media reports of them. A misreported official figure is a factual error. The official table figure, checked in the primary release, is Proven. A speech or briefing is a primary record of what was said, but it does not override the statistical tables when the two conflict. This rule is shared with the project's other registers so they all treat official wording consistently.</p>
<h2>Privacy</h2>
<p>Journalists, editors and public figures are named in their public role only. Private individuals who appear in stories are described by role, never named. See the <a href="../privacy/index.html">privacy page</a>.</p>"""
    write("method/index.html", "Method", method, [("Method", None)])

    contact = '<a href="mailto:privacy@grokforum.site">privacy@grokforum.site</a>'
    corrections = f"""<h1>Corrections and right of reply</h1>
<p>If you are a publication, journalist or named actor and believe a finding is wrong, unfair or missing context, you can ask for a correction or submit a reply.</p>
<ul><li>Name the finding ID (for example <code>F-DI-01</code>) and say what is wrong.</li>
<li>Link or attach the evidence you rely on.</li>
<li>Say whether you want your reply published alongside the finding.</li></ul>
<p><strong>Contact:</strong> {contact}</p>
<p>Accepted corrections are recorded as a new, dated score run. Earlier scores are not silently rewritten. Replies are never published automatically.</p>"""
    write("corrections/index.html", "Corrections and right of reply", corrections, [("Corrections and right of reply", None)])

    privacy = f"""<h1>Privacy</h1>
<p>MediaWatch SA is a draft public register of South African media bias. This page says what the register publishes, what it does not, and how to ask for a correction or a removal.</p>
<h2>What is published</h2>
<p>The site publishes findings about free, publicly available news articles and public posts. Each finding quotes a published line, links to that source, names the actor the line is for or against, gives a fact label, and sets out the strongest case on both sides.</p>
<p>Journalists, editors and public figures are named only in their public or professional role (for example an editor-in-chief, a bylined journalist, or a public official). Publication names, owner groups and public social-media accounts are shown only where they are already public.</p>
<h2>What is not published</h2>
<p>Private individuals who appear in a story are never named. They are described by role only (for example a municipal employee, or a spokesperson).</p>
<p>The site does not publish private contact details, identity numbers, home addresses, or other personal information of private people. It does not publish paywalled text. Internal working notes are not rendered.</p>
<h2>How this site treats visitors</h2>
<p>The site uses no cookies, no analytics and no trackers. It has no accounts and no forms. Every page carries a noindex instruction, and robots.txt disallows crawling, until a separate decision to index.</p>
<h2>Corrections and removal</h2>
<p>If you believe a published finding is wrong, unfair, or names someone who should not be named, you can ask for a correction or a removal. The same route is described on <a href="../corrections/index.html">corrections and right of reply</a>.</p>
<ul>
<li>Name the finding ID or the page address and say what is wrong.</li>
<li>Link or attach the evidence you rely on.</li>
<li>For a removal request, say which name or detail should come down and why (for example, a private person named in error).</li>
</ul>
<p><strong>Contact:</strong> {contact}</p>
<p>Accepted corrections are recorded as a new, dated score run. Earlier scores are not silently rewritten.</p>
<p>If a removal is accepted, the name is taken off the published pages at the next build; earlier copies in the repository history or in caches may still hold it.</p>
<h2>Who is responsible</h2>
<p>The responsible party is GrokForum, which publishes MediaWatch SA. Privacy and correction requests go to {contact}.</p>
<p>You can also complain to the <a href="https://inforegulator.org.za/" rel="nofollow noopener">Information Regulator (South Africa)</a>.</p>"""
    write("privacy/index.html", "Privacy", privacy, [("Privacy", None)])

    coverage = """<h1>Coverage plan</h1>
<p>The aim is to cover South African media broadly. Coverage grows in phases. No dates are promised; each phase starts only when its entry criteria are met.</p>
<ol>
<li><strong>Pilot:</strong> News24, Daily Investor and Newsday. Entry: method, fact labels and thresholds stable; free-access check done for each outlet. An error-watch log may add findings-only rows for other outlets without expanding this scored pilot.</li>
<li><strong>Major national dailies and weeklies (free content only):</strong> entry: pilot reviewed and corrected; neutral-random sampling rule fixed; driver list settled.</li>
<li><strong>Broadcasters' news sites:</strong> entry: phase 2 reaches minimum samples for its main actors; a rule for transcripts and clips agreed.</li>
<li><strong>Regional, community, Afrikaans and other-language outlets:</strong> entry: coders able to read the language; translation and quote-fidelity rule agreed.</li>
<li><strong>Further outlets and journalists' public posts at scale:</strong> entry: earlier phases stable and the corrections process proven.</li>
</ol>
<p class="note">Outlets that keep most news behind a paywall are covered only on their free content. If too little is free to reach minimum samples, the outlet shows findings only.</p>"""
    write("coverage/index.html", "Coverage plan", coverage, [("Coverage plan", None)])

    page_count = sum(1 for _ in out_dir.rglob("*.html"))
    manifest = {
        "schema": "mediawatch.manifest/v1",
        "kind": "manifest",
        "build": {"git_sha": git_sha, "run_id": run_id},
        "built_at_sast": built_at,
        "data_date": data_date,
        "data_window": dict(DATA_WINDOW),
        "counts": {
            "html_pages": page_count,
            "findings_rendered": len(findings),
            "findings_excluded_paywalled": len(excluded),
            "items": len(items),
            "writers": len(by_person),
            "publications": len(PILOT),
        },
        "inputs": [
            {"path": rel, "sha256": sha256_file(ROOT / rel)} for rel in MANIFEST_INPUTS
        ],
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    return {
        "findings_rendered": len(findings),
        "excluded": sorted(excluded),
        "excluded_detected": detected,
        "excluded_listed": sorted(listed),
        "items": len(items),
        "writers": len(by_person),
        "pages": page_count,
        "manifest": manifest,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(ROOT / "_site"))
    args = ap.parse_args(argv)
    try:
        stats = build(Path(args.out))
    except BuildError as exc:
        print(f"BUILD FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"Built {stats['pages']} pages: {stats['findings_rendered']} findings, {stats['items']} items, "
          f"{stats['writers']} writers; {len(stats['excluded'])} findings excluded (no-paywall rule).")
    mismatch = set(stats["excluded_detected"]) ^ set(stats["excluded_listed"])
    if mismatch:
        print(f"WARNING: paywall_exclusions.csv and detected set differ: {sorted(mismatch)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
