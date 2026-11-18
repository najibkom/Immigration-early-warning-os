---
name: shutdown
description: End-of-day reconciliation for the Early-Warning OS. Marks what got done, routes new commitments into project files, records open alert holds and source issues, and writes the daily log. Use when the user says "shutdown", "end of day", "wrap up", or "write today's log".
---

# Shutdown

Ask three questions in one message and wait:

1. What got done today?
2. What didn't, and why?
3. Any new commitments (client asks, partner follow-ups, deadlines)?

Then:

1. **Classify** each item: ✅ Done · 🔄 Partial (what remains) · ⏭️ Deferred (why).
2. **Route commitments** into the right `projects/*.md` under "Open tasks"; update `next_action`. Say which files changed.
3. **Pipeline status** from `alerts/board.md`: holds still pending (a hold past its 30-minute SLA is a red flag at the top of the log), alerts sent today, sources marked DEGRADED, feedback not yet logged.
4. **Decisions**: record decisions made today in the project files with the date.
5. **Roll forward**: top three priorities for tomorrow; prep needed.
6. **Save** `daily-logs/YYYY-MM-DD.md` (date from `date -u +%F`). One file per day. If it exists, append a new block separated by `---` with `# Session: YYYY-MM-DD (<label>)`; never overwrite.

Log structure:

```
# Session: YYYY-MM-DD (<label>)
## Done / Partial / Deferred
## Pipeline status (holds, alerts sent, source health)
## Decisions
## New commitments → routed to
## Tomorrow
```

Close with one line: where the log is and the top priority for tomorrow.
