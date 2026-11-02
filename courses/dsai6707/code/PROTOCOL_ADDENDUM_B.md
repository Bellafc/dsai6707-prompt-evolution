# Protocol addendum B: second-model replication on Claude Haiku 5.5 (fixed before the replication run)

Written 2026-11-02, after a smoke test (below) and before any run whose results enter the report. `PROTOCOL.md` and
`PROTOCOL_ADDENDUM_A.md` apply unchanged unless stated here.

## Why
All main results come from one model (`qwen3.8-max`). A second model from another provider tests whether the
search-level pattern (Section 5.1 of the report) and the held-out pattern (Section 5.2) depend on that model.

## Model and sampling
- `claude-haiku-5-5` through the official Anthropic SDK (`evo_prompt.backend.AnthropicBackend`, `--profile haiku`).
- The model rejects non-default temperature and top-p, so its default sampling is used (qwen: 0.7 / 0.9). Thinking is
  disabled, as for qwen; `max_tokens` 1,024, as for qwen. The API has no sampling seed; the seed stays in the cache key
  so each seed draws independent samples. Raw outputs are therefore cached but not reproducible bit for bit.
- Prices for the ledger: USD 0.10 / 0.50 per million input / output tokens (Anthropic list price).
- Everything is written under `results/haiku/` (own cache, runs, best prompts, tables and figures).

## Design
- Arms: `b0`, `nsga2`, `ga`, `random`, `nsga2_rule`, `ga_rule`, `nsga2_llmu` (all seven, same code and operators).
- Population 6, 4 generations, same search and held-out events, same knee rule.
- **Seeds 1 to 5** (qwen: 1 to 3), because the model is cheap. With five paired seeds the smallest one-sided sign-flip
  p-value is 1/32, so search-level comparisons get an exact sign-flip p-value in addition to the description.
- The LLM edit acceptance rule (5 to 120 words, else rule mutation) is **not** changed for this model. In the smoke test
  (1 seed, population 4, 1 generation, 2 search events; outputs not used) both LLM edits were rejected because Haiku
  returned 139 and 168 words. The rejection rate is reported per method; if most LLM edits are rejected, the Haiku
  replication says little about LLM mutation, and the report says so.

## Analysis
- Same tables as for qwen: search-level hypervolume and knee metrics (mean ± sd over 5 seeds), Q1 to Q3 of addendum A
  with per-seed differences and the exact one-sided sign-flip p-value over 5 seeds (descriptive, no correction),
  held-out tests against B0 (12 tests, Holm over 12) and the protocol family (42 tests, Holm over 42), sensitivity
  without `syn-k0007`.
- Cross-model reading: for each finding of the qwen study, the report states whether Haiku agrees in direction. No test
  pools the two models.

## Cost control and execution
- `python -m evo_prompt.runner --profile haiku --methods b0 nsga2 ga random nsga2_rule ga_rule nsga2_llmu --seeds 1 2 3 4 5 --gens 4 --pop 6 --heldout --budget 15`
- Estimated cost about USD 4 (smoke test: USD 0.0006 per call); the ledger cap is USD 15 (the owner's limit is 100).
  If the cap stops the run, unfinished arms are reported as incomplete.
- The API key is read from `ANTHROPIC_API_KEY` in the environment and is not written to any file in the repository.
