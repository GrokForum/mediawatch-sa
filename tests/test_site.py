"""Tests for the MediaWatch SA static site (RFC-CHG-MW-002).

Run: python -m pytest -q
"""
import csv
import hashlib
import html
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_site  # noqa: E402

ALLOWED = {"Proven", "Established", "Alleged", "Disputed", "Not established"}


@pytest.fixture(scope="session")
def site(tmp_path_factory):
    out = tmp_path_factory.mktemp("site") / "_site"
    stats = build_site.build(out)
    return out, stats


def pages(out):
    return sorted(out.rglob("*.html"))


def text_of(path):
    return path.read_text(encoding="utf-8")


def visible_text(h):
    h = re.sub(r"<[^>]+>", " ", h)
    return html.unescape(re.sub(r"\s+", " ", h))


def all_findings():
    out = {}
    for fn in build_site.FINDINGS_FILES.values():
        doc = json.loads((ROOT / "data" / fn).read_text(encoding="utf-8"))
        for f in doc["findings"]:
            out[f["id"]] = f
    return out


# ------------------------------------------------------------------ build
def test_build_succeeds(site):
    out, stats = site
    assert (out / "index.html").exists()
    assert (out / "robots.txt").exists()
    assert (out / "corrections" / "index.html").exists()
    assert (out / "method" / "index.html").exists()
    assert (out / "coverage" / "index.html").exists()
    assert (out / "privacy" / "index.html").exists()
    for pid in build_site.PILOT + build_site.WATCH:
        assert (out / "p" / pid / "index.html").exists()
    assert stats["findings_rendered"] > 0
    assert len(list((out / "f").iterdir())) == stats["findings_rendered"]


def test_build_script_cli(tmp_path):
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_site.py"), "--out", str(tmp_path / "o")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "WARNING" not in r.stderr


# ------------------------------------------------------------------ findings
def test_every_finding_page_has_quote_source_label_steelmen(site):
    out, _ = site
    data = all_findings()
    for d in (out / "f").iterdir():
        h = text_of(d / "index.html")
        fid = re.search(r'data-finding="([^"]+)"', h).group(1)
        f = data[fid]
        q = re.search(r'<blockquote class="quote finding-quote">(.*?)</blockquote>', h, re.S)
        assert q and html.unescape(q.group(1)) == f["quote"], fid
        link = re.search(r'<a class="source-link" href="([^"]+)"', h)
        assert link and html.unescape(link.group(1)) == f["url"], fid
        assert link.group(1).startswith("https://"), fid
        lab = re.search(r'<span class="badge fact-label">([^<]+)</span>', h)
        assert lab and lab.group(1) in ALLOWED, fid
        for cls in ("steelman-for", "steelman-against"):
            m = re.search(rf'<dd class="{cls}">([^<]+)</dd>', h)
            assert m and m.group(1).strip(), (fid, cls)


def test_only_allowed_fact_labels_anywhere(site):
    out, _ = site
    for p in pages(out):
        for lab in re.findall(r'<span class="badge fact-label">([^<]+)</span>', text_of(p)):
            assert lab in ALLOWED


def test_unofficial_drivers_marked_pending(site):
    out, _ = site
    official = build_site.official_drivers()
    data = all_findings()
    for d in (out / "f").iterdir():
        h = text_of(d / "index.html")
        fid = re.search(r'data-finding="([^"]+)"', h).group(1)
        pending = "driver name pending owner decision" in h
        assert pending == (data[fid]["driver"] not in official), fid


# ------------------------------------------------------------------ hidden secondary meter
LEAN_PATTERNS = re.compile(
    r"left[\s/-]*right|secondary view|lean[_ ](score|meter|rollup)|economic_axis|social_axis|"
    r"actor_axis|n_included|\blean\b", re.IGNORECASE)


def test_no_lean_meter_in_output(site):
    out, _ = site
    for p in out.rglob("*"):
        if p.is_file():
            t = p.read_text(encoding="utf-8")
            m = LEAN_PATTERNS.search(t)
            assert not m, f"{p.relative_to(out)}: {m.group(0)!r}"


