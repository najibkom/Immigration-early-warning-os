#!/usr/bin/env python3
"""Numbers for a period report: weekly, monthly, quarterly, 6-month or annual.

Usage:
  python3 period_report.py --kind week|month|quarter|half|year [--end YYYY-MM-DD]
      [--history alerts/history.csv] [--features wiki/intel/features.csv]
      [--outcomes wiki/intel/outcomes.csv] [--feedback alerts/feedback.csv]
      [--sent alerts/sent] [--out reports/<kind>/<label>]

Window = the calendar week/month/quarter/half/year containing --end (default: the
last complete one before today). Compares with the previous window and the same
window a year earlier. Writes <out>.json and <out>-data.md (tables); the reports
skill writes the narrative around them.
"""
import argparse, datetime as dt, json, os, re, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ewlib import CATEGORIES, LABELS, read_csv, fnum, mean
from periods import KINDS, window, previous, year_ago, label, period_start

ap = argparse.ArgumentParser()
ap.add_argument("--kind", required=True, choices=list(KINDS))
ap.add_argument("--end")
ap.add_argument("--history", default="alerts/history.csv")
ap.add_argument("--features", default="wiki/intel/features.csv")
ap.add_argument("--outcomes", default="wiki/intel/outcomes.csv")
ap.add_argument("--feedback", default="alerts/feedback.csv")
ap.add_argument("--sent", default="alerts/sent")
ap.add_argument("--out")
a = ap.parse_args()

if a.end:
    end = dt.date.fromisoformat(a.end)
else:  # last complete window
    s, _ = window(a.kind, dt.date.today())
    end = s - dt.timedelta(days=1)
W = window(a.kind, end)
P = previous(a.kind, W[0])
Y = year_ago(a.kind, W[0])
lab = label(a.kind, W[0])
out = a.out or f"reports/{a.kind}/{lab}"


def tier(s):
    return "critical" if s >= 85 else "elevated" if s >= 70 else "watch" if s >= 40 else "low"


def inwin(d, w):
    return w[0] <= d <= w[1]


# --- scores (daily history)
hist = []
for r in read_csv(a.history):
    try:
        hist.append((dt.date.fromisoformat(r["date"]), r["corridor"], float(r["s_final"]), r.get("top_driver", "")))
    except (KeyError, ValueError):
        pass


def score_stats(w):
    by = defaultdict(list)
    drivers = defaultdict(lambda: defaultdict(int))
    for d, c, s, drv in hist:
        if inwin(d, w):
            by[c].append((d, s))
            drivers[c][drv] += 1
    res = {}
    for c, pts in by.items():
        pts.sort()
        vals = [s for _, s in pts]
        tiers = defaultdict(int)
        for v in vals:
            tiers[tier(v)] += 1
        res[c] = {"days_scored": len(vals), "mean": round(mean(vals), 1), "max": round(max(vals), 1),
                  "last": round(vals[-1], 1), "tier_days": dict(tiers),
                  "main_driver": max(drivers[c], key=drivers[c].get) if drivers[c] else ""}
    return res


cur_s, prev_s, yoy_s = score_stats(W), score_stats(P), score_stats(Y)

# --- category indices (monthly or weekly features)
feat = []
for r in read_csv(a.features):
    try:
        feat.append((period_start(r["period"]), r["corridor"], {k: fnum(r.get(k)) for k in CATEGORIES}))
    except (KeyError, ValueError):
        pass


def cat_stats(w):
    acc = defaultdict(lambda: defaultdict(list))
    for d, c, vals in feat:
        if inwin(d, w):
            for k, v in vals.items():
                if v is not None:
                    acc[c][k].append(v)
    return {c: {k: round(mean(v), 1) for k, v in ks.items()} for c, ks in acc.items()}


cur_c, prev_c = cat_stats(W), cat_stats(P)

# --- outcomes
outc = []
for r in read_csv(a.outcomes):
    v = fnum(r.get("value"))
    if v is None:
        continue
    try:
        outc.append((period_start(r["period"]), r["corridor"], r.get("metric", ""), v))
    except (KeyError, ValueError):
        pass


def out_stats(w):
    acc = defaultdict(float)
    n = defaultdict(int)
    for d, c, m, v in outc:
        if inwin(d, w):
            acc[(c, m)] += v
            n[(c, m)] += 1
    return {f"{c}|{m}": {"total": round(acc[(c, m)]), "periods": n[(c, m)]} for (c, m) in acc}


cur_o, prev_o, yoy_o = out_stats(W), out_stats(P), out_stats(Y)

# --- feedback and sent alerts
fb = defaultdict(int)
for r in read_csv(a.feedback):
    try:
        if inwin(dt.date.fromisoformat(r["date"][:10]), W):
            fb[r.get("verdict", "?")] += 1
    except (KeyError, ValueError):
        pass
