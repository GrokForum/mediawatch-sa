# MediaWatch SA — Methodology (draft)

**Version:** 0.5-draft (adds official wording vs media wording; otherwise 0.4-draft)  
**Date:** 20 Nov 2026 (Africa/Johannesburg); 0.4-draft dated 5 Nov 2026  
**Hub:** `plan.md`  
**Constraint:** transparent, reproducible. **Primary** meter stays FOR/AGAINST named actors (no spectrum). A **secondary** left/right lean exists as reader convenience only — see `docs/LEFT_RIGHT_METHOD.md`; never mixed into primary scores.

---


## Cavus defaults (5 Nov 2026)

Marked **Cavus default, 5 Nov 2026 (owner may override)** wherever they lock a choice:

1. **Scale:** −2…+2 per actor, with the driver weights in §3. — *Cavus default, 5 Nov 2026 (owner may override)*
2. **Sample sizes:** *n* ≥ 10 findings for a publication×actor score; 5–9 = provisional; under 5 = findings only, no score. — *Cavus default, 5 Nov 2026 (owner may override)*
3. **Reposts:** a repost is its **own amplification finding** against the person who reposted, linked to the original via `repost_of_post_id`. It **adds no weight to the original**. — *Cavus default, 5 Nov 2026 (owner may override)*
4. **AfriMAGA tagging:** tag AfriForum/Solidarity cluster only when context shows who is meant (e.g. AGOA, Washington memo, named delegation). Set `target_inferred=true` and quote the context line. If context does not show it, actor = `unspecified (AfriMAGA)`. — *Cavus default, 5 Nov 2026 (owner may override)*
5. **City Press:** keep archive through **10 May 2026**, status `ceased print`; counts in the May–Oct window for dates ≤ 10 May. — *Cavus default, 5 Nov 2026 (owner may override)*
6. **First names:** keep first names **exactly as quoted**; never match them to real people. — *Cavus default, 5 Nov 2026 (owner may override)*



## 0. Two meters (kept separate)

MediaWatch SA maintains **two** measures; the secondary lean is hidden until the owner’s GO. They stay separate in data, docs, and (later) the site.

### PRIMARY — FOR / AGAINST named actors *(unchanged)*

Each finding answers: relative to a **named actor**, does this line work **FOR** or **AGAINST** that actor, and by which **driver**? Signed scores (−2…+2), min-*n* rules, and `sample_frame` splits in §§3–8 apply here. **This is the main bias claim.**

### SECONDARY — left/right lean *(reader convenience)*

Banner required on every display:

> **Secondary view: left/right lean (reader convenience). The primary measure is for/against named actors.**

Caveat: the left/right split is **contested in South Africa**. AfriForum, MK Party and the GNU are especially hard to place.

- Method: `docs/LEFT_RIGHT_METHOD.md`
- Actor map: `data/actor_axis_map.csv` (economic −2…+2 state/redistribution↔market; social −2…+2; rationale + sources; contested marked)
- Formula: `contribution = signed_score × actor_axis / 2`; lean = clamp(mean(contributions), −2, +2); same min-*n* and `sample_frame` splits as primary
- Storage: own schema / file (`lean_scores`, `data/lean_scores_draft.json`) — **never** mixed into primary `scores`
- Optional direct lean-label signals (`far-right`, `radical left`, …) logged separately; not folded into the derived lean unless an owner-approved rule says so
- Cassian seed and other external lean scales: **reference only** — not findings, not lean inputs (`docs/CROSSCHECK_CASSIAN.md`)


## 1. What we measure

**Primary** bias is **not** a political compass score (a secondary lean view exists separately — §0). Each **primary** finding answers:

> Relative to a **named actor**, does this published line (or public post by a named newsroom figure) work **FOR** or **AGAINST** that actor, and by which **driver**?

Actors are organisations, parties, governments or clearly public institutional figures (e.g. ANC, DA, EFF, MK Party, AfriForum, Solidarity, SAAI, Trump / US government). Private individuals who appear in stories are described generically and are not scored as actors unless they are public figures acting in a public role.

---

## 2. Fact labels (closed set)

Only these five labels may be applied to **factual claims** inside a finding's evidence notes or claim breakdown:

| Label | Meaning |
|-------|---------|
| **Proven** | Direct primary evidence checked (official text, unedited primary clip, API-verified post, court record, etc.) |
| **Established** | Strong secondary corroboration; reasonable people would treat as settled for practical purposes |
| **Alleged** | Asserted by a source; not independently confirmed |
| **Disputed** | Credible conflicting accounts or interpretations remain |
| **Not established** | Insufficient evidence; includes pure opinion when scored as if it were fact |

