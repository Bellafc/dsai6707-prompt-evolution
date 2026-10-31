# DRAFT pre-registration — exp01b: Does the fine-tuning advantage survive a stronger 2026 base model?

Status: **DRAFT, P1**, decision D7. Go/no-go after the feasibility spike (program.md Task S4, by 2026-11-20).
Revised 2026-10-31: the frontier base is **Qwen3.5-27B** (was Qwen3.8-27B), because it is the only 2026 model with
public sparse autoencoders, trained on the post-trained model itself, so exp06 can be replicated at this scale.

## Question

exp01 compares fine-tuning with prompting on Qwen3-8B (2025). A stronger 2026 base prompts better, so the gap may
shrink. Does LoRA school fine-tuning still beat the best prompting baseline on **`Qwen/Qwen3.5-27B`** (released
2026-02-24, Apache-2.0, dense 27B, 64 layers, hybrid: three in four layers use Gated DeltaNet linear attention,
the rest full attention; a unified vision-language model, used text-only)? And do exp06's mechanism findings hold with an SAE trained on the very
model that is fine-tuned (`Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50` / `_L0_100`, all 64 layers)?

## Design

- Same trajectories, same LoRA recipe as exp01 amendment 4 (r = 32, α = 64, bf16, 3 epochs; 4-bit training is
  not recommended for Qwen3.5), same 96 test events, same arms A/B/C (B with the same tuning budget, including the
  thinking switch) and metrics (+ the judge on the amendment-2 subset if the subscription allows). Only the base
  model changes. **No new teacher**: Opus outputs may not train models (Claude Consumer Terms §3.2), and changing
  teacher and student together would confound the comparison.
- Non-thinking mode for A and C, as in exp01.
- Hypothesis (primary, as exp01 H1): C > B on consistency per school, Holm across schools. Interaction
  (secondary): the C − B gap on Qwen3.5-27B is smaller than on Qwen3-8B (reported with CI, no test claim).
- exp06 Parts I–II repeated on these arms with the 27B SAE (exploratory replication).

## Forecasting (exp03)

Qwen3.5-27B was released on 2026-02-24, so only exp03 test events resolving on or after **2026-03-01** are
outside its training data. It enters exp03 only as a secondary, descriptive analysis on that subset (if go), and
exp05 prospectively.

## Other 2026 models considered (2026-10-31)

| Model | Why not the exp01b base |
|---|---|
| Qwen3.6-27B (2026-04-22), Qwen3.8-27B (2026-08) | newer, but no public SAE; Qwen3.8 leaves no historical forecasting window |
| Gemma 4 31B (Google, 2026-03-31, Apache-2.0, dense 30.7B, stated data cutoff January 2025) | strongest non-Qwen model on one 80 GB card, but no public SAE (Gemma Scope 2 covers Gemma 3 only); bf16 LoRA does not fit 80 GB. Optional P2: a cross-family behavioural check of H1 (no SAE), only if time remains |
| gpt-oss-20b / 120b (OpenAI, MoE) | MoE (LoRA and SAE work are harder to interpret); 120b does not fit one card for training |
| GLM-5.x, DeepSeek, Kimi, MiniMax, Nemotron 3 Ultra | far too large for one card |

## Feasibility spike (agent, program.md Task S4, ≤ 1 GPU-day, 80 GB card)

1. PEFT bf16 LoRA trains 50 steps on dummy trajectories without errors on the Gated DeltaNet layers
   (transformers ≥ 5; second venv if vLLM's pin clashes); record which modules LoRA targets and peak memory
   (≈ 56 GB expected).
2. vLLM (≥ 0.17) serves `Qwen/Qwen3.5-27B` with the adapter (max_lora_rank 32) in non-thinking mode; fallback:
   merged bf16 weights per school, served one at a time.
3. Qwen-Scope layer file loads; FVU of the 27B SAE on 50 public paragraphs (sanity check of the encoder).
4. Report time and cost per adapter. Any blocking failure → no-go, logged; the thesis keeps an 8B-only RQ1.
