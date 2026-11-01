"""Analysis of the finished matrix. Reads results/runs/*, re-scores held-out events from the disk cache (no new model
calls: the CacheOnly backend raises if a call is missing), and writes tables and figures.

Outputs (results/):
  summary_search.csv     per run: search-level metrics (HV, knee on search events, front size, evaluations)
  summary_table.md       mean +- std over seeds for every method (search level and held-out level)
  heldout_per_event.csv  per held-out event, method metrics averaged over seeds (paired input for the tests)
  heldout_tests.csv      paired exact sign-flip tests over the 10 held-out events, Holm-corrected
  figures/*.png          HV vs generation, Pareto fronts, held-out bar chart
"""

from __future__ import annotations

import csv
import itertools
import json
import math
import statistics
from pathlib import Path

from mosaic.backends import Backend, Cache
from mosaic.stats import holm, paired

from .backend import Ledger  # noqa: F401  (kept for API symmetry)
from .config import CACHE_PATH, HELDOUT_SEED, MODEL, N_HELDOUT, RESULTS_DIR, SEARCH_SEED
from .evaluate import Evaluator
from .genome import SchoolGene, PromptSet, b0
from .moo import knee
from .runner import events, sampling

METHODS = ["nsga2", "ga", "random", "nsga2_rule"]
LABEL = {"nsga2": "NSGA-II + LLM", "ga": "GA (weighted sum)", "random": "Random search",
         "nsga2_rule": "NSGA-II, rule only", "b0": "B0 hand-written"}
SEEDS = [1, 2, 3]


class CacheOnly(Backend):
    """Reads generations from the disk cache only; a missing entry is an error, never a new API call."""

    model_id = MODEL

    def __init__(self, cache: Cache, seed: int):
        super().__init__(sampling(seed), cache)

    def generate(self, reqs):
        out = []
        for r in reqs:
            hit = self.cache.get(self.key(r))
            if hit is None:
                raise KeyError("missing cached generation (would need an API call)")
            out.append({"text": hit["text"], "cached": True})
        return out


def pset_from_key(key: str) -> PromptSet:
    d = json.loads(key)
    genes = tuple(SchoolGene(g["school"], tuple(g["diagnosis"]), tuple(g["concepts"]), tuple(g["stance"]),
                             tuple(g["contrast"])) for g in d["genes"])
    return PromptSet(genes)


def load_runs(root: Path) -> dict:
    runs: dict[tuple[str, int], dict] = {}
    for d in sorted(root.iterdir()):
        if d.is_dir() and (d / "final.json").exists():
            method, seed = d.name.rsplit("_s", 1)
            runs[(method, int(seed))] = {"dir": d, "final": json.loads((d / "final.json").read_text())}
    return runs


def knee_key(front_path: Path) -> str:
    rows = [json.loads(x) for x in front_path.read_text().splitlines() if x.strip()]
    objs = [tuple(r["objectives"]) for r in rows]
    return rows[knee(objs)]["genome"]


