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

## Next publications (parked until the coverage-gate is passed)

Phase 2 on this branch codes a locked `neutral_random_v1` sample for Daily Maverick, GroundUp and The Citizen only, and shows those findings behind the coverage gate (no published scores until the owner signs off that the pilot has been reviewed). These outlets are **not** in that phase-2 trio. They wait.

- **Mail & Guardian (`mail_guardian`, mg.co.za).** A major national weekly in the coverage plan's "major national dailies and weeklies" phase. Not in the locked v1 draw. Starts only after the phase-2 entry criteria are met and the owner names a sampling RFC.
- **IOL (`iol`, iol.co.za).** Independent Media. Already on the site only as an error-watch (findings-only rows under METHODOLOGY §5b). That watch is not a scored-pilot or phase-2 expansion. A full IOL sample would need a later RFC, after the pilot review and a free-access check (much of the site may not yield a large free sample).
- **Broadcasters' news sites:** eNCA (`enca`), SABC News (`sabc_news`), EWN (`ewn`), and Newzroom Afrika (`newzroom_afrika`). Coverage-plan phase 3. Entry is: phase 2 reaches minimum samples for its main actors, and a rule for transcripts and clips is agreed. EWN already has error-watch findings only; that is not a broadcaster sample. Audio and video are not coded from the v1 article draw.

No collector, draw, or finding for these outlets is added by CHG-MW-010 except the existing IOL/EWN watch files, which this change does not expand.
