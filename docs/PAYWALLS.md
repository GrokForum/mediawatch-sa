# Paywalls register (draft)

Fetched for subscription product/price rows: **2026-11-05 (Africa/Johannesburg)**.  
No logins purchased; prices are as shown on each outlet’s public subscribe/membership page (or noted when the page 404s / is JS-gated / secondary).  
Sampled-items-blocked counts are from the MediaWatch SA draft corpus so far (News24 + Daily Investor + Newsday pilots). Other outlets: 0 until sampled.

| outlet | paywall_type | subscription_product | price_as_shown | subscribe_url | price_fetched | sampled_items_blocked | notes |
|---|---|---|---|---|---|---|---|
| News24 | metered / freemium (hard on many opinion/analysis) | Standard; Globetrotter (News24 + NYT All Access) | Standard **R119/mo** or **R1140/yr**; Globetrotter **R169/mo** or **R1649/yr** (14-day free trial on Standard) | https://www.news24.com/subscription | 2026-11-05 | **17** (pilot corpus; see `data/paywall_register.csv`) | Product catalog page live. Opinion columns frequently return 403/empty body without login. |
| Netwerk24 | metered / freemium | Standaard; NYT-bondel; Kook-bondel | Standaard **R149/mo** or **R1380/yr**; NYT-bondel **R199/mo** or **R1880/yr**; Kook-bondel **R179/mo** or **R1680/yr** (7-day free trial on Standaard) | https://www.netwerk24.com/intekening | 2026-11-05 | 0 | Same Media24 stack as News24. |
| Rapport | metered / freemium (via Netwerk24) | Same Netwerk24 products (Rapport e-paper inside Standaard) | See Netwerk24 | https://www.netwerk24.com/intekening | 2026-11-05 | 0 | Packaged under Netwerk24. |
| City Press | n/a (closed) | Was News24 Standard when live | n/a (last edition **10 May 2026**) | https://www.news24.com/citypress | 2026-11-05 | 0 in window post-closure | Archive only for May 2026; paywall was News24’s. |
| TimesLIVE | soft on live news; hard on Sunday Times / Sunday Times Daily | Sunday Times digital (incl. TimesLIVE Premium / Sunday Times Daily) | Annual digital package **R960/12 months** (stated on TimesLIVE promo 13 Mar 2026); day pass **R15/24h** (subscriptions FAQ) | https://www.timeslive.co.za/information/subscriptions/ ; offers https://www.timeslive.co.za/offers/ | 2026-11-05 | 0 | `/offers/` is JS-rendered — monthly tiers not extractable without browser. FAQ confirms most Sunday Times articles are subscriber-only; TimesLIVE rolling news largely free. |
| Sunday Times | hard (most articles) | Sunday Times digital / print+digital (Arena) | See TimesLIVE row (shared Arena stack); day pass R15 | https://www.sundaytimes.timeslive.co.za/offers/ | 2026-11-05 | 0 | Same Arena subscription FAQs. |
| Business Day | hard (Premium) | BusinessLIVE Premium / Premium Plus (Arena) | **Not shown** on `/offers/` HTML this fetch (JS gate). Secondary report: BusinessLIVE Premium ~**R120/mo** (unverified on outlet page) | https://www.businessday.co.za/offers/ ; info https://www.businessday.co.za/information/subscriptions/ | 2026-11-05 | 0 | Price needs browser/login later run. |
| Sowetan | soft / selective Premium | Arena offers (SowetanLIVE) | **Not shown** on `/offers/` HTML this fetch (JS gate) | https://www.sowetanlive.co.za/offers/ | 2026-11-05 | 0 | Arena group; price later run. |
| Daily Maverick | soft membership (Insider) — most news free | Maverick Insider | Page shows tier benefits from **R200/mo** or **R2,400/yr**; entry tiers historically from ~R75/mo (not re-confirmed on page body this fetch) | https://www.dailymaverick.co.za/insider/ | 2026-11-05 | 0 | Older `/maverick-insider/` and `/join/` 404. Membership, not classic hard paywall. |
| Mail & Guardian | metered / hard digital | Digital; Digital+Print | Secondary (shop page): Digital **R99/mo** or **R980/yr**; Digital+Print **R165/mo** or **R1,499/yr**. **Outlet shop URL suspended/404 this fetch** — unverified on live page | https://mg.co.za/ (shop https://wp.mg.co.za/shop/ → suspended; /shop/ 404) | 2026-11-05 | 0 | Re-fetch shop when live; do not buy on secondary alone. |
| IOL | unclear / possible premium | IOL Premium (URL 404) | **Not found** — `/premium` 404 | https://www.iol.co.za/premium | 2026-11-05 | 0 | No working subscribe page found. |
| The Citizen | none observed (home free); subscribe URL Cloudflare-challenged | n/a observed | **Not verified** (CF challenge on `/subscribe/`) | https://www.citizen.co.za/subscribe/ | 2026-11-05 | 0 | Home page serves free news; treat as free until paywall hit. |
| eNCA | none (broadcast/digital free) | n/a | n/a | https://www.enca.com/ | 2026-11-05 | 0 | No premium URL found. |
| SABC News | none (public broadcaster) | n/a | n/a | https://www.sabcnews.com/ | 2026-11-05 | 0 | Site returned HTTP 500 this fetch; historically free. |
| EWN | none observed | n/a | n/a | https://www.ewn.co.za/ | 2026-11-05 | 0 | No premium URL found. |
| Newzroom Afrika | none observed | n/a | n/a | https://www.newzroomafrika.tv/ | 2026-11-05 | 0 | `/subscribe` 404. |
| Maroela Media | soft / membership unclear | Inteken page present | **No price shown** on https://maroelamedia.co.za/inteken/ this fetch | https://maroelamedia.co.za/inteken/ | 2026-11-05 | 0 | Page nearly empty of product copy; later browser pass needed. |
| Moneyweb | metered (Insider Gold) | Moneyweb Insider Gold; Insider Pro | Insider Gold **R70/mo** or **R700/yr** (save R140 vs monthly); group **R560/user/yr** (5+) | https://www.moneyweb.co.za/moneyweb-insider-gold/ | 2026-11-05 | 0 | Clear product page. |
| GroundUp | none (donation) | Donations via Payfast | Donor amounts (e.g. suggested), not a paywall | https://groundup.org.za/donate/ | 2026-11-05 | 0 | Free to read; NPC funding model. |
| BizNews | soft / Premium members-only layer | BizNews Premium | Price **not shown** on `/premium` this fetch; secondary/register flows historically ~**R120/mo** or promo “fiver” — **unverified on page** | https://www.biznews.com/premium | 2026-11-05 | 0 | `/subscribe` and `/register/monthly` 404. Later login run. |
| Daily Investor | registration soft-wall (not paid) | Premium access free for registered users | **Free** after register | https://dailyinvestor.com/subscribe | 2026-11-05 | **0** (pilot: full bodies via curl; no login) | Explicitly: “Premium access to Daily Investor is free for all registered users.” Broad Media brand. Pilot May–Oct 2026 coded without register. |
| Newsday | none observed (free to read) | n/a — `/subscribe/` and `/premium/` **404** | n/a | https://newsday.co.za/ ; About https://newsday.co.za/about/ | 2026-11-05 | **0** | Full article bodies served without login this pass. FAIR Press Council stamp. Register/Login/Support-us chrome present but no paid product page found. |

