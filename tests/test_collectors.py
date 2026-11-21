"""Collectors, TLS error logging, and the locked neutral_random_v1 rule."""

from __future__ import annotations

import csv
import io
import json
import ssl
import urllib.error
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "scripts"))
import collect
import sample_neutral_random as sampler

# Committed fake-name fixture for synthetic draw tests. The real denylist
# (tests/private_names.local.txt) is gitignored and is required only for a live draw.
SYNTHETIC_NAMES = ROOT / "tests" / "fixtures" / "synthetic_private_names.txt"

SRC = (ROOT / "scripts" / "collect.py").read_text(encoding="utf-8")


def test_collector_source_never_disables_verification():
    lowered = SRC.lower()
    for needle in ("verify=false", "verify = false", "cert_none", "unverified_context", "check_hostname = false"):
        assert needle not in lowered
    assert " -k" not in SRC and not any(tok == "-k" for tok in SRC.split())
    # The default context helper must use create_default_context and nothing weaker.
    assert "ssl.create_default_context()" in SRC


def test_default_ssl_context_is_strict():
    ctx = collect.default_ssl_context()
    assert ctx.verify_mode == ssl.CERT_REQUIRED
    assert ctx.check_hostname is True


def _config():
    return {
        "outlets": {
            "newsday": {
                "name": "Newsday",
                "rss": ["https://newsday.co.za/feed/"],
                "sitemaps": [],
            }
        }
    }


def test_tls_error_is_logged_and_run_continues(tmp_path):
    err_path = tmp_path / "collector_errors.csv"
    run_id = "test-run-1"
    log = collect.ErrorLog(err_path, run_id)

    def opener(req, timeout, context):
        assert context.verify_mode == ssl.CERT_REQUIRED
        raise urllib.error.URLError(
            ssl.SSLCertVerificationError("unable to get local issuer certificate")
        )

    collector = collect.Collector(_config(), log, delay_s=0, context=collect.default_ssl_context(), opener=opener)
    body = collector.fetch_bytes("https://www.saps.gov.za/services/crimestats.php", outlet_id="saps")
    assert body is None  # logged, did not raise
    # A later URL still runs.
    def opener_ok(req, timeout, context):
        return b'<?xml version="1.0"?><rss version="2.0"><channel></channel></rss>'

    collector._opener = opener_ok
    body = collector.fetch_bytes("https://newsday.co.za/feed/", outlet_id="newsday")
    assert body is not None

    text = err_path.read_text(encoding="utf-8")
    assert b"\r\n" in err_path.read_bytes()
    rows = list(csv.DictReader(io.StringIO(text)))
    assert len(rows) == 1
    row = rows[0]
    assert row["host"] == "www.saps.gov.za"
    assert row["error_type"] == "tls"
    assert "certificate" in row["error"].lower() or "ssl" in row["error"].lower()
    assert row["outlet_id"] == "saps"
    assert row["run_id"] == run_id
    # time in SAST with a numeric offset (UTC+2, no daylight-saving now)
    assert row["logged_at_sast"].startswith("20")
    assert row["logged_at_sast"].endswith("+0200") or row["logged_at_sast"].endswith("+02:00")


def test_parse_rss_items():
    body = b"""<?xml version="1.0"?>
    <rss version="2.0"><channel>
      <item>
        <title>Example</title>
        <link>https://newsday.co.za/south-africa/1/example/</link>
        <pubDate>Thu, 20 Nov 2026 08:00:00 +0200</pubDate>
      </item>
    </channel></rss>"""
    items = collect.parse_rss_or_atom(body, "https://newsday.co.za/feed/", "newsday")
    assert len(items) == 1
    assert items[0].url.endswith("/example/")
    assert items[0].published_at.startswith("2026-11-20")


def test_parse_sitemap_and_news24_lastmod():
    body = (
        b"""<?xml version="1.0" encoding="utf-8"?>"""
        b"""<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">"""
        b"""<url><loc>https://www.news24.com/politics/example-20261120-0607</loc>"""
        b"""<lastmod>11-20-2026</lastmod></url></urlset>"""
    )
    items = collect.parse_sitemap(body, "https://www.news24.com/sitemap", "news24")
    assert len(items) == 1
    assert "2026-11-20" in items[0].published_at
    assert collect.date_from_url(items[0].url) == date(2026, 11, 20)


