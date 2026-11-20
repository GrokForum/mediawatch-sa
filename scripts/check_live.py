#!/usr/bin/env python3
"""After-deploy live check for https://mediawatch.grokforum.site (RFC-CHG-MW-003).

Read-only: GETs the live site (or --base-url), writes a JSON result, exits 0 on
PASS and 1 on FAIL. Standard library only. Never writes to git and never
changes Pages settings.

Checks:
  * GET / is 200, carries noindex, nofollow and a visible DRAFT label
  * GET /robots.txt is 200 and the body is exactly: User-agent: *\\nDisallow: /\\n
  * Sample pages carry the noindex, nofollow meta
  * /data, /docs and /plan (and their trailing-slash forms) return 404
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

SAST = ZoneInfo("Africa/Johannesburg")
DEFAULT_BASE = "https://mediawatch.grokforum.site"
ROBOTS_EXACT = "User-agent: *\nDisallow: /\n"
NOINDEX = '<meta name="robots" content="noindex, nofollow">'
DRAFT_MARKERS = ("Draft preview (DEV)", "MediaWatch SA (draft)")
SAMPLE_PATHS = ("/", "/method/", "/coverage/", "/corrections/", "/privacy/", "/p/news24/")
FORBIDDEN_PATHS = ("/data", "/data/", "/docs", "/docs/", "/plan", "/plan/")
USER_AGENT = "MediaWatch-SA-live-check/1.0"
DEFAULT_TIMEOUT = 20
DEFAULT_WAIT = 300
RETRY_EVERY = 15

class _PageSignals(HTMLParser):
    """Collect robots meta content and visible text (not script, style, or attributes)."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.robots_contents: list[str] = []
        self._chunks: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        self._on_start(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self._on_start(tag, attrs)

    def _on_start(self, tag, attrs) -> None:
        t = (tag or "").lower()
        if t in ("script", "style"):
            self._skip += 1
            return
        if t == "meta":
            data = {(k or "").lower(): (v or "") for k, v in attrs}
            if data.get("name", "").strip().lower() == "robots":
                self.robots_contents.append(data.get("content", ""))

    def handle_endtag(self, tag):
        if (tag or "").lower() in ("script", "style") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._skip == 0 and data:
            self._chunks.append(data)

    def visible_text(self) -> str:
        return " ".join(self._chunks)


def _parse_page(html: str) -> _PageSignals:
    parser = _PageSignals()
    parser.feed(html or "")
    parser.close()
    return parser


def _robots_tokens(content: str) -> set[str]:
    return {part.strip().lower() for part in content.split(",") if part.strip()}


def has_noindex_nofollow(html: str) -> bool:
    """True when a robots meta lists both noindex and nofollow (html.parser, not a substring)."""
    try:
        parsed = _parse_page(html)
    except Exception:
        return False
    return any(
        "noindex" in _robots_tokens(content) and "nofollow" in _robots_tokens(content)
        for content in parsed.robots_contents
    )


def has_visible_draft(html: str) -> bool:
    """True when a DRAFT marker appears in visible text, not in script, style, or attributes."""
    try:
        text = _parse_page(html).visible_text()
    except Exception:
        return False
    return any(marker in text for marker in DRAFT_MARKERS)


def now_sast() -> datetime:
    return datetime.now(SAST)


def iso_sast(dt: datetime | None = None) -> str:
    return (dt or now_sast()).isoformat(timespec="seconds")


def join_url(base: str, path: str) -> str:
    return base.rstrip("/") + path


class CrossHostRedirectError(urllib.error.URLError):
    """A 3xx Location pointed at a different host than the request."""


class SameHostRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Follow redirects only when the Location host equals the request host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        src = (urlparse(req.full_url).hostname or "").lower()
        dst = (urlparse(newurl).hostname or "").lower()
        if dst != src:
            raise CrossHostRedirectError(
                f"cross-host redirect from {src!r} to {dst!r} ({newurl})"
            )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _opener():
    return urllib.request.build_opener(SameHostRedirectHandler)


def fetch(url: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """GET url. Follows same-host redirects only. Returns status/body; never raises for HTTP codes."""
    req = urllib.request.Request(
        url,
        method="GET",
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,text/plain,*/*;q=0.8"},
    )
    try:
        with _opener().open(req, timeout=timeout) as resp:
            raw = resp.read()
            return {
                "url": url,
                "final_url": resp.geturl(),
                "status": int(resp.getcode()),
                "body": raw.decode("utf-8", errors="replace"),
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        raw = exc.read() if exc.fp else b""
        final = url
        try:
            final = exc.geturl() or url
        except Exception:
            final = url
        return {
            "url": url,
            "final_url": final,
            "status": int(exc.code),
            "body": raw.decode("utf-8", errors="replace"),
            "error": None,
        }
    except Exception as exc:
        return {
            "url": url,
            "final_url": url,
            "status": None,
            "body": "",
            "error": f"{type(exc).__name__}: {exc}",
        }


def _result(name: str, url: str, ok: bool, **extra) -> dict:
    row = {"name": name, "url": url, "pass": bool(ok)}
    row.update(extra)
    return row


def evaluate(base: str, timeout: int) -> list[dict]:
    checks: list[dict] = []

    home = fetch(join_url(base, "/"), timeout=timeout)
    home_noindex = has_noindex_nofollow(home["body"])
    home_draft = has_visible_draft(home["body"])
    home_ok = home["status"] == 200 and home_noindex and home_draft
    checks.append(_result(
        "home_200",
        home["url"],
        home_ok,
        status=home["status"],
        final_url=home["final_url"],
        noindex=home_noindex,
        draft=home_draft,
        error=home["error"],
    ))

    robots = fetch(join_url(base, "/robots.txt"), timeout=timeout)
    body = robots["body"]
    # Tolerate a missing final newline only for comparison after exact check;
    # the required body is exact, including the trailing newline.
    robots_ok = robots["status"] == 200 and body == ROBOTS_EXACT
    checks.append(_result(
        "robots_disallow",
        robots["url"],
        robots_ok,
        status=robots["status"],
        final_url=robots["final_url"],
        expected=ROBOTS_EXACT,
        got=body if robots["status"] == 200 else None,
        error=robots["error"],
    ))

    for path in SAMPLE_PATHS:
        got = fetch(join_url(base, path), timeout=timeout)
        page_noindex = has_noindex_nofollow(got["body"])
        ok = got["status"] == 200 and page_noindex
        checks.append(_result(
            f"noindex:{path}",
            got["url"],
            ok,
            status=got["status"],
            final_url=got["final_url"],
            noindex=page_noindex,
            error=got["error"],
        ))

    for path in FORBIDDEN_PATHS:
        got = fetch(join_url(base, path), timeout=timeout)
        ok = got["status"] == 404
        checks.append(_result(
            f"forbidden_404:{path}",
            got["url"],
            ok,
            status=got["status"],
            final_url=got["final_url"],
            error=got["error"],
        ))

    return checks


def all_pass(checks: list[dict]) -> bool:
    return all(c["pass"] for c in checks)


def run_with_wait(base: str, timeout: int, wait: int) -> tuple[list[dict], int]:
    """Retry until all checks pass or `wait` seconds have elapsed. Returns (checks, attempts)."""
    deadline = time.monotonic() + max(0, wait)
    attempts = 0
    checks: list[dict] = []
    while True:
        attempts += 1
        checks = evaluate(base, timeout=timeout)
        if all_pass(checks):
            return checks, attempts
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return checks, attempts
        time.sleep(min(RETRY_EVERY, remaining))


def report(meta: dict, checks: list[dict], attempts: int) -> dict:
    ok = all_pass(checks)
    return {
        "schema": "mediawatch.live-check/v1",
        "checked_at_sast": iso_sast(),
        "base_url": meta["base_url"],
        "git_sha": meta["git_sha"],
        "run_id": meta["run_id"],
        "event": meta["event"],
        "attempts": attempts,
        "verdict": "PASS" if ok else "FAIL",
        "checks": [{k: v for k, v in c.items() if k != "expected" or not c["pass"]} for c in checks],
    }


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base-url", default=DEFAULT_BASE)
    ap.add_argument("--out", default="live-check.json")
    ap.add_argument("--sha", default="", help="Git SHA of the deploy being checked")
    ap.add_argument("--run-id", default="", help="GitHub Actions run id, if any")
    ap.add_argument("--event", default="", help="workflow event name (schedule, push, ...)")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="per-request timeout in seconds")
    ap.add_argument("--wait", type=int, default=DEFAULT_WAIT,
                    help="seconds to retry after a fresh Pages deploy before failing")
    args = ap.parse_args(argv)

    meta = {
        "base_url": args.base_url.rstrip("/"),
        "git_sha": args.sha or "",
        "run_id": args.run_id or None,
        "event": args.event or "",
    }
    out = Path(args.out)
    try:
        checks, attempts = run_with_wait(meta["base_url"], timeout=args.timeout, wait=args.wait)
        payload = report(meta, checks, attempts)
    except Exception as exc:
        payload = {
            "schema": "mediawatch.live-check/v1",
            "checked_at_sast": iso_sast(),
            "base_url": meta["base_url"],
            "git_sha": meta["git_sha"],
            "run_id": meta["run_id"],
            "event": meta["event"],
            "attempts": 0,
            "verdict": "FAIL",
            "error": f"{type(exc).__name__}: {exc}",
            "checks": [],
        }
        write_json(out, payload)
        print(f"LIVE CHECK FAIL: {payload['error']}", file=sys.stderr)
        return 1

    write_json(out, payload)
    failed = [c["name"] for c in payload["checks"] if not c["pass"]]
    print(f"LIVE CHECK {payload['verdict']} ({payload['checked_at_sast']} SAST); "
          f"{len(payload['checks'])} checks, {payload['attempts']} attempt(s); wrote {out}")
    if failed:
        print("failed: " + ", ".join(failed), file=sys.stderr)
    return 0 if payload["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
