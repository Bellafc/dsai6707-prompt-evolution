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

## Change 5: if the original trajectories are not available (decision D11)

Regenerate 500 trajectories per school from the same 117 seed episodes with the Confirmation's teacher prompts.
Teacher: GPT-4o if it is still offered, otherwise an open-weight model whose licence (Apache-2.0 or MIT) allows
training on its outputs. Claude models are excluded (Consumer Terms §3.2). Fixed before generation: format
validity, a leakage filter (no date after 2025-04-30 and no event later than the seed episode), and a quality
filter chosen by the author. Arm T then denotes this teacher. The thesis states that the Confirmation's training
data could not be reused, and Change 4 is dropped.

## Change 6: seed-episode audit (needed by exp03)

The same adapters forecast in exp03. Trajectories whose seed episode is dated after 2025-04-30 are removed before
training, because they could carry information from exp03's calibration window. The number removed per school is
reported.

## Unchanged

The 96 test events, metrics, hypotheses H1–H4 and their interpretation rules, arm D (Claude Opus 5.5) and
amendments 1–3. Arm D's pre-generated outputs stay valid: its messages do not depend on the base model.

## Consequences elsewhere

exp03 uses the Qwen3-8B adapters and its calibration window starts on 2025-05-01; exp01b moves from Qwen3.8-27B to
Qwen3.5-27B, which has a public SAE; exp06 analyses arms A, B and C with SAEs.
