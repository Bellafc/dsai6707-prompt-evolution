"""Objectives of a prompt set, measured on the search (or held-out) events through the disk-cached backend.

  f1 fidelity     mean over schools and events of the lexicon consistency C_s (mosaic.metrics), in [0, 1]
  f2 disagreement mean over the three school pairs of mosaic.divergence.distance (share of assets with a different
                  call), in [0, 1]
  f3 length       whitespace words of all school genes, capped at LENGTH_REF_WORDS
Minimisation form used by the search: g1 = 1 - fidelity, g2 = 1 - disagreement, g3 = min(1, words / LENGTH_REF_WORDS).
Feasibility: share of parseable school outputs >= FEASIBILITY (Deb's constraint-handling rule).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from itertools import combinations
from statistics import mean

from mosaic.backends import Request
from mosaic.divergence import distance, parse
from mosaic.metrics import consistency, lexicons

from .config import FEASIBILITY, LENGTH_REF_WORDS
from .genome import SCHOOLS, PromptSet, decode


@dataclass
class Evaluation:
    school_fid: dict  # school -> mean consistency over events
    pair_dis: dict  # "a|b" -> mean signal disagreement over events
    validity: float  # parseable outputs / all outputs
    words: int

    @property
    def fidelity(self) -> float:
        return mean(self.school_fid.values())

    @property
    def disagreement(self) -> float:
        return mean(self.pair_dis.values())

    @property
    def violation(self) -> float:
        return max(0.0, FEASIBILITY - self.validity)

    @property
    def feasible(self) -> bool:
        return self.violation == 0.0

    @property
    def objectives(self) -> tuple[float, float, float]:
        return (1.0 - self.fidelity, 1.0 - self.disagreement, min(1.0, self.words / LENGTH_REF_WORDS))

    def as_dict(self) -> dict:
        return {"fidelity": round(self.fidelity, 4), "disagreement": round(self.disagreement, 4),
                "validity": round(self.validity, 4), "words": self.words, "feasible": self.feasible,
                "school_fid": {k: round(v, 4) for k, v in self.school_fid.items()},
                "pair_dis": {k: round(v, 4) for k, v in self.pair_dis.items()},
                "objectives": [round(x, 4) for x in self.objectives]}


class Evaluator:
    def __init__(self, backend, events):
        self.backend = backend
        self.events = list(events)
        self.lex = lexicons()[0]
        self.memo: dict[str, Evaluation] = {}

    def evaluate(self, psets: list[PromptSet]) -> list[Evaluation]:
        todo: dict[str, PromptSet] = {}
        for p in psets:
            k = p.key()
            if k not in self.memo and k not in todo:
                todo[k] = p
        if todo:
            reqs: list[Request] = []
            slot: dict[str, int] = {}
            where = []  # (prompt key, school, event id, request index)
            for k, p in todo.items():
                for g in p.genes:
                    for ev in self.events:
                        msgs = decode(g, ev)
                        mk = json.dumps(msgs, sort_keys=True)
                        if mk not in slot:
                            slot[mk] = len(reqs)
                            reqs.append(Request(messages=msgs, tag=f"{g.school}|{ev.id}"))
                        where.append((k, g.school, ev.id, slot[mk]))
            outs = self.backend.generate(reqs)
            texts = {(k, s, e): outs[i]["text"] for k, s, e, i in where}
            for k, p in todo.items():
                self.memo[k] = self._score(p, texts)
        return [self.memo[p.key()] for p in psets]

    def _score(self, p: PromptSet, texts: dict) -> Evaluation:
        parsed: dict[str, dict] = {s: {} for s in SCHOOLS}
        school_fid: dict[str, float] = {}
        n = ok = 0
        k = p.key()
        for s in SCHOOLS:
            vals = []
            for ev in self.events:
                t = texts[(k, s, ev.id)]
                n += 1
                vals.append(consistency(t, self.lex[s])["consistency"])
                pr = parse(t)
                if pr is not None:
                    ok += 1
                    parsed[s][ev.id] = pr
            school_fid[s] = mean(vals)
        pair_dis = {}
        for a, b in combinations(SCHOOLS, 2):
            d = distance(parsed[a], parsed[b])
            pair_dis[f"{a}|{b}"] = d["disagreement"] if d.get("n") else 0.0
        return Evaluation(school_fid=school_fid, pair_dis=pair_dis, validity=ok / n, words=p.words())
