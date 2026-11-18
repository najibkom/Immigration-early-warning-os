#!/usr/bin/env python3
"""Learn early-warning rules from history (the "learn-rules" step).

Usage:
  python3 learn.py --features wiki/intel/features.csv --outcomes wiki/intel/outcomes.csv \
      [--metric arrivals] [--max-lag 6] [--test-share 0.3] [--surge-q 0.75] \
      [--out drafts/rule-candidates-YYYY-MM-DD]

What it does, per corridor and pooled across corridors:
 1. Joins category indices (features) with the migration outcome (outcomes) by period.
 2. Correlation: for each category and lag 0..max-lag (index at t-lag vs outcome at t),
    Pearson and Spearman, on a TRAIN part (oldest periods) and a TEST part (newest).
 3. Rules: "category > threshold, lag L periods before -> surge", where surge = outcome
    above its train-set quantile (default 75th percentile). Singles and pairs (AND).
    Kept if they fire at least 3 times in train with lift >= 1.5; then checked on test.
 4. Proposed weights: positive test correlations at each category's best train lag,
    shrunk toward the current weights when history is short.
Writes <out>.json (machine) and <out>.md (human report). Proposes; never changes the rulebook.
"""
import argparse, json, os, sys, datetime
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ewlib import CATEGORIES, LABELS, read_csv, fnum, pearson, spearman, quantile, load_weights

ap = argparse.ArgumentParser()
ap.add_argument("--features", default="wiki/intel/features.csv")
ap.add_argument("--outcomes", default="wiki/intel/outcomes.csv")
ap.add_argument("--metric", default=None)
ap.add_argument("--weights", default="frameworks/weights.json")
ap.add_argument("--max-lag", type=int, default=12)
ap.add_argument("--test-share", type=float, default=0.3)
ap.add_argument("--surge-q", type=float, default=0.75)
ap.add_argument("--thresholds", default="60,70,80")
ap.add_argument("--out", default=f"drafts/rule-candidates-{datetime.date.today().isoformat()}")
a = ap.parse_args()
THR = [float(x) for x in a.thresholds.split(",")]

feat = defaultdict(dict)   # corridor -> period -> {cat: value}
for r in read_csv(a.features):
    feat[r["corridor"]][r["period"]] = {c: fnum(r.get(c)) for c in CATEGORIES}

outc = defaultdict(dict)   # corridor -> period -> value
metrics = set()
for r in read_csv(a.outcomes):
    metrics.add(r.get("metric"))
    if a.metric and r.get("metric") != a.metric:
        continue
    v = fnum(r.get("value"))
    if v is not None:
        outc[r["corridor"]][r["period"]] = outc[r["corridor"]].get(r["period"], 0) + v
if not a.metric and len(metrics) > 1:
    sys.exit(f"several outcome metrics found {sorted(m for m in metrics if m)}: pick one with --metric")

def series(corr):
    periods = sorted(set(feat[corr]) | set(outc[corr]))
    return periods, [feat[corr].get(p, {}) for p in periods], [outc[corr].get(p) for p in periods]

def pairs(X, Y, cat, lag, idx):
    xs, ys = [], []
    for t in idx:
        if t - lag < 0:
            continue
        x, y = X[t - lag].get(cat), Y[t]
        if x is not None and y is not None:
            xs.append(x); ys.append(y)
    return xs, ys

def rule_stats(X, Y, conds, idx, surge):
    fire = hit = base_n = base_hit = 0
    for t in idx:
        if Y[t] is None:
            continue
        ok = True
        for cat, thr, lag in conds:
            if t - lag < 0 or X[t - lag].get(cat) is None:
                ok = None; break
            if not X[t - lag][cat] > thr:
                ok = False
        if ok is None:
            continue
        s = Y[t] > surge
        base_n += 1; base_hit += s
        if ok:
            fire += 1; hit += s
    if base_n == 0:
        return None
    base = base_hit / base_n
    prec = hit / fire if fire else None
    lift = (prec / base) if (prec is not None and base > 0) else None
    recall = hit / base_hit if base_hit else None
    return {"fires": fire, "hits": hit, "precision": prec, "base_rate": round(base, 3),
            "lift": lift, "recall": recall, "n": base_n}

def rnd(x, k=3):
    return None if x is None else round(x, k)