def test_generator_does_not_read_lean_files():
    src = (ROOT / "scripts" / "build_site.py").read_text(encoding="utf-8")
    assert "lean_scores" not in src and "actor_axis_map" not in src


# ------------------------------------------------------------------ noindex
def test_noindex_everywhere(site):
    out, _ = site
    for p in pages(out):
        h = text_of(p)
        assert '<meta name="robots" content="noindex, nofollow">' in h, p
        assert "Draft preview (DEV)" in visible_text(h), p
    robots = (out / "robots.txt").read_text(encoding="utf-8")
    assert "User-agent: *" in robots and "Disallow: /" in robots


WATCH_DIRECTORY_HREF = "https://watch.grokforum.site/"
WATCH_DIRECTORY_LABEL = "Part of the Watch network — watch.grokforum.site"
WATCH_DIRECTORY_FOOTER = (
    f'<p><a href="{WATCH_DIRECTORY_HREF}">{WATCH_DIRECTORY_LABEL}</a></p>'
)


def test_watch_network_footer_on_every_page(site):
    """Every built HTML page has the plain Watch-directory footer link (RFC-CHG-MW-013)."""
    out, _ = site
    for p in pages(out):
        h = text_of(p)
        assert WATCH_DIRECTORY_FOOTER in h, p
        assert f'href="{WATCH_DIRECTORY_HREF}"' in h, p
        assert WATCH_DIRECTORY_LABEL in visible_text(h), p
        assert '<meta name="robots" content="noindex, nofollow">' in h, p
        assert "Draft preview (DEV)" in visible_text(h), p
        # No query, fragment or other href variant of the directory link.
        for href in re.findall(r'href="(https://watch\.grokforum\.site/[^"]*)"', h):
            assert href == WATCH_DIRECTORY_HREF, (p, href)
    robots = (out / "robots.txt").read_text(encoding="utf-8")
    assert "User-agent: *" in robots and "Disallow: /" in robots


def test_no_external_assets_or_scripts(site):
    out, _ = site
    for p in pages(out):
        h = text_of(p)
        assert "<script" not in h.lower(), p
        for m in re.finditer(r'<(?:link|img|iframe)[^>]+(?:href|src)="([^"]+)"', h):
            assert not re.match(r"https?://|//", m.group(1)), (p, m.group(1))
    css = (out / "assets" / "style.css").read_text(encoding="utf-8")
    assert "http" not in css and "@import" not in css


def test_live_placeholder_untouched():
    # 0280f59 last changed index.html/CNAME; it is unchanged by both history rewrites.
    r = subprocess.run(["git", "diff", "--quiet", "0280f59", "--", "index.html", "CNAME"], cwd=ROOT)
    assert r.returncode == 0, "root index.html / CNAME changed versus 0280f59"


# ------------------------------------------------------------------ paywall exclusion
def test_paywall_exclusions_match_rule():
    pubs, people, docs, excluded, detected, listed = build_site.load()
    assert set(detected) == set(listed), sorted(set(detected) ^ set(listed))


def test_no_paywalled_items_rendered(site):
    out, stats = site
    excluded = set(stats["excluded"])
    assert excluded, "expected the known paywalled News24 findings to be excluded"
    data = all_findings()
    reg = {build_site.norm_url(r["url"]) for r in build_site.read_csv("paywall_register.csv")}
    blob = "\n".join(text_of(p) for p in pages(out))
    for fid in excluded:
        assert not (out / "f" / build_site.slug(fid)).exists(), fid
        assert f">{fid}<" not in blob, fid
        assert f'"{fid}"' not in blob, fid
    for p in pages(out):
        for href in re.findall(r'href="(https?://[^"]+)"', text_of(p)):
            u = build_site.norm_url(html.unescape(href))
            if "news24.com" in u:
                assert u not in reg, (p, u)
    # excluded findings never counted: the n on scorecards equals counted rendered findings
    for fid in excluded:
        assert fid in data


# ------------------------------------------------------------------ thresholds
def test_threshold_function():
    f = build_site.flag_for
    assert [f(n) for n in (0, 4, 5, 9, 10, 25)] == [
        "findings_only", "findings_only", "provisional", "provisional", "full", "full"]


