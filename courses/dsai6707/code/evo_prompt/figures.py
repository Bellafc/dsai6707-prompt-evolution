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

METHODS = ["nsga2", "ga", "random", "nsga2_rule"]
LABEL = {"nsga2": "NSGA-II + LLM", "ga": "GA (weighted sum)", "random": "Random search",
         "nsga2_rule": "NSGA-II, rule only", "b0": "B0 hand-written"}
COLOR = {"nsga2": "#1b6ca8", "ga": "#2e8b57", "random": "#999999", "nsga2_rule": "#c0504d", "b0": "#444444"}
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
    ax.set_title("Hypervolume vs generation (mean ± sd, 3 seeds)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    (results / "figures").mkdir(parents=True, exist_ok=True)
    fig.savefig(results / "figures" / "hv_vs_generation.png", dpi=160)
    plt.close(fig)


def pareto(results: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
    for ax, m in zip(axes, ["nsga2", "ga"]):
        xs, ys, cs = [], [], []
        for s in SEEDS:
            p = results / "runs" / f"{m}_s{s}" / "front.jsonl"
            for line in p.read_text().splitlines():
                r = json.loads(line)
                xs.append(r["fidelity"])
                ys.append(r["disagreement"])
                cs.append(r["words"])
        sc = ax.scatter(xs, ys, c=cs, cmap="viridis", s=36, edgecolor="k", linewidth=0.3)
        ax.set_title(f"{LABEL[m]}: final archive, 3 seeds")
        ax.set_xlabel("school fidelity (search events)")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("signal disagreement (search events)")
    fig.colorbar(sc, ax=axes, label="prompt set words")
    fig.savefig(results / "figures" / "pareto_fronts.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def heldout(results: Path) -> None:
    per = {}
    with (results / "heldout_per_event.csv").open() as fh:
        for r in csv.DictReader(fh):
            per.setdefault(r["method"], []).append(r)
    order = ["b0"] + METHODS
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
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
    (results / "figures").mkdir(parents=True, exist_ok=True)
    hv_curves(results)
    pareto(results)
    heldout(results)
    print("figures written to", results / "figures")


if __name__ == "__main__":
    main()
