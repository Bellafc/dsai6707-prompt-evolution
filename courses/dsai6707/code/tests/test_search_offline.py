import random

from evo_prompt.algorithms import Search
from evo_prompt.backend import Ledger, OfflineBackend
from evo_prompt.evaluate import Evaluator
from evo_prompt.genome import b0
from evo_prompt.moo import dominates
from evo_prompt.runner import events, sampling
from mosaic.backends import Cache


def _setup(tmp_path, seed=1):
    ledger = Ledger(budget_usd=1e9, price_in=0, price_out=0)
    backend = OfflineBackend(sampling(seed), Cache(tmp_path / "c.jsonl"), ledger)
    ev = Evaluator(backend, events(3, 23))
    return backend, ev, ledger


def test_evaluation_is_feasible_and_in_range(tmp_path):
    backend, ev, _ = _setup(tmp_path)
    e = ev.evaluate([b0()])[0]
    assert e.validity == 1.0 and e.feasible
    assert 0.0 <= e.fidelity <= 1.0 and 0.0 <= e.disagreement <= 1.0
    assert set(e.pair_dis) == {"keynesian|austrian", "keynesian|monetarist", "austrian|monetarist"}


def test_second_evaluation_uses_cache_and_memo(tmp_path):
    backend, ev, ledger = _setup(tmp_path)
    ev.evaluate([b0()])
    calls = ledger.calls
    ev.evaluate([b0()])
    assert ledger.calls == calls  # no new model calls


def test_resume_from_disk_cache_gives_same_result(tmp_path):
    backend, ev, _ = _setup(tmp_path)
    e1 = ev.evaluate([b0()])[0]
    backend2, ev2, ledger2 = _setup(tmp_path)  # fresh process: only the disk cache is shared
    e2 = ev2.evaluate([b0()])[0]
    assert ledger2.calls == 0
    assert e1.as_dict() == e2.as_dict()


def _run(method, tmp_path, seed=1):
    backend, ev, _ = _setup(tmp_path, seed)
    s = Search(ev, random.Random(seed), method=method, pop_size=4, backend=backend).run(2)
    return s


def test_all_methods_run_and_spend_budget_equally(tmp_path):
    for m in ("nsga2", "nsga2_rule", "ga", "random"):
        s = _run(m, tmp_path / m)
        assert len(s.history) == 3
        assert s.evals_done == 4 * 3
        assert s.history[-1]["front"] >= 1
        assert s.history[-1]["hv"] >= 0.0


def test_search_is_deterministic_given_seed(tmp_path):
    h1 = [r["hv"] for r in _run("nsga2", tmp_path / "a", seed=5).history]
    h2 = [r["hv"] for r in _run("nsga2", tmp_path / "b", seed=5).history]
    assert h1 == h2


def test_archive_members_are_feasible_and_front_nondominated(tmp_path):
    s = _run("nsga2", tmp_path, seed=2)
    assert all(i.ev.feasible for i in s.archive.values())
    front = [(f.ev.objectives, 0.0) for f in s.front()]
    for i, a in enumerate(front):
        for j, b in enumerate(front):
            if i != j:
                assert not dominates(b, a), "a front member dominates another"
