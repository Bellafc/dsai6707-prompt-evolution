# 6-minute presentation outline

Target: 6 minutes, 8 to 9 slides, about 40 seconds each. Numbers are from `results/summary_table.md`.

| # | Time | Slide | Key message | Speaker note |
|---|---|---|---|---|
| 1 | 0:00–0:30 | Title and question | Can an EA search a *set* of competing agent prompts, with an LLM as mutation operator? | State the RQ in one sentence. |
| 2 | 0:30–1:15 | Why it matters | Multi-agent LLM ensembles collapse: agents must stay faithful *and* distinct; prompts are set by hand. | Cite the collapse evidence (debate and homogeneity studies). |
| 3 | 1:15–2:00 | Literature gap | LLM-as-operator and Pareto prompt search exist; none searches a *set* with a between-agent distinctness objective and a held-out check. | Show the positioning table (report Table 1). |
| 4 | 2:00–2:50 | Method | Genome = three school genes; objectives fidelity, disagreement, length; NSGA-II with LLM-guided mutation that targets the parent's weakest objective. | One diagram: genome → decode → three school calls → three objectives. |
| 5 | 2:50–3:30 | Setup | Synthetic events (search seed 23, held-out seed 29); population 6, 4 generations, 3 seeds; 2,743 calls, about USD 20 estimated. | Say plainly that the budget is small. |
| 6 | 3:30–4:20 | Search results | LLM mutation lifts hypervolume from 0.098 (random, rule-only NSGA-II) to 0.121 (NSGA-II) and 0.122 (GA). Selection scheme makes no visible difference. | Figure 1 (hypervolume per generation). Note: 3 seeds, descriptive. |
| 7 | 4:20–5:10 | Held-out results | Knees are 20–30% shorter than B0 (305–350 vs 438 words) with similar fidelity and disagreement; no difference survives Holm correction. | Figure 3. Be explicit: random search also gains fidelity. |
| 8 | 5:10–5:45 | Limitations and next step | 3 seeds, small budget, API model not Qwen3-8B, PROVISIONAL lexicon (Goodhart risk), assumed prices. Next: larger budget, judge-based fidelity, fixed-call control. | Own the limitations. |
| 9 | 5:45–6:00 | Conclusion | LLM-guided mutation is a useful operator for prompt-set search; a better-than-hand-written claim is not yet supported. | End on the RQ answers. |

## Backup slides (not shown unless asked)

- Pareto fronts (`results/figures/pareto_fronts.png`).
- Ablation definition and fallback rate (8 of 30 and 10 of 34 LLM children rejected and replaced by rule mutation).
- Protocol: pre-registered knee rule and tests (`code/PROTOCOL.md`).
- Cost: estimated spend USD 20.20 at assumed prices; token totals in `results/logs/matrix.log`.
