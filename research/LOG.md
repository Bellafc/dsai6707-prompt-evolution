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
