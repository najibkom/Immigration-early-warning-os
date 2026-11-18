#!/usr/bin/env python3
"""Early-Warning OS scoring engine (Layer 3), v0.2.

Usage:
  python3 score.py <signal.json> [--weights frameworks/weights.json] [--rulebook frameworks/rulebook.json]
                   [--features wiki/intel/features.csv] [--history alerts/history.csv] [--record]

signal.json:
  corridor     corridor slug
  period       e.g. 2026-11 or 2026-W47 (same granularity as features.csv)
  indices      {"econ","env","politics","social","media","other"}: 0-100 each (v0.1 keys weather/policy accepted)
  source_ids   list of Source IDs (required for Gate 2)
  contradictory_policy  optional bool

Steps: weighted base score -> + points of every approved rulebook rule that fires
(lagged conditions read from features.csv; bonus capped at 20) -> x corroboration
multiplier C -> S_final (max 100) -> tier -> 2.5-sigma anomaly check.
--record writes this period's indices into features.csv (replacing the same period).
"""
import argparse, csv, datetime, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ewlib import CATEGORIES, canon, read_csv, fnum, load_weights

VECTOR_THRESHOLD = 70
BONUS_CAP = 20
TIERS = [
    (85, "Critical Shock", "Emergency protocol: human-in-the-loop hold before broadcast (SMS, high-priority webhook, executive briefing)"),
    (70, "Elevated Risk", "Priority alert with prescriptive briefing (dedicated Slack/Teams channel, webhooks)"),
    (40, "Watchlist / Moderate", "Queue for the weekly executive intelligence digest"),
    (0, "Baseline / Low", "Silent log to the operational archive; no notification"),
]


def corroboration(idx):
    above = [k for k in CATEGORIES if k != "other" and idx[k] > VECTOR_THRESHOLD]
    n = len(above)
    if n >= 3:
        return 1.30, above, "three or more categories above 70: high-confidence factor"
    if n == 2:
        return 1.15, above, "two independent categories above 70: amplification factor"
    if n == 1:
        return 0.85, above, "single-category signal: damping factor"
    return 1.00, above, "no category above 70: neutral"


def history_series(features, corridor, period, idx):
    rows = {r["period"]: {c: fnum(r.get(c)) for c in CATEGORIES} for r in read_csv(features) if r.get("corridor") == corridor}
    rows[period] = dict(idx)
    order = sorted(rows)
    return order, rows


def apply_rules(rulebook, corridor, period, order, rows):
    fired, missing = [], []
    if not rulebook or not os.path.exists(rulebook):
        return fired, missing, 0.0
    with open(rulebook) as f:
        book = json.load(f)
    t = order.index(period)
    for rule in book.get("rules", []):
        if rule.get("status") != "approved":
            continue
        scope = rule.get("corridors", ["*"])
        if "*" not in scope and corridor not in scope:
            continue
        ok, why = True, []
        for c in rule["conditions"]:
            cat, thr, lag = canon(c["category"]), float(c["threshold"]), int(c.get("lag", 0))
            if t - lag < 0 or rows[order[t - lag]].get(cat) is None:
                ok = None
                missing.append(f"{rule['id']}: no {cat} value {lag} periods before {period}")
                break
            v = rows[order[t - lag]][cat]
            why.append(f"{cat}={v:g} in {order[t - lag]} (>{thr:g})")
            if not v > thr:
                ok = False
        if ok:
            fired.append({"id": rule["id"], "name": rule.get("name", ""), "points": float(rule.get("points", 5)),
                          "confidence": rule.get("confidence"), "evidence": why})
    bonus = min(BONUS_CAP, sum(r["points"] for r in fired))
    return fired, missing, bonus


