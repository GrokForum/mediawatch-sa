# RFC-CHG-MW-002 — Plan only: drill-down site on GitHub Pages

**Status:** PENDING REVIEW (Cavus, Cassian) and owner GO  
**Environment:** PLAN ONLY — no build, no Pages publish, no change to `index.html` in this RFC  
**Branch:** `dev/chg-mw-001-catchup` (same Cavus-specified branch as CHG-MW-001; used instead of `rfc/<ver>`)  
**Pre-change SHA (origin/main after sync, also the rollback base until CHG-MW-001 is merged):** `0d88905a569e2f997bbdf7146eb398749ae93c24`  
**Date:** 15 Nov 2026 (Africa/Johannesburg)  
**Repo:** https://github.com/GrokForum/mediawatch-sa (PUBLIC). Intended production URL: https://mediawatch.grokforum.site

This RFC is a plan. Accepting it does **not** authorise a build or a push. A later RFC will name the exact files of the first build.

---

## Environment plan

| Env | What it is | Points at production? |
|-----|------------|------------------------|
| DEV | This branch, built and viewed locally (or a later named preview). | No. Does not change Pages, DNS, or `main`. |
| TEST | Not stood up. GitHub Pages on this repo has no automatic PR preview. If the owner wants a TEST URL, that is an open question below. | — |
| PROD | GitHub Pages, legacy build from the root of `main`, custom domain `mediawatch.grokforum.site`. | Yes — only after an owner GO on a named later RFC that actually builds and merges. |

DEV never points at the production host, database, mailbox or DNS. This plan does not modify GitHub settings.

---

## Goal

Describe a static drill-down site for MediaWatch SA:

**publication → writer/editor → article or public post → evidence**

(exact quote, source link, driver, fact label, steelman for and against).

The two meters stay visually and data-separate. The primary FOR/AGAINST named-actor meter is the main claim. The secondary left/right lean is hidden until the neutral sample is large enough, and even then carries its banner and SA-contested caveat.

---

## Information architecture

1. **Home** — short what-this-is; publication list with primary FOR/AGAINST counts by actor; *n* and sample-frame disclosure; lean numbers **off** by default.
2. **Publication** — owner/editor metadata (already in `publications.csv`); writer list; actor scorecards; findings grouped by `sample_frame` (`keyword` / `neutral_random` / `counter_pull`); charts as below.
3. **Writer / editor** — public role only; person-level primary scores; list of coded articles and posts.
4. **Article or public post** — headline/date/byline; canonical URL; access note if paywalled; all findings on that item.
5. **Evidence row** — exact quote, source link, driver, fact label (one of the five), signed score, steelman for, steelman against, `target_inferred` / context quote when used.
6. **Method and corrections** — links to `docs/METHODOLOGY.md` and `docs/LEFT_RIGHT_METHOD.md` (rendered or linked); a **Corrections / right-of-reply** page; a short **paywall / access** note.

### Thresholds (same as methodology)

| Flag | *n* | Display |
|------|-----|---------|
| findings-only | *n* < 5 | Show findings; suppress the numeric score |
| provisional | 5 ≤ *n* < 10 | Show the score with a provisional badge and *n* |
| full | *n* ≥ 10 | Show the score and *n* |

Apply per entity × actor (primary) and per entity × frame (both meters). Always show the sample-frame split; do not market a keyword-only score as representative.

### Two meters, visually separate

- Primary scorecards and charts never share a number, colour scale, or heading with the lean meter.
- Lean, when eventually shown, uses the required banner: *Secondary view: left/right lean (reader convenience). The primary measure is for/against named actors.* Plus the SA-contested caveat.
- **Hide the lean meter** (no number, no chart, no nav entry) until the owner agrees the **neutral_random** sample is large enough. Draft figures exist in `data/lean_scores_draft.json` for review only. A config flag (e.g. `show_lean_meter: false`) ships with the first build.

### Charts (primary always; lean only if unlocked)

- Stacked or grouped FOR vs AGAINST counts (and mean signed score) by named actor, with *n*.
- Small multiples or a toggle by `sample_frame`.
- No chart when the flag is findings-only.

---

## Data flow (proposed approach)

No backend, no runtime database, no accounts.

**Proposal:** a plain Python static generator (`scripts/build_site.py` in a later RFC) that reads `data/*.json`, `data/*.csv`, and the methodology docs, and writes static HTML+CSS+a little JS into the Pages root (or a `site/` folder copied to the root). Charts via a small client-side library or inline SVG generated at build time.

Why a generator rather than a browser app that `fetch`es the raw JSON:

