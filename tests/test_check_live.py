"""Tests for the after-deploy live check (RFC-CHG-MW-003).

The fixture is a local HTTP server. These tests do not fetch the production
site and do not need network access beyond 127.0.0.1.
"""
import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(ROOT / "scripts"))
import check_live  # noqa: E402

WORKFLOW = ROOT / ".github" / "workflows" / "pages.yml"
# Pinned SHAs already used in pages.yml, plus upload-artifact v7.0.2.
KNOWN_SHAS = {
    "actions/checkout@11d5960a326750d5838078e36cf38b85af677262",  # v4.4.0
    "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065",  # v5.6.0
    "actions/upload-pages-artifact@56afc609e74202658d3ffba0e8f6dda462b719fa",  # v3.0.1
    "actions/deploy-pages@d6db90164ac5ed86f2b6aed7e0febac5b3c0c03e",  # v4.0.5
    "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9",  # v7.0.2
}

ROBOTS = "User-agent: *\nDisallow: /\n"
PAGE = """<!doctype html><html lang="en"><head>
<meta name="robots" content="noindex, nofollow">
<title>Publications | MediaWatch SA (draft)</title>
</head><body>
<p class="draft"><strong>Draft preview (DEV).</strong></p>
</body></html>
"""


class _Handler(BaseHTTPRequestHandler):
    # Class-level fixture state, reset per server.
    pages = {}
    status_overrides = {}
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        return

    redirects = {}

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in self.redirects:
            code, location = self.redirects[path]
            self.send_response(code)
            self.send_header("Location", location)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        # Normalise directory URLs the way Pages does: /method/ serves /method/index.html
        key = path
        if key not in self.pages and not key.endswith("/") and key + "/" in self.pages:
            key = key + "/"
        status = self.status_overrides.get(path) or self.status_overrides.get(key)
        if status:
            body = b"" if status != 200 else self.pages.get(key, b"")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if body:
                self.wfile.write(body)
            return
        if key not in self.pages:
            body = b"not found"
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        body = self.pages[key]
        self.send_response(200)
        ctype = "text/plain; charset=utf-8" if key.endswith("robots.txt") else "text/html; charset=utf-8"
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@pytest.fixture
def live_server():
    _Handler.pages = {
        "/": PAGE.encode("utf-8"),
        "/robots.txt": ROBOTS.encode("utf-8"),
        "/method/": PAGE.encode("utf-8"),
        "/coverage/": PAGE.encode("utf-8"),
        "/corrections/": PAGE.encode("utf-8"),
        "/privacy/": PAGE.encode("utf-8"),
        "/p/news24/": PAGE.encode("utf-8"),
    }
    _Handler.status_overrides = {}
    _Handler.redirects = {}
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    host, port = httpd.server_address
    url = f"http://{host}:{port}"
    try:
        yield url, _Handler
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_pass_on_good_fixture(live_server, tmp_path):
    base, _ = live_server
    out = tmp_path / "live-check.json"
    rc = check_live.main(["--base-url", base, "--out", str(out), "--wait", "0",
                          "--sha", "abc", "--run-id", "99", "--event", "test"])
    assert rc == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["verdict"] == "PASS"
    assert payload["git_sha"] == "abc"
    assert payload["run_id"] == "99"
    assert payload["event"] == "test"
    assert payload["checked_at_sast"].endswith("+02:00") or "+02:00" in payload["checked_at_sast"]
    assert all(c["pass"] for c in payload["checks"])
    names = {c["name"] for c in payload["checks"]}
    assert "home_200" in names and "robots_disallow" in names
    assert "forbidden_404:/data" in names and "forbidden_404:/docs/" in names
    assert "forbidden_404:/plan" in names


def test_fail_on_wrong_robots_and_still_writes(live_server, tmp_path):
    base, handler = live_server
    handler.pages["/robots.txt"] = b"User-agent: *\nAllow: /\n"
    out = tmp_path / "live-check.json"
    rc = check_live.main(["--base-url", base, "--out", str(out), "--wait", "0"])
    assert rc == 1
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["verdict"] == "FAIL"
    robots = next(c for c in payload["checks"] if c["name"] == "robots_disallow")
    assert robots["pass"] is False


