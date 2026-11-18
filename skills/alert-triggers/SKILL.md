---
name: alert-triggers
description: Checks every alert trigger condition and decides each alert's severity (severe or moderate) and cadence (immediate, daily, weekly, monthly) — sudden social media spikes, trends rising for days or sustained over a week, critical or elevated risk scores, one-day score jumps, weekly highs, category jumps, high or medium surge outlooks, and migration figures up against a year ago — with cooldown and updates; and edits the trigger thresholds. Use when the user says "check the triggers", "any alerts today", "is there a social media spike", "make the alert more or less sensitive", "change the trigger for X", or in every scheduled daily, weekly and monthly run.
---

# Alert triggers

`frameworks/alert-triggers.json` holds the conditions; `scripts/triggers.py` checks them. Severity sets the handling, cadence sets how fast it goes out.

## Severity and cadence

| Trigger | Detects | Severity | Goes out |
|---|---|---|---|
| MEDIA-SPIKE-SEVERE | Social media volume today ≥ 3σ and ≥ +100% vs its 30-day mean | Severe | Immediately |
| MEDIA-SPIKE-MODERATE | Social media ≥ 2σ or +50% for 2+ days in a row | Moderate | Same day |
| MEDIA-SUSTAINED | 7-day social media mean ≥ +30% vs the previous 4 weeks | Moderate | Weekly |
| SCORE-CRITICAL | S_final ≥ 85 | Severe | Immediately |
| SCORE-ELEVATED | S_final 70–84 | Moderate | Same day |
| SCORE-JUMP | S_final +15 in one day (severe if it reaches 85) | Moderate | Same day |
| WEEK-HIGH | Weekly mean ≥ 70 or 3+ critical days (severe if mean ≥ 85) | Moderate | Weekly |
| WEEK-CATEGORY-JUMP | A category index +25 in a week | Moderate | Weekly |
| OUTLOOK-HIGH | 3-month outlook high (moved to same day if the surge is expected next period) | Severe | Monthly |
| OUTLOOK-MEDIUM | 3-month outlook medium | Moderate | Monthly |
| OUTCOME-RISE | Migration figures +30% vs a year ago (severe at +60%) | Moderate | Monthly |

**Handling:** severe → held for the analyst on duty (30-minute SLA) before any broadcast. Moderate → sent when every gate passes and auto-send is on, otherwise waits for approval.
One alert per corridor per check: the most severe trigger leads, the others are listed with it. Same corridor + trigger within 12 hours is suppressed unless the value moved more than 15% (then it goes out as an UPDATE).

## Social media input

Daily social media analyses (exports, monitoring reports, platform dashboards) are ingested as aggregate rows in `wiki/intel/media-daily.csv`: `date,corridor,indicator,value,source_id,notes`, e.g. `route_search_volume`, `migration_topic_mentions`, `negative_sentiment_share`. Totals and shares only; never posts or accounts. Before any media alert goes out, the Gate 2 noise check (football, festivals, a reused hashtag) runs; a spike explained by known noise is downgraded to moderate or dropped, with the reason.

## Run

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/triggers.py" --cadence day      # every day, after scoring
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/triggers.py" --cadence week     # after the weekly report
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/triggers.py" --cadence month    # after the monthly report + outlook
```

Output: `alerts/triggers/<date>-<cadence>.md/.json`, and `alerts/trigger-log.csv`.

For each alert in the output: run `alert-draft` with severity, cadence and the trigger evidence, then `alert-review`. Report in chat: severe first, then moderate, then how many were suppressed.

## Tuning

"Make social media alerts less sensitive", "alert me when arrivals are up 20%": edit the thresholds in `frameworks/alert-triggers.json`, show old → new, and add a line to the change log in `frameworks/scoring-model.md`. Never remove the human hold on severe alerts.
