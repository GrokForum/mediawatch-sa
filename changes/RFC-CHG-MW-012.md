# RFC-CHG-MW-012 — Ombud and press-council findings per publication, last five years (DEV)

**Status:** Draft RFC, for owner decisions and review. Branch `dev/chg-mw-012-ombud-findings`; it is pushed and opened as a draft PR only on an owner GO naming the head. Not merged; not deployed. No indexing request (`robots.txt` `Disallow: /` and noindex stay).
**Environment:** DEV. Branch created from `origin/main` at `ddb7e4debb2e5285c4d7fb8fd6263adbddd785f2` (28 Nov 2026, Africa/Johannesburg).
**Pre-change SHA (rollback base):** `ddb7e4debb2e5285c4d7fb8fd6263adbddd785f2`.
**Date:** 28 Nov 2026 (Africa/Johannesburg)
**Repo:** https://github.com/GrokForum/mediawatch-sa (PUBLIC). This RFC does not change GitHub Pages settings, DNS, or indexing.
**Scope:** RFC only. It adds this file and one `docs/STATUS.md` row. No code, no data, no schema, no site change.

---

## Goal

Record the owner's request, in the owner's words:

> "rfc: add ombudsman findings per publication, last 5 years. Too many errors being apologised for, when the harm of the original piece, is done."

and propose a way to publish each tracked publication's ombud and press-council record for the last five years, showing both the finding and how long the original piece stood before any apology or correction. This RFC states what is feasible from free public sources (fetched 28 Nov 2026), proposes a design that fits `docs/METHODOLOGY.md`, and lists the decisions only the owner can make. Decision 3 was made on 28 Nov 2026 and is recorded below; the other six stay open. Nothing is built until the owner decides and a later, separately reviewed change implements it.

## Feasibility research (fetched 28 Nov 2026, about 11:44–11:58 SAST; TLS verification on; no login; free public pages only)

### Press Council of South Africa (print and online), https://presscouncilsa.org.za

