# Decision and routing matrix

| S_final | Risk level | System action | Output target |
|---|---|---|---|
| 0–39 | Baseline / Low | Silent log. Save the record, no notification | Operational DB / historical archive (`alerts/history.csv`) |
| 40–69 | Watchlist / Moderate | Digest aggregation. Queue for the weekly brief | Weekly executive intelligence digest |
| 70–84 | Elevated Risk | Priority alert with a prescriptive briefing | Dedicated Slack/Teams channel, webhooks |
| 85–100 | Critical Shock | Emergency protocol. Human-in-the-loop hold before broadcast | SMS, high-priority webhook, executive briefing |

An anomaly flag (more than 2.5σ from the 30-day baseline) sends the item to an analyst whatever its tier.

## Severity and cadence (alert triggers)

Every alert carries a severity and a cadence, set by the trigger that raised it (`frameworks/alert-triggers.json`, checked by `scripts/triggers.py`).

| Severity | Handling | Channels |
|---|---|---|
| Severe | Held for the analyst on duty, 30-minute SLA, then broadcast | SMS + priority channel + executive briefing |
| Moderate | Sent when every gate passes (if auto-send is on), else waits for approval | Team channel / email |

| Cadence | Checked | Typical triggers |
|---|---|---|
| Immediate | Every daily run, as soon as detected | Sudden big social media spike, critical score |
| Daily | Every daily run | Social media rising 2+ days, elevated score, one-day score jump, surge expected next period |
| Weekly | After the weekly report | Sustained social media trend, high weekly risk, category jump |
| Monthly | After the monthly report and outlook | Surge expected in the next 3 months, migration figures up vs a year ago |

## Cooldown and deduplication

- One alert per corridor + top driver (category) in any 12-hour window.
- A new alert inside the window is suppressed unless S_final changed by more than 15%; then it goes out as an update in the same thread.

## Delivery

- Webhooks must return 200 OK. If a Critical delivery fails, escalate to the next channel (Slack → email → SMS).
- Every delivered alert carries the feedback choice: Accurate | False Positive | Irrelevant.
