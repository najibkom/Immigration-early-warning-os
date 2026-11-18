# Scoring model (Layer 3), v0.2

The engine is `scripts/score.py` in the plugin. Never compute a score by hand in prose: run the script.

## Six categories (each indexed 0–100)

| Category | Key | Default weight | What feeds it |
|---|---|---|---|
| Economy, incl. employment and SMEs | `econ` | 0.25 | Youth unemployment, SME closures, food prices, currency, remittances |
| Weather and environment | `env` | 0.20 | Drought index, rainfall anomaly, floods, harvest loss |
| Politics and security, incl. protests and conflict | `politics` | 0.20 | Decrees, visa/border changes, protest events, conflict events |
| Social and health, incl. disease | `social` | 0.15 | Disease outbreaks, service disruption, school closures |
| Social media trends (aggregate only) | `media` | 0.15 | Search volume on routes/visas/jobs abroad, topic mentions, sentiment shares |
| Other | `other` | 0.05 | Anything relevant outside the five; not counted for corroboration |

An index is the percentile of the period's indicators within their own history (`scripts/to_index.py`): 0 = calmest period seen, 100 = most extreme. Live weights are in `frameworks/weights.json`; `learn-rules` (with approval) and `feedback` change them.

## Formula

1. Base score = Σ weight × index over the six categories.
2. Rule bonus = sum of points of every **approved** rule in `frameworks/rulebook.json` whose conditions are met (conditions can look back several periods in `wiki/intel/features.csv`). Capped at 20.
3. S_total = min(100, base + bonus).
4. Corroboration multiplier C, counting categories above 70 (excluding "other"): 0 → 1.00 · 1 → 0.85 · 2 → 1.15 · 3+ → 1.30.
5. S_final = min(100, S_total × C).

(Assumption: the original spec's S_total section was not in the excerpt provided; this weighted sum + rulebook is used. Change it here and in `score.py` if the full spec differs.)

## Learning loop

`history-load` builds `indicators.csv` → `features.csv` and `outcomes.csv`. `learn-rules` runs `scripts/learn.py`: lagged correlations and rule candidates, learned on the oldest 70% of periods and tested on the newest 30%. A human approves rules and weights. Re-run quarterly.

## Anomaly detection

30-day and 90-day rolling means of S_final per corridor from `alerts/history.csv`. More than 2.5σ from the 30-day mean (at least 7 points) → analyst review, even below 70.

## Hard rules

- Every score lists the Source IDs it rests on. No Source IDs, no published score.
- Contradictory official texts force a human hold, whatever the score.
- Only approved rules count. Draft and retired rules are ignored.

## Change log

| Date | What changed | Evidence | Approved by |
|---|---|---|---|
