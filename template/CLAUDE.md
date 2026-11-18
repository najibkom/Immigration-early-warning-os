# Early-Warning OS — AI Migration & Population Early-Warning Intelligence Pipeline

This folder is the operating system for the pipeline project. Read this file at the start of every session.

## Read first, always

1. `frameworks/governance.md`: privacy, ethics and human-oversight rules. Non-negotiable.
2. The `intel-brain` skill before any scoring, alert, digest or briefing.

## Folder map

| Folder | Holds | Written by |
|---|---|---|
| `projects/` | Workstreams (pipeline build, client deliverables, partnerships). One file each, from `_template.md` | You and the user |
| `raw/` | Inbox. Drop reports, decrees, datasets, scraped pages, notes. `signals/`, `sources/`, `decrees/`, `data/` for current information; `history/` for past documents; `outcomes/` for past migration figures. `_quarantine/` for Gate 1 failures | The user; `ingest` and `history-load` file it |
| `wiki/intel/` | **Intelligence Brain**: `corridors/`, `sources.csv`, `taxonomy.md`, `playbooks/`, `signals-index.csv`, and the historical base: `indicators.csv`, `features.csv` (0–100 index per category, corridor, period), `outcomes.csv` (migration figures) | `ingest`, `history-load`, `corridor-profile`, `source-registry`, `score-signal` |
| `alerts/` | **Alert Engine**: `board.md`, `history.csv`, `feedback.csv`, `drafts/`, `held/`, `sent/` | `score-signal`, `alert-draft`, `alert-review`, `alerts-board`, `feedback` |
| `frameworks/` | Scoring model, weights, **rulebook** (approved early-warning rules), routing matrix, quality gates, schema, templates, governance | `feedback` and `learn-rules` change `weights.json` and `rulebook.json`, only after the user approves |
| `daily-logs/` | One file per day, `YYYY-MM-DD.md`, one block per session | `shutdown` |
| `drafts/` | Anything not yet approved: proposals, concept notes, decks outlines | Any skill |

## Pipeline at a glance

Learning (once, then quarterly): `history-load` past documents + migration figures → `learn-rules` (lagged correlations, rule candidates tested on recent periods) → human approves → rulebook + weights.

Daily/weekly: Layer 1 ingest → Gate 1 → Layer 2 classify (six categories: econ, env, politics, social, media, other) → Layer 3 score (`score.py` with weights + rulebook) → Gate 2 → Layer 4 alert, digest, playbook → Gate 3 → feedback → recalibration.

## Commands (skills)

- Project OS: `setup`, `ingest`, `brief`, `shutdown`
- Intelligence Brain: `corridor-profile`, `source-registry`, `history-load`, `learn-rules`
- Alert Engine: `score-signal`, `alert-draft`, `alert-review`, `alerts-board`, `feedback`

## House rules

- Answer first, eight lines at most in chat; detail goes in the file.
- Never compute a score in prose. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/score.py"`.
- Every factual claim cites a Source ID. Unknown is written as unknown.
- Dates as YYYY-MM-DD, times in UTC.
- Never overwrite a daily log, a sent alert or `history.csv`; append.

## Project facts

- Client / funder: _to fill_
- Monitored corridors: _to fill, e.g. Sahel → Morocco coast; Morocco → Spain (Strait / Canaries)_
- Period granularity: _monthly (default) or weekly_
- Main outcome metric: _to fill, e.g. arrivals, irregular_crossings, asylum_applications_
- Analyst on duty for holds: _to fill_
- Alert channels connected: _to fill (Slack/Teams/webhook/SMS)_