def test_fail_if_forbidden_path_is_200(live_server, tmp_path):
    base, handler = live_server
    handler.pages["/data"] = PAGE.encode("utf-8")
    handler.pages["/data/"] = PAGE.encode("utf-8")
    out = tmp_path / "live-check.json"
    rc = check_live.main(["--base-url", base, "--out", str(out), "--wait", "0"])
    assert rc == 1
    payload = json.loads(out.read_text(encoding="utf-8"))
    bad = [c for c in payload["checks"] if c["name"].startswith("forbidden_404:/data") and not c["pass"]]
    assert bad


def test_fail_if_home_missing_noindex(live_server, tmp_path):
    """DRAFT stays; only the noindex meta is removed, so that guard fails on its own."""
    base, handler = live_server
    handler.pages["/"] = (
        b"<!doctype html><html lang=\"en\"><head>"
        b"<title>Publications | MediaWatch SA (draft)</title>"
        b"</head><body>"
        b"<p class=\"draft\"><strong>Draft preview (DEV).</strong></p>"
        b"</body></html>"
    )
    out = tmp_path / "live-check.json"
    rc = check_live.main(["--base-url", base, "--out", str(out), "--wait", "0"])
    assert rc == 1
    payload = json.loads(out.read_text(encoding="utf-8"))
    home = next(c for c in payload["checks"] if c["name"] == "home_200")
    assert home["pass"] is False
    assert home["noindex"] is False
    assert home["draft"] is True


def test_fail_if_home_missing_draft(live_server, tmp_path):
    """noindex stays; only the DRAFT markers are removed, so that guard fails on its own."""
    base, handler = live_server
    handler.pages["/"] = (
        b"<!doctype html><html lang=\"en\"><head>"
        b"<meta name=\"robots\" content=\"noindex, nofollow\">"
        b"<title>Publications | MediaWatch SA</title>"
        b"</head><body>"
        b"<p>hello</p>"
        b"</body></html>"
    )
    out = tmp_path / "live-check.json"
    rc = check_live.main(["--base-url", base, "--out", str(out), "--wait", "0"])
    assert rc == 1
    payload = json.loads(out.read_text(encoding="utf-8"))
    home = next(c for c in payload["checks"] if c["name"] == "home_200")
    assert home["pass"] is False
    assert home["noindex"] is True
    assert home["draft"] is False


def test_fail_if_only_method_lacks_noindex(live_server, tmp_path):
    """Other samples stay good; only /method/ loses the robots meta, so that per-page check fails."""
    base, handler = live_server
    handler.pages["/method/"] = (
        b"<!doctype html><html lang=\"en\"><head>"
        b"<title>Method | MediaWatch SA (draft)</title>"
        b"</head><body>"
        b"<p class=\"draft\"><strong>Draft preview (DEV).</strong></p>"
        b"</body></html>"
    )
    out = tmp_path / "live-check.json"
    rc = check_live.main(["--base-url", base, "--out", str(out), "--wait", "0"])
    assert rc == 1
    payload = json.loads(out.read_text(encoding="utf-8"))
    by_name = {c["name"]: c for c in payload["checks"]}
    assert by_name["home_200"]["pass"] is True
    assert by_name["robots_disallow"]["pass"] is True
    assert by_name["noindex:/"]["pass"] is True
    assert by_name["noindex:/coverage/"]["pass"] is True
    assert by_name["noindex:/corrections/"]["pass"] is True
    assert by_name["noindex:/p/news24/"]["pass"] is True
    assert by_name["noindex:/method/"]["pass"] is False
    assert by_name["noindex:/method/"]["noindex"] is False
    assert by_name["noindex:/method/"]["status"] == 200