def mean_sd(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if not xs:
        return (None, None)
    return (statistics.mean(xs), statistics.stdev(xs) if len(xs) > 1 else 0.0)


def fmt(ms, nd=3):
    m, s = ms
    return "n/a" if m is None else f"{m:.{nd}f} ± {s:.{nd}f}"


def sign_flip_exact(diffs: list[float]) -> float:
    """Two-sided exact permutation p-value for the mean paired difference (all 2^n sign patterns)."""
    n = len(diffs)
    obs = abs(sum(diffs) / n)
    hits = total = 0
    for signs in itertools.product((-1.0, 1.0), repeat=n):
        total += 1
        if abs(sum(s * d for s, d in zip(signs, diffs)) / n) >= obs - 1e-12:
            hits += 1
    return hits / total


def per_event_scores(pset: PromptSet, seed: int, cache: Cache, evs: list) -> list[dict]:
    backend = CacheOnly(cache, seed)
    out = []
    for e in evs:
        ev = Evaluator(backend, [e]).evaluate([pset])[0]
        out.append({"event": e.id, "fidelity": ev.fidelity, "disagreement": ev.disagreement, "validity": ev.validity,
                    "words": ev.words})
    return out


def main(results: Path = RESULTS_DIR) -> None:
    runs = load_runs(results / "runs")
    cache = Cache(CACHE_PATH)
    held = events(N_HELDOUT, HELDOUT_SEED)
    (results / "figures").mkdir(parents=True, exist_ok=True)

    # ---- search-level summary per run ------------------------------------------------------------------------
    rows = []
    for (m, s), r in sorted(runs.items()):
        if m == "b0":
            continue  # B0 has no search; it is handled below
        f = r["final"]
        k = f.get("knee") or {}
        rows.append({"method": m, "seed": s, "hv_final": f["hv_final"], "front_size": f["front_size"],
                     "evaluations": f["evaluations"], "knee_fidelity": k.get("fidelity"),
                     "knee_disagreement": k.get("disagreement"), "knee_validity": k.get("validity"),
                     "knee_words": k.get("words")})
    with (results / "summary_search.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    with (results / "summary.csv").open("w", newline="") as fh:
        fields = ["method", "seed", "hv_final", "front_size", "evaluations", "search_fidelity", "search_disagreement",
                  "search_validity", "search_words", "heldout_fidelity", "heldout_disagreement", "heldout_validity",
                  "heldout_words"]
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for (m, s), r in sorted(runs.items()):
            f = r["final"]
            if m == "b0":
                sr, hr = f.get("search", {}), f.get("heldout", {})
                w.writerow({"method": m, "seed": s, "search_fidelity": sr.get("fidelity"),
                            "search_disagreement": sr.get("disagreement"), "search_validity": sr.get("validity"),
                            "search_words": sr.get("words"), "heldout_fidelity": hr.get("fidelity"),
                            "heldout_disagreement": hr.get("disagreement"), "heldout_validity": hr.get("validity"),
                            "heldout_words": hr.get("words")})
                continue
            k, hr = f.get("knee") or {}, f.get("heldout") or {}
            w.writerow({"method": m, "seed": s, "hv_final": f["hv_final"], "front_size": f["front_size"],
                        "evaluations": f["evaluations"], "search_fidelity": k.get("fidelity"),
                        "search_disagreement": k.get("disagreement"), "search_validity": k.get("validity"),
                        "search_words": k.get("words"), "heldout_fidelity": hr.get("fidelity"),
                        "heldout_disagreement": hr.get("disagreement"), "heldout_validity": hr.get("validity"),
                        "heldout_words": hr.get("words")})

    # ---- held-out per event: knees (searched methods) and B0 (three replicates) -----------------------------
    per_event: dict[str, list[list[dict]]] = {}  # method -> seed -> per-event rows
    for m in METHODS:
        per_event[m] = []
        for s in SEEDS:
            if (m, s) not in runs:
                continue
            key = knee_key(runs[(m, s)]["dir"] / "front.jsonl")
            per_event[m].append(per_event_scores(pset_from_key(key), s, cache, held))
    per_event["b0"] = [per_event_scores(b0(), s, cache, held) for s in SEEDS]

    # average over seeds per event
    avg: dict[str, list[dict]] = {}
    for m, seeds_rows in per_event.items():
        avg[m] = []
        for i, e in enumerate(held):
            vals = {k: statistics.mean(sr[i][k] for sr in seeds_rows) for k in ("fidelity", "disagreement", "validity", "words")}
            avg[m].append({"event": e.id, **vals})
    with (results / "heldout_per_event.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["method", "event", "fidelity", "disagreement", "validity", "words"])
        for m in avg:
            for r in avg[m]:
                w.writerow([m, r["event"], round(r["fidelity"], 4), round(r["disagreement"], 4),
                            round(r["validity"], 4), round(r["words"], 1)])

    # ---- paired tests: each method vs B0 on fidelity and disagreement, Holm over the family ---------------
    tests = []
    for m in METHODS:
        for metric in ("fidelity", "disagreement"):
            a = [r[metric] for r in avg["b0"]]
            b = [r[metric] for r in avg[m]]
            diffs = [y - x for x, y in zip(a, b)]  # method minus B0
            boot = paired(a, b, n_boot=10000, n_perm=1, seed=0)  # bootstrap CI over events (mosaic.stats)
            tests.append({"comparison": f"{m} - b0", "metric": metric, "mean_diff": sum(diffs) / len(diffs),
                          "ci_lo": boot["ci_lo"], "ci_hi": boot["ci_hi"], "p_raw": sign_flip_exact(diffs)})
    adj = holm([t["p_raw"] for t in tests])
    for t, p in zip(tests, adj):
        t["p_holm"] = p
        t["mean_diff"] = round(t["mean_diff"], 4)
        t["ci_lo"] = round(t["ci_lo"], 4)
        t["ci_hi"] = round(t["ci_hi"], 4)
        t["p_raw"] = round(t["p_raw"], 4)
        t["p_holm"] = round(p, 4)
    with (results / "heldout_tests.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["comparison", "metric", "mean_diff", "ci_lo", "ci_hi", "p_raw", "p_holm"])
        w.writeheader()
        for t in tests:
            w.writerow({k: t[k] for k in w.fieldnames})

    # ---- markdown summary -----------------------------------------------------------------------------------
    lines = ["# Summary (3 seeds per search method; B0 over 3 sampling replicates)", "",
             "## Search events (seed 23, 5 events): archive hypervolume and knee solution", "",
             "| Method | Hypervolume | Front size | Knee fidelity | Knee disagreement | Knee validity | Knee words |",
             "|---|---|---|---|---|---|---|"]
    for m in METHODS:
        rr = [r for r in rows if r["method"] == m]
        lines.append(f"| {LABEL[m]} | {fmt(mean_sd([r['hv_final'] for r in rr]), 4)} | "
                     f"{fmt(mean_sd([r['front_size'] for r in rr]), 1)} | "
                     f"{fmt(mean_sd([r['knee_fidelity'] for r in rr]))} | "
                     f"{fmt(mean_sd([r['knee_disagreement'] for r in rr]))} | "
                     f"{fmt(mean_sd([r['knee_validity'] for r in rr]))} | "
                     f"{fmt(mean_sd([r['knee_words'] for r in rr]), 0)} |")
    lines += ["", "## Held-out events (seed 29, 10 events): knee solution, mean ± std over seeds", "",
              "| Method | Fidelity | Disagreement | Validity | Words |", "|---|---|---|---|---|"]
    for m in ["b0"] + METHODS:
        ho = [v for v in (runs[(m, s)]["final"].get("heldout") for s in SEEDS if (m, s) in runs) if v]
        if m == "b0":
            ho = [{"fidelity": x["fidelity"], "disagreement": x["disagreement"], "validity": x["validity"],
                   "words": x["words"]} for x in
                  [{"fidelity": statistics.mean(r["fidelity"] for r in sr), "disagreement": statistics.mean(
                      r["disagreement"] for r in sr), "validity": statistics.mean(r["validity"] for r in sr),
                    "words": statistics.mean(r["words"] for r in sr)} for sr in per_event["b0"]]]
        lines.append(f"| {LABEL[m]} | {fmt(mean_sd([h['fidelity'] for h in ho]))} | "
                     f"{fmt(mean_sd([h['disagreement'] for h in ho]))} | "
                     f"{fmt(mean_sd([h['validity'] for h in ho]))} | "
                     f"{fmt(mean_sd([h['words'] for h in ho]), 0)} |")
    lines += ["", "## Paired tests vs B0 on the 10 held-out events (exact sign-flip, Holm over 8 tests)", "",
              "| Comparison | Metric | Mean difference (method - B0) | 95% bootstrap CI | p (exact, raw) | p (Holm) |",
              "|---|---|---|---|---|---|"]
    for t in tests:
        lines.append(f"| {t['comparison']} | {t['metric']} | {t['mean_diff']:+.4f} | [{t['ci_lo']:+.4f}, {t['ci_hi']:+.4f}] | "
                     f"{t['p_raw']:.4f} | {t['p_holm']:.4f} |")
    (results / "summary_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
