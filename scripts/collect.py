#!/usr/bin/env python3
"""Stdlib RSS and sitemap collectors for MediaWatch SA.

Certificate and TLS errors are logged (host, error, time in
Africa/Johannesburg) to the run log and to data/collector_errors.csv,
then the run continues with the next URL. TLS verification stays on.
The collector never weakens the default SSL context.
"""

from __future__ import annotations

import argparse
import re
import csv
import json
import ssl
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse
from xml.etree import ElementTree as ET
from zoneinfo import ZoneInfo

SAST = ZoneInfo("Africa/Johannesburg")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LOCKED_CANDIDATES = DATA / "sampling" / "neutral_random_candidates_v1.csv"
MAX_RESPONSE_BYTES = 5_000_000
DEFAULT_UA = (
    "MediaWatch-SA-collector/0.1 "
    "(https://mediawatch.grokforum.site/; public methodology register)"
)
ERROR_FIELDS = [
    "logged_at_sast",
    "host",
    "url",
    "error_type",
    "error",
    "outlet_id",
    "run_id",
]


def now_sast() -> datetime:
    return datetime.now(SAST)


def fmt_sast(dt: datetime | None = None) -> str:
    if dt is None:
        dt = now_sast()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=SAST)
    return dt.astimezone(SAST).strftime("%Y-%m-%dT%H:%M:%S%z")


def default_ssl_context() -> ssl.SSLContext:
    """Strict default context. Never weaken this."""
    return ssl.create_default_context()


def is_tls_error(exc: BaseException) -> bool:
    if isinstance(exc, ssl.SSLError):
        return True
    if isinstance(exc, urllib.error.URLError):
        reason = exc.reason
        if isinstance(reason, ssl.SSLError):
            return True
        text = str(reason).lower()
        if "ssl" in text or "certificate" in text or "tls" in text:
            return True
    text = f"{type(exc).__name__}: {exc}".lower()
    return "ssl" in text or "certificate" in text or "tls" in text


def load_config(path: Path | None = None) -> dict:
    path = path or (DATA / "collectors.json")
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass
class CollectedItem:
    outlet_id: str
    url: str
    title: str = ""
    published_at: str = ""
    date_source: str = ""
    source_url: str = ""
    source_kind: str = ""


def _local(tag: str) -> str:
    if tag.startswith("{") and "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _text(el: ET.Element | None) -> str:
    if el is None or el.text is None:
        return ""
    return el.text.strip()


def parse_xml(body: bytes) -> ET.Element:
    # Strip BOM if present.
    if body.startswith(b"\xef\xbb\xbf"):
        body = body[3:]
    return ET.fromstring(body)


def iter_children(el: ET.Element, name: str):
    for child in list(el):
        if _local(child.tag) == name:
            yield child


def parse_rss_or_atom(body: bytes, source_url: str, outlet_id: str) -> list[CollectedItem]:
    root = parse_xml(body)
    kind = _local(root.tag).lower()
    items: list[CollectedItem] = []
    if kind == "rss" or kind == "rdf":
        channel = next(iter_children(root, "channel"), root)
        for item in iter_children(channel, "item"):
            url = _text(next(iter_children(item, "link"), None))
            if not url:
                guid = next(iter_children(item, "guid"), None)
                if guid is not None and guid.get("isPermaLink", "true").lower() != "false":
                    url = _text(guid)
            title = _text(next(iter_children(item, "title"), None))
            raw_date = _text(next(iter_children(item, "pubDate"), None)) or _text(
                next((c for c in item if _local(c.tag) in {"date", "published", "updated"}), None)
            )
            when, source = normalise_date(raw_date, url)
            if url:
                items.append(
                    CollectedItem(outlet_id, url, title, when, source or "rss_pubDate", source_url, "rss")
                )
    elif kind == "feed":  # Atom
        for entry in iter_children(root, "entry"):
            url = ""
            for link in iter_children(entry, "link"):
                href = (link.get("href") or "").strip()
                rel = (link.get("rel") or "alternate").lower()
                if href and rel in {"alternate", ""}:
                    url = href
                    break
                if href and not url:
                    url = href
            title = _text(next(iter_children(entry, "title"), None))
            raw_date = _text(next(iter_children(entry, "published"), None)) or _text(
                next(iter_children(entry, "updated"), None)
            )
            when, source = normalise_date(raw_date, url)
            if url:
                items.append(
                    CollectedItem(outlet_id, url, title, when, source or "atom_published", source_url, "atom")
                )
    else:
        items.extend(parse_sitemap(body, source_url, outlet_id))
    return items


