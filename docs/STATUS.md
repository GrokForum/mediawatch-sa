# MediaWatch SA — Status (5 Nov 2026, Africa/Johannesburg)

## Done

| Deliverable | Path | Notes |
|-------------|------|-------|
| Hub plan | `plan.md` | Publications + sampling, scoring summary, schema drill path, worked example |
| Methodology | `docs/METHODOLOGY.md` | −2…+2 per actor, driver weights, min *n*, confidence, steelman, POPIA |
| SQL schema | `data/schema.sql` | publication → person → article\|public_post → finding (+ score_runs) |
| JSON schema | `data/schema.json` | Same model for website/API validation |
| Publications seed | `data/publications.csv` | 21 outlets; owner/editor with source URLs + date_checked |
| People seed | `data/people.csv` | Key editors; Basson & du Toit X handles API-verified |
| Worked example | `data/pilot_findings.json` | 4 public posts, 8 findings, 8 AGOA seed leads mapped |
| Seed ingest | `seed/agoa-sa-bias-casebook-2026-11-05.md` | Already present; credited |

Directories created: `seed/`, `data/`, `docs/`.

### Worked example (brief)

News24 EiC **Adriaan Basson** (@AdriaanBasson) and Assistant Editor **Pieter du Toit** (@PieterDuToit), **4 Nov 2026**:

1. Basson 07:18:49 SAST — AfriMAGA cheerleaders / tide has turned — AGAINST AfriForum (loaded_label), AGAINST Trump/US (framing).  
2. du Toit 09:07:45 SAST — AfriMAGA bet on Trump… own the damage — AGAINST AfriForum/Solidarity (loaded_label, framing, omission). Credit: **AGOA SA casebook, Case 1**.  
3. Basson RT 10:59:57 SAST of du Toit — amplification finding.  
4. Basson 18:31:22 SAST — AfriMAGA gang / Trump's dying star — loaded_label.

### Related seeds

- **Present seed (gitignored):** `seed/agoa-sa-bias-casebook-2026-11-05.md` (AGOA SA casebook).  
- **Seed sources:** AGOA SA casebook (credited); private seed material is kept out of this repo.
- **Cassian's News24 bias meter:** later located in the gitignored seed; reference only (see the Cassian seed cross-check below). Other internal briefs were checked and not imported.

### Seed format → schema map (AGOA casebook)

| Casebook element | Maps to |
|------------------|---------|
| Case 1 post URL / time / text / metrics | `public_posts` |
| Author role + News24 | `people` + `publications` |
| Claim ladder (Proven…Not established) | `findings.fact_label` + `evidence_notes` |
| AfriMAGA / verbs / causation / omissions | `findings.driver` rows |
| Steelman du Toit / groups | `steelman_for` / `steelman_against` |
| Media bias notes #1–8 | `agoa_sa_seed_leads` in pilot JSON (`verification_status=seed_lead`) until URL re-fetched |
| Ownership paragraph | `publications.owner_group` + `owner_fact_label` |

---

## Gaps

1. **Cassian News24 bias meter** seed missing — expected in `seed/`.  
2. **Article pilot** (3–5 News24/DM May–Oct 2026 articles) **not done** — deprioritised per orchestrator; X worked example is primary.  
3. Several editors' **X handles** left blank until API-verified.  
4. Some ownership/EiC cells are **Alleged / Not established** (Maroela, Daily Investor; eNCA/Sowetan need masthead confirm).  
5. AGOA notes #1–8 need **live URL fetch + exact quotes** before scoring.  
6. SQLite DB not yet instantiated from `schema.sql`.  
7. No dual-coder process staffed yet.

---

## Next steps

1. Owner decisions on open questions in `plan.md` §6 (weights, min *n*, RT scoring, actor tagging rule, City Press, Cassian drop).  
2. Ingest Cassian bias-meter export when dropped into `seed/`.  
3. Promote AGOA leads #2–4, #6 (near/in window) to full findings.  
4. Run May–Oct 2026 stratified article sample starting with News24.  
5. `sqlite3 data/mediawatch.db < data/schema.sql` and load CSVs/JSON.  
6. POPIA pass on any public export (draft register already limited to public roles).

---

## POPIA (this draft)

**Verdict: PASS for draft-only register.**  
Named people are journalists/editors in public roles; X handles only where API-verified from public profiles; quotes are from public posts. No SA IDs, phones, private emails, home addresses, or private-citizen dossiers. Basson's first-name list is preserved only inside his published quote and is not identity-resolved by MediaWatch.


