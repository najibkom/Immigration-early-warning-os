"""Period helpers: calendar windows for reports and period-label arithmetic."""
import datetime as dt

KINDS = {"week": "Weekly", "month": "Monthly", "quarter": "Quarterly", "half": "6-month", "year": "Annual"}


def window(kind, end):
    """Calendar window [start, end] of the given kind containing date `end`."""
    if kind == "week":
        start = end - dt.timedelta(days=end.weekday())
        return start, start + dt.timedelta(days=6)
    if kind == "month":
        start = end.replace(day=1)
    elif kind == "quarter":
        start = dt.date(end.year, 3 * ((end.month - 1) // 3) + 1, 1)
    elif kind == "half":
        start = dt.date(end.year, 1 if end.month <= 6 else 7, 1)
    elif kind == "year":
        start = dt.date(end.year, 1, 1)
    else:
        raise ValueError(kind)
    months = {"month": 1, "quarter": 3, "half": 6, "year": 12}[kind]
    nxt = add_months(start, months)
    return start, nxt - dt.timedelta(days=1)


def previous(kind, start):
    return window(kind, start - dt.timedelta(days=1))


def year_ago(kind, start):
    try:
        d = start.replace(year=start.year - 1)
    except ValueError:
        d = start.replace(year=start.year - 1, day=28)
    return window(kind, d)


def add_months(d, n):
    m = d.month - 1 + n
    y = d.year + m // 12
    return dt.date(y, m % 12 + 1, 1)


def label(kind, start):
    if kind == "week":
        y, w, _ = start.isocalendar()
        return f"{y}-W{w:02d}"
    if kind == "month":
        return start.strftime("%Y-%m")
    if kind == "quarter":
        return f"{start.year}-Q{(start.month - 1) // 3 + 1}"
    if kind == "half":
        return f"{start.year}-H{1 if start.month <= 6 else 2}"
    return str(start.year)


def period_start(p):
    """'2024-03' -> 2024-03-01; '2024-W11' -> Monday of ISO week 11."""
    p = p.strip()
    if "-W" in p:
        y, w = p.split("-W")
        return dt.date.fromisocalendar(int(y), int(w), 1)
    y, m = p.split("-")[:2]
    return dt.date(int(y), int(m), 1)


def is_weekly(p):
    return "-W" in p


def shift(p, k):
    """Move a period label k periods forward (negative = back)."""
    if is_weekly(p):
        d = period_start(p) + dt.timedelta(weeks=k)
        y, w, _ = d.isocalendar()
        return f"{y}-W{w:02d}"
    d = add_months(period_start(p), k)
    return d.strftime("%Y-%m")


def months_to_periods(months, weekly):
    return round(months * 52 / 12) if weekly else months
