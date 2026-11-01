# Plan: multi-objective evolution of competing LLM agents' prompts

Target: everything submitted within **10 hours** of starting (deadline treated as 2026-11-02 until the TA says
otherwise). Order of priority: meet every requirement in `README.md` §2 first, polish second.

## 1. Research problem

Multi-agent LLM systems that pool several "perspectives" (personas, schools of thought) depend on the agents
being both **faithful** to their perspective and **different** from each other. Prompt-optimisation work
(EvoPrompt, Promptbreeder, OPRO) tunes one prompt for one score; nobody evolves a *set* of competing agents where
fidelity, mutual diversity and cost trade off. Our own measurements (`research/divergence/RESULTS.md`) show the
failure mode: hand-written prompts let some perspectives collapse onto each other (New Keynesian ≈ Keynesian).

**RQ.** Can a multi-objective evolutionary algorithm with LLM-guided variation find prompt sets for three
competing economic-school agents that dominate hand-written prompts and single-objective / random search on
fidelity, inter-agent disagreement and prompt length — and do the gains hold on unseen events?

## 2. Method (the innovation is in §2.2–2.4)

**2.1 Representation.** An individual = one prompt *set* (all three schools at once). Per school the genome is
structured: `diagnosis` (text), `concepts` (subset/ordering of a concept pool), `stance` (text), `contrast`
(optional one-line "unlike school X, you…" text). Decoded with the reused `messages()` layout.

**2.2 Objectives (minimise all, NSGA-II).**
1. f1 = −mean school fidelity: lexicon consistency (must/strong hits − anti hits, normalised) on the search events.
2. f2 = −mean pairwise disagreement among the three schools (`divergence.distance`, signal disagreement).
3. f3 = total prompt length (tokens).
Constraint: format validity ≥ 90 % (parse success); infeasible individuals ranked behind feasible (Deb's rule).

**2.3 Variation operators.**
- *Structural crossover*: swap whole school blocks or fields between two parent sets (uniform crossover on fields).
- *LLM-guided mutation* (AI → EC): the LLM rewrites one field given the objective it should improve and the
  individual's weakest score ("make the Austrian diagnosis more distinct from the Monetarist one").
- *Concept-set mutation*: add/drop/reorder concepts (cheap, no LLM).
**2.4 Diversity-aware selection.** Standard NSGA-II crowding distance (Ch. 4 / Tutorial 5) on the three
objectives; ablation without LLM mutation.

## 3. Experimental design

| Item | Setting |
|---|---|
| Model | Qwen3-8B via vLLM on one RunPod GPU (fallback: an OpenAI-compatible API, e.g. qwen3.8-max, with a USD cap) |
| Events | search set: 10 synthetic events, `make_items(..., seed=23)`; held-out set: 20 events, seed 29 |
| Budget per run | population 12 prompt sets × 8 generations ≈ 100 evaluations × 3 schools × 10 events ≈ 3,000 generations |
| Seeds | 5 independent runs per method |
| Methods (baselines) | B0 hand-written prompts (`profiles()`, no search) · B1 random search (same evaluation budget) · B2 single-objective GA (weighted sum of f1–f3, Ch. 2 GA) · **Ours: NSGA-II + LLM mutation** · ablation: NSGA-II with rule-based mutation only |
| Metrics | hypervolume of the final front (normalised objectives, fixed reference point), best fidelity, best disagreement, validity rate, prompt length; all re-measured on the **held-out** events for the selected knee solution |
| Statistics | mean ± std over 5 seeds; paired bootstrap / permutation (`mosaic.stats`) Ours vs each baseline, Holm-corrected |
| Figures | Pareto fronts (f1 vs f2, length as colour), hypervolume vs generation, held-out bar chart |

Compute estimate: Qwen3-8B on vLLM ≈ 1,500–2,500 short generations/min batched → whole matrix ≈ 2–3 GPU-hours
on one 48–80 GB card. Every call goes through the on-disk cache, so a crash loses nothing.

## 4. 10-hour schedule

| Hour | Work | Output |
|---|---|---|
| 0–0.5 | Email TA about the deadline; human confirms GPU class + hour limit; start pod (setup takes ~20 min) | pod running |
| 0.5–3 | Write `code/evo_prompt/` (genome, operators, NSGA-II, baselines, runner, hypervolume) + offline tests with `FakeBackend` | tests green |
| 3–6 | Run the experiment matrix on the pod (smoke run first: 1 seed, 2 generations); in parallel: literature review (20 papers, 2024–26) | `results/*.jsonl`, `results/summary.csv` |
| 6–7.5 | Analysis: tables, stats, figures; stop the pod | `results/figures/` |
| 7.5–9.5 | Report (human writes prose from the agent's outline and numbers), README for code, references | `report/report.pdf` |
| 9.5–10 | Final checklist (`README.md` §2), zip, email; 6-minute slide outline | submitted |

## 5. Deliverable map

| Requirement | File |
|---|---|
| Report PDF | `report/report.pdf` (source `report/report.md`) |
| Source code + README | `code/` + `code/README.md` |
| Experimental data and results | `results/` (raw JSONL, logs, `summary.csv`) |
| Supplementary | best prompts per method (`results/best_prompts/`), figures, configs |

## 6. Decisions the human must make before GPU spending

1. GPU class and hour limit (suggest: one 48 GB card, ≤ 4 h).
2. RunPod key set as an environment secret (never in chat); or choose the API fallback and a USD cap.
3. Whether the deadline is 11/2 or 11/15 (scales the number of seeds/generations, not the design).