def test_collectors_json_lists_verified_endpoints():
    cfg = json.loads((ROOT / "data" / "collectors.json").read_text(encoding="utf-8"))
    outlets = cfg["outlets"]
    assert set(outlets) == {
        "news24", "daily_investor", "newsday", "daily_maverick", "groundup", "citizen"
    }
    assert outlets["daily_maverick"]["rss"] == ["https://www.dailymaverick.co.za/dmrss/"]
    assert outlets["groundup"]["rss"] == ["https://www.groundup.org.za/sitenews/rss/"]
    assert outlets["citizen"]["rss"] == ["https://www.citizen.co.za/feed/"]
    assert outlets["daily_investor"]["rss"] == ["https://dailyinvestor.com/feed/"]
    assert outlets["newsday"]["rss"] == ["https://newsday.co.za/feed/"]
    assert "dated_sitemap_pattern" in outlets["news24"]


def test_neutral_random_v1_is_reproducible():
    rule = json.loads((ROOT / "data" / "sampling" / "neutral_random_v1.json").read_text(encoding="utf-8"))
    assert rule["seed"] == 20261120
    assert rule["k_per_outlet_week"] == 2
    assert rule["window_start"] == "2026-05-01"
    assert rule["window_end"] == "2026-11-20"
    # Three items in one week, two should be drawn; same result twice.
    candidates = [
        {
            "outlet_id": "newsday",
            "url": f"https://newsday.co.za/south-africa/{n}/story-{n}/",
            "title": f"t{n}",
            "published_at": f"2026-06-0{n}T09:00:00+0200",
            "date_source": "rss_pubDate",
            "source_url": "https://newsday.co.za/feed/",
            "source_kind": "rss",
        }
        for n in (1, 2, 3)
    ]
    # 1 June 2026 is a Monday, same ISO week as 2 and 3 June.
    a, _ = sampler.draw(candidates, rule, set(), names_path=SYNTHETIC_NAMES)
    b, _ = sampler.draw(candidates, rule, set(), names_path=SYNTHETIC_NAMES)
    assert a == b
    assert len(a) == 2
    assert {row["url"] for row in a} <= {c["url"] for c in candidates}
    assert all(row["iso_week"] == "2026-W23" for row in a)
    assert all(row["seed"] == 20261120 for row in a)


def test_neutral_random_excludes_known_paywall():
    rule = json.loads((ROOT / "data" / "sampling" / "neutral_random_v1.json").read_text(encoding="utf-8"))
    candidates = [
        {
            "outlet_id": "news24",
            "url": "https://www.news24.com/opinions/columnists/paywalled-20260505-0001",
            "title": "p",
            "published_at": "2026-05-05T09:00:00+0200",
            "date_source": "url",
            "source_url": "",
            "source_kind": "sitemap",
        },
        {
            "outlet_id": "news24",
            "url": "https://www.news24.com/politics/free-20260505-0002",
            "title": "f",
            "published_at": "2026-05-05T10:00:00+0200",
            "date_source": "url",
            "source_url": "",
            "source_kind": "sitemap",
        },
    ]
    paywalled = {"https://www.news24.com/opinions/columnists/paywalled-20260505-0001"}
    drawn, excluded = sampler.draw(candidates, rule, paywalled, names_path=SYNTHETIC_NAMES)
    assert len(excluded) == 1
    assert [r["url"] for r in drawn] == ["https://www.news24.com/politics/free-20260505-0002"]


def test_path_filters():
    cfg = json.loads((ROOT / "data" / "collectors.json").read_text(encoding="utf-8"))["outlets"]["news24"]
    assert collect.path_allowed("https://www.news24.com/politics/example-20261120-0001", cfg)
    assert not collect.path_allowed("https://www.news24.com/sport/rugby/example-20261120-0001", cfg)
    assert not collect.path_allowed("https://www.news24.com/southafrica/weather/storms-20261120-0001", cfg)


def test_date_from_url_hyphenated_and_compact():
    assert collect.date_from_url(
        "https://www.dailymaverick.co.za/article/2026-11-20-two-arrested-in-gqeberha-protest"
    ) == date(2026, 11, 20)
    assert collect.date_from_url(
        "https://www.news24.com/politics/example-20261120-0607"
    ) == date(2026, 11, 20)
    # Numeric post ids must not be read as dates.
    assert collect.date_from_url("https://dailyinvestor.com/business/165633/the-tv-presenter/") is None


def test_normalise_date_prefers_permalink_over_stale_lastmod():
    when, source = collect.normalise_date(
        "2022-01-01T00:00:00+02:00",
        "https://www.dailymaverick.co.za/article/2026-07-15-example-story",
    )
    assert when.startswith("2026-07-15")
    assert source == "url"


