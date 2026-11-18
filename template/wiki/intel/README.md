# Intelligence Brain

The knowledge every score, alert and digest is grounded in. Read through the `intel-brain` skill.

| File | What it is | Analogy in a marketing brain |
|---|---|---|
| `corridors/<slug>.md` | One dossier per monitored corridor: geography, drivers, baselines, thresholds, sources, history | ICP / segments |
| `sources.csv` | Source registry with IDs, category, method, credibility, status | Proof table |
| `taxonomy.md` | Classification codes for signals | Vocabulary |
| `playbooks/PB-*.md` | Pre-approved response playbooks matched to scenarios | Messaging hub |
| `signals-index.csv` | One row per ingested signal (correlation_id, hash, source, corridor, category, date, path) | — |
| `indicators.csv` | Raw numbers per corridor, period and category, from documents | Raw campaign data |
| `features.csv` | 0–100 index per category, corridor and period: the history the rules look back on | Performance history |
| `outcomes.csv` | Migration figures per corridor and period: what the system learns to anticipate | Campaign results |
