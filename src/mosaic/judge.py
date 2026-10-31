"""LLM-as-judge and human validation for exp01 (prereg/exp01_amendment_2.md).

Why: the Confirmation's consistency score counts keywords. An examiner will ask whether keyword hits measure
school-specific *reasoning*. The judge scores fidelity, purity, coherence and plausibility on 1-5 scales; two
human raters score a blinded sample so the judge itself is validated (QWK between humans, Spearman judge-human).

  mosaic judge --exp exp01 --split dev --limit 5          pilot (agent allowed)
  mosaic judge --exp exp01 --split test                   human only, after the final runs
  mosaic judge-report --exp exp01 --split test            paired comparisons A/B/C per school and dimension
  mosaic judge-export --exp exp01 --split test            blinded CSV for the human raters (+ key file)
  mosaic judge-agree --exp exp01 --ratings a.csv,b.csv    rater agreement and judge validity

Blinding: the judge sees the school, its definition, the task and the answer; never the arm or the model.
Arm D is excluded because the judge is the same model as arm D.
"""

from __future__ import annotations

import csv
import json
import random
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from mosaic import SCHOOLS
from mosaic import run as runmod
from mosaic.backends import Cache, ClaudeCLIBackend, FakeBackend, Request
from mosaic.config import ROOT, load_toml
from mosaic.data import read_jsonl, write_jsonl
from mosaic.report import latest_runs
from mosaic.stats import holm, paired

DIMS = ("fidelity", "purity", "coherence", "plausibility")
CONFIG = "configs/judge.toml"


def load_config() -> dict:
    return load_toml(ROOT / CONFIG)


def messages(cfg: dict, school: str, task: str, answer: str) -> list[dict]:
    user = cfg["rubric"]["user"].format(school=school.capitalize(), definition=cfg["schools"][school],
                                        task=task, answer=answer)
    return [{"role": "system", "content": cfg["rubric"]["system"]}, {"role": "user", "content": user}]


def parse_judgment(text: str) -> dict | None:
    """First JSON object in the text with all four dimensions as integers 1-5; None otherwise."""
    for m in re.finditer(r"\{.*?\}", text or "", re.S):
        try:
            obj = json.loads(m.group(0))
        except json.JSONDecodeError:
            continue
        try:
            scores = {d: int(obj[d]) for d in DIMS}
        except (KeyError, TypeError, ValueError):
            continue
        if all(1 <= v <= 5 for v in scores.values()):
            return {**scores, "rationale": str(obj.get("rationale", ""))[:400]}
    return None


def select_events(event_ids: list[str], difficulty: dict[str, str], n: int, seed: int) -> list[str]:
    """Stratified by difficulty, proportional, fixed by seed."""
    if n >= len(event_ids):
        return sorted(event_ids)
    rng = random.Random(seed)
    strata = defaultdict(list)
    for e in sorted(event_ids):
        strata[difficulty.get(e, "")].append(e)
    chosen = []
    for _, ids in sorted(strata.items()):
        k = max(1, round(n * len(ids) / len(event_ids)))
        chosen += rng.sample(ids, min(k, len(ids)))
    return sorted(chosen)[:n] if len(chosen) > n else sorted(chosen)


def collect_items(exp: str, split: str, arms: list[str]) -> list[dict]:
    """One item per (arm, event, school) from the latest run of each arm on the split."""
    runs = latest_runs(exp, split)
    items = []
    for arm in arms:
        if arm not in runs:
            raise SystemExit(f"no {split} run for arm {arm}")
        scores = {(r["event_id"], r["school"]): r for r in read_jsonl(runmod.RUNS_DIR / runs[arm] / "scores.jsonl")}
        for g in read_jsonl(runmod.RUNS_DIR / runs[arm] / "generations.jsonl"):
            task = g["messages"][-1]["content"]
            items.append({"arm": arm, "run_id": runs[arm], "event_id": g["event_id"], "school": g["school"],
                          "task": task, "answer": g["text"],
                          "difficulty": scores.get((g["event_id"], g["school"]), {}).get("difficulty", "")})
    return items


