---
name: alert-draft
description: Drafts Layer 4 intelligence outputs from scored signals — priority and critical alerts with prescriptive briefing and matched playbook, weekly executive intelligence digests, daily summaries and analyst anomaly notes — fully cited to Source IDs. Use when the user says "draft the alert", "write this week's digest", "daily summary", "executive briefing", or after score-signal routes a corridor to 70 or above.
---

# Alert draft (Layer 4)

Read the `intel-brain` skill, `frameworks/alert-templates.md` and `frameworks/governance.md`.

## Modes

- **Alert** (default, from a `*-score.json`): priority (70–84) or critical (85–100).
- **Digest**: the weekly executive intelligence digest from `alerts/history.csv`, the board's watchlist queue, `alerts/sent/` and `alerts/feedback.csv` for the last 7 days.
- **Daily**: the five-line daily summary.
- **Analyst note**: for an anomaly flag below 70; same template, titled "ANALYST NOTE — anomaly", not for broadcast.

## Alert steps

1. Load the score JSON and the input JSON. Load the records behind each Source ID.
2. **Cooldown check** (G3.1): look in `alerts/sent/` for an alert on the same corridor + top driver in the last 12 hours. If there is one and S_final changed by 15% or less, stop and say it is suppressed. If more than 15%, draft it as an UPDATE that names the earlier correlation ID.
3. **Playbook match**: from `wiki/intel/playbooks/`, pick the playbook whose scenario matches the categories above 70, the rules fired and the corridor, and whose minimum tier is met. Quote its actions verbatim. Only `approved` playbooks count as recommendations; a `draft` match is shown as "Proposed playbook (not yet approved)". No match: write "No matching playbook. Gap logged." and add a task to `projects/pipeline-build.md`. Never invent operational actions.
4. Fill the template. Drivers table and "Early-warning rules fired" straight from the score JSON, each rule with its evidence line from `frameworks/rulebook.json`. "What changed" uses only facts in the cited records. "Confidence and limits" is never empty.
5. Status: `HELD` if S_final ≥ 85 or `hitl_required`, otherwise `DRAFT`.
6. Save to `alerts/drafts/<YYYY-MM-DD>-<corridor>-<tier-short>.md` (or `alerts/held/` for HELD) with frontmatter: `correlation_id, corridor, s_final, tier, status, source_ids, playbook, created_utc`.
7. Run `alert-review` on it automatically.

## Digest steps

Follow the digest structure in the templates. Week-over-week deltas computed in code from `history.csv`, not by hand. Save to `alerts/drafts/digest-<YYYY>-W<ww>.md`, then run `alert-review`.

## Optional page

If the user wants a shareable executive page or dashboard, offer to publish it as an artifact (dashboard type for corridor scores); keep the governance rules on the page too.
