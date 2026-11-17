# RFC-CHG-MW-002 — Drill-down site: generator scaffold and three-outlet pilot (DEV build)

**Status:** Owner GO to review and merge, and GO to switch GitHub Pages to the generated site, given 17 Nov 2026 20:01 SAST. Owner NO GO on search-engine indexing: `robots.txt` stays `Disallow: /` and every page keeps `noindex, nofollow`.  
**Environment:** DEV — branch `dev/chg-mw-002-site-rw2`, rebuilt on `main` `d1029af` after the second history rewrite (17 Nov 2026). This RFC itself changes no GitHub Pages setting, DNS or the live `index.html` placeholder; the Pages switch is a separate deployment step.  
**Branch:** `dev/chg-mw-002-site-rw2` (used instead of `rfc/<ver>` to match the project's existing `dev/chg-mw-*` naming)  
**Pre-change SHA (rollback base):** `d1029af164f1fb8a150360f877e7c58b021ed92c` (`main` after the INC-MW-001 merge, as rewritten on 17 Nov 2026). Earlier SHAs in this file (`c4f6e11`, `0d88905`) predate the history rewrites.  
**Date:** 17 Nov 2026 (Africa/Johannesburg)  
**Repo:** https://github.com/GrokForum/mediawatch-sa (PUBLIC). Production URL (unchanged by this RFC): https://mediawatch.grokforum.site

History: on 15 Nov this RFC was a plan only (six open questions). It was merged to `main` as plan text with PR #1. This revision records the owner's answers (relayed by the orchestrator on 17 Nov) and adds the first DEV build. A GO to merge this branch is **not** a GO to deploy the site or to remove `noindex`; each needs its own GO.

---

## Owner answers (17 Nov 2026, relayed by the orchestrator)

| # | Question (15 Nov) | Owner answer |
|---|-------------------|--------------|
| 1 | Python generator or no-build bundle? | Use a static site generator; pick a simple one and justify it here. |
| 2 | First public build: which outlets? | Pilot sample: **News24, Daily Investor and Newsday** ("Daily Investigator" in the relay; see open question g). |
| — | Scope | **All South African media** in the end. The three outlets are only the pilot, so a phased coverage plan is added below. |
| — | Paywalls | **No paywalls, ever.** Judge only free public content. |
| 3 | Lean-meter sample size | Still open (question d). The lean meter stays hidden. |
| 4 | TEST preview URL | Still open (question e). |
| 5 | Corrections contact | Still open (question f). |
| 6 | Merge GO ≠ index GO | Not changed: noindex stays until a separate GO. |

---

## Environment plan

| Env | What it is | Points at production? |
|-----|------------|------------------------|
| DEV | This local branch. `python scripts/build_site.py` writes `_site/` (gitignored); view by opening `_site/index.html` or `python -m http.server -d _site`. | No. |
| TEST | Not stood up (open question e). | — |
| PROD | GitHub Pages, legacy build from the root of `main`, custom domain `mediawatch.grokforum.site`. | Only after a later, named deployment RFC with its own owner GO. |

---

## Goal

A static drill-down site, **publication → writer/editor → article or public post → finding (evidence)**, built from the committed `data/` files. Each finding page shows the exact quote, source link, named actor, FOR/AGAINST direction, driver, fact label (only Proven, Established, Alleged, Disputed, Not established), signed score and the steelman on both sides. The primary FOR/AGAINST meter is the only meter rendered.

---

## What changes (exact files)

| File | Change |
|------|--------|
| `scripts/build_site.py` | **New.** Static generator (Python 3 standard library only). |
| `site/assets/style.css` | **New.** Plain CSS; no web fonts, CDNs or trackers. |
| `scripts/validate_schema.py` | **New.** Read-only JSON Schema check of the findings files, `people.csv` and `publications.csv`. |
| `tests/test_site.py` | **New.** pytest suite (see Tests). |
| `requirements.txt` | **New.** Pinned check tools: `jsonschema==4.23.0`, `pytest==8.3.4`. The generator itself needs none. |
| `data/paywall_exclusions.csv` | **New** (CRLF, like the other `data/*.csv`). The 20 findings excluded under the no-paywall rule. |
| `.gitignore` | Adds `_site/`, `__pycache__/`, `.pytest_cache/`, `tests/private_names.local.txt`. |
| `docs/METHODOLOGY.md` | New §5a: free public content only (owner rule, 17 Nov 2026). |
| `docs/FREE_ACCESS.md` | Standing no-paywall rule at the top; coding step 5 changed from "code from headline/OG" to "do not code". |
| `docs/PAYWALLS.md` | Standing rule at the top; the "later login/subscribe run" section marked superseded (kept as history). |
| `changes/RFC-CHG-MW-002.md` | This record. |
| `docs/STATUS.md` | Two change-log rows: the PR #1 merge (17 Nov) and this DEV build. |
| `README.md` | Short "Build and test locally" section. |

**What stays:** root `index.html` (the live "coming soon" placeholder) and `CNAME` are byte-identical to `0280f59` (the commit that last changed them; a test checks this). No findings, people, publications, schema, paywall register or lean files are edited. GitHub settings, Pages and DNS are untouched.

---

## Generator choice and justification

**Choice: a small plain-Python generator (`scripts/build_site.py`), standard library only.**

- **The site is data, not prose.** Pages come from JSON/CSV records (findings, articles, posts, people) with roll-up arithmetic. Markdown-first generators (Jekyll, Hugo, Pelican, MkDocs) would need plugins or template logic for that.
- **The rules live in code, where tests can check them.** Paywall exclusion, the n thresholds, the hidden secondary meter, the five fact labels and dropping internal fields (evidence notes, coder, credit, recovery URLs, teasers, post metrics, X user ids) are all enforced in one auditable file. A missing quote, URL, steelman or a disallowed fact label stops the build.
- **Minimal dependencies.** Python is already used in `scripts/`. Nothing to install to build, no Node, Ruby or Go toolchain, no template engine. Jinja2 was considered and not needed at this size. The two pinned packages are only for validation and tests.
- **No JavaScript and no external assets.** Every page is static HTML and one CSS file, so there is nothing to track readers and nothing loaded from third parties.
- **Jekyll (the native Pages engine) was rejected.** Liquid is awkward for exclusions and thresholds. It also publishes working files from the repo root as-is (see "Seen, not touched": that is already happening on the live domain).

### Output directory: `_site/`, gitignored

- In DEV, generated HTML is **not committed**. Review covers the source and the tests, and the output is rebuilt the same way each time from the same commit.
- Even if `_site/` were committed by mistake, the legacy Jekyll build on Pages **ignores folders starting with `_`**, so it could not appear on the live domain.
- For a **later deployment RFC (separate GO)** there are two options:
  - **A (recommended):** a GitHub Actions Pages workflow that runs the tests, builds `_site/` and deploys it as the Pages artifact. This switches the Pages source from "branch root" to "GitHub Actions" (a settings change), keeps generated HTML out of git, and stops Jekyll from publishing `docs/`, `data/` and `plan.md`.
  - **B:** commit the built files into the Pages root in a release commit, replacing the placeholder. No settings change, but generated HTML lives in git and the repo-root publishing problem below stays unless a `_config.yml` `exclude:` is added.
  - `/docs` as the Pages source is not an option, because `docs/` holds the method documents.

---

## Site structure (as built)

| Path in `_site/` | Page |
|------------------|------|
| `index.html` | Home: what this is; the three pilot outlets with findings shown and findings excluded (paywalled). |
| `p/<publication>/` | Publication: owner group (with its fact label), editor, excluded count, **scorecard per named actor**, writers, findings grouped by sample frame. |
| `w/<person>/` | Writer, editor or desk account: public role, verified public X handle only, person × actor scorecard, items, findings. |
| `a/<article>/`, `x/<post>/` | Article or public post: title, byline/account, date (SAST), source URL, sample frame, access note, findings. |
| `f/<finding>/` | Evidence: quote, source, actor, direction, driver, fact label, signed score, status, date, writer, item, frame, context line when the actor is inferred, both steelmen. |
| `method/`, `coverage/`, `corrections/` | Method summary (primary meter only), phased coverage plan, corrections and right of reply with a **placeholder contact** (open question f). |
| `robots.txt` | `User-agent: *` / `Disallow: /` |

Pilot build: **160 pages, 81 findings rendered** (News24 39, Daily Investor 19, Newsday 23), 64 items, 8 writer/desk pages, **20 findings excluded** under the no-paywall rule.

### Scoring as implemented (primary meter only)

- Publication × actor: mean of finding signed scores (METHODOLOGY §6.3). Person × actor: mean of item-level means (§6.2).
- *n* counts the findings that enter the mean: `bias`, `borderline` and `control` rows. `accountability_exempt` rows are shown for audit but not counted (§8b). Excluded paywalled findings are neither shown nor counted.
- Thresholds: *n* ≥ 10 shows the score; 5–9 shows it with a **provisional** badge; under 5 shows findings only (no number).
- Person × actor scores drawn only from `keyword`-frame findings are suppressed (§8a rule 2) and marked so.
- Every scorecard shows the sample-frame mix. `purposive` is labelled "frame pending owner acceptance".
- Daily Investor and Newsday findings with unofficial driver names are rendered as recorded, with a visible "driver name pending owner decision" badge. They are **not** recoded. Scorecards show how many such findings each row contains.
- **Secondary left/right meter:** not read by the generator (`lean_scores_draft.json` and `actor_axis_map.csv` are never opened) and not in the output. A test checks both. It stays hidden until the owner's GO.

### noindex

Every page carries `<meta name="robots" content="noindex, nofollow">`, and `robots.txt` disallows everything, until a separate owner GO to index.

---

## No paywalled content, ever (standing owner rule, 17 Nov 2026)

Bias is judged **only on what the public can read free**. Paywalled articles are **out of the sample** and **never scored**. Headlines, standfirsts and teasers **never** stand in for the body. No subscriptions, logins, user-agent spoofing, paywall-script stripping or bypass services. Recorded in `docs/METHODOLOGY.md` §5a, `docs/FREE_ACCESS.md` and `docs/PAYWALLS.md`.

**Applied to existing findings (evidence kept, not deleted).** A finding is excluded when it records an `access_limit`, its article's `access` is not a free value, its `access_note` records a paywall, or its URL is in `data/paywall_register.csv`. The generator detects these, `data/paywall_exclusions.csv` lists them, and a test requires the two to match. All 20 are News24. No Daily Investor or Newsday finding is affected: all their bodies were free.

| Basis | Findings |
|-------|----------|
| Paywalled body; coded from headline/standfirst only | F-N24-JG-01, F-N24-JG-02 |
| Paywalled body; coded from headline/OG teaser only | F-N24-PDT-COL-01, F-N24-PDT-COL-02, F-N24-EF-01, F-N24-AB-COL-01, F-N24-AB-COL-02, F-N24-NEUT-AB-01, F-N24-NEUT-CAPA-01, F-N24-CTR-SAAI-01, F-N24-CTR-PDT-01, F-N24-FAV-CALLAND-01, F-N24-FAV-SCHREIBER-01, F-N24-FAV-SCHREIBER-02 |
| Paywalled body; coded from archived (Wayback) headline/OG teaser only | F-N24-KC-02, F-N24-KC-03, F-N24-KC-04, F-N24-KC-05 |
| Paywalled body; quote taken from the free Press Ombud ruling | F-N24-KC-01 |
| Full body recovered from Wayback, but paywalled at source | F-N24-FAV-ESKOM-01 |

Effect: Kyle Cowan's five coded findings are all excluded, so he has no writer page in this build. News24 AfriForum moves to *n* = 10 (score −1.15). News24 ANC and Solidarity are *n* = 5 (provisional).

**Kept, but for owner review (open question h):** journalists' own public X posts that share or tease paywalled News24 pieces. They are judged on the post text only: F-N24-AB-X-06, F-N24-AB-X-12, F-N24-PDT-X-09 (driver `headline_body_gap`, coded without the body), F-N24-PDT-X-10, F-N24-PDT-X-12, F-N24-PDT-X-13, F-N24-PDT-X-14, F-N24-FAV-AB-X-CALLAND.

---

## Phased coverage plan (scope: all South African media)

No dates are promised. Each phase starts when its entry criteria are met. Every phase is free public content only.

| Phase | Outlets | Entry criteria |
|-------|---------|----------------|
| 0 Pilot | News24, Daily Investor, Newsday | Method, fact labels and thresholds stable; free-access check per outlet; this RFC reviewed. |
| 1 Major national dailies and weeklies | e.g. TimesLIVE / Sunday Times, Mail & Guardian, Daily Maverick, IOL, The Citizen, Business Day, Sowetan, Moneyweb, BizNews, GroundUp (free content only) | Pilot reviewed and corrected; driver list settled (question a); neutral-random sampling rule fixed per outlet; corrections contact live (question f). |
| 2 Broadcasters' news sites | SABC News, eNCA, EWN, Newzroom Afrika | Phase 1 reaches minimum *n* on its main actors; rule agreed for transcripts, clips and on-screen text. |
| 3 Regional, community, Afrikaans and other-language outlets | e.g. Maroela Media, Netwerk24/Rapport free pieces, regional and community titles, isiZulu/isiXhosa/Sesotho outlets | Coders able to read the language; translation and quote-fidelity rule agreed; regional actor list agreed. |
| 4 Scale-out | Remaining outlets; journalists' public posts at scale | Earlier phases stable; corrections process tested on real requests; owner GO on publishing person-level scores at scale. |

Mostly paywalled outlets are covered on free content only. Where too little is free to reach minimum *n*, the outlet shows findings only.

---

## POPIA safeguards (as built)

- Journalists, editors, desk accounts and public figures appear in their public role only. Writer pages show name, public role and, where verified, the public X handle. No X user ids, no contact details.
- Private individuals are never named. The junior City Power employee appears in no output. F-N24-KC-01, which concerns City Power, is excluded under the paywall rule anyway. A local-only (gitignored) denylist test checks the output for that name without committing it.
- Internal working fields are never rendered: evidence notes, coder, credit, recovery URLs, OG and standfirst teasers, post metrics. A few steelman strings carried an internal reviewer note (an arrow followed by a reviewer name). The generator strips those notes at render time; the data files are unchanged (see "Seen, not touched").
- The output contains no paths or text from `seed/`, `data/fetched_articles/`, internal working paths or other bots' paths. Tests check for 300-character runs of any locally fetched article body (none found) and that neither folder is tracked by git.
- popia-review verdict for this change: see "Sign-off and result" below.

---

## Tests and how success is proven

`python -m pytest -q` (with `requirements.txt` installed): **24 passed, 2 xfailed**. The xfails are strict and expected: Daily Investor and Newsday schema validation, open question a.

Covered: build succeeds (API and CLI); every finding page has the exact quote, an https source link, an allowed fact label and both steelmen; unofficial drivers are badged; no secondary-meter terms in any output file and the generator never opens the lean files; noindex on every page and robots `Disallow: /`; no scripts or external assets; root `index.html` and `CNAME` unchanged against `c4f6e11`; the exclusions file matches the rule; no excluded finding or registered paywalled URL rendered; thresholds on every scorecard row; publication scores recomputed independently; no private-citizen names (local denylist); writer pages public-role only; internal fields not rendered; no seed, fetched or private paths; no fetched article text; gitignored folders untracked; News24, `people.csv` and `publications.csv` pass the schema; DI/ND fail **only** on `driver: enum`; CRLF kept on `data/*.csv`.

Schema validation (`python scripts/validate_schema.py`): News24 findings, `people.csv` and `publications.csv` **PASS**. Daily Investor **FAIL** (15 `driver: enum`) and Newsday **FAIL** (19 `driver: enum`): the known issue, not recoded here.

---

## Rollback

Nothing reaches PROD from this RFC. To roll back DEV, delete the local branch (`git branch -D dev/chg-mw-002-site`) or `git reset` it to `d1029af`. If this branch is later merged on a GO, revert the merge commit on `main`. The live site keeps showing the placeholder either way, because this RFC does not deploy. No `.bkp` files.

---

## Remaining open questions for the owner

a. **Driver names (Daily Investor, Newsday):** 34 findings use `selective_framing`, `outcome_credit`, `platforming`, `source_selection`, `omission_or_emphasis`, `threat_framing`, `markets_frame`, `legal_jeopardy_frame`, `neutral_report`. Recode them onto the official eight drivers, or extend the schema and method? (They are rendered with a "pending owner decision" badge until then.)  
b. **`accountability_exempt` in the secondary-meter n:** currently counted in the lean n with contribution 0; excluding them would move News24 to about −0.26. (Primary scores already exclude them, per METHODOLOGY §8b.)  
c. **`purposive` sample frame:** accept it as a frame? (Shown as "pending owner acceptance". All four purposive News24 findings are Kyle Cowan's and are excluded under the paywall rule in this build.)  
d. **Secondary-meter minimum n:** what neutral-random sample size, if any, unlocks the hidden lean meter?  
e. **TEST preview URL:** local DEV only, or a separate preview (e.g. a private repo, or a second Pages repo on a test subdomain) before PROD?  
f. **Corrections contact:** which owner-controlled address or form the corrections page should publish (placeholder for now)?  
g. **Confirm "Daily Investigator" = Daily Investor** (dailyinvestor.com, Broad Media), already in our data. Assumed in this build.  
h. **Paywall edge cases:** (1) may a full body recovered from a public archive (Wayback) of a piece paywalled at source ever count (F-N24-FAV-ESKOM-01)? (2) may a quote taken from a free official record about a paywalled article (Press Ombud ruling, F-N24-KC-01) count? (3) confirm journalists' own X posts sharing paywalled pieces are judged on the post text only (the 8 listed above), and whether F-N24-PDT-X-09 (`headline_body_gap` without the body) should be excluded. All are treated conservatively for now: (1) and (2) excluded, (3) kept.  
i. **`control` rows in primary means:** they currently count as coded (e.g. Newsday AfriForum *n* = 5 includes F-ND-06). Keep that, or show them outside the mean?  
j. **Public evidence notes:** `evidence_notes` hold working notes (reviewer names, seed references), so they are withheld from the site. Do you want a reviewed, public "evidence note" field per finding?

---

## Seen, not touched

- **Live PROD exposure after the PR #1 merge (fixed).** The legacy Jekyll build published the repo root of `main`. On 17 Nov 2026 (about 11:05 SAST), public GETs returned HTTP 200 for `/data/lean_scores_draft.json`, `/data/news24_pilot_findings.json`, `/docs/LEFT_RIGHT_METHOD`, `/docs/CROSSCHECK_*`, `/docs/METHODOLOGY` and `/plan`, and there was no `robots.txt`. INC-MW-001 fixed this in [PR #2](https://github.com/GrokForum/mediawatch-sa/pull/2) (root `_config.yml` exclusions and `robots.txt`). Those paths now return 404, and robots `Disallow: /` and noindex are live. Deployment option A in this change ends repo-root publishing altogether.
- **Git history (branches and tags clean; old PR refs open):** on the owner's GO on 17 Nov 2026, the repo history was rewritten to remove a private individual's name, and all earlier SHAs changed. GitHub still keeps the read-only PR #1 and PR #2 head refs on old commits. These are not linked or indexed, the facts came from public sources, and no purge will be requested (accepted risk).
- Actor names vary across files ("Ramaphosa" vs "Cyril Ramaphosa", "Trump/US" vs "Trump / US government"), which splits scorecards. Normalising them is a data change.
- `people.csv` lacks four bylined News24 journalists (Jan Gerber, Emsie Ferreira, Siyamtanda Capa, Bongekile Macupe). The site falls back to the published byline with role "Journalist (byline)". Only Macupe currently has a rendered finding.
- Internal reviewer notes inside three steelman strings (F-N24-PDT-X-04, F-N24-PDT-X-07, F-N24-AB-X-12) are stripped at render time only. The data clean-up is a separate change.
- `data/pilot_findings.json` (the 4 Nov worked example, methodology 0.2, no `sample_frame`) and its seed-lead list are not used by the site.
- Pre-existing on `main`: `scripts/write_di_pilot.py`, `write_nd_pilot.py` and `write_nd_pilot_v2.py` hard-code an absolute local working path, and `docs/STATUS.md` and `plan.md` name seed files. Neither is used by the site. Cleaning them up is a separate change.
- Methodology §6.4 mentions a confidence interval for full scores; none is computed yet (no dual-coder data).

---

## Sign-off and result

Author: project bot. Sign-off by two reviewers (expert, shadow, charter and drift checks) on the exact head; owner GO to merge given 17 Nov 2026 20:01 SAST.

Private-name denylist test: `test_no_private_citizen_names` skips in CI by design, because the denylist (`tests/private_names.local.txt`) is never committed. Run it locally with the list present (`pytest tests/test_site.py`) before every push; no hook enforces this yet.

popia-review (17 Nov 2026): **PASS** for this change and its generated output. Items found and handled: the junior City Power employee is not in the output; internal reviewer-name fragments in three steelmen are stripped at render; X user ids are not rendered. The live Jekyll exposure (fixed by INC-MW-001) and the private name in git history (removed by the 17 Nov rewrite) are recorded under "Seen, not touched".

**Result:** owner GO to merge given 17 Nov 2026 20:01 SAST; the review and merge are recorded on the pull request.
