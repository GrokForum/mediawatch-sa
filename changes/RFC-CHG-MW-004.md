# RFC-CHG-MW-004 — Public data manifest (DEV)

**Status:** Pushed as PR #5 (`dev/chg-mw-004-manifest`). Under review (reviewer A, reviewer B). Not merged; not deployed. This RFC does not change GitHub Pages settings, DNS, or indexing.  
**Environment:** DEV — branch `dev/chg-mw-004-manifest` (used instead of `rfc/<ver>` to match the project's existing `dev/chg-mw-*` naming).  
**Pre-change SHA (rollback base):** `8294282db5e2e9774e89695e8b75e0e4c16a759b` (`main` after PR #3).  
**Date:** 19 Nov 2026 (Africa/Johannesburg)  
**Repo:** https://github.com/GrokForum/mediawatch-sa (PUBLIC). Production URL (unchanged by this RFC): https://mediawatch.grokforum.site

---

## Environment plan

| Env | What it is | Points at production? |
|-----|------------|------------------------|
| DEV | This local branch. `python scripts/build_site.py` writes `_site/manifest.json` (gitignored, with the rest of `_site/`). | No. |
| TEST | Not stood up (RFC-CHG-MW-002 open question e). | — |
| PROD | GitHub Pages, already deploying `_site/` from `pages.yml` on `main` at `8294282`. A merge would start serving `/manifest.json` and a footer build stamp. | Only after a later, named deployment RFC with the owner's own GO on the exact head. |

---

## Goal

Close Phase 0 audit finding **H3**: the live site has no data manifest or build stamp, so data age cannot be verified. Publish a `manifest.json` at the site root with the build id, data date, build time and page counts, and show those facts in the footer.

---

## What changes (exact files)

| File | Change |
|------|--------|
| `scripts/build_site.py` | Write `_site/manifest.json`. Put a build stamp (short SHA, built-at in Africa/Johannesburg, data date, link to the manifest) in the footer of every HTML page. Where `editor_source_url` already contains `https://` URLs, render them next to the editor name on publication pages (standing rule: every published claim links to its source). |
| `.github/workflows/pages.yml` | Narrowly extend the "only allowed file types" check so `_site/manifest.json` is permitted. HTML, CSS and `robots.txt` stay allowed; no other JSON or extra types. |
| `tests/test_site.py` | Manifest field and count checks; file-type allowlist; footer stamp; editor source links; finding and item source-link test. `allowed_top` includes `manifest.json`. |
| `changes/RFC-CHG-MW-004.md` | This record. |
| `docs/STATUS.md` | Change-log row for this RFC. |

**What stays:** noindex on every page, exact `robots.txt` (`Disallow: /`), the visible DRAFT banner, the contact placeholder, Pages settings, and the data files themselves (read, not edited). The secondary lean meter stays unread and hidden.

---

## Manifest contents

Path: `_site/manifest.json` (generated, not committed). Schema id: `mediawatch.manifest/v1`.

| Field | Meaning |
|-------|---------|
| `build.git_sha` | Commit the site was built from (`MEDIAWATCH_GIT_SHA` or `GITHUB_SHA`, else `git rev-parse HEAD`). |
| `build.run_id` | GitHub Actions run id (`MEDIAWATCH_RUN_ID` or `GITHUB_RUN_ID`), or `null` for a local build. Together with the SHA this is the build id. |
| `built_at_sast` | Build time, ISO-8601 with the Africa/Johannesburg offset. |
| `data_date` | Calendar date (SAST) of the newest rendered (not paywall-excluded) finding in the sample. For the current pilot that is `2026-10-27`. A 30 Oct 2026 News24 item exists but is excluded under the no-paywall rule, so it does not set the data date. |
| `data_window` | The declared sample window, `2026-05-01` to `2026-10-31` ("May–October 2026"). |
| `counts` | `html_pages`, `findings_rendered`, `findings_excluded_paywalled`, `items`, `writers`, `publications`. |
| `inputs` | The committed data files the generator reads, each with a sha256. This is extra to the required fields, so a later refresh can be compared byte-for-byte. |

The workflow already has `GITHUB_SHA` and `GITHUB_RUN_ID` in the environment; the generator reads them with no further workflow wiring beyond the allowlist change.

---

## Allowed file types

`pages.yml` currently rejects anything that is not `*.html`, `*.css` or `_site/robots.txt`. This RFC adds exactly one exception: `_site/manifest.json`. It does not open the allowlist to `*.json`.

---

## Source links (standing owner rule)

A test now requires every finding page and every item page to have an `https://` source link (findings already did). Publication pages already link the outlet website. This RFC also renders `https://` URLs already stored in `editor_source_url`. Non-URL notes in that field (for example a LinkedIn post mentioned without a URL) are not rendered and are not turned into a link.

### Source-link gaps (not fixed here)

- **Owner group** is shown on the home and publication pages with a fact label, but `publications.csv` has no `owner_source_url` (or equivalent) field. No source is invented. Filling that field is a data change for a later RFC.
- Method, coverage and corrections pages are method text, not register findings; they are not each footnoted.
- Scorecards are roll-ups of findings that already link to their sources.
- Some `editor_source_url` values mention supporting sources without a URL; only the `https://` parts are linked.

---

## Tests and how success is proven (DEV)

- `uv run -q --no-project --with-requirements requirements.txt --with pyyaml python -m pytest -q -rs` — including the local denylist test.
- Manifest keys, `data_date == 2026-10-27` (computed from rendered findings), counts matching the build, input sha256 values matching the files.
- Only allowed file types in `_site/`; exactly one `.json` file, at the root.
- Every HTML page still has noindex, the DRAFT banner, the footer stamp, and a link to `manifest.json`. `test_noindex_everywhere` asserts both the robots meta and the visible `Draft preview (DEV)` banner on every HTML page.
- `robots.txt` remains exactly `User-agent: *\nDisallow: /\n`.

## Rollback

```
git checkout main
git revert <merge-commit-of-this-RFC>
```

Pre-change SHA: `8294282db5e2e9774e89695e8b75e0e4c16a759b`. No Pages settings change to undo.

## Seen, not touched

- Phase 0 findings this RFC does **not** close: B2 (nightly job — CHG-MW-003), H1 (privacy page and contact — CHG-MW-005; the contact placeholder stays), M4 (no CSP meta), L2 (favicon.ico 404), L4 (one 4.0 s sample). Other sites' findings belong to those bots.
- The live-check job is not on this branch (it lives on CHG-MW-003). After both merge, a later change can teach the live check to wait for this manifest's `git_sha`.
- RFC-CHG-MW-002 open questions (a)–(j) stay with reviewer A and the owner, including the corrections contact.
- No search-engine indexing request, no merge, no Pages settings change, no deploy. PR #5 was opened from this branch; the last remote commit remains `79f1ba61aac02607388b14da20685e0591054464`. Later local commits on this branch, including this review follow-up, have not been pushed. The branch is under review. Not merged; not deployed.


## Review follow-up (20 Nov 2026)

Manifest tests no longer treat the builder's own `sha256_file` helper as an oracle: each input digest is checked against `hashlib.sha256` of the file bytes and must be 64 lowercase hex characters. The manifest `build.git_sha` must be a 40-character lowercase hex git object name; a short sha or the fallback `unknown` does not pass. This is a local DEV follow-up. The last remote commit on this branch (PR #5) remains `79f1ba61aac02607388b14da20685e0591054464`; the local head is ahead and is not pushed.

Rollback for this follow-up: the merge commit that brought in the CHG-MW-003 cross-host redirect fix (`0964084e03de004383ad1f3ff88e0b682536e1dd` at the time of writing; `git log` on this branch).

## Sign-off

Author: the bot. Sign-off is by someone other than the author. Reviewers: reviewer A and reviewer B. The last remote commit on PR #5 is `79f1ba6`. Local work after that SHA is unpushed. Owner GO is required before merge or deploy.
