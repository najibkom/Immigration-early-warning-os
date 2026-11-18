# Scoring model (Layer 3)

The engine is `scripts/score.py` in the plugin. Never compute a score by hand in prose: run the script.

## Sub-indices (0–100 each)

| Vector | Key | Default weight | What feeds it |
|---|---|---|---|
| Social signal | `social` | 0.25 (w1) | Aggregate volume velocity, sentiment shift, search frequency on transit/displacement topics. Aggregate only, never individual posts |
| Economic stress | `econ` | 0.30 (w2) | Food prices, currency moves, unemployment, remittance flows |
| Environmental impact | `weather` | 0.25 (w3) | Drought indices, rainfall anomaly, floods, crop failure |
| Policy shift | `policy` | 0.20 (w4) | Official gazettes, decrees, visa or border rule changes |

Live weights are in `frameworks/weights.json`. The feedback skill changes them; nothing else does.

## Formula

S_total = w1·I_social + w2·I_econ + w3·I_weather + w4·I_policy

(Assumption: the source spec's Layer 3 section on S_total was not in the excerpt provided; a weighted sum of the four sub-indices is used. Change it here and in `score.py` if the full spec differs.)

## Cross-vector corroboration multiplier C

A vector "triggers" when its index is above 70.

| Vectors above 70 | C | Meaning |
|---|---|---|
| 0 | 1.00 | Neutral |
| 1 | 0.85 | Damping: single-vector signals are not trusted alone |
| 2 | 1.15 | Amplification |
| 3 or more | 1.30 | High confidence |

S_final = min(100, S_total · C)

## Anomaly detection

For each corridor the script reads `alerts/history.csv` and computes the 30-day and 90-day rolling means of S_final. If today's score is more than 2.5 standard deviations from the 30-day mean (needs at least 7 points), the signal is flagged and goes to an analyst even when the score is below 70.

## Hard rules

- Every score lists the Source IDs it rests on. No Source IDs, no score.
- Contradictory official texts (for example two decrees on the same border) force a human hold, whatever the score.
