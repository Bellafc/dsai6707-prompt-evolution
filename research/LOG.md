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
