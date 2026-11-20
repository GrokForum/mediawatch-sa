# RFC-CHG-MW-010 — Phase-2 trio sample (Daily Maverick, GroundUp, The Citizen) (DEV)

**Status:** Local branch `dev/chg-mw-010-phase2-trio`. Not pushed; no PR; not merged; not deployed.  
**Environment:** DEV — branch `dev/chg-mw-010-phase2-trio`, created from `dev/chg-mw-009-pilot-register` at `c0cc4dc79003ee1de1f38bae7b73ffb5d7cf6c5c`.  
**Pre-change SHA (rollback base):** `c0cc4dc79003ee1de1f38bae7b73ffb5d7cf6c5c`.  
**Date:** 20 Nov 2026 (Africa/Johannesburg)  
**Repo:** https://github.com/GrokForum/mediawatch-sa (PUBLIC). This RFC does not change GitHub Pages settings, DNS, or indexing.

---

## Environment plan

| Env | What it is | Points at production? |
|-----|------------|------------------------|
| DEV | This local branch. Phase-2 coding, the coverage-gate mark, and unit tests can be inspected locally. | No. |
| TEST | Not stood up. | — |
| PROD | GitHub Pages, still deploying from `main`. | Only after a later, named deployment RFC with the owner's own GO on the exact head. Publishing these phase-2 scores also needs a separate owner sign-off that the pilot has been reviewed. |

---

## Goal

Code the locked `neutral_random_v1` draws for Daily Maverick, GroundUp and The Citizen (60 + 60 + 60 = 180 slots) the same way as CHG-MW-009: fetch free text only (TLS verification on; no paywall bypass; collector errors logged and the process fail-closed). Record every coded article. Neutral ones are clean rows in the denominator. Add a finding only where a driver really fires, with an exact quote from a fetch done in this change. On the site, mark the trio as phase 2, not yet past the coverage gate: show findings, but do not publish outlet or actor scores until the owner signs off that the pilot has been reviewed. Flag Citizen lastmod-only date risk in this RFC without changing the locked rule. Park Mail & Guardian, IOL and the broadcasters in `docs/LATER.md`.

---

## What changes (exact files)

| File | Change |
|------|--------|
| `scripts/fetch_draw.py` | Exit non-zero when collector errors were logged (fail-closed). Phase-2 fetch writes a separate status table so the 009 status is not overwritten. |
| `data/sampling/neutral_random_v1_fetch_status_phase2.csv` | **New.** Fetch outcomes for the 180 trio slots (URLs and metadata only; no bodies). Run `fetch-010-2026-11-20`. All 180 slots `full_text_curl`. |
| `data/dailymaverick_phase2_findings.json` / `.csv` | 60 v1 articles, 60 coded-clean rows, 0 findings. |
| `data/groundup_phase2_findings.json` / `.csv` | 60 v1 articles, 60 coded-clean rows, 0 findings. |
| `data/citizen_phase2_findings.json` / `.csv` | 60 v1 articles, 58 coded-clean rows, 2 findings (`F-CIT-NRV1-01`, `F-CIT-NRV1-02`). |
| `scripts/build_site.py` | Phase-2 trio on the home page and publication pages: findings and v1 sample visible; scorecards omitted; coverage-gate copy. Manifest keeps scored `publications` at 3 and adds `phase2_publications`. |
| `tests/test_site.py` | Gate copy; no published phase-2 scores; v1 completeness for the 180; quote typography; `docs/LATER.md` contents. noindex/DRAFT remain. |
| `docs/LATER.md` | **New.** Parks Mail & Guardian, IOL, and the broadcasters' news sites. |
| `changes/RFC-CHG-MW-010.md` | This record, including Citizen lastmod risk, the News24 60/60 sanity check, and collection counts. |
| `docs/STATUS.md` | Change-log row. |

`data/fetched_articles/` stays gitignored. Article bodies are not committed.

## Collection and coding counts

