# Summary (5 seeds per search method; B0 over 5 sampling replicates)

## Search events (seed 23, 5 events): archive hypervolume and knee solution

| Method | Hypervolume | Front size | Knee fidelity | Knee disagreement | Knee validity | Knee words |
|---|---|---|---|---|---|---|
| NSGA-II + LLM | 0.0744 ± 0.0096 | 7.0 ± 3.6 | 0.283 ± 0.011 | 0.471 ± 0.045 | 0.973 ± 0.037 | 323 ± 33 |
| GA (weighted sum) | 0.0721 ± 0.0136 | 7.2 ± 1.9 | 0.263 ± 0.016 | 0.510 ± 0.058 | 0.947 ± 0.030 | 330 ± 30 |
| Random search | 0.0664 ± 0.0052 | 5.8 ± 2.2 | 0.299 ± 0.008 | 0.455 ± 0.027 | 0.960 ± 0.037 | 345 ± 26 |
| NSGA-II, rule only | 0.0675 ± 0.0145 | 7.8 ± 3.1 | 0.276 ± 0.040 | 0.491 ± 0.058 | 0.973 ± 0.037 | 344 ± 24 |
| GA, rule only | 0.0677 ± 0.0107 | 7.2 ± 3.6 | 0.267 ± 0.033 | 0.509 ± 0.064 | 0.987 ± 0.030 | 343 ± 19 |
| NSGA-II + unguided LLM | 0.0606 ± 0.0146 | 5.2 ± 1.9 | 0.290 ± 0.013 | 0.457 ± 0.071 | 0.973 ± 0.037 | 368 ± 44 |
| EvoPrompt (GA) | 0.0444 ± 0.0099 | 3.0 ± 0.7 | 0.254 ± 0.020 | 0.456 ± 0.068 | 0.973 ± 0.037 | 392 ± 28 |
| EvoPrompt (GA), length-bounded | 0.0491 ± 0.0085 | 6.2 ± 0.8 | 0.262 ± 0.020 | 0.483 ± 0.037 | 0.973 ± 0.037 | 412 ± 45 |

## Held-out events (seed 29, 10 events): knee solution, mean ± std over seeds

| Method | Fidelity | Disagreement | Validity | Words |
|---|---|---|---|---|
| B0 hand-written | 0.238 ± 0.018 | 0.427 ± 0.067 | 0.927 ± 0.043 | 438 ± 0 |
| NSGA-II + LLM | 0.248 ± 0.027 | 0.481 ± 0.039 | 0.960 ± 0.028 | 323 ± 33 |
| GA (weighted sum) | 0.244 ± 0.034 | 0.459 ± 0.031 | 0.940 ± 0.049 | 330 ± 30 |
| Random search | 0.259 ± 0.023 | 0.488 ± 0.058 | 0.933 ± 0.033 | 345 ± 26 |
| NSGA-II, rule only | 0.243 ± 0.020 | 0.458 ± 0.044 | 0.973 ± 0.028 | 344 ± 24 |
| GA, rule only | 0.241 ± 0.050 | 0.506 ± 0.046 | 0.967 ± 0.033 | 343 ± 19 |
| NSGA-II + unguided LLM | 0.261 ± 0.019 | 0.518 ± 0.069 | 0.967 ± 0.024 | 368 ± 44 |
| EvoPrompt (GA) | 0.224 ± 0.005 | 0.495 ± 0.040 | 0.947 ± 0.018 | 392 ± 28 |
| EvoPrompt (GA), length-bounded | 0.243 ± 0.010 | 0.463 ± 0.088 | 0.940 ± 0.028 | 412 ± 45 |

## Paired tests vs B0 on the 10 held-out events (exact sign-flip, Holm over 16 tests)

| Comparison | Metric | Mean difference (method - B0) | 95% bootstrap CI | p (exact, raw) | p (Holm) |
|---|---|---|---|---|---|
| nsga2 - b0 | fidelity | +0.0103 | [-0.0054, +0.0257] | 0.2422 | 1.0000 |
| nsga2 - b0 | disagreement | +0.0211 | [-0.0478, +0.0955] | 0.6211 | 1.0000 |
| ga - b0 | fidelity | +0.0062 | [-0.0089, +0.0209] | 0.4336 | 1.0000 |
| ga - b0 | disagreement | -0.0111 | [-0.0656, +0.0456] | 0.7031 | 1.0000 |
| random - b0 | fidelity | +0.0209 | [+0.0020, +0.0416] | 0.0996 | 1.0000 |
| random - b0 | disagreement | -0.0011 | [-0.0633, +0.0534] | 0.9902 | 1.0000 |
| nsga2_rule - b0 | fidelity | +0.0052 | [-0.0079, +0.0187] | 0.5059 | 1.0000 |
| nsga2_rule - b0 | disagreement | +0.0077 | [-0.0411, +0.0622] | 0.8047 | 1.0000 |
| ga_rule - b0 | fidelity | +0.0032 | [-0.0063, +0.0135] | 0.5547 | 1.0000 |
| ga_rule - b0 | disagreement | +0.0466 | [-0.0178, +0.1044] | 0.2031 | 1.0000 |
| nsga2_llmu - b0 | fidelity | +0.0230 | [+0.0114, +0.0345] | 0.0078 | 0.1250 |
| nsga2_llmu - b0 | disagreement | +0.0578 | [+0.0155, +0.1055] | 0.0273 | 0.4102 |
| evoprompt_ga - b0 | fidelity | -0.0136 | [-0.0281, +0.0016] | 0.1270 | 1.0000 |
| evoprompt_ga - b0 | disagreement | +0.0177 | [-0.0190, +0.0544] | 0.4219 | 1.0000 |
| evoprompt_ga_lc - b0 | fidelity | +0.0047 | [-0.0096, +0.0185] | 0.5508 | 1.0000 |
| evoprompt_ga_lc - b0 | disagreement | -0.0133 | [-0.0600, +0.0389] | 0.6250 | 1.0000 |