def test_committed_draw_matches_rule():
    rule = json.loads((ROOT / "data" / "sampling" / "neutral_random_v1.json").read_text(encoding="utf-8"))
    path = ROOT / "data" / "sampling" / "neutral_random_draw_v1.csv"
    assert path.is_file()
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    assert rows, "committed draw list is empty"
    assert all(r["algorithm_id"] == rule["algorithm_id"] for r in rows)
    assert all(int(r["seed"]) == rule["seed"] for r in rows)
    outlets = {r["outlet_id"] for r in rows}
    assert outlets == {"news24", "daily_investor", "newsday", "daily_maverick", "groundup", "citizen"}


def test_private_name_terms_are_dropped_from_the_draw(tmp_path):
    rule = json.loads((ROOT / "data" / "sampling" / "neutral_random_v1.json").read_text(encoding="utf-8"))
    candidates = [
        {
            "outlet_id": "newsday",
            "url": "https://newsday.co.za/south-africa/1/ordinary-story/",
            "title": "ordinary",
            "published_at": "2026-06-02T09:00:00+0200",
            "date_source": "rss_pubDate",
            "source_url": "",
            "source_kind": "rss",
        },
        {
            "outlet_id": "newsday",
            "url": "https://newsday.co.za/south-africa/2/zzzprivateqqq-in-slug/",
            "title": "should be dropped",
            "published_at": "2026-06-03T09:00:00+0200",
            "date_source": "rss_pubDate",
            "source_url": "",
            "source_kind": "rss",
        },
    ]
    names = tmp_path / "names.txt"
    names.write_text("ZZZPRIVATEQQQ\n", encoding="utf-8")
    drawn, _ = sampler.draw(candidates, rule, set(), names_path=names)
    assert [r["url"] for r in drawn] == ["https://newsday.co.za/south-africa/1/ordinary-story/"]


