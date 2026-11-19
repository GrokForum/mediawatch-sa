# RFC-CHG-MW-005 — Privacy page (DEV)

**Status:** DEV build complete. PENDING REVIEW (Cavus, Janus) and owner GO to push or merge. Not deployed. This RFC does not change GitHub Pages settings, DNS, or indexing.  
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

Close Phase 0 audit finding **H1** as far as a privacy page and a site-wide privacy link can go, without inventing a contact address. The live site has no `/privacy/` page and no privacy link; the Corrections page already shows the placeholder `[contact address to be confirmed by the owner before publication]`.

---

## What changes (exact files)

| File | Change |
|------|--------|
| `scripts/build_site.py` | Add a Privacy page at `privacy/index.html`. Link it from every footer (the required link) and from the site nav and the Method "Privacy" section. Keep the existing contact placeholder on Corrections and on the new page. |
| `tests/test_site.py` | Privacy page exists, required topics, noindex and DRAFT, footer link on every page, placeholder on both Corrections and Privacy, and the unconfirmed `privacy@grokforum.site` address is absent from the output. `allowed_top` includes `privacy`. |
| `changes/RFC-CHG-MW-005.md` | This record. |
| `docs/STATUS.md` | Change-log row for this RFC. |

**What stays:** noindex on every page, exact `robots.txt` (`Disallow: /`), the visible DRAFT banner, the wording of the contact placeholder, Pages settings, and the data files. No new contact address is inserted.

---

## Contact address

**The existing placeholder is kept**, on Corrections and on the new Privacy page:

`[contact address to be confirmed by the owner before publication]`

Cavus has proposed `privacy@grokforum.site` to the owner. This RFC does **not** insert that address, or any other `mailto:`, until the owner confirms it. A later one-line change can replace the placeholder once there is a named GO.

---

## What the page says

- **What is published:** findings on free public articles and public posts, each with a quote, a source link, a named actor, a fact label and both steelmen; journalists, editors and public figures only in their public or professional role.
- **What is not published:** private individuals are never named (role labels only); no private contact details, identity numbers or home addresses; no paywalled text; no internal working notes.
- **Visitors:** no cookies, analytics, trackers, accounts or forms; noindex and `Disallow: /` until a separate indexing decision.
- **Corrections and removal:** how to ask, with a link to the existing Corrections page, and the same placeholder contact.
- **Responsible party:** GrokForum, which publishes MediaWatch SA. The owner's private identity is not named. A link is given to the Information Regulator (South Africa) at its public site, as a complaints route.

The page is generated HTML, like the other static pages, so it carries the same noindex meta, DRAFT banner and `(draft)` title.

---

## Tests and how success is proven (DEV)

- `uv run -q --no-project --with-requirements requirements.txt --with pyyaml python -m pytest -q -rs` — including the local denylist test.
- Privacy page present with the required topics; footer link on every HTML page; placeholder on Corrections and Privacy; `privacy@grokforum.site` absent.
- Every HTML page still has noindex and the DRAFT banner; `robots.txt` remains exactly `User-agent: *\nDisallow: /\n`; no new file types.

## Rollback

```
git checkout main
git revert <merge-commit-of-this-RFC>
```

Pre-change SHA: `8294282db5e2e9774e89695e8b75e0e4c16a759b`. No Pages settings change to undo.

## Seen, not touched

- Phase 0 findings this RFC does **not** close: B2 (nightly job — CHG-MW-003), H3 (public data manifest — CHG-MW-004), M4 (no CSP meta), L2 (favicon.ico 404), L4 (one 4.0 s sample). Other sites' findings belong to those bots.
- The contact address itself (RFC-CHG-MW-002 open question f) stays with the owner.
- Source-link gaps (owner group has no source URL field; editor source URLs are in the data but not rendered on this branch) are reported with CHG-MW-004.
- No search-engine indexing request, no push, no PR, no merge, no Pages settings change, no deploy.

## Sign-off

Author: Grok Bot. Sign-off is by someone other than the author. Reviewers: Cavus and Janus. Owner GO is required before this branch is pushed, merged or deployed.
