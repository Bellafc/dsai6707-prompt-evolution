import random

from evo_prompt.config import REF_POINT  # noqa: F401  (import check)
from evo_prompt.genome import SCHOOLS, PromptSet, SchoolGene, b0, concept_pool, decode, sentences
from evo_prompt.operators import apply_edit, crossover, mutate_one, perturb_all, plan_llm_edit, rule_op
from evo_prompt.evaluate import Evaluation
from mosaic.teacher import make_items


def _event():
    return [it.event for it in make_items(2, seed=23) if it.school == "keynesian"][0]


def test_b0_has_three_schools_in_order_and_decodes():
    p = b0()
    assert tuple(g.school for g in p.genes) == SCHOOLS
    msgs = decode(p.gene("keynesian"), _event())
    assert [m["role"] for m in msgs] == ["system", "user"]
    assert "Framework: Keynesian." in msgs[1]["content"]
    assert "[Output]" in msgs[1]["content"]


def test_key_is_stable_and_render_contains_schools():
    p = b0()
    assert p.key() == b0().key()
    assert "## keynesian" in p.render()


def test_sentences_split():
    assert sentences("One. Two! Three?") == ("One.", "Two!", "Three?")


def test_rule_ops_keep_valid_genes():
    rng = random.Random(0)
    pool = concept_pool()
    g = b0().gene("austrian")
    for _ in range(50):
        g = rule_op(rng, g, pool)
        assert len(g.diagnosis) >= 1
        assert len(set(g.concepts)) == len(g.concepts)
        assert all(c in pool for c in g.concepts)


def test_mutate_changes_at_most_one_school():
    rng = random.Random(1)
    base = b0()
    for _ in range(20):
        m = mutate_one(rng, base, concept_pool())
        changed = [a.school for a, b in zip(base.genes, m.genes) if a != b]
        assert len(changed) <= 1


def test_crossover_keeps_school_order_and_mixes_parents():
    rng = random.Random(2)
    a = b0()
    b = perturb_all(random.Random(3), a, concept_pool(), 2, 3)
    c = crossover(rng, a, b)
    assert tuple(g.school for g in c.genes) == SCHOOLS
    for gc, ga, gb in zip(c.genes, a.genes, b.genes):
        assert gc.diagnosis in (ga.diagnosis, gb.diagnosis)


def test_llm_edit_plan_and_apply():
    rng = random.Random(4)
    p = b0()
    ev = Evaluation(school_fid={"keynesian": 0.2, "austrian": 0.5, "monetarist": 0.5},
                    pair_dis={"keynesian|austrian": 0.1, "keynesian|monetarist": 0.4, "austrian|monetarist": 0.4},
                    validity=1.0, words=p.words())
    plan = plan_llm_edit(rng, p, ev)
    assert plan.school in SCHOOLS and plan.field in ("diagnosis", "stance")
    good = "The school reads demand shortfalls as the main risk and favours fiscal support in downturns today."
    new = apply_edit(p, plan, good)
    assert new is not None and new.gene(plan.school).diagnosis != p.gene(plan.school).diagnosis or plan.field == "stance"
    assert apply_edit(p, plan, "too short") is None
    assert apply_edit(p, plan, "word " * 200) is None
