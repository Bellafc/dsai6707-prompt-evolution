"""Disagreement matrix between L3 frameworks: export, parsing, distances, report (offline)."""

import json

from mosaic import divergence

OUT = """[Think]
Demand falls.
[Output]
Causal chain: shock -> demand -> prices
Scenarios:
S1 (slowdown; growth down, inflation down): 0.6
S2 (rebound; growth up, inflation flat): 0.4
Signals:
equities: SHORT (conviction 2) - S1 hurts earnings
government bonds: LONG (conviction 3) - rates fall in S1
US dollar: NEUTRAL (conviction 1) - no clear path
gold: NEUTRAL (conviction 1) - no clear path
oil: SHORT (conviction 2) - weaker demand in S1
credit: SHORT (conviction 2) - defaults rise in S1
"""


def test_profiles_and_export(tmp_path):
    profs = divergence.profiles()
    assert {"keynesian", "austrian", "monetarist", "new_keynesian", "new_classical", "post_keynesian"} <= set(profs)
    n = divergence.export(tmp_path, n_events=3)
    assert n == 3 * 6 + 3 * 2  # six frameworks, two of them twice
    req = json.loads((tmp_path / "requests.jsonl").read_text().splitlines()[0])
    assert req["custom_id"].startswith("keynesian|0|") and "US/global data known before the event" in \
        req["body"]["messages"][1]["content"]


def test_parse_and_distance():
    p = divergence.parse(OUT)
    assert p["signals"]["government bonds"] == 1 and p["signals"]["equities"] == -1
    assert abs(p["growth"] - (-0.6 + 0.4)) < 1e-9 and abs(p["inflation"] - (-0.6)) < 1e-9
    flipped = divergence.parse(OUT.replace("government bonds: LONG", "government bonds: SHORT"))
    d = divergence.distance({"e1": p}, {"e1": flipped})
    assert d == {"n": 1, "disagreement": round(1 / 6, 3), "signals": round(1 / 6, 3), "opposite": round(1 / 6, 3),
                 "macro": 0.0}
    assert divergence.spearman([1, 2, 3, 4], [10, 20, 30, 40]) == 1.0
    assert divergence.parse("no output") is None


def test_analyze_writes_the_matrix(tmp_path):
    divergence.export(tmp_path, n_events=2)
    lines = []
    for raw in (tmp_path / "requests.jsonl").read_text().splitlines():
        cid = json.loads(raw)["custom_id"]
        text = OUT if not cid.startswith("austrian") else OUT.replace("equities: SHORT", "equities: LONG")
        lines.append({"custom_id": cid, "content": text})
    (tmp_path / "results.jsonl").write_text("".join(json.dumps(x) + "\n" for x in lines))
    s = divergence.analyze(tmp_path)
    assert s["failed"] == 0 and s["noise"]["keynesian"]["signals"] == 0.0
    assert s["pairs"]["keynesian|austrian"]["opposite"] == round(1 / 6, 3)
    assert s["nearest"]["new_keynesian"][1] != "new_keynesian"
    assert "| keynesian |" in (tmp_path / "matrix.md").read_text()
    assert s["pairs_with_positions"] == 15 and s["dispersion"]["events"] == 2
    assert set(s["space"]["coordinates_2d"]) == set(divergence.profiles())
    assert s["space"]["ols_disagreement_on_axes"]["pairs"] == 15


def test_position_test_is_exact_and_one_sided():
    pos = {n: {"state_market": i, "orthodoxy": 0} for i, n in enumerate("abcde")}
    names = list(pos)
    # disagreement equal to the distance on state_market: the true labelling is the best one
    pairs = {f"{a}|{b}": {"disagreement": abs(pos[a]["state_market"] - pos[b]["state_market"])}
             for i, a in enumerate(names) for b in names[i + 1:]}
    t = divergence.position_test(pairs, names, pos)
    assert t["state_market"]["rho"] == 1.0 and t["state_market"]["permutations"] == 120
    assert t["state_market"]["p_one_sided"] == round(2 / 120, 3)  # the identity and its mirror image tie
    assert "orthodoxy" not in t  # a constant axis has no rank correlation


def test_per_asset_counts_different_calls():
    base = {x: 0 for x in divergence.ASSETS}
    runs = {"a": {"e1": {"signals": dict(base)}}, "b": {"e1": {"signals": {**base, "gold": 1}}}}
    out = divergence.per_asset(runs, ["a", "b"])
    assert out["gold"] == 1.0 and out["oil"] == 0.0
