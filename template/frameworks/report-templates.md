# Report templates

All numbers come from `period_report.py` and `outlook.py`. Lead with the answer; cite Source IDs for every cause.

## Daily summary (every day, 5 lines)
1. Highest corridor today: score, tier, main driver.
2. Biggest mover since yesterday.
3. Alerts: sent / held / suppressed by cooldown.
4. Rules fired today.
5. Source or ingest problems.

## Weekly report
1. The week in three lines.
2. Risk scores by corridor (table): mean, max, last, change vs last week, critical and elevated days.
3. What moved: categories with the largest change, with sources.
4. Alerts sent and feedback received.
5. Watch next week: corridors close to 70, rules close to firing.

## Monthly report
1. The month in three lines.
2. Risk scores by corridor vs last month and vs the same month last year.
3. Category trends (six categories) with causes.
4. Migration figures vs last month and vs a year ago.
5. **3-month outlook**: signal per corridor, expected surge months, rules and evidence.
6. Alerts and accuracy.

## Quarterly (3-month) report
1. The quarter in five lines.
2. Scores, categories and migration figures vs last quarter and vs the same quarter last year.
3. Which rules fired, and whether surges followed (rule performance).
4. **3- and 6-month outlooks**.
5. Rulebook proposal from the quarterly `learn-rules` run, awaiting approval.
6. Sources: coverage gaps, degraded sources, credibility changes.

## 6-month report
1. The half-year in five lines, for the funder or leadership.
2. Corridor comparison: average risk, critical periods, migration totals vs the previous half and a year ago.
3. Lead indicators that mattered most, with lags.
4. **6- and 12-month outlooks**.
5. Accuracy: alerts by verdict, false-positive causes, changes made.
6. Recommendations for the next half: corridors, sources, playbooks.

## Annual report
1. The year in one paragraph.
2. Year-on-year tables per corridor: risk, categories, migration figures.
3. Early-warning performance: surges anticipated vs missed, average warning time.
4. Rulebook and weight changes over the year.
5. **12-month outlook**.
6. Governance: holds, SLA compliance, data-protection checks.

## Roll-up alerts
- **WEEKLY ALERT** — corridor, the triggering condition (weekly mean ≥ 70, 3+ critical days, +15 points, or a category +25), drivers, sources, playbook.
- **MONTHLY ALERT** — corridor, the triggering condition (3-month outlook high/medium, migration +30% vs a year ago, or monthly mean ≥ 70), expected surge months, rules and evidence, playbook.
