# MediaWatch SA — Foundation Plan (draft)

**Status:** drafts only — nothing published, posted, sent or logged into.  
**Prepared:** 5 Nov 2026 (Africa/Johannesburg, UTC+2)  
**Window:** retrospective May–Oct 2026; live from Nov 2026.

This file is the hub. Supporting artefacts:

| Path | Role |
|------|------|
| `docs/METHODOLOGY.md` | Scoring model, driver weights, roll-ups, confidence |
| `data/schema.sql` | SQL schema (publication → person → article/post → finding) |
| `data/schema.json` | Same model as JSON Schema |
| `data/publications.csv` | Seed outlet register |
| `data/people.csv` | Key editors / political writers (public roles) |
| `data/pilot_findings.json` | Worked example + mapped AGOA notes |
| `docs/STATUS.md` | Done / gaps / next steps |
| `seed/agoa-sa-bias-casebook-2026-11-05.md` | Seed from AGOA SA (Case 1 + 8 media notes) |

---

## Project rules (owner, binding)

1. **No left/right labels.** Bias is recorded as **FOR** or **AGAINST** named actors (e.g. ANC, DA, EFF, MK Party, AfriForum, Solidarity, SAAI, Trump / US government), judged case by case.
2. **Drivers per finding:** loaded labels (e.g. "AfriMAGA", "far-right"), one-sided sourcing, missing right of reply, omission, framing, headline vs body gap, factual errors and corrections.
3. **Evidence:** every finding quotes the exact line and links the source URL. Steelman both sides.
4. **Fact labels (only these five):** Proven, Established, Alleged, Disputed, Not established.
5. **POPIA:** journalists and editors are public figures; published work and public posts may be named and quoted. No doxxing, no private details. Private citizens in stories stay unnamed (generic description).
6. **Never fabricate.** Quotes, URLs, bylines and dates must come from a real fetched source; otherwise omit or mark unverified.

---

## 1. Publication list and 6-month sampling (May–Oct 2026)

### Core register (seed in `data/publications.csv`)

| Outlet | Language | Owner / group (verified level) |
|--------|----------|--------------------------------|
| News24 | EN | Media24 / Naspers — Established |
| Netwerk24 | AF | Media24 / Naspers — Established |
| Rapport | AF | Media24 / Naspers — Established |
| IOL | EN | Independent Media (Sekunjalo stake; share sizes Not established) |
| Daily Maverick | EN | Independent (memberships, ads, grants) — Established |
| TimesLIVE | EN | Arena Holdings — Established |
| Sunday Times | EN | Arena Holdings — Established |
| Mail & Guardian | EN | Independent (Karjieker / Fakude post-MDIF) — Established |
| City Press | EN | Media24 — **ceased print 10 May 2026**; archive through that date counts in window (*Cavus default*) |
| Business Day | EN | Arena Holdings — Established |
| eNCA | EN | eMedia Investments — Established |
| SABC News | EN/multi | SABC (public) — Established |
| The Citizen | EN | Caxton / CTP — Established |
| Maroela Media | AF | Independent Afrikaans digital — verify ownership further |
| Moneyweb | EN | AME — Established |
| GroundUp | EN | Independent non-profit NPC — Established |
| Sowetan | EN | Arena Holdings — Established |
| BizNews | EN | Independent (Alec Hogg) — Established |
| Daily Investor | EN | Independent digital — verify ownership further |
| Newzroom Afrika | EN | Thokozani Nkosi / Thabile Ngwato — Established |
| EWN | EN | Primedia / MIC — Established (from AGOA ownership note) |

Editors-in-chief and source URLs: see `data/publications.csv` (date_checked 2026-11-05 where fetched).

### Actors in scope (first window)

AfriForum, Solidarity, SAAI, ANC, DA, EFF, MK Party, GNU partners as named, Trump / US government, COSATU (when used as framing parallel). Expand only with owner sign-off.

### Sampling method (reproducible)