Bias analysis and steelmen are **unlabelled by design** (they are argument, not claims). Never invent a sixth label.

---

## 3. Drivers and weights

Each finding has exactly one primary `driver` (secondary drivers may be noted in `evidence_notes` but do not double-count unless a second finding row is justified).

| Driver | Code | Weight (0–2) | Rationale |
|--------|------|--------------|-----------|
| Loaded label | `loaded_label` | **1.5** | Pejorative or apartheid-/partisan-fused coinage not used as self-description (e.g. "AfriMAGA", "far-right" when contested) |
| One-sided sourcing | `one_sided_sourcing` | **1.5** | Only one camp quoted on a contested dispute |
| Missing right of reply | `missing_right_of_reply` | **1.5** | Adverse claim about an actor with no approach / no published response when reply was reasonably available |
| Omission | `omission` | **1.0** | Material contrary fact in the public record left out |
| Framing | `framing` | **1.0** | Word choice / narrative that steers judgment beyond the facts shown |
| Headline vs body gap | `headline_body_gap` | **1.5** | Headline or standfirst stronger or different than body evidence |
| Factual error | `factual_error` | **2.0** | Demonstrable false statement of fact |
| Correction | `correction` | **−1.0** *(reduces prior error)* | Published correction; links to the original finding |

Weights are a **draft for owner confirmation**.

---

## 4. Per-finding signed score (−2…+2)

```
raw = weight                          # absolute magnitude from driver table
signed = +raw  if direction == FOR
signed = −raw  if direction == AGAINST
signed_score = clamp(signed, −2, +2)
```

Examples:

- AGAINST AfriForum via `loaded_label` (1.5) → **−1.5** on AfriForum axis.  
- FOR DA via fair multi-source piece is **not** a finding unless a driver fires; neutrality produces **no row**.  
- `factual_error` AGAINST an actor → **−2.0**; a later `correction` finding on the same article contributes **+1.0** toward that actor (partial clawback), and both rows remain for audit.

Findings are the atomic unit. Do not invent article-level scores without findings.

---

## 5. Evidence requirements (hard gates)

A finding is incomplete and must not enter roll-ups unless all are true:

1. **Exact quote** (unicode-faithful; ellipses marked `[…]` only for mid-cut).  
2. **Canonical URL** (article permalink or `https://x.com/{user}/status/{id}`).  
3. **Datetime** with UTC source and SAST conversion stated.  
4. **Byline / account** of public figure.  
5. **Steelman for** and **steelman against** (one short paragraph each).  
6. **Fact label** on any discrete factual claim relied upon.  
7. Source was **fetched** this project (or credited seed with re-verify date).

If any gate fails → omit or mark `verification_status = unverified` and exclude from scores.

---

## 5a. Free public content only (owner rule, 17 Nov 2026)

Bias is judged **only on what the public can read free**. Paywalled articles are **out of the sample** and **never scored**. A headline, standfirst, OG description or other teaser **never stands in for the body** of a paywalled piece. No subscriptions, logins, user-agent spoofing, paywall-script stripping or bypass services, ever.

How it is applied:

1. A finding is **excluded** (not shown on the site, not counted in any score or *n*) when it rests on a piece that is paywalled at source: the finding has an `access_limit`, its article's `access` is not a free-access value, its `access_note` records a paywall, or its URL is in `data/paywall_register.csv`.
2. Excluded findings are listed in `data/paywall_exclusions.csv` (finding id, reason, access basis, date). Evidence rows stay in the findings files for audit; nothing is deleted.
3. A body recovered later from an archive (for example Wayback) of a piece that is paywalled at source is **excluded too**, pending an owner decision (RFC-CHG-MW-002 open question h).
4. A journalist's own **public post** (for example on X) is free content and is judged on the post text only, even when it links to a paywalled article. It never borrows the paywalled body or teaser as evidence.
5. Free registration walls (Daily Investor "free after register") are not paywalls, but this project still codes without registering.
6. Outlets with little free content show **findings only** if they cannot reach minimum *n*.

The site generator (`scripts/build_site.py`) applies the same rule and the test suite checks it.

---

## 5b. Official wording vs media wording

This rule is shared with the project's other registers so they all treat official wording the same way.

When SAPS, the NPA or a charge sheet names an offence, that wording records **what was charged**, not **what happened**. The existence of the charge is **Proven** as a charge. It does not, by itself, prove or disprove the underlying acts.

Each claim about an injury or an act is labelled on its own evidence:

