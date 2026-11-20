#!/usr/bin/env python3
"""Validate MediaWatch SA data files against data/schema.json (JSON Schema 2020-12).

RFC-CHG-MW-002. Read-only: reports problems, never rewrites data.
Usage: python scripts/validate_schema.py [--json]
Exit code 0 if every file passes, 1 otherwise.
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover
    sys.exit("jsonschema is required: pip install -r requirements.txt")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

FINDINGS_FILES = [
    "news24_pilot_findings.json",
    "dailyinvestor_pilot_findings.json",
    "newsday_pilot_findings.json",
    "iol_watch_findings.json",
    "ewn_watch_findings.json",
]


def _validator(schema, section):
    sub = {
        "$schema": schema["$schema"],
        "$defs": schema.get("$defs", {}),
        "type": "array",
        "items": schema["properties"][section]["items"],
    }
    return Draft202012Validator(sub)


def _csv_rows(name):
    with open(DATA / name, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    # empty CSV cells are null in the schema model
    return [{k: (v if v != "" else None) for k, v in r.items()} for r in rows]


def validate():
    schema = json.loads((DATA / "schema.json").read_text(encoding="utf-8"))
    results = {}
    for name in FINDINGS_FILES:
        doc = json.loads((DATA / name).read_text(encoding="utf-8"))
        errs = list(_validator(schema, "findings").iter_errors(doc["findings"]))
        results[name] = errs
    for name, section in (("people.csv", "people"), ("publications.csv", "publications")):
        rows = _csv_rows(name)
        results[name] = list(_validator(schema, section).iter_errors(rows))
    return results


def summarise(results):
    out = {}
    for name, errs in results.items():
        kinds = Counter()
        rows = set()
        for e in errs:
            path = list(e.absolute_path)
            if path:
                rows.add(path[0])
            field = path[1] if len(path) > 1 else "(row)"
            kinds[f"{field}: {e.validator}"] += 1
        out[name] = {"errors": len(errs), "rows_with_errors": len(rows), "by_field": dict(kinds)}
    return out


def main():
    summary = summarise(validate())
    if "--json" in sys.argv:
        print(json.dumps(summary, indent=2))
    else:
        for name, s in summary.items():
            status = "PASS" if s["errors"] == 0 else "FAIL"
            print(f"{status}  {name}: {s['errors']} errors in {s['rows_with_errors']} rows")
            for k, v in sorted(s["by_field"].items()):
                print(f"        {k} x{v}")
    return 0 if all(s["errors"] == 0 for s in summary.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