**Goal:** enough coded findings per outlet×actor to meet minimum sample sizes before a public score is shown (see METHODOLOGY: **n ≥ 10 findings** per publication×actor for a score; **n ≥ 5** for a provisional badge).

1. **Query construction (per outlet, per month May–Oct 2026):**  
   site search / outlet archive for each actor keyword set, e.g.  
   `AfriForum OR Solidarity OR "AfriSol" OR AfriMAGA` · `Trump AND (South Africa OR AGOA OR Afrikaner)` · `DA AND (GNU OR Cabinet)` · party names as exact.  
2. **Inclusion:** news, analysis, investigations, editorials and named columns under the outlet brand. Exclude pure wire reprints unless the outlet adds framing (headline, standfirst, bullets).  
3. **Stratified draw:** for each outlet×month, take up to **12** hits: prefer politics / national desk; if >12, sample every *k*-th by publish time so early/late month are covered. Cap **60 articles per outlet** for the 6-month pilot (~10/month).  
4. **Public posts:** for named editors/writers in `people.csv`, pull posts in the window that mention actors or loaded labels; code as `public_posts` (same finding schema). Press Code / social guidance applies as context, not as a finding by itself.  
5. **Double-read:** 10% of findings get a second coder; disagreement → escalate (no silent average).  
6. **Live from Nov 2026:** same rules, rolling weekly ingest; first live queue prioritises News24, Daily Maverick, IOL, Netwerk24, eNCA.

**Pilot priority (this foundation):** News24 public posts (worked example below) → News24 / Daily Maverick articles on AfriForum–Solidarity–US/Trump when time allows.

---

## 2. Scoring method and evidence format (summary)

Full detail: `docs/METHODOLOGY.md`.

### Per-finding record (atomic unit)

| Field | Content |
|-------|---------|
| `actor` | Named actor (no left/right spectrum) |
| `direction` | `FOR` \| `AGAINST` |
| `driver` | One of: `loaded_label`, `one_sided_sourcing`, `missing_right_of_reply`, `omission`, `framing`, `headline_body_gap`, `factual_error`, `correction` |
| `quote` | Exact line(s) |
| `url` | Canonical source URL |
| `published_at` | ISO datetime + zone note (report in SAST) |
| `fact_label` | Proven \| Established \| Alleged \| Disputed \| Not established |
| `steelman_for` | Fair reading favouring the outlet / writer |
| `steelman_against` | Fair reading against |
| `evidence_notes` | Context, parallel sources, what was checked |
| `weight` | Driver weight (see methodology) |
| `signed_score` | `direction` × weight → contribution on **−2…+2** scale |

**Sign convention:** `FOR` actor = positive; `AGAINST` actor = negative. A publication that systematically runs AGAINST AfriForum accumulates a negative AfriForum score — **not** a "right-wing" or "left-wing" score.

### Roll-up

`finding` → mean (weighted) at `article` / `public_post` → `person` (writer) → `publication`, always **per actor**. Show confidence from sample size and dual-coder agreement. Suppress scores below minimum *n*.

### Evidence format (required block)

```text
FINDING <id>
Actor: … | Direction: FOR|AGAINST | Driver: …
Quote: "…"
URL: …
Date (SAST): …
Fact label: …
Steelman (outlet): …
Steelman (critique): …
Credit / source of analysis: …
```

---

## 3. Data schema the website can drill into

Hierarchy:

```text
publications
  └─ people  (journalists/editors; public role; public X handle if verified)
       └─ articles  |  public_posts
            └─ findings  (actor, direction, driver, quote, url, fact_label, steelmen, …)
```

Drill path for UI: **Publication → Actor scorecard → Writer → Article/Post → Finding** (and reverse: Actor → all outlets).  
Schema files: `data/schema.sql`, `data/schema.json`.

---

## 4. Worked example — News24 editors, 4 Nov 2026 (AfriMAGA / "blue wave")

**Credit:** analysis and claim labels for du Toit's post reuse **AGOA SA casebook, Case 1** (`seed/agoa-sa-bias-casebook-2026-11-05.md`, live source `/workspace/agoa-sa/foundation.md` §§ Media bias notes / Bias casebook). X text and timestamps below were **re-verified** on 5 Nov 2026 via built-in X public reads + fxtwitter.

