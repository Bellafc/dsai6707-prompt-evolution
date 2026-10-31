import pytest

from mosaic import exp03_gt, exp03_questions as q

pytestmark = pytest.mark.skipif(not exp03_gt.VENDOR_SRC.exists(), reason="run `python -m mosaic vendor` first")


def rec(eid, mid, series="KXCPI", result=0, prices=(0.5, 0.5), close="2025-09-11T12:30:00Z", **kw):
    r = {"venue": "kalshi", "market_id": mid, "event_id": eid, "question": "Q", "outcome": "", "rules": "",
         "close_time": close, "result": result, "prices": {"7": prices[0], "1": prices[1]}, "series": series,
         "volume": 100.0, "early": False, "strike_type": None, "floor_strike": None, "cap_strike": None}
    r.update(kw)
    return r


def cpi_ladder(published=0.3, eid="KXCPI-25AUG", series="KXCPI", close="2025-09-11T12:30:00Z"):
    out = []
    for t, p in ((0.1, 0.9), (0.2, 0.6), (0.3, 0.2), (0.4, 0.05)):  # "above t" contracts
        out.append(rec(eid, f"{eid}-T{t}", series, int(published > t + 1e-9), (p, p), close,
                       strike_type="greater", floor_strike=t))
    return out


def test_ray_ladder_bins_realised_and_market():
    qs, ex = q.build_events(cpi_ladder(0.3))
    assert not ex and len(qs) == 1
    x = qs[0]
    assert [b["label"] for b in x["bins"]] == ["below 0.2%", "0.2%", "0.3%", "0.4%", "0.5% or higher"]
    assert x["bins"][x["realised"]]["label"] == "0.3%" and x["structure"] == "rays"
    m = x["market"]["7"]
    assert abs(sum(m) - 1) < 1e-9 and m[0] == pytest.approx(0.1) and m[1] == pytest.approx(0.3)
    assert x["window"] == "calibration" and x["forecast_date"]["7"] == "2025-09-04" and x["period"] == "2025-08"


def test_published_below_all_thresholds():
    qs, _ = q.build_events(cpi_ladder(0.0))
    assert qs[0]["bins"][qs[0]["realised"]]["label"] == "below 0.2%"


def test_inconsistent_results_excluded():
    rs = cpi_ladder(0.3)
    rs[0]["result"] = 0  # "above 0.1" no, but "above 0.2" yes: impossible
    qs, ex = q.build_events(rs)
    assert not qs and "not identified" in ex[0]["reason"]


def test_fed_labels_partition():
    labs = [("Cut >25bps", 0), ("Cut 25bps", 1), ("Fed maintains rate", 0), ("Hike 25bps", 0), ("Hike >25bps", 0)]
    rs = [rec("KXFEDDECISION-25SEP", f"m{i}", "KXFEDDECISION", r, (0.1 * (i + 1), 0.2), "2025-09-17T18:00:00Z",
              outcome=o) for i, (o, r) in enumerate(labs)]
    qs, ex = q.build_events(rs)
    assert not ex, ex
    x = qs[0]
    assert x["structure"] == "partition" and len(x["bins"]) == 5
    assert x["bins"][x["realised"]]["label"] == "-25 bp"
    assert x["market"]["1"] == pytest.approx([0.2, 0.2, 0.2, 0.2, 0.2])


def test_missing_label_and_gap_and_scope_exclusions():
    gap = [rec("KXFEDDECISION-25SEP", "a", "KXFEDDECISION", 1, outcome="Cut 25bps"),
           rec("KXFEDDECISION-25SEP", "b", "KXFEDDECISION", 0, outcome="Hike 25bps")]
    unread = [rec("KXFEDDECISION-25OCT", "c", "KXFEDDECISION", 1, outcome="Something else")]
    other = [rec("KXCFNAI-25OCT", "d", "KXCFNAI", 1)]
    pre = cpi_ladder(0.3, "KXCPI-25MAR", close="2025-04-10T12:30:00Z")
    qs, ex = q.build_events(gap + unread + other + pre)
    reasons = {e["event_id"]: e["reason"] for e in ex}
    assert not qs
    assert "partition" in reasons["KXFEDDECISION-25SEP"] and "not read" in reasons["KXFEDDECISION-25OCT"]
    assert reasons["KXCFNAI-25OCT"] == "series not in scope" and "before" in reasons["KXCPI-25MAR"]


def test_duplicate_listing_and_windows():
    old = cpi_ladder(0.3, "CPI-25AUG", "CPI")[:3]
    new = cpi_ladder(0.3, "KXCPI-25AUG")
    test = cpi_ladder(0.2, "KXCPI-26JAN", close="2026-02-11T13:30:00Z")
    qs, ex = q.build_events(old + new + test)
    assert [x["window"] for x in qs] == ["calibration", "test"]
    assert qs[0]["question_id"] == "kalshi:KXCPI-25AUG" and any("duplicate" in e["reason"] for e in ex)
    assert q.counts(qs) == {"us_cpi_mom": {"calibration": 1, "test": 1}}


def test_missing_price_gives_no_market_distribution():
    rs = cpi_ladder(0.3)
    rs[1]["prices"]["7"] = None
    qs, _ = q.build_events(rs)
    assert qs[0]["market"]["7"] is None and qs[0]["market"]["1"] is not None
