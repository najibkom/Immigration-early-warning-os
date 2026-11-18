# Early-Warning OS — AI Migration & Population Early-Warning Intelligence Pipeline

This folder is the operating system for the pipeline project. Read this file at the start of every session.

## Read first, always

1. `frameworks/governance.md`: privacy, ethics and human-oversight rules. Non-negotiable.
2. The `intel-brain` skill before any scoring, alert, digest or briefing.

## Folder map

| Folder | Holds | Written by |
|---|---|---|
| `projects/` | Workstreams (pipeline build, client deliverables, partnerships). One file each, from `_template.md` | You and the user |
| `raw/` | Inbox. Drop reports, decrees, datasets, scraped pages, notes. `signals/`, `sources/`, `decrees/`, `data/`. `_quarantine/` for Gate 1 failures | The user; `ingest` files it |
| `wiki/intel/` | **Intelligence Brain**: `corridors/`, `sources.csv`, `taxonomy.md`, `playbooks/`, `signals-index.csv` | `ingest`, `corridor-profile`, `source-registry` |
| `alerts/` | **Alert Engine**: `board.md`, `history.csv`, `feedback.csv`, `drafts/`, `held/`, `sent/` | `score-signal`, `alert-draft`, `alert-review`, `alerts-board`, `feedback` |
| `frameworks/` | Scoring model, weights, routing matrix, quality gates, schema, templates, governance | Only `feedback` changes `weights.json`; other changes need the user |
| `daily-logs/` | One file per day, `YYYY-MM-DD.md`, one block per session | `shutdown` |
| `drafts/` | Anything not yet approved: proposals, concept notes, decks outlines | Any skill |

## Pipeline at a glance

Layer 1 ingest → Gate 1 → Layer 2 classify (taxonomy, corridor, vector) → Layer 3 score (`score.py`) → Gate 2 → Layer 4 alert, digest, playbook → Gate 3 → feedback → recalibration.

## Commands (skills)

- Project OS: `setup`, `ingest`, `brief`, `shutdown`
- Intelligence Brain: `corridor-profile`, `source-registry`
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
- Analyst on duty for holds: _to fill_
- Alert channels connected: _to fill (Slack/Teams/webhook/SMS)_
