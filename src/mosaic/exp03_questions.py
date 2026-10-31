"""exp03 question set (Task 2, step 2): market events -> ordered scenario sets (bins), the realised bin, the market's
benchmark distribution, windows, and the list of exclusions with reasons.

Input: the flat records of `exp03_gt` (one per settled market). Strike and label parsing is pmpol's
(`pmpol.propositions.indicators.label_span`, team code, vendor/pmpol-academic): every contract becomes a half-open
span [lo, hi) in grid steps (CPI 0.1 pp, FOMC 25 bp). Breakpoints of all spans cut the line into elementary bins;
those bins are the scenario set. An event is kept when its contracts partition the outcome space after mapping:

  * ray ladder ("above x", "below y"): always a partition (the breakpoints are the thresholds);
  * exclusive labels / ranges: the spans must be pairwise disjoint and cover the whole line;
  * anything else (mixed rays and ranges, overlapping labels, labels pmpol does not read) is excluded and listed.

The realised bin is the single elementary bin consistent with every contract's yes/no result; if none or several fit
the event is excluded. Nothing here scores a forecast. Outcomes are stored as data for the later registered scoring.
"""

from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from mosaic.exp03_gt import KALSHI_SERIES, use_pmpol

INF = math.inf
CAL_START, TEST_START = "2025-05-01", "2026-01-01"
HORIZONS = (7, 1)  # days before close: primary, secondary
_MON = {m: i for i, m in enumerate(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV",
                                    "DEC"], 1)}


def window_of(close_iso: str) -> str:
    d = close_iso[:10]
    return "pre" if d < CAL_START else "calibration" if d < TEST_START else "test"


def period_of(event_id: str) -> str:
    """Reference period from a Kalshi event ticker like KXCPI-25AUG (-> 2025-08); '' when not of that form."""
    m = re.search(r"-(\d\d)([A-Z]{3})(\d\d)?$", event_id)
    return f"20{m.group(1)}-{_MON[m.group(2)]:02d}" if m and m.group(2) in _MON else ""


def forecast_date(close_iso: str, days: int) -> str:
    t = datetime.fromisoformat(close_iso.replace("Z", "+00:00")).astimezone(timezone.utc)
    return (t.date() - timedelta(days=days)).isoformat()


def norm_label(label: str) -> str:
    """Kalshi central-bank labels vary by series ('Cut 25 basis points', 'Hike more than 25bp'); pmpol's grammar
    reads 'bps'. Only the unit spelling is changed."""
    s = re.sub(r"\bbasis points?\b", "bps", label or "", flags=re.I)
    return re.sub(r"(?<=\d) ?bp\b", "bps", s, flags=re.I)


def series_of(venue: str, event_id: str, rs: list[dict]) -> tuple[str | None, str]:
    """(pmpol series key, reference period) of an event. Kalshi: the whitelist of series tickers; Polymarket: pmpol's
    title grammar (`identify`), which also demands that the rules name the statistical agency."""
    if venue == "kalshi":
        return KALSHI_SERIES.get(rs[0].get("series", "")), period_of(event_id)
    use_pmpol()
    from pmpol.models import Event, Market
    from pmpol.propositions.indicators import identify

    ev = Event(venue, event_id, rs[0].get("event_title", ""),
               markets=[Market(venue, r["market_id"], event_id, r["question"], r["outcome"], r.get("rules", ""),
                               close_time=r["close_time"]) for r in rs])
    got = identify(ev)
    return (got[0].key, got[1]) if got else (None, "")


def contract_span(rec: dict, series_key: str):
    """(lo, hi) in grid steps for one record, via pmpol; None if pmpol does not read the label."""
    use_pmpol()
    from pmpol.models import Market
    from pmpol.propositions.indicators import SERIES, label_span

    m = Market(rec["venue"], rec["market_id"], rec["event_id"], rec["question"], norm_label(rec["outcome"]),
               rec.get("rules", ""),
               strike_type=rec.get("strike_type"), floor_strike=rec.get("floor_strike"),
               cap_strike=rec.get("cap_strike"))
    sp = label_span(m, SERIES[series_key])
    return None if sp is None else (sp.lo, sp.hi)


def elementary_bins(spans: list[tuple[float, float]]) -> list[tuple[float, float]]:
    cuts = sorted({x for s in spans for x in s if math.isfinite(x)})
    edges = [-INF, *cuts, INF]
    return list(zip(edges[:-1], edges[1:]))


def _inside(b, s) -> bool:
    return s[0] <= b[0] and b[1] <= s[1]