Window: 1 May–20 November 2026 (Africa/Johannesburg). Algorithm `neutral_random_v1`, seed `20261120`, k=2 per outlet per ISO week.

| Outlet | Sampled | Fetched | Paywalled-replaced | Replaced as unusable (not a paywall) | Coded | Clean | New findings |
|--------|---------|---------|--------------------|--------------------------------------|-------|-------|--------------|
| Daily Maverick | 60 | 60 | 0 | 0 | 60 | 60 | 0 |
| GroundUp | 60 | 60 | 0 | 0 | 60 | 60 | 0 |
| The Citizen | 60 | 60 | 0 | 2 (depth 1) | 60 | 58 | 2 |
| **Phase-2 total** | **180** | **180** | **0** | **2** | **180** | **178** | **2** |

The two Citizen replacements were not paywalls. The original URLs `https://www.citizen.co.za/business/guardians-of-the-future-of-inclusive-conservation/` and `https://www.citizen.co.za/business/understanding-the-brain-and-the-person-behind-it/` extracted 0-character bodies (`too_short`). The pre-registered remainder URLs from the same weeks were used: `https://www.citizen.co.za/news/ramaphosa-says-gbv-means-south-african-women-are-not-free/` and `https://www.citizen.co.za/news/south-africa/elections/zumas-mk-party-set-to-be-ethekwinis-biggest-party-anc-struggles/`.

No new TLS or collector errors were logged in this fetch. `data/collector_errors.csv` still has only the two 008 watch rows (SAPS `CERTIFICATE_VERIFY_FAILED` and `feeds.24.com` `UNEXPECTED_EOF_WHILE_READING`, both 20 Nov 2026 20:33:34 SAST). Verification was not disabled.

### Findings (The Citizen)

- `F-CIT-NRV1-01` (`A-CIT-NRV1-2026W24-1`, editorial, 9 June 2026): AGAINST ANC, driver `framing` (weight 1.0). Quote Proven in the fetched body. Fact label Alleged for the quoted moral and causal claims.
- `F-CIT-NRV1-02` (`A-CIT-NRV1-2026W32-2`, View of the Week column by Kyle Zeeman, 7 August 2026): AGAINST Jacob Zuma, driver `framing` (weight 1.0). Quote Proven in the fetched body, including the typographic apostrophe in "won't". Fact label Alleged. A second finding on Trump was not added from the same simile.

Jacob Zuma is recorded as a person-actor and is not given a left/right axis placement in this change. Daily Maverick and GroundUp produced no finding that clearly met the §5 gates; labelled analysis and demonstrated accountability reporting were left clean rather than padded.

Internal *n* for phase-2 actors (not published on the site): ANC 1 and Jacob Zuma 1, both findings-only. No phase-2 actor reaches provisional or scored status.

The News24 60/60 sanity check found no missed driver, so no forward-commit News24 finding is added here.

---

## What stays

- No push, no PR, no merge to `main`, no deploy.
- `noindex` / `robots.txt` `Disallow: /` / DRAFT banner.
- Five fact labels. Private people unnamed. Exact fetched quotes only; no fabrication.
- TLS verification is never disabled. Errors are logged; the fetch exits non-zero if any error was logged.
- The locked `neutral_random_v1` seed, window, k, date-preference order, and replacement rule are not changed.
- The scored three-outlet pilot (News24, Daily Investor, Newsday) and its published scores are not rewritten, except a forward-commit fix if the News24 60/60 sanity check finds a missed finding.
- IOL and EWN remain an error watch, not a phase-2 or scored-pilot expansion.
- Historical signed scores are not rewritten.

---

## Coverage gate

Publishing **scores** (outlet or per-actor means with *n* status) for Daily Maverick, GroundUp or The Citizen is gated. This RFC shows the coded sample and any findings so they can be reviewed. It does not claim a publication score. A later, named decision by the owner that the pilot has been reviewed is required before those scores are published.

---

## Citizen lastmod-only dates (known bias risk; rule unchanged)

The locked rule prefers a date in the article permalink, then a same-day feed date, then sitemap `lastmod` or a feed date when the URL has no date. That order is not changed here.

