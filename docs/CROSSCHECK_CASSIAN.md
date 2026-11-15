# Cross-check: Cassian News24 bias meter vs MediaWatch SA pilot

**Date:** 5 Nov 2026 (Africa/Johannesburg)  
**Seed:** `seed/cassian-news24-bias-meter.md` (gitignored DM extract; Cassian via Cavus)  
**Constraint:** draft only. Cassian’s lean/Ground News labels are **not** imported into primary scores **or** into the secondary lean meter. Secondary lean (if shown) is derived only from MediaWatch primary findings × `data/actor_axis_map.csv` — see `docs/LEFT_RIGHT_METHOD.md`.

## Mapping outcome

| Bucket | Count | Notes |
|--------|------:|-------|
| Cassian calls mapped to findings (`sample_frame=external_seed`) | **0** | Seed gives no checkable quote, URL, or dated example to re-verify |
| Kept as outside references only | **3** | `data/external_references.json` REF-CASSIAN-N24-SEED-01…03 |
| Lean / Ground News axes imported into primary **or** secondary lean | **0** | Seed is reference-only; secondary lean uses our actor map, not Cassian’s scale |

## What Cassian offered

1. **Structural COI note:** Naspers IEC gifts to ANC *and* DA = character/structural conflict for a news group that claims to hold power to account; **not** asserted as a causal link to AfriForum packaging.
2. **Subjects:** Adriaan Basson, Pieter du Toit, Kyle Cowan.
3. **Axes + scale:** political lean, factuality record, target asymmetry, framing, ownership/COI, blind spots; Ground News–inspired left↔right scale + factuality High/Mixed/Low.
4. **Method sketch:** bylines corpus, Press Council, columns, investigations packages; social accusations secondary.

## Agree

- **No causal leap from Naspers gifts → AfriForum packaging.** Cassian states the non-link explicitly; our pilot likewise scores article/post drivers, not ownership-as-proof.
- **Ownership/COI is worth tracking.** We already record Media24/Naspers on `publications.csv` (`owner_group`). That is registry metadata, not a FOR/AGAINST finding.
- **Press Council / adjudicated record matters.** His “factuality record” axis matches our `factual_error` / `correction` drivers when a ruling exists. Early Cowan sample includes PCSA 000747 (City Power v News24, Sep 2026).
- **Basson and du Toit are priority News24 subjects.** Already the densest person_ids in the News24 pilot (Basson X + columns; du Toit AGOA/politics package).

## Disagree / refuse to import

- **Cassian’s Ground News–style lean scale as an input.** Not imported into primary findings and **not** used as lean inputs for the secondary meter. Owner later approved a *separate* secondary left/right view (`docs/LEFT_RIGHT_METHOD.md`) derived only from our FOR/AGAINST findings × published `actor_axis_map.csv` — that is not Cassian’s meter.
- **Treating subject lists as findings.** Naming Cowan/Basson/du Toit is a research tip, not evidence.
- **Seed file:** kept at `seed/cassian-news24-bias-meter.md` (gitignored); do not delete; reference-only.

## Coverage gap (Cassian surfaces what we had not)

| Gap | Action this pass |
|-----|------------------|
| **Kyle Cowan** absent from `people.csv` and pilot | Added (public role + `@CowansView` API-verified). **11** items fetched in a May–Oct 2026 investigations sweep; **7** coded (**5 findings**, **3 balanced_controls**). **Not a random draw** — no pre-registered neutral_random rule. KC-01 is `counter_pull` (Press Council pass); the other six coded pieces are `purposive`. Four exclusions are listed below. |
| Systematic **Press Ombud** pass on investigations | Started via City Power ruling (partial uphold: allegation presented as fact). |
| **Target asymmetry** / **blind spots** as formal axes | Not adopted as scores; can be narrative audit later from sample_frame splits. |
| Concrete Cassian **examples** (quote/URL/date) | None in seed → nothing to re-verify into `external_seed` findings. |

## Early read — Kyle Cowan (findings only; n&lt;5 mapped)

**Draw rule (honest):** 11 items were fetched; 7 were coded. There was **no** pre-registered random or fortnightly-neutral rule for this set (that rule applies only to the News24 politics skew-fix sample). Frames: F-N24-KC-01 = `counter_pull` (Press Council pass); the other six coded pieces = `purposive`.

Window sample (Wayback OG + one Ombud primary):

