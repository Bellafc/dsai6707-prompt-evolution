"""exp03 ground truth: settled Kalshi Economics/Financials markets and Polymarket economy markets (Task 2, step 1).

Extends the team's pmpol fetchers (vendor/pmpol-academic, `pmpol.ground_truth.kalshi` / `.polymarket`; see its
EXPORT_NOTES.md) from politics to macro series. pmpol's rules are kept: its User-Agent, no retry on HTTP 429 (the
error is raised and the run stops), raw data only under data/ (never committed; Kalshi forbids redistribution).

  python -m mosaic exp03 fetch --venue kalshi|polymarket [--since 2025-05-01]

Parsers are pure functions with offline fixtures (tests/test_exp03_gt.py). Nothing here scores a forecast.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from mosaic.config import ROOT

VENDOR_SRC = ROOT / "vendor" / "pmpol-academic" / "src"
RAW = ROOT / "data" / "exp03" / "raw"
SINCE = "2025-05-01"  # first resolution date in scope (exp03 draft)
KALSHI_CATEGORIES = ("Economics", "Financials")
MIN_VOLUME = 100  # contracts / USDC; below this a market has no usable price (pmpol uses 1000 for calibration)

# Series in scope (draft "Question universe"): matched on the Kalshi series title or the Polymarket event title.
IN_SCOPE = re.compile(
    r"\bcpi\b|inflation|unemployment|jobless|\bfed\b|fomc|federal funds|interest rate|rate decision|"
    r"\bgdp\b|european central bank|\becb\b|bank of (england|japan|canada|mexico)|swiss national bank|"
    r"reserve bank of australia|central bank of brazil|\bpayroll|nonfarm", re.I)


def use_pmpol() -> None:
    """Make `import pmpol` work from the extracted archive (run `python -m mosaic vendor` first)."""
    if not VENDOR_SRC.exists():
        raise SystemExit("run `python -m mosaic vendor` first (extracts the pmpol archive to vendor/)")
    if str(VENDOR_SRC) not in sys.path:
        sys.path.insert(0, str(VENDOR_SRC))


PAUSE = 0.6  # seconds between Kalshi requests (pmpol's default 0.06 hit HTTP 429 on the first run, 2026-10-31)

# Titles that match IN_SCOPE but are not the draft's series: other countries' GDP / unemployment / CPI (the draft
# keeps foreign central-bank decisions only), sub-indices of CPI, counts and maxima over a year.
OUT_OF_SCOPE = re.compile(
    r"\b(france|germany|china|japan|brazil|uk|u\.k\.|canada|india|italy|spain|mexico|korea|australia|euro ?zone|eu)\b"
    r".*\b(gdp|unemployment|cpi|inflation)\b|cpi on |number of fed|highest rate|inflation surge|"
    r"\bfood\b|\bgasoline\b|\bshelter\b|\bused car|\brent\b", re.I)


def in_scope(title: str) -> bool:
    return bool(IN_SCOPE.search(title or ""))


def out_of_scope(series: dict) -> bool:
    """Not one of the draft's series: an explicit whitelist (below) after the title filter."""
    return series.get("ticker") not in KALSHI_SERIES


# Kalshi series ticker -> pmpol indicator series (`pmpol.propositions.indicators.SERIES`). Both the old tickers and
# their KX-prefixed successors are listed, so a market counts once whichever name it was listed under.
# Chosen from the 2026-10-31 listing of Economics/Financials series (titles in data/exp03/raw/kalshi_series.json);
# the title-to-measure mapping is checked against each market's rules in exp03_questions.
KALSHI_SERIES = {
    "KXCPI": "us_cpi_mom", "CPI": "us_cpi_mom", "KXECONSTATCPI": "us_cpi_mom",
    "KXCPICORE": "us_core_cpi_mom", "CPICORE": "us_core_cpi_mom", "KXECONSTATCPICORE": "us_core_cpi_mom",
    "KXCPIYOY": "us_cpi_yoy", "CPIYOY": "us_cpi_yoy", "KXECONSTATCPIYOY": "us_cpi_yoy",
    "KXCPICOREYOY": "us_core_cpi_yoy", "CPICOREYOY": "us_core_cpi_yoy", "KXECONSTATCORECPIYOY": "us_core_cpi_yoy",
    "KXU3": "us_unemployment", "U3": "us_unemployment", "KXECONSTATU3": "us_unemployment",
    "KXGDP": "us_real_gdp_qoq_saar", "GDP": "us_real_gdp_qoq_saar",
    "KXFEDDECISION": "fed_change", "FEDDECISION": "fed_change",
    "KXCBDECISIONEU": "ecb_change", "KXCBDECISIONENGLAND": "boe_change", "KXCBDECISIONJAPAN": "boj_change",
    "KXCBDECISIONMEXICO": "banxico_change", "KXCBDECISIONCANADA": "boc_change", "KXCBDSWISS": "snb_change",
    "KXCBDECISIONAUSTRALIA": "rba_change",
}