def parse_sitemap(body: bytes, source_url: str, outlet_id: str) -> list[CollectedItem]:
    root = parse_xml(body)
    items: list[CollectedItem] = []
    for url_el in _walk_named(root, "url"):
        loc = _text(next(iter_children(url_el, "loc"), None))
        lastmod = _text(next(iter_children(url_el, "lastmod"), None))
        # news sitemap publication date, if present
        news_date = ""
        for child in list(url_el):
            if _local(child.tag) in {"news", "news:news"} or _local(child.tag) == "news":
                for n in list(child):
                    if _local(n.tag) in {"publication_date", "publicationDate"}:
                        news_date = _text(n)
        when, source = normalise_date(news_date or lastmod, loc)
        if loc:
            items.append(
                CollectedItem(outlet_id, loc, "", when, source, source_url, "sitemap")
            )
    return items


def sitemap_child_locs(body: bytes) -> list[str]:
    return [loc for loc, _lastmod in sitemap_child_entries(body)]


def sitemap_child_entries(body: bytes) -> list[tuple[str, str]]:
    root = parse_xml(body)
    if _local(root.tag) != "sitemapindex":
        return []
    entries = []
    for sm in _walk_named(root, "sitemap"):
        loc = _text(next(iter_children(sm, "loc"), None))
        lastmod = _text(next(iter_children(sm, "lastmod"), None))
        if loc:
            entries.append((loc, lastmod))
    return entries


def _walk_named(root: ET.Element, name: str):
    if _local(root.tag) == name:
        yield root
    for el in root.iter():
        if el is not root and _local(el.tag) == name:
            yield el


def normalise_date(raw: str, url: str = "") -> tuple[str, str]:
    raw = (raw or "").strip()
    parsed = parse_any_date(raw) if raw else None
    from_url = date_from_url(url)
    # A date in the permalink is the publication date. Prefer it over sitemap lastmod,
    # which is often an edit or index-refresh time. If the feed timestamp falls on the
    # same calendar day, keep the time of day from the feed.
    if from_url is not None:
        if parsed is not None and parsed.astimezone(SAST).date() == from_url:
            return parsed.astimezone(SAST).strftime("%Y-%m-%dT%H:%M:%S%z"), "url_and_feed"
        dt = datetime(from_url.year, from_url.month, from_url.day, tzinfo=SAST)
        return dt.strftime("%Y-%m-%dT%H:%M:%S%z"), "url"
    if parsed is not None:
        return parsed.astimezone(SAST).strftime("%Y-%m-%dT%H:%M:%S%z"), "lastmod_or_pub"
    return "", ""


def parse_any_date(raw: str) -> datetime | None:
    raw = raw.strip()
    # MM-DD-YYYY (News24 sitemap lastmod)
    if len(raw) >= 10 and raw[2] == "-" and raw[5] == "-" and raw[6:10].isdigit():
        try:
            month, day, year = int(raw[0:2]), int(raw[3:5]), int(raw[6:10])
            return datetime(year, month, day, tzinfo=SAST)
        except ValueError:
            pass
    for fmt in (
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ):
        try:
            text = raw
            if fmt.endswith("Z") and text.endswith("Z"):
                dt = datetime.strptime(text, fmt)
                return dt.replace(tzinfo=SAST) if dt.tzinfo is None else dt
            if fmt.endswith("%z") and text.endswith("Z"):
                text = text[:-1] + "+0000"
            if fmt.endswith("%z") and (text[-3:-2] == ":" and (text[-6] in "+-")):
                text = text[:-3] + text[-2:]
            dt = datetime.strptime(text, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=SAST)
            return dt
        except ValueError:
            continue
    try:
        dt = parsedate_to_datetime(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=SAST)
        return dt
    except (TypeError, ValueError, IndexError):
        return None