## Priority for a later login/subscribe run (owner decision)

Highest yield for MediaWatch SA coding depth right now:

1. **News24 Standard (R119/mo)** — already blocks 17 sampled items in the pilot corpus (opinion/analysis bodies).
2. **Netwerk24 Standaard (R149/mo)** — Afrikaans sister; same group, zero sampled yet.
3. **Arena Sunday Times / TimesLIVE digital (R960/yr or day pass R15)** — when Arena outlets enter sample.
4. **Moneyweb Insider Gold (R70/mo)** — cheap, clear page, useful for markets/AGOA economics.
5. **Daily Maverick Insider** — membership; most news free so lower urgency for body text.
6. **M&G / BizNews / BusinessLIVE** — re-fetch live price pages before buying (current public price pages broken or JS-gated).

**Not a paid-login priority:** Daily Investor (free after register) and Newsday (fully free this pass) — register-only if a future soft-wall blocks a body.

## Method notes

- Prices are snapshot quotes from public HTML on 2026-11-05; JS-rendered Arena `/offers/` pages did not expose amounts to curl/WebFetch.
- “Sampled items blocked” ≠ total paywalled archive — only items we attempted to code.
- Partner Content / BrandStory on News24 is **not** a reader paywall; it is labeled commercial content (see favourable-bias findings on Takealot).
