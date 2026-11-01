# DRAFT pre-registration — exp02: Structural analogy retrieval (Stage 1)

Status: **DRAFT**. Binding once copied to `prereg/` by the human, before any score on the test queries.
Thesis chapter 5 (RQ2: the retriever is the agents' L2 tool `query_episode_db`, so this experiment validates the
L2 evidence the agents cite). Priority **P1**. CPU only.

## Question

Do historical episodes that are similar in **macro state** (Mahalanobis distance over point-in-time indicators)
predict how assets react to a new episode better than narrative similarity, plain Euclidean distance, or
unconditional averages?

## Data

The 141-episode database: trigger dates, 35 FRED indicators at trigger, 22 instruments × 5 horizons of reactions
(13,571 data points), 19 transmission channels, narratives for 117 episodes.

Two data fixes before any evaluation (agent prepares, human spot-checks):

1. **Point-in-time states.** For each episode, the indicator values as published at the trigger date (ALFRED
   vintages where available; otherwise the revised value, flagged). The revised-data state is kept for an ablation.
2. **Trigger-only descriptions.** The existing narratives may describe the aftermath (including market moves),
   which would leak the outcome into semantic retrieval. Build a description of only what was known at the
   trigger date; the human spot-checks 20 of them. Original narratives are kept for a leakage test.

## Protocol (expanding window, no look-ahead)

- Queries in date order. The candidate pool for query q is every episode with a trigger date strictly before q's.
- Covariance for the Mahalanobis distance: Ledoit–Wolf shrinkage estimated on the **monthly** standardized
  indicator panel up to q's date (hundreds of months), not on the episodes — this answers the 35-dimensions /
  141-samples concern. Missing indicators: distance on the observed subspace (Gaussian marginal).
- Methods: structural (Mahalanobis) · Euclidean on standardized indicators (the "History Rhymes"-style baseline,
  Khanna et al. 2025) · semantic (cosine on trigger-only descriptions) · hybrid α·structural + (1−α)·semantic ·
  baselines: unconditional pool mean, same-category mean, random k.
- Prediction: similarity-weighted mean of the top-k analogues' reactions (k = 5) per instrument × horizon.
- Tuning (α, k ∈ {3, 5, 10}, kernel bandwidth) only on **dev queries** (trigger date < 2005-01-01).
  **Test queries**: trigger date ≥ 2005-01-01.

## Metrics

Per query: directional hit rate over available instrument × horizon cells (primary); Spearman correlation of
predicted vs realised reactions (secondary). Averaged over queries; paired comparisons over test queries.

## Hypotheses (test queries; sign-flip permutation over queries; Holm across H1–H3)

- **H1**: structural > Euclidean (hit rate).
- **H2**: hybrid > semantic-only.
- **H3**: best analogy method > unconditional pool mean.
- Descriptive: point-in-time vs revised states; trigger-only vs original narratives (a large gain from original
  narratives is evidence of hindsight leakage and is reported as such).
