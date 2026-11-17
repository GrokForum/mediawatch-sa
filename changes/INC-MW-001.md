# INC-MW-001: draft files publicly served by GitHub Pages

**Status:** The fix was raised as [PR #2](https://github.com/GrokForum/mediawatch-sa/pull/2) at `bf61748` on 17 Nov 2026. A follow-up wording commit was added on the same branch. Merge was subject to the owner's GO.
**Found:** 17 Nov 2026, about 11:05 SAST, while building CHG-MW-002.
**Impact:** After the PR #1 merge (now `bed21e7` after the history rewrite), the legacy Pages build serves the whole repo root. `/data/lean_scores_draft.json` (the hidden lean meter), `/data/news24_pilot_findings.json`, `/docs/*` and `/plan` return HTTP 200. There is no `robots.txt`.
**Fix:** A root `_config.yml` that excludes `data/`, `docs/`, `changes/`, `scripts/`, `tests/`, `plan.md` and `README.md` from the Pages build, plus a root `robots.txt` that disallows all crawlers. `index.html` and `CNAME` are untouched.
**Verify after push:** The paths above return 404, `/robots.txt` returns 200, and `/` still shows the placeholder.
**Rollback:** Revert the fix with `git revert -m 1 <merge sha>`, or turn Pages off. `main` before the fix is `bed21e7`.
**History note:** On 17 Nov 2026, on the owner's GO, the repo history was rewritten to remove a private individual's name. All SHAs changed, and earlier SHAs (such as `c4f6e11` and `11d96ba`) no longer exist on any branch.
**Out of scope:** Purging the GitHub-held PR refs from before the rewrite, and removing already-cached copies from search engines.
