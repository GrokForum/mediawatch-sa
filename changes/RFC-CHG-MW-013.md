# RFC-CHG-MW-013 — Watch-network footer back-link (DEV)

**Status:** This change adds a plain footer link on every built page to `https://watch.grokforum.site/`. `robots.txt` stays `Disallow: /` and noindex stays on every page. No indexing request. A merge to `main` is a GitHub Pages deploy and needs a named owner GO for that head.
**Environment:** DEV — branch `dev/chg-mw-013-watch-backlink` created from `origin/main` at `ddb7e4debb2e5285c4d7fb8fd6263adbddd785f2` (28 Nov 2026, Africa/Johannesburg).
**Pre-change SHA (rollback base):** `ddb7e4debb2e5285c4d7fb8fd6263adbddd785f2` (`origin/main` at the start of this change).
**Date:** 28 Nov 2026 (Africa/Johannesburg)
**Repo:** https://github.com/GrokForum/mediawatch-sa (PUBLIC). This RFC does not change GitHub Pages settings, DNS, or indexing.

---

## Environment plan

| Env | What it is | Points at production? |
|-----|------------|------------------------|
| DEV | This branch. The footer change and the test suite can be inspected locally. | No. |
| TEST | Pull-request checks and two plain PASSes on the same head, when a PR exists. | No. |
| PROD | GitHub Pages, deploying from `main` via `.github/workflows/pages.yml`. A merge to `main` is a live publish of the site. | Only after a named owner GO for merge (which is also the deploy GO) on the exact head. |

---

## Goal

Add a visible, plain link in the footer of every page built by `scripts/build_site.py` `page()` back to the Watch directory at `https://watch.grokforum.site/`. This is a chrome-only change. The owner asked for a link from each watcher site to that directory.

## What changes (exact files)

| File | Change |
|------|--------|
| `scripts/build_site.py` | In `page()`, append one footer paragraph after the existing privacy footer-nav: `<p><a href="https://watch.grokforum.site/">Part of the Watch network — watch.grokforum.site</a></p>`. The visible text uses a Unicode em dash (U+2014). The `href` is exactly `https://watch.grokforum.site/` (https, host only, trailing slash, no path, query, fragment or tracking parameters). The link is a plain `<a>` with no `target` and no `rel`. |
| `tests/test_site.py` | Add `test_watch_network_footer_on_every_page` next to `test_noindex_everywhere`. It walks every built `*.html` page and asserts the exact footer markup, the exact `href`, the exact visible text, the `noindex, nofollow` robots meta, and the visible draft banner. It also checks that `robots.txt` still has `Disallow: /`. |
| `changes/RFC-CHG-MW-013.md` | This record. |
| `docs/STATUS.md` | Change-log row for this RFC. |

## What stays

- `robots.txt` (`User-agent: *` / `Disallow: /`), the `noindex, nofollow` robots meta, and the draft banner copy are unchanged.
- The reserved repo-root `index.html` and `CNAME` are unchanged (`test_live_placeholder_untouched` still requires they match `0280f59`).
- No custom `404.html` is added. The builder still does not emit one; the Pages default 404 stays.
- Methodology, collectors, findings, publications, workflows, CSP, DNS, and Pages settings are unchanged.
- Existing footer content (publisher line, build stamp, privacy link) stays; the new paragraph is appended after it.

## Seen, not touched (out of scope)

- Other open branches and pull requests.
- Indexing policy. This change must not reopen indexing.
- A generated custom 404 page.
- Any change to the Watch directory itself.

## Risk

Low. The change is one footer paragraph on pages already built by `page()`, plus a test. The new link is plain, with no tracking parameters. The main risk is that a merge to `main` is a live GitHub Pages publish, so a wording or markup error would go live until reverted. Rollback is git, and Pages republishes the previous chrome after the revert. Indexing stays off.

## Success

- Every built HTML page contains the exact substring `href="https://watch.grokforum.site/"` and the exact visible text `Part of the Watch network — watch.grokforum.site`.
- Every built HTML page still has `<meta name="robots" content="noindex, nofollow">` and the visible draft banner. `robots.txt` still has `Disallow: /`.
- Repo-root `index.html` and `CNAME` are unchanged versus `0280f59`.
- `uv run -q --no-project --with-requirements requirements.txt python -m pytest -q` passes in the development checkout (the gitignored denylist and `data/fetched_articles/` may be present for that run as local copies and are never committed).
- The same command in a clean clone passes, with the expected skips where those local files are absent.
- review_kit is clean, or findings are explained.
- The new commits contain no denylist term and no role-word violations.

## Tests

`uv run -q --no-project --with-requirements requirements.txt python -m pytest -q`

Recorded on 28 Nov 2026 (Africa/Johannesburg), pytest 9.2.0:

- Development checkout (gitignored denylist present; `data/fetched_articles/` present as a local copy for the run only, never staged): **104 passed** in 26.57s.
- Clean clone (those local files absent): **101 passed, 3 skipped** in 6.50s. The three skips are the denylist tests and the fetched-article test, as expected.

## Rollback

Before merge: drop the branch `dev/chg-mw-013-watch-backlink`, or revert the commit(s) on it. After merge: revert the merge (or squash) commit on `main`. Pages will republish the previous chrome. Either restores the tree at rollback base `ddb7e4debb2e5285c4d7fb8fd6263adbddd785f2`. Forward-only: no rebase, amend, or force. Never on `main`.

## Sign-off

Sign-off is by someone other than the author (Reviewer A, critic reviewer). Both must give a plain PASS on the same head. Owner GO naming the exact head is required before merge. Because a merge to `main` publishes the site through Pages, that GO must be a merge-and-deploy GO. This RFC does not itself authorise a merge, push, or deploy.
