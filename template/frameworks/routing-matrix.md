# Decision and routing matrix

| S_final | Risk level | System action | Output target |
|---|---|---|---|
| 0–39 | Baseline / Low | Silent log. Save the record, no notification | Operational DB / historical archive (`alerts/history.csv`) |
| 40–69 | Watchlist / Moderate | Digest aggregation. Queue for the weekly brief | Weekly executive intelligence digest |
| 70–84 | Elevated Risk | Priority alert with a prescriptive briefing | Dedicated Slack/Teams channel, webhooks |
| 85–100 | Critical Shock | Emergency protocol. Human-in-the-loop hold before broadcast | SMS, high-priority webhook, executive briefing |

An anomaly flag (more than 2.5σ from the 30-day baseline) sends the item to an analyst whatever its tier.

## Cooldown and deduplication

- One alert per corridor + top driver in any 12-hour window.
- A new alert inside the window is suppressed unless S_final changed by more than 15%; then it goes out as an update in the same thread.

## Delivery

- Webhooks must return 200 OK. If a Critical delivery fails, escalate to the next channel (Slack → email → SMS).
- Every delivered alert carries the feedback choice: Accurate | False Positive | Irrelevant.
