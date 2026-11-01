"""Command-line runner. Every model call goes through the on-disk cache (results/cache/llm_cache.jsonl), and the search is
deterministic given its seed, so an interrupted run is resumed by running the same command again: finished calls are
read from the cache, and the trajectory is replayed identically.

Examples (run from courses/dsai6707/code):
  python -m evo_prompt.runner --methods b0 --seeds 1 2 3 --heldout
  python -m evo_prompt.runner --methods nsga2 --seeds 1 --gens 2 --pop 6       # smoke test
  python -m evo_prompt.runner --methods nsga2 ga random --seeds 1 2 3 --gens 4 --pop 6 --heldout
  python -m evo_prompt.runner --offline --methods nsga2 --seeds 1 --gens 2 --pop 4 --cache /tmp/x.jsonl   # no network
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path

from mosaic.backends import Cache
from mosaic.teacher import make_items

from .algorithms import METHODS, Search, run_b0
from .backend import BudgetExceeded, HTTPBackend, Ledger, OfflineBackend
from .config import (BASE_URL, BUDGET_USD, CACHE_PATH, HELDOUT_SEED, MAX_TOKENS, MODEL, N_HELDOUT, N_SEARCH,
                     PRICE_IN_PER_MTOK, PRICE_OUT_PER_MTOK, RESULTS_DIR, SEARCH_SEED, TEMPERATURE, TOP_P)
from .evaluate import Evaluator
from .moo import knee


def events(n: int, seed: int) -> list:
    """Synthetic events from the harness generator. One school's items are used as the event list, as in the
    thesis disagreement matrix (mosaic.divergence.export)."""
    return [it.event for it in make_items(n, seed=seed) if it.school == "keynesian"][:n]


def sampling(seed: int) -> dict:
    return {"temperature": TEMPERATURE, "top_p": TOP_P, "max_tokens": MAX_TOKENS, "seed": seed,
            "enable_thinking": False}


def build_backend(args, cache, ledger, seed: int):
    if args.offline:
        return OfflineBackend(sampling(seed), cache, ledger)
    return HTTPBackend(sampling(seed), cache, ledger=ledger, model=args.model, base_url=args.base_url,
                       workers=args.workers)


def metrics_of(ev) -> dict:
    return ev.as_dict()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def run_search(method: str, seed: int, args, cache, ledger, out_root: Path) -> dict:
    out = out_root / f"{method}_s{seed}"
    out.mkdir(parents=True, exist_ok=True)
    backend = build_backend(args, cache, ledger, seed)
    search_events = events(args.n_search, SEARCH_SEED)
    ev = Evaluator(backend, search_events)
    rng = random.Random(seed)
    s = Search(ev, rng, method=method, pop_size=args.pop, backend=backend, log=lambda m: print(f"[{method} s{seed}] {m}"))
    s.run(args.gens)

    front = s.front()
    feas_objs = [f.ev.objectives for f in front]
    kidx = knee(feas_objs) if front else None
    knee_ind = front[kidx] if front else None

    write_csv(out / "gen_log.csv", s.history)
    write_jsonl(out / "evaluations.jsonl", s.eval_log)
    write_jsonl(out / "front.jsonl", [{"objectives": list(f.ev.objectives), **metrics_of(f.ev),
                                       "genome": f.pset.key()} for f in front])
    result = {"method": method, "seed": seed, "gens": args.gens, "pop": args.pop, "n_search": args.n_search,
              "evaluations": s.evals_done, "hv_final": s.history[-1]["hv"] if s.history else None,
              "front_size": len(front), "search_events": [e.id for e in search_events],
              "knee": metrics_of(knee_ind.ev) if knee_ind else None,
              "api_calls_total": ledger.calls, "spent_usd_total": round(ledger.spent, 4)}
    if knee_ind is not None:
        RESULTS_DIR.joinpath("best_prompts").mkdir(parents=True, exist_ok=True)
        (RESULTS_DIR / "best_prompts" / f"{method}_s{seed}_knee.txt").write_text(
            knee_ind.pset.render() + "\n# metrics\n" + json.dumps(metrics_of(knee_ind.ev), indent=1) + "\n",
            encoding="utf-8")
        if args.heldout:
            held = events(args.n_heldout, HELDOUT_SEED)
            hev = Evaluator(backend, held).evaluate([knee_ind.pset])[0]
            result["heldout_events"] = [e.id for e in held]
            result["heldout"] = metrics_of(hev)
    (out / "final.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    return result


def run_b0_seed(seed: int, args, cache, ledger, out_root: Path) -> dict:
    out = out_root / f"b0_s{seed}"
    out.mkdir(parents=True, exist_ok=True)
    backend = build_backend(args, cache, ledger, seed)
    search_events = events(args.n_search, SEARCH_SEED)
    e = run_b0(Evaluator(backend, search_events))
    result = {"method": "b0", "seed": seed, "search_events": [x.id for x in search_events], "search": metrics_of(e),
              "api_calls_total": ledger.calls, "spent_usd_total": round(ledger.spent, 4)}
    if args.heldout:
        held = events(args.n_heldout, HELDOUT_SEED)
        result["heldout_events"] = [x.id for x in held]
        result["heldout"] = metrics_of(run_b0(Evaluator(backend, held)))
    (out / "final.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--methods", nargs="+", default=["nsga2"], choices=list(METHODS) + ["b0"])
    ap.add_argument("--seeds", nargs="+", type=int, default=[1, 2, 3])
    ap.add_argument("--gens", type=int, default=5)
    ap.add_argument("--pop", type=int, default=8)
    ap.add_argument("--n-search", type=int, default=N_SEARCH)
    ap.add_argument("--n-heldout", type=int, default=N_HELDOUT)
    ap.add_argument("--heldout", action="store_true", help="re-measure each knee (and B0) on held-out events")
    ap.add_argument("--offline", action="store_true", help="deterministic fake model, no network (tests and dry runs)")
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--base-url", default=BASE_URL)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--budget", type=float, default=BUDGET_USD, help="USD cap, enforced on estimated cost")
    ap.add_argument("--price-in", type=float, default=PRICE_IN_PER_MTOK)
    ap.add_argument("--price-out", type=float, default=PRICE_OUT_PER_MTOK)
    ap.add_argument("--cache", type=Path, default=CACHE_PATH)
    ap.add_argument("--out", type=Path, default=RESULTS_DIR / "runs")
    args = ap.parse_args(argv)

    cache = Cache(args.cache)
    ledger = Ledger(args.budget, args.price_in, args.price_out)
    summaries = []
    try:
        for method in args.methods:
            for seed in args.seeds:
                if method == "b0":
                    summaries.append(run_b0_seed(seed, args, cache, ledger, args.out))
                else:
                    summaries.append(run_search(method, seed, args, cache, ledger, args.out))
                print(f"done {method} seed {seed}: api_calls {ledger.calls}, spent ${ledger.spent:.2f}")
    except BudgetExceeded as e:
        print(f"STOPPED: {e}. Finished calls are cached; rerun the same command to resume.", file=sys.stderr)
        return 2
    print(f"ledger: calls {ledger.calls}, tokens in {ledger.tok_in}, out {ledger.tok_out}, "
          f"estimated spend ${ledger.spent:.2f} of ${ledger.budget:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