def date_from_url(url: str) -> date | None:
    if not url:
        return None
    patterns = (
        # Daily Maverick /article/2026-11-20-slug and similar hyphenated dates
        r"(?:^|[^\d])((?:19|20)\d{2})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])(?:[^\d]|$)",
        # News24 slugs ...-YYYYMMDD-####
        r"(?:^|[^\d])((?:19|20)\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(?:[^\d]|$)",
        # Path form /2026/11/20/
        r"/((?:19|20)\d{2})/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])(?:/|$)",
    )
    for pat in patterns:
        m = re.search(pat, url)
        if not m:
            continue
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            continue
    return None


class ErrorLog:
    def __init__(self, path: Path, run_id: str):
        self.path = path
        self.run_id = run_id
        self.count = 0
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            self._write_header()
        else:
            # Ensure header exists; keep existing rows (CRLF).
            raw = path.read_bytes()
            if not raw:
                self._write_header()

    def _write_header(self) -> None:
        self.path.write_bytes((",".join(ERROR_FIELDS) + "\r\n").encode("utf-8"))

    def record(self, url: str, exc: BaseException, outlet_id: str = "") -> dict:
        host = urlparse(url).hostname or ""
        error_type = "tls" if is_tls_error(exc) else type(exc).__name__
        row = {
            "logged_at_sast": fmt_sast(),
            "host": host,
            "url": url,
            "error_type": error_type,
            "error": f"{type(exc).__name__}: {exc}",
            "outlet_id": outlet_id,
            "run_id": self.run_id,
        }
        self._append(row)
        self.count += 1
        kind = "TLS/certificate" if error_type == "tls" else "fetch"
        print(
            f"[{kind} error] host={host} time={row['logged_at_sast']} "
            f"error={row['error']} url={url}",
            file=sys.stderr,
        )
        return row

    def _append(self, row: dict) -> None:
        # Append a CRLF row without rewriting the file (Windows-safe csv).
        line = io_line(row)
        with self.path.open("ab") as fh:
            fh.write(line.encode("utf-8"))


def io_line(row: dict) -> str:
    from io import StringIO
    buf = StringIO()
    w = csv.DictWriter(buf, fieldnames=ERROR_FIELDS, lineterminator="\r\n", extrasaction="ignore")
    w.writerow(row)
    return buf.getvalue()


class ResponseTooLarge(OSError):
    """The remote body exceeded MAX_RESPONSE_BYTES."""


def read_capped(resp, limit: int = MAX_RESPONSE_BYTES) -> bytes:
    """Read a file-like HTTP body, failing closed if it exceeds `limit` bytes."""
    buf = bytearray()
    while True:
        chunk = resp.read(65536)
        if not chunk:
            return bytes(buf)
        if len(buf) + len(chunk) > limit:
            raise ResponseTooLarge(f"response exceeded {limit} bytes")
        buf.extend(chunk)


def assert_candidate_coverage(current: dict, locked: dict, max_drop_fraction: float = 1 / 3) -> None:
    """Fail if any locked outlet lost more than a third of its candidate rows."""
    missing = [oid for oid in locked if oid not in current]
    if missing:
        raise AssertionError(f"locked outlets missing from current candidates: {missing}")
    for oid, expected in locked.items():
        got = int(current.get(oid) or 0)
        if expected and (expected - got) / expected > max_drop_fraction:
            raise AssertionError(
                f"{oid} candidates dropped too far: {got} remaining of {expected} locked"
            )


