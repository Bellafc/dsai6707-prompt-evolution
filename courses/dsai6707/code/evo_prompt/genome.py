"""Genome of a prompt set: one gene per school (diagnosis, concepts, stance, contrast).

A genome decodes to the messages() layout of mosaic.divergence, so the prompt scaffold and the output format are the
thesis harness unchanged. Only the free-text fields and the concept list vary.
"""

from __future__ import annotations

import dataclasses
import json
import re
from dataclasses import dataclass
from functools import lru_cache

from mosaic.divergence import messages, profiles

SCHOOLS = ("keynesian", "austrian", "monetarist")
_SPLIT = re.compile(r"(?<=[.!?])\s+")


def sentences(text: str) -> tuple[str, ...]:
    return tuple(s.strip() for s in _SPLIT.split(text.strip()) if s.strip())


@lru_cache(maxsize=1)
def _profiles() -> dict:
    return profiles()  # read-only; the hand-written school profiles of the thesis harness


@dataclass(frozen=True)
class SchoolGene:
    school: str
    diagnosis: tuple[str, ...]  # sentences
    concepts: tuple[str, ...]  # ordered subset of the concept pool
    stance: tuple[str, ...]  # sentences: how the school reads typical events
    contrast: tuple[str, ...] = ()  # optional sentences: "unlike the other schools, you ..."

    def words(self) -> int:
        return len(" ".join(self.diagnosis + self.stance + self.contrast + self.concepts).split())


@dataclass(frozen=True)
class PromptSet:
    genes: tuple[SchoolGene, ...]  # always in SCHOOLS order

    def key(self) -> str:
        return json.dumps(dataclasses.asdict(self), sort_keys=True)

    def gene(self, school: str) -> SchoolGene:
        return next(g for g in self.genes if g.school == school)

    def replace_gene(self, new: SchoolGene) -> PromptSet:
        return PromptSet(tuple(new if g.school == new.school else g for g in self.genes))

    def words(self) -> int:
        return sum(g.words() for g in self.genes)

    def render(self) -> str:
        out = []
        for g in self.genes:
            out.append(f"## {g.school}")
            out.append("diagnosis: " + " ".join(g.diagnosis))
            out.append("concepts: " + ", ".join(g.concepts))
            out.append("stance: " + " ".join(g.stance))
            if g.contrast:
                out.append("contrast: " + " ".join(g.contrast))
            out.append("")
        return "\n".join(out)


def b0() -> PromptSet:
    """Hand-written baseline: the thesis school profiles unchanged (no search)."""
    genes = []
    for s in SCHOOLS:
        p = _profiles()[s]
        genes.append(SchoolGene(s, sentences(p["diagnosis"]), tuple(p["concepts"]), sentences(p["signals"]), ()))
    return PromptSet(tuple(genes))


def concept_pool() -> tuple[str, ...]:
    seen: dict[str, None] = {}
    for s in SCHOOLS:
        for c in _profiles()[s]["concepts"]:
            seen.setdefault(c, None)
    return tuple(seen)


def decode(gene: SchoolGene, event) -> list[dict]:
    """Chat messages for one school on one event, in the mosaic.divergence layout."""
    base = _profiles()[gene.school]
    prof = {
        "label": base["label"],
        "diagnosis": " ".join(gene.diagnosis + gene.contrast),
        "concepts": list(gene.concepts),
        "signals": " ".join(gene.stance),
        "good_news": base["good_news"],
    }
    return messages(prof, event)
