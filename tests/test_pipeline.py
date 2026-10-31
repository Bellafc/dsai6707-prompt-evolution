import csv
import json

import pytest

import mosaic.locks as locks
import mosaic.run as run
from mosaic.data import Event, Trajectory
from mosaic.prompts import pick_exemplars
from mosaic.report import report


def test_dev_run_all_arms_fake_backend(sandbox):
    out = run.run("exp01", ["A", "B", "C", "D"], "dev", backend="fake", note="pytest")
    assert [s["arm"] for s in out] == ["A", "B", "C", "D"]
    rows = list(csv.DictReader(open(run.RESULTS), delimiter="\t"))
    assert len(rows) == 4 and all(r["status"] == "dev" for r in rows)
    # the fake adapter output has no cross-school leak, so C is purer than A
    a, c = out[0], out[2]
    assert c["contamination_mean"] < a["contamination_mean"]
    assert c["output_rate"] == 1.0
    gens = [json.loads(line) for line in open(run.RUNS_DIR / out[1]["run_id"] / "generations.jsonl")]
    assert len(gens[0]["messages"]) == 1 + 2 * 3 + 1  # system + 3 exemplar pairs + user
    text = report("exp01", "dev", out_dir=sandbox)
    assert "C vs B" in text and "EXPLORATORY" in text


def test_cache_makes_rerun_free(sandbox):
    run.run("exp01", ["A"], "dev", backend="fake")
    again = run.run("exp01", ["A"], "dev", backend="fake")
    assert again[0]["cached_fraction"] == 1.0


def test_test_split_guards(sandbox, monkeypatch, tmp_path):
    with pytest.raises(SystemExit, match="only run with --final"):
        run.run("exp01", ["A"], "test", backend="fake")
    with pytest.raises(SystemExit, match="frozen config"):
        run.run("exp01", ["A"], "test", backend="fake", final=True)
    with pytest.raises(SystemExit, match="only for the test split"):
        run.run("exp01", ["A"], "dev", final=True)
    monkeypatch.setattr(locks, "ROOT", tmp_path)  # no lock file there
    with pytest.raises(SystemExit, match="no lock"):
        run.run("exp01", ["A"], "test", final=True)


def test_exemplars_never_share_template_and_are_reproducible():
    pool = [Trajectory("austrian", f"p{i}", f"r{i}", f"T{i % 3}") for i in range(12)]
    ev = Event(id="e1", text="x", template_id="T1")
    ex = pick_exemplars(pool, ev, 3, "random", seed=7)
    assert len(ex) == 3 and all(t.template_id != "T1" for t in ex)
    assert ex == pick_exemplars(pool, ev, 3, "random", seed=7)


def test_set_dotted():
    cfg = {"arms": {"B": {"k": 3}}}
    run.set_dotted(cfg, "arms.B.k=5")
    run.set_dotted(cfg, "arms.B.strategy=category")
    assert cfg["arms"]["B"] == {"k": 5, "strategy": "category"}


def test_vendor_extract_safe(tmp_path):
    import io
    import tarfile

    from mosaic.vendor import extract

    good = tmp_path / "good.tar.gz"
    with tarfile.open(good, "w:gz") as tf:
        data = b"print('hi')\n"
        info = tarfile.TarInfo("pkg/a.py")
        info.size = len(data)
        tf.addfile(info, io.BytesIO(data))
    extract(good, tmp_path / "out")
    assert (tmp_path / "out/pkg/a.py").read_text() == "print('hi')\n"
    bad = tmp_path / "bad.tar.gz"
    with tarfile.open(bad, "w:gz") as tf:
        info = tarfile.TarInfo("../evil.py")
        info.size = 0
        tf.addfile(info, io.BytesIO(b""))
    with pytest.raises(SystemExit, match="unsafe"):
        extract(bad, tmp_path / "out2")