def test_committed_sample_has_no_local_denylist_terms():
    path = ROOT / "tests" / "private_names.local.txt"
    if not path.is_file():
        pytest.skip("local denylist not present")
    terms = sampler.load_private_name_terms(path)
    assert terms
    for rel in (
        "data/sampling/neutral_random_candidates_v1.csv",
        "data/sampling/neutral_random_draw_v1.csv",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        for term in terms:
            assert term.lower() not in text, rel


def test_locked_candidates_and_draw_hashes_match_the_lock():
    import hashlib
    rule = json.loads((ROOT / "data" / "sampling" / "neutral_random_v1.json").read_text(encoding="utf-8"))
    cand = ROOT / "data" / "sampling" / "neutral_random_candidates_v1.csv"
    draw = ROOT / "data" / "sampling" / "neutral_random_draw_v1.csv"
    assert hashlib.sha256(cand.read_bytes()).hexdigest() == rule["candidates_sha256"]
    assert hashlib.sha256(draw.read_bytes()).hexdigest() == rule["draw_sha256"]
    counts = {}
    for r in csv.DictReader(cand.open(encoding="utf-8")):
        counts[r["outlet_id"]] = counts.get(r["outlet_id"], 0) + 1
    assert counts == rule["candidate_counts"]
    collect.assert_candidate_coverage(counts, rule["candidate_counts"])


def test_candidate_coverage_fails_if_one_outlet_drops_a_third():
    rule = json.loads((ROOT / "data" / "sampling" / "neutral_random_v1.json").read_text(encoding="utf-8"))
    locked = dict(rule["candidate_counts"])
    reduced = dict(locked)
    oid = "news24"
    reduced[oid] = (locked[oid] * 2 // 3) - 1
    with pytest.raises(AssertionError, match="dropped too far"):
        collect.assert_candidate_coverage(reduced, locked)


def test_main_refuses_to_overwrite_locked_candidates(tmp_path):
    # Point config at nothing we will actually fetch: refuse happens before or after
    # collect; we pass --out to the locked path and no overwrite flag.
    import hashlib
    locked = ROOT / "data" / "sampling" / "neutral_random_candidates_v1.csv"
    before = locked.read_bytes()
    digest = hashlib.sha256(before).hexdigest()
    rc = collect.main([
        "--config", str(ROOT / "data" / "collectors.json"),
        "--errors", str(tmp_path / "errors.csv"),
        "--out", str(locked),
        "--from", "2026-05-01",
        "--to", "2026-05-01",
        "--outlets", "newsday",
        "--delay", "0",
        "--run-id", "test-no-overwrite",
    ])
    assert rc == 1
    assert locked.read_bytes() == before
    assert hashlib.sha256(locked.read_bytes()).hexdigest() == digest


def test_main_exits_nonzero_when_an_error_was_logged(tmp_path):
    err = tmp_path / "errors.csv"
    out = tmp_path / "candidates.csv"
    cfg = tmp_path / "collectors.json"
    cfg.write_text(json.dumps({
        "outlets": {
            "newsday": {"name": "Newsday", "rss": ["https://newsday.co.za/feed/"], "sitemaps": []}
        }
    }), encoding="utf-8")

    orig_init = collect.Collector.__init__

    def init_with_failing_opener(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)

        def opener(req, timeout, context):
            raise urllib.error.URLError(
                ssl.SSLCertVerificationError("unable to get local issuer certificate")
            )

        self._opener = opener

    collect.Collector.__init__ = init_with_failing_opener
    try:
        rc = collect.main([
            "--config", str(cfg),
            "--errors", str(err),
            "--out", str(out),
            "--from", "2026-05-01",
            "--to", "2026-11-20",
            "--outlets", "newsday",
            "--delay", "0",
            "--run-id", "test-fail-closed",
        ])
    finally:
        collect.Collector.__init__ = orig_init
    assert rc == 1
    rows = list(csv.DictReader(err.open(encoding="utf-8")))
    assert len(rows) >= 1
    assert out.is_file()  # still wrote; exit is non-zero


def test_read_capped_rejects_oversized_body():
    import io
    small = io.BytesIO(b"abc")
    assert collect.read_capped(small, limit=10) == b"abc"
    big = io.BytesIO(b"x" * 50)
    with pytest.raises(collect.ResponseTooLarge):
        collect.read_capped(big, limit=10)


def test_load_private_name_terms_fails_if_file_missing(tmp_path):
    missing = tmp_path / "does-not-exist.txt"
    with pytest.raises(FileNotFoundError, match="required"):
        sampler.load_private_name_terms(missing)


def test_read_capped_default_limit_is_five_million():
    """Catch a read_capped revert (uncapped read) or a raised MAX_RESPONSE_BYTES."""
    import inspect
    default = inspect.signature(collect.read_capped).parameters["limit"].default
    assert default == 5_000_000
    assert collect.MAX_RESPONSE_BYTES == 5_000_000
    assert default == collect.MAX_RESPONSE_BYTES
    # Calling without an explicit limit must use that 5 MB cap.
    ok = io.BytesIO(b"x" * 5_000_000)
    assert len(collect.read_capped(ok)) == 5_000_000
    too_big = io.BytesIO(b"x" * (5_000_000 + 1))
    with pytest.raises(collect.ResponseTooLarge, match="5000000"):
        collect.read_capped(too_big)


def test_draw_fails_closed_when_names_file_missing(tmp_path):
    rule = json.loads((ROOT / "data" / "sampling" / "neutral_random_v1.json").read_text(encoding="utf-8"))
    candidates = [
        {
            "outlet_id": "newsday",
            "url": "https://newsday.co.za/south-africa/1/ordinary-story/",
            "title": "ordinary",
            "published_at": "2026-06-02T09:00:00+0200",
            "date_source": "rss_pubDate",
            "source_url": "",
            "source_kind": "rss",
        }
    ]
    missing = tmp_path / "does-not-exist.txt"
    with pytest.raises(FileNotFoundError, match="required"):
        sampler.draw(candidates, rule, set(), names_path=missing)


def test_paywalled_draw_is_replaced_by_unused0_of_its_own_stratum():
    """A later-found paywall is replaced by unused[0] of that outlet-week, in sort order."""
    rule = json.loads((ROOT / "data" / "sampling" / "neutral_random_v1.json").read_text(encoding="utf-8"))
    # 2026-05-04 is Monday of 2026-W19; 2026-05-11 is 2026-W20.
    week19 = [
        {
            "outlet_id": "newsday",
            "url": f"https://newsday.co.za/south-africa/{n}/story-{n}/",
            "title": f"t{n}",
            "published_at": f"2026-05-0{n}T09:00:00+0200",
            "date_source": "rss_pubDate",
            "source_url": "",
            "source_kind": "rss",
        }
        for n in (4, 5, 6, 7)
    ]
    week20 = {
        "outlet_id": "newsday",
        "url": "https://newsday.co.za/south-africa/11/story-11/",
        "title": "other-week",
        "published_at": "2026-05-11T09:00:00+0200",
        "date_source": "rss_pubDate",
        "source_url": "",
        "source_kind": "rss",
    }
    candidates = week19 + [week20]
    # Pretend the draw took the 2nd and 4th of W19 (05 and 07 May).
    drawn_urls = {
        "https://newsday.co.za/south-africa/5/story-5/",
        "https://newsday.co.za/south-africa/7/story-7/",
    }
    unused = sampler.remainders_by_stratum(
        candidates, rule, set(), drawn_urls, names_path=SYNTHETIC_NAMES
    )
    pool = unused[("newsday", "2026-W19")]
    assert [r["url"] for r in pool] == [
        "https://newsday.co.za/south-africa/4/story-4/",
        "https://newsday.co.za/south-africa/6/story-6/",
    ]
    # The drawn 5 May URL is later found paywalled: replace with unused[0] of W19.
    nxt, rest = sampler.take_replacement(pool)
    assert nxt["url"] == "https://newsday.co.za/south-africa/4/story-4/"
    assert [r["url"] for r in rest] == ["https://newsday.co.za/south-africa/6/story-6/"]
    # Another week's remainder is not the replacement.
    other = unused[("newsday", "2026-W20")]
    assert [r["url"] for r in other] == ["https://newsday.co.za/south-africa/11/story-11/"]
    assert nxt["url"] not in {r["url"] for r in other}


def test_take_replacement_returns_none_when_stratum_exhausted():
    nxt, rest = sampler.take_replacement([])
    assert nxt is None
    assert rest == []


def test_sampler_main_does_not_write_when_candidates_hash_mismatches(tmp_path):
    rule = json.loads((ROOT / "data" / "sampling" / "neutral_random_v1.json").read_text(encoding="utf-8"))
    rule["candidates_sha256"] = "0" * 64
    rule_path = tmp_path / "rule.json"
    rule_path.write_text(json.dumps(rule), encoding="utf-8")
    out = tmp_path / "draw.csv"
    cand = ROOT / "data" / "sampling" / "neutral_random_candidates_v1.csv"
    rc = sampler.main([
        "--rule", str(rule_path),
        "--candidates", str(cand),
        "--out", str(out),
        "--names", str(SYNTHETIC_NAMES),
    ])
    assert rc == 1
    assert not out.exists()


def test_sampler_refuses_locked_draw_write_on_draw_hash_mismatch(tmp_path, monkeypatch):
    rule = json.loads((ROOT / "data" / "sampling" / "neutral_random_v1.json").read_text(encoding="utf-8"))
    # Candidates hash is valid; pretend the would-be draw does not match the pin.
    locked = tmp_path / "neutral_random_draw_v1.csv"
    locked.write_text("sentinel-before\n", encoding="utf-8")
    monkeypatch.setattr(sampler, "LOCKED_DRAW", locked)
    # Draw an empty payload that cannot match the locked draw hash.
    monkeypatch.setattr(sampler, "draw", lambda *a, **k: ([], []))
    rc = sampler.main([
        "--rule", str(ROOT / "data" / "sampling" / "neutral_random_v1.json"),
        "--candidates", str(ROOT / "data" / "sampling" / "neutral_random_candidates_v1.csv"),
        "--out", str(locked),
        "--names", str(SYNTHETIC_NAMES),
    ])
    assert rc == 1
    assert locked.read_text(encoding="utf-8") == "sentinel-before\n"


def test_collect_main_does_not_write_when_coverage_fails(tmp_path, monkeypatch):
    locked = tmp_path / "neutral_random_candidates_v1.csv"
    locked.write_text("sentinel-before\n", encoding="utf-8")
    monkeypatch.setattr(collect, "LOCKED_CANDIDATES", locked)

    cfg = tmp_path / "collectors.json"
    cfg.write_text(json.dumps({
        "outlets": {
            "newsday": {"name": "Newsday", "rss": ["https://newsday.co.za/feed/"], "sitemaps": []}
        }
    }), encoding="utf-8")

    orig_collect = collect.Collector.collect_outlet

    def few(self, outlet_id, window_start, window_end):
        return []

    monkeypatch.setattr(collect.Collector, "collect_outlet", few)
    rc = collect.main([
        "--config", str(cfg),
        "--errors", str(tmp_path / "errors.csv"),
        "--out", str(locked),
        "--from", "2026-05-01",
        "--to", "2026-05-01",
        "--outlets", "newsday",
        "--delay", "0",
        "--run-id", "test-coverage-no-write",
        "--overwrite-locked-candidates",
    ])
    assert rc == 1
    assert locked.read_text(encoding="utf-8") == "sentinel-before\n"

