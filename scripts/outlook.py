#!/usr/bin/env python3
"""Forward outlook: what the approved rules say about the next 3, 6 and 12 months.

Usage:
  python3 outlook.py [--horizons 3,6,12] [--rulebook frameworks/rulebook.json]
                     [--features wiki/intel/features.csv] [--outcomes wiki/intel/outcomes.csv]
                     [--as-of 2026-11] [--out reports/outlook/<as-of>]

Logic: a rule "category > X, L periods before -> surge" whose condition is already met
in a known period p predicts a surge at p + L. For each corridor, every future period
up to the longest horizon is checked against every approved rule, using only periods
already observed. Horizons are in months (converted to weeks if features are weekly).
Beyond the longest rule lag the rules cannot see: the outlook says "not covered".
"""
import argparse, datetime as dt, json, os, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ewlib import CATEGORIES, canon, read_csv, fnum, mean
from periods import shift, is_weekly, months_to_periods

ap = argparse.ArgumentParser()
ap.add_argument("--horizons", default="3,6,12")
ap.add_argument("--rulebook", default="frameworks/rulebook.json")
ap.add_argument("--features", default="wiki/intel/features.csv")
ap.add_argument("--outcomes", default="wiki/intel/outcomes.csv")
ap.add_argument("--as-of")
ap.add_argument("--out")
a = ap.parse_args()
H = [int(x) for x in a.horizons.split(",")]

rules = []
if os.path.exists(a.rulebook):
    rules = [r for r in json.load(open(a.rulebook)).get("rules", []) if r.get("status") == "approved"]

feat = defaultdict(dict)
for r in read_csv(a.features):
    feat[r["corridor"]][r["period"]] = {c: fnum(r.get(c)) for c in CATEGORIES}
outs = defaultdict(lambda: defaultdict(float))
for r in read_csv(a.outcomes):
    v = fnum(r.get("value"))
    if v is not None:
        outs[(r["corridor"], r.get("metric", ""))][r["period"]] += v

RANK = {"high": 3, "medium": 2, "low": 1}
if not feat:
    print(json.dumps({"written": [], "note": "no category history yet in features.csv: load history (history-load) or score some periods first"}, indent=2))
    sys.exit(0)
result = {"as_of": None, "horizons_months": H, "approved_rules": len(rules), "corridors": {}}
for corr, rows in sorted(feat.items()):
    known = sorted(rows)
    t0 = a.as_of if a.as_of and a.as_of in rows else known[-1]
    weekly = is_weekly(t0)
    result["as_of"] = result["as_of"] or t0
    maxp = months_to_periods(max(H), weekly)
    scoped = [r for r in rules if "*" in r.get("corridors", ["*"]) or corr in r.get("corridors", [])]
    longest = max([max(int(c.get("lag", 0)) for c in r["conditions"]) for r in scoped], default=0)
    shortest = min([min(int(c.get("lag", 0)) for c in r["conditions"]) for r in scoped], default=0)
    hits = []
    for k in range(1, maxp + 1):
        target = shift(t0, k)
        for r in scoped:
            ok, ev = True, []
            for c in r["conditions"]:
                lag = int(c.get("lag", 0))
                src = shift(target, -lag)
                if src > t0 or src not in rows or rows[src].get(canon(c["category"])) is None:
                    ok = False; break
                v = rows[src][canon(c["category"])]
                if not v > float(c["threshold"]):
                    ok = False; break
                ev.append(f"{canon(c['category'])}={v:g} in {src}")
            if ok:
                hits.append({"period": target, "ahead": k, "rule": r["id"], "name": r.get("name", ""),
                             "confidence": r.get("confidence", "low"), "evidence": ev})
    hz = {}
    for h in H:
        hp = months_to_periods(h, weekly)
        inside = [x for x in hits if x["ahead"] <= hp]
        level = "none"
        if inside:
            best = max(RANK.get(x["confidence"], 1) for x in inside)
            level = {3: "high", 2: "medium", 1: "low"}[best]
        hz[f"{h}m"] = {"periods_ahead": hp, "signal": level,
                       "expected_surge_periods": sorted({x["period"] for x in inside}),
                       "rules": sorted({x["rule"] for x in inside}),
                       "covered_by_rules": hp <= longest if scoped else False,
                       "note": ("no approved rules for this corridor" if not scoped else
                                f"rules look at most {longest} periods ahead; beyond that the outlook is not covered" if hp > longest else "")}
    trend = {}
    for (c2, m), ser in outs.items():
        if c2 != corr:
            continue
        ps = sorted(p for p in ser if p <= t0)
        last3 = [ser[p] for p in ps[-3:]]
        ya = [ser[shift(p, -(52 if weekly else 12))] for p in ps[-3:] if shift(p, -(52 if weekly else 12)) in ser]
        trend[m] = {"last_3_periods": [round(x) for x in last3], "same_periods_year_ago": [round(x) for x in ya],
                    "change_vs_year_ago_pct": round(100 * (sum(last3) - sum(ya)) / sum(ya), 1) if ya and sum(ya) and len(ya) == len(last3) else None}
    result["corridors"][corr] = {"as_of": t0, "horizons": hz, "hits": hits, "outcome_trend": trend,
                                 "rule_lag_range": [shortest, longest]}

out = a.out or f"reports/outlook/{result['as_of']}"
os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
with open(out + ".json", "w") as f:
    json.dump(result, f, indent=2)
L = [f"# Outlook data — as of {result['as_of']}", "", f"Approved rules used: {len(rules)}.", "",
     "| Corridor | " + " | ".join(f"Next {h} months" for h in H) + " |", "|---" * (len(H) + 1) + "|"]
for corr, d in result["corridors"].items():
    cells = []
    for h in H:
        z = d["horizons"][f"{h}m"]
        txt = z["signal"].upper() if z["signal"] != "none" else "no signal"
        if z["expected_surge_periods"]:
            txt += f": surge expected {', '.join(z['expected_surge_periods'][:4])} ({', '.join(z['rules'])})"
        if z["note"]:
            txt += f" — {z['note']}"
        cells.append(txt)
    L.append(f"| {corr} | " + " | ".join(cells) + " |")
L += ["", "Signal = the highest confidence among approved rules predicting a surge inside the horizon. 'No signal' means no approved rule fires, not that nothing will happen."]
with open(out + "-data.md", "w") as f:
    f.write("\n".join(L) + "\n")
print(json.dumps({"written": [out + ".json", out + "-data.md"], "as_of": result["as_of"],
                  "summary": {c: {k: v["signal"] for k, v in d["horizons"].items()} for c, d in result["corridors"].items()}}, indent=2))
