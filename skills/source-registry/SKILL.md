---
name: source-registry
description: Registers, rates and maintains the pipeline's sources in wiki/intel/sources.csv — Source IDs, category, type, collection method, language, refresh rate, credibility score and status (ACTIVE, DEGRADED, RETIRED), including credibility cuts after repeated false positives. Use when the user says "add a source", "register this gazette", "which sources do we have for drought", "mark this scraper degraded", or when ingest or corridor-profile proposes new sources.
---

# Source registry

`wiki/intel/sources.csv` is the single list of what the pipeline is allowed to cite.

## Columns

`source_id, name, category, type, url, method, language, refresh, credibility, status, false_positives, notes`

- `source_id`: next free `SRC-NNN`. Never reuse or renumber.
- `type`: government · un-agency · ngo · statistics · research · media · social-aggregate · satellite · market-data
- `method`: api · scrape-html · scrape-pdf · rss · manual · dataset-download · partner-feed
- `credibility` (0–1), starting values: government gazette or statistics office 0.9 · UN agency 0.85 · peer-reviewed or established research 0.8 · international NGO 0.75 · national media 0.6 · social aggregate 0.5 · unknown 0.4. Note why if you depart from these.
- `status`: ACTIVE · DEGRADED (parsing failures, layout drift, stale) · RETIRED

## Add

Collect the fields (ask only for what you cannot find), check the source is not already listed (same URL or name), append the row, confirm with the new ID. Remove the `EXAMPLE` row once a real source exists, after asking.

## Review

On "review sources": list by category (econ, env, politics, social, media, other, plus outcome sources) with counts, flag categories with fewer than two ACTIVE sources, DEGRADED sources, and sources not refreshed within twice their refresh period.

## Credibility cuts (called by feedback)

When a source reaches 3 false positives in 30 days in `alerts/feedback.csv`: lower its credibility by 0.1 (floor 0.2), add a dated note, tell the user. At credibility below 0.4, ask whether to retire it.

## Degraded

When a scraper or feed fails repeatedly: set `DEGRADED`, add the date and issue in notes, add the row to "Source health" in `alerts/board.md`, and add a maintenance task to `projects/pipeline-build.md`.
