# RFC-CHG-MW-009 — Code the locked pilot `neutral_random_v1` draw (DEV)

**Status:** Local branch `dev/chg-mw-009-pilot-register`. Not pushed; no PR; not merged; not deployed.  
**Environment:** DEV — branch `dev/chg-mw-009-pilot-register`, created from `dev/chg-mw-008-collectors` at `4948167836d45e6fd2e0d5add4c7db935d44a15c`.  
**Pre-change SHA (rollback base):** `4948167836d45e6fd2e0d5add4c7db935d44a15c`.  
**Date:** 20 Nov 2026 (Africa/Johannesburg)  
**Repo:** https://github.com/GrokForum/mediawatch-sa (PUBLIC). This RFC does not change GitHub Pages settings, DNS, or indexing.

---

## Environment plan

| Env | What it is | Points at production? |
|-----|------------|------------------------|
| DEV | This local branch. Coded v1 draw, sample-size display, and unit tests can be inspected locally. | No. |
| TEST | Not stood up. | — |
| PROD | GitHub Pages, still deploying from `main`. | Only after a later, named deployment RFC with the owner's own GO on the exact head. |

---

## Goal

Apply the locked `neutral_random_v1` draw to the three pilot outlets (News24, Daily Investor, Newsday) for 1 May 2026–20 Nov 2026. Fetch free text only (TLS verification on; no paywall bypass). Code each fetched article under METHODOLOGY 0.5. A coded-and-clean article produces no finding row but counts in the sample denominator. Add a finding only where a driver really fires, with an exact quote from a fetch done in this change. Show per-publication findings count, sample size, and per-actor scores with *n* status under the DRAFT banner.

---

## What changes (exact files)

| File | Change |
|------|--------|
| `scripts/fetch_draw.py` | **New.** Fetch drawn URLs with the existing collector TLS policy (`ssl.create_default_context`; never disable verification). Paywalled, 404, or non-article URLs are replaced with the next unused URL in the same stratum. Bodies go under gitignored `data/fetched_articles/`. |
| `scripts/check_staged_denylist.py` | **New.** Check `git diff --cached` against the gitignored local denylist before a commit. Does not print the term. |
| `data/sampling/neutral_random_v1_fetch_status.csv` | **New.** Fetch outcomes and replacements (URLs and metadata only; no bodies). Run id `fetch-009-2026-11-20`. |
| `data/news24_pilot_findings.json` | 60 new v1 articles, all coded clean. No new findings. Historical signed scores not rewritten. |
| `data/dailyinvestor_pilot_findings.json` / `.csv` | 59 new v1 articles (the 60th, the May tide piece, already existed and was flagged `v1_draw` without a duplicate finding), 58 coded clean, one new finding `F-DI-NRV1-01`. CSV has a CRLF row for the new finding. |
| `data/newsday_pilot_findings.json` / `.csv` | 52 new v1 articles, 46 coded clean, seven new findings `F-ND-NRV1-01`–`07`. CSV has CRLF rows for the new findings. |
| `scripts/build_site.py` | Home and publication pages show v1 sample size (coded, including clean), findings count, and per-actor scores with *n* status. Declared `DATA_WINDOW` end is 20 November 2026. Clean article pages exist and say they count in the denominator. |
| `tests/test_site.py` | v1 completeness (172 fetched and coded), exact new-finding quotes, sample-size display, clean-article pages, updated window. |
| `changes/RFC-CHG-MW-009.md` | This record. |
| `docs/STATUS.md` | Change-log rows for the rebuilt 008 head and this change. |

`data/people.csv` was not changed: new bylines stay byline-only unless a public-role row already existed. `data/fetched_articles/` stays gitignored. Article bodies are not committed.

## Collection and coding counts (run `fetch-009-2026-11-20`, 20 Nov 2026, Africa/Johannesburg)

Every one of the 172 locked pilot slots was fetched as free full text (`full_text_curl`) and coded (finding or clean). No slot exhausted replacements. No TLS or fetch errors were logged on this run. The official `data/collector_errors.csv` still holds the two earlier 008 watch rows (SAPS certificate failure; `feeds.24.com` unexpected EOF), both at 20:33:34 SAST on 20 Nov 2026; verification was not bypassed.