## Pilot update (2026-11-05 08:43 SAST)

- Cavus defaults locked in `docs/METHODOLOGY.md` + `plan.md` §6 (each marked *Cavus default, 5 Nov 2026 (owner may override)*).
- Schema: `target_inferred`, `target_context_quote`, RT `repost_of_post_id` (no weight on original).
- `data/pilot_findings.json` retagged under Cavus AfriMAGA/RT rules (9 findings).
- **News24 May–Oct 2026 pilot:** `data/news24_pilot_findings.json` + `.csv` — **38 findings**, 21 X posts, 10 articles (4 balanced controls), stop for report.
- Cassian meter: **not present** at `seed/cassian-news24-bias-meter.md`.
- Access: opinion columns largely paywalled; X path primary.

## Skew-fix pass (5 Nov 2026 SAST)

- `sample_frame` on all findings (`keyword`|`neutral_random`|`counter_pull`); METHODOLOGY §8a–8b.
- Neutral fortnightly politics draw + counter_pulls (SAAI, FOR AfriForum/Solidarity/Trump absences, AGAINST DA/GNU) appended to `data/news24_pilot_findings.json`/.csv.
- PDT AGAINST-ANC recheck: 2× `accountability_exempt`, 2× `borderline`, 2× keep `bias`.
- Still draft: no login/publish/post.

## Favourable-bias hunt + paywalls (5 Nov 2026, Africa/Johannesburg)

- Created `data/paywall_register.csv` (21 News24 paywalled/meta items) and `docs/PAYWALLS.md` (all 21 outlets in publications.csv).
- No logins / no publish / no post. Owner will subscribe later once priorities clear.
- Appended 8 FOR findings (Ramaphosa×4, Schreiber, DA secondary, Takealot/Naspers×2) + 3 fair-good-news controls; findings total **54** (FOR 20 / AGAINST 34).
- Method: BrandStory labeled but coded as commercial FOR Naspers ecosystem; presidential bylines coded soft FOR with strong steelman; “SA exhales” / bold-reset / AGOA meta kept as controls.

## Daily Investor + Newsday pilots (draft, 2026-11-05 SAST)
- publications.csv + people.csv + docs/PAYWALLS.md updated for both outlets.
- data/dailyinvestor_pilot_findings.json|.csv (19 findings)
- data/newsday_pilot_findings.json|.csv (23 findings)
- Window May–Oct 2026; draft only — no login/publish/push.

## Paywall recovery pass (2026-11-05 SAST)

Legitimate free recovery on `data/paywall_register.csv` (21 News24 rows): **2 full** (Wayback unlocked), **12 partial** (Wayback paywall shells / OG), **7 still_blocked**. No bypass/login/UA-spoof. Method note: `docs/FREE_ACCESS.md`. Recoded F-N24-FAV-ESKOM-01 evidence/quote from Wayback full body; JG-01/02 remain headline/lede-only (partial). Draft only; no git push.

## Cassian seed cross-check (5 Nov 2026 SAST)

Seed `seed/cassian-news24-bias-meter.md` (gitignored): **0** calls mapped to findings (no checkable examples); **3** kept in `data/external_references.json`. Lean/Ground News axes **not** imported. Kyle Cowan added to `people.csv`; 11 pieces fetched, 7 coded (5 findings + 3 balanced_controls); not a random draw (see `docs/CROSSCHECK_CASSIAN.md`). See `docs/CROSSCHECK_CASSIAN.md`. Draft only; no git push.


## Change log

