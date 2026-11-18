---
name: learn-rules
description: Analyses the historical base to find which categories (economy, environment, politics and security, social and health, social media, other) moved before migration changed and by how many periods, tests candidate rules on held-out recent periods, proposes rules with confidence and evidence plus learned category weights, and after human approval writes them into the rulebook used by daily scoring. Use when the user says "learn the rules", "find correlations", "what predicts arrivals", "update the rulebook", "re-train", or for the quarterly re-run.
---

# Learn rules

Turn history into early-warning rules. The script proposes; a human approves; only approved rules change scores.

Needs `wiki/intel/features.csv` and `wiki/intel/outcomes.csv` (built by `history-load`). Read the `intel-brain` skill and `frameworks/scoring-model.md`.

## 1. Run the analysis

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/learn.py" --metric <metric> \
  --features wiki/intel/features.csv --outcomes wiki/intel/outcomes.csv \
  --weights frameworks/weights.json --max-lag 6 \
  --out drafts/rule-candidates-<YYYY-MM-DD>
```

Defaults: lags 0–6 periods, oldest 70% of periods to learn, newest 30% to test, "surge" = outcome above its 75th percentile, thresholds 60/70/80. Change them only if the user asks (e.g. `--max-lag 12` for slow climate effects).

What it computes, per corridor:
- **Lead indicators**: correlation between each category index and the outcome, at each lag, on learn and test periods.
- **Rules**: "category above X, L periods before → surge", alone and in pairs, kept if they fire at least 3 times with lift ≥ 1.5 when learning, then checked on test periods. Confidence: high (holds on test with lift ≥ 1.5, 3+ fires, 24+ periods), medium, low. Points: 10 / 6 / 3.
- **Proposed weights**: from correlations that hold on test, blended with current weights when history is short.

## 2. Explain it to the user

Open `drafts/rule-candidates-<date>.md`. In chat, eight lines at most:
- the strongest lead indicators with their lag in plain words ("drought leads arrivals by about 4 months on Morocco–Spain, and it held on 2024–2025 data"),
- the top three rule candidates with confidence,
- the proposed weight change,
- any warning: short history, a category with no data, a relationship that reversed on test.

Add a domain sanity check for each high or medium rule: is there a plausible mechanism (harvest loss → rural income loss → departures)? Flag rules with no plausible mechanism as "statistical only". Correlation is not causation; say so once.

## 3. Human approval

Ask: "Approve which rules? 1 All high · 2 Pick (give numbers) · 3 None" and "Apply the proposed weights? 1 Yes · 2 No".

On approval, for each chosen rule append to `frameworks/rulebook.json`:

```json
{"id": "R-<CAT>-<LAG>-<NN>", "name": "<plain words>", "status": "approved",
 "corridors": ["<slug>"], "conditions": [{"category": "env", "op": ">", "threshold": 80, "lag": 4}],
 "points": 10, "confidence": "high",
 "evidence": "rule-candidates-<date>: train lift 3.45 (8 fires), test lift 2.57 (4 fires), test precision 1.0",
 "approved_by": "<name>", "approved_on": "<YYYY-MM-DD>"}
```

Scope a rule to the corridor it was learned on unless it held on several corridors (then list them). Retire replaced rules by setting `"status": "retired"`; never delete. For weights:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/recalibrate.py" frameworks/weights.json --from drafts/rule-candidates-<date>.json
```

Log both changes in the "Change log" table of `frameworks/scoring-model.md` (date, what, evidence file, approved by).

## 4. Re-runs

Re-run every quarter, or when a quarter of new outcome data has arrived, or when feedback shows many false positives. Compare with the previous report: rules that weakened on new data are proposed for retirement.