- **Alleged** if it rests only on a family member, a lobby group, or another untested assertion;
- **Established** if hospital records, court testimony, or similarly strong evidence backs it;
- **Proven** only from a direct primary record of the act itself.

A gap in either direction — downplaying a charge or an injury, or inflating one — is a **framing** or **omission** finding once there is an exact quote and a contrary record.

The same rule applies to official statistics and media reports of them. If an outlet misreports an official figure, that is a **factual_error**. The official table figure, checked in the primary statistical release, is **Proven**. A ministerial speech or briefing note is also a primary record of what was said, but it does not override the statistical tables when the two conflict.

Example, logged in this version: IOL and EWN reported that South Africa recorded “more than 1,600 fewer murders” year on year in the second quarter of 2026/27. The official SAPS tables in that release show 5,590 murders in July–September 2026 against 5,794 in July–September 2025, a drop of 204 (−3.5%). The 1,600 year-on-year claim is **Not established** (contradicted by the Proven SAPS tables). (The same incorrect year-on-year wording also appears in the Acting Minister’s official speech; the speech does not replace the tables.)

---

## 6. Roll-up rules

### 6.1 Article / public_post score (per actor)

```
article_actor_score = mean(signed_score of findings on that article for that actor)
```

Optional display: also show count of findings and dominant drivers.

### 6.2 Person (writer/editor) score (per actor)

```
person_actor_score = mean(article_actor_score ∪ post_actor_score)
```

Weight articles and public posts equally in v0.1 (owner may later weight articles higher).  
A **repost** is a separate `public_posts` row linked via `repost_of_post_id`. It is coded as its **own amplification finding** against the **reposter** (same drivers/actors as warranted by the amplified text). It **adds no weight to the original** author's score. — *Cavus default, 5 Nov 2026 (owner may override)*

### 6.3 Publication score (per actor)

```
publication_actor_score = mean(all finding signed_scores for that publication×actor)
```

Alternative (owner decision): mean of article-level means (prevents one mega-thread dominating). **v0.1 default = mean of findings** (simpler, every quote counts once).

### 6.4 Minimum sample sizes

| Display | Minimum findings (publication × actor) | Rule |
|---------|------------------------------------------|------|
| Findings only (no score) | *n* < 5 | Show rows; suppress numeric score |
| Provisional | 5 ≤ *n* < 10 | Show provisional score + *n* |
| Full score (−2…+2 + CI) | *n* ≥ 10 | Public score |

*Cavus default, 5 Nov 2026 (owner may override)*

Person-level scores: same thresholds on that person's findings for the actor.

### 6.5 Confidence

```
confidence = f(n, agreement)
```

Draft:

- **Low:** *n* < 10 or dual-coder agreement < 70%  
- **Medium:** *n* ≥ 10 and agreement ≥ 70%  
- **High:** *n* ≥ 25 and agreement ≥ 85%

Dual-coder: 10% sample; Cohen's κ on {actor, direction, driver} triple; disagreements escalate, not averaged.

---

## 7. Steelman protocol

For every finding:

- **Steelman for (outlet/writer):** strongest fair reading under which the line is responsible journalism or protected opinion.  
- **Steelman against:** strongest fair reading under which the line misleads, loads the dice, or omits material context.

Steelmen must not introduce unverified facts. They may point to Proven/Established context from the same case file.

---

## 8. POPIA / naming

- Journalists, editors, and other **public figures** may be named for published work and public posts.  
- Record **public role** and **verified public X handle** only.  
- No private emails beyond those published on outlet about-pages as newsroom contacts when needed for register provenance; prefer omitting personal mail from exports.  
- Private citizens in stories: generic description only.  
- Quoting a journalist's public post that itself names people does not require MediaWatch to dox or expand those identities.

---

## 9. Reproducibility checklist

- [ ] Actor list version pinned  
- [ ] Driver weight table version pinned  
- [ ] Query strings and sample seed recorded per outlet×month  
- [ ] Fetch date and tool (WebFetch / X API / fxtwitter) recorded  
- [ ] Quote hash or exact string stored  
- [ ] Coder id + review id stored  
- [ ] Seed credits (e.g. "AGOA SA casebook, Case 1") stored in `evidence_notes`

---


## 8a. Sample frames (skew control)

Every finding **must** carry a `sample_frame` field so roll-ups can weight or split by how the item entered the corpus. — *added 5 Nov 2026*

