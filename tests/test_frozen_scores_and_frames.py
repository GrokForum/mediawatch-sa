"""Historical signed scores stay frozen; legacy frames are not v1."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(ROOT / "scripts"))
import build_site  # noqa: E402

FROZEN = ROOT / "tests" / "frozen_signed_scores_v008.json"
LEGACY_FINDINGS = {
    "F-N24-NEUT-AB-01",
    "F-N24-NEUT-CAPA-01",
    "F-N24-NEUT-MACU-01",
    "F-N24-NEUT-AB-X-01",
    "F-DI-16",
    "F-DI-17",
    "F-ND-14",
    "F-ND-15",
    "F-ND-22",
}


def _num(v):
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(v)
    except (TypeError, ValueError):
        return v


def test_historical_csv_weights_and_json_signed_scores_are_frozen():
    expected = json.loads(FROZEN.read_text(encoding="utf-8"))
    assert len(expected) > 100
    current = {}
    for fn, typ in (
        ("data/news24_pilot_findings.json", "json"),
        ("data/dailyinvestor_pilot_findings.json", "json"),
        ("data/newsday_pilot_findings.json", "json"),
        ("data/news24_pilot_findings.csv", "csv"),
        ("data/dailyinvestor_pilot_findings.csv", "csv"),
        ("data/newsday_pilot_findings.csv", "csv"),
    ):
        path = ROOT / fn
        if typ == "json":
            doc = json.loads(path.read_text(encoding="utf-8"))
            for f in doc["findings"]:
                current[(fn, f["id"])] = (_num(f.get("weight")), _num(f.get("signed_score")))
        else:
            for r in csv.DictReader(path.open(encoding="utf-8")):
                current[(fn, r["id"])] = (_num(r.get("weight")), _num(r.get("signed_score")))
    got = {(row["source"], row["id"]): (_num(row["weight"]), _num(row["signed_score"])) for row in expected}
    assert current == got


def test_nine_pre_v1_rows_are_tagged_legacy_neutral():
    found = set()
    for fn in (
        "data/news24_pilot_findings.json",
        "data/dailyinvestor_pilot_findings.json",
        "data/newsday_pilot_findings.json",
    ):
        doc = json.loads((ROOT / fn).read_text(encoding="utf-8"))
        for f in doc["findings"]:
            if f["id"] in LEGACY_FINDINGS:
                assert f["sample_frame"] == "legacy_neutral", f["id"]
                found.add(f["id"])
            else:
                assert f.get("sample_frame") != "legacy_neutral" or f["id"] in LEGACY_FINDINGS
    assert found == LEGACY_FINDINGS


def test_rollup_option_b_does_not_give_legacy_the_v1_weight():
    v1 = {
        "id": "t-v1", "actor": "ANC", "direction": "AGAINST",
        "signed_score": -1.5, "accountability_status": "bias",
        "sample_frame": "neutral_random",
    }
    legacy = {
        "id": "t-leg", "actor": "ANC", "direction": "FOR",
        "signed_score": 1.5, "accountability_status": "bias",
        "sample_frame": "legacy_neutral",
    }
    rows = build_site.scorecards([v1, legacy], rollup="b")
    assert len(rows) == 1
    # Weights 4 vs 1: mean = (-1.5*4 + 1.5*1) / 5 = -0.9
    assert rows[0]["mean"] == pytest.approx(-0.9)
    unweighted = build_site.scorecards([v1, legacy], rollup="unweighted")
    assert unweighted[0]["mean"] == pytest.approx(0.0)
    assert build_site.ROLLUP_B_WEIGHTS["neutral_random"] > build_site.ROLLUP_B_WEIGHTS["legacy_neutral"]


def test_recoded_csv_rows_record_the_frozen_weight_note():
    for fn in ("data/dailyinvestor_pilot_findings.csv", "data/newsday_pilot_findings.csv"):
        rows = list(csv.DictReader((ROOT / fn).open(encoding="utf-8")))
        recoded = [r for r in rows if "frozen" in (r.get("evidence_notes") or "").lower()]
        assert recoded, fn
        for r in recoded:
            assert "Weight and signed_score are frozen" in r["evidence_notes"]
            assert ".Driver recoded" not in r["evidence_notes"]
