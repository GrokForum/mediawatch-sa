# RFC-CHG-MW-003 — Nightly build, publish and live check (DEV)

**Status:** Pushed as PR #4 (`dev/chg-mw-003-nightly`). Under review (reviewer A, reviewer B). Not merged; not deployed. This RFC does not change GitHub Pages settings, DNS, or indexing.  
**Environment:** DEV — branch `dev/chg-mw-003-nightly` (used instead of `rfc/<ver>` to match the project's existing `dev/chg-mw-*` naming).  
**Pre-change SHA (rollback base):** `8294282db5e2e9774e89695e8b75e0e4c16a759b` (`main` after PR #3).  
**Date:** 19 Nov 2026 (Africa/Johannesburg)  
**Repo:** https://github.com/GrokForum/mediawatch-sa (PUBLIC). Production URL (unchanged by this RFC): https://mediawatch.grokforum.site

---

## Environment plan

| Env | What it is | Points at production? |
|-----|------------|------------------------|
| DEV | This local branch. Workflow and `scripts/check_live.py` can be inspected and unit-tested with a local HTTP fixture. | No. The unit tests never fetch the live domain. |
| TEST | Not stood up (RFC-CHG-MW-002 open question e). | — |
| PROD | GitHub Pages, already deploying from `.github/workflows/pages.yml` on `main` at `8294282`. A merge of this RFC would add a nightly run of that same workflow, plus a post-deploy live check against the live domain. | Only after a later, named deployment RFC with the owner's own GO on the exact head. |

---

## Goal

Close Phase 0 audit finding **B2** for MediaWatch: the Pages workflow only ran on `push` and `workflow_dispatch`, so the nightly streak was 0. Add a scheduled rebuild and deploy, and after each successful deploy run a live check that records its result for that night.

---

## What changes (exact files)

| File | Change |
|------|--------|
| `.github/workflows/pages.yml` | Add a `schedule` trigger (cron `30 1 * * *`, 03:30 Africa/Johannesburg). Add a `live_check` job that runs after `deploy`, writes `live-check.json`, appends it to the job summary, and uploads it as an artifact. Both `actions/checkout` steps set `persist-credentials: false`. The `live_check` job has only `contents: read` (no `actions: write`). |
| `scripts/check_live.py` | **New.** Stdlib-only checker (see Checks). |
| `tests/test_check_live.py` | **New.** Fixture HTTP server for the checker; workflow pin, permission and trigger tests. |
| `changes/RFC-CHG-MW-003.md` | This record. |
| `requirements.txt` | Pin `PyYAML==6.0.2`. `tests/test_check_live.py` imports `yaml`, and CI installs only this file. |
| `docs/STATUS.md` | Change-log row for this RFC. |

**What stays:** the build and deploy jobs, their pinned action SHAs, the noindex / robots / allowed-file-type gates, the generator, the data files, `robots.txt`, the DRAFT banner, and all Pages settings. Indexing stays off. Reviewers are reviewer A and reviewer B.

---

## Why a schedule on `pages.yml`, not a second workflow

One workflow keeps a single concurrency group (`pages`) and a single deploy path. A second workflow would either duplicate the build/deploy steps or have to `workflow_dispatch` this one, with two places to keep pins and permissions in sync. The nightly is the same build that a push already runs, plus the live check, which also runs after push and manual deploys so those are recorded too.

Schedule: **03:30 Africa/Johannesburg** (`30 1 * * *` UTC). South Africa has no daylight-saving change. PublicFunds' nightly is about 03:20 SAST; 03:30 keeps MediaWatch close without sharing the exact minute.

---

## How the result is saved: an artifact, not a commit to `main`

**Choice: upload `live-check.json` as a GitHub Actions artifact** named `live-check-${{ github.run_id }}`, retention 90 days (the maximum for a public repository). The same JSON is appended to the job summary, which stays with the workflow run.

**Why not commit the log to `main`:** that would need `contents: write` on the default branch. A nightly bot-commit would also retrigger `on: push` and could loop. The owner's standing rule is that a push to the public repo needs the owner's own GO on the exact head; a workflow that writes to `main` would bypass that.

**Why not a `nightly-logs` branch:** still `contents: write` (even if scoped by a carefully written push), more moving parts, and a second history to keep private-name clean. Not justified for a 14-day Phase 0 streak.

**Trade-off, recorded:** artifacts on a public repo expire after 90 days. That covers the 14-day Phase 0 window and a long review margin, but it is not a permanent register. A later RFC can add a logs branch or an external store if the owner wants a permanent trail; this RFC does not.

The `live_check` job has only `contents: read`. It has no `actions: write`, no `pages: write`, no `id-token`, and no `contents: write`. The workflow-level permission stays `contents: read`. Both checkout steps set `persist-credentials: false`, so the job does not keep a `GITHUB_TOKEN` in the local git config.

`actions/upload-artifact` (pinned at v7.0.2) uploads with the runner-injected `ACTIONS_RUNTIME_TOKEN`, not `GITHUB_TOKEN`. It does not need the `actions` scope on `GITHUB_TOKEN`. (`contents: read` is still required so the job can check out `scripts/check_live.py`.)

---

## Checks

`scripts/check_live.py` GETs `https://mediawatch.grokforum.site` (or `--base-url`) with the User-Agent `MediaWatch-SA-live-check/1.0`. After a Pages deploy it retries for `--wait` seconds (300 in the workflow) so a CDN lag is not a false fail. It always writes the JSON, then exits 0 on PASS and 1 on FAIL.

| Check | Pass rule |
|-------|-----------|
| `home_200` | `GET /` is 200, the page contains `<meta name="robots" content="noindex, nofollow">`, and a visible DRAFT marker (`Draft preview (DEV)` or `MediaWatch SA (draft)`). |
| `robots_disallow` | `GET /robots.txt` is 200 and the body is exactly `User-agent: *\nDisallow: /\n`. |
| `noindex:` for `/`, `/method/`, `/coverage/`, `/corrections/`, `/p/news24/` | 200 and the same noindex meta. |
| `forbidden_404:` for `/data`, `/data/`, `/docs`, `/docs/`, `/plan`, `/plan/` | Final status 404 (INC-MW-001). |

The JSON records `checked_at_sast`, `git_sha`, `run_id`, `event`, `attempts`, `verdict`, and per-check status codes. It does not store full HTML bodies.

A failed live check turns the workflow red. It does **not** roll back the deploy automatically (the job has no write access to Pages or to `main`). Rollback remains git: revert the merge, or restore the Pages source from tag `snapshot-2026-11-17-pre-mw-pr3` (`d1029af`), each with the owner's GO.

**Known limitation:** until a public build stamp exists (proposed in CHG-MW-004), a slow new deploy can be checked against the previous successful one if that previous site already passes. The wait/retry reduces this; it does not eliminate it. This RFC does not add a manifest.

---

## Tests and how success is proven (DEV)

- `uv run -q --no-project --with-requirements requirements.txt python -m pytest -q -rs` — including the local denylist test. `PyYAML==6.0.2` is pinned in `requirements.txt` (CI installs only that file).
- New tests: fixture server PASS and FAIL cases (wrong robots, `/data` served as 200, missing noindex only, missing DRAFT only); workflow has the schedule, the `live_check` job, no `contents: write`, no `actions: write`, `persist-credentials: false` on both checkouts, pinned 40-character action SHAs, 90-day artifact retention. The home-page DRAFT and noindex guards are tested in separate fixtures so each fails on its own.
- `github.sha`, `github.run_id` and `github.event_name` used by the live-check `run:` step are passed through `env:` (`GIT_SHA`, `RUN_ID`, `EVENT_NAME`) and referenced as shell variables, so the script cannot be rewritten by template injection.
- A local `scripts/build_site.py` build still has noindex on every HTML page, exact `robots.txt`, and only the already-allowed file types (this RFC adds none).

## Rollback

```
git checkout main
git revert <merge-commit-of-this-RFC>
```

Or, before merge, delete the branch. Pre-change SHA: `8294282db5e2e9774e89695e8b75e0e4c16a759b`. This RFC does not change Pages settings, so rolling back the workflow is enough to return to push/manual deploys only.

## Seen, not touched

- Phase 0 findings this RFC does **not** close: H1 (privacy page and contact — CHG-MW-005; the contact placeholder stays until the owner confirms an address), H3 (public data manifest — CHG-MW-004), M4 (no CSP meta), L2 (favicon.ico 404), L4 (one 4.0 s sample). TenderWatch and PoliticianWatch items, and all PublicFunds items, belong to those bots.
- The corrections contact placeholder is unchanged.
- RFC-CHG-MW-002 open questions (a)–(j) stay with reviewer A and the owner.
- `/privacy/` is not in the live-check `SAMPLE_PATHS` on this branch. Until CHG-MW-005 is deployed the live site has no `/privacy/` page, and adding that path here would turn the nightly red. CHG-MW-005 will add it.

- `pages-build-deployment` still appears in the Actions list as GitHub's legacy Pages job; `build_type` is already `workflow`. Not changed.
- Source-link gaps on published claims (owner group has no source URL field; editor source URLs are in the data but not rendered) are reported with CHG-MW-004, not fixed here.
- No search-engine indexing request, no `contents: write`, no merge, no Pages settings change, no deploy. The branch has been pushed as PR #4 and is under review.

## Sign-off

Author: the bot. Sign-off is by someone other than the author. Reviewers: reviewer A and reviewer B. The branch has been pushed as PR #4. Owner GO is required before merge or deploy.