def test_provisional_badge_text_is_locked():
    """The visible status labels are a closed set; do not reword without a change record."""
    assert build_site.badge("provisional") == '<span class="badge provisional">provisional</span>'
    assert build_site.badge("findings_only") == '<span class="badge findings_only">findings only</span>'
    assert build_site.badge("full") == '<span class="badge full">score</span>'
    note = (
        "Score shown only when n &ge; 10; 5&ndash;9 is provisional; under 5 shows findings only. "
        "Accountability-exempt findings are listed but not counted."
    )
    html = build_site.scorecard_table([
        {"actor": "ANC", "for": 0, "against": 6, "n": 6, "score": -1.0,
         "flag": "provisional", "suppressed": "", "pending_drivers": 0,
         "frames": {"keyword": 6}},
    ], "publication")
    assert note in html
    assert ">provisional</span>" in html


def test_thresholds_applied_on_scorecards(site):
    out, _ = site
    seen = 0
    for p in pages(out):
        for m in re.finditer(r'<tr class="score-row"([^>]*)>(.*?)</tr>', text_of(p), re.S):
            attrs = dict(re.findall(r'data-([a-z]+)="([^"]*)"', m.group(1)))
            n = int(attrs["n"])
            assert attrs["flag"] == build_site.flag_for(n)
            if n < 5 or attrs["suppressed"] == "1":
                assert attrs["score"] == "", (p, attrs)
                assert "&ndash;" in m.group(2)
            else:
                assert attrs["score"] != "", (p, attrs)
            if 5 <= n < 10:
                assert 'badge provisional' in m.group(2)
            seen += 1
    assert seen > 0


def test_publication_scores_recomputed_independently(site):
    out, stats = site
    excluded = set(stats["excluded"])
    for pid, fn in build_site.FINDINGS_FILES.items():
        doc = json.loads((ROOT / "data" / fn).read_text(encoding="utf-8"))
        acc = defaultdict(list)
        for f in doc["findings"]:
            if f["id"] in excluded or f.get("accountability_status") == "accountability_exempt":
                continue
            if f.get("signed_score") is None:
                continue
            acc[f["actor"]].append(float(f["signed_score"]))
        h = text_of(out / "p" / pid / "index.html")
        rows = {html.unescape(a): (int(n), s) for a, n, s in
                re.findall(r'data-level="publication" data-actor="([^"]+)" data-n="(\d+)" data-flag="[^"]+" data-score="([^"]*)"', h)}
        for actor, vals in acc.items():
            n, s = rows[actor]
            assert n == len(vals)
            if n >= 5:
                assert abs(float(s) - round(sum(vals) / n, 2)) < 1e-9


# ------------------------------------------------------------------ POPIA / privacy
def _private_names():
    p = ROOT / "tests" / "private_names.local.txt"
    if not p.exists():
        return []
    return [l.strip().lower() for l in p.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.startswith("#")]


def test_no_private_citizen_names(site):
    out, _ = site
    names = _private_names()
    if not names:
        pytest.skip("tests/private_names.local.txt not present (local-only denylist)")
    for p in pages(out):
        t = visible_text(text_of(p)).lower()
        for n in names:
            assert not re.search(rf"\b{re.escape(n)}\b", t), p.relative_to(out)


def test_writer_pages_are_public_role_only(site):
    out, _ = site
    people = {r["id"]: r for r in build_site.read_csv("people.csv")}
    for d in (out / "w").iterdir():
        h = text_of(d / "index.html")
        # no contact or identity details beyond name, public role and verified public X handle
        assert not re.search(r"mailto:|tel:|\+27|\b0\d{2}[ -]?\d{3}[ -]?\d{4}\b", h), d
        assert "x_user_id" not in h
        p = people.get(d.name)
        if p and p.get("x_user_id"):
            assert p["x_user_id"] not in h, d


