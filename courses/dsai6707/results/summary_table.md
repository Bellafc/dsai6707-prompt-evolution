# Summary (3 seeds per search method; B0 over 3 sampling replicates)

## Search events (seed 23, 5 events): archive hypervolume and knee solution

| Method | Hypervolume | Front size | Knee fidelity | Knee disagreement | Knee validity | Knee words |
|---|---|---|---|---|---|---|
| NSGA-II + LLM | 0.1211 ± 0.0182 | 9.3 ± 1.5 | 0.461 ± 0.026 | 0.460 ± 0.025 | 0.978 ± 0.039 | 330 ± 50 |
| GA (weighted sum) | 0.1220 ± 0.0130 | 10.7 ± 1.2 | 0.452 ± 0.038 | 0.459 ± 0.032 | 1.000 ± 0.000 | 305 ± 29 |
| Random search | 0.0978 ± 0.0119 | 4.3 ± 0.6 | 0.474 ± 0.011 | 0.437 ± 0.017 | 1.000 ± 0.000 | 350 ± 38 |
| NSGA-II, rule only | 0.0979 ± 0.0135 | 7.7 ± 4.0 | 0.460 ± 0.016 | 0.429 ± 0.061 | 0.933 ± 0.000 | 346 ± 37 |

## Held-out events (seed 29, 10 events): knee solution, mean ± std over seeds

| Method | Fidelity | Disagreement | Validity | Words |
|---|---|---|---|---|
| B0 hand-written | 0.406 ± 0.002 | 0.407 ± 0.028 | 0.989 ± 0.019 | 438 ± 0 |
| NSGA-II + LLM | 0.424 ± 0.017 | 0.423 ± 0.006 | 0.989 ± 0.019 | 330 ± 50 |
| GA (weighted sum) | 0.448 ± 0.043 | 0.419 ± 0.027 | 0.978 ± 0.019 | 305 ± 29 |
| Random search | 0.432 ± 0.009 | 0.432 ± 0.024 | 0.967 ± 0.033 | 350 ± 38 |
| NSGA-II, rule only | 0.433 ± 0.032 | 0.428 ± 0.048 | 1.000 ± 0.000 | 346 ± 37 |

## Paired tests vs B0 on the 10 held-out events (exact sign-flip, Holm over 8 tests)

| Comparison | Metric | Mean difference (method - B0) | p (raw) | p (Holm) |
|---|---|---|---|---|
| nsga2 - b0 | fidelity | +0.0179 | 0.2168 | 1.0000 |
| nsga2 - b0 | disagreement | +0.0056 | 0.8672 | 1.0000 |
| ga - b0 | fidelity | +0.0426 | 0.0293 | 0.2051 |
| ga - b0 | disagreement | -0.0074 | 0.8848 | 1.0000 |
| random - b0 | fidelity | +0.0262 | 0.0254 | 0.2031 |
| random - b0 | disagreement | +0.0000 | 0.9805 | 1.0000 |
| nsga2_rule - b0 | fidelity | +0.0272 | 0.0566 | 0.3398 |
| nsga2_rule - b0 | disagreement | +0.0204 | 0.5664 | 1.0000 |
