# RFC-CHG-MW-007 — Official wording rule and Q2 2026/27 murder-figure findings (DEV)

**Status:** Branch `dev/chg-mw-007-police-wording`. Public inside draft [PR #7](https://github.com/GrokForum/mediawatch-sa/pull/7) (merged into `dev/chg-mw-008-collectors` at `be75ded`); not merged to `main`; not deployed.  
**Environment:** DEV — branch `dev/chg-mw-007-police-wording`, created from `origin/main`.  
**Pre-change SHA (rollback base):** `8294282db5e2e9774e89695e8b75e0e4c16a759b` (`main` after PR #3).  
**Date:** 20 Nov 2026 (Africa/Johannesburg)  
**Repo:** https://github.com/GrokForum/mediawatch-sa (PUBLIC). This RFC does not change GitHub Pages settings, DNS, or indexing.

---

## Environment plan

| Env | What it is | Points at production? |
|-----|------------|------------------------|
| DEV | This local branch. Findings, methodology and the generated `/method/` page can be inspected and unit-tested locally. | No. |
| TEST | Not stood up. | — |
| PROD | GitHub Pages, still deploying from `main` at `8294282`. A merge of this RFC would add two findings-only outlet pages and the official-wording rule to a later public build. | Only after a later, named deployment RFC with the owner's own GO on the exact head. |

---

## Goal

Log a verified factual error in IOL and EWN reporting of SAPS Q2 2026/27 murder statistics, and add the shared “official wording vs media wording” rule (the same rule as the project's other registers) to the MediaWatch methodology.

---

## What changes (exact files)

| File | Change |
|------|--------|
| `docs/METHODOLOGY.md` | Bump to **0.5-draft**. Add §5b Official wording vs media wording. Prior findings keep their existing `methodology_version`. Historical scores are not rewritten. |
| `scripts/build_site.py` | Render the new method section on `/method/`. Add a findings-only **error watch** for IOL and EWN (not an expansion of the scored three-outlet pilot). Note the watch on the coverage plan. |
| `data/iol_watch_findings.json` | **New.** One free IOL article and one `factual_error` finding. |
| `data/ewn_watch_findings.json` | **New.** One free EWN article and one `factual_error` finding. |
| `data/people.csv` | Add the two public bylines (journalist role only; no private contact or unverified handles). |
| `scripts/validate_schema.py` | Validate the two new findings files. |
| `tests/test_site.py` | Tests for the method section, the two findings, schema, and watch pages. |
| `changes/RFC-CHG-MW-007.md` | This record. |
| `docs/STATUS.md` | Change-log row. |

**What stays:** the three-outlet scored pilot, Pages settings, `robots.txt`, noindex, the contact placeholder, data already on `main`, and all previously coded findings and scores.

---

## The logged error

The official SAPS Q2 2026/27 document (`https://www.saps.gov.za/services/downloads/2026/2026-2027_-_2nd_Quarter_WEB.pdf`, also linked from `https://www.saps.gov.za/services/crimestats.php`) was checked directly. The crime-situation table for July–September shows Murder **5,590** (2026) against **5,794** (2025), count difference **−204**, percentage change **−3,5%**.

IOL (`https://iol.co.za/news/crime-and-courts/2026-11-20-sa-records-1600-fewer-murders-but-5590-people-killed-in-three-months/`, Se-Anne Rall, published 20 Nov 2026 08:05:14 UTC / 10:05:14 SAST) and EWN (`https://www.ewn.co.za/2026/11/20/sa-continues-to-record-decline-in-murders-violent-crime-cachalia`, Tsholo Tsoku, published 20 Nov 2026 08:24:47 UTC / 10:24:47 SAST) both state as fact that there were more than 1,600 fewer murders year on year. Both pages were free to read. No correction was present when fetched on 20 Nov 2026.

The same incorrect year-on-year wording appears in the Acting Minister of Police's official speech of 20 Nov 2026 (SAPS newsroom speech list, nid 72569). The speech also states the current count of 5,590 correctly. The speech is treated as a primary record of what was said; it does not override the official tables. Other category percentages in the articles (carjacking −16.8%, truck hijacking −27.9%, residential robbery −7%, sexual offences −2.7%) match the tables.

Each finding is `factual_error`, actor `SAPS`, direction `FOR` (the published line inflates the official year-on-year murder-decline record), fact label `Not established` for the 1,600 claim, with the official table figures labelled Proven in the evidence notes. Sample frame `purposive`. Signed score +2.0. No private names.

---

## Tests and how success is proven (DEV)

- `uv run -q --no-project --with-requirements requirements.txt python -m pytest -q -rs` — including the local denylist test.
- New tests cover the method-page section, methodology 0.5-draft, and both findings (quote, URL, dates, official SAPS figures, no correction noted).
- A local `scripts/build_site.py` build still has noindex on every HTML page, exact `robots.txt`, and only the already-allowed file types.

## Rollback

```
git checkout main
```

Or delete the branch `dev/chg-mw-007-police-wording`. If this RFC is later merged, rollback is `git revert <merge-commit>`. Pre-change SHA: `8294282db5e2e9774e89695e8b75e0e4c16a759b`. This RFC does not change Pages settings.

## Seen, not touched

- Existing pilot findings and their methodology_version values (0.3-draft / 0.4-draft).
- Open RFCs on other branches (nightly live check, public manifest, privacy page).
- Editor-in-chief still blank for EWN in `publications.csv`.
- No search-engine indexing request, no merge, no Pages settings change, no deploy. (This branch was not pushed on its own; it became public inside draft [PR #7](https://github.com/GrokForum/mediawatch-sa/pull/7) through the 008 merge `be75ded`.)

## Sign-off

Author: the bot. Sign-off is by someone other than the author. Owner GO was given to log the error, watch, and add the same official-wording rule as the project's other registers (20 Nov 2026). Owner GO is still required before merge or deploy.
