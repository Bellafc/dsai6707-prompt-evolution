"""Run one or more arms of an experiment on a split, score, and log.

  mosaic run --exp exp01 --arms A,B,C --split dev [--limit 20] [--set arms.B.k=5] [--backend fake] --note "..."
  mosaic run --exp exp01 --arms A,B,C,D --split test --final --note "final"

Output per arm: runs/<run_id>/{config.json, generations.jsonl, scores.jsonl, summary.json} and one row in
experiments/results.tsv. Generations are cached (cache/generations.jsonl), so a rerun with identical prompts and
sampling costs nothing.
"""

from __future__ import annotations

import copy
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from mosaic import SCHOOLS, locks
from mosaic.backends import Cache, FakeBackend, OpenAIBackend, Request, VLLMBackend
from mosaic.config import ROOT, load_toml, paths, stable_hash
from mosaic.data import load_events, load_trajectories, write_jsonl
from mosaic.metrics import diversity, score_response, signal_set
from mosaic.parse import parse
from mosaic.prompts import build_messages, has_placeholder, pick_exemplars, read_prompt

RESULTS = ROOT / "experiments/results.tsv"
RUNS_DIR = ROOT / "runs"
CACHE_PATH = ROOT / "cache/generations.jsonl"
COLUMNS = ["run_id", "utc", "commit", "dirty", "exp", "arm", "split", "n_events", "consistency_mean",
           "consistency_keynesian", "consistency_austrian", "consistency_monetarist", "contamination_mean",
           "completeness_mean", "output_rate", "diversity", "usd", "status", "config_hash", "note"]


def set_dotted(cfg: dict, assignment: str) -> None:
    key, _, raw = assignment.partition("=")
    try:
        val = json.loads(raw)
    except json.JSONDecodeError:
        val = raw
    node = cfg
    *parents, last = key.split(".")
    for k in parents:
        node = node.setdefault(k, {})
    node[last] = val


def prior_finals(exp: str, arm: str) -> list[dict]:
    if not RESULTS.exists():
        return []
    with open(RESULTS, encoding="utf-8") as f:
        return [r for r in csv.DictReader(f, delimiter="\t")
                if r["exp"] == exp and r["arm"] == arm and r["status"] == "final"]


def append_result(row: dict) -> None:
    new = not RESULTS.exists()
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, delimiter="\t", extrasaction="ignore")
        if new:
            w.writeheader()
        w.writerow(row)


def make_backends(cfg: dict, arms: list[str], kind: str | None, cache: Cache) -> dict:
    sampling = cfg["sampling"]
    out = {}
    local = [a for a in arms if a in ("A", "B", "C")]
    if local:
        if kind == "fake":
            be = FakeBackend(sampling, cache)
        else:
            p = paths()
            adapters = {s: str(Path(p["adapters_dir"]) / s) for s in SCHOOLS} if "C" in arms else {}
            m = cfg["model"]
            be = VLLMBackend(sampling, cache, base_model=m["base"], adapters=adapters,
                             max_model_len=m.get("max_model_len", 16384),
                             gpu_memory_utilization=m.get("gpu_memory_utilization", 0.9),
                             max_lora_rank=m.get("max_lora_rank", 32))
        for a in local:
            out[a] = be
    if "D" in arms:
        t = cfg["teacher"]
        out["D"] = FakeBackend(sampling, cache) if kind == "fake" else OpenAIBackend(
            sampling, cache, model=t["model"], usd_per_mtok_in=t["usd_per_mtok_in"],
            usd_per_mtok_out=t["usd_per_mtok_out"], budget_usd=t["budget_usd"])
    return out


