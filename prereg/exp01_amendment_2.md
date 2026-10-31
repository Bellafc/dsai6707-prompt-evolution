# exp01 — Amendment 2 (2026-10-31): validity check of the keyword metric

Registered before any model output exists. Adds a secondary outcome; the primary outcome (H1, keyword
consistency C_s, arm C vs arm B) is unchanged.

## Why

C_s counts school vocabulary. An examiner can fairly ask whether keyword hits measure school-specific *reasoning*.
The Confirmation itself called the metric "necessary but not sufficient". This amendment adds an independent
judgment and validates that judgment against humans.

## Judge

- Claude Opus 5.5 (`configs/judge.toml`), blind to arm and model. It sees the designated school, a one-paragraph
  definition of the school, the task and the answer.
- Four 1–5 scales: **fidelity** (reasoning driven by the school's mechanisms), **purity** (no competing-school
  drivers), **coherence** (event → mechanisms → scenarios → signals), **plausibility** (economically sound).
- Items: arms A, B, C on a fixed, difficulty-stratified subset of 48 test events × 3 schools = 432 judgments.
  **Arm D is excluded**: the judge is the same model as arm D (self-preference).
- 10% of items are judged twice to estimate test–retest reliability (the CLI exposes no temperature).

## Human validation

- Two raters (the author and one economics-trained colleague, named in the thesis) independently score a blinded
  sample of 60 judged items (stratified by arm × school) with the same rubric, without seeing arm, model or the
  judge's scores.
- Reported: inter-rater quadratic-weighted κ per scale; Spearman correlation between the judge and the mean human
  score per scale.

## Decision rules (fixed now)

- **Judge accepted** as a measure for a scale if inter-rater QWK ≥ 0.40 **and** judge–human Spearman ≥ 0.50 on
  that scale. Accepted scales are reported as secondary evidence for H1/H2; other scales are reported as
  exploratory only.
- **Convergent validity of C_s**: Spearman between C_s and judge fidelity over all judged items is reported. If it
  is below 0.30, the thesis states that keyword consistency does not track judged school fidelity and gives the
  judge results equal weight in the discussion of RQ1.
- Comparisons C vs B, C vs A, B vs A per school and scale: paired permutation tests, Holm correction across all
  judge comparisons (secondary family).
