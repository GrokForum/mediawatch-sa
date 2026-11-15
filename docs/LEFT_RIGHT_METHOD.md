# Secondary meter: left/right lean (reader convenience)

**Status:** draft — 5 Nov 2026 (Africa/Johannesburg)  
**Banner (required on every display):**  
> **Secondary view: left/right lean (reader convenience). The primary measure is for/against named actors.**

**Honest caveat:** The left/right split is **contested in South Africa**. Parties and civil-society actors often reject the US/European spectrum; ethnocultural, liberation, and coalition politics cut across it. AfriForum, MK Party, and the GNU are especially hard to place. Treat every lean number as a derived convenience layer, never as the main bias claim.

This meter is **kept separate** in data (`data/lean_scores_draft.json`, schema `lean_scores`), docs, and later the site. It must **never** be mixed into primary FOR/AGAINST scores.

---

## Relationship to the primary meter

| | Primary | Secondary (this doc) |
|--|---------|----------------------|
| Question | FOR or AGAINST a **named actor**, by which **driver**? | Where do those findings sit on a published left↔right map? |
| Inputs | Quotes, URLs, drivers, fact labels | Primary findings × `data/actor_axis_map.csv` |
| Output | `signed_score` per actor (−2…+2) | `lean_economic`, `lean_social`, `lean_composite` (−2…+2) |
| Can stand alone? | Yes | No — meaningless without primary findings |

Cassian’s seed and any other outside lean labels are **reference only**. They are **not** imported as primary findings and **not** used as lean inputs (`docs/CROSSCHECK_CASSIAN.md`).

---

## Actor → axis map

File: `data/actor_axis_map.csv`

| Column | Meaning |
|--------|---------|
| `actor` | Exact actor string used in findings (aliases listed separately) |
| `economic_axis` | −2…+2: **state/redistribution** (−) ↔ **market** (+) |
| `social_axis` | −2…+2: **egalitarian / progressive-cultural** (−) ↔ **traditional / ethnocultural / conservative** (+) |
| `placement_contested` | `no` / `partial` / `yes` / `n/a` (unmapped) |
| `rationale` | Why this placement |
| `sources` | Manifestos, own platforms, or statement that the actor is unmapped |

**Rules for placements**

1. Prefer the actor’s **own published platform / manifesto**.  
2. Do **not** assert a placement without a source line.  
3. Mark contested placements (`partial` or `yes`) when reasonable readers disagree.  
4. Institutional / commercial actors with no partisan platform (e.g. City Power, IDAC, Takealot/Naspers) are **unmapped** and excluded from lean derivation.  
5. `unspecified (…)` actors are **excluded** from lean derivation.

Hard cases called out in the map: **AfriForum**, **Solidarity**, **MK Party**, **GNU**, and foreign **Trump / US government** as a proxy.

---

## Formula

Primary finding already carries:

```
signed_score ∈ [−2, +2]     # + if direction=FOR, − if direction=AGAINST
```

For each finding whose `actor` is mapped:

```
contribution_economic = signed_score × actor.economic_axis / 2
contribution_social   = signed_score × actor.social_axis   / 2
```

Interpretation (matches the owner rule):

- **FOR** an actor shifts the outlet/writer **toward** that actor’s mapped position.  
- **AGAINST** an actor shifts the outlet/writer **away** from that actor’s mapped position.  
  (Because `signed_score` is negative for AGAINST, the product flips direction on the axis.)

Roll-up for an entity (publication or person):

```
lean_economic  = clamp( mean(contribution_economic), −2, +2 )
lean_social    = clamp( mean(contribution_social),   −2, +2 )
lean_composite = clamp( mean(lean_economic, lean_social), −2, +2 )
```

**Rounding:** compute both axis means and the composite from **unrounded** values (`lean_composite` is the mean of the unrounded axis means). Round each displayed lean to **3 decimal places only at output**. Do not average already-rounded axis scores (that shifted News24 keyword from −0.396 to −0.397 and counter_pull from 0.083 to 0.084).

On this draft map, **negative ≈ left**, **positive ≈ right**. Always show the banner and caveat with the number.

### Minimum-*n* (same as primary)

Applied to the count of **included** (mapped) findings for that entity × frame:

| Flag | *n* included | Display |
|------|-------------|---------|
| `findings_only` | *n* < 5 | Show contribution rows; **lean_economic / lean_social / lean_composite are stored as null** (not a hidden number) |
| `provisional` | 5 ≤ *n* < 10 | Show lean + provisional badge + *n* |
| `full` | *n* ≥ 10 | Show lean + *n* (still secondary; still caveated) |

### Sample-frame split (same as primary)

Compute lean **pooled** and **per `sample_frame`** (`keyword` / `neutral_random` / `counter_pull` / `purposive` / `external_seed`). Keyword-heavy pools are disclosed; do not market a keyword-only lean as representative.

### Contested-placement share

```
share_contested_placements = (# included findings whose actor is contested partial|yes) / n_included
```

Report beside the lean so readers see when AfriForum/GNU-type placements dominate the mean.

---

## Optional: direct lean-label signals

Loaded labels such as **“far-right”** or **“radical left”** in a finding quote may be logged as `direct_lean_label_signals` on the lean entity.

- These are a **documented separate input**.  
- They are **not** folded silently into `lean_economic` / `lean_social` / `lean_composite`.  
- Field `direct_lean_label_signals_folded_into_score` stays `false` unless a future owner-approved rule changes that (version bump required).

---

## Worked micro-example

AfriForum mapped at `economic_axis = +1.0`, `social_axis = +1.5` (contested).

| Finding | signed_score | contrib_econ | contrib_social |
|---------|-------------:|-------------:|---------------:|
| AGAINST AfriForum, framing (−1.0) | −1.0 | −0.50 | −0.75 |
| FOR DA (+1.0), DA econ +1.5 social +0.5 | +1.0 | +0.75 | +0.25 |

Mean of those two → lean_economic = +0.125, lean_social = −0.25, composite ≈ −0.06 (near centre; *n*=2 → findings_only).

---

## What this meter is not

- Not a substitute for naming who was helped or harmed.  
- Not an import of Cassian / Ground News / AllSides labels.  
- Not a claim that SA politics is one-dimensional.  
- Not applied to unmapped institutions.

Primary method remains `docs/METHODOLOGY.md`. Schema separation: `lean_scores` (see `data/schema.json` / `data/schema.sql`).
