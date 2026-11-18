---
name: setup
description: Start here. Builds the Early-Warning OS workspace in the current folder (projects, raw inbox, Intelligence Brain, Alert Engine, frameworks, daily logs), never overwriting existing files, then fills the project facts and walks through a first scored signal. Use when the user says "set up the early-warning OS", "start the pipeline project", "install the workspace", or runs it again to check what is missing.
---

# Setup

Build the workspace, then coach one first loop: corridor → source → signal → score → draft alert.

**Keep it short.** Answer first, eight lines at most per reply, one round of questions at a time.

## 1. Copy the template

Run:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/setup.sh" "$(pwd)"
```

The script copies `${CLAUDE_PLUGIN_ROOT}/template/` into the folder and skips every file that already exists. Report in one line what it created and what it skipped. If the folder is not empty and has no `CLAUDE.md`, say so and ask once before running.

Check `python3 --version` works; `score.py` needs Python 3.8+ and the standard library only.

## 2. Fill the project facts

Ask in one message, then write the answers into the "Project facts" section of `CLAUDE.md`:

1. Client or funder, and who reads the alerts?
2. Which corridors to monitor first (two or three)?
3. Who is the analyst on duty for held alerts?
4. Which alert channels exist today (Slack, Teams, email, webhook, SMS)?

Anything skipped stays `_to fill_`.

## 3. First loop (offer, do not force)

Offer: "Run a first loop now? 1 Yes, on your first corridor · 2 Yes, on a made-up example · 3 Later".

On yes, in order: `corridor-profile` for one corridor → `source-registry` for two or three sources → a test `score-signal` with indices the user gives (or example values: social 76, econ 72, weather 81, policy 40, marked EXAMPLE) → `alert-draft` on the result → `alert-review`. Mark every example file `EXAMPLE` in its title so it is never mistaken for live intelligence.

## 4. Close

Tell the user the next step in one line (usually: drop real sources in `raw/` and run `ingest`). Point to `projects/pipeline-build.md` for the 16-week roadmap.

## Re-running

On a second run, the script only adds missing files. Then list what is still `_to fill_` in `CLAUDE.md`, corridors without a profile, and playbooks still in draft.