- **Domain.** `presscouncil.org.za` redirects (301) to `presscouncilsa.org.za`; the redirect target verifies.
- **robots.txt** (https://presscouncilsa.org.za/robots.txt, HTTP 200): `User-agent: *`, empty `Disallow:`, and a sitemap line. Nothing is disallowed. **Proven.**
- **Terms of use** (https://presscouncilsa.org.za/terms-of-use/, updated 27 Sep 2024): rulings "are published on our website"; English text is authoritative over translations. No reuse restriction on rulings is stated. Our rule stays: short exact quotes and a link, never a full-text copy.
- **Rulings lists:** https://presscouncilsa.org.za/category/rulings/ (all), `/category/rulings/ombud-rulings/`, `/category/rulings/leave-to-appeal/`, `/category/rulings/appeals-panel/`, `/category/rulings/ombuds-hearings/`, plus one category per year back to 2008. The site is WordPress and also exposes its public JSON listing (`/wp-json/wp/v2/posts?categories=13`), advertised in the page head and not disallowed. The listing is by post date and category. It has **no filter by publication**; the publication appears only in the title ("complainant v publication") and in the ruling header.
- **Stages and appeal.** Complaints go to a Public Advocate, who may decline or settle; unresolved ones go to the Press Ombud or a Deputy Press Ombud (some matters are heard by an Adjudication Panel). Either side may apply for leave to appeal within seven working days to the Chair of Appeals; if granted, an Appeals Panel decides. Source: Complaints Procedures, updated May 2023 (https://presscouncilsa.org.za/wp-content/uploads/2024/10/PCSA-COMPLAINTS-PROCEDURES-June-2023-1.pdf). A complaint is due within 20 working days of publication unless the Public Advocate accepts it late. A ruling's directions are published "at the earliest opportunity after the time for an application for leave to appeal has lapsed", so some delay between ruling and apology is built into the process.
- **Sanctions scale** (same Procedures, s.7–8): caution or reprimand; a correction, retraction or explanation, with an apology where appropriate, and/or the findings, published as directed (it may not later be removed); publication of the complainant's reply; supplementary directions. Three tiers: Tier 1 minor breaches (apology on an inside page); Tier 2 serious breaches (apology with prominence set by the Ombud, front or home page possible, apology text approved by the Ombud); Tier 3 serious misconduct (adds a "space sanction"). The Council's non-binding guidance note (https://presscouncilsa.org.za/2021/01/25/publication-of-apologies-and-corrections/) sets the placement test for prominence: for a serious reputational error, the same page (or front page, page 2 or 3) in print; appended where it is always visible, plus the landing page if the original was there, and on social accounts that carried the original, online. There is **no fine**.
- **What a ruling page shows.** Checked on https://presscouncilsa.org.za/2026/11/27/gauteng-dept-of-infrastructure-development-vs-timeslive-and-sowetan/: ruling date; the Ombud's office; complaint number; author (byline); date of publication; publications; headlines and URLs; the Press Code clauses complained of; a numbered finding per complaint ("upheld" or "dismissed"); the directed sanction (apology wording, placement, right of reply, approval before publication); and the appeals instruction. On the 153 ombud-level rulings in the window, a text check found a "Press Code" mention in 152, "Clause" in 136, an "Author" line in 125, and "Date of publication" in 78 (older rulings carry it inside a "SUMMARY" paragraph). So the fields exist, but the layout changed over time and extraction will need per-layout rules.
- **Apology date and placement are not on the Council's site.** The ruling gives the direction, not the date the outlet complied. They have to be found on the outlet's own site. A worked check: a Daily Maverick ruling of 7 Mar 2024 on an article of 3 Oct 2023 (the outlet had itself added a correction note on 4 Oct 2023). The outlet's apology page appeared on 3 May 2024. That is 156 days article to ruling, 57 days ruling to apology, 213 days article to apology. The apology could be found by search, so this is feasible per ruling but manual. The 27 Nov 2026 ruling above (article 17 Aug 2026, ruling 26 Nov 2026, 101 days) had no apology yet, because its appeal window is open.
- **Volume and counts.** Rulings posts dated 1 Nov 2021 to 30 Nov 2026 (REST total 232): 153 ombud-level, 58 leave-to-appeal decisions, 15 appeals-panel decisions, 5 ombuds' hearings, 1 other. By post year: 2021 (Nov–Dec) 6, 2022 35, 2023 29, 2024 34, 2025 37, 2026 (to 27 Nov) 91. Why 2026 is higher is **Not established**. Ombud-level rulings by respondent named in the title (rough: some titles name two outlets and the title is not the finding): News24 37, Daily Maverick 19, Sunday Times 16, City Press 15, Sunday World 13, TimesLive 11, Media24 Afrikaans titles 9, Mail & Guardian 8, The Citizen 7, amaBhungane 4, IOL and other Independent titles 3, Daily Sun 2, EWN 2, GroundUp 2, Sowetan 1, Business Day or Financial Mail 1, Moneyweb 1; 13 name other outlets.
- **Upheld rate per outlet is Not established.** The outcome sits in prose and in per-complaint lines (one 2026 ruling has eight complaints: two upheld, six dismissed). A keyword count over all 153 rulings gave unusable results, because most rulings contain both "upheld" and "dismissed". Each ruling has to be read and coded, so the first load is a coding job.
- **Denominator.** The Council's own dashboard for January to June 2026 (https://presscouncilsa.org.za/wp-content/uploads/2026/07/Press-Council-Complaints-Management-Dashboard-Jan-June-2026.png44.pdf, an image PDF read by eye) shows 129 complaints received, 21 resolved, 60 declined, 14 withdrawn or deferred, 34 pending, and 24 referred for adjudication. Complaints received per year run at roughly 230 to 380 for 2021–2025 (chart read, approximate). So published rulings are a **minority** of complaints. Settlements at the Public Advocate stage leave no public per-outlet record: **Not established** per outlet.
- **Who is covered.** Membership is voluntary. Independent Media (Independent Newspapers, Africa Community Media, IOL) was expelled on 23 Oct 2024 (https://presscouncilsa.org.za/2024/10/23/press-council-expels-independent-media-group/) after refusing to comply with a finding; its complaints are now lodged with its own ombud. The members page (https://presscouncilsa.org.za/subscriber-members/) is a lettered list; a text search of it did not show every outlet that has rulings, so per-outlet membership is **Not established** from that page. A missing ruling record therefore never means a clean record.

### Broadcast: BCCSA, https://www.bccsa.co.za

- **Domain and TLS.** `bccsa.org.za` and `www.bccsa.org.za` failed the TLS handshake (unexpected EOF). Verification was not disabled and those hosts were not used. `https://www.bccsa.co.za/` (found through the search index) verifies.
- **robots.txt** (https://www.bccsa.co.za/robots.txt, HTTP 200): disallows `/wp-admin/` only. **Proven.**
- **Sanctions** (https://www.bccsa.co.za/sanctions/): dismiss; reprimand; direct a correction and/or a summary of findings to be broadcast; direct a broadcast of the complainant's concise response; fine up to R100,000; record criticism of a complainant; ancillary directions.
- **Listing.** WordPress, with one category per broadcaster (for example e.tv, SABC radio and TV, MultiChoice, 702, 947) and a public JSON listing. A "Judgments" page says uploads are still in progress, so the archive may be incomplete. Rulings are titled "Adjudication No: nn/A/year" or "Case number: nn/year", with complainant, broadcaster, programme, broadcast date and time, the code clauses and the finding in the text.
- **Counts.** Posts dated 1 Nov 2021 to 30 Nov 2026 (REST total 207): 2021 (Nov–Dec) 2, 2022 46, 2023 27, 2024 51, 2025 38, 2026 (to 23 Nov) 43. Title matches (rough; dismissals and upheld together): eNCA 23, SABC titles 42, MultiChoice/DStv titles 55, Newzroom Afrika 6. Upheld per broadcaster is **Not established**, as above.
- **Appeal.** Appeals exist (for example a 2026 appeal that succeeded against eNCA on the comment clause: https://www.bccsa.co.za/2026/11/23/case-number-03-2026-afriforum-vs-enca-comment/). Appeal posts are listed alongside first-instance rulings, so appeal outcomes need linking by case.
- **Coverage.** The BCCSA signatories page lists television and radio broadcasters. Whether Newzroom Afrika is bound is **Not established** from the fetched list, although rulings name it.

### In-house ombuds

- **News24** has a named public editor who also serves City Press and the group's English brands, and the group says it operates under the Press Council's rules (https://www.news24.com/citypress/news/your-voice-matters-meet-our-new-ombud-and-public-editor-20250912-0687, from a search excerpt). No public register of the public editor's findings was found: **Not established**. Formal complaints go to the Press Council, so those rulings are already in scope above.
- **Daily Maverick** has no named ombud; it publishes a corrections policy (https://www.dailymaverick.co.za/article/2026-02-17-daily-mavericks-approach-to-corrections-press-council-and-press-ombud-rulings/) with a 48-hour target for straightforward factual disputes and notes on each corrected article. That makes its own corrections visible per article, but there is no findings register.
- **Independent Media** has its own Group Ombud and says rulings are published on its website (https://iol.co.za/iol-complaints-procedure/, s.7.2). robots.txt at https://www.independentmediaombud.co.za/robots.txt returned 200 with no blanket disallow; the homepage returned 503 "Maintenance Mode" at fetch time. Counts: **Not established**.
- **Everyone else** (Mail & Guardian, TimesLive, The Citizen, EWN, SABC News and others): no in-house findings register was checked this turn. **Not established**.

### What the research means for the request

| Question | Answer |
|----------|--------|
| Can rulings be listed per publication for 1 Nov 2021 – 30 Nov 2026? | **Yes for the Press Council and the BCCSA**: dated, public, no disallow, title shows the respondent. Independent Media's ombud: not yet. |
| Are date, publication, article, clauses and outcome present? | Mostly. Article date and clauses are in most rulings; outcome is prose per complaint, so each ruling is hand-coded. |
| Can the apology date and placement be measured? | Per ruling, by finding the outlet's own page. Feasible, manual, and not on the ruling site. Print placement is often not checkable from free pages (stays Not established). |
| Is the ruling count a fair comparison between outlets? | **No, not on its own**: volume, complaint rate and membership differ, and settlements are invisible. See the steelman section. |

## Proposed design

### 1. New record type: `ombud_ruling` (separate from `findings`)

One row per ruling decision (first-instance and each appeal stage are separate rows, linked by case). Fields:

| Field | Meaning |
|-------|---------|
| `ruling_id` | Body plus its own case number (Press Council complaint number; BCCSA adjudication or case number) |
| `body` | `press_council`, `bccsa`, `independent_media_ombud`, or `in_house` |
| `stage` | `ombud`, `adjudication_panel`, `leave_to_appeal`, `appeals_panel`, `bccsa_adjudicator`, `bccsa_tribunal`, `bccsa_appeal` |
| `ruling_date`, `ruling_url`, `fetched_on` | Date as printed on the ruling; the fetch date |
| `publication_id` | Links to `data/publications.csv`; a ruling naming two outlets gets one row per outlet, with a shared `ruling_id` |
| `article_url`, `article_headline`, `article_published`, `article_access` | Headline quoted exactly. `article_access` follows §5a: if the article is paywalled, the ruling record may still exist, but no article text is read or quoted beyond what the ruling itself quotes |
| `byline` | Only where the ruling names the author, as a public role. Stored for provenance, not rolled up (see open decision 6) |
| `complainant_type`, `complainant_label` | `organisation`, `public_body`, `public_figure_in_role`, or `private_person`. Named only for the first three; a private person is stored as "a private complainant" |
| `code_version`, `clauses` | The Press Code in force (a new Code took effect on 30 Sep 2022, so clause numbers differ before it) or the BCCSA code, and the clauses complained of |
| `sub_findings` | One entry per complaint: clause, upheld or dismissed |
| `finding` | `upheld`, `partly_upheld`, `dismissed` (ruling level); `appeal_status`; `final_finding` after appeal. A ruling inside its appeal window is `appeal_window_open` and is not counted as final |
| `sanctions` | Closed list: `reprimand`, `correction`, `retraction`, `explanation`, `apology`, `right_of_reply`, `findings_published`, `takedown`, `fine`, `space_sanction`, `other`, plus the directed placement as quoted |
| `own_correction_date` | If the outlet corrected on its own before the ruling (the ruling usually says so) |
| `remedy_date`, `remedy_url`, `remedy_placement`, `remedy_checked_on` | When and where the apology or correction ran, found on the outlet's site. `not_found` is a valid value, with the date checked |
| `lag_to_ruling_days`, `lag_ruling_to_remedy_days`, `lag_to_remedy_days` | Computed from the three dates: article to ruling, ruling to remedy, article to remedy. Kept as separate segments so a process delay (the complaint window and the appeal window) is not blamed on the outlet |
| `prominence_parity` | `comparable`, `lesser`, or `not_established`, with the test named (the Council's placement guidance, items 9–10) |
| `quote`, `steelman_outlet`, `steelman_complainant` | One short exact quote from the ruling; one short paragraph each, as in §7 |
| `label` | `Proven` (see below) |

Fetched ruling text is stored under the existing gitignored fetched-articles area and never committed; the repo holds the structured row and a short quote only.

### 2. Per-publication display

On each publication page, a block headed **Press-council and ombud record (accountability, not bias)**, last five years by ruling date:

- Rulings decided, and upheld, partly upheld and dismissed, per year, using the final finding after appeal.
- Sanction mix (share of upheld rulings that carried an apology, correction, retraction, right of reply, takedown or fine).
- Median lag in three segments (article to ruling; ruling to remedy; article to remedy) and how many remedies were not found.
- "Corrected on its own initiative before the ruling": count, shown as visible credit.
- Share of upheld rulings where remedy prominence was comparable to the original (with a separate count of "not established").
- A **jurisdiction line**: member, expelled (with date), not a signatory, or Not established. Absence of rulings is never shown as a clean record.
- The sample rule follows §6.4: under five rulings shows the rulings only, with no medians or shares; five to nine is provisional; ten or more is a full block.

### 3. Relationship to the bias meter

- **Decided by the owner, 28 Nov 2026 (decision 3):** the ruling record is a **separate dataset** that never feeds the bias scores, roll-ups or findings. It is kept in its own file and display, as the secondary lean is. It produces no signed score, no driver weight and no contribution to any publication×actor mean.
- The two datasets are not merged and do not cross-reference. A ruling is not evidence for a bias finding, a bias finding does not cite a ruling, and neither dataset carries a field or link that points into the other. Every bias finding stands on its own fetched free evidence under §5, whatever any ombud has ruled on the same article.
- The existing `factual_error` and `correction` drivers are unchanged by this RFC. A published remedy does not trigger the `correction` driver's +1.0 clawback.
- Neutral and dismissed results are kept: a dismissed complaint is shown as dismissed, never as a mark against the outlet.

### 4. Fact labels

- A ruling row is **Proven as the ruling was made**: the body's published ruling was fetched and checked, so it is a primary record of what the body found and directed. This is the same idea as §5b (official wording records what was charged, not what happened).
- It does **not** by itself prove the underlying facts of the article. Any claim about those facts carries its own label under §2.
- A **dismissed** complaint records that the body found no breach; it is **not** a finding against the outlet and carries no negative inference.
- A ruling overturned or varied on appeal: both rows stay for audit; the display uses the final finding.
- Lag figures are arithmetic on dated public pages and carry the label of their weakest date. A remedy that was not found is **Not established**, not "none".
- Harm: reach and damage of the original piece are **Not established** (no free reach data). The display shows exposure time, not measured harm.

### 5. POPIA

- Complainants who are private persons stay unnamed, in the record, the page and this repo. Public bodies, organisations, public figures in their public role, journalists and publications may be named, as in §8.
- The Council's complaints are lodged against publications, not individual journalists or editors (https://presscouncilsa.org.za/complaints/). The byline is therefore stored for provenance only; no per-journalist ruling tally is proposed.
- Ruling pages carry contact details and sometimes private detail; none is stored or pasted. Only the contact address `privacy@grokforum.site` appears in this project.
- Defamation guard: every statement uses the body's own words ("the Press Ombud found…") with the link, the date, the appeal status and the final outcome, and is updated or removed if the body later varies it. Outlets can ask for a correction through the contact address.

### 6. Steelman, both sides

- **For outlets.** Prompt self-correction deserves visible credit, hence the "own initiative before the ruling" count and the separate lag segments. A raw ruling count penalises outlets that join the system and engage with the ombud, and outlets outside the system never appear. Large outlets draw more complaints, and many complaints come from parties in a dispute with the outlet; a complaint count is not an error rate. Many rulings are dismissed, and an outlet that wins deserves that shown. Part of the lag is process, not the outlet.
- **For the complainant and the reader.** An apology that runs weeks or months after the article, on an inside page or under the headline's reach, leaves the original impression standing, which is the owner's point. Settlements at the Public Advocate stage leave no public record, so the published rulings undercount errors that were quietly fixed. A non-member's record is invisible. A prompt correction can still be too small for the harm.
- **Normalisation.** Per-outlet complaints received are not published (the dashboard is aggregate): **Not established**. MediaWatch holds no census of each outlet's article output (the pilot register is a locked sample), so rulings per thousand articles is **Not established** and is not shown. What can be shown fairly is the upheld share of rulings decided, the share corrected on the outlet's own initiative, and the jurisdiction line. If the owner wants a volume base, a published, free output figure per outlet would be needed first.

## Decisions for the owner (decision 3 decided 28 Nov 2026; the other six open)

1. **Sources in scope.** Proposed first: Press Council (all four ruling types) and the BCCSA (including its appeals). Later: Independent Media's ombud (once its site is reachable), and any in-house register that proves to be public. Which outlets not yet in `publications.csv` appear in the rulings (for example Sunday World, Daily Sun, amaBhungane, Sunday Independent) and whether to add them; and whether Cape Town News (named by a sister register) should be added.
2. **Window.** Proposed: rulings dated 1 Nov 2021 to 30 Nov 2026 on first load, then a rolling five years, refreshed monthly. Alternatives: window by article date; a longer span.
3. **Do rulings feed scores? DECIDED by the owner, 28 Nov 2026.** No. In the owner's words: "Rulings are 3rd party and often subjective, despite requirement to be objective. Your suggestion is approved, a separate record of ruling sheds light on those, while your bias meter sheds light on bias. 2 different datasets, not to be merged." Rulings are a separate dataset that never feeds bias scores, roll-ups or findings, and the rulings are not used as evidence for a bias finding. Options (C) (an upheld ruling opens a candidate finding) and (D) (a remedy counts as a `correction` clawback), and the evidence route under (B), are rejected. Steelman: the ruling bodies are valuable as a public record of what was found and directed, but they are third parties whose rulings can be subjective, so MediaWatch keeps them visible without letting them stand in for its own evidence. Keeping the datasets apart also protects the outlet from a ruling counting twice, and protects the ruling record from MediaWatch's own coding. The cost is that a reader must compare the two views themselves.
4. **Accuracy-only errors.** A sister register offered three identity errors in one outlet's explainer (a judge's first name and a gendered pronoun) as candidate findings; they are unscored accuracy slips with no for/against direction. Should a separate, unscored `accuracy_note` type join this accountability record, or stay out? This RFC does not add it.
5. **Scope of "per publication".** Publication-level only (proposed), or also per outlet group (for example Media24, Arena, Independent Media)?
6. **Bylines.** Store only (proposed), or also show a per-journalist list? Complaints are lodged against publications, so the default is no per-journalist roll-up.
7. **Prominence parity.** Use the Council's placement guidance as the test (proposed), and show print placement as "not established" unless a free, public copy exists.

## What this change contains / what stays

This branch adds `changes/RFC-CHG-MW-012.md` and one row in `docs/STATUS.md`. It changes no code, data, schema, workflow, site page, `robots.txt`, `CNAME` or GitHub setting, and no collector runs. `docs/METHODOLOGY.md` is unchanged here; a later change would add a section describing the ruling record as a separate dataset. No score, weight or roll-up changes, so no prior score is frozen or rewritten. The two meters and their files are untouched.

## Later work (each a separate RFC, reviewed, with an owner GO)

1. **Schema and data (CHG-MW-012a).** `data/ombud_rulings.csv`, validation in `scripts/validate_schema.py`, `outlet_type`-style jurisdiction field on `publications.csv`, a methodology section.
2. **Collector (CHG-MW-012b).** Reads the Press Council and BCCSA listings, one request at a time with a pause, an identifying user agent, robots.txt checked first, TLS verification on, and errors written to `data/collector_errors.csv`. It stores structure, not full ruling text.
3. **Site block (CHG-MW-012c).** The per-publication display above, behind the same noindex and draft marker.

Tests those changes must cover at least:

- robots.txt and TLS: respect the disallow lines; never disable TLS verification; the BCCSA collector uses `bccsa.co.za`, not the hosts that failed.
- Fail closed on a host that does not verify, or a 503.
- A ruling inside its appeal window is not counted as final.
- A dismissed ruling is shown as dismissed and adds no negative mark.
- A private complainant is never stored by name (test with a synthetic name built at run time).
- The accountability record never changes a bias score, and the frozen historical scores stay byte-identical.
- The two datasets stay unmerged: no `ombud_ruling` field names an actor, score or finding id; no findings file references a `ruling_id`; the site build never joins them into a score.
- Lag arithmetic (three segments) on fixed dated examples, and `not_found` is shown as Not established.
- No full-text reproduction of any ruling or article; fetched text stays gitignored.

## Success

This RFC records the owner's request, the 28 Nov 2026 feasibility evidence with URLs, what is and is not established, the proposed record type and display, how it relates to the bias meter (decided: separate datasets, never merged) and the five fact labels, the POPIA and defamation guards, both steelmen, and the remaining open owner decisions.

## Tests

Documentation only; no executable tests are added. The existing suite and `review_kit` are run on the branch as a drift check, and the staged denylist check, pickaxe check and stale-word grep are run before the commit.

## Seen, not touched

- Older files on `main` still carry agent-name wording in role positions (flagged earlier for a separate cleanup change).
- `docs/STATUS.md` rows for the older branches still carry stale "not pushed" wording; left as they are.
- The Press Council's members page is a lettered list that did not show every outlet with rulings; this RFC does not resolve it.

## Rollback

Delete the branch `dev/chg-mw-012-ombud-findings`. Base remains `ddb7e4debb2e5285c4d7fb8fd6263adbddd785f2`. After a merge, `git revert` the merge or squash commit (forward-only: no rebase, amend or force). Never on `main`.

## Sign-off

Sign-off is by someone other than the author (Reviewer A, critic reviewer). Owner GO naming the head is required before merge, and a separate owner GO before any later implementation change.
