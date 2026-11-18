---
name: feedback
description: Runs the closed-loop feedback of Quality Gate 3 — logs analyst verdicts on sent alerts (Accurate, False Positive, Irrelevant), lowers the credibility of sources with repeated false positives, and recalibrates the sub-index weights (minus 2% on the driving vector, renormalised) with a recorded change history. Use when the user says "log feedback", "this alert was a false positive", "recalibrate the weights", or "how accurate have alerts been".
---

# Feedback and recalibration

## Log a verdict

1. Identify the alert in `alerts/sent/` (by correlation ID, corridor or date).
2. Record the verdict: Accurate · False Positive · Irrelevant, the analyst, and a note.
3. Append to `alerts/feedback.csv`: `date,correlation_id,corridor,top_driver,source_ids,verdict,analyst,note,action_taken`.

## On a False Positive

1. **Weight**: propose lowering the top driver's weight by 2% (relative), with the others renormalised to sum to 1. Show old → new. On confirmation:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/recalibrate.py" frameworks/weights.json <vector> --pct 2
   ```

   Add a dated line to the "Weight changes" table at the end of `frameworks/scoring-model.md` (create the table if missing): date, vector, old, new, correlation ID, analyst.
2. **Sources**: count false positives per Source ID in the last 30 days of `feedback.csv`. At three or more, hand to `source-registry` for a credibility cut.
3. Write the action in `action_taken`.

Never change weights without the user confirming, and never by more than 2% per verdict. If weights drift more than 10 points from the defaults in total, flag it and suggest a review with the client.

## Accuracy report

On request: precision by corridor and by vector (Accurate ÷ all verdicts), counts per verdict, sources with the most false positives, weight changes over the period. Computed in code from `feedback.csv`.
