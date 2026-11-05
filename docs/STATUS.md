# MediaWatch SA — Status (5 Nov 2026, Africa/Johannesburg)

## Done

| Deliverable | Path | Notes |
|-------------|------|-------|
| Hub plan | `/workspace/mediawatch-sa/plan.md` | Publications + sampling, scoring summary, schema drill path, worked example |
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

### Workspace search (related files)

- **Present seed:** `mediawatch-sa/seed/agoa-sa-bias-casebook-2026-11-05.md` (AGOA SA casebook).  
- **Seed sources:** AGOA SA casebook (credited); private seed material is kept out of this repo.
- **Cassian refs elsewhere (not bias-meter data):** `/workspace/ktb/cassian-brief-2026-11-02.md`, `/workspace/cavus/cassian-asks.md` — not imported.  
- **Cassian's News24 bias meter:** **not found** under `seed/` or obvious `/workspace` paths this pass.

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