def analyse(name, X, Y):
    n = len(Y)
    valid = [t for t in range(n) if Y[t] is not None]
    if len(valid) < 8:
        return {"corridor": name, "periods": len(valid), "skipped": "fewer than 8 periods with outcomes"}
    cut = valid[int(len(valid) * (1 - a.test_share))]
    train = [t for t in valid if t < cut]
    test = [t for t in valid if t >= cut]
    surge = quantile([Y[t] for t in train], a.surge_q)

    corr = {}
    for c in CATEGORIES:
        best = None
        rows = []
        for L in range(0, a.max_lag + 1):
            xt, yt = pairs(X, Y, c, L, train)
            xs, ys = pairs(X, Y, c, L, test)
            r_tr, r_te = pearson(xt, yt), pearson(xs, ys)
            row = {"lag": L, "r_train": rnd(r_tr), "rho_train": rnd(spearman(xt, yt)),
                   "r_test": rnd(r_te), "n_train": len(xt), "n_test": len(xs)}
            rows.append(row)
            if r_tr is not None and (best is None or abs(r_tr) > abs(best["r_train"])):
                best = row
        corr[c] = {"best": best, "by_lag": rows}

    singles = []
    for c in CATEGORIES:
        for L in range(0, a.max_lag + 1):
            for thr in THR:
                tr = rule_stats(X, Y, [(c, thr, L)], train, surge)
                if tr and tr["fires"] >= 3 and tr["lift"] and tr["lift"] >= 1.5:
                    te = rule_stats(X, Y, [(c, thr, L)], test, surge)
                    singles.append({"conditions": [{"category": c, "op": ">", "threshold": thr, "lag": L}],
                                    "train": tr, "test": te})
    # keep the best threshold/lag per category, then pair the top singles
    best_single = {}
    for s in singles:
        c = s["conditions"][0]["category"]
        if c not in best_single or (s["train"]["lift"], s["train"]["fires"]) > (best_single[c]["train"]["lift"], best_single[c]["train"]["fires"]):
            best_single[c] = s
    pair_rules = []
    keys = list(best_single)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            c1 = best_single[keys[i]]["conditions"][0]; c2 = best_single[keys[j]]["conditions"][0]
            conds = [(c1["category"], c1["threshold"], c1["lag"]), (c2["category"], c2["threshold"], c2["lag"])]
            tr = rule_stats(X, Y, conds, train, surge)
            if tr and tr["fires"] >= 3 and tr["lift"] and tr["lift"] >= 1.5:
                pair_rules.append({"conditions": [c1, c2], "train": tr, "test": rule_stats(X, Y, conds, test, surge)})

    rules = list(best_single.values()) + pair_rules
    for r in rules:
        te = r["test"] or {}
        lift_te, fires_te = te.get("lift"), te.get("fires", 0)
        if lift_te and lift_te >= 1.5 and fires_te >= 3 and len(valid) >= 24:
            conf = "high"
        elif lift_te and lift_te >= 1.2 and fires_te >= 2:
            conf = "medium"
        else:
            conf = "low"
        r["confidence"] = conf
        r["points"] = {"high": 10, "medium": 6, "low": 3}[conf]
        for part in ("train", "test"):
            if r[part]:
                for k in ("precision", "lift", "recall"):
                    r[part][k] = rnd(r[part][k], 2)
    rules.sort(key=lambda r: ({"high": 0, "medium": 1, "low": 2}[r["confidence"]],
                              -((r["test"] or {}).get("lift") or 0), -r["train"]["lift"]))
    return {"corridor": name, "periods": len(valid), "train_periods": len(train), "test_periods": len(test),
            "train_range": [periods_of[name][train[0]], periods_of[name][train[-1]]],
            "test_range": [periods_of[name][test[0]], periods_of[name][test[-1]]],
            "surge_threshold": rnd(surge, 2), "correlations": corr, "rules": rules}

results = []
periods_of = {}
corridors = sorted(set(feat) & set(outc))
pooled_X, pooled_Y = [], []
for corr in corridors:
    P, X, Y = series(corr)
    periods_of[corr] = P
    results.append(analyse(corr, X, Y))

# proposed weights from pooled evidence: average positive test r at each category's best train lag
cur = load_weights(a.weights)
score = {c: [] for c in CATEGORIES}
nper = 0
for res in results:
    if "correlations" not in res:
        continue
    nper += res["periods"]
    for c in CATEGORIES:
        b = res["correlations"][c]["best"]
        if b and b["r_train"] is not None and b["r_test"] is not None and b["r_train"] > 0 and b["r_test"] > 0:
            score[c].append(b["r_test"])
        else:
            score[c].append(0.0)
