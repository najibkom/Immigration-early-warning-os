#!/usr/bin/env python3
"""Closed-loop recalibration (Quality Gate 3 feedback).

Usage:
  python3 recalibrate.py <weights.json> <vector> [--pct 2]

Lowers one sub-index weight by --pct percent (relative, default 2%), renormalises
all four weights to sum to 1, and writes the file back. Prints old and new weights.
Vectors: social, econ, weather, policy.
"""
import json, sys, argparse

ap = argparse.ArgumentParser()
ap.add_argument("weights")
ap.add_argument("vector", choices=["social", "econ", "weather", "policy"])
ap.add_argument("--pct", type=float, default=2.0)
a = ap.parse_args()

with open(a.weights) as f:
    w = json.load(f)
old = dict(w)
w[a.vector] = w[a.vector] * (1 - a.pct / 100)
total = sum(w[k] for k in ["social", "econ", "weather", "policy"])
for k in ["social", "econ", "weather", "policy"]:
    w[k] = round(w[k] / total, 4)
with open(a.weights, "w") as f:
    json.dump(w, f, indent=2)
print(json.dumps({"old": old, "new": w}, indent=2))
