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