| Value | Meaning | How drawn |
|-------|---------|-----------|
| `keyword` | Hit via actor/term search (AfriForum, Solidarity, SAAI, Trump, AGOA, AfriMAGA, etc.) | Search → fetch → code |
| `neutral_random` | Date-based politics draw, **not** keyed on the scored actor | Fixed weekdays from `/politics`, archive, or sitemap; ~2 stories/week across the window |
| `counter_pull` | Deliberate search for the **opposite** direction of the provisional pattern | e.g. FOR AfriForum/Solidarity/SAAI; AGAINST DA/GNU; FOR Trump/US; matching writer X on the same weeks; or a Press Council / Ombud pass that is not a random draw |
| `external_seed` | Re-verified from an outside seed that supplies a checkable quote, URL and date | Only after re-verify; otherwise keep as an external reference |
| `purposive` | Judgement / byline corpus with **no** pre-registered random rule | e.g. a named-journalist investigations sample to fill a coverage gap. Do **not** label this `neutral_random`. |

**Rules:**

1. Tag every finding, including balanced controls' linked articles when a finding is coded; controls themselves record `sample_frame` on the article/control row.
2. Keyword-only pilots are **skewed**; do not publish person×actor scores from keyword alone.
3. Absences discovered by `counter_pull` (zero hits) are recorded in `meta.counter_pull_absences` — absence is data, not a fabricated FOR/AGAINST row.
4. Roll-up options (owner chooses at score run): (a) report three parallel scores by frame; (b) weight `neutral_random` highest; (c) pool all frames but disclose mix.

Neutral-sample procedure used in the News24 May–Oct 2026 skew-fix pass: select politics stories near fixed mid-week dates (~fortnightly Tue/Fri proxies across May–Oct), prefer the lead politics item that day; code FOR/AGAINST drivers **or** log as `balanced_controls` when no driver fires.


## 8b. Accountability vs bias (governing-party rule)

Routine **accountability reporting** on a governing party or governing coalition partner is **not** coded as bias when **all** of the following hold:

1. **Sourced:** the adverse claim rests on a named primary or strong secondary source (official record, court filing, IEC statement, audited figure, on-record quote). Fact label is Proven or Established (or Alleged only when the piece clearly marks allegation and attributes it).
2. **Right of reply:** the actor was approached, or a published response / prior public denial is fairly reflected; or reply was reasonably unavailable and that is noted.
3. **No loaded driver:** the piece does not depend on `loaded_label`, one-sided sourcing of a contested dispute, headline–body gap, or framing that goes materially beyond the sourced facts.
4. **Proportionate:** the tone matches the gravity of the sourced facts (correction of a false party claim, disclosure failure, court finding, etc.).

If those gates pass → mark the row `accountability_status = accountability_exempt`, keep the quote for audit, and **exclude** it from person/publication signed-score means.

If a driver still fires (e.g. "circus" editorialising on top of a fair IEC rebuttal, or teaser that states Alleged politicisation as settled fact) → keep as bias finding with `accountability_status = bias` or `borderline`, and explain in `evidence_notes`.

**Applies especially to ANC / GNU coverage.** Opposition parties get the same rule when they hold executive office (e.g. DA ministers in the GNU): sourced accountability ≠ automatic AGAINST finding.

Re-audit trigger: any existing AGAINST finding on a governing actor must be re-checked against this rule when `sample_frame` work runs.

---

## 8c. `accountability_status`, including `control`

`accountability_status` on a finding is one of:

| Value | Meaning |
|-------|---------|
| `bias` | Coded as a bias finding that enters signed-score means (subject to min-*n*). |
| `borderline` | A bias finding kept, but flagged as close to the accountability or proportion gate; explain in `evidence_notes`. |
| `accountability_exempt` | Sourced accountability that meets all §8b gates; quote kept; `signed_score` may be null; excluded from signed-score means. |
| `accountability` | Accountability reporting logged as such (e.g. on a balanced_control row). |
| `neutral_method` | Method/process note with no FOR/AGAINST driver. |
| `control` | A finding retained as a **balance or contrast** observation in the sample (for example, an outlet also platforming criticism that cuts against a provisional pattern, or a straight news note kept as a soft/neutral control). It still has a quote, URL and fact label. It is not the same as `accountability_exempt`. |

---

## 10. Versioning


Breaking changes to weights, labels, or the secondary axis map bump `methodology_version` (and `left_right_method` version when only the secondary changes) and freeze prior scores as `score_run` / `lean_score_run` snapshots. Never silently rewrite historical public scores. Never rewrite primary scores to absorb lean.

0.5-draft (20 Nov 2026) adds §5b (official wording vs media wording) and is shared with the project's other registers. Prior findings keep the methodology_version they were coded under. Historical public scores are not rewritten.
