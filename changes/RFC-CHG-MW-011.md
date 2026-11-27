# RFC-CHG-MW-011 — Add Politicsweb as a tracked opinion outlet (DEV)

**Status:** Draft, under review. Branch `dev/chg-mw-011-politicsweb`; it is pushed and opened as a draft PR only on an owner GO naming the head. Not merged; not deployed. No indexing request (`robots.txt` `Disallow: /` and noindex stay).
**Environment:** DEV — branch created from `origin/main` at `1dcd5b7fcac0cd76d19f80d6b6ecead464cc5014`, then forward-merged `origin/main` at `14f60a7c1ee925811ae9106398df6cf45c5b4f2a` (27 Nov 2026, Africa/Johannesburg).
**Pre-change SHA (rollback base):** `14f60a7c1ee925811ae9106398df6cf45c5b4f2a` (current `main` after the forward-merge).
**Date:** 22 Nov 2026 (Africa/Johannesburg)
**Repo:** https://github.com/GrokForum/mediawatch-sa (PUBLIC). This RFC does not change GitHub Pages settings, DNS, or indexing.

---

## Goal

Record the owner's decision that Politicsweb (https://www.politicsweb.co.za) is included as a tracked outlet, reversing `plan.md` row 8's exclusion of "Die Gewete / Politicsweb / The Common Sense" as "opinion camps, not news". Opinion outlets are valid for bias measurement. Daily Investor is already covered (active pilot in `data/publications.csv`; collector with `https://dailyinvestor.com/feed/` on CHG-MW-008, now on `main` `14f60a7c`) — no change for it. This RFC is feasibility and labelling only: no collector, no `publications.csv` row, no site change.

## Owner decisions

1. Label Politicsweb clearly as **OPINION** on its public page and in `publications.csv` through a new `outlet_type` field (proposed below; not added in this change).
2. `docs/METHODOLOGY.md` applies unchanged.
3. Named-actor scores will later be cross-referenced with the project's politician-profile register, so political-opinion bias sits in context. This is a future link, not built now.
4. The purpose is a spread of outlets, so that one house's coverage of a given actor can be compared against its peers, using only the five fact labels (Proven, Established, Alleged, Disputed, Not established) and neutral wording.

## Proposed `outlet_type` field

Add a column `outlet_type` to `data/publications.csv` in a later, reviewed change. Suggested values:

| Value | Meaning |
|-------|---------|
| `news` | Predominantly original news reporting |
| `opinion` | Predominantly commentary, columns and analysis |
| `mixed` | A substantial, ongoing mix of original reporting and opinion under one masthead |

Politicsweb would be `opinion`. The public publication page would show that label (OPINION). The field is reader context; it does not change scoring rules.

## Collector feasibility (fetched 22 Nov 2026, Africa/Johannesburg; TLS verification on)

**robots.txt** (`https://www.politicsweb.co.za/robots.txt`, HTTP 200 at 07:34 SAST): the file is a content-signal preamble only (1,248 bytes, 24 lines). It defines `search`, `ai-input` and `ai-train`, and says that if a signal is omitted the operator neither grants nor restricts that use. It sets no `content-signal` yes/no values, and has no `User-agent`, `Allow`, `Disallow` or `Sitemap` lines. Quoted close:

> (c) If the website operator does not include a content signal for a corresponding use, the website operator neither grants nor restricts permission via content signal with respect to the corresponding use.

**RSS:** `https://www.politicsweb.co.za/rss.xml` is a working RSS 2.0 feed (HTTP 200, 50 headline items; also linked from the site footer as "RSS Feed"). Its atom self href is `https://rss.politicsweb.co.za/politicsweb/rss/politicsweb/en/politicsweb_daily_news.xml`; that host failed TLS verification (`UNEXPECTED_EOF_WHILE_READING`). Verification was not disabled. The collector must use `https://www.politicsweb.co.za/rss.xml` (the www host) with TLS verification on, not the atom self href. Common paths `/feed`, `/rss`, `/sitemap.xml` and `/rss-news/sitemap` returned 404.

