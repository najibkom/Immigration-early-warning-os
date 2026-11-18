---
name: corridor-profile
description: Builds or updates a corridor dossier in the Intelligence Brain — geography, population context, drivers by vector, baselines, thresholds, known noise, matching playbooks and history — from the user's sources, ingested signals and cited web research. Use when the user says "profile a corridor", "add the Sahel to Morocco corridor", "update the corridor dossier", or names a new route to monitor.
---

# Corridor profile

One dossier per corridor at `wiki/intel/corridors/<slug>.md`, from `wiki/intel/corridors/_template.md`. Slug: `origin-to-destination` in lowercase, e.g. `sahel-to-morocco-coast`.

## 1. Scope (one round of questions)

Confirm origin areas, transit nodes, destination areas (region level), the client's main concern on this corridor, and any sources the user already trusts. Skip what the user already said.

## 2. Gather

In this order:
1. Workspace: signals in `wiki/intel/signals-index.csv` for this corridor, files in `raw/`, notes in `projects/` and `daily-logs/`.
2. Web research for context and baselines when the workspace is thin: prefer UN agencies (IOM DTM, UNHCR, WFP, FAO), national statistics offices, official gazettes, FEWS NET, World Bank, peer-reviewed work. Record each source you use as a proposed row for `sources.csv` (hand to `source-registry`).
3. Never collect or record personal data; aggregate figures only.

## 3. Draft the dossier

Fill every section of the template. For each driver and baseline give the indicator, the normal range and the Source ID. Mark anything uncertain `(unconfirmed)`. "Known noise" lists events that cause false spikes on this corridor (religious and national holidays, football tournaments, seasonal agricultural work, hashtag reuse). "Matching playbooks" lists existing PB IDs and gaps where a playbook is missing.

Write it, then show a five-line summary and the open questions. Ask the user to confirm or correct; apply corrections.

## 4. Update mode

When the dossier exists: read it, show what changed since `last_profiled` (new signals, alerts, feedback), propose edits as a short diff, apply on confirmation, update `last_profiled`.
