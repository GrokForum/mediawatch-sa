# LATER: parked ideas

Ideas not worth tackling yet. Each line names what it is and why it waits. Nothing here is scheduled. An item moves into a named RFC only on the owner's GO.

## Hardening (from Phase 0 reviews)
- **DRAFT title marker:** check_live's visible-text parser does not skip `<title>`, so a page whose only DRAFT marker is the title passes. Skip head and title, or drop the title marker, and add a title-only test.
- **CHG-MW-006 PR CI:** a test-only `pull_request` workflow (contents: read, no secrets, no deploy) so PRs show checks before merge.
- **MANIFEST_INPUTS:** review which input files the manifest hashes, and keep that list in one place.
- **/privacy/ in the live-check sample:** a one-line follow-up once #4 and #6 are both on main.
- **CSP meta tag (audit item M4):** add a Content-Security-Policy tag so pages only load scripts and styles from the site itself.
- **favicon.ico (audit item L2):** add a small site icon; browsers ask for it and it currently returns 404.
- **Owner-group sources:** publications.csv has no source URL for owner groups (e.g. "Media24 / Naspers"). Add a source field and link it.
- **Supporting sources without URLs:** some editor_source_url notes mention sources with no link. Find and link them.

## Data and method (open owner decisions)
- Daily Investor and Newsday unofficial driver names: the 2 xfails, pending a decision.
- Actor-name normalisation (e.g. "Ramaphosa" vs "Cyril Ramaphosa").
- people.csv is missing 4 News24 bylines, and some writers have no page.
- The write_*_pilot.py scripts hard-code a local path.
- RFC-002 open questions (a) to (j).

## Product
- One site aggregating all four watch sites, through the public directory at watch.grokforum.site.
- Widen the window beyond May to Oct 2026 for more data points, and add the live monthly intake from November.
- Roll out to more publications beyond the three pilots, following the coverage plan.
- Journalists' own public posts (X) as their own evidence stream.

## Reviewer B round 3 follow-ups (non-blocking)
- Require the visible DRAFT banner itself, not just any DRAFT marker. This goes with the title-marker fix.
- Make the visible-text parser skip template, textarea and noscript.
- Add live-check mutations for nofollow and for the exception paths.
- Parse the robots meta in test_site too, not by substring.
- Scan visible text for emails, catching addresses split across tags and spaced "@" variants.
