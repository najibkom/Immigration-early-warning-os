---
name: history-load
description: Loads the historical base the system learns from — past documents in six categories (economy incl. employment and SMEs, weather and environment, politics and security incl. protests and conflict, social and health incl. disease, social media trends, other) and past migration figures per corridor and period — turning them into indicators, 0–100 category indices (features.csv) and outcomes (outcomes.csv). Use when the user says "load the history", "here are past reports", "add migration figures for 2019–2025", "build the historical dataset", or drops files in raw/history or raw/outcomes.
---

# History load

Build the two tables the learning step needs, for every corridor and period:

- `wiki/intel/indicators.csv` — raw indicators (what the documents say, as numbers)
- `wiki/intel/features.csv` — one 0–100 index per category, computed from the indicators
- `wiki/intel/outcomes.csv` — what actually happened to migration

Read `frameworks/governance.md` and `wiki/intel/taxonomy.md` first. Follow Gate 1 rules (sources registered, no personal data) for every file.

## 1. Agree the frame (one round of questions)

- **Granularity**: monthly (`2024-03`) or weekly (`2024-W11`). Monthly is the default; use one granularity everywhere.
- **Corridors** and **time span** (two years or more per corridor is the target; say plainly if there is less).
- **Outcome metric**: one main measure per run, e.g. `arrivals`, `irregular_crossings`, `asylum_applications`, `departures_intentions` (IOM DTM). Other metrics can be stored too.

## 2. Outcomes (what happened)

Read files in `raw/outcomes/` (IOM DTM, UNHCR, Frontex, Spanish Ministry of Interior, national statistics, partner data). Append one row per corridor × period × metric to `wiki/intel/outcomes.csv`: `period,corridor,metric,value,unit,source_id,notes`. Note revisions and gaps in `notes`. Never estimate a missing period; leave it out.

## 3. Indicators (what the documents say)

Read files in `raw/history/` (sub-folders per category are welcome but not required). For each document, extract **numbers per period and corridor**, one row each in `wiki/intel/indicators.csv`: `period,corridor,category,indicator,value,direction,source_id,notes`.

| Category | Key | Typical indicators (examples) |
|---|---|---|
| Economy, incl. employment and SMEs | `econ` | youth_unemployment_pct, sme_closures, food_price_index, currency_change_pct, remittances |
| Weather and environment | `env` | drought_index, rainfall_anomaly_pct (direction −1), flood_events, cereal_harvest_change_pct (direction −1) |
| Politics and security, incl. protests and conflict | `politics` | protest_events, conflict_events, fatalities, visa_rule_changes, border_closure_days |
| Social and health, incl. disease | `social` | disease_cases, outbreak_declared (0/1), school_closures, service_disruptions |
| Social media trends (aggregate only) | `media` | route_search_volume, migration_topic_mentions, negative_sentiment_share |
| Other | `other` | anything relevant that fits none of the above; name it clearly |

Rules:
- Text-only documents (news, reports) become **counts per period** (e.g. number of protest events reported), never quotes about people.
- `direction` is `1` when a higher value means more pressure, `-1` when it means less (more rain, better harvest).
- Social media is aggregate only: volumes, shares, trends. Never individual posts or accounts.
- Show a summary table per category (indicators found, periods covered, gaps) and ask the user to confirm before writing.

## 4. Build the indices

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/to_index.py" wiki/intel/indicators.csv --out wiki/intel/features.csv --merge
```

Each index is the percentile of the indicator within its own history (0 = calmest period seen, 100 = most extreme), averaged per category. Report: corridors × periods built, categories with no data, periods with fewer than three categories.

## 5. Next step

If at least 8 periods per corridor have both features and outcomes, offer `learn-rules`. With fewer than 24, warn that rules will be low confidence.
