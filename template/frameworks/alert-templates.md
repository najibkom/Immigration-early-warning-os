# Alert templates

Plain, neutral, cited. Every factual line ends with its Source IDs in brackets, e.g. `[SRC-004, SRC-019]`.

## Priority alert (70–84) and Critical alert (85–100)

```
[TIER] — <Corridor name> — S_final <score> (<+/- change> vs 30-day mean)
Correlation ID: <uuid>    Generated: <date time UTC>    Status: DRAFT | HELD | APPROVED

WHAT CHANGED (2–3 lines)
<the conditions that moved, each with a source>

DRIVERS
| Vector | Index | Weight | Contribution |
| ... from score.py output ... |
Corroboration: <n> vectors above 70 → C = <value>

CONFIDENCE AND LIMITS
<single-vector? data gaps? contradictory texts? degraded sources?>

RECOMMENDED PLAYBOOK: <PB-ID> — <name>
1. <action from the pre-approved playbook, unchanged>
2. ...

SOURCES
SRC-xxx — <name, date>
Feedback: Accurate | False Positive | Irrelevant
```

## Weekly executive intelligence digest

1. Week at a glance: corridors by S_final, week-over-week delta, tier changes.
2. Top three movements, each with drivers and sources.
3. Watchlist items (40–69) in one line each.
4. Alerts sent this week and their feedback.
5. Source health: degraded scrapers, credibility changes.
6. Weight changes from recalibration, if any.

## Daily summary

Five lines at most: highest corridor, biggest mover, new alerts, holds pending, source issues.
