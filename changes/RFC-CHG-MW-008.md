# RFC-CHG-MW-008 — Collectors, locked `neutral_random` sampling, and official driver recode (DEV)

**Status:** Local branch `dev/chg-mw-008-collectors`. Not pushed; no PR; not merged; not deployed.  
**Environment:** DEV — branch `dev/chg-mw-008-collectors`, created from `dev/chg-mw-005-privacy` with `dev/chg-mw-007-police-wording` merged in.  
**Pre-change SHA (rollback base):** `be75dedf46442bcdabac04f344aae861787076a6` (008 after the forward-only merge of 007).  
**Date:** 20 Nov 2026 (Africa/Johannesburg)  
**Repo:** https://github.com/GrokForum/mediawatch-sa (PUBLIC). This RFC does not change GitHub Pages settings, DNS, or indexing.

---

## Environment plan

| Env | What it is | Points at production? |
|-----|------------|------------------------|
| DEV | This local branch. Collectors, the locked sampling rule, recoded driver names, and unit tests can be inspected locally. | No. |
| TEST | Not stood up. | — |
| PROD | GitHub Pages, still deploying from `main`. A later merge would publish the locked rule, the recoded driver labels, and collector artefacts. | Only after a later, named deployment RFC with the owner's own GO on the exact head. |

---

## Goal

1. Ship stdlib RSS/sitemap collectors for the pilot outlets (News24, Daily Investor, Newsday) and the phase-2 trio (Daily Maverick, GroundUp, The Citizen), with certificate and TLS errors logged (host, error, time in Africa/Johannesburg) to the run log and to `data/collector_errors.csv`, then the run continuing. Verification is never disabled.
2. Lock `neutral_random` in METHODOLOGY §8a as a pre-registered, seeded, reproducible rule, with the seed and the draw list committed.
3. Resolve the two Daily Investor / Newsday unofficial-driver schema failures by recoding those names onto the official closed driver set, without rewriting historical weights or signed scores.

---

## What changes (exact files)

| File | Change |
|------|--------|
| `scripts/collect.py` | **New.** Stdlib urllib + `xml.etree` RSS, Atom and sitemap collector. Default SSL context only. Errors logged; the run continues. |
| `scripts/sample_neutral_random.py` | **New.** Applies `neutral_random_v1` (seed `20261120`, k=2 per outlet per ISO week). |
| `data/collectors.json` | **New.** Verified endpoints (fetched under default TLS on 20 Nov 2026). |
| `data/collector_errors.csv` | **New.** CRLF log of fetch and TLS errors from the committed collection run, plus a header for later appends. |
| `data/sampling/neutral_random_v1.json` | **New.** Frozen seed, window (`2026-05-01`–`2026-11-20`), k, and replacement rule. |
| `data/sampling/neutral_random_candidates_v1.csv` | **New.** Candidate universe used for the first draw (URLs and dates only; no article bodies). |
| `data/sampling/neutral_random_draw_v1.csv` | **New.** The committed draw list. |
| `docs/METHODOLOGY.md` | Lock §8a to `neutral_random_v1`. Use “the sibling crime register” in place of leftover agent-style register nicknames. |
| `scripts/build_site.py` | Method page: official-driver recode note; locked-frame wording; “sibling crime register”. |
| `data/dailyinvestor_pilot_findings.json` / `.csv` | Recode unofficial driver names to the official set. Weights and signed scores frozen. Original name recorded in `evidence_notes`. |
| `data/newsday_pilot_findings.json` / `.csv` | Same recode. |
| `tests/test_collectors.py` | **New.** TLS policy, error-log shape, parsers, reproducible draw, path filters. |
| `tests/test_site.py` | Drop the two strict xfails; expect DI/Newsday schema to pass. Official-wording test looks for “sibling crime register”. |
| `changes/RFC-CHG-MW-007.md` | Wording only, on this branch: “sibling crime register” in place of the leftover nickname. 007 history is not amended. |
| `changes/RFC-CHG-MW-008.md` | This record. |
| `docs/STATUS.md` | Change-log row. |

---

## What stays

