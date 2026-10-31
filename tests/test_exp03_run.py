import json
import math

import pytest

from mosaic import exp03_run as r

Q = {"question_id": "kalshi:X", "series": "us_cpi_mom", "period": "2025-08", "window": "calibration",
     "forecast_date": {"7": "2025-09-04", "1": "2025-09-10"},
     "bins": [{"label": "below 0.2%", "lo": None, "hi": 2}, {"label": "0.2%", "lo": 2, "hi": 3},
              {"label": "0.3%", "lo": 3, "hi": 4}, {"label": "0.4% or higher", "lo": 4, "hi": None}],
     "realised": 2,
     "contracts": [{"id": "a", "lo": 2, "hi": None, "result": 1}, {"id": "b", "lo": 3, "hi": None, "result": 1},
                   {"id": "c", "lo": 4, "hi": None, "result": 0}]}


def test_event_text_lists_scenarios_without_prices():
    t = r.event_text(Q)
    assert "S1: below 0.2%" in t and "S4: 0.4% or higher" in t and "2025-09-04" in t
    assert "market" not in t.lower() and "kalshi" not in t.lower() and "0.5" not in t.split("Scenarios")[0]


def test_parse_bins_formats_and_renormalisation():
    ok = "[Think] blah 0.3\n[Output]\nCausal chain: a -> b\nScenario probabilities:\nS1: 0.10\nS2: 0.20\nS3: 0.45\nS4: 0.25\n"
    assert r.parse_bins(ok, Q) == pytest.approx([0.1, 0.2, 0.45, 0.25])
    pct = "[Output]\n- S1 = 10%\n- S2 = 20%\n- **S3**: 50%\n- S4: 20 %\n"
    assert r.parse_bins(pct, Q) == pytest.approx([0.1, 0.2, 0.5, 0.2])
    off = "[Output]\nS1: 0.1\nS2: 0.2\nS3: 0.5\nS4: 0.3\n"  # sums to 1.1: renormalised
    assert sum(r.parse_bins(off, Q)) == pytest.approx(1.0) and r.parse_bins(off, Q)[2] == pytest.approx(0.5 / 1.1)


def test_parse_bins_invalid_cases():
    assert r.parse_bins("[Output]\nS1: 0.5\nS2: 0.5\nS3: 0.5\nS4: 0.5\n", Q) is None  # sum 2.0
    assert r.parse_bins("[Output]\nS1: 0.5\nS2: 0.5\nS3: 0.0\n", Q) is None  # S4 missing
    assert r.parse_bins("no output block", Q) is None
    assert r.parse_bins("[Output]\nS1: 7\nS2: 0.2\nS3: 0.4\nS4: 0.4\n", Q) is None  # 7 is not a probability


def test_forecast_from_samples():
    f, fail = r.forecast_from_samples([[0.2, 0.2, 0.2, 0.4], None, [0.4, 0.2, 0.2, 0.2]], 4)
    assert not fail and f == pytest.approx([0.3, 0.2, 0.2, 0.3])
    assert r.forecast_from_samples([None, None, None], 4) == ([0.25] * 4, True)


def test_rps_and_log_score():
    assert r.rps([0, 0, 1, 0], 2) == 0
    assert r.rps([0.25] * 4, 2) == pytest.approx((0.25 ** 2 + 0.5 ** 2 + 0.25 ** 2) / 3)  # (0.0625+0.25+0.0625)/3
    # one-step miss costs less than a three-step miss (ordered bins)
    assert r.rps([0, 1, 0, 0], 2) < r.rps([1, 0, 0, 0], 2)
    assert r.log_score([0.1, 0.1, 0.0, 0.8], 2) == pytest.approx(-math.log(0.01))  # floor


def test_brier_and_contract_prob():
    p = [0.1, 0.2, 0.45, 0.25]
    assert r.contract_prob(p, Q, Q["contracts"][1]) == pytest.approx(0.7)  # bins 0.3% and >=0.4%
    assert r.brier([0, 0, 1, 0], Q) == 0
    assert r.brier(r.uniform(4), Q) > 0


def test_ece_and_pools():
    assert r.ece([(0.9, 1)] * 9 + [(0.9, 0)]) == pytest.approx(0.0)
    assert r.ece([(1.0, 0)] * 5) == pytest.approx(1.0)
    assert r.pool_equal([[1, 0], [0, 1]]) == [0.5, 0.5]


def test_test_window_refused(tmp_path):
    p = tmp_path / "q.jsonl"
    p.write_text(json.dumps({**Q, "window": "test"}) + "\n")
    with pytest.raises(SystemExit):
        r.load_questions("test", path=p)
    assert r.load_questions("calibration", path=p) == []


def test_pilot_refuses_other_windows_and_caps_limit():
    with pytest.raises(SystemExit):
        r.pilot(["base"], window="test")