| Piece | Date | Frame | Coding |
|-------|------|-------|--------|
| City Power spokesperson article | 24 May 2026 | counter_pull | **AGAINST City Power** via `factual_error` (−2): Ombud found disinformation-campaign-as-fact (and two related claims) breached Press Code 1.3/3.3; apology ordered. Other complaints dismissed. |
| AfriForum “money machine” | 26 Jul 2026 (page date; date-only) | purposive | **AGAINST AfriForum** via `framing` (−1): “money machine” / “splurges” headline diction. Overlaps Basson X amplification already in pilot. |
| Orania R108m “take over” | 6 Sep 2026 (page date; date-only) | purposive | **AGAINST AfriForum** and **Solidarity** via `framing` (−1 each). |
| IDAC 700 days | 18 Jul 2026 | purposive | **AGAINST IDAC** via `framing` (−1, borderline): OG “credibility crisis” language; body locked. |
| Mashatile son-in-law payback | 2 Sep 2026 | purposive | **balanced_control** (accountability) — payback after exposé; private debtor not scored and not named here. |
| SSA / EFF declassified | 25 Oct 2026 | purposive | **balanced_control** (accountability) — document-led state-capture reporting from available text. |
| Reporting notes (Thebe) | 14 Jun 2026 | purposive | **balanced_control** (method note) — interview about prior story, no driver in OG. |

**Fetched and not coded (4):**

| Item | Why excluded |
|------|----------------|
| `mashatile_settle` (10 Oct 2026) | Later follow-up on the same deputy-president housing-fund matter already coded as BC-N24-KC-01; not an independent piece. Private debtor not named. |
| `notes_r15bn` | Reporting Notes companion to the AfriForum spend story already coded as F-N24-KC-02; method piece, not a separate findings-bearing article. |
| `zuma_spy` | Fetched in the same sweep and not coded (neither finding nor control). No contemporaneous exclusion note was kept; no reason is invented here. |
| `city_power_press_ombud_PCSA000747` | Second City Power file: the Press Council ruling, used as evidence for F-N24-KC-01, not a Cowan article and not a separate coded piece. |

**Pattern (early, paywall-limited):** Cowan’s investigations hit **both** AfriForum/Solidarity financials **and** ANC-orbit / state-institution accountability (Mashatile fund, SSA, IDAC, City Power). That undercuts any simple “one-camp attack dog” story from headlines alone. The City Power Ombud hit is a real adjudicated miss on allegation-vs-fact discipline. Mapped *n* on Cowan is under 5, so person lean is findings-only (numeric lean stored as null).

## Pilot overlap map (Basson / du Toit)

| Theme | Our pilot | Cassian seed |
|-------|-----------|--------------|
| AfriForum/Solidarity US lobbying, “AfriMAGA”, Trumpistan | Multiple PDT/JG/AB findings | Subject listed; **no example** |
| Basson X AGAINST AfriForum / FOR AgriSA / DA chirps | Keyword + counter_pull rows | Subject listed; **no example** |
| Naspers/Media24 ownership | `publications.csv` only | Structural COI reference |
| Cowan AfriForum money / Orania | **New this pass** | Subject listed; **no example** |

**Agree on substance where comparable:** heavy News24 scrutiny of AfriForum/Solidarity is real in our pilot — Cassian’s choice of subjects is directionally consistent.  
**No scored disagree on concrete calls:** he did not supply any to test.

## Problems / limits

1. Seed is a **brief/axes** extract, not a coded meter with exhibits — mapping yield = 0 findings.
2. News24 **hard paywall** → most Cowan coding from OG/Wayback shells; City Power is the exception via Ombud text.
3. Wrong X handle `@kylecowan` is an unrelated US account; correct public handle is **`@CowansView`** (API-verified 5 Nov 2026).
4. Private persons in investigations (e.g. debtors, junior staff) are not scored as actors and are referred to only by role; institutional and public-figure actors only.
5. Draft only; seed remains gitignored; **no git push**.

## Files touched

- `data/external_references.json` (new)
- `data/people.csv` (+ `kyle_cowan`)
- `data/news24_pilot_findings.json` / `.csv` (+ KC sample)
- `data/fetched_articles/news24_cowan/` (gitignored teasers + Ombud note)
- `docs/CROSSCHECK_CASSIAN.md` (this file)

## Secondary lean meter note (5 Nov 2026)

Cassian seed remains **reference only**: not imported as primary findings and **not** used as inputs to `data/lean_scores_draft.json`. Secondary lean is derived solely from MediaWatch primary findings × `data/actor_axis_map.csv` (`docs/LEFT_RIGHT_METHOD.md`). Seed file retained (gitignored).
