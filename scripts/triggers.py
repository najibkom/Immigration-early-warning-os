#!/usr/bin/env python3
"""Evaluate alert triggers: decides severity (severe | moderate) and cadence
(immediate | day | week | month) from scores, daily social media trends, weekly
reports, outlooks and migration figures.

Usage:
  python3 triggers.py --cadence day|week|month [--date YYYY-MM-DD]
      [--config frameworks/alert-triggers.json] [--history alerts/history.csv]
      [--media wiki/intel/media-daily.csv] [--week-report reports/week/<label>.json]
      [--outlook reports/outlook/<as-of>.json] [--month-report reports/month/<label>.json]
      [--log alerts/trigger-log.csv] [--out alerts/triggers/<date>-<cadence>]

--cadence day   checks immediate + day triggers (run every day)
--cadence week  checks week triggers (run after the weekly report)
--cadence month checks month triggers (run after the monthly report and outlook)
Cooldown: the same corridor + trigger is not raised again within cooldown_hours
unless the measured value changed by more than update_if_change_pct (then: UPDATE).
"""
import argparse, csv, datetime as dt, glob, json, math, os, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ewlib import read_csv, fnum, mean

ap = argparse.ArgumentParser()
ap.add_argument("--cadence", required=True, choices=["day", "week", "month"])
ap.add_argument("--date")
ap.add_argument("--config", default="frameworks/alert-triggers.json")
ap.add_argument("--history", default="alerts/history.csv")
ap.add_argument("--media", default="wiki/intel/media-daily.csv")
ap.add_argument("--week-report")
ap.add_argument("--month-report")
ap.add_argument("--outlook")
ap.add_argument("--log", default="alerts/trigger-log.csv")
ap.add_argument("--out")
a = ap.parse_args()

today = dt.date.fromisoformat(a.date) if a.date else dt.date.today()
cfg = json.load(open(a.config))
want = {"day": {"immediate", "day"}, "week": {"week"}, "month": {"month"}}[a.cadence]
fired = []


def latest(pattern):
    files = sorted(glob.glob(pattern))
    return files[-1] if files else None


def add(t, corridor, value, evidence, severity=None, cadence=None):
    fired.append({"trigger": t["id"], "name": t["name"], "corridor": corridor,
                  "severity": severity or t["severity"], "cadence": cadence or t["cadence"],
                  "value": round(value, 2) if isinstance(value, (int, float)) else value, "evidence": evidence})


# ---------- data
scores = defaultdict(dict)  # corridor -> date -> s_final (last of the day)
for r in read_csv(a.history):
    try:
        scores[r["corridor"]][dt.date.fromisoformat(r["date"])] = float(r["s_final"])
    except (KeyError, ValueError):
        pass
media = defaultdict(lambda: defaultdict(float))  # (corridor, indicator) -> date -> value
msrc = defaultdict(set)
for r in read_csv(a.media):
    v = fnum(r.get("value"))
    try:
        d = dt.date.fromisoformat(r["date"])
    except (KeyError, ValueError):
        continue
    if v is not None:
        media[(r["corridor"], r.get("indicator", "volume"))][d] += v
        if r.get("source_id"):
            msrc[(r["corridor"], r.get("indicator", "volume"))].add(r["source_id"])


def baseline(series, end, days):
    vals = [series[end - dt.timedelta(days=i)] for i in range(1, days + 1) if (end - dt.timedelta(days=i)) in series]
    if len(vals) < 7:
        return None, None
    m = mean(vals)
    sd = math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1)) if len(vals) > 1 else 0
    return m, sd


def spike(series, d, days):
    if d not in series:
        return None
    m, sd = baseline(series, d, days)
    if m is None:
        return None
    v = series[d]
    z = (v - m) / sd if sd > 0 else (0 if v == m else float("inf"))
    pct = 100 * (v - m) / m if m else None
    return v, m, z, pct


