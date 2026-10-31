# Orchestrator protocol (Claude Code cloud session → RunPod pods)

You are the **orchestrator**: a Claude Code cloud session on this repository with no GPU. You start, watch and stop
RunPod GPU pods; the experiments themselves run on the pods, where a second Claude Code session follows
`program.md`. Read `CLAUDE.md`, `research/THESIS_DESIGN.md` §5 (dates) and `research/backlog.md` first.

```
you (cloud session) ──REST──▶ RunPod pod ──▶ scripts/pod_bootstrap.sh ──▶ Claude Code on the pod (program.md)
        ▲                                                           │
        └──── git fetch origin agent/* ◀──── push at session end ───┘     the human merges into main
```

## Rules

1. **No secrets in text.** Never print, write, commit or ask for a token. The RunPod API key reaches RunPod as a
   network secret of this cloud environment (host `rest.runpod.io`); the pods get their tokens from RunPod
   secrets (`claude_oauth_token`, `github_token`, optional `hf_token`). `mosaic pod get` already hides them.
2. **Money.** One pod at a time (never `--allow-parallel` unless the human says so), one GPU, `--hours` at most
   the task's budget below. Before `create`, tell the human the GPU class, the expected $/h (from `pod list`
   after creation, or RunPod's price list) and the hour limit. Stop pods you no longer need: a stopped pod costs
   only its storage; the network volume keeps everything.
3. **Held-out data stays human.** You never run, schedule or script freeze, final runs, test-split pregen or
   judging, and you never start a pod for them; for those the human asks for a task `H` pod (no agent) and works
   in its terminal.
4. **Branches.** Pods push only to `agent/...` branches. You summarise them and open a pull request into `main`
   for the human; you do not merge.
5. **Logs.** Each pod start and stop gets one entry in `research/LOG.md` (pod id, task, GPU, hours, branch),
   committed and pushed on your session branch like any other change.

## Commands (run `pip install -e .` once per session)

| Purpose | Command |
|---|---|
| What is running | `python -m mosaic pod list` |
| Network volumes | `python -m mosaic pod volumes`; create: `python -m mosaic pod volume-create --dc <dataCenterId> --size 200` |
| Start a task | `python -m mosaic pod create --task S --gpu 80gb --hours 4 --volume <volumeId> [--dc <dataCenterId>]` |
| Preview the request | add `--dry-run` |
| Details | `python -m mosaic pod get <podId>` |
| Stop / resume / delete | `python -m mosaic pod stop <podId>` · `start <podId>` · `terminate <podId>` (terminate only when the human asks) |
| Results | `git fetch origin 'refs/heads/agent/*:refs/remotes/origin/agent/*'`, then read `research/LOG.md` and the diff on that branch |

## Task budgets (program.md)

| Task | GPU | `--hours` | Needs |
|---|---|---|---|
| S spikes (serving, `mosaic train`, SAE check, Qwen3.5-27B LoRA) | 80gb | 4 | nothing from the human |
| 2 exp03 data build (CPU and network) | 48gb (cheapest) | 6 | — |
| 0 adapters + parity | 48gb or 80gb | 3 | assets on the volume, backlog row `train` = go |
| 1 exp01 dev loop | 48gb | 6 | Task 0 done |
| 5 exp06 instrument | 48gb | 6 | Task 0 done |
| H human pod (freeze, final runs, ratings) | as needed | ≤ 4 | the human at a terminal |

## Watching a pod

A pod's session ends by itself: the bootstrap pushes `pod <id>: end of session` to its branch and stops the pod.
When asked for a status (or every ≥ 20 minutes in a `/loop` the human started): `pod list`, fetch the agent
branches, report new LOG entries and any "For the human" items. Stop a pod yourself if it is still RUNNING
more than 30 minutes after its hour limit, or if its branch already has the end-of-session commit (the pod could
not stop itself).

## Human setup (一次性設定，人來做)

1. RunPod：建立這個專案專用的 API key；在 **Secrets** 建 `claude_oauth_token`（自己電腦跑 `claude setup-token`
   的結果）、`github_token`（GitHub fine-grained token，只給 `alexanderkong-arch/PolyU`，Contents: Read and
   write）、可選 `hf_token`。
2. RunPod：在有 H100／A100 80GB 的資料中心建一個 200 GB 的 network volume，記下 volume id 和 data center id。
   資料（96 個 test 事件、dev 事件、訓練軌跡、episode DB、開題時的生成結果）上傳到 volume 的
   `/workspace/assets/{events,trajectories,episodes,legacy}/`；原始 prompt 和關鍵字表則 commit 進 repo
   （`configs/prompts/`、`configs/lexicons.toml`）。
3. GitHub：在這個 repo 安裝 Claude GitHub App（或在自己電腦跑 `/web-setup`）。
4. claude.ai/code：建一個 cloud environment，network access 用 **Trusted**，在 **Network secrets** 加一個
   secret：host `rest.runpod.io`，header `Authorization`，prefix `Bearer`，value 貼 RunPod API key。不要把 key
   放進環境變數或貼進對話。
5. 在這個環境開一個 session（repo `alexanderkong-arch/PolyU`，branch `main`），告訴它：讀 `ops/ORCHESTRATOR.md`，
   用 volume `<id>` 開 Task S。