class Collector:
    def __init__(
        self,
        config: dict,
        error_log: ErrorLog,
        user_agent: str = DEFAULT_UA,
        delay_s: float = 0.2,
        context: ssl.SSLContext | None = None,
        opener=None,
    ):
        self.config = config
        self.error_log = error_log
        self.user_agent = user_agent
        self.delay_s = delay_s
        self.context = context or default_ssl_context()
        self._opener = opener  # optional test hook: callable(request, timeout, context)
        self._last_request = 0.0

    def fetch_bytes(self, url: str, outlet_id: str = "") -> bytes | None:
        if self.delay_s and self._last_request:
            wait = self.delay_s - (time.monotonic() - self._last_request)
            if wait > 0:
                time.sleep(wait)
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": self.user_agent,
                "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*;q=0.8",
            },
        )
        self._last_request = time.monotonic()
        try:
            if self._opener is not None:
                return self._opener(req, timeout=30, context=self.context)
            with urllib.request.urlopen(req, timeout=30, context=self.context) as resp:
                return read_capped(resp)
        except Exception as exc:  # log, continue to the next URL; never disable TLS
            self.error_log.record(url, exc, outlet_id=outlet_id)
            return None

    def collect_outlet(
        self,
        outlet_id: str,
        window_start: date | None = None,
        window_end: date | None = None,
    ) -> list[CollectedItem]:
        cfg = self.config["outlets"][outlet_id]
        items: list[CollectedItem] = []
        seen: set[str] = set()

        def add_all(batch: Iterable[CollectedItem]) -> None:
            for item in batch:
                key = item.url.strip().rstrip("/").lower()
                if not key or key in seen:
                    continue
                if window_start or window_end:
                    d = item_date(item)
                    if d is None:
                        # Keep undated items so the sampler can record them as undated; they
                        # are excluded from the draw itself.
                        pass
                    else:
                        if window_start and d < window_start:
                            continue
                        if window_end and d > window_end:
                            continue
                seen.add(key)
                items.append(item)

        for rss_url in cfg.get("rss") or []:
            body = self.fetch_bytes(rss_url, outlet_id)
            if body is None:
                continue
            try:
                add_all(parse_rss_or_atom(body, rss_url, outlet_id))
            except ET.ParseError as exc:
                self.error_log.record(rss_url, exc, outlet_id=outlet_id)

        for sm_url in cfg.get("sitemaps") or []:
            add_all(self._collect_sitemap(sm_url, outlet_id, cfg, window_start, window_end))

        if cfg.get("dated_sitemap_pattern"):
            if not window_start or not window_end:
                raise ValueError("dated sitemap collection requires a window")
            add_all(
                self._collect_dated_sitemaps(outlet_id, cfg, window_start, window_end)
            )
        return items

    def _collect_dated_sitemaps(
        self, outlet_id: str, cfg: dict, start: date, end: date
    ) -> list[CollectedItem]:
        items: list[CollectedItem] = []
        pattern = cfg["dated_sitemap_pattern"]
        day = start
        while day <= end:
            url = pattern.format(year=day.year, month=day.month, day=day.day)
            body = self.fetch_bytes(url, outlet_id)
            if body is not None:
                try:
                    items.extend(parse_sitemap(body, url, outlet_id))
                except ET.ParseError as exc:
                    self.error_log.record(url, exc, outlet_id=outlet_id)
            day += timedelta(days=1)
        return items

    def _collect_sitemap(
        self,
        url: str,
        outlet_id: str,
        cfg: dict,
        window_start: date | None,
        window_end: date | None,
        depth: int = 0,
    ) -> list[CollectedItem]:
        if depth > 3:
            return []
        body = self.fetch_bytes(url, outlet_id)
        if body is None:
            return []
        try:
            children = sitemap_child_entries(body)
        except ET.ParseError as exc:
            self.error_log.record(url, exc, outlet_id=outlet_id)
            return []
        if children:
            allow = cfg.get("sitemap_allow_substrings") or []
            deny = cfg.get("sitemap_deny_substrings") or []
            items: list[CollectedItem] = []
            for child, lastmod in children:
                if deny and any(s in child for s in deny):
                    continue
                if allow and not any(s in child for s in allow):
                    continue
                if window_start and lastmod:
                    parsed = parse_any_date(lastmod)
                    if parsed is not None and parsed.date() < window_start:
                        continue
                items.extend(
                    self._collect_sitemap(
                        child, outlet_id, cfg, window_start, window_end, depth + 1
                    )
                )
            return items
        try:
            return parse_sitemap(body, url, outlet_id)
        except ET.ParseError as exc:
            self.error_log.record(url, exc, outlet_id=outlet_id)
            return []


def item_date(item: CollectedItem) -> date | None:
    if not item.published_at:
        return date_from_url(item.url)
    parsed = parse_any_date(item.published_at)
    return parsed.date() if parsed else date_from_url(item.url)


