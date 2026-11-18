---
type: project
status: active
priority: P1
cadence: weekly
next_action: "Confirm the first three corridors and the source list for Phase 1"
tags: [pipeline, roadmap]
---

# Pipeline build — 16-week roadmap

## Overview
Build and roll out the AI Migration & Population Early-Warning Intelligence Pipeline in four phases, each closing with its quality gate working.

## Goals
- Phase 1 (weeks 1–4): ingestion live for social aggregates (Meta, YouTube), gazettes, weather (NOAA), macro data; JSON schema and document archive in place.
- Phase 2 (weeks 5–8): LLM taxonomy classification; Gate 1 (SHA-256 hashing, schema validation, quarantine queue); PostgreSQL (Supabase) + pgvector.
- Phase 3 (weeks 9–12): scoring model S_final; RAG citation check and anomaly detection (Gate 2); human-in-the-loop dashboard for scores ≥ 85.
- Phase 4 (weeks 13–16): alert router (webhooks, Slack, Teams, SMS); executive dashboards (Looker Studio / Superset); feedback loop and weight recalibration (Gate 3).

## Current status
As of YYYY-MM-DD: setup.

## Key people
- 

## Open tasks
- [ ] Phase 1: list sources per vector in `wiki/intel/sources.csv`
- [ ] Phase 1: profile the first corridors with `corridor-profile`
- [ ] Phase 1: agree the playbook library with the client (`wiki/intel/playbooks/`)
- [ ] Phase 2: confirm taxonomy codes in `wiki/intel/taxonomy.md`
- [ ] Phase 3: name the analyst on duty and the 30-minute SLA process
- [ ] Phase 4: connect alert channels and test delivery

## Decisions
- 

## Links and sources
- Technical spec: the pipeline design document (Layers 1–4, Quality Gates 1–3, governance)
- Stack: n8n / Airflow, Playwright / Apify, Claude, PostgreSQL (Supabase), pgvector, S3/GCS, Looker Studio / Superset, Slack / Teams / Twilio