- Draft and internal fields can be dropped at build time (e.g. coder notes that are not for display).
- The public site does not have to expose every working file under `/data/`.
- Pages stays a static artefact; `main` after GO contains only what the owner agreed to publish.

Alternative, if the owner prefers zero build step: a single `index.html` plus vanilla JS that reads a committed, review-trimmed `data/public/` JSON bundle. Either way, there is no server code.

Fetched article bodies and the Cassian seed are never copied into the site output (`seed/` and `data/fetched_articles/` stay gitignored).

---

## Replacing the placeholder and noindex

Current `index.html` is a "coming soon" page with `<meta name="robots" content="noindex">`. That is already on `main`.

1. The first build RFC replaces `index.html` with the real home page and adds the drill-down pages.
2. **Keep `noindex`** (and, if added, a `robots.txt` Disallow) on every page until the owner gives a **named GO to index**. The GO to merge a build is not automatically a GO to index.
3. After that GO, a tiny follow-up change removes noindex / opens `robots.txt`. Rollback is a revert of that change.

---

## Paywall note

Every article page that was coded from a headline, OG teaser, or partial archive must show an access note (from `access_limit` / `paywall_register.csv`): what was recovered, the recovery route (e.g. Wayback), and that the canonical citation remains the outlet URL. Link a short public summary of `docs/PAYWALLS.md` and `docs/FREE_ACCESS.md`. Do not imply full-body coding where the body was locked. No bypass language.

---

## Corrections / right-of-reply page

A standing page that:

- Explains how a publication, journalist, or named actor can request a correction or file a right of reply on a finding.
- States that evidence is quoted and linked, and that fact labels are only the five allowed terms.
- Collects the request through a published contact path the owner names (an owner-controlled mailbox or a later form). The bot must not invent a public inbox or auto-publish replies.
- Ties accepted corrections to the `correction` / `factual_error` drivers and a new score_run, never a silent rewrite of historical public scores (METHODOLOGY §10).

---

## POPIA safeguards (for the later build)

- Public journalists, editors and public figures in their public role only.
- Private story subjects stay unnamed; do not surface names that appear only inside a paywalled body or a gitignored fetch.
- Keep first names exactly as quoted; never identity-resolve them.
- No SA IDs, phones, private emails, home addresses, or account numbers.
- No linking of a pseudonymous account to a real person beyond already API-verified public professional handles.
- Do not ship `seed/`, `data/fetched_articles/`, or raw working JSON that still holds fields we would not put on a public page.
- Run the popia-review skill on the generated output before any GO to merge.

**Plan-only verdict:** not a release. The later build RFC must record its own PASS or BLOCK.

---

## Tests / acceptance (for the later build RFC)

1. Every displayed finding shows quote, URL, driver, fact label, and both steelmans.
2. Fact labels on the site are only the five allowed terms.
3. Numeric primary scores obey the *n* thresholds; lean is hidden while the flag is off.
4. Sample-frame splits are visible and not mixed into a single unexplained number.
5. Primary and secondary meters are visually and data-separate.
6. `noindex` present until the index GO.
7. Site output contains no paths from `seed/` or `data/fetched_articles/`, and no `/workspace/agoa-sa` paths.
8. POPIA scan of the generated HTML is PASS.
9. Placeholder is gone only on the pages the build RFC names; rollback restores the pre-change SHA or reverts the merge.

---

## Rollback

Until a later build is merged, there is nothing to roll back in PROD: this commit is plan text on a DEV branch.

After a future build merge: revert that later RFC's commit(s) on `main` (GitHub Pages will republish the previous root, including the "coming soon" placeholder if that is what `main` then contains). Record the pre-build SHA in that later RFC. Do not use `.bkp` files.

---

## Open questions for the owner

There are **six** open questions:

1. Is a Python static generator acceptable, or do you want a no-build HTML+JS bundle?
2. Should the first public build include Daily Investor and Newsday as well as News24, or News24 only until the unofficial driver labels on DI/Newsday are recoded?
3. What size of **neutral_random** sample is enough to show the lean meter (a number, or "not on the first public version")?
4. Do you want a TEST preview URL (and if so, where), or is local DEV + merge-to-`main` enough?
5. Which contact path should the corrections / right-of-reply page publish?
6. Confirm that a GO to merge the first build is **not** a GO to remove `noindex`, unless you say so in the same GO.

---

## What this RFC does not do

No site code, no replacement of `index.html`, no Pages or DNS change, no push, no PR, no commit to `main`. `seed/` and `data/fetched_articles/` stay uncommitted.

---

**Status remains: PENDING REVIEW (Cavus, Cassian) and owner GO.**
