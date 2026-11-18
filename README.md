# Early-Warning OS

A project operating system for the **AI Migration & Population Early-Warning Intelligence Pipeline**, built on the same three-module pattern as a personal OS + marketing brain + campaign engine.

| Module | Skills | Replaces (marketing analogy) |
|---|---|---|
| Project OS | `setup`, `ingest`, `brief`, `shutdown` | Personal OS |
| Intelligence Brain | `intel-brain` (auto), `corridor-profile`, `source-registry` | Marketing Brain (ICP → corridors, proof → sources, vocabulary → taxonomy, messaging → playbooks) |
| Alert Engine | `score-signal`, `alert-draft`, `alert-review`, `alerts-board`, `feedback` | Campaign Engine (brief → score, drafts → alerts, quality gate → Gates 1–3, campaigns board → alerts board) |

## Start

Open an empty folder and run the **setup** skill. It copies the workspace template (never overwriting) and walks a first loop.

## The loop

`raw/` drop → **ingest** (Gate 1) → **score-signal** (`scripts/score.py`) → **alert-draft** → **alert-review** (Gate 2, human hold ≥ 85) → send → **feedback** (Gate 3, recalibration) → **alerts-board**.

## Scoring

- S_total = Σ wᵢ·Iᵢ over social (0.25), econ (0.30), weather (0.25), policy (0.20)
- C = 0.85 (one vector > 70), 1.15 (two), 1.30 (three+), 1.00 (none)
- S_final = min(100, S_total·C); anomaly if > 2.5σ from the 30-day mean
- Tiers: 0–39 silent log · 40–69 weekly digest · 70–84 priority alert · 85–100 critical, human hold

`python3 scripts/score.py signal.json --weights frameworks/weights.json --history alerts/history.csv`

## Requirements

Python 3.8+ (standard library only). Optional connectors: Slack / Teams / email for sending, a web search tool for corridor research.

## Governance

Aggregate-only social analysis, PII redaction at ingest (GDPR, Morocco Law 09-08), correlation IDs end to end, human-in-the-loop for critical scores, playbook actions only from client-approved playbooks. See `template/frameworks/governance.md`.

## Assumptions in v0.1

- S_total is a weighted sum (that section of the spec was not in the excerpt provided).
- Recalibration lowers a weight by 2% relative and renormalises.
- A vector "triggers" above 70.
