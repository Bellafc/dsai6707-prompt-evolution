"""Variation operators: rule-based mutation, structural crossover, and LLM-guided mutation (AI -> EC).

Rule-based operators never call the model. LLM-guided mutation asks the model to rewrite one text field of one school,
and the request states the objective that the parent is weakest on (fidelity, distinctness from another school, or
length). Its output is accepted only if it has 5 to 120 words; otherwise the caller falls back to a rule operator.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from mosaic.divergence import profiles
from mosaic.metrics import lexicons

from .genome import SCHOOLS, PromptSet, SchoolGene, sentences


def _apply(op: str, rng, g: SchoolGene, pool: tuple[str, ...]) -> SchoolGene | None:
    if op == "drop_diag" and len(g.diagnosis) > 2:
        i = rng.randrange(len(g.diagnosis))
        return replace(g, diagnosis=g.diagnosis[:i] + g.diagnosis[i + 1:])
    if op == "swap_diag" and len(g.diagnosis) > 1:
        d = list(g.diagnosis)
        i, j = rng.sample(range(len(d)), 2)
        d[i], d[j] = d[j], d[i]
        return replace(g, diagnosis=tuple(d))
    if op == "drop_concept" and len(g.concepts) > 3:
        i = rng.randrange(len(g.concepts))
        return replace(g, concepts=g.concepts[:i] + g.concepts[i + 1:])
    if op == "add_concept":
        cands = [c for c in pool if c not in g.concepts]
        if cands:
            c = rng.choice(cands)
            pos = rng.randrange(len(g.concepts) + 1)
            return replace(g, concepts=g.concepts[:pos] + (c,) + g.concepts[pos:])
    if op == "swap_concept" and len(g.concepts) > 1:
        c = list(g.concepts)
        i, j = rng.sample(range(len(c)), 2)
        c[i], c[j] = c[j], c[i]
        return replace(g, concepts=tuple(c))
    return None


OPS = ("drop_diag", "swap_diag", "drop_concept", "add_concept", "swap_concept")


def rule_op(rng, g: SchoolGene, pool: tuple[str, ...]) -> SchoolGene:
    ops = list(OPS)
    rng.shuffle(ops)
    for op in ops:
        new = _apply(op, rng, g, pool)
        if new is not None and new != g:
            return new
    return g


def mutate_one(rng, p: PromptSet, pool: tuple[str, ...]) -> PromptSet:
    """Rule mutation of one randomly chosen school (1 or 2 operators). Touches one school, so the other two
    school prompts (and their cached model outputs) are unchanged."""
    g = p.gene(rng.choice(SCHOOLS))
    for _ in range(rng.randint(1, 2)):
        g = rule_op(rng, g, pool)
    return p.replace_gene(g)


def perturb_all(rng, p: PromptSet, pool: tuple[str, ...], lo: int, hi: int) -> PromptSet:
    """Rule perturbation of every school, lo..hi operators each (used for the initial population and for B1)."""
    genes = []
    for g in p.genes:
        for _ in range(rng.randint(lo, hi)):
            g = rule_op(rng, g, pool)
        genes.append(g)
    return PromptSet(tuple(genes))


def crossover(rng, a: PromptSet, b: PromptSet) -> PromptSet:
    """Structural crossover: either swap whole school blocks, or mix field by field inside each school."""
    if rng.random() < 0.5:
        return PromptSet(tuple(rng.choice((ga, gb)) for ga, gb in zip(a.genes, b.genes)))
    genes = []
    for ga, gb in zip(a.genes, b.genes):
        pick = lambda f: rng.choice((getattr(ga, f), getattr(gb, f)))  # noqa: E731
        genes.append(SchoolGene(ga.school, pick("diagnosis"), pick("concepts"), pick("stance"), pick("contrast")))
    return PromptSet(tuple(genes))


@dataclass(frozen=True)
class LLMEdit:
    school: str
    field: str  # "diagnosis" or "stance"
    objective: int  # 0 fidelity, 1 distinctness, 2 length, -1 unguided control
    instruction: str
    current: str


def plan_llm_edit(rng, p: PromptSet, parent_ev) -> LLMEdit:
    """Choose the objective to improve (proportional to how badly the parent does on it) and build the instruction."""
    obj = rng.choices([0, 1, 2], weights=[max(g, 1e-3) for g in parent_ev.objectives])[0]
    lex = lexicons()[0]
    label = {s: profiles()[s]["label"] for s in SCHOOLS}
    if obj == 0:
        school = min(parent_ev.school_fid, key=parent_ev.school_fid.get)
        field = "diagnosis"
        terms = ", ".join(lex[school].must[:5])
        instr = (f"Rewrite this {label[school]} paragraph so that it states the school's core mechanisms more "
                 f"explicitly. Use some of these terms where they fit: {terms}. Do not use terms that belong to the "
                 f"other schools.")
    elif obj == 1:
        pair = min(parent_ev.pair_dis, key=parent_ev.pair_dis.get)
        a, b = pair.split("|")
        school, other = (a, b) if rng.random() < 0.5 else (b, a)
        field = rng.choice(["diagnosis", "stance"])
        instr = (f"The {label[school]} and {label[other]} schools currently reach similar calls on the same events. "
                 f"Rewrite this {field} so that {label[school]} reasons to clearly different calls about growth, "
                 f"inflation and interest rates from {label[other]}, while staying inside its own framework. Do not "
                 f"mention {label[other]} by name.")
    else:
        school = max(SCHOOLS, key=lambda s: p.gene(s).words())
        field = "diagnosis"
        instr = "Shorten this paragraph to at most 40 words, keeping its key mechanisms."
    g = p.gene(school)
    current = " ".join(g.diagnosis if field == "diagnosis" else g.stance)
    return LLMEdit(school, field, obj, instr, current)


UNGUIDED_INSTRUCTION = "Rewrite this paragraph in your own words. Keep its meaning and keep it as one paragraph."


def plan_unguided_edit(rng, p: PromptSet) -> LLMEdit:
    """Control for the guided edit (method nsga2_llmu): the same LLM call and acceptance rule, but the school and the
    field are drawn uniformly at random and the instruction carries no information about any objective."""
    school = rng.choice(SCHOOLS)
    field = rng.choice(["diagnosis", "stance"])
    g = p.gene(school)
    current = " ".join(g.diagnosis if field == "diagnosis" else g.stance)
    return LLMEdit(school, field, -1, UNGUIDED_INSTRUCTION, current)


def edit_messages(e: LLMEdit) -> list[dict]:
    system = ("You edit one paragraph of a prompt for an economist agent. Output only the rewritten paragraph, with "
              "no preamble and no quotation marks.")
    user = f"{e.instruction}\n\nCurrent paragraph:\n{e.current}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def apply_edit(p: PromptSet, e: LLMEdit, text: str) -> PromptSet | None:
    text = " ".join((text or "").split()).strip('"')
    n = len(text.split())
    if n < 5 or n > 120:
        return None
    g = p.gene(e.school)
    new = replace(g, diagnosis=sentences(text)) if e.field == "diagnosis" else replace(g, stance=sentences(text))
    return p.replace_gene(new)


# EvoPrompt (GA) operator, Guo et al. (ICLR 2024), Figure 1 / Algorithm 2: one LLM call performs crossover of two parent
# prompts and mutation of the result. The template is the paper's text verbatim; the answer is read from the
# <prompt>...</prompt> brackets. Applied to the diagnosis paragraph of each school (see PROTOCOL_ADDENDUM_C.md).
EVOPROMPT_GA_TEMPLATE = (
    "Please follow the instruction step-by-step to generate a better prompt.\n"
    "1. Cross over the following prompts and generate a new prompt:\n"
    "Prompt 1: {p1}\n"
    "Prompt 2: {p2}\n"
    "2. Mutate the prompt generated in Step 1 and generate a final prompt bracketed with <prompt> and </prompt>."
)


# Length-constrained variant (addendum D): the paper's template with one sentence appended to step 2.
EVOPROMPT_LC_SUFFIX = " The final prompt must not be longer than the longer of Prompt 1 and Prompt 2."


def evoprompt_messages(p1: str, p2: str, length_constrained: bool = False) -> list[dict]:
    text = EVOPROMPT_GA_TEMPLATE.format(p1=p1, p2=p2) + (EVOPROMPT_LC_SUFFIX if length_constrained else "")
    return [{"role": "user", "content": text}]


def evoprompt_extract(text: str) -> str | None:
    """The text inside the last <prompt>...</prompt> pair, or None if there is none."""
    import re

    found = re.findall(r"<prompt>(.*?)</prompt>", text or "", re.S | re.I)
    return found[-1] if found else None


def roulette(rng, scores: list[float]) -> int:
    """Roulette-wheel selection, p_i = s_i / sum_j s_j (EvoPrompt Section 3.2)."""
    total = sum(scores)
    x = rng.random() * total
    acc = 0.0
    for i, sc in enumerate(scores):
        acc += sc
        if x <= acc:
            return i
    return len(scores) - 1
