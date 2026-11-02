# Protocol addendum C: a published baseline (EvoPrompt-GA) and parallel execution (fixed before these runs)

Written 2026-11-02, before any model call for `evoprompt_ga`. `PROTOCOL.md` and addenda A and B apply unless stated.

## Why
The course asks for baselines that include relevant existing methods. None of the arms so far is a published method.

## The baseline: EvoPrompt (GA)
Guo et al., "Connecting Large Language Models with Evolutionary Algorithms Yields Powerful Prompt Optimizers",
ICLR 2024 (arXiv 2309.08532), Section 3.2, Figure 1 and Algorithm 2, read from the paper on 2026-11-02.

- **Selection.** Two parents per child by roulette wheel, p_i = s_i / sum_j s_j. Score s = 1 - mean(g1, g2, g3) (the
  GA's equal-weight scalarisation turned into a score); infeasible sets get s = 1e-6.
- **Evolution.** One LLM call per school and child with the paper's template, verbatim: "Please follow the instruction
  step-by-step to generate a better prompt. 1. Cross over the following prompts and generate a new prompt: Prompt 1:
  ... Prompt 2: ... 2. Mutate the prompt generated in Step 1 and generate a final prompt bracketed with <prompt> and
  </prompt>." Prompt 1 and 2 are the two parents' diagnosis paragraphs of that school. The child takes the bracketed
  text as its diagnosis for each school; concepts, stance and contrast come from the first parent.
- **Update.** N children per generation, merged with the N parents; the best N are kept (feasibility first, then the
  scalar fitness, as the GA).
- **Adaptations, stated as such.** (i) The paper evolves one prompt; an individual here is a set of three, so the
  operator is applied to each school's diagnosis (three LLM calls per child; other arms make at most one). (ii) The same
  acceptance rule as all other arms: an answer without brackets or outside 5 to 120 words leaves that school's
  diagnosis as in the first parent. (iii) The final solution is chosen by the shared knee rule, not by EvoPrompt's
  argmax, so that all arms are compared on the same archive and knee. (iv) Same initial population (B0 plus perturbed
  copies) as the other arms; the paper also starts from manual prompts.

## Runs
- qwen (`results/`): `evoprompt_ga`, seeds 1 to 3, population 6, 4 generations, held-out; `--budget 10`. Runs alone on
  the shared qwen cache after addendum A finished.
- Haiku (`results/haiku/`): `evoprompt_ga`, seeds 1 to 5, same settings.

## Parallel execution of the Haiku replication (change to addendum B's execution, not to its design)
The sequential Haiku run is stopped after `b0` (seeds 1 to 5) and `nsga2` seeds 1 to 3 finished and `nsga2` seed 4 had
started. Its cache file is then frozen as a read-only base. Each remaining arm (`nsga2` seeds 4 to 5, `ga`, `random`,
`nsga2_rule`, `ga_rule`, `nsga2_llmu`, `evoprompt_ga`) runs in its own process with its own cache layer
(`results/haiku/cache/layers/<method>.jsonl`, `--cache-base`). Finished calls in the base are reused; new calls are
not shared between arms. Consequence: arms that would have produced identical prompt sets (for example `nsga2` and
`ga` in the first generation) now draw separate samples for them, so their trajectories are less coupled than in the
qwen study. The analysis reads each arm's own layer over the base.

## Analysis additions
- Q4 (search level): `nsga2` vs `evoprompt_ga`, final hypervolume, per-seed differences (and the exact one-sided
  sign-flip p-value over 5 seeds for Haiku), read as in addendum A.
- Held-out: `evoprompt_ga` vs B0 joins the method-versus-B0 table (14 tests, Holm over 14) and the protocol family
  (14 + 42 = 56 tests, Holm over 56). The comparison of interest is `nsga2` vs `evoprompt_ga`, read inside the family.
- The LLM answer rejection rate of `evoprompt_ga` is reported next to those of the other LLM arms.

## Amendment (2026-11-02, after 18 operator outputs and before any fitness comparison)
The first qwen generation showed that the paper's operator writes whole prompts: all 18 bracketed answers had 143 to
370 words, so the 120-word acceptance rule (adaptation ii above) rejected every one and the baseline would have run
without variation. Adaptation (ii) is replaced for `evoprompt_ga` only: a bracketed answer is accepted if it has 5 to
600 words (600 is the length normalisation of g3; a longer diagnosis alone saturates the length objective). Long
answers are therefore penalised by the length objective, not discarded. Both `evoprompt_ga` runs (qwen and Haiku)
were stopped and restarted from their caches. The only search output seen from the stopped runs was the qwen seed-1
log line for generation 1 (hypervolume unchanged from generation 0, as expected when every answer is rejected); no
result file was written. With `max_tokens` 1,024, an answer cut off before `</prompt>` still counts as rejected.