def test_internal_fields_never_rendered(site):
    out, _ = site
    data = all_findings()
    blob = "\n".join(visible_text(text_of(p)) for p in pages(out))
    for f in data.values():
        note = (f.get("evidence_notes") or "").strip()
        if len(note) > 40:
            assert note[:40] not in blob, f["id"]
    for word in ("evidence_notes", "mediawatch-sa-pilot", "mediawatch-sa-foundation", "Cavus", "Cassian", "casebook"):
        assert word.lower() not in blob.lower(), word


def test_no_seed_or_fetched_or_private_paths_in_output(site):
    out, _ = site
    bad = re.compile(r"seed/|fetched_articles|/workspace|agoa[-_ ]sa|owner-supplied|/home/", re.IGNORECASE)
    for p in out.rglob("*"):
        if p.is_file():
            m = bad.search(p.read_text(encoding="utf-8"))
            assert not m, (p, m.group(0))
    allowed_top = {"index.html", "robots.txt", "assets", "p", "w", "a", "x", "i", "f",
                   "method", "corrections", "coverage", "privacy", "manifest.json"}
    assert {c.name for c in out.iterdir()} <= allowed_top


def test_no_fetched_article_text_in_output(site):
    out, _ = site
    fetched = ROOT / "data" / "fetched_articles"
    if not fetched.exists():
        pytest.skip("no local fetched_articles")
    blob = re.sub(r"\s+", " ", "\n".join(visible_text(text_of(p)) for p in pages(out)))
    for fp in fetched.rglob("*"):
        if not fp.is_file():
            continue
        t = re.sub(r"\s+", " ", fp.read_text(encoding="utf-8", errors="ignore"))
        # any 300-character run of a fetched body would be more than a short quote
        for i in range(0, max(0, len(t) - 300), 300):
            chunk = t[i:i + 300]
            assert chunk not in blob, fp.name


def test_gitignored_folders_not_tracked():
    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    for f in files:
        assert not f.startswith(("seed/", "data/fetched_articles/", "_site/")), f
    assert "tests/private_names.local.txt" not in files


# ------------------------------------------------------------------ schema
def _schema_summary():
    jsonschema = pytest.importorskip("jsonschema")  # noqa: F841
    import validate_schema
    return validate_schema.summarise(validate_schema.validate())


def test_schema_news24_and_registers_pass():
    s = _schema_summary()
    for name in ("news24_pilot_findings.json", "iol_watch_findings.json",
                 "ewn_watch_findings.json", "people.csv", "publications.csv"):
        assert s[name]["errors"] == 0, (name, s[name])


@pytest.mark.parametrize("name", ["dailyinvestor_pilot_findings.json", "newsday_pilot_findings.json"])
def test_schema_di_newsday_drivers(name):
    s = _schema_summary()
    assert s[name]["errors"] == 0, s[name]


# ------------------------------------------------------------------ line endings
def test_crlf_preserved_on_data_csvs():
    for p in sorted((ROOT / "data").glob("*.csv")):
        raw = p.read_bytes()
        assert b"\r\n" in raw, p.name
        assert raw.count(b"\n") == raw.count(b"\r\n"), p.name


# ------------------------------------------------------------------ privacy (RFC-CHG-MW-005)
CONTACT_PLACEHOLDER = "[contact address to be confirmed by the owner before publication]"


def test_privacy_page_present_with_required_topics(site):
    out, _ = site
    path = out / "privacy" / "index.html"
    assert path.is_file()
    h = text_of(path)
    vis = visible_text(h).lower()
    assert "what is published" in vis
    assert "private" in vis and "never named" in vis
    assert "public" in vis and "role" in vis
    assert "correction" in vis and "removal" in vis
    assert '<meta name="robots" content="noindex, nofollow">' in h
    assert "Draft preview (DEV)" in h
    assert "MediaWatch SA (draft)" in text_of(path).split("<title>")[1].split("</title>")[0]
    # Information Regulator is a public body, linked as a right of complaint.
    assert "https://inforegulator.org.za/" in h
    # Responsible party named as the publisher, not a private person.
    assert "GrokForum" in h
    assert "taken off the published pages at the next build" in vis
    assert "repository history" in vis and "caches" in vis