# ---------- checks
for t in cfg["triggers"]:
    if t["cadence"] not in want and not (a.cadence == "day" and t["check"] == "outlook"):
        continue
    p = t.get("params", {})
    c = t["check"]

    if c == "media_spike":
        for (corr, ind), ser in media.items():
            s = spike(ser, today, p.get("baseline_days", 30))
            if s and s[2] >= p["z_min"] and s[3] is not None and s[3] >= p["pct_min"]:
                add(t, corr, s[3], [f"{ind} = {s[0]:g} today vs {s[1]:.1f} 30-day mean (z {s[2]:.1f}, {s[3]:+.0f}%)",
                                    "sources: " + " ".join(sorted(msrc[(corr, ind)]))])

    elif c == "media_rising":
        for (corr, ind), ser in media.items():
            ok, ev = True, []
            for k in range(p.get("days", 2)):
                d = today - dt.timedelta(days=k)
                s = spike(ser, d, p.get("baseline_days", 30))
                if not (s and (s[2] >= p["z_min"] or (s[3] or 0) >= p["pct_min"])):
                    ok = False; break
                ev.append(f"{d}: {ind} {s[0]:g} (z {s[2]:.1f}, {s[3]:+.0f}%)")
            if ok:
                add(t, corr, len(ev), ev + ["sources: " + " ".join(sorted(msrc[(corr, ind)]))])

    elif c == "media_sustained":
        for (corr, ind), ser in media.items():
            w = [ser[today - dt.timedelta(days=i)] for i in range(p["window_days"]) if today - dt.timedelta(days=i) in ser]
            b = [ser[today - dt.timedelta(days=i)] for i in range(p["window_days"], p["window_days"] + p["baseline_days"]) if today - dt.timedelta(days=i) in ser]
            if len(w) >= 4 and len(b) >= 7 and mean(b):
                pct = 100 * (mean(w) - mean(b)) / mean(b)
                if pct >= p["pct_min"]:
                    add(t, corr, pct, [f"{ind}: 7-day mean {mean(w):.1f} vs {mean(b):.1f} over the previous 4 weeks ({pct:+.0f}%)"])

    elif c in ("score_at_least", "score_between", "score_jump"):
        for corr, ser in scores.items():
            if today not in ser:
                continue
            v = ser[today]
            if c == "score_at_least" and v >= p["min"]:
                add(t, corr, v, [f"S_final {v} on {today}"])
            elif c == "score_between" and p["min"] <= v <= p["max"]:
                add(t, corr, v, [f"S_final {v} on {today}"])
            elif c == "score_jump":
                y = ser.get(today - dt.timedelta(days=1))
                if y is not None and v - y >= p["points"]:
                    sev = "severe" if v >= p.get("severe_if_reaches", 999) else None
                    add(t, corr, v - y, [f"S_final {y} → {v} in one day"], severity=sev)

    elif c in ("week_mean", "category_jump"):
        path = a.week_report or latest("reports/week/*.json")
        if not path:
            continue
        rep = json.load(open(path))
        for corr, d in rep["corridors"].items():
            s = d.get("scores")
            if c == "week_mean" and s:
                crit = s["tier_days"].get("critical", 0)
                if s["mean"] >= p["min"] or crit >= p["critical_days"]:
                    sev = "severe" if s["mean"] >= p["severe_min"] else None
                    add(t, corr, s["mean"], [f"week {rep['label']}: mean {s['mean']}, {crit} critical days ({os.path.basename(path)})"], severity=sev)
            if c == "category_jump":
                cur, prev = d.get("categories") or {}, d.get("categories_previous") or {}
                for k in cur:
                    if k in prev and cur[k] - prev[k] >= p["points"]:
                        add(t, corr, cur[k] - prev[k], [f"{k} index {prev[k]} → {cur[k]} week {rep['label']}"])

    elif c == "outlook":
        path = a.outlook or latest("reports/outlook/*.json")
        if not path:
            continue
        ol = json.load(open(path))
        for corr, d in ol["corridors"].items():
            hz = d["horizons"].get(p["horizon"])
            if not hz or hz["signal"] not in p["levels"]:
                continue
            soon = [h for h in d["hits"] if h["ahead"] <= p.get("escalate_to_day_if_within_periods", 0)]
            if a.cadence == "day":
                if soon:  # surge expected next period: do not wait for the monthly alert
                    add(t, corr, hz["signal"], [f"surge expected {soon[0]['period']} by {', '.join(sorted({h['rule'] for h in soon}))}"] +
                        [e for h in soon for e in h["evidence"]][:4], cadence="day")
            elif t["cadence"] in want:
                add(t, corr, hz["signal"], [f"{p['horizon']} outlook {hz['signal']}: surge expected {', '.join(hz['expected_surge_periods'])}",
                                            "rules: " + ", ".join(hz["rules"])])

    elif c == "outcome_yoy":
        path = a.month_report or latest("reports/month/*.json")
        if not path:
            continue
        rep = json.load(open(path))
        for corr, d in rep["corridors"].items():
            for m, o in (d.get("outcomes") or {}).items():
                ch = o.get("change_vs_year_ago_pct")
                if ch is not None and ch >= p["pct_min"]:
                    sev = "severe" if ch >= p.get("severe_pct", 999) else None
                    add(t, corr, ch, [f"{m} {o['total']} in {rep['label']} vs {o['year_ago']} a year earlier ({ch:+}%)"], severity=sev)

