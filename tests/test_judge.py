import csv
import json

import numpy as np
import pytest

import mosaic.run as run
from mosaic.judge import (judge, judge_agree, judge_export, judge_report, latest_judge_dir, parse_judgment, qwk,
                          select_events, spearman)
from mosaic.data import read_jsonl


def test_parse_judgment_strict():
    ok = parse_judgment('x {"fidelity": 4, "purity": 5, "coherence": 3, "plausibility": 2} y')
    assert ok["fidelity"] == 4 and ok["plausibility"] == 2
    assert parse_judgment('{"fidelity": 6, "purity": 5, "coherence": 3, "plausibility": 2}') is None
    assert parse_judgment("no json here") is None
    # skips an earlier unrelated object
    assert parse_judgment('{"a": 1} then {"fidelity": 1, "purity": 1, "coherence": 1, "plausibility": 1}')


def test_select_events_stratified_and_fixed():
    ids = [f"e{i}" for i in range(20)]
    diff = {e: ("hard" if i < 10 else "medium") for i, e in enumerate(ids)}
    a = select_events(ids, diff, 8, seed=1)
    assert a == select_events(ids, diff, 8, seed=1) and len(a) == 8
    assert sum(diff[e] == "hard" for e in a) == 4


def test_agreement_statistics():
    assert qwk([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]) == pytest.approx(1.0)
    assert qwk([1, 1, 5, 5], [5, 5, 1, 1]) < 0
    assert spearman([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.0)
    assert np.isnan(spearman([1, 1, 1], [1, 2, 3]))


def test_judge_pipeline_fake(sandbox):
    run.run("exp01", ["A", "B", "C"], "dev", backend="fake", note="for judge")
    d = judge("exp01", "dev", backend="fake")
    rows = list(read_jsonl(d / "judgments.jsonl"))
    assert {r["arm"] for r in rows} == {"A", "B", "C"} and all(r["parsed"] for r in rows)
    assert all("D" != r["arm"] for r in rows)
    meta = json.loads((d / "meta.json").read_text())
    assert meta["n_items"] == 6 * 3 * 3 and meta["repeats"] == round(54 * 0.10)
    text = judge_report("exp01", "dev", out_dir=sandbox)
    assert "C vs A" in text and "fidelity" in text
    sheet, key = judge_export("exp01", "dev", out_dir=sandbox)
    rows = list(csv.DictReader(open(sheet)))
    assert rows and "arm" not in rows[0] and set(rows[0]) >= {"item", "school", "answer", "fidelity"}
    keyd = json.loads(key.read_text())
    for name, shift in (("r1.csv", 0), ("r2.csv", 0)):
        with open(sandbox / name, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            for r in rows:
                k = keyd[r["item"]]
                w.writerow({**r, **{dim: min(5, k[dim] + shift) for dim in ("fidelity", "purity", "coherence",
                                                                             "plausibility")}})
    res = judge_agree("exp01", [str(sandbox / "r1.csv"), str(sandbox / "r2.csv")], str(key))
    assert res["n_items"] == len(rows) and res["fidelity_qwk_raters"] == pytest.approx(1.0)
    assert latest_judge_dir("exp01", "dev") == d


def test_judge_test_split_needs_human(sandbox):
    from mosaic.cli import main

    with pytest.raises(SystemExit, match="human"):
        main(["judge", "--exp", "exp01", "--split", "test"])
