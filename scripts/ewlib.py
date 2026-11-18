"""Shared helpers for Early-Warning OS scripts (standard library only)."""
import csv, math, os

CATEGORIES = ["econ", "env", "politics", "social", "media", "other"]
LABELS = {
    "econ": "Economy (jobs, SMEs, prices, remittances)",
    "env": "Weather & environment (drought, floods, harvests)",
    "politics": "Politics & security (decrees, protests, conflict)",
    "social": "Social & health (disease, services, education)",
    "media": "Social media trends (aggregate only)",
    "other": "Other",
}
# v0.1 keys still accepted
ALIASES = {"weather": "env", "policy": "politics", "economy": "econ", "environment": "env",
           "health": "social", "socialmedia": "media", "social_media": "media"}
DEFAULT_WEIGHTS = {"econ": 0.25, "env": 0.20, "politics": 0.20, "social": 0.15, "media": 0.15, "other": 0.05}


def canon(k):
    k = k.strip().lower()
    return ALIASES.get(k, k)


def read_csv(path):
    if not path or not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def pearson(xs, ys):
    n = len(xs)
    if n < 4:
        return None
    mx, my = mean(xs), mean(ys)
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman(xs, ys):
    if len(xs) < 4:
        return None
    return pearson(ranks(xs), ranks(ys))


def quantile(xs, q):
    s = sorted(xs)
    if not s:
        return None
    pos = (len(s) - 1) * q
    lo, hi = int(math.floor(pos)), int(math.ceil(pos))
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


def load_weights(path):
    import json
    w = dict(DEFAULT_WEIGHTS)
    if path and os.path.exists(path):
        with open(path) as f:
            raw = json.load(f)
        w = {k: 0.0 for k in CATEGORIES}
        for k, v in raw.items():
            if k.startswith("_"):
                continue
            k = canon(k)
            if k in w:
                w[k] += float(v)
    total = sum(w.values()) or 1.0
    return {k: w[k] / total for k in CATEGORIES}