def judge(exp: str, split: str, *, limit: int | None = None, backend: str | None = None) -> Path:
    cfg = load_config()
    jc = cfg["judge"]
    items = collect_items(exp, split, jc["arms"])
    diff = {i["event_id"]: i["difficulty"] for i in items}
    events = select_events(sorted(diff), diff, jc["n_events"], jc["seed"])
    if limit:
        events = events[:limit]
    items = [i for i in items if i["event_id"] in set(events)]
    rng = random.Random(jc["seed"])
    rng.shuffle(items)  # arms interleaved: no ordering cue
    cache = Cache(runmod.CACHE_PATH)

    def make(sampling):
        if backend == "fake":
            return _FakeJudge(sampling, cache)
        return ClaudeCLIBackend(sampling, cache, model=jc["model"], effort=jc.get("effort"))

    main_be, repeat_be = make({"judge": 1}), make({"judge": 1, "repeat": 1})
    reqs = [Request(messages(cfg, i["school"], i["task"], i["answer"]), tag=f"judge|{i['event_id']}|{i['school']}")
            for i in items]
    out = main_be.generate(reqs)
    n_rep = int(round(len(items) * jc.get("repeat_fraction", 0)))
    rep_idx = sorted(random.Random(jc["seed"] + 1).sample(range(len(items)), n_rep)) if n_rep else []
    rep = dict(zip(rep_idx, repeat_be.generate([reqs[k] for k in rep_idx]))) if rep_idx else {}

    rows = []
    for k, (i, g) in enumerate(zip(items, out)):
        j = parse_judgment(g["text"])
        row = {"arm": i["arm"], "event_id": i["event_id"], "school": i["school"], "difficulty": i["difficulty"],
               "source_run": i["run_id"], "parsed": j is not None, **(j or {})}
        if k in rep:
            jr = parse_judgment(rep[k]["text"])
            row["repeat"] = {d: jr[d] for d in DIMS} if jr else None
        rows.append(row)
    utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = runmod.RUNS_DIR / f"{exp}-judge-{split}-{utc}"
    out_dir.mkdir(parents=True)
    write_jsonl(out_dir / "judgments.jsonl", rows)
    meta = {"exp": exp, "split": split, "events": events, "n_items": len(rows), "model": jc["model"],
            "parsed_rate": float(np.mean([r["parsed"] for r in rows])) if rows else 0.0, "repeats": len(rep_idx)}
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta))
    return out_dir


class _FakeJudge(FakeBackend):
    model_id = "fake-judge"

    def _generate(self, reqs):
        out = []
        for r in reqs:
            answer = r.messages[1]["content"].split("Analyst's answer:")[-1].lower()
            leak = "aggregate demand" in answer and "keynesian" not in r.messages[1]["content"].lower()[:60]
            s = 2 if leak else 4
            out.append({"text": json.dumps({"fidelity": s, "purity": s, "coherence": 3, "plausibility": 3,
                                            "rationale": "fake"}), "usage": {}, "seconds": 0.0})
        return out


def latest_judge_dir(exp: str, split: str) -> Path:
    dirs = sorted(runmod.RUNS_DIR.glob(f"{exp}-judge-{split}-*"))
    if not dirs:
        raise SystemExit(f"no judge run for {exp} on {split}")
    return dirs[-1]


def judge_report(exp: str, split: str, out_dir: Path | None = None) -> str:
    d = latest_judge_dir(exp, split)
    rows = [r for r in read_jsonl(d / "judgments.jsonl") if r["parsed"]]
    by = {(r["arm"], r["event_id"], r["school"]): r for r in rows}
    comparisons = [("A", "B"), ("A", "C"), ("B", "C")]
    res, keys, ps = {}, [], []
    for base, arm in comparisons:
        for dim in DIMS:
            for s in SCHOOLS:
                ev = sorted({e for (a, e, sc) in by if sc == s and a == base} &
                            {e for (a, e, sc) in by if sc == s and a == arm})
                r = paired([by[(base, e, s)][dim] for e in ev], [by[(arm, e, s)][dim] for e in ev], seed=0)
                res[(base, arm, dim, s)] = r
                if r.get("n"):
                    keys.append((base, arm, dim, s))
                    ps.append(r["p"])
    for k, p in zip(keys, holm(ps)):
        res[k]["p_holm"] = p
    reps = [r for r in read_jsonl(d / "judgments.jsonl") if r.get("repeat") and r["parsed"]]
    lines = [f"# {exp} judge scores on {split} (secondary outcome; judge = {d.name})", "",
             f"Items parsed: {len(rows)}. Holm correction over all {len(ps)} judge comparisons. "
             "Arm D excluded (same model as the judge).", ""]
    if reps:
        lines.append("Test-retest (same item judged twice): " + ", ".join(
            f"{dim} ρ = {spearman([r[dim] for r in reps], [r['repeat'][dim] for r in reps]):.2f}" for dim in DIMS)
            + f" (n = {len(reps)})")
        lines.append("")
    for base, arm in comparisons:
        lines += [f"## {arm} vs {base}", "", "| dimension | school | mean base → arm | diff [95% CI] | p (Holm) |",
                  "|---|---|---|---|---|"]
        for dim in DIMS:
            for s in SCHOOLS:
                r = res[(base, arm, dim, s)]
                if r.get("n"):
                    lines.append(f"| {dim} | {s} | {r['mean_a']:.2f} → {r['mean_b']:.2f} | {r['diff']:+.2f} "
                                 f"[{r['ci_lo']:+.2f}, {r['ci_hi']:+.2f}] | {r.get('p_holm', r['p']):.4f} |")
        lines.append("")
    text = "\n".join(lines)
    out = (out_dir or ROOT / "reports") / f"{exp}_judge_{split}_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return text