def structure(spans) -> str:
    """'rays', 'partition' or '' (not a partition)."""
    if all(math.isinf(lo) != math.isinf(hi) for lo, hi in spans):
        return "rays"
    ss = sorted(spans)
    if ss[0][0] != -INF or ss[-1][1] != INF:
        return ""
    return "partition" if all(a[1] == b[0] for a, b in zip(ss, ss[1:])) else ""


def realised_bin(bins, spans, results) -> int | None:
    fit = [i for i, b in enumerate(bins) if all(_inside(b, s) == bool(r) for s, r in zip(spans, results))]
    return fit[0] if len(fit) == 1 else None


def market_distribution(bins, spans, prices, kind: str) -> list[float] | None:
    """Normalised market probabilities of the elementary bins at one horizon; None if any price is missing."""
    if any(p is None for p in prices):
        return None
    if kind == "partition":
        q = [0.0] * len(bins)
        for s, p in zip(spans, prices):
            for i, b in enumerate(bins):
                if _inside(b, s):
                    q[i] += p
    else:  # rays: P(X >= cut) for each breakpoint, differenced; "below" rays give 1 - price
        ge = {}
        for (lo, hi), p in zip(spans, prices):
            if hi == INF:
                ge[lo] = p
            else:
                ge.setdefault(hi, 1 - p)
        cuts = sorted(ge)
        # clip to a monotone non-increasing sequence of tail probabilities
        tail, run = [], 1.0
        for c in cuts:
            run = min(run, max(0.0, ge[c]))
            tail.append(run)
        q = [1.0 - tail[0]] + [tail[i] - tail[i + 1] for i in range(len(cuts) - 1)] + [tail[-1]]
    z = sum(q)
    return [x / z for x in q] if z > 0 else None


def fmt(x: float, unit: str, step: float) -> str:
    v = x * step
    if unit == "bp":
        return "no change" if v == 0 else f"{v:+.0f} bp"
    return f"{v:.{2 if step < 0.1 else 1}f}%"


def bin_label(b, unit: str, step: float) -> str:
    lo, hi = b
    if lo == -INF:
        return f"below {fmt(hi, unit, step)}" if unit == "pct" else f"{fmt(hi - 1, unit, step)} or lower"
    if hi == INF:
        return f"{fmt(lo, unit, step)} or higher"
    if hi - lo == 1:
        return fmt(lo, unit, step)
    return f"{fmt(lo, unit, step)} to {fmt(hi - 1, unit, step)}"