### Handles (verified)

| Person | Role | X | User id |
|--------|------|---|---------|
| Adriaan Basson | Editor-in-chief, News24 | [@AdriaanBasson](https://x.com/AdriaanBasson) | 189506833 |
| Pieter du Toit | Assistant Editor: Investigations, News24 | [@PieterDuToit](https://x.com/PieterDuToit) | 32115555 |

Bios on X name News24 (Proven, X API 5 Nov 2026).

### Post A — Basson, "AfriMAGA cheerleaders" (taunt tied to US results)

- **URL:** https://x.com/AdriaanBasson/status/2117849021675139317  
- **Created:** 2026-11-04 05:18:49 UTC = **07:18:49 SAST**  
- **Exact text:** "I dedicate this one to Elon, Andre, Chris, Joel, Sebastiaan, Gareth, Rob, Flip, Dirk, Jaco, Kallie, Ernst and all the other AfriMAGA cheerleaders. The tide has turned."  
- **Quotes:** NYT breaking post on Democrats capturing Senate control (id 2117842738288738621).  
- **Metrics (5 Nov 2026 fetch):** ~57.1k views, 984 likes, 237 reposts, 308 replies.  
- **Coded findings (draft):**  
  - Actor tagging under Cavus default: Post A lacks AGOA/memo/delegation context → prefer **`unspecified (AfriMAGA)`** unless paired with Case 1 context; first names kept as quoted, never resolved. Direction **AGAINST** — Driver **loaded_label** — label existence **Proven**.  
  - Actor **Trump / US government** — Direction **AGAINST** (celebrating midterm rebuke as "tide has turned") — Driver **framing** — Opinion; factual midterm outcome separate (**Established** via quoted NYT item, not re-audited here).

### Post B — du Toit, "AfriMAGA made a bet…" (Basson reposted)

- **URL:** https://x.com/PieterDuToit/status/2117876437977841977  
- **Created:** 2026-11-04 07:07:45 UTC = **09:07:45 SAST** (matches Case 1).  
- **Exact text:** "AfriMAGA made a bet on Trump, prostrated themselves in front of him, and agitated for their separatist plans in the WH. They thought it wise to expose this country to the vagaries and impulses of an unstable president. And they must own the damage Trump did to SA."  
- **Quotes:** Edward Luce (FT) https://x.com/EdwardGLuce/status/2117849544079905202 (05:20:53 UTC / 07:20:53 SAST).  
- **Basson RT:** https://x.com/AdriaanBasson/status/2117904674011701623 — created **08:59:57 UTC = 10:59:57 SAST** (Case 1 said ~10:59 SAST — confirmed).  
- **Claim labels:** per **AGOA SA Case 1** (Established / Not established / Disputed ladder) — not re-litigated here.  
- **Bias drivers (Case 1, mapped):** loaded_label ("AfriMAGA"); framing (prostrated / agitated / separatist); omission (memo asked SA stay in AGOA; USTR reasons name neither group); causation dispute on "own the damage".  
- **Steelmen:** as in Case 1 (du Toit vs groups) — copied into `pilot_findings.json`.

### Post C — Basson follow-up, "AfriMAGA gang" / "Trump's dying star"

- **URL:** https://x.com/AdriaanBasson/status/2118018275506532498  
- **Created:** 2026-11-04 16:31:22 UTC = **18:31:22 SAST**  
- **Exact text:** "We saw what happened. / Gareth didn't. / Gareth is not a serious person. / He does not know the first thing about journalism. He and his fellow band of unserious pod bros will wither with the rest of the AfriMAGA gang who hitched their wagons to Trump's dying star. / Supernova."  
- **Driver:** loaded_label + framing; personal attack on a named public commentator (record as framing/loaded_label against the actor cluster, not as a private-citizen finding).

### What this example tests

- Public-post path in the schema (not only articles).  
- Editor amplification (original + RT) under the same publication.  
- Loaded pejorative without left/right spectrum.  
- Reuse of external casebook with clear credit and no fabrication.

Machine-readable coding: `data/pilot_findings.json`.

---

## 5. Mapping AGOA SA's 8 media-bias notes → schema

From seed casebook / foundation §§ Media bias notes (credit **AGOA SA**). These are **seed leads**, not fully coded findings until each URL is re-fetched and quoted:

| # | Outlet / source | Likely actor(s) | Likely direction | Likely driver(s) | Window note |
|---|-----------------|-----------------|------------------|------------------|-------------|
| 1 | AFP via RTL (Oct 2026) | AfriForum/Afrikaners discourse | AGAINST (editorialised "false allegations") | framing | In window |
| 2 | IOL COSATU (3 Nov 2026) | AfriForum/Solidarity | AGAINST (one side only in extract) | one_sided_sourcing, missing_right_of_reply | Just after window; live |
| 3 | IOL "Ramaphosa and Lamola blamed" (3 Nov) | SA gov / Solidarity voices | FOR Solidarity (mirror of #2) | one_sided_sourcing | Live |
| 4 | EWN Lamola/citizenship (8 Oct 2026) | DA vs claim | mixed / lean balanced | headline_body_gap ("misinformation" unattributed) | In window |
| 5 | Daily Maverick (11 Mar 2025) | AfriForum et al. / treason framing | AGAINST (stronger than quote) | framing, headline_body_gap | **Before** May–Oct window — archive only |
| 6 | The Citizen (3 Nov 2026) | Bozell / SA gov reply thin | mild AGAINST SA gov reply balance | omission | Live |
| 7 | News24 "Separate development…" (26 Feb 2025) | AfriForum memo | AGAINST (apartheid-loaded frame) | loaded_label / framing, headline_body_gap | Before window — archive |
| 8 | Die Gewete / Politicsweb / The Common Sense | n/a | n/a | exclude (opinion camps, not news) | Out of news sample |

Ownership line from same seed (Established except IOL share sizes): IOL / EWN / DM / Citizen / News24 — already reflected in `publications.csv`.

---

## 6. Locked defaults and remaining owner questions

### Cavus defaults (applied 5 Nov 2026; owner may override)

1. **Scale:** −2…+2 per actor, with current driver weights. — *Cavus default, 5 Nov 2026 (owner may override)*
2. **Sample sizes:** ≥10 findings → score; 5–9 → provisional; under 5 → findings only, no score. — *Cavus default, 5 Nov 2026 (owner may override)*
3. **Reposts:** own amplification finding against the reposter, linked to the original; **adds no weight to the original**. — *Cavus default, 5 Nov 2026 (owner may override)*
4. **AfriMAGA:** tag AfriForum/Solidarity only when context shows who is meant (AGOA, Washington memo, named delegation); set `target_inferred=true` and quote the context line; else actor = `unspecified (AfriMAGA)`. — *Cavus default, 5 Nov 2026 (owner may override)*
5. **City Press:** keep archive to **10 May 2026**, flagged ceased print; counts in window. — *Cavus default, 5 Nov 2026 (owner may override)*
6. **First names:** keep exactly as quoted; never match to real people. — *Cavus default, 5 Nov 2026 (owner may override)*

### Still open

1. Cassian's News24 bias meter seed: expected at `seed/cassian-news24-bias-meter.md` — not present as of this update; cross-check when dropped.
2. Whether publication roll-up should mean findings or mean of article-means (METHODOLOGY still defaults to mean of findings).

---

## 7. Immediate next steps

1. Owner sign-off on open questions above.  
2. Drop Cassian bias-meter export into `seed/` and map columns → schema.  
3. Re-fetch URLs for AGOA notes #1–4, #6 (in/near window) and promote from leads to full findings.  
4. Begin May–Oct 2026 News24 article sample on AfriForum / Solidarity / US–SA.  
5. Stand up SQLite from `schema.sql` and load CSVs + pilot JSON.
