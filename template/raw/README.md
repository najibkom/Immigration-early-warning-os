# raw/ — the inbox

Drop anything here, then run the `ingest` skill. Originals stay here as the immutable archive; the Intelligence Brain links back to them.

- `signals/` — reports, articles, social aggregates (CSV/exports), field notes
- `sources/` — information about a new source to register (URL, owner, method)
- `decrees/` — official gazettes, decrees, regulations (PDF/HTML)
- `data/` — datasets: prices, rainfall, drought indices, unemployment, remittances
- `_quarantine/` — created by `ingest` for records that fail Gate 1, with the reason

Do not drop files containing personal data about private individuals; `ingest` will redact it, but it is better not to collect it.
