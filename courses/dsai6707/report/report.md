---
title: "Evolving a Set of Competing Economic-School Prompts: NSGA-II with LLM-Guided Mutation"
author: "[Student name], DSAI6707 Advanced Computational Intelligence, PolyU"
date: "November 2026"
bibliography: references.bib
link-citations: true
---

> **Draft status.** Written with AI assistance (see Appendix A). Every number below is traceable to a file in `results/`; the student reviews and edits the prose before submission.

# Abstract

Multi-perspective LLM agents are useful only if each agent stays faithful to its perspective and the agents differ from one another. Prompt-optimisation work usually tunes one prompt against one score, so the trade-off between fidelity, mutual distinctness and prompt length is not searched directly. We cast the design of three economic-school agents (Keynesian, Austrian, Monetarist) as a constrained multi-objective problem over a *set* of prompts and search it with NSGA-II, using an LLM as a guided mutation operator. Each objective is measured on synthetic macroeconomic events through a disk-cached model backend. In a reduced-budget study (population 6, four generations, three seeds per method, 2,743 model calls, about USD 20 estimated), NSGA-II with LLM-guided mutation and a single-objective weighted-sum GA reach a hypervolume of about 0.12, against about 0.098 for random search and for NSGA-II with rule-based mutation only. On ten held-out events, the selected prompt sets are 20–30% shorter than the hand-written baseline with similar fidelity and disagreement, but no method improves significantly on the baseline after Holm correction, and random search gains almost as much fidelity as the evolutionary methods. We report these results as they are and discuss what the budget can and cannot establish.

**Keywords:** evolutionary prompt optimisation, multi-objective evolutionary algorithms, NSGA-II, LLM-guided mutation, multi-agent diversity, quality-diversity.

# 1 Introduction

## 1.1 Problem and motivation

Systems that combine several LLM agents, each speaking from a different perspective, are increasingly used for analysis, forecasting and debate [@Baltaji2024persona; @Takano2025hawkish]. Their value rests on two properties that pull in opposite directions. Each agent must stay *faithful* to its perspective, and the agents must be *distinct* from one another, or the ensemble collapses into one voice. Recent evidence points to exactly this failure: debate and ensemble systems lose diversity through conformity and majority pressure [@Wu2025debate; @Zhu2026demystifying], and aligned models produce homogeneous outputs across many open-ended queries [@Jiang2025hivemind]. Prompts are the cheapest lever for setting perspective, but they are usually written by hand.

Evolutionary prompt optimisation can search prompts automatically, with an LLM supplying the variation operators [@Fernando2024promptbreeder; @Guo2024evoprompt; @Lange2024large]. These methods, however, optimise one prompt against one scalar score. None of them evolves a *set* of prompts whose members must be good individually and different from each other, and none exposes the trade-off between fidelity, distinctness and cost (prompt length). Multi-objective prompt search has started to appear [@Zhao2025pareto; @Camara2025moprompt], ; we found no such work for multi-agent sets.

The thesis harness from which this project borrows its measurements provides motivating evidence. In a 240-request disagreement matrix over six economic frameworks (synthetic events, seed 11, the same model identifier `qwen3.8-max`), the three trained schools disagreed about twice as much as one school disagreed with itself, while New Keynesian duplicated Keynesian within the noise floor (`research/divergence/RESULTS.md` in the thesis repository, not a bibliography entry). This evidence is used here only as motivation; none of its events or outputs enter the experiments below.

## 1.2 Research questions

- **RQ1.** Can NSGA-II over prompt sets, with LLM-guided mutation, find prompt sets that dominate a hand-written baseline and single-objective or random search in fidelity, inter-agent disagreement and length?
- **RQ2.** Which component carries the effect: the LLM-guided mutation or the selection scheme?
- **RQ3.** Do the gains hold on unseen events?

## 1.3 Contributions

1. **Representation and objectives.** An individual is a set of three school genes (diagnosis, concepts, stance, contrast) decoded through the unchanged thesis prompt scaffold. Objectives are school fidelity, inter-school disagreement and prompt length, with Deb's constraint handling on output validity.
2. **Operators.** Structural crossover at school and field level; rule mutation that touches one school per child; and an LLM-guided mutation in which the parent's weakest objective is turned into a rewrite instruction (AI-to-EC).
3. **Protocol.** A pre-registered analysis protocol (`code/PROTOCOL.md`), held-out events from a separate seed, exact sign-flip tests on held-out events with Holm correction, and a fully cached pipeline that can be re-run offline from the committed raw outputs.

