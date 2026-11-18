#!/usr/bin/env python3
"""Weight changes for Early-Warning OS.

Feedback mode (one false positive):
  python3 recalibrate.py frameworks/weights.json --lower <category> [--pct 2]
Apply learned weights (after a human approves a learn-rules report):
  python3 recalibrate.py frameworks/weights.json --from drafts/rule-candidates-YYYY-MM-DD.json

Categories: econ, env, politics, social, media, other (v0.1 names weather/policy accepted).
Weights are always renormalised to sum to 1. Prints old and new.
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ewlib import CATEGORIES, canon, load_weights

ap = argparse.ArgumentParser()
ap.add_argument("weights")
ap.add_argument("--lower")
ap.add_argument("--pct", type=float, default=2.0)
ap.add_argument("--from", dest="src")
a = ap.parse_args()

old = load_weights(a.weights)
new = dict(old)
if a.src:
    with open(a.src) as f:
        new = {canon(k): float(v) for k, v in json.load(f)["proposed_weights"].items()}
elif a.lower:
    c = canon(a.lower)
    if c not in CATEGORIES:
        sys.exit(f"unknown category {a.lower}")
    new[c] = new[c] * (1 - a.pct / 100)
else:
    sys.exit("give --lower <category> or --from <report.json>")
tot = sum(new.get(c, 0) for c in CATEGORIES)
new = {c: round(new.get(c, 0) / tot, 4) for c in CATEGORIES}
with open(a.weights, "w") as f:
    json.dump(new, f, indent=2)
print(json.dumps({"old": {k: round(v, 4) for k, v in old.items()}, "new": new}, indent=2))