**Paywall:** Not a hard wall on all content. Unauthenticated fetches of non-member articles returned full article text (e.g. https://www.politicsweb.co.za/news/south-africa-approaches-its-mugabe-moment). A paid membership exists (About: financed by advertising and paid members). Site config advertises `freeReads` of 3 per 7 days and "member-only articles". At least one column is members-only: https://www.politicsweb.co.za/news/out-of-the-slough-of-despond is labelled Members Only, JSON-LD `isAccessibleForFree: false`, and the unauthenticated body was a short teaser only. Owner rule stands: paywalled, member-only, or meter-locked items, and teasers, are never scored; no login and no bypass.

**Content mix** (nav: OPINION, DOCUMENTS, POLITICS; policy on https://www.politicsweb.co.za/about): the About page says opinion pieces are always clearly categorized as opinion, and that political statements, press releases and primary documents are published as an unaltered, attributed archival record, kept separate from the outlet's commentary and analysis. On this fetch that split was visible: own editor and columnist analysis with full free text; a The Common Sense (TCS) item whose body ended "Continue reading." (a teaser of another masthead); an ANC statement ending "Issued by the African National Congress" (https://www.politicsweb.co.za/news/anc-rejects-market-pressure-on-coalition-negotiations); and a Presidency-issued speech (https://www.politicsweb.co.za/news/ai-cyril-ramaphosa-message-to-silicon-valley).

**Publisher** (public pages only): Legal Notice (https://www.politicsweb.co.za/legal-notice) — Politicsweb FC UG, registered in Bremen (HRB 40345 HB); James Myburgh, Managing Director. **Proven.** About page — James Myburgh is editor, publisher and curator; founded 2007; partnership with Moneyweb ended 2010; financed today by advertising and paid members. **Established** (outlet's own account).

## How to handle the mix (later coding)

- Score Politicsweb's own editorial, columns, analysis and any original reporting as the outlet, under METHODOLOGY.md unchanged.
- Record republished party statements, official speeches and primary documents as the issuer's own words, not as Politicsweb bias.
- Attribute republished commentary from another masthead (for example TCS bylines) to that source, not as Politicsweb's own voice; any selection or amplification stays under the existing repost rule, which covers `public_posts`; the article-level rule for republished items comes in the coding change. Do not code from a teaser.
- Member-only, meter-locked and paywalled items stay out of the sample.

## What this change contains / what stays

This branch adds only `changes/RFC-CHG-MW-011.md`. No collector, no `publications.csv` edit, no `plan.md` or `docs/STATUS.md` edit, no merge to main, no deploy, no indexing request. Die Gewete and The Common Sense stay outside the tracked-outlet list unless the owner later says otherwise (TCS appears here only as a source Politicsweb sometimes reprints).

## Success

This RFC records the inclusion decision, the OPINION label and `outlet_type` proposal, that METHODOLOGY.md applies unchanged, the future politician-profile register link, the comparison purpose, and the 22 Nov 2026 feasibility evidence.

## Tests

This RFC is documentation only and adds no executable tests. The later implementation RFC (collector and `outlet_type`) must cover at least:

- robots.txt and TLS: the collector uses `https://www.politicsweb.co.za/rss.xml` with TLS verification on, and does not use the atom self-href host that failed verification.
- Meter exclusion: paywalled, member-only, or meter-locked items, and teasers, are never scored; no login and no bypass.
- Attribution: Politicsweb's own editorial, columns, analysis and original reporting are scored as the outlet; republished party statements and official speeches are attributed to the issuer; republished commentary from another masthead is attributed to that source, not as Politicsweb's own voice.
- Exact quotes only: any finding quotes exact words from a fetch done in that change.
- Fetched article bodies are gitignored and are not committed.
- No full-text reproduction: the repo and the public site must not reproduce Politicsweb article full text.

## Rollback

Delete the branch `dev/chg-mw-011-politicsweb`. Base remains `14f60a7c1ee925811ae9106398df6cf45c5b4f2a`. Forward-only: no rebase, amend, or force. Never on `main`.

## Sign-off

Sign-off is by someone other than the author (Reviewer A, critic reviewer). Owner GO naming the head is required before merge or deploy. Implementation (collector and `outlet_type` field) comes in a later, separately reviewed change.