def test_noindex_ignores_substring_outside_robots_meta(live_server, tmp_path):
    """The exact meta string in a comment, script and body text is not a robots meta."""
    exact = check_live.NOINDEX
    base, handler = live_server
    handler.pages["/"] = (
        "<!doctype html><html lang=\"en\"><head>"
        f"<!-- {exact} -->"
        "<title>Publications | MediaWatch SA (draft)</title>"
        "</head><body>"
        "<script>const x = '" + exact.replace("'", "\\'") + "';</script>"
        "<p>The required tag is " + exact.replace("<", "&lt;") + "</p>"
        '<p class="draft"><strong>Draft preview (DEV).</strong></p>'
        "</body></html>"
    ).encode("utf-8")
    out = tmp_path / "live-check.json"
    rc = check_live.main(["--base-url", base, "--out", str(out), "--wait", "0"])
    assert rc == 1
    payload = json.loads(out.read_text(encoding="utf-8"))
    home = next(c for c in payload["checks"] if c["name"] == "home_200")
    assert home["noindex"] is False
    assert home["draft"] is True
    assert home["pass"] is False
    # Direct helper: attribute-reordered meta still counts; a comment or escaped
    # substring does not (a raw meta tag inside <p> would still be a robots meta).
    reordered = '<meta content="noindex, nofollow" name="robots">'
    assert check_live.has_noindex_nofollow(reordered) is True
    assert check_live.has_noindex_nofollow(f"<!-- {exact} -->") is False
    assert check_live.has_noindex_nofollow(f"<p>{exact.replace('<', '&lt;')}</p>") is False


def test_draft_ignores_markers_in_script_style_or_attributes(live_server, tmp_path):
    """DRAFT markers in script, style or attributes do not satisfy the visible-text check."""
    base, handler = live_server
    handler.pages["/"] = (
        b"<!doctype html><html lang=\"en\"><head>"
        b"<meta name=\"robots\" content=\"noindex, nofollow\">"
        b"<title>Publications | MediaWatch SA</title>"
        b"<style>.x::before { content: \"Draft preview (DEV)\"; }</style>"
        b"</head><body>"
        b"<script>const label = \"Draft preview (DEV)\"; const t = \"MediaWatch SA (draft)\";</script>"
        b"<p title=\"Draft preview (DEV)\" data-label=\"MediaWatch SA (draft)\">hello</p>"
        b"</body></html>"
    )
    out = tmp_path / "live-check.json"
    rc = check_live.main(["--base-url", base, "--out", str(out), "--wait", "0"])
    assert rc == 1
    payload = json.loads(out.read_text(encoding="utf-8"))
    home = next(c for c in payload["checks"] if c["name"] == "home_200")
    assert home["noindex"] is True
    assert home["draft"] is False
    assert home["pass"] is False
    visible = "<p class=\"draft\"><strong>Draft preview (DEV).</strong></p>"
    hidden = '<p title="Draft preview (DEV)">hello</p>'
    assert check_live.has_visible_draft(visible) is True
    assert check_live.has_visible_draft(hidden) is False


def test_forbidden_paths_and_samples_match_rfc():
    assert check_live.FORBIDDEN_PATHS == (
        "/data", "/data/", "/docs", "/docs/", "/plan", "/plan/")
    assert "/" in check_live.SAMPLE_PATHS
    assert "/privacy/" in check_live.SAMPLE_PATHS
    assert check_live.ROBOTS_EXACT == "User-agent: *\nDisallow: /\n"


# ------------------------------------------------------------------ workflow
def _load_workflow():
    # Keep comments by also reading the raw text for SHA pins.
    # PyYAML 1.1 treats the key `on` as boolean True.
    raw = WORKFLOW.read_text(encoding="utf-8")
    doc = yaml.safe_load(raw)
    if True in doc and "on" not in doc:
        doc["on"] = doc.pop(True)
    return doc, raw


def test_workflow_has_nightly_schedule_and_live_check_job():
    doc, raw = _load_workflow()
    cron = doc["on"]["schedule"]
    assert {"cron": "30 1 * * *"} in cron
    # 03:30 Africa/Johannesburg (UTC+2) is recorded next to the cron.
    assert "03:30" in raw and "Africa/Johannesburg" in raw
    assert "live_check" in doc["jobs"]
    job = doc["jobs"]["live_check"]
    assert job["needs"] == "deploy" or job["needs"] == ["deploy"]
    assert job["permissions"]["contents"] == "read"
    assert job["permissions"].get("pages") is None
    assert "id-token" not in job["permissions"]
    assert "actions" not in job["permissions"]


