# Macro-MOSAIC：MPhil 論文實驗環境（PolyU DSAI）

這是 Futian Jiang 的 MPhil 論文實驗 repo。實驗在 RunPod 上跑，由 Claude Code 自動執行研究迴圈（auto-research）。
**論文設計、時程和規則以 [`research/THESIS_DESIGN.md`](research/THESIS_DESIGN.md) 為準。**它依據學校 RPg Handbook 第 10 章和 DSAI 2025/26 課程文件的畢業要求制定。

## 三個研究問題與對應實驗

| RQ | 問題 | 實驗 | 章 | 優先級 |
|---|---|---|---|---|
| RQ1 | 微調能不能比最強的 prompting（few-shot CoT，含模型自己的 thinking 模式）更好地教會模型「學派化推理」？模型內部到底改變了什麼？ | exp01（Qwen3-8B）：A zero-shot／B few-shot／C LoRA／D Opus 5.5／T 老師模型（可選），加上 LLM 評審與兩位人工評審；exp06：用稀疏自編碼器（SAE）看模型內部；exp01b：Qwen3.5-27B 複製 | 4 | P0／P1 |
| RQ2 | 用總經狀態找歷史類比，能不能比敘事相似度更準地預測資產反應？ | exp02：擴展時間窗檢索，只用當時已知的資料（point-in-time） | 5 | P1 |
| RQ3 | 多學派合成的機率預測，在模型訓練之後才結算的真實總經結果上，是否比單一學派、prompt 學派更好？是否校準、一致？ | exp03：2025–26 已結算總經市場；exp04：一致性；exp05：即時前瞻（可選） | 6 | P0／P1／P2 |

論文的知識架構沿用 pmpol 的 L0–L5 分層：三個學派是 L3（有爭議的框架，並列、不選邊），每個預測都附回溯到 L0–L4 的推理證明和分析信心（見 THESIS_DESIGN §2a）。

exp01 已事先登記（[`prereg/`](prereg/)，含三份修正案）。Confirmation 的 Qwen2.5 adapter 沒有保存，所以改在 Qwen3-8B 上重新訓練，見修正案 4 草稿（[`research/prereg_drafts/exp01_amendment_4_DRAFT.md`](research/prereg_drafts/exp01_amendment_4_DRAFT.md)），由你登記。D 組（Opus 5.5）不需要 GPU，原始 prompt 和 test 事件備齊後可以先用 `mosaic pregen` 產生、之後再評分（修正案 3）。exp02–06 的草稿在 [`research/prereg_drafts/`](research/prereg_drafts/)，要在計算任何分數之前由你登記。

## 分工

- **Agent（Claude Code，無人值守）**：照 [`program.md`](program.md) 做 dev 和校準資料上的工作：parity 檢查、調 few-shot 組、建 exp03 資料集、實作和測試。每一步都記在 [`research/LOG.md`](research/LOG.md)，產出記在 [`research/AI_USE_LEDGER.md`](research/AI_USE_LEDGER.md)。agent 不寫論文內文。
- **你**：提供資料和原始 prompt、做設計決策（THESIS_DESIGN §8）、登記、凍結、跑 test（`scripts/final.sh`）、人工評分、寫論文。凍結、跑 test 和 test 上的評審都需要在互動終端機手動確認。

## 在 RunPod 上開始

```bash
cd /workspace && git clone https://github.com/alexanderkong-arch/PolyU polyu && cd polyu && git checkout exp-env
bash setup/runpod_setup.sh                 # venv、vLLM、Claude Code、下載 Qwen3-8B（約 16 GB）
# 想同時準備 exp01b：EXTRA_MODELS="Qwen/Qwen3-8B-Base Qwen/Qwen3.5-27B" bash setup/runpod_setup.sh
# 上傳資料（見 data/README.md；adapter 在 pod 上用 mosaic train 重新訓練），換回原始 prompt 和關鍵字表
# 資料還沒到也可以先開始：agent 會先做 program.md 的 Task S（試跑）和 Task 2（exp03 資料）
export CLAUDE_CODE_OAUTH_TOKEN=...         # 在自己電腦跑 claude setup-token 取得；不要設 ANTHROPIC_API_KEY
mosaic doctor --arms A,B,C,D               # 資料到齊後直到顯示 ready
tmux new -s ar 'bash scripts/autoresearch.sh'
```

查看進度：`mosaic status`、`tail research/LOG.md`、`mosaic report --exp exp01 --split dev`。

## 目錄

```
research/THESIS_DESIGN.md   論文設計：畢業要求、RQ、章節、時程、AI 使用規則、口試問題對照、待決事項
program.md                  auto-research 協議（規則、預算、Task 0–4、交接）
prereg/                     已登記的事前登記（登記後不改，只加修正案）
research/prereg_drafts/     exp02–05 草稿
configs/                    exp01.toml、lexicons.toml、judge.toml、prompts/
src/mosaic/                 框架：data、prompts、backends（vLLM+LoRA / Claude CLI / OpenAI / fake）、parse、metrics、
                            judge、stats、run、report、locks、vendor
experiments/results.tsv     每一次跑分一列（只增不刪）
locks/                      凍結紀錄與 test 存取紀錄
scripts/                    autoresearch.sh（agent）、final.sh（人）
```

`pmpol-academic-2026-10-21.tar.gz` 是團隊的預測市場系統，exp03 的資料會用到（`python -m mosaic vendor` 解壓到 `vendor/`）；論文裡要標明它是團隊程式碼。