# --- human validation ---------------------------------------------------------------------------------------------

def judge_export(exp: str, split: str, out_dir: Path | None = None) -> tuple[Path, Path]:
    """Blinded rating sheet (no arm, no model) + a separate key file; stratified by arm x school."""
    cfg = load_config()
    jc = cfg["judge"]
    d = latest_judge_dir(exp, split)
    judged = [r for r in read_jsonl(d / "judgments.jsonl") if r["parsed"]]
    items = {(i["arm"], i["event_id"], i["school"]): i for i in collect_items(exp, split, jc["arms"])}
    rng = random.Random(jc["seed"] + 2)
    cells = defaultdict(list)
    for r in judged:
        cells[(r["arm"], r["school"])].append(r)
    per = max(1, jc["human_sample"] // max(1, len(cells)))
    chosen = []
    for _, rs in sorted(cells.items()):
        chosen += rng.sample(rs, min(per, len(rs)))
    rng.shuffle(chosen)
    out_dir = out_dir or ROOT / "reports"
    out_dir.mkdir(exist_ok=True)
    sheet, key = out_dir / f"{exp}_human_rating_sheet.csv", out_dir / f"{exp}_human_rating_key.json"
    with open(sheet, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["item", "school", "definition", "task", "answer", *DIMS])
        for n, r in enumerate(chosen, 1):
            it = items[(r["arm"], r["event_id"], r["school"])]
            w.writerow([f"H{n:03d}", r["school"], cfg["schools"][r["school"]], it["task"], it["answer"],
                        "", "", "", ""])
    key.write_text(json.dumps({f"H{n:03d}": {"arm": r["arm"], "event_id": r["event_id"], "school": r["school"],
                                              **{dim: r[dim] for dim in DIMS}}
                               for n, r in enumerate(chosen, 1)}, indent=1))
    print(f"rating sheet: {sheet}\nkey (do not show raters): {key}")
    return sheet, key


def rankdata(x) -> np.ndarray:
    x = np.asarray(x, float)
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x))
    ranks[order] = np.arange(1, len(x) + 1)
    for v in np.unique(x):  # average ranks for ties
        m = x == v
        ranks[m] = ranks[m].mean()
    return ranks


def spearman(a, b) -> float:
    if len(a) < 3:
        return float("nan")
    ra, rb = rankdata(a), rankdata(b)
    if ra.std() == 0 or rb.std() == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def qwk(a, b, k: int = 5) -> float:
    """Quadratic-weighted Cohen's kappa for ratings on 1..k."""
    a, b = np.asarray(a, int) - 1, np.asarray(b, int) - 1
    o = np.zeros((k, k))
    for i, j in zip(a, b):
        o[i, j] += 1
    w = np.array([[(i - j) ** 2 / (k - 1) ** 2 for j in range(k)] for i in range(k)])
    e = np.outer(o.sum(1), o.sum(0)) / o.sum()
    den = (w * e).sum()
    return float(1 - (w * o).sum() / den) if den else float("nan")


def read_ratings(path: str) -> dict[str, dict[str, int]]:
    out = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                out[r["item"]] = {d: int(r[d]) for d in DIMS}
            except (KeyError, ValueError):
                continue  # unrated row
    return out


def judge_agree(exp: str, rating_files: list[str], key_file: str | None = None) -> dict:
    key = json.loads(Path(key_file or ROOT / "reports" / f"{exp}_human_rating_key.json").read_text())
    raters = [read_ratings(p) for p in rating_files]
    common = sorted(set(key).intersection(*[set(r) for r in raters]))
    res = {"n_items": len(common)}
    for d in DIMS:
        h = np.array([[r[i][d] for i in common] for r in raters], float)
        res[f"{d}_qwk_raters"] = round(qwk(h[0], h[1]), 3) if len(raters) >= 2 and common else None
        res[f"{d}_spearman_judge_vs_humans"] = round(spearman(h.mean(0), [key[i][d] for i in common]), 3) \
            if common else None
    print(json.dumps(res, indent=1))
    return res