def build_events(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """(questions, exclusions). Kalshi records only carry whitelisted series (`KALSHI_SERIES`); other records are
    listed as excluded 'series not in scope'."""
    use_pmpol()
    from pmpol.propositions.indicators import SERIES

    groups = defaultdict(list)
    for r in records:
        groups[(r["venue"], r["event_id"])].append(r)
    qs, ex = [], []

    def drop(venue, eid, reason, n=0):
        ex.append({"venue": venue, "event_id": eid, "reason": reason, "markets": n})

    for (venue, eid), rs in sorted(groups.items()):
        key, period = series_of(venue, eid, rs)
        if key is None:
            drop(venue, eid, "series not in scope", len(rs))
            continue
        close = max(r["close_time"] for r in rs)
        if window_of(close) == "pre":
            drop(venue, eid, "closed before 2025-05-01", len(rs))
            continue
        spans = [contract_span(r, key) for r in rs]
        if any(s is None for s in spans):
            drop(venue, eid, "a contract label or strike is not read by pmpol", len(rs))
            continue
        kind = structure(spans)
        if not kind:
            drop(venue, eid, "contracts do not partition the outcome space (or overlap)", len(rs))
            continue
        bins = elementary_bins(spans)
        k = realised_bin(bins, spans, [r["result"] for r in rs])
        if k is None:
            drop(venue, eid, "realised bin not identified from the contract results", len(rs))
            continue
        s = SERIES[key]
        mk = {h: market_distribution(bins, spans, [r["prices"].get(str(h)) for r in rs], kind) for h in HORIZONS}
        qs.append({
            "question_id": f"{venue}:{eid}", "venue": venue, "series": key, "period": period,
            "close_time": close, "window": window_of(close), "unit": s.unit, "step": s.step,
            "bins": [{"label": bin_label(b, s.unit, s.step), "lo": None if b[0] == -INF else b[0],
                      "hi": None if b[1] == INF else b[1]} for b in bins],
            "realised": k, "structure": kind, "n_contracts": len(rs),
            "forecast_date": {str(h): forecast_date(close, h) for h in HORIZONS},
            "market": {str(h): v for h, v in mk.items()},
            # the binary contracts, for Brier/ECE and H4: span in grid steps (None = unbounded), result, prices
            "contracts": [{"id": r["market_id"], "lo": None if sp[0] == -INF else sp[0],
                           "hi": None if sp[1] == INF else sp[1], "result": r["result"],
                           "price": {str(h): r["prices"].get(str(h)) for h in HORIZONS}}
                          for r, sp in zip(rs, spans)],
            "early": any(r.get("early") for r in rs),
            "volume": sum(r.get("volume") or 0 for r in rs),
        })
    return dedupe(qs, ex)


def dedupe(qs: list[dict], ex: list[dict]) -> tuple[list[dict], list[dict]]:
    """The same release listed under an old and a KX ticker: keep the one with most contracts."""
    best = {}
    for q in qs:
        k = (q["series"], q["close_time"][:10])
        rank = lambda x: (x["venue"] == "kalshi", x["n_contracts"])  # noqa: E731  Kalshi first: it is the benchmark
        if k not in best or rank(q) > rank(best[k]):
            if k in best:
                ex.append({"venue": best[k]["venue"], "event_id": best[k]["question_id"].split(":", 1)[1],
                           "reason": "duplicate listing of the same series and release date",
                           "markets": best[k]["n_contracts"]})
            best[k] = q
        else:
            ex.append({"venue": q["venue"], "event_id": q["question_id"].split(":", 1)[1],
                       "reason": "duplicate listing of the same series and release date", "markets": q["n_contracts"]})
    return sorted(best.values(), key=lambda q: (q["close_time"], q["series"])), ex


def counts(qs: list[dict]) -> dict:
    out = defaultdict(lambda: defaultdict(int))
    for q in qs:
        out[q["series"]][q["window"]] += 1
    return {s: dict(w) for s, w in sorted(out.items())}


def card(qs: list[dict], ex: list[dict], n_markets: int, cov: dict | None = None) -> str:
    """Markdown data card: counts only (no forecast and no score of any system)."""
    from collections import Counter

    wins = ("calibration", "test")
    c = counts(qs)
    lines = ["# exp03 data card (generated by `python -m mosaic exp03 card`; counts only, nothing scored)", "",
             f"Source markets fetched: {n_markets}. Questions kept: {len(qs)}. Exclusions: {len(ex)}.",
             "Windows by market close date: calibration 2025-05-01..2025-12-31, test 2026-01-01..end. "
             "Test-window rows exist as data; no forecast or score of any system has been computed on them.", "",
             "## Questions per series and window", "", "| series | calibration | test | mean bins |", "|---|---|---|---|"]
    for s, w in c.items():
        nb = [len(q["bins"]) for q in qs if q["series"] == s]
        lines.append(f"| {s} | {w.get('calibration', 0)} | {w.get('test', 0)} | {sum(nb) / len(nb):.1f} |")
    tot = {w: sum(x.get(w, 0) for x in c.values()) for w in wins}
    lines += [f"| **total** | {tot['calibration']} | {tot['test']} | |", "",
              "## Venue and structure", ""]
    for k, n in sorted(Counter((q["venue"], q["structure"]) for q in qs).items()):
        lines.append(f"- {k[0]} / {k[1]}: {n}")
    nomk = sum(q["market"]["7"] is None for q in qs)
    lines += ["", f"Questions without a market benchmark at 7 days (a price missing): {nomk}; at 1 day: "
                  f"{sum(q['market']['1'] is None for q in qs)}.", "", "## Exclusions by reason", ""]
    for reason, n in Counter(e["reason"] for e in ex).most_common():
        lines.append(f"- {reason}: {n} events")
    lines += ["", "Out-of-scope events are other Kalshi/Polymarket series that matched the title filter or the Polymarket "
                  "economy tag but are not in the draft's series list (including Kalshi's 'Exactly x%' ladders of the "
                  "KXECONSTAT* series, whose contracts leave gaps and tails and so do not partition the outcomes; the "
                  "same releases are covered by the KX* ladders and deduplicated).", ""]
    if cov:
        lines += ["## Context coverage (share of contexts with >= 1 observation; median staleness of the latest one)",
                  "", "| indicator | share | median staleness (days) |", "|---|---|---|"]
        for k, v in cov.items():
            lines.append(f"| {k} | {v['share']:.2f} | {v['median_staleness_days']} |")
    return "\n".join(lines) + "\n"


def write_jsonl(rows, path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
