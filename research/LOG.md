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

### 2026-10-31 (pod session, Task 2) — exp03: ground-truth fetchers and ALFRED contexts, first network contact
- hypothesis: pmpol's politics fetchers extend to macro markets with small changes.
- change: `src/mosaic/exp03_gt.py` (Kalshi Economics/Financials + Polymarket economy tag, scope filter, flat
  records with strikes/rules/prices at 1, 7, 30 days before close), `src/mosaic/exp03_context.py` (ALFRED as-of
  fetch, 12 vintages per request, cache), `configs/exp03_indicators.toml` (the 35-indicator panel),
  `python -m mosaic exp03 fetch|vintages`, tests `tests/test_exp03_gt.py`, `tests/test_exp03_context.py`
  (43 offline tests pass). `python -m mosaic vendor` extracted the archive; EXPORT_NOTES.md read (team code; its
  rules: research only, tests offline, platform text not redistributed).
- command: `python -m mosaic exp03 fetch --venue kalshi`; `python -m mosaic exp03 vintages --series UNRATE ...`
- result: (1) Kalshi: 235 in-scope series by title; the run was stopped by **HTTP 429** after 53 markets (pmpol's
  0.06 s pause is too fast for the historical candle endpoint). Per rule 10 no retry in the same run; pause raised
  to 0.6 s, scope narrowed (other countries' GDP/unemployment/CPI and CPI sub-indices excluded), file is resumable.
  (2) ALFRED works keyless: UNRATE as of 2025-09-04 ends at July (August was published 09-05), as of 09-10 at August.
  (3) The "35 indicators" are not listed anywhere in the repository (the Confirmation names categories only): the
  panel in `configs/exp03_indicators.toml` is 25 ids mapped from the report's categories plus 10 guessed fillers.
- decision: keep; Kalshi fetch to be restarted once (slower), not in a loop.
- next: restart the Kalshi fetch slowly; Polymarket; scenario-set builder with tests.

### 2026-10-31 (pod session, Task 2) — exp03: data build, question set, contexts, runner, pilot
- hypothesis: the pmpol grids and labels map Kalshi/Polymarket macro markets to ordered scenario sets; the
  prompted and adapter systems can write per-bin probabilities in the required format.
- change: `src/mosaic/exp03_gt.py` (whitelist `KALSHI_SERIES`, pause 0.6 s), `exp03_questions.py` (pmpol spans →
  elementary bins, realised bin from contract results, market benchmark at 7 and 1 days, dedupe, windows, data
  card), `exp03_context.py` (`build_contexts`, `coverage`), `exp03_run.py` (prompt, `parse_bins`, RPS, log score,
  Brier, ECE, pools, pilot guarded to ≤ 10 calibration questions), `configs/exp03_prompts/neutral.txt` (school-
  neutral system prompt; `configs/prompts/` is write-denied, so it lives here), CLI `mosaic exp03
  fetch|build|contexts|card|pilot|vintages`. 62 offline tests pass.
- command: `exp03 fetch --venue kalshi|polymarket`, `exp03 build`, `exp03 contexts`, `exp03 card`,
  `exp03 pilot --limit 10 --systems "base,K',A',M',K,A,M"`
- run_ids: pilot `runs/exp03-pilot-20261031T194747Z` (10 calibration questions × 3 samples)
- result: (1) 3,757 Kalshi + Polymarket settled markets → **149 questions** (58 calibration, 91 test; counts per
  series in `research/exp03_data_card.md`), 405 excluded events (248 out of scope, 68 duplicate listings, 59 no
  partition, 30 labels pmpol does not read). Calibration is thin for central banks (BoE 2, ECB 1, BoC 1, RBA/BoJ/
  Banxico/SNB 0) and GDP (2): the primary pooled test rests on US CPI/core/unemployment/Fed. (2) HTTP 429 once
  (see above); no other refusals. Polymarket economy tag: 1,598 markets fetched. (3) Contexts: 298 rows (149 × 2
  horizons), all 35 series return data; **TEDRATE is 1,510 days stale** (discontinued 2022) and
  GFDEBTN/DRTSCILM/CSUSHPINSA are 99–192 days old (quarterly / lagged releases). (4) Pilot parse rates (3 samples ×
  10 events): base 0.93, K′ 1.00, A′ 0.93, M′ 0.93, no event without a valid sample. Adapters K, A, M: **not run,
  no adapters exist** (Task 0 `mosaic train` not done). The pilot used the placeholder `user_template.txt`, so
  numbers are not final. Nothing was scored on any window.
- decision: keep. Task 2 is complete except the adapter pilot; the registration needs the human decisions below.
- next: Task 0 (adapters), then rerun `exp03 pilot --systems K,A,M`.
- note: `pilot` reloads the vLLM engine per system and sample (~10 min each on the A40); acceptable for 10 events,
  but a final run should reuse one engine.

READY FOR HUMAN: register exp03 (draft `research/prereg_drafts/exp03_market_forecasting.md`), open questions:
1. The 35-indicator panel (25 mapped + 10 guessed ids; TEDRATE dead) — replace with the episode database's list.
2. Calibration is only 58 events (central banks 0–2 each): is the calibration window (2025-05 → 12) long enough to
   fit λ of pool-skill and the temperature of pool-cal, or should the window or the pooling of series change?
3. Kalshi's "Exactly x%" ladders (KXECONSTAT*) were excluded (no tails); the same releases are covered by the KX*
   ladders. Polymarket yielded few usable events (see card): keep as a secondary source or drop it?
4. Bin labels follow pmpol's grid (CPI 0.1 pp): bins are coarser than the grid where a ladder lacks a strike.
5. Scenario format "S1: 0.25" is new for the schools (trained on free-form scenario lists); the adapter pilot will
   show whether that costs format compliance.
6. `configs/exp03_prompts/neutral.txt` is my wording of the school-neutral arm-A style prompt: please review.

## For the human (2026-10-31, Task 2)
- 35 個 FRED 指標的確切清單不在 repo 裡（Confirmation 只寫類別）。`configs/exp03_indicators.toml` 前 25 個是我依類別
  對應的 FRED id，後 10 個（group = "filler"）是猜的。請對照 episode 資料庫匯出的欄位，換成真正的 id。

### 2026-10-31 18:20 UTC — infra: Task S and Task 2 in parallel (human: run autonomously, parallel OK)
- CA-MTL-1 (volume `dy1ct9hkm0`) had no H100 or A40 at 18:06, so both pods run without a network volume
  (200 GB pod volume each), in whatever data center RunPod picks; models are downloaded again.
- pod start: `ivotx555nzu8ir` (mosaic-S-20261031-1820), task S, NVIDIA H100 80GB HBM3, $3.99/h, `--hours 4`,
  push branch `agent/task-S-20261031-1820`.
- pod start: `7bthnznndpeuxu` (mosaic-2-20261031-1820), task 2, NVIDIA A40, $0.59/h, `--hours 6`,
  push branch `agent/task-2-20261031-1820`.
- permission flags of #4: confirmed through the heartbeats; both agents run their allowed commands (the few
  denials were `sed`, `python -c` and `ls` outside the repository, as intended).

