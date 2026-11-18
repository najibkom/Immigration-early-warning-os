# Early-Warning OS

A project operating system for the **AI Migration & Population Early-Warning Intelligence Pipeline**, built on the same three-module pattern as a personal OS + marketing brain + campaign engine. Version 0.2 learns its early-warning rules from your own history.

| Module | Skills | Marketing analogy |
|---|---|---|
| Project OS | `setup`, `ingest`, `brief`, `shutdown` | Personal OS |
| Intelligence Brain | `intel-brain` (auto), `corridor-profile`, `source-registry`, `history-load`, `learn-rules` | Marketing Brain |
| Alert Engine | `score-signal`, `alert-draft`, `alert-review`, `alerts-board`, `feedback` | Campaign Engine |

## How it works

**1. Learn (once, then every quarter)**
- Drop past documents in `raw/history/` in six categories: economy (incl. employment, SMEs), weather and environment, politics and security (incl. protests, conflict), social and health (incl. disease), social media trends, other.
- Drop past migration figures per corridor and period in `raw/outcomes/` (IOM DTM, UNHCR, Frontex, ministries).
- `history-load` turns them into indicators → 0–100 category indices per corridor and period (`features.csv`) and outcomes (`outcomes.csv`).
- `learn-rules` finds which categories moved before migration changed and by how many periods, tests candidate rules on the most recent 30% of periods, and proposes rules with confidence plus learned weights. A human approves; approved rules go into `frameworks/rulebook.json`.

**2. Run (every day or week)**
`ingest` new information (Gate 1) → `score-signal` (weights + approved rules that look back over past periods) → `alert-draft` → `alert-review` (Gate 2, human hold at 85+) → send → `feedback` (Gate 3) → `alerts-board`, weekly digest.

## Scoring

- Base = Σ weight × index over econ, env, politics, social, media, other (defaults 0.25 / 0.20 / 0.20 / 0.15 / 0.15 / 0.05; replaced by learned weights once approved)
- + points of approved rules that fire (high 10, medium 6, low 3; capped at 20)
- × C: 0.85 (one category > 70), 1.15 (two), 1.30 (three+), 1.00 (none)
- S_final ≤ 100. Tiers: 0–39 log · 40–69 weekly digest · 70–84 priority alert · 85–100 critical, human hold. Anomaly if > 2.5σ from the 30-day mean.

## Scripts (Python 3.8+, standard library only)

| Script | Does |
|---|---|
| `scripts/to_index.py` | Indicators → 0–100 category indices (percentile within each indicator's own history) |
| `scripts/learn.py` | Lagged correlations, rule candidates (single and paired), train/test check, proposed weights → `.md` + `.json` report |
| `scripts/score.py` | Scores a corridor-period with weights + rulebook, corroboration, tiers, anomaly; `--record` adds the period to history |
| `scripts/recalibrate.py` | `--lower <category>` after a false positive, or `--from <report.json>` to apply approved learned weights |
| `scripts/setup.sh` | Copies the workspace template without overwriting |

## Governance

Aggregate-only social media analysis, PII redaction at ingest (GDPR, Morocco Law 09-08), correlation IDs end to end, human-in-the-loop for critical scores, playbook actions only from client-approved playbooks, rules only after human approval. See `template/frameworks/governance.md`.

## Assumptions

- S_total is a weighted sum plus rule bonus (that section of the original spec was not in the excerpt provided).
- Rules are learned per corridor; "surge" = outcome above its 75th percentile in the learning periods.
- Correlation is not causation: rules are early-warning signs, reviewed by a human before use.

## Upgrading from 0.1

Run `setup` again in your folder: it adds the new files (rulebook, features, outcomes, indicators) and leaves yours untouched. Old index names `weather` and `policy` are read as `env` and `politics`. The old `social` (social media) is now `media`; `social` now means social conditions and health. Update `weights.json` to the six categories.
