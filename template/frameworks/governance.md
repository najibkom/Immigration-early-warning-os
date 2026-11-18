# Governance, privacy and ethics

These rules apply to every file and output in this workspace. They are not tunable.

## Purpose

The pipeline anticipates pressure on populations so that humanitarian, development and public-policy actors can prepare: relief, services, labour programmes, protection. Recommendations lead with protection and assistance.

## Privacy (EU GDPR, Morocco Law 09-08)

- Aggregate only. Social media is analysed as volumes, velocities, sentiment percentages and search frequencies. Individual posts, profiles, names, handles, faces, phone numbers, street addresses and IPs are never stored, quoted or shown.
- PII is redacted at ingest, before anything is saved to `wiki/` or `alerts/`.
- No output identifies, tracks or profiles an individual or a small identifiable group (a family, a named boat, a specific house).
- Location granularity in outputs: region or city, never a precise point tied to people.

## Traceability

- Every record carries a `correlation_id` from raw document to alert.
- Every alert line links to Source IDs; every Source ID links to an archived original in `raw/`.

## Human oversight

- Critical scores (≥ 85) and contradictory official texts are held for a named human analyst; 30-minute review SLA.
- Playbook actions are pre-approved by the client. The engine selects and quotes them; it never invents new operational actions.

## Language

Neutral and factual. Describe conditions, drivers and needs. No dehumanising terms ("flood of migrants", "invasion", "illegals"). Use "people on the move", "migrants", "displaced people", "asylum seekers" as the source context warrants.