def run(exp: str, arms: list[str], split: str, *, schools: list[str] | None = None, limit: int | None = None,
        overrides: list[str] | None = None, backend: str | None = None, final: bool = False,
        allow_rerun: str | None = None, note: str = "") -> list[dict]:
    cfg = copy.deepcopy(load_toml(ROOT / f"configs/{exp}.toml"))
    for o in overrides or []:
        set_dotted(cfg, o)
    schools = schools or list(SCHOOLS)
    p = paths()

    if split == "test":
        if not final:
            raise SystemExit("the test split is only run with --final (see program.md, rule 1)")
        if limit or overrides or backend == "fake":
            raise SystemExit("--final runs use the frozen config: no --limit, --set or fake backend")
        problems = locks.verify(exp)
        if problems:
            raise SystemExit("lock check failed:\n  " + "\n  ".join(problems))
        for a in arms:
            if prior_finals(exp, a) and not allow_rerun:
                raise SystemExit(f"arm {a} already has a final run; pass --allow-rerun '<reason>' to override")
    elif final:
        raise SystemExit("--final is only for the test split")

    events = load_events(Path(p["events_dir"]) / f"{split}.jsonl")
    if limit:
        events = events[:limit]
    prompts_dir = ROOT / "configs/prompts"
    user_t = read_prompt("user_template.txt", prompts_dir)
    systems = {s: read_prompt(f"{s}.system.txt", prompts_dir) for s in schools}
    placeholders = [n for n, t in [("user_template", user_t), *systems.items()] if has_placeholder(t)]
    if placeholders:
        print(f"WARNING: placeholder prompts ({', '.join(placeholders)}); dev numbers are not comparable "
              "to the Confirmation until the original prompts are restored (program.md, Task 0)")

    cache = Cache(CACHE_PATH)
    backends = make_backends(cfg, arms, backend, cache)
    git = locks.git_state()
    summaries = []
    for arm in arms:
        acfg = cfg["arms"].get(arm, {})
        pools = {}
        if arm == "B":
            pools = {s: load_trajectories(Path(p["trajectories_dir"]) / f"{s}.jsonl", s) for s in schools}
        reqs, meta = [], []
        for ev in events:
            for s in schools:
                exemplars = (pick_exemplars(pools[s], ev, int(acfg.get("k", 3)), acfg.get("strategy", "random"),
                                            int(cfg["sampling"].get("seed", 0)), acfg.get("max_chars"))
                             if arm == "B" else None)
                system = systems[s]
                if arm == "B" and acfg.get("extra_dir"):  # optional extra school guidance, few-shot arm only
                    extra = ROOT / acfg["extra_dir"] / f"{s}.txt"
                    if extra.exists():
                        system = system.rstrip() + "\n\n" + extra.read_text(encoding="utf-8").strip()
                msgs = build_messages(arm, s, ev, system=system, user_template=user_t, exemplars=exemplars)
                reqs.append(Request(msgs, adapter=s if arm == "C" else None, tag=f"{arm}|{s}|{ev.id}"))
                meta.append((ev, s))
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        chash = stable_hash({"cfg": cfg, "arm": arm, "split": split, "limit": limit, "schools": schools})[:8]
        run_id = f"{exp}-{arm}-{split}-{utc}-{chash}"
        out, n = RUNS_DIR / run_id, 1
        while out.exists():  # two runs in the same second
            n += 1
            out = RUNS_DIR / f"{run_id}-{n}"
        run_id = out.name
        out.mkdir(parents=True)
        if split == "test":
            locks.log_test_access(exp, run_id, note or "final")
        gens = backends[arm].generate(reqs)

        rows, by_event = [], defaultdict(dict)
        for (ev, s), g in zip(meta, gens):
            parsed = parse(g["text"])
            sc = score_response(g["text"], parsed, s)
            rows.append({"event_id": ev.id, "school": s, "difficulty": ev.difficulty, "category": ev.category,
                         **sc, "signals": parsed.signals})
            by_event[ev.id][s] = signal_set(parsed)
        div = {e: diversity([d[s] for s in schools if s in d]) for e, d in by_event.items()} if len(schools) > 1 else {}

        (out / "config.json").write_text(json.dumps(
            {"exp": exp, "arm": arm, "split": split, "schools": schools, "limit": limit, "overrides": overrides,
             "backend": backend or "default", "git": git, "cfg": cfg, "note": note}, indent=2, ensure_ascii=False))
        write_jsonl(out / "generations.jsonl", [{"event_id": ev.id, "school": s, "messages": r.messages, **g}
                                                for (ev, s), r, g in zip(meta, reqs, gens)])
        for r in rows:
            r["diversity"] = div.get(r["event_id"])
        write_jsonl(out / "scores.jsonl", rows)

        cons = {s: float(np.mean([r["consistency"] for r in rows if r["school"] == s])) for s in schools}
        dv = [v for v in div.values() if v is not None]
        summary = {
            "run_id": run_id, "utc": utc, "commit": git["commit"], "dirty": git["dirty"], "exp": exp, "arm": arm,
            "split": split, "n_events": len(events), "consistency_mean": round(float(np.mean(list(cons.values()))), 4),
            **{f"consistency_{s}": round(v, 4) for s, v in cons.items()},
            "contamination_mean": round(float(np.mean([r["anti_hits"] for r in rows])), 4),
            "completeness_mean": round(float(np.mean([r["completeness"] for r in rows])), 4),
            "output_rate": round(float(np.mean([r["has_output"] for r in rows])), 4),
            "diversity": round(float(np.mean(dv)), 4) if dv else "",
            "usd": round(getattr(backends[arm], "spent", 0.0), 4),
            "status": "final" if final else "dev", "config_hash": chash,
            "note": (note + (f" | rerun: {allow_rerun}" if allow_rerun else "")).replace("\t", " ").replace("\n", " "),
            "cached_fraction": round(float(np.mean([g["cached"] for g in gens])), 3),
        }
        (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
        append_result(summary)
        summaries.append(summary)
        print(json.dumps(summary, ensure_ascii=False))
    return summaries