def path_allowed(url: str, cfg: dict) -> bool:
    path = urlparse(url).path or "/"
    if not path.startswith("/"):
        path = "/" + path
    for prefix in cfg.get("exclude_path_prefixes") or []:
        if path.startswith(prefix):
            return False
    includes = cfg.get("include_path_prefixes") or []
    if not includes:
        return True
    return any(path.startswith(p) for p in includes)


def write_candidates_csv(path: Path, items: list[CollectedItem]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["outlet_id", "url", "title", "published_at", "date_source", "source_url", "source_kind"]
    from io import StringIO
    buf = StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    for item in items:
        w.writerow(asdict(item))
    path.write_text(buf.getvalue(), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect RSS/sitemap article URLs (TLS verified).")
    parser.add_argument("--config", default=str(DATA / "collectors.json"))
    parser.add_argument("--errors", default=str(DATA / "collector_errors.csv"))
    parser.add_argument("--out", default=str(DATA / "sampling" / "neutral_random_candidates_v1.csv"))
    parser.add_argument("--from", dest="date_from", default="2026-05-01")
    parser.add_argument("--to", dest="date_to", default=None)
    parser.add_argument("--outlets", default="")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--delay", type=float, default=0.2)
    parser.add_argument(
        "--overwrite-locked-candidates",
        action="store_true",
        help="Required to write to the locked v1 candidates file.",
    )
    args = parser.parse_args(argv)

    out_path = Path(args.out)
    if out_path.resolve() == LOCKED_CANDIDATES.resolve() and not args.overwrite_locked_candidates:
        print(
            "refusing to overwrite the locked candidates file without "
            "--overwrite-locked-candidates",
            file=sys.stderr,
        )
        return 1
    window_start = date.fromisoformat(args.date_from)
    if args.date_to:
        window_end = date.fromisoformat(args.date_to)
    else:
        window_end = now_sast().date()
    run_id = args.run_id or f"collect-{fmt_sast()}"
    config = load_config(Path(args.config))
    outlet_ids = [s.strip() for s in args.outlets.split(",") if s.strip()] or list(
        config["outlets"].keys()
    )
    errors = ErrorLog(Path(args.errors), run_id)
    collector = Collector(config, errors, delay_s=args.delay)
    for watch in config.get("tls_watch") or []:
        print(f"tls watch {watch['url']}", file=sys.stderr)
        collector.fetch_bytes(watch["url"], outlet_id=watch.get("outlet_id") or "")
    all_items: list[CollectedItem] = []
    for oid in outlet_ids:
        print(f"collecting {oid} {window_start}..{window_end}", file=sys.stderr)
        batch = collector.collect_outlet(oid, window_start, window_end)
        cfg = config["outlets"][oid]
        kept = [it for it in batch if path_allowed(it.url, cfg)]
        print(f"  fetched {len(batch)} in window, {len(kept)} after path filters", file=sys.stderr)
        all_items.extend(kept)
    out_path = Path(args.out)
    if out_path.resolve() == LOCKED_CANDIDATES.resolve() and not args.overwrite_locked_candidates:
        print(
            "refusing to overwrite the locked candidates file without "
            "--overwrite-locked-candidates",
            file=sys.stderr,
        )
        return 1
    rule_path = DATA / "sampling" / "neutral_random_v1.json"
    if rule_path.is_file() and (
        out_path.resolve() == LOCKED_CANDIDATES.resolve()
        or not args.outlets
    ):
        rule = json.loads(rule_path.read_text(encoding="utf-8"))
        locked = rule.get("candidate_counts") or {}
        if locked:
            current: dict[str, int] = {}
            for it in all_items:
                oid = getattr(it, "outlet_id", None) or (it.get("outlet_id") if isinstance(it, dict) else "")
                if oid:
                    current[oid] = current.get(oid, 0) + 1
            try:
                assert_candidate_coverage(current, locked)
            except AssertionError as exc:
                print(f"{exc}; refusing to write {out_path}", file=sys.stderr)
                return 1
    write_candidates_csv(out_path, all_items)
    print(f"wrote {len(all_items)} candidates to {args.out}", file=sys.stderr)
    if errors.count:
        print(f"{errors.count} collector error(s) logged; exiting non-zero", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
