---
name: score-signal
description: Computes the composite risk score for a corridor with the Layer 3 engine — weighted sub-indices (social, economic, environmental, policy), cross-vector corroboration multiplier, S_final, 2.5-sigma anomaly check against the 30-day baseline, risk tier and routing — and logs it. Use when the user says "score the corridor", "run the scoring", "what's the risk level for X", or after ingest moves an index.
---

# Score signal (Layer 3)

Never compute a score in prose. Always run the engine.

Read `frameworks/scoring-model.md`, `frameworks/routing-matrix.md` and the `intel-brain` skill first.

## 1. Set the sub-indices

For the corridor, each of the four indices is a 0–100 value. Get them, in order of preference:
1. Given directly by the user or an upstream pipeline export.
2. Derived from the latest records in `wiki/intel/signals/` against the dossier's baselines. Show how each index was set (indicator, value, baseline, mapping to 0–100) and the Source IDs, and ask the user to confirm before scoring.

If a vector has no data, say so and use 0 for that index unless the user gives a value; note it as a data gap.

## 2. Run

Write the input to `alerts/drafts/<YYYY-MM-DD>-<corridor>-input.json`:

```json
{"corridor": "<slug>", "indices": {"social": 0, "econ": 0, "weather": 0, "policy": 0},
 "source_ids": ["SRC-..."], "contradictory_policy": false}
```

Then:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/score.py" alerts/drafts/<file>-input.json \
  --weights frameworks/weights.json --history alerts/history.csv \
  > alerts/drafts/<YYYY-MM-DD>-<corridor>-score.json
```

## 3. Log and route

- Append to `alerts/history.csv`: `date,corridor,s_final,tier,top_driver,correlation_id` (new UUIDv4 for the scoring event). One row per corridor per day; if today's row exists, ask before adding a second.
- Report in chat, five lines: S_final and tier, top driver and contributions, C and why, anomaly result, routing action.
- Route by tier:
  - **0–39**: done. Logged only.
  - **40–69**: add to "Watchlist queue" in `alerts/board.md`.
  - **70–84**: offer `alert-draft` now.
  - **85–100** or `hitl_required: true`: run `alert-draft` with status HELD, then `alert-review`. Nothing goes out before a human approves.
  - **Anomaly flag** at any tier: offer an analyst note via `alert-draft`.
- Update the corridor's row on the board (or run `alerts-board`).
