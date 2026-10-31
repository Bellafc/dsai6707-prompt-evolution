# exp01 — Amendment 1 (2026-10-31)

Registered before any arm B, D or test-split result existed (no model has been run with real weights yet).
The original registration (`exp01_prompt_vs_sft.md`) is unchanged; this amendment takes precedence where they differ.

## Change

- **Arm D** is now **Claude Opus 5.5** (`claude-opus-5-5`), called through Claude Code in headless mode
  (`claude -p`) on the author's own subscription. It receives exactly the same [system, user] messages as A and C:
  the CLI's default system prompt is replaced in full, all tools and MCP servers are disabled, project
  customizations are not loaded, one turn, nothing persisted.
- **Arm T** (optional) is GPT-4o, the teacher model that generated the SFT trajectories, with the original
  sampling settings. It is run only if an API key and budget are available.

## Why

Cost: the subscription covers D. Role: D is now a **frontier-model reference** (how far a current top model is
from the 7B adapters), not the teacher. The question "why not use the teacher directly?" is answered only by T;
if T is not run, the thesis says so.

## Deviations this introduces (reported with the results)

1. **Sampling**: the CLI exposes no temperature or top-p, so D uses the model's defaults with reasoning effort
   fixed at `medium` for every call. D therefore does not share A/B/C's sampling settings; D vs C comparisons
   are descriptive (CIs reported, no hypothesis attached), as already specified for D.
2. **Knowledge cutoff**: Opus 5.5 is much newer than Qwen2.5. The 96 test events are synthetic, so this does not
   create leakage in exp01, but it matters for exp05 and is noted there.
3. **Usage limits**: calls may pause on subscription usage windows. Responses are cached per call and the run
   resumes; the final D run may span several sessions. Partial runs are not reported.

Hypotheses H1–H4 and the decision rules are unchanged (they involve A, B and C only).
