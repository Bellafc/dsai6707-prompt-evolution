# 6-minute presentation outline

Target: 6 minutes, 8 to 9 slides, about 40 seconds each. Numbers are from `results/summary_table.md`.

| # | Time | Slide | Key message | Speaker note |
|---|---|---|---|---|
| 1 | 0:00–0:30 | Title and question | Can an EA search a *set* of competing agent prompts, with an LLM as mutation operator? | State the RQ in one sentence. |
| 2 | 0:30–1:15 | Why it matters | Multi-agent LLM ensembles collapse: agents must stay faithful *and* distinct; prompts are set by hand. | Cite the collapse evidence (debate and homogeneity studies). |
| 3 | 1:15–2:00 | Literature gap | LLM-as-operator and Pareto prompt search exist; none searches a *set* with a between-agent distinctness objective and a held-out check. | Show the positioning table (report Table 1). |
| 4 | 2:00–2:50 | Method | Genome = three school genes; objectives fidelity, disagreement, length; NSGA-II with LLM-guided mutation that targets the parent's weakest objective. | One diagram: genome → decode → three school calls → three objectives. |
| 5 | 2:50–3:30 | Setup | Synthetic events (search seed 23, held-out seed 29); population 6, 4 generations; qwen 3 seeds, Claude Haiku 5.5 5 seeds; ablations, unguided control, EvoPrompt-GA; 13,121 calls, about USD 33. | Say plainly that the budget is small; protocols committed before runs. |
| 6 | 3:30–4:20 | Search results | qwen 2 x 2 table: selection does not matter; guided LLM mutation 0.12 vs 0.10 for rule mutation *and* for unguided LLM rewriting, in every seed: the guidance carries the gain. Haiku: same direction in 4 of 5 seeds; beats EvoPrompt-GA (verbatim fails, length-bounded variant 5/5, p = 0.031). | Table 2b and Q1–Q5. Note: descriptive on 3 seeds. |
| 7 | 4:20–5:10 | Held-out results | Knees are 20–30% shorter than B0 (305–356 vs 438 words) with similar fidelity and disagreement; on neither model does any difference survive Holm correction. | Figure 3. Be explicit: random search also gains fidelity. |
| 8 | 5:10–5:45 | Limitations and next step | Small budget, 3 seeds on qwen, length rule tuned to qwen (half of Haiku edits rejected), PROVISIONAL lexicon (Goodhart risk), qwen EvoPrompt incomplete, addendum D post hoc. Next: relative length rule, judge-based fidelity, more generations. | Own the limitations. |
| 9 | 5:45–6:00 | Conclusion | Objective-guided LLM mutation, not LLM rewriting as such, is the useful ingredient; a better-than-hand-written claim on unseen events is not supported. | End on the RQ answers. |

## Backup slides (not shown unless asked)

- Pareto fronts (`results/figures/pareto_fronts.png`).
- Ablation definition and fallback rate (8 of 30 and 10 of 34 LLM children rejected and replaced by rule mutation).
- Protocol: knee rule and tests fixed in `code/PROTOCOL.md` before the held-out analysis (deviations in report §4.8).
- Cost: qwen about USD 27.31 at assumed prices, Haiku USD 5.28 at list prices; token totals in the caches.
- EvoPrompt failure mode: children 668–1,132 words, 3 of 120 feasible; length-bounded variant 396–608 words, 60 of 120 feasible.
