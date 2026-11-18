#!/usr/bin/env python3
"""Early-Warning OS scoring engine (Layer 3).

Usage:
  python3 score.py <signal.json> [--weights frameworks/weights.json] [--history alerts/history.csv]

signal.json fields:
  corridor            corridor slug, e.g. "sahel-to-morocco-coast"
  indices             {"social": 0-100, "econ": 0-100, "weather": 0-100, "policy": 0-100}
  source_ids          list of Source IDs from wiki/intel/sources.csv (required, Gate 2)
  contradictory_policy  optional bool: conflicting decrees detected (forces HITL)

history.csv columns: date,corridor,s_final  (one row per scored day)

Prints a JSON result: s_total, C, s_final, tier, action, anomaly, hitl, reasons.
"""
import csv, json, math, sys, argparse, datetime, os

DEFAULT_WEIGHTS = {"social": 0.25, "econ": 0.30, "weather": 0.25, "policy": 0.20}
VECTOR_THRESHOLD = 70
TIERS = [
    (85, "Critical Shock", "Emergency protocol: human-in-the-loop hold before broadcast (SMS, high-priority webhook, executive briefing)"),
    (70, "Elevated Risk", "Priority alert with prescriptive briefing (dedicated Slack/Teams channel, webhooks)"),
    (40, "Watchlist / Moderate", "Queue for the weekly executive intelligence digest"),
    (0,  "Baseline / Low", "Silent log to the operational archive; no notification"),
]


def load_weights(path):
    if path and os.path.exists(path):
        with open(path) as f:
            w = json.load(f)
        w = {k: float(w[k]) for k in DEFAULT_WEIGHTS}
    else:
        w = dict(DEFAULT_WEIGHTS)
    total = sum(w.values())
    return {k: v / total for k, v in w.items()}  # always renormalise to 1


def corroboration(indices):
    above = [k for k, v in indices.items() if v > VECTOR_THRESHOLD]
    n = len(above)
    if n >= 3:
        return 1.30, above, "three or more vectors above threshold: high-confidence factor"
    if n == 2:
        return 1.15, above, "two independent vectors above threshold: amplification factor"
    if n == 1:
        return 0.85, above, "single-vector signal: damping factor"
    return 1.00, above, "no vector above threshold: neutral"


def anomaly(history_path, corridor, current):
    if not history_path or not os.path.exists(history_path):
        return {"checked": False, "reason": "no history file"}
    today = datetime.date.today()
    vals30, vals90 = [], []
    with open(history_path) as f:
        for row in csv.DictReader(f):
            if row.get("corridor") != corridor:
                continue
            try:
                d = datetime.date.fromisoformat(row["date"])
                v = float(row["s_final"])
            except (KeyError, ValueError):
                continue
            age = (today - d).days
            if 0 < age <= 30:
                vals30.append(v)
            if 0 < age <= 90:
                vals90.append(v)
    if len(vals30) < 7:
        return {"checked": False, "reason": f"only {len(vals30)} points in the last 30 days (need 7)"}
    mean = sum(vals30) / len(vals30)
    sd = math.sqrt(sum((v - mean) ** 2 for v in vals30) / (len(vals30) - 1))
    z = (current - mean) / sd if sd > 0 else 0.0
    return {
        "checked": True,
        "mean_30d": round(mean, 2), "sd_30d": round(sd, 2),
        "mean_90d": round(sum(vals90) / len(vals90), 2) if vals90 else None,
        "z": round(z, 2), "flag": abs(z) > 2.5,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("signal")
    ap.add_argument("--weights", default="frameworks/weights.json")
    ap.add_argument("--history", default="alerts/history.csv")
    a = ap.parse_args()

    with open(a.signal) as f:
        sig = json.load(f)
    idx = {k: float(sig["indices"].get(k, 0)) for k in DEFAULT_WEIGHTS}
    for k, v in idx.items():
        if not 0 <= v <= 100:
            sys.exit(f"index {k}={v} is outside 0-100")

    reasons = []
    w = load_weights(a.weights)
    s_total = sum(w[k] * idx[k] for k in w)
    C, above, why = corroboration(idx)
    s_final = min(100.0, s_total * C)
    reasons.append(why)

    tier, action = next((t, act) for floor, t, act in TIERS if s_final >= floor)
    an = anomaly(a.history, sig.get("corridor"), s_final)
    if an.get("flag"):
        reasons.append(f"anomaly: {an['z']} sigma from the 30-day baseline")
        if s_final < 70:
            tier, action = "Watchlist / Moderate (anomaly)", "Anomaly flag: route to analyst for review even below 70"

    hitl = s_final >= 85 or bool(sig.get("contradictory_policy"))
    if sig.get("contradictory_policy"):
        reasons.append("contradictory regulatory text: automated broadcast frozen")
    if not sig.get("source_ids"):
        reasons.append("GATE 2 FAIL: no Source IDs, score cannot be published")

    print(json.dumps({
        "corridor": sig.get("corridor"),
        "weights": {k: round(v, 4) for k, v in w.items()},
        "indices": idx,
        "contributions": {k: round(w[k] * idx[k], 2) for k in w},
        "top_driver": max(w, key=lambda k: w[k] * idx[k]),
        "vectors_above_70": above,
        "s_total": round(s_total, 2), "C": C, "s_final": round(s_final, 2),
        "tier": tier, "action": action, "hitl_required": hitl,
        "anomaly": an, "reasons": reasons,
    }, indent=2))


if __name__ == "__main__":
    main()
