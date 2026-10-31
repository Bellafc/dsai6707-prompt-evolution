"""Offline tests for the exp03 ground-truth parsers (fixtures are hand-written, not Kalshi data)."""

import pytest

from mosaic import exp03_gt

pytestmark = pytest.mark.skipif(not exp03_gt.VENDOR_SRC.exists(), reason="run `python -m mosaic vendor` first")

DAY = 86400
CLOSE = "2025-09-11T12:30:00Z"
CLOSE_TS = 1757593800


def _candles():
    return [{"end_period_ts": CLOSE_TS - 7 * DAY, "yes_bid": {"close_dollars": "0.40"},
             "yes_ask": {"close_dollars": "0.44"}, "price": {"close_dollars": "0.41"}},
            {"end_period_ts": CLOSE_TS - 1 * DAY, "yes_bid": {"close_dollars": "0.10"},
             "yes_ask": {"close_dollars": "0.90"}, "price": {"close_dollars": "0.55"}}]


def _market(**kw):
    m = {"ticker": "KXCPI-25AUG-T0.3", "event_ticker": "KXCPI-25AUG", "title": "CPI in Aug 2025?",
         "yes_sub_title": "Above 0.3%", "close_time": CLOSE, "expected_expiration_time": CLOSE,
         "result": "yes", "volume_fp": "5000", "strike_type": "greater", "floor_strike": 0.3,
         "rules_primary": "BLS first release", "rules_secondary": "x"}
    m.update(kw)
    return m


def test_kalshi_record_prices_and_strikes():
    rec = exp03_gt.kalshi_record(_market(), {"ticker": "KXCPI", "title": "CPI", "category": "Economics"}, _candles())
    assert rec["result"] == 1 and rec["strike_type"] == "greater" and rec["floor_strike"] == 0.3
    assert rec["series"] == "KXCPI" and "BLS first release" in rec["rules"]
    assert rec["prices"]["7"] == 0.42 and rec["price_kind"]["7"] == "mid"  # tight book: midpoint
    assert rec["prices"]["1"] == 0.55 and rec["price_kind"]["1"] == "last"  # spread 0.8: last trade
    assert rec["prices"]["30"] is None  # no candle that old


def test_kalshi_record_rejects_unresolved():
    assert exp03_gt.kalshi_record(_market(result=""), {"ticker": "S"}, _candles()) is None


def test_polymarket_record():
    m = {"slug": "fed-decision-in-sep", "id": 1, "outcomes": '["Yes","No"]', "outcomePrices": '["1","0"]',
         "umaResolutionStatus": "resolved", "closedTime": "2025-09-17 18:00:00+00", "endDate": "2025-09-17T00:00:00Z",
         "question": "Fed decision in September?", "groupItemTitle": "25 bps decrease", "volumeNum": 9000,
         "events": [{"slug": "fed-sep", "title": "Fed decision in September?"}], "description": "rules"}
    rec = exp03_gt.polymarket_record(m, {"1": 0.9, "7": 0.8, "30": None})
    assert rec["result"] == 1 and rec["outcome"] == "25 bps decrease" and rec["prices"]["7"] == 0.8
    assert exp03_gt.polymarket_record({**m, "outcomePrices": '["0.5","0.5"]'}, {}) is None


def test_scope_filter():
    assert exp03_gt.in_scope("CPI core month-over-month") and exp03_gt.in_scope("Fed decision in March")
    assert exp03_gt.in_scope("Unemployment rate") and exp03_gt.in_scope("US GDP growth")
    assert not exp03_gt.in_scope("Highest temperature in NYC") and not exp03_gt.in_scope("S&P 500 close")
