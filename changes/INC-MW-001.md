# INC-MW-001: draft files publicly served by GitHub Pages

**Status:** PENDING owner GO (prepared locally, not pushed)
**Found:** 17 Nov 2026, about 11:05 SAST, while building CHG-MW-002.
**Impact:** After the PR #1 merge (`c4f6e11`), the legacy Pages build serves the whole repo root. `/data/lean_scores_draft.json` (the hidden lean meter), `/data/news24_pilot_findings.json`, `/docs/*` and `/plan` return HTTP 200. There is no `robots.txt`.
**Fix:** A root `_config.yml` that excludes `data/`, `docs/`, `changes/`, `scripts/`, `tests/`, `plan.md` and `README.md` from the Pages build, plus a root `robots.txt` that disallows all crawlers. `index.html` and `CNAME` are untouched.
**Verify after push:** The paths above return 404, `/robots.txt` returns 200, and `/` still shows the placeholder.
**Rollback:** `git revert` this commit, or reset main to `c4f6e11`.
**Out of scope:** The surname in `d3ca635` history (the owner's call, via Cavus), and removing already-cached copies from search engines.
