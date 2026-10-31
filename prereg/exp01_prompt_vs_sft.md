# Pre-registration — exp01: Fine-tuning vs. prompting (CoT) for school-specific reasoning

Registered: 2026-10-31 (this file's first commit is the registration record). Version 1.
Do not edit after registration. To change anything, add `exp01b_*.md` with a new date and say why.

## Question

At the Confirmation of Registration the panel asked why the school agents are fine-tuned instead of prompted with
chain-of-thought. The Confirmation compared LoRA SFT against the same Qwen2.5-7B-Instruct with a school-specific
system prompt and the same output format (zero-shot CoT, arm A). It did not compare against the strongest
prompting baseline (few-shot CoT with the school's own reasoning examples) or against the teacher model.

## Arms (all on the same events, same sampling: T = 0.7, top-p 0.9, max 2048 tokens, fixed seed)

| Arm | Model | Prompt |
|---|---|---|
| A | Qwen2.5-7B-Instruct | school system prompt + user template (= Confirmation "base") |
| B | Qwen2.5-7B-Instruct | A + k exemplar trajectories from that school's SFT corpus (k, selection, truncation and optional extra school guidance tuned on dev only) |
| C | Qwen2.5-7B-Instruct + school LoRA (r = 32) | same messages as A |
| D | GPT-4o (the teacher) | same messages as A |

## Data

- **test**: the 96 held-out events of the Confirmation (Sec. 4.2.1; medium 42, hard 47, very hard 7). Touched once,
  after `mosaic freeze`, by a human, for all four arms.
- **dev**: events disjoint from test (recommended: historical episodes from the episode database), used only to
  tune arm B and to debug. Exemplars are never drawn from the same template as the event.

## Metrics (definitions as in the Confirmation, Sec. 4.2.3; frozen in `src/mosaic/metrics.py`)

Consistency C_s (Eq. 4.1), contamination (anti-signal hits), structural completeness (7 elements), inter-school
diversity (Eq. 4.2). Keyword lists are the Confirmation's original lists (Task 0 parity check passed before freeze).

## Hypotheses and decision rules (written before any arm B or D result)

- **H1 (primary)**: C > B on consistency, per school. Paired sign-flip permutation test over the 96 events,
  Holm correction across the three schools, α = 0.05.
- **H2**: C < B on contamination for at least two of three schools (same test, unadjusted, reported as secondary).
- **H3**: C ≥ B on `[Output]` presence; reported descriptively with 95% bootstrap CIs.
- **H4**: diversity(C) > diversity(B), paired over events.
- **D** is a reference, not a hypothesis: we report C vs D and A vs D with CIs.

Interpretation, fixed in advance:

1. H1 holds for ≥ 2 schools → fine-tuning adds school fidelity beyond the best prompting baseline.
2. H1 fails (C ≈ B) → the thesis argues for SFT on cost, latency, reproducibility and control of the knowledge
   cutoff, not on fidelity, and says so.
3. B > C significantly for ≥ 2 schools → reported as a negative result; Stage 2 is re-examined.

Keyword metrics measure school fidelity, not forecasting accuracy. Forecasting quality (Brier, calibration,
coherence on resolved macro markets) is exp03 and is not claimed here.

## Tuning budget for arm B (fairness)

At most 12 distinct B configurations evaluated on dev (≤ 40 events each). Allowed knobs: k ∈ {1, 2, 3, 5},
strategy ∈ {random, category}, max_chars, extra school guidance text. The chosen configuration and every
configuration tried are listed in `research/exp01_dev_summary.md` before freeze.