# 2 Related Work

We collected 34 papers from 2024–2026 (`report/references.bib`). On 2026-11-01 every author list and first-submission date was re-checked against its arXiv page. Venue information comes from arXiv comments, the course reference list, or a venue page. The DOIs of the TEVC and CSUR surveys came from search results and must be confirmed on the publisher site before submission (see `AI_USE.md`). They are grouped by theme; the classic Promptbreeder and EvoPrompt papers are included because their venue versions are from 2024. The synthesis below is organised by method, not by paper.

## 2.1 LLMs as evolutionary variation operators

The strongest current trend treats an LLM as the mutation and crossover operator of an evolutionary loop. Promptbreeder evolves task prompts and the mutation prompts themselves [@Fernando2024promptbreeder]; EvoPrompt connects LLM-generated crossover and mutation with GA and DE on discrete prompts [@Guo2024evoprompt]; EvoLLM treats an LLM as an in-context recombination step for evolution strategies [@Lange2024large]. Beyond prompts, LLMs design heuristics and algorithms: EoH co-evolves natural-language thoughts with code [@Liu2024evolution], ReEvo adds reflective, verbal feedback to crossover and mutation [@Ye2024reevo], LLaMEA generates metaheuristics that beat CMA-ES on BBOB [@vanStein2024llamea], and Eureka evolves reward code from simulator feedback [@Ma2024eureka]. Automated design of agentic systems applies the same idea to whole agents, with an archive rather than a selection population [@Hu2025automated]. Surveys place these methods in a common frame, with the LLM as optimiser, predictor, extractor or designer [@Wu2025evolutionary; @Liu2026systematic]. Recent work also adds guidance on which parent and which operator to call, to save model calls [@Wang2026how].

**Gap.** Nearly all of this work optimises a single fitness value. Where diversity appears, it is an exploration device inside one search, not an objective.

## 2.2 Multi-objective and quality-diversity search with LLMs

Pareto-based prompt search is emerging. Pareto Prompt Optimization trains a prompt generator with dominance-based preference losses instead of a fixed scalarisation [@Zhao2025pareto]. MOPrompt runs a multi-objective evolutionary search on accuracy versus context length and reports a 31% shorter prompt at the best baseline's accuracy on one sentiment task [@Camara2025moprompt]. REMoH wraps NSGA-II around LLM-generated heuristics, with a clustering reflection step that keeps offspring diverse [@Fornies2025remoh]; an LLM-aided MOEA uses an LLM only when a surrogate says it is worth the call [@Liu2024llm]. On the quality-diversity side, LLMs can propose archive members in context [@Lim2024incontext], MAP-Elites explores prompt space by structural descriptors [@Santos2025diverse], and CycleQD cycles which objective acts as the quality measure while the others act as behaviour axes [@Kuroki2025cycleqd].

**Gap.** Multi-objective LLM search so far targets accuracy versus cost on one task. None uses a *between-agent* distinctness objective, and none evaluates a prompt set on held-out events.

## 2.3 Diversity and perspective fidelity in multi-agent LLM systems

Multi-agent discussion can increase viewpoint diversity, but conformity and confabulation erode it. Persona-assigned agents drift from their assigned views under debate instructions [@Baltaji2024persona]. Vanilla debate often underperforms majority vote, and explicitly diversifying the initial viewpoints and calibrating confidence helps [@Zhu2026demystifying]. In a controlled logic study, group diversity and reasoning strength mattered most, while majority pressure discouraged independent correction [@Wu2025debate]. Diversity collapses across models, not only within one: an open-ended study finds intra-model repetition and inter-model homogeneity [@Jiang2025hivemind]. For economic reasoning, LLMs lean towards intervention-oriented causal conclusions, and that bias persists under one-shot prompting [@Lee2026ideological]. Macro agents with explicit hawkish and dovish beliefs can improve FOMC classification, but the study does not check whether agents stay faithful to their belief across rounds [@Takano2025hawkish]. Survey simulations with LLM agents match macro expectation distributions only when priors are injected [@Lin2025simulating].