def anomaly(history_path, corridor, current):
    rows = read_csv(history_path)
    today = datetime.date.today()
    v30, v90 = [], []
    for r in rows:
        if r.get("corridor") != corridor:
            continue
        try:
            age = (today - datetime.date.fromisoformat(r["date"])).days
            v = float(r["s_final"])
        except (KeyError, ValueError):
            continue
        if 0 < age <= 30:
            v30.append(v)
        if 0 < age <= 90:
            v90.append(v)
    if len(v30) < 7:
        return {"checked": False, "reason": f"only {len(v30)} points in the last 30 days (need 7)"}
    m = sum(v30) / len(v30)
    sd = math.sqrt(sum((v - m) ** 2 for v in v30) / (len(v30) - 1))
    z = (current - m) / sd if sd > 0 else 0.0
    return {"checked": True, "mean_30d": round(m, 2), "sd_30d": round(sd, 2),
            "mean_90d": round(sum(v90) / len(v90), 2) if v90 else None, "z": round(z, 2), "flag": abs(z) > 2.5}


def record(features, corridor, period, idx, source_ids):
    rows = read_csv(features)
    rows = [r for r in rows if not (r.get("corridor") == corridor and r.get("period") == period)]
    rows.append({"period": period, "corridor": corridor, **{c: idx[c] for c in CATEGORIES},
                 "n_indicators": "", "source_ids": " ".join(source_ids)})
    rows.sort(key=lambda r: (r["corridor"], r["period"]))
    os.makedirs(os.path.dirname(features) or ".", exist_ok=True)
    with open(features, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["period", "corridor"] + CATEGORIES + ["n_indicators", "source_ids"])
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in w.fieldnames})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("signal")
    ap.add_argument("--weights", default="frameworks/weights.json")
    ap.add_argument("--rulebook", default="frameworks/rulebook.json")
    ap.add_argument("--features", default="wiki/intel/features.csv")
    ap.add_argument("--history", default="alerts/history.csv")
    ap.add_argument("--record", action="store_true")
    a = ap.parse_args()

    with open(a.signal) as f:
        sig = json.load(f)
    idx = {c: 0.0 for c in CATEGORIES}
    gaps = []
    given = {canon(k): v for k, v in sig.get("indices", {}).items()}
    for c in CATEGORIES:
        if c in given and given[c] is not None:
            v = float(given[c])
            if not 0 <= v <= 100:
                sys.exit(f"index {c}={v} is outside 0-100")
            idx[c] = v
        elif c != "other":
            gaps.append(c)
    corridor = sig.get("corridor")
    period = sig.get("period") or datetime.date.today().strftime("%Y-%m")

    w = load_weights(a.weights)
    base = sum(w[c] * idx[c] for c in CATEGORIES)
    order, rows = history_series(a.features, corridor, period, idx)
    fired, missing, bonus = apply_rules(a.rulebook, corridor, period, order, rows)
    s_total = min(100.0, base + bonus)
    C, above, why = corroboration(idx)
    s_final = min(100.0, s_total * C)
    reasons = [why]
    if gaps:
        reasons.append("data gap (scored as 0): " + ", ".join(gaps))

    tier, action = next((t, act) for floor, t, act in TIERS if s_final >= floor)
    an = anomaly(a.history, corridor, s_final)
    if an.get("flag"):
        reasons.append(f"anomaly: {an['z']} sigma from the 30-day baseline")
        if s_final < 70:
            tier, action = "Watchlist / Moderate (anomaly)", "Anomaly flag: route to analyst for review even below 70"
    hitl = s_final >= 85 or bool(sig.get("contradictory_policy"))
    if sig.get("contradictory_policy"):
        reasons.append("contradictory official texts: automated broadcast frozen")
    if not sig.get("source_ids"):
        reasons.append("GATE 2 FAIL: no Source IDs, score cannot be published")
    if a.record:
        record(a.features, corridor, period, idx, sig.get("source_ids", []))

    contrib = {c: round(w[c] * idx[c], 2) for c in CATEGORIES}
    print(json.dumps({
        "corridor": corridor, "period": period,
        "weights": {k: round(v, 4) for k, v in w.items()}, "indices": idx, "contributions": contrib,
        "top_driver": max(contrib, key=contrib.get),
        "base_score": round(base, 2),
        "rules_fired": fired, "rule_bonus": round(bonus, 2), "rules_not_checked": missing,
        "categories_above_70": above, "s_total": round(s_total, 2), "C": C, "s_final": round(s_final, 2),
        "tier": tier, "action": action, "hitl_required": hitl, "anomaly": an, "reasons": reasons,
        "recorded_to_features": a.record,
    }, indent=2))


if __name__ == "__main__":
    main()
