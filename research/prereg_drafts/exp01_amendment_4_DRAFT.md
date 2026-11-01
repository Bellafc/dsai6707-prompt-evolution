# exp01 — Amendment 4 (DRAFT, 2026-10-31): new base model and retrained adapters

Status: **DRAFT** (decisions D7 and D11). It becomes binding when the author moves it to
`prereg/exp01_amendment_4.md`, adds it to `prereg` in `configs/exp01.toml` and commits, which must happen before
any arm A, B or C output on the new base model is generated for the test split (including `mosaic pregen`) and
before `mosaic freeze`. Dev runs before that date only serve to tune arm B and are logged as such.

## Why

The Confirmation's LoRA adapters (on Qwen2.5-7B-Instruct) were not kept. Arm C must be retrained in any case, so
the base model is chosen again now, before any output of a new base model exists.

## Change 1: base model

Arms A, B and C use **`Qwen/Qwen3-8B`** (post-trained, Apache-2.0, released 2025-04-29; Hugging Face revision
pinned at freeze), in **non-thinking mode** (chat template `enable_thinking = false`) in both training and
inference, so the trained `[Think] → [ToolCall] → [Observe] → [Output]` trace is the only reasoning the model
writes. Reasons:

1. Public sparse autoencoders exist for every layer of Qwen3-8B (Qwen-Scope, 2026), which exp06 needs. Qwen3.8 has
   none.
2. Released 2025-04-29: exp03 keeps a leakage-free history from 2025-05 (about 18 months of resolved markets).
   A 2026 base would leave about 8 months (Qwen3.5) or none (Qwen3.8).
3. Standard dense architecture with mature LoRA tooling (PEFT training, vLLM multi-LoRA serving).
4. Same size class as the Confirmation's model, so the change is one model generation, not a change of scale.
   Scale is studied separately in exp01b (Qwen3.5-27B).

## Change 2: arm C is retrained (`mosaic train`)

One LoRA adapter per school, trained once, never tuned on dev or test:

| Setting | Value | Note |
|---|---|---|
| Data | the 500 trajectories per school of the Confirmation, minus exclusions from Change 6 | if unavailable, Change 5 |
| LoRA | r = 32, α = 64, dropout 0.05, all linear projections of the attention and MLP blocks | r and α as the Confirmation |
| Precision | bf16 weights | the Confirmation used 4-bit NF4 (QLoRA) on a < 24 GB card; bf16 drops the quantisation step and matches exp01b, where 4-bit training is not recommended for Qwen3.5 |
| Schedule | 3 epochs; learning rate 2e-4, cosine decay, 3% warm-up; effective batch 16; max length 4,096 tokens | 3 epochs as the Confirmation; the other values were not reported there and are fixed here |
| Loss | assistant tokens only | |
| Seed | 20261030 | |

`mosaic freeze` records the SHA-256 of every adapter file, and the generation cache key includes them, so outputs
of an earlier adapter can never be reused for a retrained one.

## Change 3: arm B may use the model's own reasoning mode

Qwen3-8B has a native thinking mode, a stronger form of chain-of-thought than the written CoT the Confirmation
compared against. To keep B the strongest prompting baseline, B's tuning space adds `enable_thinking ∈ {false,
true}`, inside the existing budget of 12 configurations on dev. With thinking on, the model may use up to 4,096
thinking tokens in addition to the 2,048-token answer; keyword metrics, the judge and exp06 score only the answer
after `</think>`; thinking length is reported. All other sampling settings are unchanged.

## Change 4 (optional, descriptive): reproduce the Confirmation

If the original trajectories are available, two extra arms are run on the same 96 test events: **A7** =
Qwen2.5-7B-Instruct with arm A's messages, and **C7** = Qwen2.5-7B-Instruct with adapters retrained with the
Confirmation's own recipe (4-bit NF4, r = 32, α = 64, 3 epochs; unreported settings as in Change 2). Their
metrics are compared with Confirmation Table 4.3, descriptively (no hypothesis). This links Chapter 4 to the
Confirmation report and replaces the Task 0 parity check that needed the lost adapters.

## Change 5: the original trajectories are not available (decision D11; revised 2026-11-01)

The Confirmation's 1,500 GPT-4o trajectories were not kept, so they are regenerated with teacher prompt version 5
(`src/mosaic/teacher.py`, pilots and reviews in `research/teacher_pilot/`):

- **Items**: 500 per school (seed 0, items version 4), each an abstract event from 107 templates in the 14 categories
  of Confirmation Sec. 4.2.1 (reconstructed wording, `configs/teacher/templates.toml`) with random slot values and a
  random, internally consistent US/global backdrop. No real 2023–2026 event is described.
- **Tools**: the teacher works as the agent with two tools executed by the harness (`src/mosaic/tools.py`):
  `get_macro_data` returns the item's backdrop, `query_episode_db` returns episodes dated before 2025 from the stand-in
  table `configs/tools/episodes_standin.toml` (checked by the author before the run). The teacher writes no tool result.
- **Teacher** (fixed by the author before the full run): ☐ `qwen3.8-max` through the Alibaba Cloud token plan, only
  if the plan's terms allow using outputs to train models (Model Studio's service-specific terms limit content from
  *trial* use to evaluating the model); ☐ otherwise an open-weight model served on a pod, e.g. Qwen3.8-27B
  (Apache-2.0) or Qwen3.8-Flash-Next (qwen-community licence, training on outputs allowed). Claude models are excluded
  (Consumer Terms §3.2). Arm T denotes the teacher chosen.
- **Filters fixed before generation** (`teacher.check_v4` for prompt version 5): the protocol (episode tool, then
  macro tool, then the answer, one call each); tool results identical on re-execution; the Confirmation markers in
  order; 2–4 scenario probabilities summing to 1; six signals with conviction and reason; leakage (no date after
  April 2025); no other school named; no echoed instruction phrase; a [Proof] of 4–8 steps typed L1/L2/L3/L5 whose
  L1/L2 refs were returned by the tools and whose L5 step names the most likely scenario; a confidence line. A
  deterministic format normalisation (conviction form, scenario layout) runs before the filters; wording is untouched.
- **Formats**: each kept conversation gives (a) the single-pass text in the Confirmation's format (tool calls and
  results inline, [Proof] dropped, arm-A system and user messages with the event's macro context), on which **arm C is
  trained**, and (b) the multi-turn agent conversation used for the C-agent of exp03 and exp07 (not part of exp01).

The thesis states that the Confirmation's training data could not be reused, and Change 4 is dropped.

## Change 6: seed-episode audit (needed by exp03)

The same adapters forecast in exp03. Trajectories whose seed episode is dated after 2025-04-30 are removed before
training, because they could carry information from exp03's calibration window. The number removed per school is
reported. With the regenerated data of Change 5 the items are synthetic and the returned episodes end in 2024, so
the audit checks that no trajectory names a date after April 2025 (the leakage filter) and reports zero removals
unless that check fails.

## Unchanged

The 96 test events, metrics, hypotheses H1–H4 and their interpretation rules, arm D (Claude Opus 5.5) and
amendments 1–3. Arm D's pre-generated outputs stay valid: its messages do not depend on the base model.

## Consequences elsewhere

exp03 uses the Qwen3-8B adapters and its calibration window starts on 2025-05-01; exp01b moves from Qwen3.8-27B to
Qwen3.5-27B, which has a public SAE; exp06 analyses arms A, B and C with SAEs.