raw = {c: (sum(v) / len(v) if v else 0.0) for c, v in score.items()}
tot = sum(raw.values())
alpha = min(1.0, nper / 48.0) if tot > 0 else 0.0   # trust learned weights more with more history
if tot > 0:
    floor = 0.02   # keep every category slightly in view so no blind spot is learned in
    raw = {c: max(raw[c], floor * tot) for c in CATEGORIES}
    tot = sum(raw.values())
    learned = {c: raw[c] / tot for c in CATEGORIES}
    proposed = {c: round((1 - alpha) * cur[c] + alpha * learned[c], 4) for c in CATEGORIES}
    s = sum(proposed.values()); proposed = {c: round(v / s, 4) for c, v in proposed.items()}
else:
    learned, proposed = None, cur

report = {"generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
          "metric": a.metric or (sorted(m for m in metrics if m) or [None])[0],
          "settings": {"max_lag": a.max_lag, "test_share": a.test_share, "surge_quantile": a.surge_q, "thresholds": THR},
          "current_weights": {k: round(v, 4) for k, v in cur.items()},
          "learned_weights": None if learned is None else {k: round(v, 4) for k, v in learned.items()},
          "shrinkage_alpha": round(alpha, 2), "proposed_weights": proposed,
          "corridors": results}
os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
with open(a.out + ".json", "w") as f:
    json.dump(report, f, indent=2)

# human report
L = [f"# Rule candidates — {report['metric']} — {report['generated'][:10]}", "",
     "Status: PROPOSED. Nothing is used until a human approves it into frameworks/rulebook.json.", "",
     "## Proposed weights", "", "| Category | Current | Learned | Proposed |", "|---|---|---|---|"]
for c in CATEGORIES:
    lw = "–" if learned is None else f"{learned[c]:.2f}"
    L.append(f"| {LABELS[c]} | {cur[c]:.2f} | {lw} | {proposed[c]:.2f} |")
L += ["", f"Shrinkage toward current weights: alpha = {alpha:.2f} (1.0 = fully learned; reached at 48 corridor-periods).", ""]
for res in results:
    L += [f"## Corridor: {res['corridor']}", ""]
    if "skipped" in res:
        L += [f"Skipped: {res['skipped']} ({res['periods']} periods).", ""]
        continue
    L += [f"Periods with outcomes: {res['periods']} (train {res['train_range'][0]}–{res['train_range'][1]}, "
          f"test {res['test_range'][0]}–{res['test_range'][1]}). Surge = {report['metric']} above {res['surge_threshold']}.", "",
          "### Lead indicators (best lag on train, checked on test)", "",
          "| Category | Best lag | r train | r test | Holds on test? |", "|---|---|---|---|---|"]
    for c in CATEGORIES:
        b = res["correlations"][c]["best"]
        if not b:
            L.append(f"| {LABELS[c]} | – | – | – | no data |"); continue
        holds = "yes" if (b["r_test"] is not None and b["r_train"] is not None and b["r_train"] * b["r_test"] > 0 and abs(b["r_test"]) >= 0.2) else "no"
        L.append(f"| {LABELS[c]} | {b['lag']} | {b['r_train']} | {b['r_test']} | {holds} |")
    L += ["", "### Rule candidates", "", "| # | Rule | Train lift (fires) | Test lift (fires) | Test precision | Confidence | Points |", "|---|---|---|---|---|---|---|"]
    if not res["rules"]:
        L.append("| – | No rule met the minimum (3 fires, lift 1.5 on train) | | | | | |")
    for i, r in enumerate(res["rules"], 1):
        cond = " AND ".join(f"{c['category']} > {c['threshold']:g} ({c['lag']} periods before)" for c in r["conditions"])
        te = r["test"] or {}
        L.append(f"| {i} | {cond} → surge | {r['train']['lift']} ({r['train']['fires']}) | {te.get('lift')} ({te.get('fires', 0)}) | {te.get('precision')} | {r['confidence']} | {r['points']} |")
    L.append("")
L += ["## Read with care", "",
      "- Correlation is not causation: these are warning signs, not explanations.",
      "- Lift = how much more often a surge follows when the rule fires, compared with normal (1.0 = no better than chance).",
      "- Low-confidence rules are shown for discussion; approve them only with a domain reason.",
      "- Re-run every quarter as new outcome data arrives."]
with open(a.out + ".md", "w") as f:
    f.write("\n".join(L) + "\n")
print(json.dumps({"written": [a.out + ".md", a.out + ".json"], "corridors": len(results),
                  "rules": sum(len(r.get("rules", [])) for r in results), "proposed_weights": proposed}, indent=2))