- No push, no PR, no merge to `main`, no deploy.
- `noindex` / `robots.txt` `Disallow: /` / DRAFT banner.
- Paywalled content is not fetched, spoofed, or scored. Known exclusions are dropped before the draw.
- The five fact labels. Private people unnamed.
- IOL and EWN remain an error watch, not a scored-pilot expansion.
- The scored pilot remains News24, Daily Investor and Newsday. Phase-2 collectors and draw rows are registered here; publishing phase-2 scores needs the later RFC and the owner’s sign-off that the pilot has been reviewed.
- Historical signed scores are not rewritten.
- `pages.yml` persist-credentials and live-check behaviour from the 005 stack.

---

## Driver recode (RFC-CHG-MW-002 open question a)

The unofficial names are mapped as follows. Weights and signed scores are left as they were.

| Previous name | Official name |
|---------------|---------------|
| `selective_framing`, `threat_framing`, `markets_frame`, `legal_jeopardy_frame`, `outcome_credit`, `platforming`, `neutral_report` | `framing` |
| `omission_or_emphasis` | `omission` |
| `source_selection` | `one_sided_sourcing` |

---

## Endpoints verified on 20 Nov 2026 (default TLS, no bypass)

| Outlet | Working source | Notes |
|--------|----------------|-------|
| News24 | Dated sitemaps `https://www.news24.com/news24/sitemapindex/0/{year}/{month}/{day}` (also `/2026/05/01`). robots.txt lists `https://www.news24.com/sitemap`. | Advertised RSS `https://feeds.24.com/articles/news24/topstories/rss` failed with a TLS unexpected-EOF. Logged; not used as a source. |
| Daily Investor | RSS `https://dailyinvestor.com/feed/`; sitemap `https://dailyinvestor.com/wp-sitemap.xml` (posts only). | |
| Newsday | RSS `https://newsday.co.za/feed/`; sitemap `https://newsday.co.za/wp-sitemap.xml` (posts only). | Some sitemap `lastmod` values look like later edits, not original publication dates. The rule prefers RSS `pubDate` then a URL date then `lastmod`. |
| Daily Maverick | RSS `https://www.dailymaverick.co.za/dmrss/`; sitemap `https://www.dailymaverick.co.za/sitemap_index.xml` (`article-sitemap*` only). | |
| GroundUp | RSS `https://www.groundup.org.za/sitenews/rss/` (canonical `https://groundup.org.za/sitenews/rss/`); sitemap `https://groundup.org.za/sitemap.xml`. | |
| The Citizen | RSS `https://www.citizen.co.za/feed/`; sitemap `https://www.citizen.co.za/sitemap_index.xml` (`post-sitemap*` whose index `lastmod` is on or after the window start). | |
| SAPS (watch only, not a media outlet) | `https://www.saps.gov.za/services/crimestats.php` | Known incomplete chain: `CERTIFICATE_VERIFY_FAILED` / unable to get local issuer certificate. Logged; verification not disabled. |

---


## Collection run (20 Nov 2026, Africa/Johannesburg)

Run id `collect-2026-11-20T2022+0200`. Window `2026-05-01`–`2026-11-20`. Verification stayed on.

**TLS / certificate errors** (logged; run continued):

- `www.saps.gov.za` at 20:33:34 SAST — `CERTIFICATE_VERIFY_FAILED`: unable to get local issuer certificate (known incomplete chain).
- `feeds.24.com` at 20:33:34 SAST — `UNEXPECTED_EOF_WHILE_READING` on the advertised News24 Top Stories RSS feed.

No other fetch errors were logged on this run.

**Candidates after path filters, permalink-date recovery, window filter, dropping 35 URLs that matched the local private-names denylist (gitignored; the name is not recorded here), and dropping 21 known-paywall URLs at draw time:**

| Outlet | Candidates in window | Weeks with a draw | Drawn (`k=2`) |
|--------|----------------------|-------------------|----------------|
| News24 | 10,464 | 30 | 60 |
| Daily Investor | 2,049 | 30 | 60 |
| Newsday | 1,559 | 26 (publication was sparse in May, consistent with the June relaunch) | 52 |
| Daily Maverick | 5,015 | 30 | 60 |
| GroundUp | 762 | 30 | 60 |
| The Citizen | 11,548 | 30 | 60 |
| **Total** | **31,397** | | **352** |

