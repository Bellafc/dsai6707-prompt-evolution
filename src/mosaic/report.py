"""Compare arms on one split: paired tests per school, Holm correction over the pre-registered primary family.

  mosaic report --exp exp01 --split dev      latest dev run of each arm (exploratory)
  mosaic report --exp exp01 --split test     the final runs (confirmatory; the numbers that go in the thesis)
"""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime, timezone

from mosaic import SCHOOLS
from mosaic.config import ROOT, load_toml
from mosaic.data import read_jsonl
from mosaic import run as runmod
from mosaic.stats import holm, paired

METRICS = [("consistency", "consistency C_s (higher = more school-specific)"),
           ("anti_hits", "contamination: anti-signal hits (lower = purer)"),
           ("completeness", "structural completeness (7 elements)")]


def latest_runs(exp: str, split: str) -> dict[str, str]:
    if not runmod.RESULTS.exists():
        raise SystemExit("no runs yet: experiments/results.tsv does not exist")
    with open(runmod.RESULTS, encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f, delimiter="\t") if r["exp"] == exp and r["split"] == split
                and (r["status"] == "final" if split == "test" else True)]
    latest = {}
    for r in rows:  # file order = time order
        latest[r["arm"]] = r["run_id"]
    return latest


def load_scores(run_id: str) -> dict[tuple[str, str], dict]:
    return {(r["event_id"], r["school"]): r for r in read_jsonl(runmod.RUNS_DIR / run_id / "scores.jsonl")}


def _fmt(r: dict) -> str:
    if not r.get("n"):
        return "| – | – | – | – | – |"
    return (f"| {r['mean_a']:.3f} → {r['mean_b']:.3f} | {r['diff']:+.3f} [{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}] "
            f"| {r['p']:.4f} | {f"{r['p_holm']:.4f}" if 'p_holm' in r else '–'} | {r['win_rate']:.0%} |")


def report(exp: str, split: str, out_dir=None) -> str:
    cfg = load_toml(ROOT / f"configs/{exp}.toml")
    runs = latest_runs(exp, split)
    scores = {a: load_scores(r) for a, r in runs.items()}
    comparisons = [tuple(c.split(">")) for c in cfg["report"]["comparisons"]]  # "A>C" means C vs baseline A
    primary = {tuple(c.split(">")) for c in cfg["report"]["primary"]}
    results = defaultdict(dict)
    prim_keys, prim_ps = [], []
    for base, arm in comparisons:
        if base not in scores or arm not in scores:
            continue
        for metric, _ in METRICS:
            for s in SCHOOLS:
                keys = sorted(k for k in scores[base] if k[1] == s and k in scores[arm])
                a = [float(scores[base][k][metric]) for k in keys]
                b = [float(scores[arm][k][metric]) for k in keys]
                r = paired(a, b, seed=0)
                results[(base, arm, metric)][s] = r
                if (base, arm) in primary and metric == cfg["report"]["primary_metric"] and r.get("n"):
                    prim_keys.append((base, arm, metric, s))
                    prim_ps.append(r["p"])
        ev_a = {k[0]: v["diversity"] for k, v in scores[base].items() if v.get("diversity") is not None}
        ev_b = {k[0]: v["diversity"] for k, v in scores[arm].items() if v.get("diversity") is not None}
        common = sorted(set(ev_a) & set(ev_b))
        results[(base, arm, "diversity")]["all"] = paired([ev_a[e] for e in common], [ev_b[e] for e in common])
    for k, p in zip(prim_keys, holm(prim_ps)):
        results[k[:3]][k[3]]["p_holm"] = p

    when = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    kind = "CONFIRMATORY (frozen, final runs)" if split == "test" else "EXPLORATORY (dev split; not thesis evidence)"
    lines = [f"# {exp} on {split}: {kind}", "", f"Generated {when}. Runs: " +
             ", ".join(f"{a} = `{r}`" for a, r in sorted(runs.items())), "",
             f"Primary family (Holm-corrected): {', '.join(cfg['report']['primary'])} on "
             f"`{cfg['report']['primary_metric']}`, one test per school. Other p-values are unadjusted.", ""]
    for base, arm in comparisons:
        if (base, arm, "consistency") not in results:
            continue
        lines += [f"## {arm} vs {base}", ""]
        for metric, label in METRICS:
            lines += [f"**{label}**", "", "| school | mean base → arm | diff [95% CI] | p | p (Holm) | arm wins |",
                      "|---|---|---|---|---|---|"]
            for s in SCHOOLS:
                lines.append(f"| {s} " + _fmt(results[(base, arm, metric)].get(s, {})))
            lines.append("")
        d = results[(base, arm, "diversity")].get("all", {})
        lines += ["**inter-school diversity (Jaccard distance, per event)**", "",
                  "| | mean base → arm | diff [95% CI] | p | p (Holm) | arm wins |", "|---|---|---|---|---|---|",
                  "| all events " + _fmt(d), ""]
    text = "\n".join(lines)
    out = (out_dir or ROOT / "reports") / f"{exp}_{split}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(text + "\n", encoding="utf-8")
    print(text)
    print(f"\nwritten to {out}")
    return text
