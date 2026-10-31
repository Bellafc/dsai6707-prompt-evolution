import json

import pytest

from mosaic import SCHOOLS


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """Tiny dev/test events + trajectories in tmp; run outputs redirected away from the repo."""
    ev = tmp_path / "data/events"
    ev.mkdir(parents=True)
    cats = ["monetary policy", "inflation data", "geopolitical shock"]
    for split, n in (("dev", 6), ("test", 4)):
        with open(ev / f"{split}.jsonl", "w") as f:
            for i in range(n):
                f.write(json.dumps({"id": f"{split}-{i}", "text": f"{split} event {i}: the Fed surprises markets",
                                    "difficulty": ["medium", "hard"][i % 2], "category": cats[i % 3],
                                    "template_id": f"T{i}", "macro_context": {"CPI": 3.1, "FEDFUNDS": 4.5}}) + "\n")
    tr = tmp_path / "data/trajectories"
    tr.mkdir(parents=True)
    for s in SCHOOLS:
        with open(tr / f"{s}.jsonl", "w") as f:
            for i in range(8):
                f.write(json.dumps({"template_id": f"T{i % 4}", "messages": [
                    {"role": "system", "content": s}, {"role": "user", "content": f"{cats[i % 3]} example {i}"},
                    {"role": "assistant", "content": f"[Think] {s} reasoning {i}\n[Output]\n- SPX: LONG"}]}) + "\n")
    import mosaic.run as run

    p = {"events_dir": ev, "trajectories_dir": tr, "adapters_dir": tmp_path / "adapters"}
    monkeypatch.setattr(run, "paths", lambda: p)
    monkeypatch.setattr(run, "RESULTS", tmp_path / "results.tsv")
    monkeypatch.setattr(run, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(run, "CACHE_PATH", tmp_path / "cache.jsonl")
    return tmp_path