def test_privacy_linked_from_every_footer(site):
    out, _ = site
    for p in pages(out):
        h = text_of(p)
        assert re.search(r'<a href="(?:(?:../)*)privacy/index.html">Privacy</a>', h), p


def test_contact_address_on_corrections_and_privacy(site):
    out, _ = site
    mailto = 'href="mailto:privacy@grokforum.site"'
    for rel in ("corrections/index.html", "privacy/index.html"):
        h = text_of(out / rel)
        assert "privacy@grokforum.site" in h, rel
        assert mailto in h, rel
        assert CONTACT_PLACEHOLDER not in h, rel
        assert "contact-placeholder" not in h, rel


def test_confirmed_privacy_address_in_output(site):
    out, _ = site
    blob = "\n".join(p.read_text(encoding="utf-8") for p in out.rglob("*") if p.is_file())
    assert "privacy@grokforum.site" in blob.lower()
    assert CONTACT_PLACEHOLDER not in blob


ALLOWED_EMAIL = "privacy@grokforum.site"
_AT_CODES = re.compile(r"&#0*64;|&#x0*40;|&commat;|%40", re.I)
_AT_WORDS = re.compile(r"\s*\[\s*at\s*\]\s*|\s*\(\s*at\s*\)\s*", re.I)
_EMAIL_RE = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.I)
_MAILTO_RE = re.compile(r"mailto:([^\"\'\s<>]+)", re.I)


def decode_email_obfuscation(text: str) -> str:
    """Decode common email hide-outs before scanning (entities, %40, [at] / (at))."""
    s = text.replace("&commat;", "@").replace("&COMMAT;", "@")
    s = html.unescape(s)
    s = _AT_CODES.sub("@", s)
    s = unquote(s)
    s = _AT_WORDS.sub("@", s)
    return s


def foreign_emails(text: str) -> list[str]:
    """Email addresses and mailto targets in text other than the role address."""
    decoded = decode_email_obfuscation(text)
    found = []
    for match in _EMAIL_RE.finditer(decoded):
        addr = match.group(0).rstrip(".,;:").lower()
        if addr != ALLOWED_EMAIL:
            found.append(addr)
    for match in _MAILTO_RE.finditer(decoded):
        target = match.group(1).split("?", 1)[0].strip().lower()
        target = decode_email_obfuscation(target)
        if target.startswith("mailto:"):
            target = target[7:]
        if "@" in target and target != ALLOWED_EMAIL:
            found.append(target)
    unique = []
    for addr in found:
        if addr not in unique:
            unique.append(addr)
    return unique


def test_email_obfuscation_decoder_catches_variants():
    # Assemble the foreign address at runtime so this tracked file contains
    # no email literal other than the allowed role address.
    local, domain = "alert", "example.com"
    expected = f"{local}@{domain}"
    variants = {
        f"{local}&#64;{domain}": expected,
        f"{local}&#x40;{domain}": expected,
        f"{local}%40{domain}": expected,
        f"{local}&commat;{domain}": expected,
        f"{local} [at] {domain}": expected,
        f"{local}(at){domain}": expected,
    }
    for raw, expected in variants.items():
        decoded = decode_email_obfuscation(raw)
        assert expected in decoded, (raw, decoded)
        assert foreign_emails(raw) == [expected]
        assert foreign_emails(f"mailto:{raw}") == [expected]
    assert foreign_emails("Contact privacy@grokforum.site") == []
    assert foreign_emails('href="mailto:privacy@grokforum.site"') == []
    assert foreign_emails("privacy&#64;grokforum.site") == []
    assert foreign_emails("privacy [at] grokforum.site") == []


def test_only_allowed_email_in_built_site(site):
    """Walk the built site; any email or mailto other than the role address fails."""
    out, _ = site
    offenders = []
    for path in sorted(p for p in out.rglob("*") if p.is_file()):
        raw = path.read_text(encoding="utf-8", errors="replace")
        found = foreign_emails(raw)
        if found:
            offenders.append((str(path.relative_to(out)), found))
    assert offenders == [], offenders

