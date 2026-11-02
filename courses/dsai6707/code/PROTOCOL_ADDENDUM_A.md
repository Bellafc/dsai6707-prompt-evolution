# Protocol addendum A: completing the ablation (fixed before any run of the new arms)

Written 2026-11-02, before any model call for `ga_rule` or `nsga2_llmu`. The commit that adds this file precedes the
commit of their results; `git log` shows the order. Everything in `PROTOCOL.md` (events, objectives, feasibility,
hypervolume, knee rule, sampling, model) applies unchanged unless stated here.

## Why
The main matrix leaves two gaps (report Section 5.1): the 2 x 2 design selection x mutation has no GA with rule
mutation only, and nothing separates the objective-directed instruction from LLM rewriting as such.

## New arms
- `ga_rule`: the GA of `PROTOCOL.md` (feasibility first, then the equal-weight sum of g1..g3) with rule mutation only.
- `nsga2_llmu`: NSGA-II with *unguided* LLM mutation. Same LLM call, share (0.5 of mutations), acceptance rule
  (5 to 120 words, else fall back to rule mutation) and system message as `nsga2`, but the school and the field
  (diagnosis or stance) are drawn uniformly at random and the instruction is the fixed text "Rewrite this paragraph in
  your own words. Keep its meaning and keep it as one paragraph." It carries no objective, lexicon or length information.
- Population 6, 4 generations, algorithm seeds 1, 2, 3, held-out evaluation of each knee; `qwen3.8-max` with the same
  sampling as the main matrix. Both arms share the initial population of `nsga2`, `ga` and `nsga2_rule` per seed.

## Questions and decision rules (all search-level comparisons are descriptive: 3 paired seeds, smallest p = 1/8)
- **Q1 selection under rule mutation:** `ga_rule` vs `nsga2_rule`, final archive hypervolume.
- **Q2 LLM mutation under GA selection:** `ga` vs `ga_rule`, final hypervolume.
- **Q3 guidance:** `nsga2` vs `nsga2_llmu`, final hypervolume.
- For each question, report the mean ± sd and the three per-seed differences. A direction is called "consistent" only
  if all three seeds agree in sign; otherwise the report says there is no evidence either way. The report also gives
  the 2 x 2 table of mean hypervolume (selection x mutation).

## Held-out tests
- Table of method-versus-B0 tests extended to the six search methods: 12 tests (fidelity, disagreement), exact
  sign-flip over the 10 held-out events, Holm over the 12.
- Protocol family extended accordingly: 12 method-versus-B0 plus 30 method-versus-method tests, Holm over 42, written to
  `results/heldout_tests_protocol.csv`. The two pre-specified method-versus-method comparisons of interest are
  `nsga2` vs `nsga2_llmu` and `ga` vs `ga_rule` (fidelity and disagreement); they are read inside the 42-test family.
- The duplicated held-out event sensitivity check (`syn-k0007`) is applied to the new arms as well.

## Cost control and execution
- `python -m evo_prompt.runner --methods ga_rule nsga2_llmu --seeds 1 2 3 --gens 4 --pop 6 --heldout --budget 15`
- The ledger cap (USD 15, estimated at the assumed prices of `config.py`) applies to this command; cached calls are
  free. Order: `ga_rule` seeds 1-3, then `nsga2_llmu` seeds 1-3. If the cap stops the run, unfinished arms are reported
  as incomplete, not with fewer seeds.
- Results go to `results/runs/ga_rule_s*/` and `results/runs/nsga2_llmu_s*/`; the log to `results/logs/addendum_a.log`.
