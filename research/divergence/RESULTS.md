# Disagreement matrix: results (2026-11-01)

Purpose (design note decision 2, now closed by the scope rule D13): check that the three trained schools make
different calls beyond run-to-run noise, see where the candidate frameworks sit, and test whether literature
positions predict disagreement. Evaluation only; nothing here is trained on or preregistered.

Setup: six frameworks (Keynesian, Austrian, Monetarist from `configs/teacher/templates.toml`; New Keynesian, New
Classical, Post-Keynesian from `configs/frameworks.toml`) × 30 synthetic events (seed 11), all voiced by one prompted
model (qwen3.8-max). Keynesian and New Keynesian were run twice for the noise floor. 240 requests, 239 parsed. Numbers
from `matrix.json` (`mosaic.divergence.analyze`); per-asset noise computed from the repeated runs.

## 1. The three schools differ beyond noise

| Measure | Pairs among K, A, M | Same framework twice (noise) |
|---|---|---|
| Signal disagreement (0 same, 1 opposite) | 0.21 (A–M), 0.26 (K–M), 0.28 (K–A) | 0.12 (K), 0.14 (NK) |
| Share of different calls (Kuncheva–Whitaker) | 0.33, 0.39, 0.42 | 0.21 |
| Macro gap (growth + inflation direction, 0–4) | 0.54–0.59 | 0.41–0.43 |

Every pair of trained schools disagrees about twice as much as one school disagrees with itself. Austrian and
Monetarist are the closest pair; Keynesian and Austrian the farthest.

## 2. Candidate frameworks

- **New Keynesian ≈ Keynesian**: signal disagreement 0.14, at the noise floor. It adds no information in this task.
- **Post-Keynesian** is near Keynesian (0.17), a little above noise.
- **New Classical** is the most distinct framework: the largest macro gap to every other framework (0.57–0.68) and
  its own MDS dimension. Under D13 it is not added; it is the main distinct framework the thesis leaves out
  (Ch. 7, limitation and future work).

## 3. Literature positions do not predict disagreement

| Distance used | Spearman ρ (15 pairs) | Exact one-sided p (720 relabellings) |
|---|---|---|
| state–market + orthodoxy | +0.28 | 0.19 |
| state–market only | +0.13 | 0.33 |
| orthodoxy only | +0.31 | 0.16 |

OLS of disagreement on the two axis distances: R² = 0.05. The sign is positive but nowhere near significant, and the
macro gap does not follow the positions at all (ρ = −0.29). This matches Gordon & Dahl (2013): economists'
disagreement is mostly not left–right. Caveats: six frameworks give little power; the positions are still a single
draft coding (the two-coder CHES-style coding should be done before the test is reported); one model voices all
frameworks, so a shared tilt of that model (Lee et al. 2026: most models lean interventionist) would compress the
disagreement, which makes section 1 conservative.

## 4. Where they disagree: inflation and money channels, not the direction of risk

Different calls per asset among the three schools, against the noise floor (mean of the two repeated frameworks):

| Asset | Three schools | Noise | Excess |
|---|---|---|---|
| Oil | 0.42 | 0.15 | +0.27 |
| Gold | 0.47 | 0.24 | +0.23 |
| US dollar | 0.52 | 0.34 | +0.18 |
| Government bonds | 0.37 | 0.19 | +0.18 |
| Equities | 0.28 | 0.17 | +0.11 |
| Credit | 0.22 | 0.17 | +0.05 |

The schools mostly agree on risk assets (equities, credit) and disagree on the assets that carry inflation and
monetary channels (oil, gold, the dollar, bonds). The dollar is also the noisiest asset within a framework.

## 5. Exploratory: two dimensions, read as mechanisms rather than positions

Classical MDS of the disagreement matrix: the first two dimensions carry 69% of the variance (0.38, 0.32; the third
0.16). Dimension 1 separates Austrian and Monetarist (+0.23, +0.17) from the Keynesian family (K −0.15, NK −0.15, PK
−0.06); dimension 2 isolates New Classical (+0.28). One reading, with six points only: forecast disagreement follows
the causal mechanism a framework assigns (demand, money, real shocks with rational expectations) more than its
political position. Suggestive only; not a claim for the thesis without more frameworks or a second model.

## 6. For the profile review (D9)

Mean signal per framework (−1 short … +1 long) shows the Austrian profile is only mildly long gold (+0.17) against
Keynesian +0.40 and Post-Keynesian +0.80, and the most bearish on credit (−0.83). The reviewer may check whether the
Austrian profile should name gold's role as a hedge against monetary debasement; the profile wording, not the
validator, would change. All frameworks lean bearish on average (growth −0.23 to −0.33), a property of the synthetic
event set.

## Use in the thesis

- Ch. 4 (design rationale, "Why these three schools?"): the three schools make different calls beyond noise, and the
  most mainstream candidate (New Keynesian) duplicates the Keynesian school in this task.
- Ch. 7: New Classical is the distinct framework left out; disagreement does not follow ideological distance
  (Gordon & Dahl), so the thesis does not claim that the schools map the political-economic space.
- Rerun `analyze` after the two-coder positions; report the permutation test, not the plain Spearman p-value.
