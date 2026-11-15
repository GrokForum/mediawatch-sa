# RFC-CHG-MW-001 — Catch-up: paywall recovery, Cassian cross-check, Cowan sample, two meters

**Status:** PENDING REVIEW (Cavus, Cassian) and owner GO  
**Environment:** DEV — local branch only, not published  
**Branch:** `dev/chg-mw-001-catchup` (Cavus-specified name; used instead of the it-project default `rfc/<ver>` pattern)  
**Pre-change SHA (origin/main after sync):** `0d88905a569e2f997bbdf7146eb398749ae93c24`  
**Date:** 15 Nov 2026 (Africa/Johannesburg)  
**Repo:** https://github.com/GrokForum/mediawatch-sa (PUBLIC). Pushing publishes. No push, no PR, and nothing committed to `main` in this change.

---

## Environment

DEV only. Work is on `dev/chg-mw-001-catchup`, branched from updated `main` at the pre-change SHA above. GitHub Pages, DNS, and repository settings are not touched. Nothing in this RFC goes to PROD until the owner gives a GO on the exact head.

---

## Goal

Commit, locally only, the unpushed catch-up already done in the working tree after 5 Nov 2026:

1. Legitimate free paywall recovery on the News24 register, with method note and recode of one full-body recovery.
2. Cassian News24 bias-meter cross-check: seed stays gitignored and reference-only; zero calls imported as findings; three references logged.
3. Kyle Cowan added as a public-role News24 journalist, with a neutral May–Oct 2026 sample.
4. Two meters, kept separate: **PRIMARY** remains the owner's FOR/AGAINST named-actor meter; **SECONDARY** is a left/right lean for reader convenience, with its own method, map, schema and draft scores, never mixed into primary scores.

---

## Scope — files that change

### Added

| Path | Role |
|------|------|
| `docs/FREE_ACCESS.md` | Legitimate free-access method (Wayback, existing archive.today reads only, republication, author gift links, library PressReader). No bypass. |
| `docs/CROSSCHECK_CASSIAN.md` | Cassian seed mapping (0 findings, 3 references); Cowan sample notes. |
| `docs/LEFT_RIGHT_METHOD.md` | Secondary lean method, banner, formula, min-*n*, sample-frame split, contested-placement rule. |
| `data/actor_axis_map.csv` | Actor → economic/social axis placements, sources, contested flags. Unmapped actors excluded from lean. |
| `data/lean_scores_draft.json` | Draft secondary scores for News24, Daily Investor, Newsday, Basson, du Toit, Cowan. |
| `data/external_references.json` | Three Cassian references; not imported as findings or lean inputs. |
| `changes/RFC-CHG-MW-001.md` | This record. |

### Modified

| Path | Role |
|------|------|
| `data/paywall_register.csv` | Recovery columns (`recovery_source`, `recovery_url`, `snapshot_timestamp`, `recovery_status`, `recovery_notes`, `recovered_at_sast`). Counts: full 2, partial 12, still_blocked 7. |
| `data/news24_pilot_findings.json` / `.csv` | Paywall recode of F-N24-FAV-ESKOM-01 (Wayback full body); Kyle Cowan sample (5 findings + 3 balanced_controls); meta for recovery and Cassian passes. Findings total **59**. |
| `data/people.csv` | Added `kyle_cowan` (public role, `@CowansView` API-verified 5 Nov 2026). |
| `data/schema.json` / `data/schema.sql` | v0.4-draft: `lean_score_runs`, `lean_scores`, `actor_axis_map` kept separate from primary `scores`. Also: `signed_score` and `credit` may be null (accountability_exempt / no credit); optional `sample_frame` and `accountability_status` documented. |
| `docs/METHODOLOGY.md` | Version 0.4-draft. New §0 on two meters. Primary rules in §§3–8 unchanged. |
| `plan.md` | Project rule 1 updated to two meters; Cassian item closed as reference-only; secondary-meter section added. |
| `docs/STATUS.md` | Paywall-recovery and Cassian/Cowan notes; this RFC change-log line. |

### This-pass corrections before commit (not in the original uncommitted tree)

- Removed `dm_ids` and `dm_times_sast` from `data/external_references.json` so internal DM-extract locators are not published. A `seed_locator_note` points at the gitignored seed only.
- Replaced the stale News24 meta flag `cassian_crosscheck: "NO_CASSIAN — seed … not present"` with a pointer to `cassian_seed_pass` / `docs/CROSSCHECK_CASSIAN.md`.
- Documented in `lean_scores_draft.json` meta that accountability_exempt findings (`signed_score` null) are currently included in *n* with contribution 0, preserving the 5 Nov 2026 draft figures. Reviewers may prefer excluding them.