### 2026-10-31 20:21 UTC — infra: Task 2 pod finished and stopped itself
- pod stop: `7bthnznndpeuxu` (task 2, A40, $0.59/h) ended its session at 20:21 UTC with READY FOR HUMAN:
  register exp03, pushed `agent/task-2-20261031-1820` and stopped itself; ≈ 2 h, ≈ $1.2.
- merged as #5 (orchestrator checks: 49 passed, 13 skipped for the pmpol archive, 0 failed; no measurement
  files touched).

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

### 2026-10-31 22:33 UTC — infra: Task S pod finished and stopped itself
- pod stop: `ivotx555nzu8ir` (task S, H100 80GB, $3.99/h) ended its session at 22:33 UTC with READY FOR HUMAN:
  Task S done, pushed `agent/task-S-20261031-1820` and stopped itself; ≈ 4 h 13 min, ≈ $17.
- merged as #7. The branch predated #5, so only the append-only LOG and AI-use ledger conflicted; both sides'
  entries were kept (orchestrator checks on the merged tree: 53 passed, 15 skipped, 0 failed; no measurement
  files touched).
- day total (all pods, 2026-10-31): ≈ $43 (two stuck pods before the heredoc fix ≈ $23, the 14:0x tests < $1,
  Task 2 ≈ $1.2, Task S ≈ $17), plus volume `dy1ct9hkm0` storage.