Automated multi-agent design is also active. MASS optimises prompts and topology in three stages with a single task score [@Zhou2026mass]. EvoMAS evolves multi-agent configurations by mutation and crossover guided by execution traces [@Hu2026evomas].

**Gap.** Diversity is studied as an accuracy device or as a property to be measured, but not as an optimisation target next to persona fidelity, and not for competing economic perspectives.

## 2.4 Evolutionary model merging, fine-tuning and self-evolution

Evolution has been applied to parameters and recipes rather than text. Evolutionary search over merge recipes, in parameter and data-flow space, yields state-of-the-art Japanese models [@Akiba2025merging]. Multi-objective evolution of merged experts trades cross-task performance against storage [@Qiu2026modular], and a two-dimensional recombination of LLM blocks is searched by bi-level multi-objective evolution [@Wu2026lego]. Layer-wise merging of reasoning-tuned LLMs is another route to combining specialised models [@Zhang2024unconstrained]. Evolution strategies can fine-tune billion-parameter LLMs without gradients [@Qiu2026es], and black-box evolutionary merging works from API queries alone [@Chen2025evomerging]. Self-evolving training co-evolves a rubric generator and a policy without human labels [@Li2026evolm].

**Gap.** These methods optimise weights, which requires training or merging infrastructure. The project's setting, where the only decision variables are the texts of a few prompts, is a cheaper and more interpretable point in the same family.

## 2.5 Synthesis and positioning

Table 1 summarises the literature along the axes that matter for this project.

| Axis | Typical finding | Relevance to our design |
|---|---|---|
| LLM as operator | Works for prompts, heuristics and code [@Fernando2024promptbreeder; @Guo2024evoprompt; @Liu2024evolution] | We use an LLM mutation with an objective-directed instruction |
| Objective | Mostly one scalar; Pareto variants exist for accuracy versus cost [@Zhao2025pareto; @Camara2025moprompt] | Three objectives, one of which is inter-agent distinctness |
| Diversity | Measured or used as initialisation; homogeneity documented [@Jiang2025hivemind; @Zhu2026demystifying] | Made an explicit objective |
| Persona fidelity | Erodes under debate [@Baltaji2024persona; @Wu2025debate] | Measured with a lexicon; held out on separate events |
| Evaluation | Mostly one task; few held-out checks | Search and held-out seeds are separate; ablations are reported |

**Our position.** To our knowledge no paper combines (i) a *set* of agent prompts as one individual, (ii) a between-agent distinctness objective next to fidelity and length, (iii) an LLM as the mutation operator guided by the weakest objective, and (iv) a held-out check on unseen events. We treat the position as a gap identified from this review rather than as a proof of novelty.

# 3 Method

## 3.1 Problem formulation

An individual is a prompt set $P = (g_{\text{kw}}, g_{\text{au}}, g_{\text{mo}})$ with one gene per school. For a set of synthetic events $E$, each school $s$ answers each event with a parseable report or fails. Three objectives are minimised, all in $[0,1]$:

- $g_1 = 1 - \text{fidelity}(P)$, where fidelity is the mean lexicon consistency of each school's answers (the thesis consistency score, $C_s$).
- $g_2 = 1 - \text{disagreement}(P)$, where disagreement is the mean pairwise signal disagreement between the three schools (`mosaic.divergence.distance`).
- $g_3 = \min(1, \text{words}(P)/600)$.

Feasibility requires that at least 90% of school outputs are parseable. Infeasible sets are ranked by their violation, following Deb's rule.

## 3.2 Genome and decoding

Each school gene has four parts: `diagnosis` (sentences), `concepts` (an ordered subset of a concept pool), `stance` (sentences describing typical readings of events) and an optional `contrast` (sentences of the form "unlike the other schools, you ..."). Decoding fills the unchanged `mosaic.divergence.messages()` template, so the output format (causal chain, scenarios, signals) and the events are identical to the thesis harness. The initial population is the hand-written set B0 plus perturbed copies of it.

## 3.3 Variation