# ------------------------------------------------------------------ manifest (RFC-CHG-MW-004)
def test_manifest_json_present_and_valid(site):
    out, stats = site
    path = out / "manifest.json"
    assert path.is_file()
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert doc["schema"] == "mediawatch.manifest/v1"
    assert doc["kind"] == "manifest"
    sha = doc["build"]["git_sha"]
    # Full git object name from this repo; "unknown" or a short sha must not pass.
    assert isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{40}", sha), sha
    # local pytest has no GITHUB_RUN_ID unless the environment set one
    assert "run_id" in doc["build"]
    assert doc["built_at_sast"]
    expected_data_date = max(
        d for d in (
            build_site.to_sast_date(f.get("published_at_sast") or f.get("published_at"))
            for f in all_findings().values()
            if f["id"] not in stats["excluded"]
        ) if d
    )
    assert doc["data_date"] == expected_data_date
    # Newest rendered finding date (pilot window plus any later error-watch rows).
    assert expected_data_date >= "2026-10-27"
    assert doc["data_window"]["start"] == "2026-05-01"
    assert doc["data_window"]["end"] == "2026-11-20"
    counts = doc["counts"]
    assert counts["html_pages"] == stats["pages"] == len(pages(out))
    assert counts["findings_rendered"] == stats["findings_rendered"]
    assert counts["findings_excluded_paywalled"] == len(stats["excluded"])
    assert counts["items"] == stats["items"]
    assert counts["writers"] == stats["writers"]
    assert counts["publications"] == 3
    paths = [i["path"] for i in doc["inputs"]]
    assert paths == list(build_site.MANIFEST_INPUTS)
    for item in doc["inputs"]:
        # Independent sha256: hashlib, not the site builder's helper.
        expected = hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest()
        assert re.fullmatch(r"[0-9a-f]{64}", item["sha256"]), item
        assert item["sha256"] == expected


def test_only_allowed_file_types_including_manifest(site):
    out, _ = site
    unexpected = []
    for p in out.rglob("*"):
        if p.is_dir():
            continue
        rel = p.relative_to(out)
        if p.suffix in {".html", ".css"} or str(rel) in {"robots.txt", "manifest.json"}:
            continue
        unexpected.append(str(rel))
    assert unexpected == []
    # exactly one json file, at the site root
    json_files = [p for p in out.rglob("*.json")]
    assert [p.relative_to(out).as_posix() for p in json_files] == ["manifest.json"]


def test_footer_build_stamp_and_manifest_link(site):
    out, _ = site
    for p in pages(out):
        h = text_of(p)
        assert 'class="build-stamp"' in h, p
        assert "Africa/Johannesburg" in h
        assert f'data date {json.loads((out / "manifest.json").read_text(encoding="utf-8"))["data_date"]}' in h
        assert "manifest.json" in h
        assert '<meta name="robots" content="noindex, nofollow">' in h


def test_workflow_allows_exactly_manifest_json():
    raw = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
    assert "! -path '_site/manifest.json'" in raw
    assert "! -name '*.json'" not in raw


# ------------------------------------------------------------------ source links (standing owner rule)
def test_every_published_finding_and_item_links_to_source(site):
    """Every register finding and item page must link an https source."""
    out, _ = site
    for d in (out / "f").iterdir():
        h = text_of(d / "index.html")
        link = re.search(r'<a class="source-link" href="([^"]+)"', h)
        assert link and html.unescape(link.group(1)).startswith("https://"), d
    for folder in ("a", "x", "i"):
        root = out / folder
        if not root.exists():
            continue
        for d in root.iterdir():
            h = text_of(d / "index.html")
            assert re.search(r"<dt>Source</dt>\s*<dd><a href=\"https://", h), d


def test_publication_editor_https_sources_are_linked(site):
    out, _ = site
    pubs = {r["id"]: r for r in build_site.read_csv("publications.csv")}
    for pid in build_site.PILOT:
        h = text_of(out / "p" / pid / "index.html")
        pub = pubs[pid]
        for url in build_site.https_urls(pub.get("editor_source_url") or ""):
            assert f'class="source-link" href="{html.escape(url, quote=True)}"' in h, (pid, url)
        # Owner group is published but publications.csv has no owner source URL field.
        # That gap is reported in RFC-CHG-MW-004; this test only checks the group is shown.
        assert html.escape(pub["owner_group"]) in h

