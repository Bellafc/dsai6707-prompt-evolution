# Research log (append-only)

### 2026-10-31 — environment created
- change: harness `src/mosaic`, prereg exp01, program.md, RunPod setup.
- state: offline tests pass (fake backend). No real model run yet.
- next: Task 0 on the pod.

## For the human
- Restore the original Confirmation prompts into `configs/prompts/` (remove the `<<PLACEHOLDER` line) and the
  original keyword lists into `configs/lexicons.toml` (remove `PROVISIONAL`).
- Put the Confirmation's saved generations (if they exist) in `data/legacy/{base,sft}_{school}.jsonl` for the
  parity check.

### 2026-10-31 — design: new base model, SAE experiment (exp06), first-day spikes
- change: the Confirmation's Qwen2.5 adapters were not kept → base model Qwen3-8B, adapters retrained
  (`research/prereg_drafts/exp01_amendment_4_DRAFT.md`); exp06 SAE draft; exp01b moves to Qwen3.5-27B (public
  SAE); exp03 calibration window starts 2025-05-01; program.md gains Task S (spikes without assets) and Task 5
  (exp06); the vLLM cache key now covers chat-template options and the adapter files; `mosaic freeze` records the
  adapter files.
- state: 27 offline tests pass. No real model run yet.
- next: Task S on the pod.

## For the human (2026-10-31)
- 請確認 Confirmation 的 1,500 條 GPT-4o 訓練軌跡、96 個 test 事件、dev 事件、原始 prompt、關鍵字表還在不在；
  在的話上傳到 pod 的 `data/` 和 `configs/`（格式見 `data/README.md`，軌跡最好附 seed episode 與日期）。
  軌跡如果不見了，請決定 D11（用哪個老師模型重產）。
- 讀過修正案 4 草稿後，把它移到 `prereg/exp01_amendment_4.md`，加進 `configs/exp01.toml` 的 `prereg` 清單並
  commit；必須在任何 A/B/C 的 test 輸出（含 pregen）之前。
- D7（Qwen3-8B 主力 + Qwen3.5-27B 前沿）確認後，把 `research/backlog.md` 的 `train` 列狀態改成 `go`。
- D10：exp06 做 Part I+II（預設）還是只做 Part I。