| Outlet | Sampled | Fetched | Paywalled-replaced | Coded | Clean | New v1 findings | Actors now provisional | Actors now scored |
|--------|---------|---------|--------------------|-------|-------|-----------------|------------------------|-------------------|
| News24 | 60 | 60 | 36 (max replacement depth 13; JSON-LD `isAccessibleForFree` only) | 60 | 60 | 0 | Solidarity *n*=5, ANC *n*=5 (pre-existing counted findings) | AfriForum *n*=10 (pre-existing counted findings) |
| Daily Investor | 60 | 60 | 0 | 60 (59 new + 1 already coded tide article, not re-found) | 58 | 1 (`F-DI-NRV1-01`, ANC, `headline_body_gap`) | Ramaphosa *n*=5 (unchanged), ANC *n*=5 (was 4) | none |
| Newsday | 52 | 52 | 0 | 52 | 46 | 7 (on 6 articles; Phala Phala carries two) | ANC *n*=7 (was 4), AfriForum *n*=5 (unchanged) | none |
| **Pilot total** | **172** | **172** | **36** | **172** | **164** | **8** | — | — |

Published scorecard *n* (generated from the same `build_site.scorecards` roll-up the site uses, counting only rendered findings; paywalled findings are excluded):

**News24:** AfriForum n=10 scored; ANC n=5 provisional; Solidarity n=5 provisional; Trump / US government n=4 findings-only; DA n=3 findings-only; AgriSA n=2 findings-only; Cyril Ramaphosa n=2 findings-only; Takealot / Naspers n=2 findings-only; unspecified (AfriMAGA) n=2 findings-only; EFF n=1 findings-only; GNU n=1 findings-only.
**Daily Investor:** ANC n=5 provisional; Ramaphosa n=5 provisional; AfriForum n=2 findings-only; DA n=2 findings-only; GNU n=2 findings-only; Solidarity n=2 findings-only; Trump/US n=2 findings-only.
**Newsday:** ANC n=7 provisional; AfriForum n=5 provisional; DA n=4 findings-only; EFF n=4 findings-only; Ramaphosa n=4 findings-only; GNU n=2 findings-only; Trump/US n=2 findings-only; SAAI n=1 findings-only; Solidarity n=1 findings-only.

News24 DA is findings-only at *n*=3; Cyril Ramaphosa is findings-only at *n*=2; Trump / US government is findings-only at *n*=4. Newsday EFF, Ramaphosa and DA remain findings-only at *n*=4. No finding was added to push an actor over a threshold. A unit test checks that these *n* and status labels still match the site roll-up. Daily Investor and Newsday registration CTAs, related lists and comments were cut before coding (they are not the article body). Historical signed scores were not rewritten.

New finding quotes were taken from the free fetch on this change and checked against the cleaned body (typographic punctuation included) before the JSON was written.

---

## What stays

- No push, no PR, no merge to `main`, no deploy.
- `noindex` / `robots.txt` `Disallow: /` / DRAFT banner.
- Five fact labels. Private people unnamed. Exact fetched quotes only; no fabrication.
- TLS verification is never disabled. Errors are logged and the run continues.
- The locked `neutral_random_v1` seed, window, k, and replacement rule are not changed.
- IOL and EWN remain an error watch, not a scored-pilot expansion.
- Phase-2 outlets are not scored on the public pilot pages in this RFC (that is CHG-MW-010).
- Historical findings and signed scores from earlier coding passes are not rewritten.

---

## Paywall and replacement

A drawn URL that is paywalled, 404, or not an article is replaced with the first unused URL from the start of the same outlet-week stratum in the original sort order (unused[0], pop(0); the pre-registered rule). Intermediate attempts are in `data/sampling/neutral_random_v1_replacement_attempts.csv`. Teasers never stand in for a paywalled body. News24 access is judged from JSON-LD `isAccessibleForFree` (the `article-locked` CSS hook also appears on free articles and is not used alone). Daily Investor and Newsday are fetched without registering.

---

## Success

- Every v1 pilot slot is either a fetched-and-coded article (finding or clean) or an honestly recorded exhaustion of replacements.
- Findings pass the §5 gates (exact quote, URL, datetime, byline, steelmen, fact label, fetched here).
- The site shows findings count, sample size, and per-actor scores with *n* status under the DRAFT banner.
- Tests, build, pickaxe on the staged tree (0), and review-kit pass except for known old-identity commits.
- POPIA review PASS.

## Rollback

Git: return this branch to `4948167836d45e6fd2e0d5add4c7db935d44a15c`. Forward-only: no rebase, amend, or force. Never on `main`. Never build on or push `local/do-not-push-008-denylist-history`.

## Result

SUCCEEDED (local DEV branch only; not pushed; not merged; not deployed).

## Sign-off

Author: the bot. Sign-off is by someone other than the author. Owner direction (relayed) was to do this work on a local branch only, on top of `4948167`. Owner GO is still required, naming the head, before push, PR, merge to `main`, or deploy.