### 2026-11-01 — infra: teacher pipeline for the SFT trajectories (D11), Task T
- decision (human): regenerate the trajectories now, with the largest Qwen3.8 that runs. Qwen3.8-2.4T-A95B
  (~2.5 TB in FP8) does not fit any single RunPod pod, so the teacher is `Qwen/Qwen3.8-Flash-Next-FP8` (180B,
  licence qwen-community: research use and training on outputs allowed, no MAU/revenue thresholds reached), on
  2 × H200. A Claude teacher (Opus or Haiku 5.5) was asked for and declined by the orchestrator (Anthropic usage
  terms; THESIS_DESIGN §4a; amendment 4 Change 5 excludes Claude).
- change: `configs/teacher/templates.toml` (107 abstract event templates in the 14 categories of Confirmation
  Sec. 4.2.1, slot lists, school profiles: concepts, mechanisms, stance; the original templates were not kept, so
  this wording is a reconstruction for the human to review), `src/mosaic/teacher.py` (seeded items with random
  macro snapshots, teacher prompt, Change 5 filters: marker order, probabilities summing to 1, ≥ 4 signals, no date
  after April 2025; records in the data contract with the arm-A messages of inference plus the raw event),
  `mosaic teacher`, `mosaic pod create --gpu-count` and GPU class `141gb`, program.md Task T (pilot of 20 per school,
  then human review), `tests/test_teacher.py`; 57 offline tests pass.
- next: Task T pod (2 × H200, `--hours 3`).

## For the human (2026-11-01, teacher)
- 修正案 4 Change 5 寫的是「Apache-2.0 或 MIT」的老師；Qwen3.8-Flash-Next 是 qwen-community 授權（允許學術使用和拿輸出
  訓練），正式登記前請把 Change 5 改成實際使用的模型與授權。
- `configs/prompts/*.system.txt` 和 `user_template.txt` 仍是 PLACEHOLDER 版本。軌跡裡存了原始事件，換上原始 prompt
  後可以重組訊息，不必重新產生。
- 107 個事件模板和三個學派的設定是依開題報告第 4.2.1 節重建的，請在完整生成（每學派 500 條）前看一下
  `configs/teacher/templates.toml` 和試產樣本 `research/teacher_pilot/`。

### 2026-11-01 — infra: teacher run through a hosted API, by the human
- decision (human): no 2 × H200 pod for the teacher; the human runs it through a hosted OpenAI-compatible API on
  their own account (cheaper than renting GPUs for one batch), then commits the results.
- change: `scripts/teacher_api.py` (standard library only: writes the requests itself with `--n`, sends them with
  `--workers` in parallel, resumable, refuses Claude model ids), `mosaic teacher-export` / `teacher-import`
  (`export_jobs`, `import_results`: OpenAI Batch request format; replies validated with the same Change 5 filters,
  reasoning blocks stripped, Claude teachers refused). End-to-end checked against a local stub API; 59 offline
  tests pass.
- next: the human runs the pilot (`--n 20`) and commits `research/teacher_runs/pilot/{manifest.json,results.jsonl}`;
  the orchestrator imports, checks keep rates and writes the samples for review.