Permalink dates recovered the Daily Maverick universe (sitemaps often omitted `lastmod`; URLs are `/article/YYYY-MM-DD-…`). Sitemap `lastmod` remains the date source for Daily Investor, Newsday, GroundUp and The Citizen. The Citizen November lastmod counts are much higher than earlier months and may include bulk lastmod refreshes; that is a date-quality caveat, not a reason to disable TLS or to invent a post-hoc day cap. A coded replacement, if needed later, follows the pre-registered remainder rule.

## Success

- Tests pass, including the former DI/Newsday xfails (now expected passes).
- Collector unit tests prove TLS errors are logged (host, error, SAST time) and the run continues, and that the source does not weaken verification.
- `neutral_random_v1` produces the same draw twice from the same candidates.
- The seed file and draw list are committed.
- Site build succeeds; noindex, robots and the DRAFT banner stay.
- Pickaxe over the denylist is 0. review-kit has no new open findings except the known old-identity commits.

## Rollback

Git: `git checkout dev/chg-mw-008-collectors` is this change; reset or revert back to `be75dedf46442bcdabac04f344aae861787076a6` (the 007 merge). Forward-only: no rebase, amend, or force. Never on `main`.

## Seen, not touched

- `scripts/write_di_pilot.py`, `scripts/write_nd_pilot.py`, `scripts/write_nd_pilot_v2.py` still contain some unofficial driver names and are not a live build path.
- Mail & Guardian, IOL (as a scored outlet), and broadcasters are not onboarded here.
- Existing News24 `neutral_random` rows from the mid-week proxy pass are not redrawn.


## Review follow-up (20 Nov 2026)

Responds to reviewer B's blocking notes on this change, on top of the rebuilt 008 head `4948167836d45e6fd2e0d5add4c7db935d44a15c` and the forward merge of the 003–005 follow-ups.

1. `scripts/collect.py` still logs TLS and other fetch errors and continues to the next URL, but `main` now exits non-zero when any error was logged. The locked candidates file is not overwritten unless `--overwrite-locked-candidates` is set. Response bodies are capped at 5,000,000 bytes.
2. `data/sampling/neutral_random_v1.json` now pins `candidates_sha256`, `draw_sha256`, and per-outlet `candidate_counts`. A test fails if a third of one outlet's candidates is dropped, and another test checks the pinned hashes.
3. A test freezes historical CSV `weight` values and JSON `signed_score` values (and the CSV signed scores).
4. The nine findings that carried a `neutral_random` tag but were not drawn with `neutral_random_v1` (`F-N24-NEUT-AB-01`, `F-N24-NEUT-CAPA-01`, `F-N24-NEUT-MACU-01`, `F-N24-NEUT-AB-X-01`, `F-DI-16`, `F-DI-17`, `F-ND-14`, `F-ND-15`, `F-ND-22`), and their associated article and control rows, are retagged `legacy_neutral`. METHODOLOGY 8a option (b) weights locked `neutral_random` highest and does not give `legacy_neutral` that weight. Published scorecards stay unweighted unless a score run chooses option (b).
5. The frozen-weight recode note is now on the Daily Investor and Newsday finding CSV rows that were recoded (15 + 19 = 34 rows; every unofficial driver remapped in CHG-MW-008). The missing space before "Driver recoded" in the JSON (and now CSV) notes is fixed. Historical weights and signed scores are unchanged.
6. The STATUS row that cited unreachable commit `9d7b194` is removed. The rebuilt 008 commit on `be75ded` remains `4948167`.
7. `sample_neutral_random.load_private_name_terms` fails if the denylist file is missing, instead of drawing unfiltered.

Rollback for this follow-up: `6b5d88f17bf86648e860415759cf123b0575fc59`. Local DEV only; not pushed; not merged; not deployed.

## Sign-off

Author: the bot. Sign-off is by someone other than the author. Owner direction (relayed) was to do this work on a local branch only. Owner GO is still required, naming the head, before push, PR, merge to `main`, or deploy.
