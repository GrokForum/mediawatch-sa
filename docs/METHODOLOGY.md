# MediaWatch SA — Methodology (draft)

**Version:** 0.3-draft (Cavus defaults + sample_frame + accountability rule)  
**Date:** 5 Nov 2026 (Africa/Johannesburg)  
**Hub:** `/workspace/mediawatch-sa/plan.md`  
**Constraint:** transparent, reproducible, no left/right spectrum labels.

---


## Cavus defaults (5 Nov 2026)

Marked **Cavus default, 5 Nov 2026 (owner may override)** wherever they lock a choice:

1. **Scale:** −2…+2 per actor, with the driver weights in §3. — *Cavus default, 5 Nov 2026 (owner may override)*
2. **Sample sizes:** *n* ≥ 10 findings for a publication×actor score; 5–9 = provisional; under 5 = findings only, no score. — *Cavus default, 5 Nov 2026 (owner may override)*
3. **Reposts:** a repost is its **own amplification finding** against the person who reposted, linked to the original via `repost_of_post_id`. It **adds no weight to the original**. — *Cavus default, 5 Nov 2026 (owner may override)*
4. **AfriMAGA tagging:** tag AfriForum/Solidarity cluster only when context shows who is meant (e.g. AGOA, Washington memo, named delegation). Set `target_inferred=true` and quote the context line. If context does not show it, actor = `unspecified (AfriMAGA)`. — *Cavus default, 5 Nov 2026 (owner may override)*
5. **City Press:** keep archive through **10 May 2026**, status `ceased print`; counts in the May–Oct window for dates ≤ 10 May. — *Cavus default, 5 Nov 2026 (owner may override)*
6. **First names:** keep first names **exactly as quoted**; never match them to real people. — *Cavus default, 5 Nov 2026 (owner may override)*


## 1. What we measure

Bias is **not** a political compass score. Each finding answers:

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
| `counter_pull` | Deliberate search for the **opposite** direction of the provisional pattern | e.g. FOR AfriForum/Solidarity/SAAI; AGAINST DA/GNU; FOR Trump/US; matching writer X on the same weeks |

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

## 10. Versioning

Breaking changes to weights or labels bump `methodology_version` and freeze prior scores as `score_run` snapshots. Never silently rewrite historical public scores.
