#!/usr/bin/env python3
"""Fail if staged content matches the gitignored local private-names denylist.

Run against `git diff --cached` before every commit so a hit never lands in history.
The denylist file itself is never staged.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = ROOT / "tests" / "private_names.local.txt"


def terms() -> list[str]:
    if not NAMES.is_file():
        raise FileNotFoundError(
            f"check_staged_denylist: denylist is required at {NAMES}; refusing to skip"
        )
    out = []
    for line in NAMES.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out


def main() -> int:
    try:
        names = terms()
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if not names:
        print("check_staged_denylist: denylist is empty; refusing to skip", file=sys.stderr)
        return 1
    diff = subprocess.check_output(["git", "diff", "--cached", "-U0", "--"], cwd=ROOT)
    # Do not print the matching term.
    text = diff.decode("utf-8", "replace").lower()
    hits = 0
    for term in names:
        if term.lower() in text:
            hits += 1
    if hits:
        print(
            f"check_staged_denylist: BLOCK — {hits} denylist term(s) present in the staged diff. "
            "Unstage or rewrite the change. The term is not printed.",
            file=sys.stderr,
        )
        return 1
    print("check_staged_denylist: PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
