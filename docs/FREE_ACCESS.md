# Free access routes (draft method note)

**Project:** MediaWatch SA  
**Purpose:** Document *legitimate* free routes to article text when the owner cannot afford subscriptions. Draft only — no publish.  
**Rules this pass obeyed:** no Googlebot/crawler UA spoofing; no paywall-script stripping; no bypass services (12ft, removepaywall, etc.); no logins; archive.today **read existing snapshots only** (do not create); Internet Archive / republications / public author gift links only.  
**Checked:** 2026-11-05 (Africa/Johannesburg).

Canonical links always stay the outlet URL. Archived or companion copies are **evidence**, not replacements.

## Standing rule: no paywalled content, ever (owner, 17 Nov 2026)

Bias is judged **only on what the public can read free**. Paywalled articles are **out of the sample** and **never scored**. A headline, standfirst, OG description or other teaser **never stands in for the body** of a paywalled piece. No subscriptions, logins, user-agent spoofing, paywall-script stripping or bypass services, ever.

This supersedes the earlier practice in this note of coding a paywalled piece from its headline, OG description or standfirst, and of treating an archived copy of a paywalled body as a substitute. The routes below are kept as history and for checking **free** pieces only. Whether an archived copy of a piece paywalled at source may ever count is an open owner question (RFC-CHG-MW-002, question h); until then such findings are excluded. See `docs/METHODOLOGY.md` §5a and `data/paywall_exclusions.csv`.

---

## What worked this pass (News24 paywall_register)

| Route | Result on ~21 News24 rows |
|---|---|
| Wayback availability / replay | **14/21** had snapshots. **2** were true full-body free captures (`isAccessibleForFree=true`). **12** were paywall *shells* (`article__body--locked`) — title/OG only. |
| archive.ph / archive.today | Host returned CAPTCHA / TLS failures from this environment; **no existing snapshot confirmed**. No new archives created. |
| Republication (MSN / Netwerk24 / Maroela / Politicsweb) | **No verbatim** copies of the registered News24 URLs found in public search. Related free coverage sometimes exists (e.g. Citizen on Hill-Lewis/Phala Phala) but is a **different piece**. |
| Author X gift / share links (`x` public reads) | **None** found for the registered URLs in author/News24 posts around publication dates. |

**Counts:** full **2** · partial **12** · still_blocked **7**.  
Recovered text lives under `data/fetched_articles/` (gitignored). Register columns: `recovery_source`, `recovery_url`, `snapshot_timestamp`, `recovery_status`, `recovery_notes`.

---

## Per-outlet free routes (publications.csv spot-checks)

Spot-check = 1–2 live article/section fetches plus Wayback availability where useful. Models change; re-check before coding.

### News24 (Media24) — hard digital paywall on most politics/opinion
- **Live:** many politics/column URLs ship `article__body--locked` / `isAccessibleForFree=false` (teaser + subscribe CTA).
- **Wayback:** often archives the **locked shell**, not the unlocked body. Occasional free pieces (e.g. some business explainers, presidential hosted opinion) appear in IA with full body.
- **Does not work here:** assuming every IA hit is full text — always confirm body.

### Netwerk24 (Media24, Afrikaans) — subscriber wall
- Spot-check (`Hill-Lewis: Ramaphosa doen niks…`, 2026-09-18): live page locked, `isAccessibleForFree=false`, ~teaser only. No Wayback closest snapshot on that URL at check time.
- Same Media24 stack as News24; expect similar IA-shell behaviour.
- Free routes: rare free promos; Afrikaans republication elsewhere (Maroela sometimes covers same *events*, not always same *copy*); library PressReader for print Netwerk24/Rapport if offered.

### Rapport (Media24, via Netwerk24)
- Section hubs push subscribe CTAs. Article bodies follow Netwerk24 paywall.
- Rapport-origin pieces sometimes appear in English on News24 (still paywalled). Free route is the same Media24 pattern — IA only if unlocked body was crawled.

### Sunday Times / TimesLIVE (Arena)
- Spot-check (2026-11-05 politics/Sunday Times news URLs): full article HTML readable without login on sampled live pages (election/wire-style). Homepage still carries heavy “subscribe/premium/paywall” chrome — **metered or selective** wall likely on exclusives.
- Free routes: many digital news pages currently open; Wayback; PressReader (Sunday Times commonly in SA city library PressReader catalogues).

### Business Day (Arena)
- Spot-check: live pages showed lock/subscribe signals while still exposing substantial paragraph HTML on some politics URLs — treat as **soft/hybrid** wall; do not assume durable free access.
- Free routes: occasional open articles; Wayback; PressReader (Business Day frequently listed for library members).

### Mail & Guardian
- Spot-check: news article body returned in full on a 2026-11-04 politics URL; membership chrome present site-wide but sample was readable.
- Free routes: many MG digital stories free; membership for support/some extras; Wayback; PressReader often includes M&G for library users.

### Moneyweb
- Spot-check (`Sun International… Kimberley casino`): **full free** body in live fetch (~6k+ chars), subscribe CTAs in chrome only.
- Free routes: most Moneyweb news free to read; some premium/events behind account — confirm per URL. Wayback as backup.

### Daily Maverick
- Spot-check (two 2026 article URLs): **full free** bodies; membership appeals but not a hard wall on samples.
- Free routes: standard DM journalism free in browser; membership voluntary/support. Wayback works well historically.

---

## PressReader via public libraries (general)

Several South African city and university libraries license **PressReader** for cardholders (examples historically publicised: City of Cape Town, City of Johannesburg, some university libraries). With a valid library membership you can open PressReader’s app or site and read participating **print/digital editions** (often Sunday Times, Business Day, Mail & Guardian, and various Magazines).  

This is a **legitimate licensed** route, not a bypass: access is tied to library membership terms, may be geofenced or capped, and title lists vary by library. It does **not** automatically unlock News24/Netwerk24 web paywalls. Use it when the needed piece appears in an edition PressReader carries; keep the outlet’s canonical URL as the citation and note PressReader as the evidence path.

---

## Practical coding rule for this project

1. Try Wayback (availability → fetch → **confirm body**, not just HTTP 200).  
2. Check for an existing archive.today snapshot (read only).  
3. Search for a verbatim republication on a free site (e.g. MSN, Politicsweb, Netwerk24, Maroela) — related coverage of the same event is not a substitute for the same copy.  
4. Search the author’s public X posts near the pub date for gift/share links.  
5. If the piece is paywalled at source: **do not code it.** Register the URL in `paywall_register.csv`, leave it out of the sample, and move on. Headlines and teasers never stand in for the body (owner rule, 17 Nov 2026). **Do not** buy a subscription for the owner and **do not** use bypass tooling.