- **Structural crossover** (probability 0.7). With probability 0.5 whole school genes are swapped between parents; otherwise each field of each school is picked from one parent.
- **Rule mutation.** One school is chosen; one or two of: drop or swap a diagnosis sentence, drop, add or reorder a concept. It changes one school, so the other two school outputs are reused from the cache.
- **LLM-guided mutation** (probability 0.5 of the mutations in the LLM methods). The parent's evaluation picks the objective to improve, with probability proportional to its badness: fidelity (rewrite the least faithful school's diagnosis using its lexicon terms), distinctness (rewrite one field of one of the two most similar schools so that it makes different calls from the other), or length (shorten the longest school's diagnosis to 40 words). The model returns one paragraph; it is accepted if it has 5 to 120 words, and otherwise the child falls back to rule mutation (8 of 30 LLM children in NSGA-II and 10 of 34 in the GA were rejected this way).

## 3.4 Selection

- **NSGA-II.** Constrained non-dominated sorting, crowding distance, binary tournament on (rank, crowding), and elitist $(\mu+\lambda)$ environmental selection [@Deb2002].
- **GA (B2).** The same operators, but selection by feasibility first and then the equal-weight sum of $g_1, g_2, g_3$. This isolates the effect of the selection scheme.

## 3.5 Baselines, ablation and indicator

- **B0.** The hand-written profiles, evaluated with three independent sampling seeds.
- **B1 random search.** Independent random rule perturbations of B0 (1 to 3 operators per school), the same number of evaluations, and the same archive.
- **Ablation.** NSGA-II with rule mutation only (no LLM).
- **Indicator.** Exact 3-D hypervolume of the feasible non-dominated archive, with reference point (1, 1, 1). The archive keeps every feasible set evaluated, so all methods are compared on the same footing.
- **Knee.** The archive member closest to the ideal point (0, 0, 0). The rule was fixed before the held-out run (`code/PROTOCOL.md`).

# 4 Experimental Setup

## 4.1 Task and data

The task is a set of synthetic macroeconomic events produced by `mosaic.teacher.make_items`. The search set is the first five events of seed 23 and the held-out set is the first ten of seed 29; search and held-out sets share no events. Seed 11 (the thesis disagreement matrix) and all thesis held-out files are not used. Lexicons come from `configs/lexicons.toml`, which the thesis marks as PROVISIONAL; this affects the fidelity objective (Section 6).

## 4.2 Model and backend

Each call goes to an OpenAI-compatible endpoint (`qwen3.8-max`, the model used for the thesis disagreement matrix) with temperature 0.7, top-p 0.9, at most 1,024 output tokens, thinking disabled and a per-run sampling seed. Every response is stored in an append-only cache keyed by the model, the messages and the sampling parameters (`results/cache/llm_cache.jsonl`). A ledger records token counts and an estimated spend, with a USD 30 cap. The spend uses assumed list prices of USD 2.4 and 9.6 per million input and output tokens; the measured token counts are stored, so the cost can be recomputed with the provider's sheet.

## 4.3 Hyperparameters

| Parameter | Value |
|---|---|
| Population $N$ | 6 |
| Generations $G$ | 4 (so $N(G+1) = 30$ evaluations per run) |
| Search events / held-out events | 5 / 10 |
| Algorithm seeds (paired across methods) | 1, 2, 3 |
| Crossover / mutation / LLM share | 0.7 / 0.9 / 0.5 |
| Tournament size | 2 |
| Feasibility threshold | 0.9 |
| Length normalisation | 600 words |
| Hypervolume reference | (1, 1, 1) |
| LLM edit length | 5 to 120 words |
| Sampling | temperature 0.7, top-p 0.9, max 1,024 tokens, thinking off |

## 4.4 Procedure

1. For each method and seed, run the search on the five search events and keep the archive (`results/runs/<method>_s<seed>/gen_log.csv`, `evaluations.jsonl`, `front.jsonl`).
2. Select the knee of the final archive and write it to `results/best_prompts/`.
3. Re-measure each knee, and B0, on the ten held-out events. Each knee is also re-scored from the cache per event (`results/heldout_per_event.csv`).
4. Average over seeds per event and test each method against B0 with an exact paired sign-flip test over the ten events. Correct for eight tests with Holm (`results/heldout_tests.csv`).

## 4.5 Statistics

Search-level results are mean ± sample standard deviation over three seeds. Held-out intervals are 95% percentile bootstrap intervals over the ten events (10,000 resamples, `mosaic.stats.paired`, seed 0). They are not corrected for multiple comparisons; the p-values are exact sign-flip values and are the ones corrected with Holm. With three paired seeds the smallest attainable one-sided sign-flip p-value is 1/8, so search-level comparisons are reported descriptively. The inferential test uses the ten held-out events, where the smallest attainable two-sided p-value is 2/1024.

## 4.6 Reproduction

`code/README.md` gives the commands. The matrix was run with `python -m evo_prompt.runner --methods b0 nsga2 ga random nsga2_rule --seeds 1 2 3 --gens 4 --pop 6 --heldout --budget 30`, and the tables with `python -m evo_prompt.analyze` and `python -m evo_prompt.figures`. The analysis reads only the committed cache, so it makes no model calls.

# 5 Results and Analysis

## 5.1 Search level

Table 2 reports the archive and the knee on the search events. Values are mean ± sd over three seeds (`results/summary_table.md`).

| Method | Hypervolume | Front size | Knee fidelity | Knee disagreement | Knee validity | Knee words |
|---|---|---|---|---|---|---|
| NSGA-II + LLM | 0.1211 ± 0.0182 | 9.3 ± 1.5 | 0.461 ± 0.026 | 0.460 ± 0.025 | 0.978 ± 0.039 | 330 ± 50 |
| GA (weighted sum) | 0.1220 ± 0.0130 | 10.7 ± 1.2 | 0.452 ± 0.038 | 0.459 ± 0.032 | 1.000 ± 0.000 | 305 ± 29 |
| Random search | 0.0978 ± 0.0119 | 4.3 ± 0.6 | 0.474 ± 0.011 | 0.437 ± 0.017 | 1.000 ± 0.000 | 350 ± 38 |
| NSGA-II, rule only | 0.0979 ± 0.0135 | 7.7 ± 4.0 | 0.460 ± 0.016 | 0.429 ± 0.061 | 0.933 ± 0.000 | 346 ± 37 |

![**Figure 1.** Mean hypervolume of the feasible archive per generation (3 seeds, shaded ±1 sd). Generation 0 is the shared initial population.](../results/figures/hv_vs_generation.png)

Figure 1 shows the mean hypervolume per generation. Generation 0 is the shared initial population (0.071 for NSGA-II, the ablation and the GA alike; 0.073 for random search). From generation 1 on, NSGA-II and the GA rise above the two methods without LLM mutation (generation 4: 0.121 and 0.122, against 0.098 and 0.098), and the gap widens over the generations. ![**Figure 2.** Final feasible archives of NSGA-II + LLM and the GA (3 seeds each), fidelity against disagreement on the search events, coloured by prompt-set length.](../results/figures/pareto_fronts.png)

Figure 2 shows the final archives in the fidelity–disagreement plane, coloured by length.

The pattern answers RQ2 at this budget. NSGA-II without LLM mutation has the same hypervolume as random search (0.0979 against 0.0978), so selection alone adds nothing over random sampling here. Adding the LLM as mutation operator raises the hypervolume to 0.121 for NSGA-II and 0.122 for the GA, and the choice of selection scheme makes no visible difference (the GA's selection is single-objective, yet its archive has the same hypervolume). In this experiment the LLM-guided mutation is the component that carries the search-level gain. With three seeds the standard deviations overlap, so this is a descriptive finding, not a significance claim.

## 5.2 Held-out events

Table 3 reports the knee solutions on the ten held-out events. B0 is re-measured with three sampling seeds.

| Method | Fidelity | Disagreement | Validity | Words |
|---|---|---|---|---|
| B0 hand-written | 0.406 ± 0.002 | 0.407 ± 0.028 | 0.989 ± 0.019 | 438 |
| NSGA-II + LLM | 0.424 ± 0.017 | 0.423 ± 0.006 | 0.989 ± 0.019 | 330 ± 50 |
| GA (weighted sum) | 0.448 ± 0.043 | 0.419 ± 0.027 | 0.978 ± 0.019 | 305 ± 29 |
| Random search | 0.432 ± 0.009 | 0.432 ± 0.024 | 0.967 ± 0.033 | 350 ± 38 |
| NSGA-II, rule only | 0.433 ± 0.032 | 0.428 ± 0.048 | 1.000 ± 0.000 | 346 ± 37 |

Table 4 gives the paired tests. Each comparison uses the ten held-out events, and Holm correction covers the eight method-versus-B0 tests.

| Comparison | Metric | Mean difference (method − B0) | 95% bootstrap CI | p (exact, raw) | p (Holm) |
|---|---|---|---|---|---|
| NSGA-II + LLM − B0 | fidelity | +0.0179 | [-0.0086, +0.0413] | 0.2168 | 1.0000 |
| NSGA-II + LLM − B0 | disagreement | +0.0056 | [-0.0649, +0.0725] | 0.8672 | 1.0000 |
| GA (weighted sum) − B0 | fidelity | +0.0426 | [+0.0133, +0.0734] | 0.0293 | 0.2051 |
| GA (weighted sum) − B0 | disagreement | -0.0074 | [-0.0889, +0.0704] | 0.8848 | 1.0000 |
| Random search − B0 | fidelity | +0.0262 | [+0.0084, +0.0437] | 0.0254 | 0.2031 |
| Random search − B0 | disagreement | +0.0000 | [-0.0813, +0.0741] | 0.9805 | 1.0000 |
| NSGA-II, rule only − B0 | fidelity | +0.0272 | [+0.0041, +0.0503] | 0.0566 | 0.3398 |
| NSGA-II, rule only − B0 | disagreement | +0.0204 | [-0.0518, +0.0852] | 0.5664 | 1.0000 |

No comparison is significant after Holm correction (smallest adjusted p = 0.203). Before correction, the exact sign-flip p-values for the fidelity gains of the GA and random search are about 0.03. The uncorrected 95% bootstrap intervals exclude zero for the fidelity gains of the GA, random search and the ablation, but the corresponding p-values do not survive the correction across eight tests. We therefore read these fidelity gains as suggestive, not established. ![**Figure 3.** Held-out fidelity and disagreement of B0 and the knee solutions. Bars are the mean over the ten events; error bars are standard errors; dots are individual events.](../results/figures/heldout_bars.png)

Figure 3 shows the per-event values.

Three observations follow from the tables.

1. **The prompt sets get shorter, not less faithful.** The searched knees have 305 to 350 words against 438 for B0 (about 20% to 30% shorter), with fidelity and disagreement within a few hundredths of B0. For a deployment where prompt length costs tokens, this is a real trade-off gain; the experiment does not show that it is more than that.
2. **Most of the held-out fidelity gain is not specific to evolution.** Random search, which applies no selection, gains more fidelity (+0.026) than NSGA-II with LLM mutation (+0.018); the ablation gains +0.027. Only the GA's gain (+0.043) is clearly larger, and it is not significant after correction. This does not show that search works, and it is the main caution for the conclusions in Section 6.
3. **Disagreement does not move.** No method changes disagreement by more than 0.02 on held-out events, and B0's own three sampling replicates range from 0.22 to 0.38 on the search events. The differences in disagreement are inside the sampling noise.

## 5.3 Qualitative observations

What we can count: 8 of 30 LLM-guided children in NSGA-II (27%) and 10 of 34 in the GA (29%) were rejected by the 5-to-120-word check and replaced by rule mutation (`results/runs/*/evaluations.jsonl`, origin suffix `f`). What we have not done yet is a qualitative reading of the accepted edits. This is left open for the student's review, and the best prompt sets for each method are stored in `results/best_prompts/` so that the reading can be done without re-running anything.

# 6 Discussion

## 6.1 What the results say

At this budget, LLM-guided mutation increases the hypervolume of the search archive relative to both random sampling and rule-based NSGA-II, which answers RQ2 in favour of the LLM as the operator. The selection scheme does not matter in our setting. On held-out events the searched prompt sets are shorter, with fidelity and disagreement close to the hand-written set, which is a modest answer to RQ1 and RQ3: no dominance over B0 is established, and no method beats random search on the held-out events by a margin that survives correction.

## 6.2 Limitations

- **Budget.** Population 6 and four generations give 30 evaluations per run. This is a smoke-scale study. It was reduced from the planned population 8 and five generations so that the total stayed under the USD 30 cap (estimated spend USD 20.20).
- **Seeds.** Three seeds per method. The smallest attainable sign-flip p-value on three paired seeds is 0.125, so search-level comparisons are descriptive.
- **Model.** The model is `qwen3.8-max` through an API, not Qwen3-8B on a GPU. Output is cached but not bit-reproducible across providers; the raw responses are committed so that analysis can be repeated without the API.
- **Cost figures.** The USD figures use assumed list prices (USD 2.4 and 9.6 per million tokens), not the provider's invoice. Token counts are measured.
- **Lexicon.** The fidelity objective uses a lexicon the thesis marks as PROVISIONAL. Optimising it invites Goodhart-style gaming: a set can raise its lexicon hits without a better analysis. Expert or model-based judging of faithfulness is the natural fix and is not included.
- **Synthetic events.** The events are generated, and their macro context is synthetic. The results say nothing about real forecasting accuracy.
- **Confounds.** The LLM methods make more model calls per child than rule mutation, and they produce more novel text. The comparison holds the evaluation budget fixed in evaluations, not in calls.
- **Single school family.** The three schools are one economic taxonomy. Generalisation to other perspectives is not tested.

## 6.3 Future work

A full-scale run with population 8 or more, at least five seeds, and a larger search set would give the inferential power the held-out tests lack. Replacing the lexicon with a judge model calibrated on human ratings would address the Goodhart risk. The most useful extension is a control that holds the number of model calls fixed across methods, to separate the LLM effect from the extra text it generates.

# 7 Conclusion

We formulated the design of three competing economic-school agents as a constrained multi-objective search over prompt sets, with fidelity, inter-agent disagreement and length as objectives and an LLM as the guided mutation operator. Under a reduced budget, the LLM-guided mutation raised the search hypervolume from about 0.098 to about 0.12, while selection scheme made no visible difference. On ten unseen events, the searched prompt sets are 20–30% shorter than the hand-written baseline with similar fidelity and disagreement, but no held-out improvement survives multiple-comparison correction, and random search gains almost as much fidelity as the evolutionary methods. The evidence supports LLM-guided mutation as a useful operator for prompt-set search and does not yet support a claim that the evolved sets outperform careful hand-written prompts on unseen events.

# Appendix A: Use of AI tools

- **Literature review.** Four sub-agents, each covering one theme, searched for 2024–2026 papers and opened the arXiv or venue page of each candidate. Author lists and first-submission dates of all entries were re-checked against arXiv on 2026-11-01. Venue details come from arXiv comments or the course reference list. The student still has to confirm the DOIs of the two surveys on the publisher sites before submission (see `AI_USE.md`).
- **Code.** The evo_prompt package, tests and runner were written with an AI coding assistant. They pass 20 offline tests (`python -m pytest -q courses/dsai6707/code`) and the repository's own test suite; the student has not yet reviewed the code line by line.
- **Analysis and figures.** Written with AI assistance; numbers are generated by the scripts in `code/evo_prompt/` and can be regenerated from `results/`.
- **Report prose.** This draft was written with AI assistance. The student is responsible for the final wording, the interpretation and the citations.
- **Experiments.** The model calls were made by the code in this repository, through the API, under the budget cap described above.

# Appendix B: File map for the numbers

| Number | File |
|---|---|
| Hypervolume, front size, knee search metrics | `results/summary_search.csv`, `results/summary_table.md` |
| Held-out means, per-event values | `results/summary_table.md`, `results/heldout_per_event.csv` |
| Paired tests and Holm | `results/heldout_tests.csv` |
| Hypervolume curves | `results/runs/<method>_s<seed>/gen_log.csv`, `results/figures/hv_vs_generation.png` |
| Evaluations and origins (LLM children, rejections) | `results/runs/<method>_s<seed>/evaluations.jsonl` |
| Best prompt sets | `results/best_prompts/<method>_s<seed>_knee.txt` |
| Raw model outputs | `results/cache/llm_cache.jsonl` |
| Spend and token totals | `results/logs/matrix.log` (ledger line) |
| Smoke test | `results/smoke/nsga2_s1/` |
| Analysis protocol | `code/PROTOCOL.md` |

# References
