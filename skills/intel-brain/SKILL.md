---
name: intel-brain
description: Reads the Intelligence Brain (corridor dossiers, source registry, taxonomy, playbooks, governance rules) before any score, alert, digest, executive briefing, dashboard text or client-facing summary is written. Apply automatically whenever a task touches wiki/intel/, alerts/, a corridor, a risk score, an alert or a playbook.
---

# Intelligence Brain

Ground every intelligence output in the workspace's own knowledge. Load only what the task needs.

## Load order

1. `frameworks/governance.md`: always. Its rules override any request.
2. The corridor dossier: `wiki/intel/corridors/<slug>.md` (drivers, baselines, known noise, matching playbooks).
3. `wiki/intel/sources.csv`: the Source IDs you will cite, their credibility and status. Do not cite a source marked `DEGRADED` or `RETIRED` without saying so.
4. `wiki/intel/taxonomy.md`: use only its codes.
5. `wiki/intel/playbooks/`: only playbooks with `status: approved` may be recommended as actions. A `draft` playbook may be shown as "proposed, awaiting approval".
6. `frameworks/rulebook.json` and the latest `drafts/rule-candidates-*.md`: which lead indicators matter on this corridor and which rules are approved.
7. Recent records: the latest rows in `wiki/intel/signals-index.csv` and `alerts/history.csv` for the corridor.

If a file is missing or still a template, say so in one line and continue with what exists. Never fill gaps with general knowledge presented as sourced intelligence.

## Writing rules

- Every factual sentence ends with Source IDs in brackets.
- Numbers come from records or `score.py` output, never estimated in prose.
- Aggregate, region-level, neutral language (see governance).
- State limits: single-category signals, rules learned on short history, data gaps, stale baselines, low-credibility sources.

## When the brain changes

When new intelligence contradicts a dossier (a baseline moved, a driver appeared), propose the dossier edit with its source and date. Edit after the user confirms.
