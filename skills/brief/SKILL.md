---
name: brief
description: Produces a fast context brief on a corridor, source, playbook, workstream, stakeholder or topic from the workspace (projects, Intelligence Brain, alerts, daily logs), plus email and calendar when connected. Use when the user asks "brief me on X", "where are we on the Sahel corridor", "what do we know about this source", or before a client or partner meeting.
---

# Brief

A one-page brief, grounded only in what is in the workspace and connected tools.

1. Find everything on the subject: `grep -ril "<subject>"` across `projects/`, `wiki/intel/`, `alerts/`, `daily-logs/` (most recent first), `drafts/`. If email or calendar connectors are present, search them for the subject and the next meeting.
2. Write the brief in chat, eight to fifteen lines:
   - **What it is** (one line)
   - **Current state** (latest S_final and tier for a corridor, status for a project), with dates
   - **What changed recently** (last two weeks)
   - **Open items and decisions pending**
   - **Risks and gaps** (missing data, degraded sources, unapproved playbooks)
   - **Next step**
3. Cite file paths for each point the user may want to open, and Source IDs for intelligence claims.
4. If the user asks to keep it, save to `drafts/brief-<slug>-<YYYY-MM-DD>.md`.

Never fill a gap from general knowledge as if it were project intelligence; label it "background, not from our sources" if you add it.
