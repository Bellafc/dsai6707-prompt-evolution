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
