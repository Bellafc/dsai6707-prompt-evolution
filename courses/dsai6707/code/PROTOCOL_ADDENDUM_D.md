# Protocol addendum D: a length-bounded EvoPrompt variant (fixed before its runs)

Written 2026-11-02, after the Haiku runs of addendum C had finished and been analysed. This addendum is therefore
*post hoc*: it responds to an observed result, and the report labels it so.

## What was observed
On Haiku, every `evoprompt_ga` child had 668 to 1,132 words (initial population: median 420), the length objective was
saturated for all of them, and only 3 of 120 children (2.5%) were feasible, because agent outputs to such long prompts
were often cut off or unparseable. The archive hypervolume never rose above that of the initial population (0.044 in
every generation), so the win of `nsga2` over `evoprompt_ga` (5 of 5 seeds) mostly shows that the paper's operator,
which has no notion of length, does not work in a length- and format-constrained prompt-set problem.

## The variant
`evoprompt_ga_lc`: identical to `evoprompt_ga` (addendum C and its amendment) except that one sentence is appended to
step 2 of the paper's template: "The final prompt must not be longer than the longer of Prompt 1 and Prompt 2." It is
the smallest change that gives the operator the length information the problem needs. The verbatim baseline stays in
the report as well.

## Runs and analysis
- Haiku only (the qwen quota is exhausted), seeds 1 to 5, population 6, 4 generations, held-out, `--profile haiku`,
  one process per seed with its own cache layer (`layers/evoprompt_ga_lc__s<seed>.jsonl`) over the frozen base,
  `--budget 2` per process.
- Q5: `nsga2` vs `evoprompt_ga_lc`, final hypervolume, per-seed differences and the exact one-sided sign-flip p-value
  over five seeds; read with the decision rule of addendum A (consistent only if all five seeds agree in sign).
- Held-out: joins the method-versus-B0 table (16 tests, Holm over 16) and the protocol family (16 + 56 = 72 tests).
- The share of feasible children and the children's length are reported for both EvoPrompt arms.