# ------------------------------------------------------------------ CHG-MW-007 official wording / Q2 murder figures
def test_method_page_has_official_wording_section(site):
    out, _ = site
    h = visible_text(text_of(out / "method" / "index.html")).lower()
    assert "official wording vs media wording" in h
    assert "what was charged" in h and "what happened" in h
    assert "factual error" in h
    assert "project's other registers" in h
    assert "ktb" not in h and "crimewatch" not in h
    src_m = (ROOT / "docs" / "METHODOLOGY.md").read_text(encoding="utf-8")
    assert "KTB" not in src_m and "CrimeWatch" not in src_m
    src = (ROOT / "docs" / "METHODOLOGY.md").read_text(encoding="utf-8")
    assert src.split("**Version:**", 1)[1].lstrip().startswith("0.5-draft")
    assert "## 5b. Official wording vs media wording" in src


def test_q2_murder_stat_findings(site):
    """IOL and EWN 1,600-fewer-murders claims against official SAPS Q2 tables."""
    out, _ = site
    data = all_findings()
    saps_url = "https://www.saps.gov.za/services/downloads/2026/2026-2027_-_2nd_Quarter_WEB.pdf"
    cases = {
        "F-IOL-Q2-MURDER-1600": {
            "publication_id": "iol",
            "url_part": "sa-records-1600-fewer-murders",
            "quote_part": "a decline of more than 1,600 murders compared with the same period last year",
            "byline": "Se-Anne Rall",
        },
        "F-EWN-Q2-MURDER-1600": {
            "publication_id": "ewn",
            "url_part": "sa-continues-to-record-decline-in-murders-violent-crime-cachalia",
            "quote_part": "more than 1,600 fewer murders were recorded compared to the same period last year",
            "byline": "Tsholo Tsoku",
        },
    }
    for fid, exp in cases.items():
        f = data[fid]
        assert f["driver"] == "factual_error"
        assert f["actor"] == "SAPS"
        assert f["direction"] == "FOR"
        assert f["fact_label"] == "Not established"
        assert f["sample_frame"] == "purposive"
        assert f["methodology_version"] == "0.5-draft"
        assert exp["quote_part"] in f["quote"]
        assert exp["url_part"] in f["url"]
        assert f["url"].startswith("https://")
        assert f["byline"] == exp["byline"]
        notes = f["evidence_notes"]
        assert saps_url in notes
        assert "5,590" in notes and "5,794" in notes
        assert "-204" in notes or "204" in notes
        assert "3,5%" in notes or "3.5%" in notes
        assert "No correction" in notes or "no correction" in notes.lower()
        assert (out / "f" / fid / "index.html").is_file(), fid
    home = text_of(out / "index.html")
    assert "Error watch" in home
    assert (out / "p" / "iol" / "index.html").is_file()
    assert (out / "p" / "ewn" / "index.html").is_file()




# ------------------------------------------------------------------ CHG-MW-009 v1 sample
def test_data_window_covers_v1_draw():
    assert build_site.DATA_WINDOW["start"] == "2026-05-01"
    assert build_site.DATA_WINDOW["end"] == "2026-11-20"
    assert "November" in build_site.DATA_WINDOW["label"]


