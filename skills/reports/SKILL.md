---
name: reports
description: Produces the period reports and forward outlooks — weekly, monthly, quarterly (3-month), 6-month and annual reports looking back over the period (risk scores, category trends, migration figures vs previous period and vs a year earlier, alerts and accuracy), plus 3-, 6- and 12-month outlooks from the approved rulebook — and the weekly and monthly roll-up alerts. Use when the user says "weekly report", "monthly report", "quarterly report", "6-month report", "annual report", "outlook", "what's coming in the next 3/6/12 months", or when a scheduled run asks for one.
---

# Reports and outlooks

Read the `intel-brain` skill and `frameworks/report-templates.md`. Numbers come only from the scripts below; never compute them in prose.

## Which report

| Ask | Kind | Window | Outlook included |
|---|---|---|---|
| Weekly report | `week` | last complete ISO week | — |
| Monthly report | `month` | last complete month | 3 months |
| Quarterly (3-month) report | `quarter` | last complete quarter | 3 and 6 months |
| 6-month report | `half` | last complete half-year | 6 and 12 months |
| Annual report | `year` | last complete year | 12 months |
| Outlook only | — | as of the latest period | 3, 6 and 12 months |

The user can name another window ("report for Q2 2025"): pass `--end` with a date inside it.

## 1. Get the numbers

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/period_report.py" --kind <kind> [--end YYYY-MM-DD]
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/outlook.py" --horizons 3,6,12
```

These write `reports/<kind>/<label>.json` + `-data.md` and `reports/outlook/<as-of>.json` + `-data.md`.

## 2. Write the report

Follow the template for the kind in `frameworks/report-templates.md`. Save to `reports/<kind>/<label>.md`. Rules:
- Lead with the answer: the corridors that matter this period and why, in three lines.
- Tables come from the `-data.md` files unchanged. Narrative explains them, citing Source IDs for causes.
- Compare with the previous period and with the same period a year earlier where data exists.
- Outlook section: the signal level per corridor and horizon, the rules behind it with their evidence lines, and the coverage note ("rules look at most N months ahead"). "No signal" never means "nothing will happen".
- Charts: if the user wants a shareable page, publish the report as a Dashboard artifact (trend of S_final, category indices, outcomes vs year ago).

## 3. Review and send

Run `alert-review` on the report (Gate 2 grounding and language checks apply to reports too). Reports are informational: when they pass, send them to the report recipients in `CLAUDE.md` through the connected channel, or keep them in `reports/` and say where they are. Log the send in the daily log.

## 4. Roll-up alerts (weekly and monthly cadence)

Run `alert-triggers` with `--cadence week` after the weekly report and `--cadence month` after the monthly report and outlook; it applies the conditions below (thresholds live in `frameworks/alert-triggers.json`).

After the weekly report, raise a **weekly alert** for any corridor where at least one is true:
- mean S_final for the week ≥ 70, or 3+ days at Critical;
- mean S_final up 15 points or more vs the previous week;
- a category index up 25 points or more vs the previous week.

After the monthly report, raise a **monthly alert** for any corridor where:
- the 3-month outlook signal is **high** or **medium**; or
- migration figures are up 30% or more vs the same month a year earlier; or
- the month's mean S_final ≥ 70.

Draft each with `alert-draft` (type WEEKLY or MONTHLY roll-up, with the triggering condition named) and run `alert-review`. Routing follows `frameworks/routing-matrix.md`: an outlook alert with a high signal is handled like Elevated; anything containing a Critical score is held for the analyst.
