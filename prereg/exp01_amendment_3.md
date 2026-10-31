# exp01 — Amendment 3 (2026-10-31): pre-generating untuned arms before the freeze

Registered before any arm D output exists. Changes when outputs are generated, not how they are scored.

## Change

Arms whose inputs are fixed by the registration (A, C, D, T: the school system prompt + user template, fixed
models, fixed sampling) may have their **test outputs generated before the freeze** with `mosaic pregen`
(human-gated). Arm B cannot: its configuration is tuned on dev.

## Safeguards

- Pre-generation writes only to the generation cache. It computes no score, writes no run and no results row;
  each pre-generation is logged in `locks/test_access.log` as "generation only, not scored".
- Nobody reads the pre-generated outputs before the freeze. The official final run (after `mosaic freeze`) reads
  them back from the cache. The cache key is the exact model, message list and sampling settings, so any later
  change to a prompt, the model or the sampling forces a fresh generation instead of reusing a stale one.
- The original Confirmation prompts must be restored before pre-generation (the command refuses placeholders).

## Why

Arm D (Claude Opus 5.5) runs on the author's subscription with usage windows. Generating its 288 outputs early,
on a machine without a GPU, removes it from the critical path of the final run.

## Data-use restriction

Arm D outputs and judge scores are used for evaluation only. They are never used as training data for any model:
the Claude Consumer Terms (section 3, item 2) do not allow using the service to develop or train AI models.
