---
name: automate
description: Sets up, lists, pauses or changes the automated schedule of the Early-Warning OS on the user's computer — daily ingest, scoring and alerts; weekly report and weekly alert; monthly report, 3-month outlook and monthly alert; quarterly report and rule re-learning proposal; 6-month report and outlook; annual report and 12-month outlook. Use when the user says "automate it", "run it every day", "schedule the reports", "set up the automation", "pause the schedule", or "what runs automatically".
---

# Automate

The schedule runs as scheduled tasks on the user's computer, in this workspace folder. Each run starts fresh, so every task prompt is complete on its own.

## Before creating anything

1. Check `CLAUDE.md` "Project facts" and "Automation": corridors, period granularity, outcome metric, analyst on duty, alert channel, report recipients, auto-send setting. Ask once for anything missing that the schedule needs (at least corridors, analyst, and where alerts and reports should go).
2. Find the scheduling tools with a tool search (`create_trigger`, `list_triggers`, `update_trigger`, `delete_trigger`). List existing tasks first and do not duplicate one. If no scheduling tool exists, say so and stop.
3. Get the folder's absolute path on the user's computer (the connected folder). Every task needs `requires_local_device: true` and that folder.

## The schedule (user's local time; default times shown)

| Task name | When | Cron (CRON_TZ=<user zone>) | What the run does |
|---|---|---|---|
| EW daily run | every day 06:47 | `47 6 * * *` | `ingest` new files in raw/ incl. daily social media analyses (Gate 1); score every corridor (`score-signal`); `alert-triggers --cadence day` (immediate and daily triggers); draft and review the triggered alerts; send Elevated alerts (70–84) that pass every gate if auto-send is on; hold Critical (85+) for the analyst and notify them; refresh the board; write the daily summary |
| EW weekly report | Monday 07:13 | `13 7 * * 1` | `reports` kind week, then `alert-triggers --cadence week` |
| EW monthly report | 1st of month 07:23 | `23 7 1 * *` | `reports` kind month + 3-month outlook, then `alert-triggers --cadence month` |
| EW quarterly report | 1 Jan/Apr/Jul/Oct 07:37 | `37 7 1 1,4,7,10 *` | `reports` kind quarter (3-month) + 3- and 6-month outlooks; run `learn-rules` and save the proposal for human approval (never auto-approve) |
| EW 6-month report | 1 Jan and 1 Jul 07:53 | `53 7 1 1,7 *` | `reports` kind half + 6- and 12-month outlooks |
| EW annual report | 2 Jan 08:11 | `11 8 2 1 *` | `reports` kind year + 12-month outlook + source and rulebook review |

Offer the defaults; change times if the user asks. Use their time zone from the conversation or `CLAUDE.md`.

## Task prompt (adapt per row)

Write each prompt as a complete instruction, for example for the daily run:

> In the Early-Warning OS workspace at <absolute folder path>: read CLAUDE.md and frameworks/governance.md. Run the daily cycle: (1) ingest every new file in raw/ with the ingest skill, filing only items that pass Gate 1 and quarantining the rest; (2) score every corridor listed in CLAUDE.md for the current period with the score-signal skill; (3) run the alert-triggers skill with cadence day and, for every triggered alert, draft it with alert-draft (severity, cadence, trigger evidence) and review it with alert-review; (4) send moderate alerts that pass every gate through <channel> only if CLAUDE.md says auto-send: on, otherwise leave them in alerts/drafts for approval; (5) hold every severe alert in alerts/held and notify <analyst> through <channel> at once; never broadcast a severe alert without their approval; (6) refresh alerts/board.md; (7) write a five-line daily summary to reports/daily/<date>.md and to the daily log. Ask no questions; record any decision you had to make at the top of the summary.

## Rules that never change in automated runs

- Severe alerts (critical scores, sudden big social media spikes, high-confidence surges) and contradictory official texts are never broadcast without a named human's approval.
- New rules and weights from a scheduled `learn-rules` are proposals only; they wait for approval.
- No personal data, ever; aggregate social media only.
- A run that cannot reach a source or channel records it on the board and in the summary; it does not retry endlessly.

## After creating

Confirm in one short table: task, next run, approval setting. Tell the user each task's approval setting as the tool reports it; if runs will ask for approval, mention they can switch the task to automatic approval in its settings if their organization allows it. Record the schedule under "Automation" in `CLAUDE.md`.

## Changing or pausing

"Pause the daily run", "move the weekly report to Friday", "stop everything": use the scheduling tools to update or disable, then update `CLAUDE.md`.
