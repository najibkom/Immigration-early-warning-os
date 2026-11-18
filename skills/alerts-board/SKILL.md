---
name: alerts-board
description: Shows and refreshes the Alerts board — every corridor with its latest S_final, tier, delta vs the 30-day mean, top driver, anomaly flag, status and next step, plus pending human-review holds with SLA timers, the weekly watchlist queue and source health — and can render it as a dashboard page. Use when the user says "show the board", "where are all corridors", "what's held", "pipeline status", or "make a dashboard".
---

# Alerts board

`alerts/board.md` is the one view of the whole pipeline.

## Refresh

1. For each corridor dossier in `wiki/intel/corridors/` (skip `_template.md`), take the latest row in `alerts/history.csv`. Compute in code the delta against the 30-day mean.
2. Holds: every file in `alerts/held/` not yet approved or rejected, with `held_since`, `sla_due` and minutes remaining (negative = breached).
3. Watchlist: corridors scored 40–69 in the last 7 days not yet in a sent digest.
4. Source health: rows in `wiki/intel/sources.csv` with status DEGRADED.
5. Next step per corridor: one short action (re-score, ingest new data, draft alert, approve hold, update dossier).
6. Rewrite `alerts/board.md` with "As of" in UTC.

## Show

In chat: holds first (breached SLA in bold), then corridors at 70+, then a count of the rest. Eight lines at most; the full table is in the file.

## Dashboard page

If asked for a dashboard or a shareable view, build it from the board data as a dashboard artifact (corridor scores, tier colours, trend from `history.csv`, holds). Region-level only, no personal data, governance note in the footer.
