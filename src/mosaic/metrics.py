"""Metrics. The definitions follow the Confirmation report, Sec. 4.2.3, and are frozen by prereg/exp01:

  consistency  C_s = max(0, 1/2 * |must hits|/|must pool| + 1/2 * min(|strong hits|/5, 1) - 0.15 * |anti hits|)  (4.1)
  contamination  mean |anti-signal hits| per response
  completeness   fraction of the 7 structural elements present (parse.Parsed.completeness)
  diversity      per event, mean pairwise Jaccard distance of the schools' (asset, direction) sets          (4.2)

Plus forecasting scores used by later experiments (Brier, ECE). Changing anything here after a lock exists makes
`mosaic run --split test` refuse to run: that is intended. Version the prereg instead.
"""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from mosaic.config import ROOT, load_toml
from mosaic.parse import Parsed


@dataclass(frozen=True)
class Lexicon:
    must: tuple[str, ...]
    strong: tuple[str, ...]
    anti: tuple[str, ...]


@lru_cache(maxsize=4)
def lexicons(path: str = "configs/lexicons.toml") -> tuple[dict[str, Lexicon], dict]:
    cfg = load_toml(ROOT / path)
    opts = cfg.get("options", {})
    lex = {s: Lexicon(tuple(v["must"]), tuple(v["strong"]), tuple(v["anti"])) for s, v in cfg["schools"].items()}
    return lex, opts


@lru_cache(maxsize=4096)
def _pattern(term: str) -> re.Pattern:
    # word boundaries only where the term starts/ends with a word character ("MV=PQ", "IS-LM" still match)
    body = r"\s+".join(re.escape(w) for w in term.split())
    left = r"(?<!\w)" if term[0].isalnum() else ""
    right = r"(?!\w)" if term[-1].isalnum() else ""
    return re.compile(left + body + right, re.I)


def hits(text: str, terms: tuple[str, ...], mode: str = "distinct") -> int:
    if mode == "occurrences":
        return sum(len(_pattern(t).findall(text)) for t in terms)
    return sum(1 for t in terms if _pattern(t).search(text))


def consistency(text: str, lex: Lexicon, mode: str = "distinct") -> dict:
    m, s, a = hits(text, lex.must, mode), hits(text, lex.strong, mode), hits(text, lex.anti, mode)
    score = max(0.0, 0.5 * m / len(lex.must) + 0.5 * min(s / 5, 1.0) - 0.15 * a)
    return {"consistency": score, "must_hits": m, "strong_hits": s, "anti_hits": a}


def jaccard_distance(a: set, b: set) -> float | None:
    u = a | b
    return None if not u else 1 - len(a & b) / len(u)


def diversity(signal_sets: list[set]) -> float | None:
    """Mean pairwise Jaccard distance across schools for one event; pairs with two empty sets are skipped."""
    d = [x for x in (jaccard_distance(a, b) for a, b in itertools.combinations(signal_sets, 2)) if x is not None]
    return float(np.mean(d)) if d else None


def signal_set(p: Parsed, assets: tuple[str, ...] | None = None) -> set[tuple[str, str]]:
    return {(k, v) for k, v in p.signals.items() if not assets or k in assets}


def score_response(text: str, parsed: Parsed, school: str) -> dict:
    lex, opts = lexicons()
    scope = parsed.output if opts.get("scope", "full") == "output" else text
    r = consistency(scope, lex[school], opts.get("count_mode", "distinct"))
    r.update({"completeness": parsed.completeness(), "has_output": parsed.tags["Output"],
              "has_scenarios": parsed.has_scenarios, "has_signals": parsed.has_signals,
              "n_signals": len(parsed.signals), "scenario_sum": round(parsed.scenario_sum, 4)})
    return r


# --- forecasting scores (exp03+) ------------------------------------------------------------------

def brier(p: np.ndarray, y: np.ndarray) -> float:
    return float(np.mean((np.asarray(p, float) - np.asarray(y, float)) ** 2))


def ece(p: np.ndarray, y: np.ndarray, bins: int = 10) -> float:
    p, y = np.asarray(p, float), np.asarray(y, float)
    idx = np.minimum((p * bins).astype(int), bins - 1)
    return float(sum(abs(p[idx == b].mean() - y[idx == b].mean()) * (idx == b).mean()
                     for b in range(bins) if (idx == b).any()))
