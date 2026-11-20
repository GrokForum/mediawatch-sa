#!/usr/bin/env python3
"""Apply the pre-registered neutral_random_v1 sampling rule."""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

SAST = ZoneInfo("Africa/Johannesburg")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "scripts"))
import collect  # noqa: E402


def load_paywall_urls() -> set[str]:
    urls: set[str] = set()
    for name in ("paywall_exclusions.csv", "paywall_register.csv"):
        path = DATA / name
        if not path.exists():
            continue
        with path.open(encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                for key in ("url", "article_url", "canonical_url"):
                    if row.get(key):
                        urls.add(collect.norm_url(row[key]) if hasattr(collect, "norm_url") else _norm(row[key]))
    return urls



def load_private_name_terms(path: Path | None = None) -> list[str]:
    path = path or (ROOT / "tests" / "private_names.local.txt")
    if not path.exists():
        raise FileNotFoundError(
            f"private-names denylist is required at {path}; refusing to draw without it"
        )
    terms = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        terms.append(line)
    return terms


def contains_private_name(row: dict, terms: list[str]) -> bool:
    if not terms:
        return False
    blob = f"{row.get('url') or ''} {row.get('title') or ''}".lower()
    return any(term.lower() in blob for term in terms)


def _norm(url: str) -> str:
    return (url or "").strip().rstrip("/").lower()


def row_date(row: dict) -> date | None:
    raw = (row.get("published_at") or "").strip()
    if raw:
        parsed = collect.parse_any_date(raw)
        if parsed is not None:
            return parsed.astimezone(SAST).date()
    return collect.date_from_url(row.get("url") or "")


def iso_week_key(d: date) -> str:
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def load_candidates(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def draw(
    candidates: list[dict],
    rule: dict,
    paywalled: set[str],
    names_path: Path | None = None,
) -> tuple[list[dict], list[dict]]:
    start = date.fromisoformat(rule["window_start"])
    end = date.fromisoformat(rule["window_end"])
    k = int(rule["k_per_outlet_week"])
    seed = int(rule["seed"])
    terms = load_private_name_terms(names_path)
    pool: list[dict] = []
    excluded_paywall: list[dict] = []
    excluded_names = 0
    undated = 0
    for row in candidates:
        url = _norm(row.get("url") or "")
        if not url:
            continue
        if url in paywalled:
            excluded_paywall.append(row)
            continue
        if contains_private_name(row, terms):
            excluded_names += 1
            continue
        d = row_date(row)
        if d is None:
            undated += 1
            continue
        if d < start or d > end:
            continue
        item = dict(row)
        item["_date"] = d.isoformat()
        item["_week"] = iso_week_key(d)
        item["_url_norm"] = url
        pool.append(item)

    rng = random.Random(seed)
    outlets = sorted({r["outlet_id"] for r in pool})
    drawn: list[dict] = []
    for oid in outlets:
        weeks = sorted({r["_week"] for r in pool if r["outlet_id"] == oid})
        for week in weeks:
            stratum = [
                r
                for r in pool
                if r["outlet_id"] == oid and r["_week"] == week
            ]
            stratum.sort(key=lambda r: ((r.get("published_at") or ""), r["_url_norm"]))
            take = k if len(stratum) >= k else len(stratum)
            picked = rng.sample(stratum, take) if take else []
            # Preserve original order of this stratum as remainder for replacements.
            picked_urls = {r["_url_norm"] for r in picked}
            remainder = [r for r in stratum if r["_url_norm"] not in picked_urls]
            for i, r in enumerate(picked, start=1):
                drawn.append(
                    {
                        "algorithm_id": rule["algorithm_id"],
                        "seed": seed,
                        "outlet_id": oid,
                        "iso_week": week,
                        "draw_index": i,
                        "url": r["url"],
                        "published_at": r.get("published_at") or "",
                        "date_source": r.get("date_source") or "",
                        "title": r.get("title") or "",
                        "source_url": r.get("source_url") or "",
                        "source_kind": r.get("source_kind") or "",
                        "status": "drawn",
                        "replacement_for": "",
                        "remainder_after": len(remainder),
                    }
                )
    return drawn, excluded_paywall


def remainders_by_stratum(
    candidates: list[dict],
    rule: dict,
    paywalled: set[str],
    drawn_urls: set[str],
    names_path: Path | None = None,
) -> dict[tuple[str, str], list[dict]]:
    """Unused candidates per (outlet, iso_week) in the original sort order."""
    start = date.fromisoformat(rule["window_start"])
    end = date.fromisoformat(rule["window_end"])
    terms = load_private_name_terms(names_path)
    paywalled = {_norm(u) for u in paywalled}
    drawn_urls = {_norm(u) for u in drawn_urls}
    pool: list[dict] = []
    for row in candidates:
        url = _norm(row.get("url") or "")
        if not url or url in paywalled:
            continue
        if contains_private_name(row, terms):
            continue
        d = row_date(row)
        if d is None or d < start or d > end:
            continue
        item = dict(row)
        item["_date"] = d.isoformat()
        item["_week"] = iso_week_key(d)
        item["_url_norm"] = url
        pool.append(item)
    out: dict[tuple[str, str], list[dict]] = {}
    for oid in sorted({r["outlet_id"] for r in pool}):
        for week in sorted({r["_week"] for r in pool if r["outlet_id"] == oid}):
            stratum = [r for r in pool if r["outlet_id"] == oid and r["_week"] == week]
            stratum.sort(key=lambda r: ((r.get("published_at") or ""), r["_url_norm"]))
            out[(oid, week)] = [r for r in stratum if r["_url_norm"] not in drawn_urls]
    return out


def take_replacement(unused: list[dict]) -> tuple[dict | None, list[dict]]:
    """Replace a paywalled or unusable draw with unused[0] of that stratum."""
    if not unused:
        return None, []
    return unused[0], list(unused[1:])


def write_draw(path: Path, rows: list[dict]) -> None:

    fields = [
        "algorithm_id",
        "seed",
        "outlet_id",
        "iso_week",
        "draw_index",
        "url",
        "published_at",
        "date_source",
        "title",
        "source_url",
        "source_kind",
        "status",
        "replacement_for",
        "remainder_after",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rule", default=str(DATA / "sampling" / "neutral_random_v1.json"))
    parser.add_argument("--candidates", default=str(DATA / "sampling" / "neutral_random_candidates_v1.csv"))
    parser.add_argument("--out", default=str(DATA / "sampling" / "neutral_random_draw_v1.csv"))
    args = parser.parse_args(argv)
    rule = json.loads(Path(args.rule).read_text(encoding="utf-8"))
    candidates = load_candidates(Path(args.candidates))
    paywalled = load_paywall_urls()
    drawn, excluded = draw(candidates, rule, paywalled)
    write_draw(Path(args.out), drawn)
    print(
        f"drew {len(drawn)} rows from {len(candidates)} candidates "
        f"(excluded {len(excluded)} known-paywall URLs) -> {args.out}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
