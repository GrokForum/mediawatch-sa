# RFC-CHG-MW-012 — Ombud and press-council findings per publication, last five years (DEV)

**Status:** Draft RFC, for owner decisions and review. Decisions 1 and 3 are DECIDED (28 Nov 2026), and the owner added a separate ruling-bias meter (section 7); decisions 2 and 4 to 8, the outlet sub-decisions A to D and L, and the ruling-meter sub-decisions E to K are still open. Branch `dev/chg-mw-012-ombud-findings`, opened as draft [PR #13](https://github.com/GrokForum/mediawatch-sa/pull/13); any later commit is pushed only on an owner GO naming the new head. No indexing request (`robots.txt` `Disallow: /` and noindex stay).
**Environment:** DEV. Branch created from `origin/main` at `ddb7e4debb2e5285c4d7fb8fd6263adbddd785f2` (28 Nov 2026, Africa/Johannesburg).
**Pre-change SHA (rollback base):** `ddb7e4debb2e5285c4d7fb8fd6263adbddd785f2`.
**Date:** 28 Nov 2026 (Africa/Johannesburg)
**Repo:** https://github.com/GrokForum/mediawatch-sa (PUBLIC). This RFC does not change GitHub Pages settings, DNS, or indexing.
**Scope:** RFC only. It adds this file, one `docs/STATUS.md` row and one `docs/LATER.md` line. No code, no data, no schema, no site change.

---

## Goal

Record the owner's request, in the owner's words:

> "rfc: add ombudsman findings per publication, last 5 years. Too many errors being apologised for, when the harm of the original piece, is done."

and propose a way to publish each tracked publication's ombud and press-council record for the last five years, showing both the finding and how long the original piece stood before any apology or correction. This RFC states what is feasible from free public sources (fetched 28 Nov 2026), proposes a design that fits `docs/METHODOLOGY.md`, and lists the decisions only the owner can make. Decision 3 (28 Nov 2026, separate datasets) and decision 1 (28 Nov 2026, every outlet with good reach that has rulings in this phase) are recorded below. The owner also asked for a separate bias meter on the rulings themselves, which is designed in section 7 and stays inside the ruling dataset. Nothing is built until the owner decides and a later, separately reviewed change implements it.

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
- **Coverage.** The BCCSA signatories page (https://www.bccsa.co.za/signatories/, HTTP 200, page dated 15 Oct 2026) lists television broadcasters (MultiChoice (DStv) subscription, e.tv, SABC 1, 2 and 3) and radio broadcasters (including 702, 947, 567 Cape Talk and the public SABC stations). Newzroom Afrika is **not listed in its own name**, so its signatory status in its own name is **Not established**. The rulings in the window name "MultiChoice Newzroom Afrika" as the respondent (for example https://www.bccsa.co.za/?p=6687), and MultiChoice (DStv) is a listed signatory. eNCA is likewise not listed by name; the rulings name eNCA, and e.tv and MultiChoice (DStv) are listed.

### In-house ombuds

- **News24** has a named public editor who also serves City Press and the group's English brands, and the group says it operates under the Press Council's rules (https://www.news24.com/citypress/news/your-voice-matters-meet-our-new-ombud-and-public-editor-20250912-0687, from a search excerpt). No public register of the public editor's findings was found: **Not established**. Formal complaints go to the Press Council, so those rulings are already in scope above.
- **Daily Maverick** has no named ombud; it publishes a corrections policy (https://www.dailymaverick.co.za/article/2026-02-17-daily-mavericks-approach-to-corrections-press-council-and-press-ombud-rulings/) with a 48-hour target for straightforward factual disputes and notes on each corrected article. That makes its own corrections visible per article, but there is no findings register.
- **Independent Media** has its own Group Ombud and says rulings are published on its website (https://iol.co.za/iol-complaints-procedure/, s.7.2; the page returned HTTP 403 to my fetch, so this is from a search excerpt). robots.txt at https://www.independentmediaombud.co.za/robots.txt returned 200 with no blanket disallow; the homepage returned 503 "Maintenance Mode" at fetch time. Counts: **Not established**.
- **Everyone else** (Mail & Guardian, TimesLive, The Citizen, EWN, SABC News and others): no in-house findings register was checked this turn. **Not established**.

### What the research means for the request

| Question | Answer |
|----------|--------|
| Can rulings be listed per publication for 1 Nov 2021 – 30 Nov 2026? | **Yes for the Press Council and the BCCSA**: dated, public, no disallow, title shows the respondent. Independent Media's ombud: not yet. |
| Are date, publication, article, clauses and outcome present? | Mostly. Article date and clauses are in most rulings; outcome is prose per complaint, so each ruling is hand-coded. |
| Can the apology date and placement be measured? | Per ruling, by finding the outlet's own page. Feasible, manual, and not on the ruling site. Print placement is often not checkable from free pages (stays Not established). |
| Is the ruling count a fair comparison between outlets? | **No, not on its own**: volume, complaint rate and membership differ, and settlements are invisible. See the steelman section. |

## Outlet scope for this phase (decision 1, DECIDED 28 Nov 2026)

Owner's words: "Add all outlets with good reach in this phase. Later net(s) will get all online publications in SA and will also examine reports on SA from outside."

**This phase** covers every outlet with good reach that has a ruling in the window, including those not yet in `data/publications.csv`. **Later phases** (each its own RFC and owner GO; recorded in `docs/LATER.md`): (1) all online publications in South Africa; (2) foreign reporting on South Africa.

### Reach criterion (proposed; the threshold and the online rule are open sub-decisions)

No free audited online audience figure was found for South African news sites: the industry web-measurement series published by IAB SA with Narratiive (latest found: August 2022, https://iabsa.net/wp-content/uploads/2024/04/Narratiive_stats_insights_August_2022.pdf) ended when that dashboard closed on 31 Aug 2022. The Reuters Institute Digital News Report 2026 for South Africa (https://reutersinstitute.politics.ox.ac.uk/digital-news-report/2026/south-africa) is free and has two weekly-reach charts, which I read live on 28 Nov 2026 (about 12:30 SAST) from their public data tables: offline (https://datawrapper.dwcdn.net/ZsCTY/2/dataset.csv) and online (https://datawrapper.dwcdn.net/vKvmI/4/dataset.csv). Each lists 16 brands with the share of respondents who used the brand for news in the last week. It is a survey of mostly English speakers, not audience measurement, and not a complete list of brands, so a brand missing from a chart is **Not established**, not low reach. The free audited source is the Audit Bureau of Circulations (ABC), whose quarterly newspaper tables I read through trade coverage (Q3 2026, 19 Nov 2026: https://www.bizcommunity.com/article/abc-q3-2026-newspapers-circulation-steadies-for-newspaper-category-184036a). Those are print tables only; ABC magazine and digital tables were not read. Print circulation is a weak and falling proxy: it understates online-first outlets, and Mail & Guardian's Q3 2026 total is 2,515.

An outlet is "good reach" and in scope if it meets **any one** of the tests below. Each test is run for each outlet with a named source; a test with no free source is **Not established**, not a fail.

| Test | Rule | Source |
|------|------|--------|
| R1 print | ABC-audited total circulation of at least 5,000 copies in the latest published quarter (proposed threshold, sub-decision B) | ABC Q3 2026 newspaper tables (https://www.bizcommunity.com/article/abc-q3-2026-newspapers-circulation-steadies-for-newspaper-category-184036a) |
| R2 broadcast | A national or metro broadcaster, or a national television news channel, that is a BCCSA signatory | BCCSA signatories page (https://www.bccsa.co.za/signatories/) |
| R3 reach survey | Listed in either Reuters Institute 2026 South Africa weekly-reach chart (16 brands each; share of the survey sample using the brand for news in the last week) | Offline https://datawrapper.dwcdn.net/ZsCTY/2/dataset.csv; online https://datawrapper.dwcdn.net/vKvmI/4/dataset.csv (read 28 Nov 2026) |
| R4 named | An outlet the owner names for this phase | Owner instruction; none named so far |

The two Reuters charts as read (percent using the brand for news in the last week). Offline: eNCA 47, SABC News 46, Sunday Times 27, Metro FM 24, local radio news 22, BBC News 22, CNN 21, Newzroom Afrika 17, other regional or local newspaper 17, Sowetan 15, The Citizen 14, community newspaper 12, Ukhozi FM 12, Isolezwe 11, SAfm 10, The Star 10. Online: News24 61, eNCA 52, SABC News 43, Daily Sun 29, BBC News 23, CNN.com 20, The South African 18, The Citizen 16, Daily Maverick 15, Netwerk24 14, Mail & Guardian 12, TimesLive 12, SowetanLive 12, Al Jazeera 12, IOL 11, community newspaper 11.

Community and local titles are out of this phase by default (sub-decision C).

### The stay list is grandfathered

The 22 outlets already in `data/publications.csv` are **grandfathered**: this RFC does not remove any of them, whatever the tests show. Each is still run through R1 to R4 below, and any that would fail, or is Not established, on today's free evidence is flagged as an owner decision (sub-decision L: keep all, which is the proposed default, or review those flagged). "Rulings" counts ombud-level rulings in the window by title; "0" means none found by title, so the reach columns are shown for information only.

| Outlet | Rulings | R1 print (ABC Q3 2026) | R2 BCCSA | R3 Reuters 2026 | Today |
|--------|---------|------------------------|----------|-----------------|-------|
| News24 | 37 | n/a (online) | n/a | online 61 | Passes (R3) |
| City Press | 15 | Not in the ABC tables read | n/a | Not listed | **Flag L: no test passes on free evidence** |
| Netwerk24 | 2 | n/a (online; Die Burger print is a separate title) | n/a | online 14 | Passes (R3) |
| Rapport | 1 | Not in the ABC tables read | n/a | Not listed | **Flag L: Not established** |
| IOL | 3 | n/a (online) | n/a | online 11 | Passes (R3) |
| Daily Maverick | 19 | Weekly Saturday title 8,201 | n/a | online 15 | Passes (R1, R3) |
| TimesLive | 11 | n/a (online) | n/a | online 12 | Passes (R3) |
| Sunday Times | 16 | 41,681 | n/a | offline 27 | Passes (R1, R3) |
| Mail & Guardian | 8 | 2,515, **below R1** | n/a | online 12 | Passes on **R3 only**; **Flag L: fails R1, kept by R3** |
| Business Day | 0 | 11,629 | n/a | Not listed | Passes (R1) |
| eNCA | 23 | n/a | Not listed by name; e.tv and MultiChoice (DStv) are listed signatories and the rulings are decided against eNCA | offline 47; online 52 | Passes (R3); R2 by name Not established |
| SABC News | 42 (SABC titles, all programmes) | n/a | SABC 1, 2 and 3 and the public SABC radio stations are listed | offline 46; online 43 | Passes (R2, R3) |
| The Citizen | 7 | 19,211 | n/a | offline 14; online 16 | Passes (R1, R3) |
| Maroela Media | 3 | Not in the ABC tables read | n/a | Not listed | **Flag L: Not established** |
| Moneyweb | 1 | Not in the ABC tables read | n/a | Not listed | **Flag L: Not established** |
| GroundUp | 2 | Not in the ABC tables read | n/a | Not listed | **Flag L: Not established** |
| Sowetan | 1 | 8,867 | n/a | offline 15; online 12 | Passes (R1, R3) |
| BizNews | 0 | Not in the ABC tables read | n/a | Not listed | **Flag L: Not established** |
| Daily Investor | 0 | Not in the ABC tables read | n/a | Not listed | **Flag L: Not established** |
| Newzroom Afrika | 6 | n/a | **Not listed in its own name: Not established.** Rulings name "MultiChoice Newzroom Afrika"; MultiChoice (DStv) is a listed signatory | offline 17 | Passes (R3); **Flag L: R2 in own name Not established** |
| EWN | 2 | n/a | n/a (its operator's radio stations are listed signatories; EWN is not named) | Not listed | **Flag L: Not established** |
| Newsday | 0 | Not in the ABC tables read | n/a | Not listed | **Flag L: Not established** |

Summary: 13 of the 22 pass at least one test on today's free evidence (News24, Netwerk24, IOL, Daily Maverick, TimesLive, Sunday Times, Mail & Guardian, Business Day, eNCA, SABC News, The Citizen, Sowetan, Newzroom Afrika). Mail & Guardian passes only on R3, and Newzroom Afrika's R2 status in its own name is Not established. Nine are flagged L as Not established or no test passed (City Press, Rapport, Maroela Media, Moneyweb, GroundUp, BizNews, Daily Investor, EWN, Newsday). None is dropped.

### Outlets this phase would add (new to the register), run through the same tests

Outlets that pass at least one test today are proposed as additions (the data change comes later, 012a). Outlets that pass no test, or only R3 as an online-first title, are **candidates** for sub-decision A.

| Outlet | Rulings | R1 print | R2 BCCSA | R3 Reuters 2026 | R4 | Result |
|--------|---------|----------|----------|-----------------|----|--------|
| Sunday World | 13 | 7,152 (4,368 paid, 2,784 free) | n/a | Not listed | no | **Add** (R1) |
| Die Burger | 2 (shared with Netwerk24) | Daily 23,945; Saturday 27,696 | n/a | Not listed | no | **Add** (R1) |
| Daily Dispatch | 1 | 9,860 | n/a | Not listed | no | **Add** (R1) |
| The Witness | 1 (shared ruling) | Daily 6,102 | n/a | Not listed | no | **Add** (R1) |
| Primedia radio (702, Cape Talk, 947) | 22 BCCSA rulings by title | n/a | 702, 947 and 567 Cape Talk are listed signatories | Not listed (local radio news is a generic entry) | no | **Add** as broadcast outlets (R2); audience figures are paid and Not established |
| SABC radio stations (Metro FM, Ukhozi FM, SAfm, 5FM) | part of the 42 SABC titles | n/a | Listed as public radio signatories | Offline: Metro FM 24, Ukhozi FM 12, SAfm 10 | no | **Add** for news and current-affairs programming only (R2, R3; sub-decision D) |
| MultiChoice channels | 55 BCCSA titles | n/a | MultiChoice (DStv) is a listed signatory | Not listed as its own brand | no | **Add** for news and current-affairs programming only (R2; D); whether each ruling concerns news was not checked |
| Daily Sun | 2 | ABC lists it "Discontinued" (live-read Q2 2025 table: https://www.bizcommunity.com/article/abc-q2-2025-newspapers-show-growth-despite-closure-of-media-24-titles-402979a); the Media24 page says it is a digital-only brand (https://www.media24.com/newspaper/daily-sun/) | n/a | online 29 | **no** (the owner did not name it; it was an example in the instruction) | **Candidate (A):** meets R3 only, online-first |
| The South African | 3 | n/a | n/a | online 18 | no | **Candidate (A):** meets R3 only, online-first |
| MyBroadband | 1 | n/a | n/a | Not listed | no | **Candidate (A):** no test passed; a 2022 closed-series figure (2.57m unique browsers) is not current |
| amaBhungane | 4 | Not in the ABC tables read | n/a | Not listed | no | **Candidate (A):** no test passed |
| Financial Mail | 1 | Not in the ABC newspaper tables read (ABC magazine tables not read): Not established | n/a | Not listed | no | **Candidate (A):** no test passed. Business Day, its sister title, is in the register and passes R1 (11,629) |
| Sunday Independent | 1 | Not in the ABC tables read | n/a | Not listed | no | **Candidate (A):** no test passed |
| Briefly News, The Continent, Vrye Weekblad, Bhekisisa | 1, 2, 1, 1 | Not in the ABC tables read | n/a | Not listed | no | **Candidates (A):** no test passed |
| Community and local titles (for example Ladysmith Gazette 2,468; Oudtshoorn Courant 3,984; Overstrand Herald; BloemNews) | 1 each | Below R1 or not in the tables read | n/a | Not listed | no | **Out of this phase (C)** |

Summary: 7 new outlets or groups pass at least one test and are proposed as additions (Sunday World, Die Burger, Daily Dispatch, The Witness, Primedia radio, SABC radio stations, MultiChoice channels; the last two for news only). Two are candidates that meet R3 only (Daily Sun, The South African). Eight are candidates with no test passed (MyBroadband, amaBhungane, Financial Mail, Sunday Independent, Briefly News, The Continent, Vrye Weekblad, Bhekisisa). Local titles are out. Each online-first R3-only title stays a candidate until sub-decision A is made.

Adding an outlet to `publications.csv` is a data change and comes in the later data change (012a); this RFC records the decision and the list.

## Proposed design

### 1. New record type: `ombud_ruling` (separate from `findings`)

One row per ruling decision **per publication** (first-instance and each appeal stage are separate rows, linked by case; a ruling that names two outlets produces one row per outlet sharing the same `ruling_id`). Fields:

| Field | Meaning |
|-------|---------|
| `ruling_id` | Body plus its own case number (Press Council complaint number; BCCSA adjudication or case number) |
| `body` | `press_council`, `bccsa`, `independent_media_ombud`, or `in_house` |
| `stage` | `ombud`, `adjudication_panel`, `leave_to_appeal`, `appeals_panel`, `bccsa_adjudicator`, `bccsa_tribunal`, `bccsa_appeal` |
| `ruling_date`, `ruling_url`, `fetched_on` | Date as printed on the ruling; the fetch date. `ruling_url` is the ID form with no slug (see 1a) |
| `publication_id` | Links to `data/publications.csv`. Counts per publication count a shared ruling once for each outlet it names; any total across outlets de-duplicates by `ruling_id` |
| `article_url`, `article_headline`, `article_published`, `article_access` | Headline quoted exactly, in its redacted form where a private name appears (see 1a). `article_access` follows §5a: if the article is paywalled, the ruling record may still exist, but no article text is read or quoted beyond what the ruling itself quotes |
| `byline` | Only where the ruling names the author, as a public role. Stored for provenance, not rolled up (see open decision 6) |
| `complainant_type`, `complainant_label` | `organisation`, `public_body`, `public_figure_in_role`, or `private_person`. Named only for the first three; a private person, including a one-person business, is stored as "a private complainant" (see 1a) |
| `code_version`, `clauses` | The Press Code in force (a new Code took effect on 30 Sep 2022, so clause numbers differ before it) or the BCCSA code, and the clauses complained of |
| `sub_findings` | One entry per complaint: clause, upheld or dismissed |
| `finding` | `upheld`, `partly_upheld`, `dismissed` (ruling level); `appeal_status`; `final_finding` after appeal. A ruling inside its appeal window is `appeal_window_open` and is not counted as final |
| `sanctions` | Closed list: `reprimand`, `correction`, `retraction`, `explanation`, `apology`, `right_of_reply`, `findings_published`, `takedown`, `fine`, `space_sanction`, `other`, plus the directed placement as quoted |
| `own_correction_date` | If the outlet corrected on its own before the ruling (the ruling usually says so) |
| `remedy_date`, `remedy_url`, `remedy_placement`, `remedy_checked_on` | When and where the apology or correction ran, found on the outlet's site. `not_found` is a valid value, with the date checked. `remedy_url` follows the same rule as `ruling_url` (see 1a), and a placement quoted from a direction is redacted |
| `lag_to_ruling_days`, `lag_ruling_to_remedy_days`, `lag_to_remedy_days` | Computed from the three dates: article to ruling, ruling to remedy, article to remedy. Kept as separate segments so a process delay (the complaint window and the appeal window) is not blamed on the outlet |
| `prominence_parity` | `comparable`, `lesser`, or `not_established`, with the test named (the Council's placement guidance, items 9–10) |
| `quote`, `steelman_outlet`, `steelman_complainant` | One short exact quote from the ruling, chosen so it carries no private name, or redacted (see 1a); one short paragraph each, as in §7 |
| `label` | `Proven` (see below) |

Fetched ruling text is stored under the existing gitignored fetched-articles area and never committed; the repo holds the structured row and a short quote only.

### 1a. Redaction rule (private complainants and one-person businesses)

Ruling pages, their URL slugs, headlines, apology headlines and quotes can carry a private complainant's name. No such name is kept in any field of any committed file, in any display, or in this repo's history.

- **Who counts as private.** A natural person who is not a public figure acting in a public role is `private_person`. So is a **one-person business** (a sole proprietor, a professional practising in their own name, or a company whose name is a personal name or whose ruling describes the complainant as its only owner or director). When in doubt, treat the complainant as private and mask. An organisation or public body is named only when it is clearly more than one person or a public institution.
- **URLs.** Both ruling sites are WordPress, and `https://<host>/?p=<post id>` redirects (HTTP 301, checked 28 Nov 2026 on both) to the full slug URL. `ruling_url` and `remedy_url` are stored in that ID form, which carries no slug, never the slug URL. `article_url` is stored as given unless its slug carries a private name, in which case it is stored as `withheld_private_name` with its SHA-256 for audit. The outlet's own apology page is handled the same way.
- **Headlines and quotes.** A name is replaced by `[name withheld]` (the mid-cut marker rule in §5 applies to omitted text only). A quote is chosen so it needs no private name; if it cannot be, it is redacted the same way. A sanction placement that quotes a direction naming the complainant ("a headline including the words 'apology' and ...") is redacted.
- **How it is done.** Redaction happens at ingest, before any row is written. Raw fetched text stays in the gitignored fetched-articles area. Each private name seen at ingest is added to the gitignored local denylist, so the staged denylist check and the pickaxe check block it from any commit.
- **Linked names.** A public body, a public figure in role, a journalist's byline and an outlet may be named, as in §8. A private complainant's name also never appears in the page title, the file names or the commit messages.

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

- **Decided by the owner, 28 Nov 2026 (decision 3):** the ruling record is a **separate dataset** that never feeds the media bias scores, roll-ups or findings. It is kept in its own files and display, as the secondary lean is. The `ombud_ruling` rows carry no score and make no contribution to any media publication×actor mean. (The ruling-bias meter in section 7 scores the ruling text inside that same dataset and is likewise never merged with the media meter.)
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

- Complainants who are private persons, including one-person businesses, stay unnamed, in the record, the page and this repo, and the redaction rule in 1a applies to URLs, headlines and quotes. Public bodies, organisations, public figures in their public role, journalists and publications may be named, as in §8.
- The Council's complaints are lodged against publications, not individual journalists or editors (https://presscouncilsa.org.za/complaints/). The byline is therefore stored for provenance only; no per-journalist ruling tally is proposed.
- Ruling pages carry contact details and sometimes private detail; none is stored or pasted. Only the contact address `privacy@grokforum.site` appears in this project.
- Defamation guard: every statement uses the body's own words ("the Press Ombud found…") with the link, the date, the appeal status and the final outcome, and is updated or removed if the body later varies it. Outlets can ask for a correction through the contact address.

### 6. Steelman, both sides

- **For outlets.** Prompt self-correction deserves visible credit, hence the "own initiative before the ruling" count and the separate lag segments. A raw ruling count penalises outlets that join the system and engage with the ombud, and outlets outside the system never appear. Large outlets draw more complaints, and many complaints come from parties in a dispute with the outlet; a complaint count is not an error rate. Many rulings are dismissed, and an outlet that wins deserves that shown. Part of the lag is process, not the outlet.
- **For the complainant and the reader.** An apology that runs weeks or months after the article, on an inside page or under the headline's reach, leaves the original impression standing, which is the owner's point. Settlements at the Public Advocate stage leave no public record, so the published rulings undercount errors that were quietly fixed. A non-member's record is invisible. A prompt correction can still be too small for the harm.
- **Normalisation.** Per-outlet complaints received are not published (the dashboard is aggregate): **Not established**. MediaWatch holds no census of each outlet's article output (the pilot register is a locked sample), so rulings per thousand articles is **Not established** and is not shown. What can be shown fairly is the upheld share of rulings decided, the share corrected on the outlet's own initiative, and the jurisdiction line. If the owner wants a volume base, a published, free output figure per outlet would be needed first.

### 7. Ruling-bias meter (inside the ruling dataset; added on the owner's instruction, 28 Nov 2026)

Owner's words: "You can add a bias meter on ombud rulings, they're also human."

**Boundary (keeps decision 3).** This is a second meter that lives wholly inside the ruling dataset. It has its own files, its own actor ids, its own roll-ups and its own display block, headed "Ruling record: bias in the rulings (about the rulings, not the media)". It is never merged with the media bias meter and never cross-referenced to it: no media finding id appears in a ruling finding, no ruling id or ruling finding appears in a media finding, the two use separate actor id spaces with no join, and no figure combines them. A reader compares the two views for themselves.

**Question each ruling finding answers.** Relative to a named actor, does this passage of the ruling (its reasoning or its directions) work FOR or AGAINST that actor, and by which driver? The ruling's reasoning is scored against the record before the body (the complaint, the response, the article as the ruling quotes it, and any free public primary record). It is **not** a judgment of the adjudicator as a person.

**Same rules as the media meter.** The METHODOLOGY drivers, weights (§3), signed score (§4), evidence gates (§5), free-content rule (§5a), fact labels (§2), steelman protocol (§7) and POPIA rules (§8) apply unchanged, read for a ruling:

| Driver | Read for a ruling |
|--------|-------------------|
| `loaded_label` | The ruling uses a pejorative coinage or loaded term about a party that is not its own self-description |
| `one_sided_sourcing` | The reasoning rests on one party's submissions on a contested point, without testing them against the other side or the record |
| `missing_right_of_reply` | A party was not given the chance to answer an adverse point the ruling relies on |
| `omission` | A material fact in the record is left out of the reasoning |
| `framing` | Word choice or narrative that steers beyond what the record shows |
| `headline_body_gap` | The ruling's summary or headline is stronger or different than its reasoning and findings |
| `factual_error` | The ruling states a demonstrable false fact, checked against the record |
| `correction` | A later appeal or variation corrects the ruling; links only to the original ruling finding inside this dataset |

A ruling that applies the code to the record, hears both sides and gives sourced, proportionate reasons produces **no row** (neutrality produces no row), mirroring §8b: sourced reasoning is not bias. Every row has an exact quote from the ruling, its URL, its date, the body and office as printed, a fact label on any factual claim, and both steelmen. The steelman for the ruling states the strongest fair reading under which it correctly applies the code; the steelman against states the strongest fair reading under which it misreads the record or loads the dice.

**Actors the meter can score.**
- **The outlet** (the publication or broadcaster the ruling is about).
- **The complainant, only if** it is an organisation, a public body or a public figure acting in a public role. A **private complainant (including a one-person business) is never an actor and stays unnamed**; a ruling that favours a private complainant is scored for its effect on the outlet only.
- The body and the office-holders are the **source** of the text, not scored actors. Ombud, deputy ombud, panel and chair of appeals are public office-holders and may be named in that role, as published on the ruling.

**Roll-ups and minimum n.** The unit is body × actor (for example Press Council × a named outlet, BCCSA × a named broadcaster), the counterpart of publication × actor. §6.4 applies to the number of findings: under 5 shows the findings only with no score, 5 to 9 is provisional, 10 or more is a public score. Proposed extra guard: a score needs findings from at least three distinct rulings, so one long ruling cannot make a score. Confidence follows §6.5 (dual-coded 10% sample, Cohen's kappa on the actor, direction and driver triple), and every AGAINST finding is dual-coded before display (proposed, sub-decision I). A ruling reversed or varied on appeal keeps its original rows and gains a `correction` row; the display uses the final ruling.

**Defamation care.** Score the reasoning against the record, not the person. Wording is "the ruling at paragraph N works AGAINST the outlet because it …", never "the ombud is biased". Quotes are short and exact; each finding shows the appeal status; whether the body is told before a score is published is open (sub-decision H), and **until the owner decides H, no ruling-meter score is published**; the contact address is open to the body at any time. No finding is made about an adjudicator's motives, health, family, affiliations or conduct outside the ruling.

**Open sub-decisions for this meter.** (E) Name individual office-holders in any roll-up (default no: body and office level only; a named person only if the owner decides and n is at least 10). (F) Coding frame: all rulings in the window (about 440 across the Press Council and the BCCSA, as counted above) or a locked random draw by stratum, as the pilot did (§8a). (G) Driver weights: the same as the media meter (proposed) or ruling-specific. (H) Pre-publication notice to the body. (I) Dual-code every AGAINST finding. (J) Whether appeal stages are scored as rulings of their own (proposed) or only the final ruling. (K) Whether BCCSA entertainment and harm-to-children rulings are in the frame, or news and current affairs only (linked to D).

## Decisions for the owner (decisions 1 and 3 decided 28 Nov 2026; the others open)

1. **Sources and outlets in scope. DECIDED by the owner, 28 Nov 2026.** In the owner's words: "Add all outlets with good reach in this phase. Later net(s) will get all online publications in SA and will also examine reports on SA from outside." This phase covers every outlet with good reach that has rulings in the window (criterion and outlet list in "Outlet scope for this phase" above). Sources remain the Press Council (all four ruling types) and the BCCSA (including its appeals), with Independent Media's ombud later once its site is reachable. Later phases, each its own RFC and owner GO: all South African online publications, and foreign reporting on South Africa (also in `docs/LATER.md`). Sub-decisions still open: **A** whether an online-first outlet that meets only R3 (survey-based; Daily Sun 29 and The South African 18) is added, and how to treat outlets that meet no test (the candidates above); **B** the R1 threshold (proposed 5,000 copies); **C** community and local titles (default out); **D** which broadcast programmes (news and current affairs only, proposed); **L** the grandfathered stay list: keep all 22 (proposed default) or review those flagged L.
2. **Window.** Proposed: rulings dated 1 Nov 2021 to 30 Nov 2026 on first load, then a rolling five years, refreshed monthly. Alternatives: window by article date; a longer span.
3. **Do rulings feed scores? DECIDED by the owner, 28 Nov 2026.** No: rulings never feed the media bias scores, roll-ups or findings. (The owner then added a separate ruling-bias meter, section 7, which stays inside the ruling dataset.) In the owner's words: "Rulings are 3rd party and often subjective, despite requirement to be objective. Your suggestion is approved, a separate record of ruling sheds light on those, while your bias meter sheds light on bias. 2 different datasets, not to be merged." Rulings are a separate dataset that never feeds bias scores, roll-ups or findings, and the rulings are not used as evidence for a bias finding. Options (C) (an upheld ruling opens a candidate finding) and (D) (a remedy counts as a `correction` clawback), and the evidence route under (B), are rejected. Steelman: the ruling bodies are valuable as a public record of what was found and directed, but they are third parties whose rulings can be subjective, so MediaWatch keeps them visible without letting them stand in for its own evidence. Keeping the datasets apart also protects the outlet from a ruling counting twice, and protects the ruling record from MediaWatch's own coding. The cost is that a reader must compare the two views themselves.
4. **Accuracy-only errors.** A sister register offered three identity errors in one outlet's explainer (a judge's first name and a gendered pronoun) as candidate findings; they are unscored accuracy slips with no for/against direction. Should a separate, unscored `accuracy_note` type join this accountability record, or stay out? This RFC does not add it.
5. **Scope of "per publication".** Publication-level only (proposed), or also per outlet group (for example Media24, Arena, Independent Media)?
6. **Bylines.** Store only (proposed), or also show a per-journalist list? Complaints are lodged against publications, so the default is no per-journalist roll-up.
7. **Prominence parity.** Use the Council's placement guidance as the test (proposed), and show print placement as "not established" unless a free, public copy exists.
8. **Ruling-bias meter (new, 28 Nov 2026).** Approved in principle by the owner ("You can add a bias meter on ombud rulings, they're also human."); the design is section 7 and sub-decisions E to K are open.

## What this change contains / what stays

This branch adds `changes/RFC-CHG-MW-012.md`, one row in `docs/STATUS.md` and one line in `docs/LATER.md`. It changes no code, data, schema, workflow, site page, `robots.txt`, `CNAME` or GitHub setting, and no collector runs. `docs/METHODOLOGY.md` is unchanged here; a later change would add a section describing the ruling record as a separate dataset. No score, weight or roll-up changes, so no prior score is frozen or rewritten. The two meters and their files are untouched.

## Later work (each a separate RFC, reviewed, with an owner GO)

1. **Schema and data (CHG-MW-012a).** `data/ombud_rulings.csv`, validation in `scripts/validate_schema.py`, `outlet_type`-style jurisdiction field on `publications.csv`, a methodology section.
2. **Collector (CHG-MW-012b).** Reads the Press Council and BCCSA listings, one request at a time with a pause, an identifying user agent, robots.txt checked first, TLS verification on, and errors written to `data/collector_errors.csv`. It stores structure, not full ruling text.
3. **Site block (CHG-MW-012c).** The per-publication display above, behind the same noindex and draft marker.
4. **Ruling-bias meter (CHG-MW-012d).** Own schema and files, a METHODOLOGY section for the ruling meter, a pilot on a locked draw of rulings, dual coding, and the separation tests below.
5. **Later phases.** All South African online publications, and foreign reporting on South Africa, each its own RFC (also in `docs/LATER.md`).

Tests those changes must cover at least:

- robots.txt and TLS: respect the disallow lines; never disable TLS verification; the BCCSA collector uses `bccsa.co.za`, not the hosts that failed.
- Fail closed on a host that does not verify, or a 503.
- A ruling inside its appeal window is not counted as final.
- A dismissed ruling is shown as dismissed and adds no negative mark.
- A private complainant is never stored by name (test with a synthetic name built at run time), including a one-person business, in a URL slug, a headline, a quote, a sanction placement and a file name; `ruling_url` and `remedy_url` are stored in the slug-free ID form; a redacted headline carries `[name withheld]`.
- The accountability record never changes a bias score, and the frozen historical scores stay byte-identical.
- The two datasets stay unmerged: the `ombud_ruling` table carries no actor, score or media finding id; no media findings file references a `ruling_id` or a ruling finding; no ruling-meter file references a media finding id or media actor id; the two use separate actor id spaces; the site build never joins or sums them.
- Ruling meter: a private complainant is never an actor; an office-holder is never a scored actor; min-n and the three-distinct-rulings guard hold; a ruling with sound reasoning produces no row; a reversed ruling gains a `correction` row inside the ruling dataset only.
- Lag arithmetic (three segments) on fixed dated examples, and `not_found` is shown as Not established.
- No full-text reproduction of any ruling or article; fetched text stays gitignored.

## Success

This RFC records the owner's request, the 28 Nov 2026 feasibility evidence with URLs, what is and is not established, the proposed record type and display, how it relates to the bias meter (decided: separate datasets, never merged), the reach criterion and outlet list (decision 1), the separate ruling-bias meter with its defamation care and minimum-n rules, the five fact labels, the POPIA guards, both steelmen, and the remaining open owner decisions.

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