| Date (Africa/Johannesburg) | RFC | Env | Result | Rollback SHA |
|----------------------------|-----|-----|--------|--------------|
| 2026-11-15 | CHG-MW-001 | DEV (`dev/chg-mw-001-catchup`; not published) | PENDING REVIEW (reviewer A, previous reviewer) and owner GO | `0d88905a569e2f997bbdf7146eb398749ae93c24` |
| 2026-11-15 | CHG-MW-002 | DEV (plan only, same branch; not published) | PENDING REVIEW (reviewer A, previous reviewer) and owner GO | `d3ca635d4ff54e25e287ef3a7249fc9102b57220` (or revert `9515e9ce65d41e74bc090d49237c196d6eb7ecdd`) |
| 2026-11-15 | CHG-MW-001 review fixes | DEV (`dev/chg-mw-001-catchup`; not published) | PENDING REVIEW (reviewer A, previous reviewer) and owner GO | `9515e9ce65d41e74bc090d49237c196d6eb7ecdd` |
| 2026-11-15 | CHG-MW-001 review fixes 2 | DEV (`dev/chg-mw-001-catchup`; not published) | PENDING REVIEW (reviewer A, previous reviewer) and owner GO | `55534683a8ef6134c3a03c4b265e44561288b610` |
| 2026-11-15 | CHG-MW-001 push log | Branch pushed at `f74158a` as draft [PR #1](https://github.com/GrokForum/mediawatch-sa/pull/1), 20:50 SAST; docs-only `1a726a0` pushed to the same branch 15 Nov 22:53 SAST; not merged | PENDING owner GO for merge | close PR #1 / delete remote branch |
| 2026-11-17 | CHG-MW-001 merge (PR #1) | `main` | PR #1 merged on the owner's GO (relayed by the orchestrator); after the second history rewrite the merge is `cbbcb9e`. Recorded here by CHG-MW-002 | tag `snapshot-2026-11-17-pre-pr1` (`0d88905`) |
| 2026-11-17 | CHG-MW-002 site build (generator scaffold, 3-outlet pilot, no-paywall rule) | DEV (`dev/chg-mw-002-site-rw2` on `main` `d1029af`) | Owner GO to merge and to switch Pages, 17 Nov 2026 20:01 SAST; indexing NO GO; tests 24 passed, 2 xfailed (DI/ND driver names); popia-review PASS | `d1029af164f1fb8a150360f877e7c58b021ed92c` (revert the merge, or reset to it) |
| 2026-11-19 | CHG-MW-003 nightly build + live check (schedule on pages.yml, artifact log, no contents: write) | DEV (`dev/chg-mw-003-nightly` on `main` `8294282`) | pushed as PR #4; under review (reviewer A, reviewer B); not merged; not deployed | `8294282db5e2e9774e89695e8b75e0e4c16a759b` |
| 2026-11-19 | CHG-MW-003 review fixes (pin PyYAML==6.0.2; persist-credentials: false on both checkouts; drop actions: write) | DEV (`dev/chg-mw-003-nightly`) | pushed as PR #4; under review (reviewer A, reviewer B); not merged; not deployed | `2c512bba9aadfb14d07fce10b741cfe9632157f0` |
| 2026-11-19 | CHG-MW-003 review fixes 2 (env: for github context in run steps; split DRAFT and noindex fixtures; STATUS: pushed as PR #4) | DEV (`dev/chg-mw-003-nightly`) | pushed as PR #4; under review (reviewer A, reviewer B); not merged; not deployed | `c9efd49a5e5f58af87b5a452bedc8a999f319ade` |
| 2026-11-19 | CHG-MW-003 review fixes 3 (per-page /method/ noindex fixture; parse robots meta with html.parser; DRAFT in visible text only) | DEV (`dev/chg-mw-003-nightly`) | pushed as PR #4; under review (reviewer A, reviewer B); not merged; not deployed | `88ffa2ef3468af54b1e08255169487fd8afcaa6e` |
| 2026-11-19 | CHG-MW-004 public data manifest (`_site/manifest.json`, footer stamp, editor source links) | DEV (`dev/chg-mw-004-manifest` on `main` `8294282`) | pushed as PR #5; under review (reviewer A, reviewer B); not merged; not deployed | `8294282db5e2e9774e89695e8b75e0e4c16a759b` |
| 2026-11-19 | CHG-MW-004 review fix (role words in RFC and STATUS changelog) | DEV (`dev/chg-mw-004-manifest`) | pushed as PR #5; under review (reviewer A, reviewer B); not merged; not deployed | `923418ccb1818c08aca2a1a9c944ad4f2019584d` |
| 2026-11-19 | CHG-MW-004 review fix 2 (STATUS: pushed as PR #5, under review, not merged, not deployed) | DEV (`dev/chg-mw-004-manifest`) | pushed as PR #5; under review (reviewer A, reviewer B); not merged; not deployed | `c5924d5ed2655d3cc9c8a3fdb176cf0067ddc740` |
| 2026-11-19 | CHG-MW-004 review fix 3 (test_noindex_everywhere also asserts the visible DRAFT banner on every page) | DEV (`dev/chg-mw-004-manifest`) | pushed as PR #5; under review (reviewer A, reviewer B); not merged; not deployed | `8a9b71e4b57febc5b274c7883bde23ced407a16d` |
| 2026-11-19 | CHG-MW-005 privacy page (footer link; owner contact address privacy@grokforum.site in) | DEV (`dev/chg-mw-005-privacy` on `main` `8294282`) | pushed as PR #6; under review (reviewer A, reviewer B); not merged; not deployed | `8294282db5e2e9774e89695e8b75e0e4c16a759b` |
| 2026-11-19 | CHG-MW-005 contact address (owner decision, relayed by reviewer A: privacy@grokforum.site) | DEV (`dev/chg-mw-005-privacy` on `main` `8294282`) | pushed as PR #6; under review (reviewer A, reviewer B); not merged; not deployed | `9da4fb339058ca46b3d39e90df95d6ff9d04d9d9` |
| 2026-11-19 | CHG-MW-005 merge of CHG-MW-004 (stamp + privacy footer; allowed_top has manifest.json and privacy) and role words in the RFC | DEV (`dev/chg-mw-005-privacy`) | pushed as PR #6; under review (reviewer A, reviewer B); not merged; not deployed | `d79d28358e1b981f9c41a7d326fb61025e2faf87` |
| 2026-11-19 | CHG-MW-005 review fix (role address wording; STATUS: pushed as PR #6, under review, not merged, not deployed) | DEV (`dev/chg-mw-005-privacy`) | pushed as PR #6; under review (reviewer A, reviewer B); not merged; not deployed | `2f224786d7ce865d50c4f2233272c450b06b2c21` |
| 2026-11-19 | CHG-MW-005 review fix 3 (site-wide allowed-email test with decoded variants; honest removal sentence on the privacy page) | DEV (`dev/chg-mw-005-privacy`) | pushed as PR #6; under review (reviewer A, reviewer B); not merged; not deployed | `97792ec0380739c43361aa09785c31ed972b968b` |
| 2026-11-19 | CHG-MW-005 merge of updated CHG-MW-004 (visible DRAFT banner asserted on every page) | DEV (`dev/chg-mw-005-privacy`) | pushed as PR #6; under review (reviewer A, reviewer B); not merged; not deployed | `259ca1d69359a6351851fbfc96be3cf2cf44f216` |
| 2026-11-19 | CHG-MW-005 review fix 3b (assemble foreign-email fixtures at runtime so the test file has no other email literal) | DEV (`dev/chg-mw-005-privacy`) | pushed as PR #6; under review (reviewer A, reviewer B); not merged; not deployed | `9f1d8e4c79255177b426251105ff52700e4163f7` |
| 2026-11-20 | CHG-MW-004 merge of CHG-MW-003 (persist-credentials: false on both checkouts; live check; PyYAML pin) | DEV (`dev/chg-mw-004-manifest`) | pushed as PR #5; under review (reviewer A, reviewer B); not merged; not deployed | `79f1ba61aac02607388b14da20685e0591054464` |
| 2026-11-20 | CHG-MW-005 merge of updated CHG-MW-004 (includes CHG-MW-003 persist-credentials and live check) | DEV (`dev/chg-mw-005-privacy`) | pushed as PR #6; under review (reviewer A, reviewer B); not merged; not deployed | `e2da734271a17403385ad54f49f6c4b6c4bf71f1` |
| 2026-11-20 | CHG-MW-005 add /privacy/ to live-check SAMPLE_PATHS (safe here because this branch deploys the page) | DEV (`dev/chg-mw-005-privacy`) | local only; not pushed. The last remote commit on this branch (PR #6) remains `e2da734271a17403385ad54f49f6c4b6c4bf71f1`. This commit and later local work are unpushed; not merged; not deployed | `d77e291106e9409e27bc3b8b36be7230540cdb4c` |
| 2026-11-20 | CHG-MW-007 official wording rule (§5b, methodology 0.5-draft) and IOL/EWN Q2 murder-figure findings | DEV (`dev/chg-mw-007-police-wording` on `main` `8294282`) | local branch; not pushed; no PR; under review; not merged; not deployed | `8294282db5e2e9774e89695e8b75e0e4c16a759b` |
| 2026-11-20 | CHG-MW-008 merge of CHG-MW-007 (official wording rule and IOL/EWN findings) onto the 005 stack | DEV (`dev/chg-mw-008-collectors` on `dev/chg-mw-005-privacy`) | local branch; not pushed; no PR; not merged; not deployed | `455f27067cdda3be680fadf74ce70ddbccb74c22` |
| 2026-11-20 | CHG-MW-008 collectors, locked neutral_random_v1 sampling, and official driver recode | DEV (`dev/chg-mw-008-collectors` on `dev/chg-mw-005-privacy` + CHG-MW-007) | local branch; not pushed; no PR; not merged; not deployed | `be75dedf46442bcdabac04f344aae861787076a6` |
| 2026-11-20 | CHG-MW-008 rebuilt as a single commit on `be75ded` (identical tree to the cleaned 008 work) | DEV (`dev/chg-mw-008-collectors`) | local branch; not pushed; no PR; not merged; not deployed | `4948167836d45e6fd2e0d5add4c7db935d44a15c` |
| 2026-11-20 | CHG-MW-003 review follow-up (fail closed on a cross-host redirect; same-host redirects still followed) | DEV (`dev/chg-mw-003-nightly`) | local only; not pushed. The last remote commit on this branch remains `3ea260fc181601eac7cb38b9e3e8f6364bb4bf17`. Local head is newer and unpushed; not merged; not deployed | `587f27b2f5c57d4c21db09dd413967c484d26e0a` |
| 2026-11-20 | CHG-MW-004 review follow-up (manifest tests use independent hashlib sha256 and require a 40-hex git SHA; STATUS: last remote/PR #5 tip is 79f1ba6, local head is ahead and unpushed) | DEV (`dev/chg-mw-004-manifest`) | local only; not pushed. The last remote commit on this branch (PR #5) remains `79f1ba61aac02607388b14da20685e0591054464`. Local head is newer and unpushed; not merged; not deployed | `0964084e03de004383ad1f3ff88e0b682536e1dd` |
| 2026-11-20 | CHG-MW-005 review follow-up (STATUS: last remote/PR #6 tip is e2da734, local head is ahead and unpushed) | DEV (`dev/chg-mw-005-privacy`) | local only; not pushed. The last remote commit on this branch (PR #6) remains `e2da734271a17403385ad54f49f6c4b6c4bf71f1`. Local head is newer and unpushed; not merged; not deployed | `34f81ae93c2fa87cbd580bbffd488366e0521683` |
| 2026-11-20 | CHG-MW-008 review follow-up (fail closed on collector errors; lock candidates behind a flag and pin sha256; freeze historical scores; retag nine pre-v1 rows as `legacy_neutral`; option (b) ignores that tag for the v1 weight; frozen-weight note in the recode CSVs; missing space fixed; denylist file required; response size capped) | DEV (`dev/chg-mw-008-collectors`) | local branch; not pushed; no PR; not merged; not deployed | `6b5d88f17bf86648e860415759cf123b0575fc59` |
| 2026-11-20 | CHG-MW-008 review follow-up 2 (injectable names path for synthetic draw tests; committed fake-name fixture; `read_capped` default limit 5_000_000; paywalled draw replaced by unused[0] of its own stratum) | DEV (`dev/chg-mw-008-collectors`) | local branch; not pushed; no PR; not merged; not deployed | this commit on `dev/chg-mw-008-collectors` (rollback `fee8916a40a02f222eed88491bb560c71e7fe190`) |
| 2026-11-20 | CHG-MW-008 review follow-up 3 (runtime lock-hash and coverage checks before any write; `read_capped` 5 MB cap wired into tests; frozen article rows; SameHostRedirectHandler refuses https-to-http and port changes; STATUS: 003 local head ahead of remote 3ea260f, not pushed) | DEV (`dev/chg-mw-008-collectors`) | local branch; not pushed; no PR; not merged; not deployed | this commit on `dev/chg-mw-008-collectors` (rollback `90c06534a0c8a2accf113c9418e5016c0d52904a`) |
| 2026-11-20 | CHG-MW-009 code the locked pilot `neutral_random_v1` draw (172 fetched and coded; 8 new findings; 164 clean; sample size on the site) | DEV (`dev/chg-mw-009-pilot-register` on `4948167`) | local branch; not pushed; no PR; not merged; not deployed | `4948167836d45e6fd2e0d5add4c7db935d44a15c` |
| 2026-11-21 | CHG-MW-008 review follow-up 4 (lock provisional badge text with a unit test) | DEV (`dev/chg-mw-008-collectors`) | local branch; not pushed; no PR; not merged; not deployed | this commit on `dev/chg-mw-008-collectors` (rollback `b0973f3610a7612d6ecd58693440ac130110ec0e`) |
| 2026-11-21 | CHG-MW-009 review follow-up (RFC actor n from site scorecards; lock first-unused-from-start wording; persist replacement attempts; isAccessibleForFree tests; check_staged_denylist fails closed if the denylist is missing) | DEV (`dev/chg-mw-009-pilot-register`) | local branch; not pushed; no PR; not merged; not deployed | this commit on `dev/chg-mw-009-pilot-register` |
