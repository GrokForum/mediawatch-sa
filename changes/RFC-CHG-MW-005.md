# RFC-CHG-MW-005 — Privacy page (DEV)

**Status:** Pushed as PR #6 (`dev/chg-mw-005-privacy`). Under review (reviewer A, reviewer B). Not merged; not deployed. This RFC does not change GitHub Pages settings, DNS, or indexing.  
**Environment:** DEV — branch `dev/chg-mw-005-privacy` (used instead of `rfc/<ver>` to match the project's existing `dev/chg-mw-*` naming).  
**Pre-change SHA (rollback base):** `8294282db5e2e9774e89695e8b75e0e4c16a759b` (`main` after PR #3).  
**Date:** 19 Nov 2026 (Africa/Johannesburg)  
**Repo:** https://github.com/GrokForum/mediawatch-sa (PUBLIC). Production URL (unchanged by this RFC): https://mediawatch.grokforum.site

---

## Environment plan

| Env | What it is | Points at production? |
|-----|------------|------------------------|
| DEV | This local branch. `python scripts/build_site.py` writes `_site/privacy/index.html`. | No. |
| TEST | Not stood up (RFC-CHG-MW-002 open question e). | — |
| PROD | GitHub Pages, already deploying `_site/` from `pages.yml` on `main` at `8294282`. A merge would start serving `/privacy/` and a footer (and nav) link on every page. | Only after a later, named deployment RFC with the owner's own GO on the exact head. |

---

## Goal

Close Phase 0 audit finding **H1**: the live site has no `/privacy/` page and no privacy link, and the Corrections page showed a contact placeholder. This RFC adds the privacy page and, after the owner's decision of 19 Nov 2026 (relayed by reviewer A), uses the role address `privacy@grokforum.site` as the contact.

---

## What changes (exact files)

| File | Change |
|------|--------|
| `scripts/build_site.py` | Add a Privacy page at `privacy/index.html`. Link it from every footer (the required link) and from the site nav and the Method "Privacy" section. Contact on Corrections and Privacy is `privacy@grokforum.site` (a `mailto:` link), per the owner's 19 Nov 2026 decision. |
| `tests/test_site.py` | Privacy page exists, required topics, noindex and DRAFT, footer link on every page, `mailto:privacy@grokforum.site` on Corrections and Privacy, and the old contact placeholder is gone from the output. `allowed_top` includes `privacy` (and, after the merge of CHG-MW-004, `manifest.json`). |
| `changes/RFC-CHG-MW-005.md` | This record. |
| `docs/STATUS.md` | Change-log row for this RFC. |

**What stays:** noindex on every page, exact `robots.txt` (`Disallow: /`), the visible DRAFT banner, Pages settings, and the data files.

---

## Contact address

On 19 Nov 2026 the owner decided the contact is the role address `privacy@grokforum.site`, as relayed by reviewer A. The previous placeholder (`[contact address to be confirmed by the owner before publication]`) is replaced on the Corrections page and the Privacy page with a `mailto:privacy@grokforum.site` link. The same address is used in the Privacy page's "Who is responsible" section.

This answers RFC-CHG-MW-002 open question f for MediaWatch SA.

---

## What the page says

- **What is published:** findings on free public articles and public posts, each with a quote, a source link, a named actor, a fact label and both steelmen; journalists, editors and public figures only in their public or professional role.
- **What is not published:** private individuals are never named (role labels only); no private contact details, identity numbers or home addresses; no paywalled text; no internal working notes.
- **Visitors:** no cookies, analytics, trackers, accounts or forms; noindex and `Disallow: /` until a separate indexing decision.
- **Corrections and removal:** how to ask, with a link to the existing Corrections page, and the contact `privacy@grokforum.site`. If a removal is accepted, the name is taken off the published pages at the next build; earlier copies in the repository history or in caches may still hold it.
- **Responsible party:** GrokForum, which publishes MediaWatch SA. The owner's private identity is not named. A link is given to the Information Regulator (South Africa) at its public site, as a complaints route.

The page is generated HTML, like the other static pages, so it carries the same noindex meta, DRAFT banner and `(draft)` title.

---

## Tests and how success is proven (DEV)

- `uv run -q --no-project --with-requirements requirements.txt --with pyyaml python -m pytest -q -rs` — including the local denylist test.
- Privacy page present with the required topics (including the honest removal sentence); footer link on every HTML page; `mailto:privacy@grokforum.site` on Corrections and Privacy; the old placeholder gone from the output. A site-wide test walks the built `_site` and fails on any email address or `mailto` other than `privacy@grokforum.site`, after decoding `&#64;`, `&#x40;`, `%40`, `&commat;` and `[at]` / `(at)` variants.
- Every HTML page still has noindex and the DRAFT banner; `robots.txt` remains exactly `User-agent: *\nDisallow: /\n`; no new file types.

## Rollback

```
git checkout main
git revert <merge-commit-of-this-RFC>
```

Pre-change SHA: `8294282db5e2e9774e89695e8b75e0e4c16a759b`. No Pages settings change to undo.

## Live-check sample path `/privacy/`

`scripts/check_live.py` and its `SAMPLE_PATHS` live on the CHG-MW-003 branch, not on this one until that change is on the same tree. `/privacy/` must be added to `SAMPLE_PATHS` on **this** change, not on CHG-MW-003: until this privacy page is deployed, the live site has no `/privacy/` and the 003 nightly would go red if it sampled that path.

This branch therefore records the required addition here and does not copy the 003 checker into this PR. Once CHG-MW-003 is on `main` (or otherwise on the same tree as this branch), a one-line follow-up should add `/privacy/` to `SAMPLE_PATHS` (and to the checker's local fixture pages) so the nightly confirms the privacy page is 200 and noindex.

## Seen, not touched

- Phase 0 findings this RFC does **not** close: B2 (nightly job — CHG-MW-003), M4 (no CSP meta), L2 (favicon.ico 404), L4 (one 4.0 s sample). H3 (the public data manifest) is now on this branch by a forward-only merge of CHG-MW-004. Other sites' findings belong to those bots.
- RFC-CHG-MW-002 open question f (corrections contact) is answered: `privacy@grokforum.site`, owner decision 19 Nov 2026, relayed by reviewer A.
- Source-link gaps (owner group has no source URL field; editor source URLs are in the data but not rendered on this branch) are reported with CHG-MW-004.
- No search-engine indexing request, no merge, no Pages settings change, no deploy. The branch has been pushed as PR #6 and is under review.

## Sign-off

Author: the bot. Sign-off is by someone other than the author. Reviewers: reviewer A and reviewer B. The branch has been pushed as PR #6. Owner GO is required before merge or deploy.
