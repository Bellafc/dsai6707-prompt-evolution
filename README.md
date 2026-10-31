# Macro-MOSAIC 實驗環境（MPhil, PolyU DSAI）

在 RunPod 上用 Claude Code 自動跑研究迴圈（auto-research）的實驗框架。第一個實驗 **exp01** 回答 Confirmation 口試的問題：「為什麼做微調，而不是用 CoT？」

| 組別 | 內容 |
|---|---|
| A | Qwen2.5-7B + 學派 system prompt，zero-shot CoT（= Confirmation 的 base 組） |
| B | A + 學派 SFT 軌跡當 few-shot 範例（agent 在 dev 上調到最強） |
| C | Qwen2.5-7B + 學派 LoRA（你的方法） |
| D | Claude Opus 5.5（前沿模型參考，走你的 Claude 訂閱） |
| T | GPT-4o（產生 SFT 資料的老師模型，可選，要 OpenAI API） |

假設與判定規則事先寫死在 [`prereg/exp01_prompt_vs_sft.md`](prereg/exp01_prompt_vs_sft.md)；D 組改用 Opus 的理由與限制見 [`prereg/exp01_amendment_1.md`](prereg/exp01_amendment_1.md)。

## 分工

- **Agent（Claude Code，無人值守）**：照 [`program.md`](program.md) 跑——先做 parity 檢查（重現 Confirmation 的表 4.3），再在 dev 上把 B 組調到最強，每一輪都記在 [`research/LOG.md`](research/LOG.md) 和 `experiments/results.tsv` 並 commit。
- **你**：提供資料與原始 prompt、讀 dev 總結、執行一次性的凍結與 test 跑分（`scripts/final.sh`）、push。凍結和 test 跑分必須在互動終端機手動確認，agent 做不到。

## 在 RunPod 上開始

```bash
cd /workspace && git clone https://github.com/alexanderkong-arch/PolyU polyu && cd polyu && git checkout exp-env
bash setup/runpod_setup.sh                 # venv、vLLM、Claude Code、下載 Qwen2.5-7B（約 15 GB）
# 上傳資料與 adapter（見 data/README.md），換回原始 prompt 和關鍵字表
export CLAUDE_CODE_OAUTH_TOKEN=...   # 在自己電腦跑 claude setup-token 取得；不要設 ANTHROPIC_API_KEY
mosaic doctor --arms A,B,C,D               # 直到顯示 ready
tmux new -s ar 'bash scripts/autoresearch.sh'
```

查看進度：`mosaic status`、`tail research/LOG.md`、`mosaic report --exp exp01 --split dev`。

## 目錄

```
program.md            auto-research 協議（規則、預算、Task 0/1、交接）
CLAUDE.md             Claude Code 在這個 repo 的慣例
prereg/               事前登記（登記後不改）
configs/              exp01.toml、lexicons.toml、prompts/
src/mosaic/           框架：data、prompts、backends（vLLM+LoRA / OpenAI / fake）、parse、metrics、stats、run、report、locks
experiments/results.tsv   每一次跑分一列（只增不刪）
research/             LOG.md、backlog.md、各實驗的 dev 總結
locks/                凍結紀錄與 test 存取紀錄
scripts/              autoresearch.sh（agent）、final.sh（人）
```

`pmpol-academic-2026-10-21.tar.gz` 是團隊的預測市場系統，exp03 之後會用到（見 `research/backlog.md`）。