def test_workflow_has_no_contents_write():
    doc, raw = _load_workflow()
    top = doc.get("permissions") or {}
    assert top.get("contents") in (None, "read")
    assert top.get("contents") != "write"
    for name, job in doc["jobs"].items():
        perms = job.get("permissions") or {}
        assert perms.get("contents") in (None, "read"), name
        assert perms.get("contents") != "write", name
        assert perms.get("actions") != "write", name


def test_checkouts_do_not_persist_credentials():
    doc, _ = _load_workflow()
    checkouts = []
    for job in doc["jobs"].values():
        for step in job.get("steps") or []:
            if isinstance(step.get("uses"), str) and "actions/checkout@" in step["uses"]:
                checkouts.append(step)
    assert len(checkouts) == 2
    for step in checkouts:
        assert step.get("with", {}).get("persist-credentials") is False


def test_workflow_actions_are_pinned_shas():
    raw = WORKFLOW.read_text(encoding="utf-8")
    uses = []
    for line in raw.splitlines():
        if "uses:" in line:
            uses.append(line.split("uses:", 1)[1].strip().split()[0])
    assert uses, "expected pinned actions"
    for u in uses:
        action, sha = u.split("@")
        assert len(sha) == 40 and all(c in "0123456789abcdef" for c in sha), u
        assert u in KNOWN_SHAS, u


def test_artifact_retention_is_90_days_and_unique_per_run():
    doc, raw = _load_workflow()
    job = doc["jobs"]["live_check"]
    upload = [s for s in job["steps"] if isinstance(s.get("uses"), str) and "upload-artifact@" in s["uses"]]
    assert len(upload) == 1
    step = upload[0]
    assert step["with"]["retention-days"] == 90
    assert step["with"]["path"] == "live-check.json"
    assert "${{ github.run_id }}" in str(step["with"]["name"])
    assert step.get("if") == "always()"


def test_run_blocks_have_no_template_expressions():
    """github.* (and other ${{ }} expressions) used by run: steps must be in env:."""
    raw = WORKFLOW.read_text(encoding="utf-8")
    in_run = False
    run_indent = None
    for line in raw.splitlines():
        if re.match(r"^\s+run:\s*\|?\s*$", line) or re.match(r"^\s+run:\s+\S", line):
            in_run = True
            run_indent = len(line) - len(line.lstrip())
            assert "${{" not in line, line
            continue
        if in_run:
            if line.strip() and (len(line) - len(line.lstrip())) <= run_indent:
                in_run = False
            else:
                assert "${{" not in line, line



def test_same_host_redirect_is_followed(live_server):
    """A 302 that stays on the same host is followed and the final page is used."""
    base, handler = live_server
    handler.redirects["/via-redirect"] = (302, base + "/method/")
    got = check_live.fetch(base + "/via-redirect")
    assert got["error"] is None
    assert got["status"] == 200
    assert got["final_url"].rstrip("/") == (base + "/method/").rstrip("/")
    assert check_live.has_noindex_nofollow(got["body"])


def test_fail_on_cross_host_redirect(live_server, tmp_path):
    """A Location on another host is not followed and the live check fails."""
    base, handler = live_server
    # Second listener on 127.0.0.1, advertised as localhost so the hostnames differ.
    other = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=other.serve_forever, daemon=True)
    thread.start()
    try:
        _, other_port = other.server_address
        other_url = f"http://localhost:{other_port}/"
        handler.redirects["/"] = (302, other_url)
        # Direct fetch must not return the other host's body.
        got = check_live.fetch(base + "/")
        assert got["status"] is None
        assert got["body"] == ""
        assert got["error"] and "cross-host redirect" in got["error"]
        assert "localhost" in got["error"]

        out = tmp_path / "live-check.json"
        rc = check_live.main(["--base-url", base, "--out", str(out), "--wait", "0"])
        assert rc == 1
        payload = json.loads(out.read_text(encoding="utf-8"))
        assert payload["verdict"] == "FAIL"
        home = next(c for c in payload["checks"] if c["name"] == "home_200")
        assert home["pass"] is False
        assert home["error"] and "cross-host redirect" in home["error"]
    finally:
        other.shutdown()
        other.server_close()
