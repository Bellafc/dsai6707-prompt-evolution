"""Figures for the report: hypervolume vs generation, Pareto fronts (search archive), held-out bars with per-event points.
Reads results/runs and results/heldout_per_event.csv written by evo_prompt.analyze. No model calls.
"""

from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .config import RESULTS_DIR  # noqa: E402

METHODS = ["nsga2", "ga", "random", "nsga2_rule", "ga_rule", "nsga2_llmu", "evoprompt_ga", "evoprompt_ga_lc"]
LABEL = {"nsga2": "NSGA-II + LLM", "ga": "GA (weighted sum)", "random": "Random search",
         "nsga2_rule": "NSGA-II, rule only", "ga_rule": "GA, rule only", "nsga2_llmu": "NSGA-II + unguided LLM",
         "evoprompt_ga": "EvoPrompt (GA)",
         "evoprompt_ga_lc": "EvoPrompt (GA), length-bounded", "b0": "B0 hand-written"}
COLOR = {"nsga2": "#1b6ca8", "ga": "#2e8b57", "random": "#999999", "nsga2_rule": "#c0504d", "ga_rule": "#e69f00",
         "nsga2_llmu": "#7b5ea7", "evoprompt_ga": "#8c564b", "evoprompt_ga_lc": "#d17a5b", "b0": "#444444"}
SEEDS = [1, 2, 3]


def hv_curves(results: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for m in METHODS:
        series = []
        for s in SEEDS:
            p = results / "runs" / f"{m}_s{s}" / "gen_log.csv"
            if p.exists():
                rows = list(csv.DictReader(p.open()))
                series.append([float(r["hv"]) for r in rows])
        if not series:
            continue
        n = min(len(x) for x in series)
        gens = list(range(n))
        mean = [statistics.mean(x[g] for x in series) for g in gens]
        sd = [statistics.stdev(x[g] for x in series) if len(series) > 1 else 0 for g in gens]
        ax.plot(gens, mean, marker="o", color=COLOR[m], label=LABEL[m])
        ax.fill_between(gens, [a - b for a, b in zip(mean, sd)], [a + b for a, b in zip(mean, sd)],
                        color=COLOR[m], alpha=0.12)
    ax.set_xlabel("generation (population 6; 0 = initial population)")
    ax.set_ylabel("hypervolume of feasible archive")
    ax.set_title(f"Hypervolume vs generation (mean ± sd, {len(SEEDS)} seeds)")
    ax.set_xticks(range(5))
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    (results / "figures").mkdir(parents=True, exist_ok=True)
    fig.savefig(results / "figures" / "hv_vs_generation.png", dpi=160)
    plt.close(fig)


def pareto(results: Path) -> None:
    methods = [m for m in ["nsga2", "nsga2_llmu", "nsga2_rule", "evoprompt_ga", "ga", "ga_rule", "random", "evoprompt_ga_lc"]
               if all((results / "runs" / f"{m}_s{s}" / "front.jsonl").exists() for s in SEEDS)]
    data = {}
    for m in methods:
        xs, ys, cs = [], [], []
        for s in SEEDS:
            p = results / "runs" / f"{m}_s{s}" / "front.jsonl"
            for line in p.read_text().splitlines():
                r = json.loads(line)
                xs.append(r["fidelity"])
                ys.append(r["disagreement"])
                cs.append(r["words"])
        data[m] = (xs, ys, cs)
    allc = [c for _, _, cs in data.values() for c in cs]
    ncol = 4 if len(methods) > 6 else 3 if len(methods) > 4 else 2
    fig, axes = plt.subplots(2, ncol, figsize=(5 * ncol, 7.6), sharex=True, sharey=True, squeeze=False)
    for ax, m in zip(axes.flat, methods):
        xs, ys, cs = data[m]
        sc = ax.scatter(xs, ys, c=cs, cmap="viridis", vmin=min(allc), vmax=max(allc), s=36, edgecolor="k",
                        linewidth=0.3)
        ax.set_title(f"{LABEL[m]}: final archive, {len(SEEDS)} seeds", fontsize=9)
        ax.grid(alpha=0.3)
    for ax in list(axes.flat)[len(methods):]:
        ax.set_visible(False)
    for ax in axes[1]:
        ax.set_xlabel("school fidelity (search events)")
    for ax in axes[:, 0]:
        ax.set_ylabel("signal disagreement (search events)")
    fig.colorbar(sc, ax=axes, label="prompt set words")
    fig.savefig(results / "figures" / "pareto_fronts.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def heldout(results: Path) -> None:
    per = {}
    with (results / "heldout_per_event.csv").open() as fh:
        for r in csv.DictReader(fh):
            per.setdefault(r["method"], []).append(r)
    order = ["b0"] + METHODS
    order = [m for m in order if m in per]
    fig, axes = plt.subplots(1, 2, figsize=(1.6 * len(order) + 2, 4.4))
    for ax, metric in zip(axes, ["fidelity", "disagreement"]):
        means, errs = [], []
        for i, m in enumerate(order):
            vals = [float(r[metric]) for r in per[m]]
            means.append(statistics.mean(vals))
            errs.append(statistics.stdev(vals) / len(vals) ** 0.5)  # standard error over the 10 events
            ax.scatter([i] * len(vals), vals, s=10, color="k", alpha=0.35, zorder=3)
        ax.bar(range(len(order)), means, yerr=errs, color=[COLOR[m] for m in order], alpha=0.8, capsize=4)
        ax.set_xticks(range(len(order)))
        ax.set_xticklabels([LABEL[m].replace(" + ", "\n+ ").replace(" (", "\n(") for m in order], fontsize=7)
        ax.set_title(f"Held-out {metric} (seed 29, 10 events)")
        ax.grid(axis="y", alpha=0.3)
    axes[0].set_ylabel("mean over events (bar), ± standard error; dots = events")
    fig.tight_layout()
    fig.savefig(results / "figures" / "heldout_bars.png", dpi=160)
    plt.close(fig)


def main(results: Path = RESULTS_DIR) -> None:
    global SEEDS, METHODS
    SEEDS = sorted(int(p.name.rsplit("_s", 1)[1]) for p in (results / "runs").glob("b0_s*")) or SEEDS
    METHODS = [m for m in METHODS if all((results / "runs" / f"{m}_s{s}" / "final.json").exists() for s in SEEDS)]
    (results / "figures").mkdir(parents=True, exist_ok=True)
    hv_curves(results)
    pareto(results)
    heldout(results)
    print("figures written to", results / "figures")


if __name__ == "__main__":
    import sys

    from .config import HAIKU

    main(HAIKU["results"] if "--profile" in sys.argv and "haiku" in sys.argv else RESULTS_DIR)
