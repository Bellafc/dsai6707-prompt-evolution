# Macro-MOSAIC：MPhil 論文實驗環境（PolyU DSAI）

這是 Futian Jiang 的 MPhil 論文實驗 repo。實驗在 RunPod 上跑，由 Claude Code 自動執行研究迴圈（auto-research）。
**論文設計、時程和規則以 [`research/THESIS_DESIGN.md`](research/THESIS_DESIGN.md) 為準。**它依據學校 RPg Handbook 第 10 章和 DSAI 2025/26 課程文件的畢業要求制定。
附理由的中文設計文件：[`research/DESIGN_DOC_zh.md`](research/DESIGN_DOC_zh.md)（Claude Docs 版的快照）。
開題報告、投影片、PQE survey 和原本 claude.ai Project 裡的筆記都在 [`docs/project/`](docs/project/)。

## 三個研究問題與對應實驗

論文的總問題（2026-11-01 確定）：**語言模型 agent 能不能依照明確、彼此競爭的經濟理論推理，同時做到模型內部真的照理論運作、說出來的推理可以稽核、給出的機率值得信任**？三個 RQ 從三個角度回答，共用同一個實驗設計：prompt／微調 × 單次生成／用真工具並附分層證明的本體論 agent（見 [`research/DESIGN_ontology_agents.md`](research/DESIGN_ontology_agents.md)）。

| RQ | 角度 | 問題 | 實驗 | 章 | 優先級 |
|---|---|---|---|---|---|
| RQ1 | 腦中在算什麼 | 微調能不能比最強的 prompting（few-shot CoT，含模型自己的 thinking 模式）更好地教會模型一個學派的框架？改變的是模型內部的概念，還是只有寫出來的用詞？ | exp01（Qwen3-8B，已登記）：A zero-shot／B few-shot／C LoRA／D Opus 5.5／T 老師模型（可選），加上 LLM 評審與兩位人工評審；exp06：用稀疏自編碼器（SAE）看模型內部；exp01b：Qwen3.5-27B 複驗 | 4 | P0／P1 |
| RQ2 | 它說了什麼 | agent 必須用真工具查時點事實（L1）和歷史基準率（L2），並為每個預測寫分層證明時，它的推理能不能稽核、是不是忠實？證明是否有效、能否追溯到 L0–L4；引用的證據一改，結論會不會跟著改；證明裡宣稱的機制，模型內部有沒有真的激活？ | exp02：總經狀態類比 vs 敘事相似度，當作 L2 工具的驗證（擴展時間窗、只用當時已知的資料）；exp07（新）：證明有效性、反事實工具結果、證明步驟分類、SAE 證明忠實度，只用開發集和 2025 年以前的事件 | 5 | P1 |
| RQ3 | 它有多確定 | 把多個彼此競爭的框架的機率預測合起來，在模型訓練之後才結算的真實總經結果上，是否勝過單一框架和其他多樣性來源（人設、多模型、重複抽樣）？是否校準、一致？框架之間的分歧和分析信心，能不能事先指出哪些預測容易出錯？ | exp03：2025–26 已結算總經市場（H1–H7，加 H8 多樣性來源）；exp04：一致性；exp05：即時前瞻（可選） | 6 | P0／P1／P2 |

論文的知識架構沿用 pmpol 的 L0–L5 分層：三個學派是 L3（有爭議的框架，並列、不選邊），每個預測都附回溯到 L0–L4 的推理證明和分析信心（見 THESIS_DESIGN §2a）。

exp01 已事先登記（[`prereg/`](prereg/)，含三份修正案）。Confirmation 的 Qwen2.5 adapter 沒有保存，所以改在 Qwen3-8B 上重新訓練，見修正案 4 草稿（[`research/prereg_drafts/exp01_amendment_4_DRAFT.md`](research/prereg_drafts/exp01_amendment_4_DRAFT.md)），由你登記。D 組（Opus 5.5）不需要 GPU，原始 prompt 和 test 事件備齊後可以先用 `mosaic pregen` 產生、之後再評分（修正案 3）。exp02–06 的草稿在 [`research/prereg_drafts/`](research/prereg_drafts/)，要在計算任何分數之前由你登記。

## 分工

- **Agent（Claude Code，無人值守）**：照 [`program.md`](program.md) 做 dev 和校準資料上的工作：parity 檢查、調 few-shot 組、建 exp03 資料集、實作和測試。每一步都記在 [`research/LOG.md`](research/LOG.md)，產出記在 [`research/AI_USE_LEDGER.md`](research/AI_USE_LEDGER.md)。agent 不寫論文內文。
- **你**：提供資料和原始 prompt、做設計決策（THESIS_DESIGN §8）、登記、凍結、跑 test（`scripts/final.sh`）、人工評分、寫論文。凍結、跑 test 和 test 上的評審都需要在互動終端機手動確認。

## 用 Claude Code Cloud 指揮 RunPod（建議）

一個沒有 GPU 的 Claude Code cloud session 當「指揮」：用 RunPod API 開 GPU pod、看進度、關機；實驗在 pod 上由另一個
Claude Code 照 `program.md` 跑，結束時把 commit 推到 `agent/...` 分支、自己關機，由你合併。一次性設定（RunPod
secrets、network volume、Claude Code 環境的 network secret）和指揮的規則見 [`ops/ORCHESTRATOR.md`](ops/ORCHESTRATOR.md)。
金鑰不進 repo、不貼進對話。

## 手動在 RunPod 上開始

```bash
cd /workspace && git clone https://github.com/Bellafc/macro-mosaic polyu && cd polyu
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
research/DESIGN_DOC_zh.md   中文設計文件（附理由，Claude Docs 快照）
docs/project/               開題報告 PDF、HTML 投影片、口頭陳述稿、PQE survey、Project 筆記（PROJECT_NOTES.md）
program.md                  auto-research 協議（規則、預算、Task 0–4、交接）
prereg/                     已登記的事前登記（登記後不改，只加修正案）
research/prereg_drafts/     exp01 修正案 4、exp01b、exp02–06 草稿
configs/                    exp01.toml、lexicons.toml、judge.toml、prompts/
src/mosaic/                 框架：data、prompts、backends（vLLM+LoRA / Claude CLI / OpenAI / fake）、parse、metrics、
                            judge、stats、run、report、locks、vendor
experiments/results.tsv     每一次跑分一列（只增不刪）
locks/                      凍結紀錄與 test 存取紀錄
scripts/                    autoresearch.sh（agent）、pod_bootstrap.sh（pod 開機流程）、final.sh（人）
ops/ORCHESTRATOR.md         指揮 session 的規則與一次性設定
```

`pmpol-academic-2026-10-21.tar.gz` 是團隊的預測市場系統，exp03 的資料會用到（`python -m mosaic vendor` 解壓到 `vendor/`）；論文裡要標明它是團隊程式碼。
