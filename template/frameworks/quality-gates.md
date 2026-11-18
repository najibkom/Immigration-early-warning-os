# Quality gates

Three gates. A gate recommends; a human decides at Gate 2 holds. Nothing is broadcast because the model said so.

## Gate 1: Ingestion integrity (ingest skill)

| ID | Check | Fail action |
|---|---|---|
| G1.1 | Every record has a `correlation_id` (UUIDv4) | Assign one |
| G1.2 | SHA-256 hash of the source content is not already in `wiki/intel/signals-index.csv` | Mark duplicate, skip |
| G1.3 | Record matches `frameworks/signal-schema.json` (required fields present, types right) | Quarantine to `raw/_quarantine/` with the reason |
| G1.4 | Source is in `wiki/intel/sources.csv` and not `DEGRADED` | Register it first or quarantine |
| G1.5 | PII scrubbed: no individual names, street addresses, phone numbers, IPs or user handles of private persons | Redact before saving |
| G1.6 | Social signals stored as aggregates only (volumes, percentages, trends) | Rewrite as aggregate or reject |

## Gate 2: Grounding and logic audit (alert-review skill, before scoring is published)

| ID | Check | Must pass |
|---|---|---|
| G2.1 | Every factual sentence in the summary cites a Source ID from `sources.csv` | Yes |
| G2.2 | No number, date, place or decree appears that is not in a cited source | Yes |
| G2.3 | Score was produced by `score.py`, and the JSON output is attached | Yes |
| G2.4 | Noise filter: social spike checked against baseline viral dynamics (sport, pop culture, a hashtag reused for something else) | Yes |
| G2.5 | Single-vector alerts say so and carry the 0.85 damping | |
| G2.6 | Contradictory official texts named and the item held | Yes |
| G2.7 | S_final ≥ 85 → human hold, 30-minute review SLA, nothing goes out until approved | Yes |
| G2.8 | Language is neutral and protection-oriented: describes conditions and needs, never stigmatises a group | Yes |

## Gate 3: Delivery assurance and feedback (alert-review, alerts-board, feedback skills)

| ID | Check |
|---|---|
| G3.1 | Cooldown: no other alert for the same corridor + driver in the last 12 hours, unless the score moved more than 15% |
| G3.2 | Channel matches the tier in the routing matrix |
| G3.3 | Delivery confirmed (200 OK, or a sent note); a failed Critical delivery escalated |
| G3.4 | Feedback choice attached; feedback logged in `alerts/feedback.csv` |
| G3.5 | Repeated false positives from one source lower its credibility in `sources.csv` and trigger a weight recalibration |
