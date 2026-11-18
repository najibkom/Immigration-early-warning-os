---
name: ingest
description: Processes current information dropped in raw/ (reports, decrees, datasets, social aggregates, source notes) through Quality Gate 1 — correlation IDs, SHA-256 deduplication, schema validation, PII redaction, quarantine — and files each item into the Intelligence Brain (signals, indicator rows, outcomes) with its taxonomy, corridor and category (past documents for learning go through history-load). Use when the user says "ingest", "process the inbox", "I dropped files in raw", or shares a new report, decree or dataset to add.
---

# Ingest (Layer 1 → Gate 1 → Layer 2)

Turn raw drops into clean, cited signal records. Propose first, file after the user confirms.

Read `frameworks/governance.md`, `frameworks/quality-gates.md` (Gate 1), `frameworks/signal-schema.json`, `wiki/intel/taxonomy.md` and `wiki/intel/sources.csv` before starting.

## 1. Inventory

List new files in `raw/` (anything not yet in `wiki/intel/signals-index.csv` by path or hash). Skip `raw/_quarantine/`. For each, compute the hash:

```bash
sha256sum "raw/<path>"
```

Read each file (PDF, CSV, HTML, text, images of documents). Large datasets: read the header and summarise in code, never paste rows.

## 2. Gate 1 per item

Run every check in Gate 1 (G1.1–G1.6):

- **Duplicate** (hash already indexed): report, skip.
- **Unknown source**: propose a new row for `sources.csv` (hand to `source-registry`), or quarantine.
- **PII**: redact names of private persons, handles, phone numbers, street addresses, IPs in anything you write. Never copy them into `wiki/` or `alerts/`. Public officials and institutions acting officially may be named.
- **Individual social posts**: convert to aggregate metrics (count, velocity, sentiment share) or reject.
- **Schema fail**: move to `raw/_quarantine/` with a sidecar `<file>.reason.md`.

## 3. Classify (Layer 2)

For each passing item propose: corridor (from `wiki/intel/corridors/`, or "new corridor?"), category (econ, env, politics, social, media, other), taxonomy codes, the aggregate metric with its baseline if known, and the indicator row(s) it gives for `wiki/intel/indicators.csv` (period, indicator name as used in history, value, direction), a one- or two-sentence neutral summary, confidence 0–1. Flag POL-CONF when two official texts contradict each other.

Show the proposals as one table: file · source · corridor · category · codes · summary · Gate 1 result. Ask: "File these? 1 All · 2 Some (say which) · 3 Change first".

## 4. File

On confirmation:
- Generate a UUIDv4 per record: `python3 -c "import uuid;print(uuid.uuid4())"`.
- Append one row per record to `wiki/intel/signals-index.csv`.
- Write the record as JSON to `wiki/intel/signals/<YYYY-MM>/<correlation_id>.json` (create folders as needed), matching the schema.
- Add a dated line under the corridor dossier's "History" or "Open questions" when the signal changes the picture.
- Append the indicator rows to `wiki/intel/indicators.csv`.
- Daily social media analyses (exports, monitoring reports): also append one aggregate row per corridor, day and indicator to `wiki/intel/media-daily.csv` (`date,corridor,indicator,value,source_id,notes`) so spikes are caught the same day.
- Migration figures (arrivals, crossings, asylum applications) go to `wiki/intel/outcomes.csv`, not to signals: they are what the system learns to anticipate.
- Leave originals in `raw/` untouched: they are the archive.

## 5. Report

Three lines: filed, duplicates, quarantined (with reasons). Then one next step, usually: "Indices moved on <corridor>: run `score-signal`?"
