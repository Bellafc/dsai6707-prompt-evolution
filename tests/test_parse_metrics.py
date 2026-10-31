import numpy as np
import pytest

from mosaic.metrics import Lexicon, brier, consistency, diversity, ece, hits, jaccard_distance
from mosaic.parse import parse
from mosaic.stats import holm, paired

TRAJ = """[Think] The cut lowers rates.
[ToolCall: query_episode_db]
[Observe] 2019 mid-cycle cut
[Think] Transmission: rates -> credit -> demand
[Output]
Causal chain: cut -> lower funding costs -> investment
Scenario probabilities:
- Soft landing: 55%
- Recession: 0.25
- Reacceleration: 20%
Signals:
- SPX: LONG (conviction 0.6)
- UST 10Y - short
- Gold = neutral
"""


def test_parse_all_seven_elements():
    p = parse(TRAJ)
    assert all(p.tags.values())
    assert p.causal_chain and p.has_scenarios and p.has_signals
    assert p.completeness() == 1.0
    assert [round(v, 2) for _, v in p.scenarios] == [0.55, 0.25, 0.20]
    assert abs(p.scenario_sum - 1.0) < 1e-9
    assert p.signals == {"SPX": "long", "UST10Y": "short", "GOLD": "neutral"}


def test_parse_missing_output_block():
    p = parse("[Think] just prose, no structured block. SPX: LONG")
    assert not p.tags["Output"] and p.signals == {} and p.completeness() == pytest.approx(1 / 7)


def test_keyword_matching_symbols_and_boundaries():
    assert hits("Using MV=PQ and IS-LM here", ("MV=PQ", "IS-LM")) == 2
    assert hits("multipliers everywhere", ("multiplier",)) == 0  # whole words only
    assert hits("Aggregate\n demand fell", ("aggregate demand",)) == 1
    assert hits("M2 grew; M2 again", ("M2",), mode="occurrences") == 2


def test_consistency_formula_eq_4_1():
    lex = Lexicon(must=("a1", "a2", "a3", "a4", "a5", "a6"), strong=("s1", "s2", "s3", "s4", "s5", "s6"),
                  anti=("x1", "x2"))
    # 3/6 must, 6 strong (capped at 5), 1 anti: 0.5*0.5 + 0.5*1 - 0.15 = 0.60
    r = consistency("a1 a2 a3 s1 s2 s3 s4 s5 s6 x1", lex)
    assert r["consistency"] == pytest.approx(0.60)
    assert consistency("x1 x2", lex)["consistency"] == 0.0  # floored at zero


def test_jaccard_and_diversity():
    a, b = {("SPX", "long"), ("GOLD", "long")}, {("SPX", "short"), ("GOLD", "long")}
    assert jaccard_distance(a, b) == pytest.approx(1 - 1 / 3)
    assert jaccard_distance(set(), set()) is None
    assert diversity([a, a, b]) == pytest.approx((0 + 2 / 3 + 2 / 3) / 3)


def test_forecast_scores():
    assert brier(np.array([1.0, 0.0]), np.array([1, 0])) == 0.0
    assert ece(np.array([0.9] * 10), np.array([1] * 9 + [0])) == pytest.approx(0.0)


def test_paired_and_holm():
    a = np.zeros(40)
    b = np.r_[np.full(30, 0.2), np.full(10, -0.1)]
    r = paired(a, b, seed=1)
    assert r["diff"] == pytest.approx(0.125) and r["ci_lo"] > 0 and r["p"] < 0.01 and r["win_rate"] == 0.75
    assert holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
