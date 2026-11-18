---
name: score-signal
description: Computes the composite risk score for a corridor and period with the Layer 3 engine — six category indices (economy, environment, politics and security, social and health, social media, other), learned weights, approved rulebook rules that look back over past periods, the corroboration multiplier, S_final, a 2.5-sigma anomaly check, risk tier and routing — and records the period in the historical base. Use when the user says "score the corridor", "run the scoring", "what's the risk level for X", "weekly scoring", or after ingest moves an index.
---

# Score signal (Layer 3)

Never compute a score in prose. Always run the engine.

Read `frameworks/scoring-model.md`, `frameworks/routing-matrix.md` and the `intel-brain` skill first.

## 1. Set the six indices for this period

Period = the current month (`2026-11`) or week (`2026-W47`), matching the granularity in `CLAUDE.md`.

Preferred way, the same method as the history so the rules stay valid:
1. Add this period's indicator rows (from newly ingested records) to `wiki/intel/indicators.csv`, using the same indicator names as the history.
2. Rebuild the indices: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/to_index.py" wiki/intel/indicators.csv --out wiki/intel/features.csv --merge`
3. Read this period's row from `features.csv`.

If there is no history yet, set each index by judgement against the corridor dossier's baselines, show how (indicator, value, baseline, 0–100) with Source IDs, and ask the user to confirm. The user can also give indices directly.

A category with no data: say so; it is scored 0 and reported as a data gap.

## 2. Run

Write `alerts/drafts/<YYYY-MM-DD>-<corridor>-input.json`:

```json
{"corridor": "<slug>", "period": "2026-11",
 "indices": {"econ": 0, "env": 0, "politics": 0, "social": 0, "media": 0, "other": 0},
 "source_ids": ["SRC-..."], "contradictory_policy": false}
```

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/score.py" alerts/drafts/<file>-input.json \
  --weights frameworks/weights.json --rulebook frameworks/rulebook.json \
  --features wiki/intel/features.csv --history alerts/history.csv --record \
  > alerts/drafts/<YYYY-MM-DD>-<corridor>-score.json
```

Use `--record` only when the indices were not already written to `features.csv` by `to_index.py` in step 1 (judgement or user-given indices), so the period becomes history for future rules.

## 3. Log and route

- Append to `alerts/history.csv`: `date,corridor,s_final,tier,top_driver,correlation_id` (new UUIDv4). One row per corridor per day; ask before adding a second.
- Report in chat, six lines: S_final and tier; base score and top driver; **rules fired** in plain words with their evidence ("drought was 87 in July, 4 months ago: rule R-ENV-04, +10"); C and why; anomaly; routing action. Mention `rules_not_checked` if history is missing.
- Route by tier:
  - **0–39**: logged only.
  - **40–69**: add to "Watchlist queue" in `alerts/board.md`.
  - **70–84**: offer `alert-draft`.
  - **85–100** or `hitl_required`: run `alert-draft` with status HELD, then `alert-review`. Nothing goes out before a human approves.
  - **Anomaly flag**: offer an analyst note via `alert-draft`.
- Update the corridor's row on the board.
