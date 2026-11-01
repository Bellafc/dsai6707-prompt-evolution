# Analysis protocol (fixed before the full matrix was run)

Written 2026-11-01, before any full-matrix result existed. Changes after this point must be listed as deviations in the report.

## Events
- Search set: `mosaic.teacher.make_items(5, seed=23)`, keynesian items (5 events). Used for all search and objectives.
- Held-out set: `make_items(10, seed=29)`, keynesian items (10 events). Used once per knee solution and for B0. Never used for search decisions.
- Seed 11 (thesis disagreement matrix) and all thesis held-out files are not used.

## Methods and budget
- `b0`: hand-written prompt set (mosaic.divergence profiles), evaluated with three LLM sampling seeds (1, 2, 3).
- `nsga2`: constrained NSGA-II with structural crossover, rule mutation and LLM-guided mutation.
- `ga`: single-objective GA, equal-weight sum of g1..g3 with feasibility first, same operators as `nsga2`.
- `random`: B1, independent random rule perturbations of B0, same evaluation count.
- `nsga2_rule`: ablation, NSGA-II without LLM-guided mutation.
- Population N = 6, generations G = 4, so every search method evaluates N(G+1) = 30 prompt sets.
- Algorithm seeds 1, 2, 3 (paired across methods: the same seed gives the same initial population for `nsga2`, `ga`, `nsga2_rule`).

## Objectives (minimisation, all in [0, 1])
- g1 = 1 - fidelity, fidelity = mean lexicon consistency over schools and events (mosaic.metrics, PROVISIONAL lexicon).
- g2 = 1 - disagreement, disagreement = mean pairwise signal disagreement (mosaic.divergence.distance).
- g3 = min(1, words / 600).
- Feasible if the share of parseable school outputs is at least 0.9. Infeasible solutions are ranked by violation (Deb).

## Quality indicator
- Hypervolume of the feasible non-dominated archive (all evaluated feasible prompt sets) with reference point (1, 1, 1).

## Knee rule (applied identically to every method)
- Knee = feasible archive member closest to the ideal point (0, 0, 0) in (g1, g2, g3) space. Ties: first in evaluation order.

## Statistics
- Search-level comparisons over 3 seeds: mean and sample standard deviation only. Sign-flip permutation over 3 seeds cannot give p < 0.125, so it is reported as descriptive.
- Held-out comparisons: per held-out event, the knee's metric averaged over the 3 seeds versus B0's metric on the same event. Paired sign-flip permutation over the 10 events (exact enumeration of 2^10 sign patterns), Holm correction across the family of comparisons (method vs. B0 and method vs. method).

## Cost controls
- Estimated spend capped at USD 30 by the ledger (assumed prices in config.py; measured token counts are stored per call in results/cache/llm_cache.jsonl).
- Order of execution: b0, nsga2, ga, random, nsga2_rule. If the cap stops the run, the ablation is reported as incomplete rather than with fewer seeds.
