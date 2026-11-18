#!/usr/bin/env python3
"""Turn raw indicators into 0-100 category indices per corridor and period.

Usage:
  python3 to_index.py indicators.csv --out wiki/intel/features.csv [--merge]

indicators.csv columns:
  period      sortable label, same granularity everywhere: 2024-03 (monthly) or 2024-W11 (weekly)
  corridor    corridor slug
  category    econ | env | politics | social | media | other
  indicator   name, e.g. youth_unemployment_pct, protest_events, cholera_cases, drought_spi
  value       number
  direction   +1 if higher = more pressure (default), -1 if higher = less pressure (e.g. rainfall)
  source_id   SRC-xxx

Method: for each corridor x indicator, the value's percentile rank within that
indicator's own history (direction applied) x 100. A category index for a period
is the mean of its indicators' indices that period. Transparent, robust to units,
and every index can be traced to its indicators and sources.

Output (features.csv): period,corridor,econ,env,politics,social,media,other,n_indicators,source_ids
--merge keeps existing rows for (period, corridor) pairs not in the new file.
"""
import argparse, csv, os, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ewlib import CATEGORIES, canon, read_csv, fnum, mean

ap = argparse.ArgumentParser()
ap.add_argument("indicators")
ap.add_argument("--out", default="wiki/intel/features.csv")
ap.add_argument("--merge", action="store_true")
a = ap.parse_args()

rows = read_csv(a.indicators)
series = defaultdict(list)          # (corridor, indicator) -> [(period, value, dir, cat, src)]
bad = 0
for r in rows:
    v = fnum(r.get("value"))
    cat = canon(r.get("category", ""))
    if v is None or cat not in CATEGORIES or not r.get("period") or not r.get("corridor"):
        bad += 1
        continue
    d = -1.0 if str(r.get("direction", "1")).strip() in ("-1", "-") else 1.0
    series[(r["corridor"], r["indicator"])].append((r["period"], v * d, cat, r.get("source_id", "")))

cell = defaultdict(lambda: defaultdict(list))   # (period, corridor) -> cat -> [index]
srcs = defaultdict(set)
for (corr, ind), pts in series.items():
    vals = [p[1] for p in pts]
    n = len(vals)
    for period, v, cat, src in pts:
        below = sum(1 for x in vals if x < v)
        equal = sum(1 for x in vals if x == v)
        pct = (below + 0.5 * equal) / n if n > 1 else 0.5
        cell[(period, corr)][cat].append(round(pct * 100, 1))
        if src:
            srcs[(period, corr)].add(src)

out = {}
if a.merge:
    for r in read_csv(a.out):
        out[(r["period"], r["corridor"])] = r
for key, cats in cell.items():
    period, corr = key
    row = {"period": period, "corridor": corr}
    for c in CATEGORIES:
        m = mean(cats.get(c, []))
        row[c] = "" if m is None else round(m, 1)
    row["n_indicators"] = sum(len(v) for v in cats.values())
    row["source_ids"] = " ".join(sorted(srcs[key]))
    out[key] = row

os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
with open(a.out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["period", "corridor"] + CATEGORIES + ["n_indicators", "source_ids"])
    w.writeheader()
    for key in sorted(out, key=lambda k: (k[1], k[0])):
        w.writerow(out[key])
print(f"wrote {len(out)} corridor-period rows to {a.out} ({len(series)} indicator series, {bad} rows skipped)")