sent = defaultdict(int)
if os.path.isdir(a.sent):
    for fn in os.listdir(a.sent):
        if not fn.endswith(".md"):
            continue
        txt = open(os.path.join(a.sent, fn), encoding="utf-8", errors="ignore").read(3000)
        m = re.search(r"created_utc:\s*(\d{4}-\d{2}-\d{2})", txt)
        t = re.search(r"tier:\s*(.+)", txt)
        if m and inwin(dt.date.fromisoformat(m.group(1)), W):
            sent[(t.group(1).strip() if t else "unknown")] += 1


def pct(a_, b_):
    return None if not b_ else round(100 * (a_ - b_) / b_, 1)


corridors = sorted(set(cur_s) | set(cur_c) | {k.split("|")[0] for k in cur_o})
report = {
    "kind": a.kind, "label": lab, "window": [W[0].isoformat(), W[1].isoformat()],
    "previous_window": [P[0].isoformat(), P[1].isoformat()], "year_ago_window": [Y[0].isoformat(), Y[1].isoformat()],
    "corridors": {},
    "alerts_sent_by_tier": dict(sent), "feedback": dict(fb),
}
for c in corridors:
    s, ps = cur_s.get(c), prev_s.get(c)
    report["corridors"][c] = {
        "scores": s, "scores_previous": ps, "scores_year_ago": yoy_s.get(c),
        "mean_change_vs_previous": None if not (s and ps) else round(s["mean"] - ps["mean"], 1),
        "categories": cur_c.get(c), "categories_previous": prev_c.get(c),
        "outcomes": {k.split("|")[1]: {**v, "previous": prev_o.get(k, {}).get("total"), "year_ago": yoy_o.get(k, {}).get("total"),
                                       "change_vs_previous_pct": pct(v["total"], prev_o.get(k, {}).get("total")),
                                       "change_vs_year_ago_pct": pct(v["total"], yoy_o.get(k, {}).get("total"))}
                     for k, v in cur_o.items() if k.startswith(c + "|")},
    }

os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
with open(out + ".json", "w") as f:
    json.dump(report, f, indent=2)

L = [f"# {KINDS[a.kind]} report data — {lab} ({W[0]} to {W[1]})", "",
     f"Compared with {label(a.kind, P[0])} ({P[0]} to {P[1]}) and {label(a.kind, Y[0])} a year earlier.", "",
     "## Risk scores by corridor", "",
     "| Corridor | Days scored | Mean | Max | Last | Mean vs previous | Critical days | Elevated days | Main driver |",
     "|---|---|---|---|---|---|---|---|---|"]
for c in corridors:
    s = report["corridors"][c]["scores"]
    if not s:
        L.append(f"| {c} | 0 | – | – | – | – | – | – | – |"); continue
    ch = report["corridors"][c]["mean_change_vs_previous"]
    L.append(f"| {c} | {s['days_scored']} | {s['mean']} | {s['max']} | {s['last']} | {'–' if ch is None else f'{ch:+}'} | "
             f"{s['tier_days'].get('critical', 0)} | {s['tier_days'].get('elevated', 0)} | {s['main_driver']} |")
L += ["", "## Category indices (mean, change vs previous)", "", "| Corridor | " + " | ".join(CATEGORIES) + " |", "|---" * (len(CATEGORIES) + 1) + "|"]
for c in corridors:
    cc, pc = report["corridors"][c]["categories"] or {}, report["corridors"][c]["categories_previous"] or {}
    cells = []
    for k in CATEGORIES:
        if k in cc:
            d = f" ({cc[k] - pc[k]:+.1f})" if k in pc else ""
            cells.append(f"{cc[k]}{d}")
        else:
            cells.append("–")
    L.append(f"| {c} | " + " | ".join(cells) + " |")
L += ["", "## Migration outcomes", "", "| Corridor | Metric | Total | Previous | Change | Year ago | Change vs year ago |", "|---|---|---|---|---|---|---|"]
any_o = False
for c in corridors:
    for m, v in report["corridors"][c]["outcomes"].items():
        any_o = True
        f_ = lambda x: "–" if x is None else f"{x:+}%"
        L.append(f"| {c} | {m} | {v['total']} | {v['previous'] if v['previous'] is not None else '–'} | {f_(v['change_vs_previous_pct'])} | "
                 f"{v['year_ago'] if v['year_ago'] is not None else '–'} | {f_(v['change_vs_year_ago_pct'])} |")
if not any_o:
    L.append("| – | no outcome figures in this window yet | | | | | |")
L += ["", "## Alerts and feedback", "",
      f"Alerts sent by tier: {dict(sent) or 'none'}. Feedback: {dict(fb) or 'none'}."]
with open(out + "-data.md", "w") as f:
    f.write("\n".join(L) + "\n")
print(json.dumps({"written": [out + ".json", out + "-data.md"], "label": lab, "window": report["window"], "corridors": corridors}, indent=2))
