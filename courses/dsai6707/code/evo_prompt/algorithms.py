"""Search methods compared in the project. All methods share the representation, the evaluator, the operators and the
evaluation budget N * (G + 1) individuals; they differ only in selection and in whether LLM-guided mutation is used.

  nsga2       NSGA-II (constrained non-dominated sort + crowding) + structural crossover + rule and LLM-guided mutation
  nsga2_rule  the same NSGA-II with rule-based mutation only (ablation: no LLM mutation)
  ga          single-objective GA: feasibility first, then the equal-weight sum of g1..g3, elitist (mu + lambda),
              same variation operators as nsga2 (isolates the effect of selection)
  random      B1: independent random rule perturbations of the hand-written prompt set, keeping the Pareto archive
  ga_rule     the GA with rule-based mutation only (completes the 2 x 2 design selection x mutation; addendum A)
  nsga2_llmu  NSGA-II with unguided LLM mutation: same LLM call and acceptance rule as nsga2, but a random school and
              field and an instruction without objective information (isolates the guidance; addendum A)
  b0          B0: hand-written prompt set, no search (see run_b0 in runner.py)

Every method keeps an external archive of all feasible evaluated prompt sets; final fronts and hypervolume are taken
from that archive, so methods are compared on the same footing.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import mean

from mosaic.backends import Request

from .config import P_CROSS, P_LLM, P_MUT, REF_POINT
from .evaluate import Evaluation, Evaluator
from .genome import PromptSet, b0, concept_pool
from .moo import hv3, nondominated_objectives, rank_and_crowding, select
from .operators import (apply_edit, crossover, edit_messages, mutate_one, perturb_all, plan_llm_edit,
                        plan_unguided_edit)

METHODS = ("nsga2", "nsga2_rule", "ga", "random", "ga_rule", "nsga2_llmu")


@dataclass
class Ind:
    pset: PromptSet
    ev: Evaluation
    origin: str


class Search:
    def __init__(self, evaluator: Evaluator, rng, *, method: str, pop_size: int, backend, log=None):
        if method not in METHODS:
            raise ValueError(method)
        self.ev = evaluator
        self.rng = rng
        self.method = method
        self.N = pop_size
        self.backend = backend
        self.use_llm = method in ("nsga2", "ga", "nsga2_llmu")
        self.ga_select = method in ("ga", "ga_rule")
        self.pool = concept_pool()
        self.base = b0()
        self.archive: dict[str, Ind] = {}
        self.eval_log: list[dict] = []
        self.history: list[dict] = []
        self.evals_done = 0
        self.log = log or (lambda msg: None)

    # ---- bookkeeping -------------------------------------------------------------------------------------------
    def _eval(self, psets: list[PromptSet], origins: list[str], gen: int) -> list[Ind]:
        evs = self.ev.evaluate(psets)
        inds = []
        for p, e, o in zip(psets, evs, origins):
            ind = Ind(p, e, o)
            inds.append(ind)
            if e.feasible:
                self.archive[p.key()] = ind
            self.eval_log.append({"gen": gen, "origin": o, **e.as_dict(), "genome": p.key()})
        self.evals_done += len(psets)
        return inds

    def front(self) -> list[Ind]:
        vals = list(self.archive.values())
        idx = nondominated_objectives([v.ev.objectives for v in vals])
        return [vals[i] for i in idx]

    def hypervolume(self) -> float:
        return hv3([f.ev.objectives for f in self.front()], REF_POINT)

    def _log(self, gen: int, pop: list[Ind]) -> None:
        feas = list(self.archive.values())
        row = {
            "gen": gen,
            "evaluations": self.evals_done,
            "archive": len(feas),
            "front": len(self.front()),
            "hv": round(self.hypervolume(), 6),
            "best_fidelity": round(max((i.ev.fidelity for i in feas), default=math.nan), 4),
            "best_disagreement": round(max((i.ev.disagreement for i in feas), default=math.nan), 4),
            "pop_validity_mean": round(mean(i.ev.validity for i in pop), 4),
            "pop_feasible": round(mean(1.0 if i.ev.feasible else 0.0 for i in pop), 4),
            "api_calls": self.backend.ledger.calls,
            "spent_usd": round(self.backend.ledger.spent, 4),
        }
        self.history.append(row)
        self.log(f"gen {gen:>2}  evals {row['evaluations']:>3}  front {row['front']:>2}  HV {row['hv']:.4f}  "
                 f"best fid {row['best_fidelity']}  calls {row['api_calls']}  spent ${row['spent_usd']}")

    # ---- variation -----------------------------------------------------------------------------------------------
    def _breed(self, pop: list[Ind]) -> tuple[list[PromptSet], list[str]]:
        rng = self.rng
        if self.ga_select:
            keys = [(i.ev.violation, mean(i.ev.objectives)) for i in pop]
        else:
            rank, cd = rank_and_crowding([(i.ev.objectives, i.ev.violation) for i in pop])
            keys = [(rank[k], -cd[k]) for k in range(len(pop))]

        def pick() -> Ind:
            a, b = rng.randrange(len(pop)), rng.randrange(len(pop))  # binary tournament
            return pop[a] if keys[a] <= keys[b] else pop[b]

        kids: list[PromptSet] = []
        origins: list[str] = []
        parents: list[Ind] = []
        llm_idx: list[int] = []
        for _ in range(self.N):
            p1, p2 = pick(), pick()
            if rng.random() < P_CROSS:
                child, o = crossover(rng, p1.pset, p2.pset), "x"
            else:
                child, o = p1.pset, "c"
            if rng.random() < P_MUT:
                if self.use_llm and rng.random() < P_LLM:
                    llm_idx.append(len(kids))
                    o += "L"
                else:
                    child = mutate_one(rng, child, self.pool)
                    o += "R"
            kids.append(child)
            origins.append(o)
            parents.append(p1)

        if llm_idx:
            if self.method == "nsga2_llmu":
                plans = [plan_unguided_edit(rng, kids[k]) for k in llm_idx]
            else:
                plans = [plan_llm_edit(rng, kids[k], parents[k].ev) for k in llm_idx]
            outs = self.backend.generate(
                [Request(messages=edit_messages(p), tag=f"llm-edit|{p.objective}") for p in plans])
            for k, plan, out in zip(llm_idx, plans, outs):
                new = apply_edit(kids[k], plan, out["text"])
                if new is None:  # rejected output: fall back to a rule mutation
                    new = mutate_one(rng, kids[k], self.pool)
                    origins[k] += "f"
                kids[k] = new
        return kids, origins

    def _survive(self, union: list[Ind]) -> list[Ind]:
        if self.ga_select:
            union.sort(key=lambda i: (i.ev.violation, mean(i.ev.objectives)))
            return union[: self.N]
        idx = select([(i.ev.objectives, i.ev.violation) for i in union], self.N)
        return [union[i] for i in idx]

    # ---- drivers ------------------------------------------------------------------------------------------------
    def run(self, gens: int) -> "Search":
        if self.method == "random":
            for g in range(gens + 1):
                psets = [perturb_all(self.rng, self.base, self.pool, 1, 3) for _ in range(self.N)]
                inds = self._eval(psets, ["rand"] * self.N, g)
                self._log(g, inds)
            return self
        psets = [self.base] + [perturb_all(self.rng, self.base, self.pool, 1, 2) for _ in range(self.N - 1)]
        pop = self._eval(psets, ["init"] * self.N, 0)
        self._log(0, pop)
        for g in range(1, gens + 1):
            kids, origins = self._breed(pop)
            cinds = self._eval(kids, origins, g)
            pop = self._survive(pop + cinds)
            self._log(g, pop)
        return self


def run_b0(evaluator: Evaluator) -> Evaluation:
    """B0: the hand-written prompt set, evaluated once on the given events (repeat with other sampling seeds)."""
    return evaluator.evaluate([b0()])[0]
