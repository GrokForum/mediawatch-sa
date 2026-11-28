# RFC-CHG-MW-SEC-01 — Bump pytest to 9.2.0 (DEV)

**Status:** Opened as draft [PR #12](https://github.com/GrokForum/mediawatch-sa/pull/12) on branch `dev/chg-mw-sec-deps-2026-11`. This change bumps the test-only pytest pin from 8.3.4 to 9.2.0. `robots.txt` stays `Disallow: /` and noindex stays on every page. No indexing request.
**Environment:** DEV — branch created from `origin/main` at `5ae6eb3d8a7c089e6b478fc8bfb7149e73cfa30f` (27 Nov 2026, Africa/Johannesburg).
**Pre-change SHA (rollback base):** `5ae6eb3d8a7c089e6b478fc8bfb7149e73cfa30f` (`origin/main` at the start of this change).
**Date:** 27 Nov 2026 (Africa/Johannesburg)
**Repo:** https://github.com/GrokForum/mediawatch-sa (PUBLIC). This RFC does not change GitHub Pages settings, DNS, or indexing.

---

## Environment plan

| Env | What it is | Points at production? |
|-----|------------|------------------------|
| DEV | This branch. The pin change and the test suite can be inspected locally. | No. |
| TEST | Not stood up. | — |
| PROD | GitHub Pages, still deploying from `main`. | Only after a later, named deployment with the owner's own GO on the exact head. |

---

## Goal

Move the test-only `pytest` pin from 8.3.4 to the current 9.x release, 9.2.0, which is past the fix for PYSEC-2026-1845 / CVE-2025-71176 / GHSA-6w46-j5rx-g56g (fixed in pytest 9.0.3). The advisory is a local tmpdir issue (CVSS 3.1 6.8). The site generator remains standard-library only. Source: watcher-site security baseline, 27 November 2026, item L-1. The owner approved patching on 27 Nov 2026.

## What changes (exact files)

| File | Change |
|------|--------|
| `requirements.txt` | `pytest==8.3.4` → `pytest==9.2.0`. The `jsonschema` and `PyYAML` pins stay. |
| `changes/RFC-CHG-MW-SEC-01.md` | This record. |
| `docs/STATUS.md` | Change-log row for this RFC. |

No other pin file exists in this repo. CI (`.github/workflows/pages.yml`) installs `requirements.txt` and so picks up this pin.

## What stays

- Methodology, collectors, site generator, publications, findings, workflows, `robots.txt`, noindex, and CNAME are unchanged.
- `jsonschema==4.23.0` and `PyYAML==6.0.2` are unchanged.
- pytest remains a check and CI tool only; it does not ship in the published site.

## Seen, not touched (out of scope)

- Baseline item M-4 (add a meta Content-Security-Policy on MediaWatch pages) is a site-generator change, not a dependency pin. It is left for a later, separately reviewed RFC.
- Baseline item L-2 (duckdb 1.4.1 encryption advisory, fixed in 1.4.2) does not apply: duckdb is not pinned in `requirements.txt` and is not imported in this repo.
- Baseline item H-1 (pdfminer.six / pdfplumber) does not apply: those packages are not used here.
- Other baseline items (DNS and hosting, email authentication, `security.txt`, and HTTP headers that GitHub Pages cannot set) are not MediaWatch dependency pins.

## Risk

Low. pytest is a dev and CI test runner, not part of the published site. pytest 9 may reject APIs removed since 8.3.4; any breakage is fixed in this change with small, named edits, or the branch is dropped. The advisory is local to the test runner's tmpdir handling.

## Success

- `requirements.txt` pins `pytest==9.2.0`.
- `uv run -q --no-project --with-requirements requirements.txt python -m pytest -q` passes in the development checkout (the gitignored denylist and `data/fetched_articles/` may be present for that run as a local symlink and are never committed).
- The same command in a clean clone passes, with the expected skips where those local files are absent.
- review_kit is clean, or findings are explained.
- The new commits contain no denylist term and no role-word violations.

## Tests

`uv run -q --no-project --with-requirements requirements.txt python -m pytest -q`

Recorded on 27 Nov 2026 (Africa/Johannesburg), pytest 9.2.0:

- Development checkout (gitignored denylist present; `data/fetched_articles/` present as a local symlink for the run only, never staged): **103 passed** in 27.00s.
- Clean clone (those local files absent): **100 passed, 3 skipped** in 6.88s. The three skips are the denylist tests and the fetched-article test, as expected.

## Rollback

Before merge: drop the branch `dev/chg-mw-sec-deps-2026-11`, or revert the commit(s) on it. After merge: revert the merge commit. Either restores `pytest==8.3.4` on top of `5ae6eb3d8a7c089e6b478fc8bfb7149e73cfa30f`. Forward-only: no rebase, amend, or force. Never on `main`.

## Sign-off

Sign-off is by someone other than the author (Reviewer A, critic reviewer). Owner GO naming the head is required before merge or deploy.
