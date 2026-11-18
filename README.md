# Early-Warning OS

A project operating system for the **AI Migration & Population Early-Warning Intelligence Pipeline**, built on the same three-module pattern as a personal OS + marketing brain + campaign engine. Version 0.3 learns its early-warning rules from your own history, reports on five time scales with 3/6/12-month outlooks, raises alerts by severity and urgency (including same-day social media spikes), and runs on a schedule.

| Module | Skills | Marketing analogy |
|---|---|---|
| Project OS | `setup`, `ingest`, `brief`, `shutdown` | Personal OS |
| Intelligence Brain | `intel-brain` (auto), `corridor-profile`, `source-registry`, `history-load`, `learn-rules` | Marketing Brain |
| Alert Engine | `score-signal`, `alert-triggers`, `alert-draft`, `alert-review`, `alerts-board`, `feedback` | Campaign Engine |
| Reporting & automation | `reports`, `automate` | Reporting agent |

## Install

**Claude desktop app:** open the `early-warning-os.plugin` file from the chat and press install. The `.plugin` file is a zip archive: do not open it in a text editor.

**Claude Code (terminal or the VS Code extension):** in a Claude Code session, run

```
/plugin marketplace add najibkom/early-warning-os
/plugin install early-warning-os@early-warning-os
```

On Claude Code 2.1.275 or later this works in one step: `/plugin install early-warning-os --marketplace najibkom/early-warning-os`. The repository is private, so your git must be signed in to GitHub with access to it.

**To read or edit the files in VS Code:** clone this repository (`git clone https://github.com/najibkom/early-warning-os`) and open the folder, or rename the `.plugin` file to `.zip` and extract it.

## How it works

**1. Learn (once, then every quarter)**
- Drop past documents in `raw/history/` in six categories: economy (incl. employment, SMEs), weather and environment, politics and security (incl. protests, conflict), social and health (incl. disease), social media trends, other.
- Drop past migration figures per corridor and period in `raw/outcomes/` (IOM DTM, UNHCR, Frontex, ministries).
- `history-load` turns them into indicators → 0–100 category indices per corridor and period (`features.csv`) and outcomes (`outcomes.csv`).
- `learn-rules` finds which categories moved before migration changed and by how many periods, tests candidate rules on the most recent 30% of periods, and proposes rules with confidence plus learned weights. A human approves; approved rules go into `frameworks/rulebook.json`.

**2. Run (every day or week)**
`ingest` new information (Gate 1) → `score-signal` (weights + approved rules that look back over past periods) → `alert-draft` → `alert-review` (Gate 2, human hold at 85+) → send → `feedback` (Gate 3) → `alerts-board`, weekly digest.

**3. Report (automatic)**

| Report | Looks back over | Looks ahead |
|---|---|---|
| Daily summary | yesterday | — |
| Weekly | last week vs the week before | — |
| Monthly | last month vs previous and a year ago | 3 months |
| Quarterly (3-month) | last quarter vs previous and a year ago | 3 and 6 months |
| 6-month | last half-year | 6 and 12 months |
| Annual | last year | 12 months |

Outlooks come from approved rules: a rule "drought > 80, 4 months before → surge" that is met today predicts a surge in 4 months.

**4. Alerts by condition, severity and urgency**

| Severity | Examples | Cadence | Handling |
|---|---|---|---|
| Severe | Sudden big social media spike (≥3σ and +100% in a day), critical score ≥85, high-confidence surge expected | Immediate (same day) or monthly for outlooks | Held for the analyst, 30-min SLA |
| Moderate | Social media rising 2+ days, score 70–84, +15 in a day, sustained weekly trend, category jump, medium outlook, migration +30% vs a year ago | Daily, weekly or monthly | Sent when every gate passes (auto-send) |

Thresholds are editable in `frameworks/alert-triggers.json`. 12-hour cooldown per corridor and trigger; updates only if the value moves >15%.

**5. Automation and missed runs**

Say "automate it": scheduled tasks on your computer run the daily cycle (ingest, score, triggers, alerts), the weekly, monthly, quarterly, 6-month and annual reports, and a quarterly rule re-learning proposal. If the computer was off, the next run catches up: missed days are scored and checked (alerts marked LATE), missed reports are produced. For no gaps at all, run the schedule in the cloud from a private GitHub data repository.

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
| `scripts/period_report.py` | Numbers for weekly, monthly, quarterly, 6-month and annual reports, vs previous period and a year ago |
| `scripts/outlook.py` | 3/6/12-month outlook from approved rules and their lags |
| `scripts/triggers.py` | Alert triggers: severity, cadence, cooldown, updates; daily social media spike detection |
| `scripts/catchup.py` | Lists missed daily runs and reports after the computer was off; records completed runs |
| `scripts/setup.sh` | Copies the workspace template without overwriting |

## Governance

Aggregate-only social media analysis, PII redaction at ingest (GDPR, Morocco Law 09-08), correlation IDs end to end, human-in-the-loop for critical scores, playbook actions only from client-approved playbooks, rules only after human approval. See `template/frameworks/governance.md`.

## Assumptions

- S_total is a weighted sum plus rule bonus (that section of the original spec was not in the excerpt provided).
- Rules are learned per corridor; "surge" = outcome above its 75th percentile in the learning periods.
- Correlation is not causation: rules are early-warning signs, reviewed by a human before use.

## Upgrading from 0.1

Run `setup` again in your folder: it adds the new files (rulebook, features, outcomes, indicators) and leaves yours untouched. Old index names `weather` and `policy` are read as `env` and `politics`. The old `social` (social media) is now `media`; `social` now means social conditions and health. Update `weights.json` to the six categories.
