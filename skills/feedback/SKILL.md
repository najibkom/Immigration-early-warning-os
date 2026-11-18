---
name: feedback
description: Runs the closed-loop feedback of Quality Gate 3 — logs analyst verdicts on sent alerts (Accurate, False Positive, Irrelevant), lowers the credibility of sources with repeated false positives, lowers the driving category's weight by 2% (renormalised), flags rulebook rules that keep firing without a surge, and reports accuracy. Use when the user says "log feedback", "this alert was a false positive", "recalibrate the weights", or "how accurate have alerts been".
---

# Feedback and recalibration

## Log a verdict

1. Identify the alert in `alerts/sent/` (by correlation ID, corridor or date).
2. Record the verdict: Accurate · False Positive · Irrelevant, the analyst, and a note.
3. Append to `alerts/feedback.csv`: `date,correlation_id,corridor,top_driver,source_ids,verdict,analyst,note,action_taken`. Put the IDs of rules that fired (from the alert's score JSON) in `note` as `rules=R-..`.

## On a False Positive

1. **Weight**: propose lowering the top driver category by 2% (relative), the others renormalised. Show old → new. On confirmation:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/recalibrate.py" frameworks/weights.json --lower <econ|env|politics|social|media|other> --pct 2
   ```

   Add a line to the "Change log" in `frameworks/scoring-model.md`.
2. **Sources**: count false positives per Source ID in the last 30 days of `feedback.csv`. At three or more, hand to `source-registry` for a credibility cut.
3. **Rules**: count false positives per rule ID over 90 days. At three or more, propose setting that rule to `"status": "retired"` in `frameworks/rulebook.json` (or raising its threshold), and suggest a `learn-rules` re-run.
4. **Noise**: if the analyst names a cause (football final, festival, hashtag reuse), propose adding it to the corridor dossier's "Known noise".
5. Write what was done in `action_taken`.

Never change weights or rules without the user confirming, and never by more than 2% per verdict. If weights drift more than 10 points from the last approved `learn-rules` weights, flag it and suggest a re-run of `learn-rules` instead of more manual nudges.

## Accuracy report

On request: precision by corridor, by category and by rule (Accurate ÷ all verdicts), counts per verdict, sources with the most false positives, weight and rulebook changes over the period. Computed in code from `feedback.csv`.