### 2026-11-01 — D11: teacher pilot through the hosted API (qwen3.8-max)
- command: `python3 scripts/teacher_api.py research/teacher_runs/pilot --n 20 --network-secret --base-url
  https://token-plan.maas.qianwenaiapi.com/compatible-mode/v1 --model qwen3.8-max --workers 16` (key from the
  environment's network secret), then `mosaic teacher-import --jobs research/teacher_runs/pilot --out
  data/trajectories/pilot`.
- fixes on the way: non-streamed requests were cut by a gateway after ~30 s (HTTP 502) and retried forever, so the
  runner now streams (#11); 3 of 60 streams were reset mid-reply and succeeded on the resumed re-run. The leakage
  filter rejected "before 2025" / "pre-2025", the boundary the teacher prompt itself asks for; it now ignores a 2025
  directly preceded by before / pre- / prior to / earlier than (test added). A later 2025 date is still rejected.
- result: 60/60 replies, ~2 min each with ~4,200 reasoning tokens (dropped); 59/60 kept (1 missing block marker);
  keynesian 19, austrian 20, monetarist 20. Every kept trajectory uses its own school's core terms and none uses the
  other schools' signature term (aggregate demand / malinvestment / money supply). Years ≥ 2023 appear only as the
  "before 2025" boundary or pre-2025 analogs. Tokens 38k in, 311k out (250k reasoning). Samples for review:
  `research/teacher_pilot/samples.md`.
- next: human review of the samples and the templates, then the full run (`--n 500`, ~1,500 requests).

### 2026-11-01 — infra: the orchestrator pushes with git (human decision)
- change: `Bash(git push*)` removed from the deny list of `.claude/settings.json`, so the orchestrator session pushes
  its branch directly (the GitHub API path cannot carry multi-megabyte files such as the full teacher run). Pods keep
  the rule through `runpod.POD_DENY`, passed by `scripts/autoresearch.sh` (`tests/test_runpod.py` checks it);
  ORCHESTRATOR.md rule 6.

### 2026-11-01 — D11: Opus review of the teacher pilot; teacher prompt version 2
- review: three Claude Opus 5.5 reviewers (evaluation only) scored the 59 kept pilot trajectories 1–5 on school
  fidelity, causal coherence, event responsiveness, output consistency, factual hygiene. Means K 3.8/3.4/3.2/3.5/3.7,
  A 4.1/3.5/3.3/2.9/3.8, M 4.5/3.9/3.7/3.6/3.4; all three verdicts "train with changes". Main problems: default
  bearish signals (equities SHORT 52/59, gold LONG 56/59) also for good news, checklist use of school concepts,
  backdrop numbers before get_macro_data, US backdrop for foreign events, templated scenarios, vague analogs,
  implausible backdrops. Summary and per-item scores: `research/teacher_pilot/opus_review.md`, `opus_review/*.json`.
- change: teacher prompt version 2 (table in opus_review.md): school diagnosis and good-news cases instead of
  must-use concepts, consistent US/global backdrop, tool-honest order, JSON tool arguments, dated analogs, signals
  with conviction and reason and no default direction, direction-share report per batch; manifests carry
  `prompt_version` and imports refuse a mismatch. 63 offline tests pass.
- next: pilot v2 (20 per school), same Opus review, compare.

### 2026-11-01 — D11: pilot v2 (teacher prompt version 2); prompt version 3, format normalisation
- command: `scripts/teacher_api.py research/teacher_runs/pilot-v2 --n 20 ... --model qwen3.8-max` (60/60 replies;
  60k tokens in, 414k out), `mosaic teacher-import`.
- result: 51/60 kept after normalisation (K 15, A 19, M 17). All 9 rejects skipped the second [Think] (the v2 rules
  named only the first and third). Signal diversity up: equities SHORT 30/51 (v1 52/59), gold LONG 34/51 (v1 56/59);
  remaining warnings (> 70 % one direction): Keynesian bonds LONG 12/15 and gold LONG 11/15, Austrian gold LONG
  15/19 and credit SHORT 14/19.
- change: prompt version 3 adds the rule for the second [Think]; `normalize()` rewrites "SHORT (2)" and
  "(conviction: 2)" to "(conviction 2)" on signal lines before validation (5 v2 replies had only that format slip;
  wording untouched); manifests carry `items_version` separately (imports rebuild items, so only the item generator
  must match; the record keeps the run's prompt version). 64 offline tests pass.
- next: Opus review of pilot v2 with the v1 rubric; the full run waits for the human's scope decision.

### 2026-11-01 — D11: Opus review of pilot v2
- result: same rubric, means v1 → v2: Keynesian 3.79/3.42/3.21/3.47/3.74 → 4.13/3.80/4.00/3.67/4.87, Austrian
  4.10/3.45/3.25/2.90/3.75 → 4.42/4.05/3.58/3.53/4.58, Monetarist 4.50/3.85/3.70/3.60/3.40 → 4.59/3.88/4.18/4.06/4.53;
  overall 3.61 → 4.12. Verdicts still "with changes". Remaining issues listed in research/teacher_pilot/opus_review.md
  (teacher-written tool results; signals that follow S1 only; templated probabilities; undefined asset referents;
  prompt echoes; backdrop skew; residual gold/bond defaults).
- decision needed (human): real tools (episode DB, ALFRED contexts) vs self-simulated tool calls; it shapes the
  trajectory format, exp01's inference and exp03. The full teacher run waits for this and the scope decision.

### 2026-11-01 — design note: fine-tuning vs ontology agent, agent training, three RQs
- change: `research/DESIGN_ontology_agents.md` §4a, a factorial design (prompted / fine-tuned / beyond SFT ×
  single pass / ontology agent with real tools and a proof) and the agent-training methods (agent SFT core,
  rejection-sampling fine-tuning recommended, multi-turn RL as stretch; rewards only from rules or realised
  outcomes, never from a Claude judgement; the exp03 test window never used). §2, three proposed RQs from the three
  interpretability angles: RQ1 inside the model (exp01, exp06, exp01b), RQ2 what the agent says (exp02 as the L2
  tool, new exp07 for proof validity, counterfactual tools and proof faithfulness), RQ3 how sure (exp03 with H8
  diversity sources, exp04, exp05). Decisions 7 (training depth) and 8 (adopt the RQs) added.
- decision needed (human): decisions 1–8 of the design note; THESIS_DESIGN stays unchanged until the author decides.

### 2026-11-01 — RQs adopted (three angles on one design)
- decision (human): the three RQs of `research/DESIGN_ontology_agents.md` §2 are adopted (decision 8).
- change: THESIS_DESIGN §2 (overarching question, RQ table with angles, contributions tagged by RQ), §2a (L0–L2
  tools), §3 (chapter map: Ch. 5 "Grounded, auditable agents"), §4 (row on the RQ change), §7 (two new examiner
  questions: proof faithfulness, diversity sources), §8 (adoption note); README and DESIGN_DOC_zh (repo snapshot and
  the Claude Docs document, rev 44) in the same words; backlog rows `tools` (P0) and `exp07` (P1); RQ labels in the
  exp02 and exp06 drafts. exp01 and its registration are untouched.
- next: decisions 1–7 of the design note; then the tool layer, the exp07 draft and exp03 H8 before the 11-25
  registration.

### 2026-11-01 — D11/RQ2: tool layer and teacher prompt version 4 (real tools)
- change: `src/mosaic/tools.py`: `get_macro_data` (L1) and `query_episode_db` (L2) over
  `configs/tools/episodes_standin.toml` (79 named, dated, pre-2025 episodes, qualitative accounts without statistics,
  idf-weighted retrieval; a stand-in for the episode database, human check pending). Teacher prompt version 4: the
  backdrop reaches the teacher only through get_macro_data (function calling), the final message adds a [Proof]
  block typed by layer and checked against the refs the tools returned, plus a confidence line. Items version 3
  recentres the backdrop (unemployment above 4.5% in 50% of draws, was 72%; CPI skewed towards 2%). School diagnoses
  carry the review fixes (real rates, the zero bound, trend money growth). `scripts/teacher_api.py` runs the tool
  loop with streamed tool calls. One run gives two formats: the Confirmation single-pass text for exp01 arm C
  (flattened, proof dropped) and the multi-turn agent conversation for C-agent.
- command: `scripts/teacher_api.py … --n 20 --model qwen3.8-max --network-secret --limit 1` (smoke test)
- result: function calling works on the token plan (6.0k tokens in, 5.5k out for one conversation); the teacher used
  both tools in order and the trajectory passed every check after two fixes: scenario lines written "S1 (…): p 0.50"
  are normalised, and proof steps citing several refs ("- L1 [A] with [B]: …") are accepted. Its first [Think] still
  said "the event gives no bp", so step 1 no longer lists size units. The smoke run is not part of the pilot.
- deviation: planned get_rules (L0) as a tool (design note §3) / L0 stays in the task prompt / none for RQ2, which
  names L1 and L2 only; exp03 already passes the scenario set / keep, note it in the design note.
- next: pilot v4 (20 per school) and the Opus review.

### 2026-11-01 05:16 UTC — infra: Task A pod (agent spike)
- pod `tmd8qxb4j16eh3` (`mosaic-A-20261101-0516`), NVIDIA A40 48 GB, $0.59/h, `--hours 2` (watchdog at 4 h), branch
  `claude/vibrant-tesla-rqvzo1`, pushes to `agent/task-A-20261101-0516`, heartbeat `agent/log-tmd8qxb4j16eh3`.
- no network volume: CA-MTL-1 (where `dy1ct9hkm0` lives) listed no GPU in stock, so the pod has its own 60 GB volume,
  downloads Qwen3-8B itself and is terminated (not only stopped) after its push, so no storage cost remains.
- deviation: planned the network volume / none in stock in CA-MTL-1 / about 10 min more setup per pod / pods without the
  volume until stock returns; consider a second volume in a data center with stock if this persists.

### 2026-11-01 — drafts: exp07 (RQ2) and exp03 H8 plus agent arms (RQ3)
- change: new `research/prereg_drafts/exp07_faithfulness.md` (systems A-agent, C-agent, C-agent+RFT; E-dev seed 7,
  E-test fixed at registration, E-hist if the episode database arrives; M1 validity and grounding, M2 counterfactual
  sensitivity with cited vs placebo indicators, M3 SAE faithfulness, a validated proof-step typer; F-H1 to F-H4 with
  Holm). exp03 draft: pool-persona, pool-models (open models released before 2025-05), pool-sample at equal ensemble
  size, H8 (pool-eq beats each of them), agent arms as secondary systems with a cut-off date (2026-12-10).
- decision needed (human): the personas' wording, the two extra open models and their licences, F-H1 to F-H4 and the
  counterfactual shifts; both drafts are registered by the human.

### 2026-11-01 — merge of the reference session; deviation protocol; two deviations logged
- change: the reference session's branch (`claude/fervent-pascal-hzleuz`: AI-assisted Ch. 2–3 drafts, verified
  bibliographies, `research/thesis_drafts/`) merged into the session branch (ledger conflict resolved by keeping all
  rows in date order); that session now works only on references. The deviation protocol the human asked for ("runs
  will differ from the plan; adjust promptly") is now THESIS_DESIGN §6, program.md rule 14 (with a `deviation:` line
  in the log format) and ORCHESTRATOR rule 7. THESIS_DESIGN §5 gains the tool layer, teacher v4, Task A, exp07, the
  H8 pools and the 12-10 agent-arm cut-off.
- deviation: exp03 counts / the 2026-10-31 Task 2 entry says 149 questions, 58 calibration and 91 test, while the
  committed `research/exp03_data_card.md` sums to 51 and 98 (total 149 in both) / affects the calibration-size
  statements (design note §4a, now "51 by the data card") and the exp03 registration / recount with `mosaic exp03
  card` on the next pod that mounts the network volume (the data live there) and correct whichever is wrong.
- deviation: Task S hand-off (2026-10-31) said `mosaic doctor` found the original prompts in place, but
  `configs/prompts/*.txt` still start with the PLACEHOLDER line / the arm A/C prompts are missing, so the v4 records
  carry placeholder system prompts / the records are rebuilt from the stored conversations once the human commits the
  originals (`mosaic teacher-import` again); `mosaic doctor`'s placeholder check should be verified on the next pod.

### 2026-11-01 — RQ2/Task A: agent spike, Qwen3-8B as prompted agent with the real tools
- hypothesis: a prompted Qwen3-8B can follow the agent contract (episode tool, macro tool, [Output], [Proof]).
- change: none (measurement only); report `research/agent_spike.md`.
- command: `python -m mosaic agent-spike --n 10` and `... --thinking` (A40, ~9 min each)
- run_ids: `runs/agent-spike/non-thinking`, `runs/agent-spike/thinking` (not versioned)
- result: 0/30 pass all checks in both modes. Tool calls parse (0 malformed), but protocol 0/30 both modes (final
  message lacks [Think]; 5/30 thinking conversations call both tools in one message), signals malformed in 25–30/30,
  proof valid 0/30 (non-thinking) vs 5/30 (thinking), 0 scenario probabilities found in 25–30/30. One non-thinking
  conversation put all 13 indicator names into a single string (tool error). Time 530 s / 557 s.
- deviation: the teacher (qwen3.8-max) passed every check on its smoke conversation after normalisation; the 8B
  starting point is 0 %. No harness bug found (tools run, transcripts complete), so no code change.
- decision: keep as the A-agent baseline; no prompt tuning (Task A rule 3).
- next: human decides on normalisation / format example / rejection-sampling SFT. READY FOR HUMAN: agent spike.

## For the human (2026-11-01, Task A)
- The prompted 8B agent reaches 0 % on the strict contract in both modes; see `research/agent_spike.md` for the
  failure types and the suggested (untested) prompt changes. The checks may be stricter than a reader needs: say if
  you want a lenient variant to separate "wrong form" from "wrong content".
- The pod GPU showed 100 % utilisation and 558 MiB in use before I started anything (another process on the card?);
  the timings above may be slightly inflated.

### 2026-11-01 — D11: Opus review of pilot v4; teacher prompt version 5, items version 4
- result: review of the 57 kept v4 conversations (`research/teacher_pilot/opus_review.md`, three Opus 5.5 reviewers,
  evaluation only): five shared criteria 4.01 (v2 4.12, v1 3.61), school fidelity 4.61, grounding 3.54 (new), verdict
  "with changes" from all three. Tool honesty is fixed by construction; new problems: the step-3 echo "weigh the
  event" (52/57 by regex), "this/the school" (44/57), pre-event data read as effects, S1 at 0.40-0.50 and repeated
  tuples, "Confidence: moderate" 57/57, residual credit SHORT and gold or bond defaults, signals on minority
  scenarios, the US backdrop used for foreign events, implausible backdrops.
- change: prompt version 5 (no echoed instructions; data declared pre-event; contradictions only against levels the
  event states; scenario, confidence and asset-referent definitions; minority-scenario and backdrop-only calls capped;
  foreign events not judged with US data; indicators behind the signals requested); school profiles (Keynesian terms
  defined, the quotable supply-shock line rewritten; Austrian stance made conditional on real rates and money
  creation, natural-rate comparison; Monetarist 3.5-4.5% band, implied velocity, supply-shock argument restricted);
  validator from version 5 on: echo phrases rejected, at most 8 proof steps, an L5 step must name the most likely
  scenario; batch report: modal-probability band, repeated tuples, confidence levels, shared 5-word phrases,
  direction warning at 65%. Items version 4: growth draws skewed positive (37% negative, was ~50%), curve tied to the
  policy path and inflation, oil tied to CPI, three lagged or smoothed series, event-stated US levels imposed.
  Episode table +7 (86): money-fund and stablecoin runs, PBoC reserve-requirement cuts, HOLC and the 2009
  modification programme, the SNB floor. Tool: indicator names joined in one string are split (agent spike).
  99 offline tests pass.
- next: pilot v5 (20 per school), automatic checks against the v4 echo counts, then the Opus review.

## For the human (2026-11-01, teacher terms before the full run)
- 老師 qwen3.8-max 是透過 token plan 的託管 API 呼叫的。開源權重的 Qwen3.8-Max License 允許微調與衍生作品、沒有禁止拿輸出訓練，
  營收門檻（MaaS 業者年營收超過 5,000 萬美元）也碰不到；但託管 API 受阿里雲條款約束：Model Studio service-specific terms 第 III 節
  規定「試用（trial）互動產生的內容只能用來評估模型表現，不得作其他用途，也不得提供給第三方」。請確認 token plan 是付費方案而且
  條款允許拿輸出訓練模型；確認前，完整的 1,500 條不會開跑（試產只用來評估，不受影響）。若不允許，改用 pod 上的開源老師
  （Qwen3.8-27B，Apache-2.0；或 Qwen3.8-Flash-Next，qwen-community 授權允許拿輸出訓練），v5 流程不用改。
  修正案 4 Change 5 已改寫成實際流程，老師一欄留給你勾選。
