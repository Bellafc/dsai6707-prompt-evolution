# Disagreement matrix

Parsed 239 analyses, 1 unparsable.

Signal disagreement (0 = same calls, 1 = all opposite), above the diagonal; macro gap (expected growth plus inflation direction, 0-4), below it.

| | keynesian | austrian | monetarist | new_keynesian | new_classical | post_keynesian |
|---|---|---|---|---|---|---|
| keynesian | – | 0.28 | 0.26 | 0.14 | 0.23 | 0.17 |
| austrian | 0.54 | – | 0.21 | 0.31 | 0.29 | 0.23 |
| monetarist | 0.59 | 0.57 | – | 0.28 | 0.27 | 0.26 |
| new_keynesian | 0.50 | 0.64 | 0.66 | – | 0.25 | 0.19 |
| new_classical | 0.66 | 0.57 | 0.67 | 0.68 | – | 0.28 |
| post_keynesian | 0.50 | 0.49 | 0.59 | 0.49 | 0.62 | – |

Noise (the same framework run twice):

- keynesian: signals 0.12, opposite 0.04, macro 0.41 (n=29)
- new_keynesian: signals 0.14, opposite 0.08, macro 0.43 (n=30)

Forecast dispersion across all frameworks: {'events': 30, 'growth': 0.212, 'inflation': 0.24}; three schools only: {'events': 30, 'growth': 0.175, 'inflation': 0.191}.
Literature distance (state-market + orthodoxy) vs measured disagreement, Spearman over 15 pairs: 0.277.
Exact permutation test (frameworks relabelled, one-sided): both rho +0.277, p 0.193; state_market rho +0.133, p 0.328; orthodoxy rho +0.309, p 0.156 (720 permutations).

Different calls per asset, mean over pairs: all frameworks {'equities': 0.289, 'government bonds': 0.369, 'US dollar': 0.502, 'gold': 0.518, 'oil': 0.316, 'credit': 0.244}; three schools {'equities': 0.278, 'government bonds': 0.367, 'US dollar': 0.522, 'gold': 0.467, 'oil': 0.422, 'credit': 0.222}.

Multidimensional scaling: variance share by dimension [0.375, 0.316, 0.16, 0.081]; 2-D coordinates {'keynesian': [-0.146, -0.04], 'austrian': [0.234, -0.077], 'monetarist': [0.171, 0.041], 'new_keynesian': [-0.152, -0.074], 'new_classical': [-0.049, 0.284], 'post_keynesian': [-0.059, -0.134]}.
OLS of pairwise disagreement on the distance along each axis: {'intercept': 0.34, 'state_market': 0.011, 'orthodoxy': 0.005, 'r2': 0.048, 'pairs': 15}.

Nearest framework by signal disagreement:

- keynesian: new_keynesian (0.14)
- austrian: monetarist (0.21)
- monetarist: austrian (0.21)
- new_keynesian: keynesian (0.14)
- new_classical: keynesian (0.23)
- post_keynesian: keynesian (0.17)