---

## What stays unchanged

- Primary FOR/AGAINST scale (−2…+2), driver list in the methodology, fact labels (Proven, Established, Alleged, Disputed, Not established), min-*n* rules, sample-frame split, AfriMAGA / repost / first-name / City Press defaults.
- Publications seed, Daily Investor and Newsday pilots, `data/pilot_findings.json`, `docs/PAYWALLS.md`, `scripts/write_*_pilot.py`, `index.html`, `CNAME`, `README.md`, `.gitignore`.
- `seed/` and `data/fetched_articles/` remain gitignored and are **not** staged or committed (Cassian DMs, AGOA casebook, copyrighted full texts).
- GitHub Pages, DNS, and repository settings.
- No new fact labels.

---

## How success is proven

1. Every `data/*.json` file parses.
2. Schema validation (JSON Schema 2020-12) of findings, `actor_axis_map`, `lean_scores`, `people.csv` and `publications.csv` where feasible. News24 and worked-example findings pass. Known mismatches on already-published Daily Investor / Newsday pilots are listed under "Seen, not touched".
3. Every CSV loads with a consistent column count.
4. Every finding (JSON and CSV) has a source HTTP(S) URL and a non-empty exact quote.
5. `fact_label` is only one of: Proven, Established, Alleged, Disputed, Not established.
6. Draft lean scores recompute from primary findings × `actor_axis_map.csv` (exempt `signed_score` null treated as 0, matching this draft).
7. `git check-ignore` still excludes `seed/` and `data/fetched_articles/`; those paths are not staged.
8. No `/workspace/agoa-sa` paths in committed files.
9. POPIA scan of `origin/main..HEAD` returns PASS (see below).

Existing `scripts/write_*_pilot.py` were **not** re-run: they would overwrite the already-published Daily Investor / Newsday pilots.

---

## Rollback

Pre-change SHA: `0d88905a569e2f997bbdf7146eb398749ae93c24`.

- Before any merge: delete or close the branch / PR; `main` is untouched.
- After a future owner-GO merge: `git revert` of the merge or of the CHG-MW-001 commit(s), back to the pre-change SHA (or an equivalent revert commit on `main`).
- No `.bkp` files. No live data to restore. Pages content does not change until a later GO merges to `main`.

---

## Seen, not touched

- Daily Investor and Newsday pilots (already on `main`) use driver strings outside the methodology enum: `selective_framing`, `outcome_credit`, `platforming`, `source_selection`, `omission_or_emphasis`, `threat_framing`, `markets_frame`, `legal_jeopardy_frame`, `neutral_report`. Recoding those drivers onto the official list is a separate change. (`accountability_status: control` on F-DI-16, F-ND-06 and F-ND-22 is now in the schema enum and defined in METHODOLOGY §8c. The *values* were already in those published pilots; the *validation failures* were introduced in the first CHG-MW-001 commit, when the enum was added without `control`. That claim of “pre-existing failures” in an earlier draft of this RFC was wrong and is corrected here.)
- News24 findings and meta still carry `methodology_version: 0.3-draft` because primary coding rules did not change; the document is 0.4-draft for the secondary meter.
- Historical "Gaps" in `docs/STATUS.md` still say some early items were missing; later sections and this RFC supersede that.
- `index.html` placeholder, HTTPS/CNAME, and the unused SQLite instantiation.
- Article IDs such as `A-N24-KC-2026-07-25-MONEY` and `A-N24-KC-2026-09-05-ORANIA` keep the URL-slug date; `published_at` is the page date (26 Jul / 6 Sep) with `published_at_precision=date`. The IDAC page date (19 Jul vs stored 18 Jul) was not in the review-fix list and is unchanged.
- Scripts already on `main` still use `Path("/workspace/mediawatch-sa/data")` (inside this project, not an outside-bot path).

---

## POPIA

**Verdict: PASS** (after the redaction below). This is a public repo; the scan covered the full intended diff (`origin/main`..branch).

### Removed

- `dm_ids` and `dm_times_sast` in `data/external_references.json` (internal identifiers and times from a gitignored DM extract). Not required in a public file. Locators stay only in `seed/cassian-news24-bias-meter.md` (gitignored).
- The name of a junior City Power employee (a private person) that had appeared in F-N24-KC-01 evidence notes as part of a dismissed-complaint list. Replaced with “naming of a City Power employee.” No other committed file still carries that name.

