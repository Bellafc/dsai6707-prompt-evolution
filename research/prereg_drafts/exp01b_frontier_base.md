# DRAFT pre-registration — exp01b: Does the fine-tuning advantage survive a 2026 frontier base model?

Status: **DRAFT, P1**, decision D7. Go/no-go after a one-day feasibility spike (by 2026-11-20).

## Question

exp01 compares fine-tuning with prompting on Qwen2.5-7B (2024). A stronger 2026 base prompts better, so the gap
may shrink. Does LoRA school fine-tuning still beat the best few-shot prompting on **Qwen3.8-27B** (released
2026-08-14, Apache-2.0, dense 27B, hybrid Gated DeltaNet + gated attention)?

## Design

- Same 1,500 GPT-4o trajectories, same LoRA recipe (r = 32, α = 64, 3 epochs), same 96 test events, same arms
  A/B/C and metrics as exp01 (+ the judge). Only the base model changes, so the comparison isolates scale and
  generation of the base. **No new teacher**: Opus outputs may not be used to train models (Claude Consumer
  Terms §3.2), and changing teacher and student together would confound the comparison.
- Non-thinking mode, so the model's own hidden reasoning does not sit outside the trained `[Think]` format;
  sampling as exp01.
- Hypothesis (primary, as exp01 H1): C > B on consistency per school, Holm across schools. Interaction
  (secondary): the C − B gap on Qwen3.8-27B is smaller than on Qwen2.5-7B (reported with CI, no test claim).

## Not in exp03

Qwen3.8-27B's knowledge cutoff is unpublished and its pretraining very likely covers 2025–26 macro releases, so it
cannot be evaluated on exp03's historical window. Its forecasting is evaluated only prospectively (exp05).

## Feasibility spike (agent, ≤ 1 GPU-day, 80 GB card)

1. vLLM serves `Qwen/Qwen3.8-27B` with a LoRA adapter (max_lora_rank 32) in non-thinking mode.
2. PEFT/QLoRA (4-bit) trains 50 steps on 100 trajectories without errors on the Gated DeltaNet layers; record
   which modules LoRA targets and the memory used.
3. Report time and cost per adapter. Any failure → no-go, logged; the thesis keeps a 7B-only RQ1.