# ---------- one alert per corridor and cadence: keep the most severe trigger, list the others
order = {"severe": 0, "moderate": 1}
fired.sort(key=lambda x: (x["corridor"], order[x["severity"]]))

# ---------- cooldown and updates
log = read_csv(a.log)
now = dt.datetime.combine(today, dt.datetime.now().time())
final = []
for f_ in fired:
    prev = [r for r in log if r.get("corridor") == f_["corridor"] and r.get("trigger") == f_["trigger"]]
    status = "NEW"
    if prev:
        last = prev[-1]
        try:
            age_h = (now - dt.datetime.fromisoformat(last["time"])).total_seconds() / 3600
        except (KeyError, ValueError):
            age_h = 1e9
        if age_h < cfg.get("cooldown_hours", 12):
            lv, nv = fnum(last.get("value")), f_["value"] if isinstance(f_["value"], (int, float)) else None
            if lv and nv is not None and abs(nv - lv) / abs(lv) * 100 > cfg.get("update_if_change_pct", 15):
                status = "UPDATE"
            else:
                status = "SUPPRESSED"
    f_["status"] = f_.get("status") or status
    final.append(f_)

new_log = [{"time": now.isoformat(timespec="minutes"), "corridor": f_["corridor"], "trigger": f_["trigger"],
            "severity": f_["severity"], "cadence": f_["cadence"], "value": f_["value"], "status": f_["status"]} for f_ in final]
if new_log:
    exists = os.path.exists(a.log)
    os.makedirs(os.path.dirname(a.log) or ".", exist_ok=True)
    with open(a.log, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(new_log[0]))
        if not exists:
            w.writeheader()
        w.writerows(new_log)

out = a.out or f"alerts/triggers/{today}-{a.cadence}"
os.makedirs(os.path.dirname(out), exist_ok=True)
active = [f_ for f_ in final if f_["status"] != "SUPPRESSED"]
by_corr = defaultdict(list)
for f_ in active:
    by_corr[f_["corridor"]].append(f_)
alerts = []
for corr, fs in by_corr.items():
    top = min(fs, key=lambda x: order[x["severity"]])
    alerts.append({"corridor": corr, "severity": top["severity"], "cadence": top["cadence"],
                   "status": "UPDATE" if any(x["status"] == "UPDATE" for x in fs) else "NEW",
                   "handling": "HOLD for analyst (30-min SLA) before any broadcast" if top["severity"] == "severe"
                   else "send when every gate passes (auto-send setting applies)",
                   "triggers": fs})
alerts.sort(key=lambda x: order[x["severity"]])
json.dump({"date": today.isoformat(), "cadence": a.cadence, "alerts": alerts,
           "suppressed": [f_ for f_ in final if f_["status"] == "SUPPRESSED"]}, open(out + ".json", "w"), indent=2)
L = [f"# Triggered alerts — {today} — {a.cadence} check", ""]
if not alerts:
    L.append("No trigger met its condition.")
for al in alerts:
    L += [f"## {al['severity'].upper()} — {al['corridor']} ({al['status']})", f"Handling: {al['handling']}", ""]
    for f_ in al["triggers"]:
        L.append(f"- **{f_['trigger']}** {f_['name']} [{f_['cadence']}]: " + "; ".join(f_["evidence"]))
    L.append("")
open(out + ".md", "w").write("\n".join(L) + "\n")
print(json.dumps({"written": [out + ".md", out + ".json"],
                  "alerts": [{k: x[k] for k in ("corridor", "severity", "cadence", "status")} for x in alerts],
                  "suppressed": len(final) - len(active)}, indent=2))