### GitHub timeline scrub — confirmed clear

On 5 Nov 2026 a third-party personal GitHub timeline was wrongly counted as a recovery for "Travels to Trumpistan" and then scrubbed. `news24_pilot_findings.json` meta `paywall_recovery_pass.correction_note` already records: "Removed third-party as recovery for Travels to Trumpistan; row is partial via Wayback paywall shell only. JG-01/JG-02 restored to News24 headline/lede evidence." A full-tree search (including gitignored `seed/` and `data/fetched_articles/`) found no `github.com` timeline, gist, overview, contributions, or personal-GitHub recovery URL or wording.

### Reviewed and retained

- Journalists, editors and public figures in their public role (names, public X handles / user IDs API-verified from public profiles, bylines, Press Ombud officers).
- Exact Ombud-cited quote in F-N24-KC-01 naming the City Power **spokesperson** (a public-role official, and a different person from the junior employee above) and News24 journalist Khaya Koko. The spokesperson is also in the published headline and the canonical URL, which cannot be altered. The scored actor remains the institution City Power. The junior employee’s name is not in that quote and was not redacted as if it were the spokesperson.
- Mashatile "son-in-law" item kept only as the published News24 headline and canonical URL; the private debtor is **not named** in our files and is **not scored** as an actor.
- SAAI president Theo De Jager named in a public caption in a public-role context.

### Not found

- SA ID, passport or phone numbers, emails, physical addresses, account numbers, plates, precise home locations, keys or tokens.
- Private citizens named as finding actors or otherwise identified beyond a published headline's role description.
- Linking of a pseudonymous account to a real person (Cowan's correct public handle `@CowansView` is API-verified; the note that `@kylecowan` is an unrelated US account does not identify a private person).
- Personal (non-public-role) details about journalists (no family, home, health or private contact details).
- Any `/workspace/agoa-sa` path, or the author of the owner-supplied commentary in that private foundation file.

---

## Review fixes (15 Nov 2026, after Cavus PASS_WITH_CONCERNS)

A second commit on this branch addresses the review. It does not amend the first two commits. Pre-change SHA for the *branch* remains `0d88905a569e2f997bbdf7146eb398749ae93c24`. Rollback of **only** the review-fix commit is revert of that commit (parent `9515e9ce65d41e74bc090d49237c196d6eb7ecdd`).

1. Junior City Power employee: name removed from evidence notes and the tree; referred to only by role. Spokesperson in the Ombud quote is a different, public-role person (see POPIA).
2. Cowan sample documented honestly: 11 fetched, 7 coded; four exclusions listed; KC-01 = `counter_pull`; other coded pieces = `purposive` (new sample_frame; no random rule was invented). Lean/frame splits recomputed; News24 `neutral_random` is now findings-only (*n*=4).
3. `control` added to the schema enum and defined in METHODOLOGY §8c. The earlier “pre-existing failures” wording in this RFC is corrected above.
4. F-N24-KC-05 quote extended to the full OG sentence ending “into police Crime Intelligence,” verified against the Wayback OG.
5. `lean_*` stored as **null** when `flag=findings_only` (Cowan and other sub-*n* groupings). No hidden raw number.
6. REF-02 wording updated for the two meters.
7. `docs/FREE_ACCESS.md` list restored to 1–5 (missing step 3 is republication search).
8. CHG-MW-002 rollback SHA in `docs/STATUS.md` is `d3ca635` (or revert `9515e9c`), not `0d88905`.
9. METHODOLOGY §0: “maintains two measures; lean hidden until owner GO.”
10. `schema.sql` findings table: nullable `sample_frame` and `accountability_status` (and `published_at_precision`).
11. KC-02–KC-04 `published_at` set to the page dates 26 Jul and 6 Sep, with `published_at_precision=date`.
12. Other bots’ `/workspace/…` paths removed from `docs/STATUS.md`; hub path in STATUS and METHODOLOGY is now relative `plan.md`.
13. `people.csv` du Toit note is public-role only; no internal AGOA casebook reference.

**Status remains: PENDING REVIEW (Cavus, Cassian) and owner GO.**

---

## Sign-off


Four-eyes review is for Cavus and Cassian (expert, shadow, charter, drift). This RFC is not self-signed SUCCEEDED.

**Status remains: PENDING REVIEW (Cavus, Cassian) and owner GO.**
