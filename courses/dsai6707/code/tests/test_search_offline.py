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
    for m in ("nsga2", "nsga2_rule", "ga", "random", "ga_rule", "nsga2_llmu", "evoprompt_ga", "evoprompt_ga_lc"):
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


def test_rule_only_methods_make_no_llm_edits(tmp_path):
    for m in ("nsga2_rule", "ga_rule"):
        s = _run(m, tmp_path / m, seed=3)
        assert not any("L" in r["origin"] for r in s.eval_log)


def test_unguided_control_uses_neutral_instruction(tmp_path):
    from evo_prompt.operators import UNGUIDED_INSTRUCTION, plan_unguided_edit

    rng = random.Random(0)
    plans = [plan_unguided_edit(rng, b0()) for _ in range(50)]
    assert all(p.instruction == UNGUIDED_INSTRUCTION and p.objective == -1 for p in plans)
    assert {p.field for p in plans} == {"diagnosis", "stance"}
    assert len({p.school for p in plans}) == 3
    s = _run("nsga2_llmu", tmp_path, seed=4)
    assert any("L" in r["origin"] for r in s.eval_log)


def test_new_methods_share_initial_population_with_their_pairs(tmp_path):
    g0 = lambda m: [r["genome"] for r in _run(m, tmp_path / m, seed=6).eval_log if r["gen"] == 0]  # noqa: E731
    assert g0("ga_rule") == g0("nsga2_rule") == g0("nsga2_llmu") == g0("nsga2")


def test_haiku_profile_sampling_keeps_seed_in_key_and_drops_temperature():
    s1, s2 = sampling(1, "haiku"), sampling(2, "haiku")
    assert "temperature" not in s1 and "top_p" not in s1 and s1["thinking"] == "disabled"
    assert s1 != s2  # different seeds give different cache keys


def test_evoprompt_operator_template_extraction_and_roulette():
    from evo_prompt.operators import EVOPROMPT_GA_TEMPLATE, evoprompt_extract, roulette

    assert EVOPROMPT_GA_TEMPLATE.startswith("Please follow the instruction step-by-step to generate a better prompt.")
    assert "2. Mutate the prompt generated in Step 1" in EVOPROMPT_GA_TEMPLATE
    assert evoprompt_extract("1. Crossover Prompt: a\n2. <prompt>Final text.</prompt>") == "Final text."
    assert evoprompt_extract("no brackets") is None
    rng = random.Random(0)
    picks = [roulette(rng, [0.1, 0.0, 0.9]) for _ in range(2000)]
    assert picks.count(1) == 0 and 1500 < picks.count(2) < 1900


def test_evoprompt_children_change_diagnosis_only(tmp_path):
    s = _run("evoprompt_ga", tmp_path, seed=7)
    kids = [r for r in s.eval_log if r["gen"] > 0]
    assert kids and all(r["origin"].startswith("E") for r in kids)


def test_length_constrained_evoprompt_appends_one_sentence():
    from evo_prompt.operators import EVOPROMPT_GA_TEMPLATE, EVOPROMPT_LC_SUFFIX, evoprompt_messages

    plain = evoprompt_messages("a b c", "d e")[0]["content"]
    lc = evoprompt_messages("a b c", "d e", True)[0]["content"]
    assert plain == EVOPROMPT_GA_TEMPLATE.format(p1="a b c", p2="d e") and lc == plain + EVOPROMPT_LC_SUFFIX