Every Citizen candidate in the locked v1 universe (11,548 URLs) has **no date in the URL**. All of them carry `date_source=lastmod_or_pub`. Of those, 5,494 (47.6%) have a lastmod/feed timestamp in November 2026 (Africa/Johannesburg). A lastmod is an update time, not a reliable publication date: older articles that were recrawled or lightly edited in November can flood the November strata, and items whose lastmod later moved out of an earlier week can drop out of that week's pool.

The v1 draw is still two URLs per ISO week, so the 60 Citizen slots are spread across 30 weeks (seven of the 60 have a November lastmod). That stratification limits, but does not remove, the bias. November lastmod-only Citizen candidates are a **known date-quality risk** for this outlet's v1 sample and should be kept in mind when the phase-2 findings are reviewed. GroundUp URLs in this universe also lack permalink dates, but the lastmod mass is much smaller (762 candidates) and is not November-dominated in the same way. Daily Maverick permalinks carry dates; all 60 DM draws used `date_source=url`.

---

## News24 60/60 clean — coding was not superficial

News24's locked v1 draw ended 60 of 60 coded clean (36 slots used a pre-registered paywall replacement, which shifted the sample toward business and world news). The 60 were read under METHODOLOGY 0.5. Actor-adjacent pieces were checked for drivers; none fired. Five examples:

1. **Law firms in court over BEE rules** (`A-N24-NRV1-2026W19-2`). A Reuters-sourced court preview. The firms' challenge, the government's code, and black lawyers' discrimination claims are all reported, with the firms' defences. The outlet is not adding an unattributed FOR/AGAINST line.
2. **Water and Sanitation Minister Pemmy Majodina apologises for swearing** (`A-N24-NRV1-2026W38-1`). Straight news of a public apology. The DA, ActionSA and AfriForum responses are attributed; Majodina's statement is carried. That is sourced accountability, not a loaded frame.
3. **Cyril Ramaphosa \| SA’s food supply rests on white farmers** (`A-N24-NRV1-2026W42-2`). A signed presidential column that News24 hosted. The voice is Ramaphosa's, clearly bylined. Hosting a public-office column is not scored as News24 writing FOR Ramaphosa, and Ramaphosa is not coded as a News24 journalist.
4. **Early results show major shift from ANC; … today’s top 7 stories** (`A-N24-NRV1-2026W45-2`). A news-digest roundup of the day's stories, not an editorial argument about the ANC. (A farm-attack item in the same package names a private victim; that person is not recorded in the register.)
5. **IEC orders revote at Northern Cape voting district** (`A-N24-NRV1-2026W46-1`). A process story sourced to an IEC statement and the IEC chairperson, including the statutory basis for a revote. No driver fires.

If a later re-read shows a missed driver, that is a forward commit on this branch, not a rewrite of the 009 scores.

---

## Success

- Every v1 phase-2 slot is either a fetched-and-coded article (finding or clean) or an honestly recorded exhaustion of replacements.
- Findings pass the §5 gates (exact quote, URL, datetime, byline, steelmen, fact label, fetched here).
- The site marks the trio as phase 2, shows findings, and does not publish scores for them.
- Citizen lastmod risk is recorded here; the locked rule is unchanged.
- `docs/LATER.md` lists Mail & Guardian, IOL, and the broadcasters.
- Tests, build, pickaxe on the staged tree (0), and review-kit pass except for known old-identity commits.
- POPIA review PASS.

## Rollback

Git: return this branch to `c0cc4dc79003ee1de1f38bae7b73ffb5d7cf6c5c`. Forward-only: no rebase, amend, or force. Never on `main`.

## Sign-off

Author: the bot. Sign-off is by someone other than the author. Owner direction was to do this work on a local branch only, on top of `c0cc4dc`. Owner GO is still required, naming the head, before push, PR, merge to `main`, or deploy. A separate owner sign-off that the pilot has been reviewed is required before phase-2 scores are published.
