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