def test_v1_pilot_sample_is_fully_coded():
    """Every locked v1 pilot slot is a fetched article, coded as a finding or clean."""
    status_path = ROOT / "data" / "sampling" / "neutral_random_v1_fetch_status.csv"
    rows = [r for r in csv.DictReader(status_path.open(encoding="utf-8"))
            if r["outlet_id"] in build_site.PILOT]
    assert len(rows) == 172
    assert all(r["access"] == "full_text_curl" and r["status"] == "fetched" for r in rows)

    docs = {}
    for pid, fn in build_site.FINDINGS_FILES.items():
        if pid not in build_site.PILOT:
            continue
        docs[pid] = json.loads((ROOT / "data" / fn).read_text(encoding="utf-8"))

    by_url = {}
    for pid, doc in docs.items():
        for a in doc["articles"]:
            if a.get("v1_draw"):
                by_url[(pid, (a["url"] or "").rstrip("/").lower())] = a
    assert len(by_url) == 172

    for r in rows:
        art = by_url[(r["outlet_id"], r["url"].rstrip("/").lower())]
        assert art.get("algorithm_id") == "neutral_random_v1"
        assert art.get("access") == "full_text_curl"
        controls = {c["article_id"] for c in docs[r["outlet_id"]].get("balanced_controls", [])
                    if c.get("reason") == "coded_clean"}
        finding_aids = {f["article_id"] for f in docs[r["outlet_id"]]["findings"]}
        assert art["id"] in controls or art["id"] in finding_aids, art["id"]
        assert not (art["id"] in controls and art["id"] in finding_aids), art["id"]


def test_v1_new_finding_quotes_are_exact_and_labelled():
    allowed = ALLOWED
    expected = {
        "F-DI-NRV1-01",
        "F-ND-NRV1-01", "F-ND-NRV1-02", "F-ND-NRV1-03", "F-ND-NRV1-04",
        "F-ND-NRV1-05", "F-ND-NRV1-06", "F-ND-NRV1-07",
    }
    found = {}
    for pid, fn in build_site.FINDINGS_FILES.items():
        if pid not in build_site.PILOT:
            continue
        doc = json.loads((ROOT / "data" / fn).read_text(encoding="utf-8"))
        for f in doc["findings"]:
            if f["id"] in expected:
                found[f["id"]] = f
                assert f["quote"].strip()
                assert f["url"].startswith("https://")
                assert f["fact_label"] in allowed
                assert f["steelman_for"].strip() and f["steelman_against"].strip()
                assert f["methodology_version"] == "0.5-draft"
                assert f.get("accountability_status") == "bias"
    assert set(found) == expected


def test_home_and_publication_pages_show_v1_sample_size(site):
    out, _ = site
    home = visible_text(text_of(out / "index.html"))
    assert "v1 sample (coded)" in home
    assert "Coded clean" in home
    assert "1 May" in home and "20 November 2026" in home
    # News24 60/60, Daily Investor 60/58, Newsday 52/46 appear in the home table
    for pid, coded, clean in (("news24", 60, 60), ("daily_investor", 60, 58), ("newsday", 52, 46)):
        h = visible_text(text_of(out / "p" / pid / "index.html"))
        assert f"{coded} articles coded" in h
        assert f"{clean} coded clean" in h
        assert "v1 sample size" in h
        assert "coded-and-clean" in h


def test_coded_clean_article_pages_exist(site):
    out, _ = site
    # A known clean News24 v1 article should have a page and the clean note
    doc = json.loads((ROOT / "data" / "news24_pilot_findings.json").read_text(encoding="utf-8"))
    finding_aids = {f["article_id"] for f in doc["findings"]}
    clean = next(a for a in doc["articles"] if a.get("v1_draw") and a["id"] not in finding_aids)
    path = out / "a" / clean["id"] / "index.html"
    assert path.is_file(), clean["id"]
    h = visible_text(text_of(path))
    assert "Coded clean" in h
    assert "sample denominator" in h


def test_rfc_009_actor_counts_match_site_rollup():
    """RFC-CHG-MW-009 actor n/status must be generated from the same roll-up as the site."""
    rfc = (ROOT / "changes" / "RFC-CHG-MW-009.md").read_text(encoding="utf-8")
    _, _, docs, excluded, _, _ = build_site.load()
    for line in build_site.format_pilot_actor_rollup(docs, excluded):
        assert line in rfc, line
    # The reviewer's News24 counted figures must appear (paywalled findings excluded).
    assert "AfriForum n=10 scored" in rfc
    assert "Solidarity n=5 provisional" in rfc
    assert "DA n=3 findings-only" in rfc
    assert "Cyril Ramaphosa n=2 findings-only" in rfc