def kalshi_record(m: dict, series: dict, candles: list[dict]) -> dict | None:
    """One settled Kalshi market -> a flat record: pmpol's `Resolved` plus the strike, rules and series fields the
    scenario-set builder needs. None when the market has no yes/no result or no close time."""
    use_pmpol()
    from pmpol.ground_truth.kalshi import to_resolved

    r = to_resolved(m, series, candles)
    if r is None:
        return None
    rules = "\n".join(x for x in (m.get("rules_primary"), m.get("rules_secondary")) if x)
    return {**r.to_dict(), "series": series.get("ticker", ""), "series_title": series.get("title", ""),
            "strike_type": m.get("strike_type"), "floor_strike": _f(m.get("floor_strike")),
            "cap_strike": _f(m.get("cap_strike")), "rules": rules,
            "open_time": m.get("open_time"), "expiration_value": m.get("expiration_value")}


def _f(x):
    try:
        return None if x in (None, "") else float(x)
    except (TypeError, ValueError):
        return None


def polymarket_record(m: dict, prices: dict) -> dict | None:
    use_pmpol()
    from pmpol.ground_truth.polymarket import to_resolved

    r = to_resolved(m, prices)
    if r is None:
        return None
    ev = (m.get("events") or [{}])[0]
    return {**r.to_dict(), "event_title": ev.get("title", ""), "rules": m.get("description") or "",
            "series": "", "series_title": "", "strike_type": None, "floor_strike": None, "cap_strike": None}


def since_ts(since: str) -> str:
    return since + "T00:00:00Z"


def fetch_kalshi(since: str = SINCE, out: Path | None = None, log=sys.stderr, max_scan: int = 3000) -> int:
    """Settled markets closing on/after `since` in every in-scope Economics/Financials series, with the daily
    candles before close. Resumable: tickers already in the output file are skipped."""
    use_pmpol()
    from pmpol.ground_truth.kalshi import KalshiHistory

    out = out or RAW / "kalshi_econ.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {json.loads(x)["market_id"] for x in out.read_text().splitlines() if x.strip()} if out.exists() else set()
    k = KalshiHistory(pause=PAUSE)
    series = [s for s in k.series(KALSHI_CATEGORIES) if in_scope(s.get("title", "")) and not out_of_scope(s)]
    (RAW / "kalshi_series.json").write_text(json.dumps(series, indent=1), encoding="utf-8")
    print(f"kalshi: {len(series)} in-scope series", file=log, flush=True)
    total = 0
    with open(out, "a", encoding="utf-8") as fh:
        for s in series:
            n = scanned = 0
            for m, hist in k.settled_markets(s["ticker"]):
                scanned += 1
                if scanned > max_scan:
                    break
                if (m.get("close_time") or "") < since_ts(since):
                    if not hist:
                        continue  # /markets returns the most recent first: older ones may still follow in /historical
                    break  # historical pages are also newest first
                vol = float(m.get("volume_fp") or m.get("volume") or 0)
                if m["ticker"] in done or vol < MIN_VOLUME or (m.get("result") or "") not in ("yes", "no"):
                    continue
                rec = kalshi_record(m, s, k.candles(s["ticker"], m, hist))
                if rec:
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    fh.flush()
                    n += 1
            total += n
            print(f"kalshi {s['ticker']} ({s.get('title', '')[:50]}): +{n}", file=log, flush=True)
    return total


def polymarket_economy_tag(client) -> int:
    """Gamma tag id of 'economy' (looked up by slug, not hard-coded)."""
    d = client._get(client._gamma, "/tags/slug/economy", {})
    if not d or "id" not in d:
        raise SystemExit("Polymarket: tag 'economy' not found")
    return int(d["id"])


def fetch_polymarket(since: str = SINCE, out: Path | None = None, log=sys.stderr, limit: int = 20000) -> int:
    use_pmpol()
    from pmpol.ground_truth.polymarket import PolymarketHistory, horizon_prices, resolution

    out = out or RAW / "polymarket_econ.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {json.loads(x)["market_id"] for x in out.read_text().splitlines() if x.strip()} if out.exists() else set()
    pm = PolymarketHistory()
    tag = polymarket_economy_tag(pm)
    total = 0
    with open(out, "a", encoding="utf-8") as fh:
        for m in pm.closed_markets(tag_id=tag, limit=limit):
            ev = (m.get("events") or [{}])[0]
            if (m.get("closedTime") or "") < since or resolution(m) is None:
                continue
            if not in_scope(ev.get("title", "") + " " + (m.get("question") or "")):
                continue
            if (m.get("slug") or str(m.get("id"))) in done or (m.get("volumeNum") or 0) < MIN_VOLUME:
                continue
            rec = polymarket_record(m, horizon_prices(pm, m))
            if rec:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fh.flush()
                total += 1
    print(f"polymarket: +{total}", file=log, flush=True)
    return total