### 2026-10-31 — infra: orchestrated RunPod workflow
- change: `mosaic pod list|get|create|stop|start|terminate|volumes|volume-create` (RunPod REST, standard library;
  no key in code: network secret on the Claude Code environment, RunPod secrets for the pod's tokens);
  `scripts/pod_bootstrap.sh` (setup → one agent session for `$MOSAIC_TASK` under a hard time limit → push to an
  `agent/...` branch → stop the pod; task `H` = a pod for the human); `ops/ORCHESTRATOR.md`; program.md rule 8.
- state: 32 offline tests pass. Not yet tried against the real RunPod API (first `pod create` = Task S).
- next: the human does the one-time setup in `ops/ORCHESTRATOR.md`, then the orchestrator starts Task S.

## For the human (2026-10-31, RunPod)
- 一次性設定照 `ops/ORCHESTRATOR.md` 最後一節做；RunPod API key 只放在 Claude Code 環境的 network secret。
- pod 上的 agent 只能跑 `.claude/settings.json` 允許的指令。Task S4（Qwen3.5-27B 要 transformers ≥ 5）如果需要第二個
  venv，請自己在 allow 清單加上 `"Bash(uv venv *)"`；否則 agent 會記下來請你處理。

### 2026-10-31 — docs: archive of the claude.ai Project
- change: everything from the claude.ai Project "PolyU" copied into the repository: `docs/project/` (Confirmation
  report PDF, 30-slide HTML deck, "Why PhD" statement, Bella's PQE survey source, `PROJECT_NOTES.md` with the
  panel, reviewer fixes, framing guidance and an index of earlier chats) and `research/DESIGN_DOC_zh.md`
  (snapshot of the Chinese design document, rev 38). Pointers added to README, CLAUDE.md and THESIS_DESIGN.
- state: from now on work continues in Claude Code on this repository; THESIS_DESIGN.md remains the source of truth.

- decision (human): the Confirmation LaTeX source and slides are not kept; the thesis and new slides are written
  from scratch, with the report's content taken from `docs/project/confirmation/jft_confirmation_final.{pdf,txt}`.

### 2026-10-31 05:29 UTC — infra: first orchestrated pod (Task 2)
- change: `src/mosaic/runpod.py` sends an explicit User-Agent (Cloudflare blocked urllib's default, error 1010).
- pod start: `4px2qrufhfwxzj` (mosaic-2-20261031-0529), task 2 (exp03 data build), NVIDIA A40, $0.59/h,
  `--hours 2`, no network volume (200 GB pod volume), push branch `agent/task-2-20261031-0529`.
- why task 2 first: cheapest useful smoke test of the RunPod secrets and bootstrap; Task S (80 GB) follows once
  a network volume exists.

### 2026-10-31 08:27 UTC — infra: network volume and Task S pod (parallel with Task 2, human OK)
- volume: `dy1ct9hkm0` (mosaic-volume, 200 GB, CA-MTL-1; chosen from RunPod's public stock data: H100 80GB
  and A40 High in the same data center).
- pod start: `3wiqxmzq8f05mg` (mosaic-S-20261031-0827), task S, NVIDIA H100 80GB HBM3, $3.99/h, `--hours 4`,
  volume `dy1ct9hkm0`, push branch `agent/task-S-20261031-0827`. Started with `--allow-parallel` because the
  human allowed it while the Task 2 pod (`4px2qrufhfwxzj`) was still running past its expected end.

### 2026-10-31 08:51 UTC — infra: Task 2 pod stopped by the orchestrator
- pod stop: `4px2qrufhfwxzj` (task 2, A40) stopped at 08:51 UTC, 3 h 21 min after creation (≈ $2.0), still RUNNING
  well past its 2 h limit plus setup; no `agent/task-2-20261031-0529` branch was pushed.
- state: unknown from outside (REST shows no logs). Commits, if any, stay in `/workspace/polyu` on the pod's own
  200 GB volume (stopped, not terminated). Possible causes: slow setup, the session not ending, or a failed push.
- next: the human reads the pod's Logs in the RunPod console (`[bootstrap ...]` lines); then decide whether to
  start it again to push, or terminate it.

### 2026-10-31 13:42 UTC — infra: Task S pod stopped; root cause of both stuck pods
- pod stop: `3wiqxmzq8f05mg` (task S, H100, $3.99/h) stopped at 13:42 UTC after 5 h 15 min (≈ $21), no branch.
- cause (from the pod's container log, read by the human): setup finished (models downloaded, 32 tests pass,
  `claude` logged in with the oauth token, vLLM importable), then `setup/runpod_setup.sh` printed its closing
  message through an unquoted heredoc. Its backticks ran `mosaic train` (error) and `claude setup-token`, which
  waited for interactive input forever. Neither pod (task 2, task S) ever reached its agent session; the RunPod
  secrets and the bootstrap's secret checks worked.
- fix: quoted heredoc, setup runs with stdin from /dev/null, regression test over all pod shell scripts
  (`tests/test_runpod.py`); 33 offline tests pass.
- next: pods clone `main`, so the fix must be merged (or pods started with `--branch`) before the next pod.
  Models and the venv are cached on volume `dy1ct9hkm0`, so the next setup is short.

### 2026-10-31 14:02 UTC — infra: Task S pod restarted with the setup fix
- pod start: `phe3hfe0mapatt` (mosaic-S-20261031-1402), task S, NVIDIA H100 80GB HBM3, $3.99/h, `--hours 4`,
  volume `dy1ct9hkm0` (CA-MTL-1), checks out `claude/vibrant-tesla-rqvzo1` (the fix is not on `main` yet; human
  chose this over waiting for the merge), push branch `agent/task-S-20261031-1402`.

### 2026-10-31 14:16 UTC — infra: idle-proof pods; why the pod agent could not work
- pod `phe3hfe0mapatt` (14:02, `--branch` build): setup 2 min, agent session 14:04:47–14:05:41, push to
  `agent/task-S-20261031-1402` and self-stop all worked. The agent (logged there) was denied every Bash call
  ("This command requires approval"), even `nvidia-smi`, `python -m pytest`, `git add`, which are on the allow
  list of `.claude/settings.json`, and stopped. `claude -p` silently ignores settings files that fail
  validation, so the project's allow and deny rules were probably never applied on the pods.
- pod `x5vqzpo13npvwy` (14:16, `main`, $3.99/h): first heartbeat 14:16:40; agent session ended after 2 s with
  status 1 (the human's subscription hit its usage limit then), pushed `agent/task-S-20261031-1416` (no
  changes) and stopped itself at 14:18. Cost ≈ $0.15.
- merged #1 (setup heredoc fix), #2 (log heartbeat to `agent/log-<pod>`), #3 (setup timeout 90 min, lifetime
  watchdog at `--hours` + 2 h); the orchestrator now merges its own PRs (ORCHESTRATOR.md rule 4).
- fix (this PR): `scripts/autoresearch.sh` passes the allow and deny rules of `.claude/settings.json` to
  `claude -p` as `--allowedTools` / `--disallowedTools` (both rule spellings, `src/mosaic/runpod.py`
  `permission_flags`), so they apply whether or not the project file is read; 36 offline tests pass.

### 2026-10-31 19:45 UTC — S1: Qwen3-8B serving, non-thinking (pod `agent/task-S-20261031-1820`, H100 80GB)
- hypothesis: `VLLMBackend` with `chat_template_kwargs = {enable_thinking = false}` serves Qwen3-8B with no `<think>` block.
- change: new `src/mosaic/spikes.py` + `mosaic spike env|dummy|serve` (dummy events/trajectories under `scratch/`, public
  text only); `mosaic train` and `tests/test_train_format.py` (S2, below). Env: torch 2.13.0+cu130, vllm 0.32.0,
  transformers 5.19.0, peft 0.21.2, trl 1.17.1; no bitsandbytes, no flash_attn.
- command: `python -m mosaic spike serve --tag S1` (3 dummy events × 3 school prompts = 9 requests, max_tokens 1024)
- result: 0/9 outputs with a `<think>` block or reasoning field; 8,191 completion tokens in 12.0 s = 680 tokens/s
  (9 concurrent requests, H100). Only 9/9 contain `[Output]` (plain prompt, no fine-tuning; not a quality claim).
  Cold start was slow: weights 32 s, torch.compile ~1 min, then a first-use FlashInfer sampling JIT build (nvcc,
  ~2 min); cached afterwards on the volume (`/root/.cache` — check if that is on the network volume).
  Outputs: `scratch/S1_outputs.jsonl`.
- decision: keep
- next: S2 smoke training (20 steps, 50 dummy trajectories) → serve the adapter as arm C.

### 2026-10-31 20:00 UTC — S2: `mosaic train` smoke test, adapter served as arm C
- hypothesis: LoRA SFT with the amendment 4 recipe (r 32, α 64, dropout .05, all-linear, bf16, lr 2e-4 cosine, 3% warm-up,
  effective batch 16, loss on assistant tokens only, Qwen3 chat template with enable_thinking=false) trains and the
  adapter loads in vLLM.
- change: `src/mosaic/train.py` + `mosaic train` (PEFT + transformers `Trainer`; TRL not used because masking is
  explicit: prompt = chat template with generation prompt, completion = reply + `<|im_end|>`, labels −100 on the
  prompt; examples over 4,096 tokens are dropped, not truncated). `tests/test_train_format.py` (5 tests, fake
  tokenizer): masking, prompt equal to inference prompt incl. empty think block, drop on overflow. Fixed on the
  way: transformers 5 has no `warmup_ratio` / `group_by_length` in `TrainingArguments` (warm-up steps computed).
  41 offline tests pass.
- command: `python -m mosaic train --school keynesian --data scratch/traj/keynesian.jsonl --out scratch/adapters/keynesian
  --max-steps 20`, then `python -m mosaic spike serve --adapters-dir scratch/adapters --tag S2C`
- result: 50 dummy trajectories (fake-backend format, `scratch/traj/`), 20 steps (micro-batch 4 × 4 accumulation) in
  29.2 s, peak 19.6 GiB, mean loss 0.539. vLLM served the adapter (`max_lora_rank` 32) on the 3 dummy events: 0
  `<think>` blocks, 3/3 outputs follow the trained dummy trajectory format (`[Think] … [ToolCall: query_episode_db]
  [Observe] …`), i.e. the adapter is applied. 124 tokens/s on 3 requests. Not a quality claim: dummy data.
  Real run size: 500 trajectories × 3 epochs = ~94 steps per school, roughly 2–3 min of training if lengths are similar
  (real trajectories are longer; estimate to be redone on real data).
- decision: keep
- next: S3 SAE reader check; S4 Qwen3.5-27B LoRA feasibility.

### 2026-10-31 20:35 UTC — S3: Qwen-Scope SAE reader check (early reading of gate S0, not the gate)
- hypothesis: the model-card TopK encoder (`topk(x W_enc^T + b_enc)`, decoder `a W_dec^T + b_dec`, hook = output of
  `model.model.layers[n]`) reconstructs the residual stream of Qwen3-8B-Base and, less well, of Qwen3-8B.
- change: `src/mosaic/sae.py` (loader, encode/decode, FVU, CE recovered, splice and mean-ablate hooks, `gate()`),
  `tests/test_sae.py` (3 offline tests on random tensors), `mosaic spike sae|hf-ls`. SAE `Qwen/SAE-Res-Qwen3-8B-Base-
  W64K-L0_50`, layers 9, 18, 27. Texts: first 200 paragraphs of 60–200 words from WikiText-103 test
  (`Salesforce/wikitext`), ≈ 29k tokens; position 0 excluded; for Qwen3-8B the paragraph is the assistant reply to
  "Write a short informative paragraph." in non-thinking chat format, scored on reply tokens only. Also compared the
  variant "subtract b_dec before encoding" ("center").
- command: `python -m mosaic spike sae --model Qwen/Qwen3-8B-Base --tag base_plain`; `… --model Qwen/Qwen3-8B --chat --tag chat`
- result (card formula; "center" was worse everywhere: FVU 0.28–1.14, so the card formula is the right one):

  | model | layer | FVU | CE clean | CE splice | CE mean-abl. | CE recovered |
  |---|---|---|---|---|---|---|
  | Base, plain | 9 | 0.255 | 2.44 | 5.81 | 8.99 | **0.49** |
  | Base, plain | 18 | 0.153 | 2.44 | 3.47 | 9.72 | 0.86 |
  | Base, plain | 27 | 0.262 | 2.44 | 2.86 | 8.20 | 0.93 |
  | Qwen3-8B, chat | 9 | 0.271 | 3.07 | 5.76 | 8.86 | **0.53** |
  | Qwen3-8B, chat | 18 | 0.322 | 3.07 | 4.89 | 8.65 | **0.67** |
  | Qwen3-8B, chat | 27 | 0.297 | 3.07 | 3.34 | 10.27 | 0.96 |

  Against the draft thresholds (FVU ≤ 0.40, CE recovered ≥ 0.80, FVU ≤ 1.5 × reader's): reader passes at layers 18
  and 27 and fails at 9 (CE recovered 0.49). Qwen3-8B (chat) passes only at layer 27; at 18 it fails on CE recovered
  (0.67) and on the relative FVU (0.32 > 1.5 × 0.153 = 0.23). Layer 9 fails CE in both: its FVU is fine, so either
  early layers are fragile to splicing or the layer-index convention is off by one there; not tested (only the
  three layers allowed). Caveats: one neutral corpus (Wikipedia), 200 paragraphs, no LoRA state, no school-specific
  text; the 0.80 threshold is not confirmed on school text. The splice result at layer 27 for the chat model is
  the one analysis layer that currently looks usable for all states.
- decision: keep (the reader works; exp06 Task 5 should expect to pick layers from {18, 27} plus layers ≠ 9, and
  check more layers in gate S0 proper. Draft threshold "3 layers ≥ 4 apart that pass for every state" may be
  impossible with layers 9/18/27 only.)
- next: S4 Qwen3.5-27B LoRA feasibility.

### 2026-10-31 22:35 UTC — S4: Qwen3.5-27B bf16 LoRA feasibility (evidence for D7)
- hypothesis: Qwen3.5-27B can be LoRA-trained in bf16 on one H100 80GB and its adapter served by vLLM.
- change: none to the recipe; `mosaic train --base Qwen/Qwen3.5-27B` unchanged (same venv: transformers 5.19 and
  vllm 0.32 coexist, so no second venv was needed). New: `mosaic spike serve --gpu-util --max-batched-tokens`,
  `VLLMBackend(engine_kwargs=…)` (not part of the cache key), `mosaic spike adapter-rename`.
- command: `python -m mosaic train --school keynesian --base Qwen/Qwen3.5-27B --data scratch/traj/keynesian.jsonl
  --out scratch/adapters27/keynesian --max-steps 50 --micro-batch 2`; then `mosaic spike serve --model Qwen/Qwen3.5-27B
  --adapters-dir … --gpu-util 0.85 --max-batched-tokens 4096`
- result:
  - Training works: 50 steps (micro-batch 2 × 8 accumulation = 16) on 50 dummy trajectories in 353 s, peak 56.5 GiB,
    loss 1.8 → 6e-6 (memorised: dummy data). `all-linear` also hit the Gated DeltaNet projections (`in_proj_qkv`,
    `in_proj_z`, `in_proj_a`, `in_proj_b`, `out_proj`) as well as q/k/v/o and the MLP. Adapter 992 tensors, fp32.
  - Serving needed three fixes. (1) Cold start of vLLM on this model: ~20 min in the model-registry inspection plus
    compile, before any weights load (cached afterwards, but under `/root/.cache`, i.e. probably not on the volume).
    (2) vLLM OOM at 0.90 and at 0.75 `gpu_memory_utilization` during CUDA-graph memory profiling (77 GiB allocated, so
    not the utilisation setting): fixed with `max_num_batched_tokens=4096`, `max_num_seqs=16`, util 0.85.
    (3) **Silent no-op adapter**: the adapter trained through `AutoModelForCausalLM` has keys
    `base_model.model.model.layers.*`; vLLM loads Qwen3.5 as `Qwen3_5ForConditionalGeneration`, whose text layers are
    `model.language_model.layers.*`. With the original keys vLLM ran its LoRA kernels without error but the outputs
    ignored the adapter (long free-text answers, 0/3 in the trained format). After renaming the keys
    (`mosaic spike adapter-rename`, 992/992 keys) the adapter is applied: 3/3 outputs in the trained format.
    Serving speed: ~98–110 tokens/s on 3 requests (not a throughput measurement).
  - Merged-weights fallback was not needed and not tested.
- decision: keep. D7 evidence: the 27B route is feasible on one 80 GB card; ~6 min for 50 steps at short sequences
  (real trajectories are longer; expect tens of minutes per adapter). Open risk to fix before exp01b: `mosaic train`
  should rename keys automatically (or load the multimodal class) and `mosaic doctor`/a post-train check should
  generate a few tokens through vLLM and compare with the base, because a silently ignored adapter looks like
  "fine-tuning has no effect".
- next: hand-off.

### 2026-10-31 22:40 UTC — S: Task S done
- READY FOR HUMAN: Task S done. All four spikes ran on the pod (H100 80GB, ~3 h of the 4 h limit, GPU generation/training
  time well under the 6 h budget). 44 offline tests pass. Raw outputs and logs are in `scratch/` (not versioned).

  | spike | result | note |
  |---|---|---|
  | S1 serving | pass | no `<think>`, 680 tokens/s at 9 concurrent requests |
  | S2 train | pass | 20 steps / 29 s / 19.6 GiB; adapter applied in vLLM |
  | S3 SAE | partial | reader passes layers 18, 27; Qwen3-8B chat passes only layer 27; layer 9 fails CE |
  | S4 27B | pass with fixes | key rename needed, OOM fix, 20-min cold start |

  Cost estimate for the remaining steps (H100 80GB at $3.99/h, from these timings; real data lengths unknown):
  - Task 0 (doctor, seed audit): CPU only, ~$0 once the assets arrive. A 48 GB card (A40 $0.59/h class) is enough for
    8B work: training peak 19.6 GiB (micro-batch 4), vLLM 8B ~16 GiB weights.
  - Three Qwen3-8B adapters: ~94 optimizer steps each at 500 trajectories × 3 epochs. At the dummy speed (1.5 s/step)
    that is minutes; with real 1–2k-token trajectories expect 15–30 min each → about $3–6 on an H100, less on a 48 GB card.
  - exp01 dev loop (Task 1): A, C and 12 B configurations × 40 events × 3 schools of generation; at ~700 tokens/s
    and ~1k tokens per answer, about 3 s per answer batch-amortised → roughly 1–2 GPU-hours ($4–8), plus 5 min vLLM cold start.
  - exp06 Task 5: gate S0 over the three states and every 4th layer needs activation passes (S3 took ~6 min per model
    for 3 layers × 2 encoders on 29k tokens); expect 2–4 GPU-hours on a 48 GB card.
  - exp01b 27B: per school adapter ~tens of minutes to ~1 h on an 80 GB card, plus the 20-min vLLM cold start each session.
- assets: not on the pod (`data/events/*.jsonl` missing in `mosaic doctor`). Task 2 (CPU + network) can go on a cheaper
  pod; the GPU is only needed again once events, trajectories (D11) and the `train` row `go` are there.

## For the human (2026-10-31, Task S)
- Prompts and lexicon: `mosaic doctor` says the originals are in place (no placeholder warnings) — thanks.
- Still missing: `data/events/{dev,test}.jsonl`, `data/trajectories/*.jsonl` (decision D11), `data/legacy/*` if it exists.
- D7: the 27B path works but needs the key rename above; I can add it to `mosaic train` in Task 0 if you want 27B adapters.
- exp06 draft, gate S0: with only layers 9/18/27 the rule "three layers ≥ 4 apart that pass for every state" is probably
  unsatisfiable (9 fails CE for reader and chat; 18 fails for chat). Proper S0 should scan every 4th layer, as the draft says;
  consider relaxing "passes for every state" or accepting layer 27 plus neighbours. Thresholds are yours to set at registration.
- Environment: vLLM/FlashInfer JIT caches live under `/root/.cache`; if that is not on the network volume, every new pod
  pays ~5 min (8B) to ~20 min (27B) of cold start. Consider `HF_HOME`/`VLLM_CACHE_ROOT`/`FLASHINFER_WORKSPACE_BASE` on the volume.
