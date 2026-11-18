#!/usr/bin/env python3
"""Catch-up after missed scheduled runs (computer off, app closed, source down).

List what was missed:
  python3 catchup.py --type daily|week|month|quarter|half|year [--today YYYY-MM-DD] [--max-days 62]
Record a completed run (call at the end of every run, scheduled or catch-up):
  python3 catchup.py --type daily --mark YYYY-MM-DD
  python3 catchup.py --type week  --mark 2026-W46      (the report label)

Run log: alerts/run-log.csv (type,covered,completed_utc,mode).
For daily runs the output lists every missed date since the last completed one
(up to --max-days back); for reports, every missed report window, each with an
--end date to pass to period_report.py. If there is no log yet, nothing is listed:
the first run starts the log.
"""
import argparse, csv, datetime as dt, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ewlib import read_csv
from periods import window, label

ap = argparse.ArgumentParser()
ap.add_argument("--type", required=True, choices=["daily", "week", "month", "quarter", "half", "year"])
ap.add_argument("--today")
ap.add_argument("--max-days", type=int, default=62)
ap.add_argument("--mark")
ap.add_argument("--mode", default="scheduled")
ap.add_argument("--log", default="alerts/run-log.csv")
a = ap.parse_args()
today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()

if a.mark:
    exists = os.path.exists(a.log)
    os.makedirs(os.path.dirname(a.log) or ".", exist_ok=True)
    with open(a.log, "a", newline="") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["type", "covered", "completed_utc", "mode"])
        w.writerow([a.type, a.mark, dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), a.mode])
    print(json.dumps({"marked": a.type, "covered": a.mark}))
    sys.exit(0)

done = {r["covered"] for r in read_csv(a.log) if r.get("type") == a.type}
missed = []
if a.type == "daily":
    dates = sorted(done)
    if dates:
        last = dt.date.fromisoformat(dates[-1])
        d = max(last + dt.timedelta(days=1), today - dt.timedelta(days=a.max_days))
        while d < today:  # today itself is the normal run
            if d.isoformat() not in done:
                missed.append({"date": d.isoformat()})
            d += dt.timedelta(days=1)
else:
    if done:
        # walk back over complete windows before today until the last done one
        s, _ = window(a.type, today)
        cur_end = s - dt.timedelta(days=1)
        limit = today - dt.timedelta(days=max(a.max_days, 400 if a.type in ("half", "year") else 120))
        while cur_end > limit:
            ws, we = window(a.type, cur_end)
            lab = label(a.type, ws)
            if lab in done:
                break
            missed.append({"label": lab, "end": we.isoformat()})
            cur_end = ws - dt.timedelta(days=1)
        missed.reverse()

print(json.dumps({"type": a.type, "today": today.isoformat(), "log_started": bool(done),
                  "missed": missed, "count": len(missed),
                  "note": ("" if done else "no completed run recorded yet: nothing to catch up; this run starts the log") +
                          (f" (looked back at most {a.max_days} days)" if a.type == "daily" and done else "")}, indent=2))
