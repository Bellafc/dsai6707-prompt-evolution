<!-- Snapshot of the Claude Docs design document "Macro-MOSAIC 畢業論文設計" (https://claude.ai/artifact/53m7SsccYQaQqwo9Bdw85Z), exported 2026-10-31 (rev 38); RQ sections synced with it on 2026-11-01 (rev 44); timeline note and deviation rule (rev 45). research/THESIS_DESIGN.md stays the source of truth; when one changes, update the other. -->

# Macro-MOSAIC 畢業論文設計

Oct 30, 2026 · @Bella

建議 Jun 15, 2027 送審，最晚 Feb 15, 2027 交 GSB/2B。論文收斂成三個研究問題（2026-11-01 改成同一個設計的三個角度：模型內部、agent 說了什麼、有多確定），主要證據從 2023–25 回測改成模型訓練之後才結算的 2025–26 總經預測市場。知識架構沿用 pmpol 的 L0–L5 分層：三個學派是 L3，每個預測都附推理證明和分析信心。開題的 Qwen2.5 adapter 沒有保存，所以改在 Qwen3-8B 上重新訓練，並新增用 SAE 看模型內部的 exp06。現在就能用 Claude Code 指揮 RunPod 開始試跑；有 11 件事要你和張老師決定。

## 畢業要求對設計的限制

有四條規定直接決定設計：送審要在 Normal Period 結束前，GSB/2B 要提前 4 個月，沒有已接收的論文要多過一關系上初審，口試結果由兩位校外委員決定。

| 規定 | 出處 | 對設計的影響 |
| --- | --- | --- |
| 送審要在 Normal Period 結束前（全職 MPhil 2 年，最長 3 年） | RPg Handbook 10.2；DSAI 2025/26 | 2025 年 9 月入學，約 2027 年 8 月底截止（確切日期待確認）。目標訂在 6 月中，留 2.5 個月緩衝 |
| 送審前至少 4 個月交 Form GSB/2B，附 3 頁內的論文簡介 | Handbook 10.2 | 題目、研究問題、貢獻要在 2 月中定下來，所以實驗設計要在 1 月底前收斂 |
| 論文裡沒有已被好的期刊或會議接收的 paper，送外審前要先過 DSAI Thesis Assessment Committee 初審 | DSAI 5.7 | 初審要多久文件沒寫。IJCAI 2027 若被接收（4 月 21 日放榜），可以省掉這一關 |
| 校內審約 4 週、外審 6 週；至少 2 位校外委員，兩人意見一致才算 | Handbook 10.3–10.4 | 口試大約在送審後 3–5 個月。委員是校外的領域專家，弱點會被直接問到 |
| 口試約 2 小時：報告 30 分鐘（最長 40）加問答，問題由 BoE 主席轉問 | Handbook 10.4 | 每個可能的問題都要有事先登記的實驗，或明說的限制（見口試問題對照） |
| 英文、符合格式規範、附完整相似度報告 | Handbook 10.1–10.2 | 投稿論文的段落要在論文裡註明；開題報告沒有公開，可以沿用 |
| AI 產生的內容要標明；交出的作業必須是自己的；學生負全責 | PolyU GenAI 學生指引（2026-01-05 修訂） | 論文內文由你寫；agent 的產出全部記錄下來（見 AI 使用與學術誠信） |
| 送審前完成：7 學分、GPA ≥ 2.70、AIE、Research Seminars I & II（每年至少 10 場，加一篇至少 1,500 字的報告）、英文課、National Education 線上課 | DSAI 5.1–5.9 | 和實驗無關，但沒完成就不能送審；2 月前要檢查 |

## 時程：從送審日往回推

（時程圖：15 個里程碑，2026/11–2027/10。日期表見 [THESIS_DESIGN.md §5](THESIS_DESIGN.md)；互動版在 Claude Docs。）

exp01 和 exp03 是關鍵路徑：它們 12 月底前完成，才趕得上 IJCAI，2 月 15 日的 GSB/2B 也才寫得出確定的貢獻。

2026-11-01 新增的里程碑：11/4 Task A（Qwen3-8B 當 agent 的測試）和完整的 v4 老師生成，11/22 exp03 校準期的 H8 組合和 agent 組別，12/4 exp07 試跑，12/10 exp03 agent 組別的截止日。日期表見 THESIS_DESIGN.md §5；時程圖還沒畫入這幾項。

## 需要重新設計的地方

開題計畫有八處要改，都是外審最容易抓的弱點。改完以後範圍變小，但證據更硬；論文第 1 章和第 7 章要寫明改了什麼、為什麼改。

| 開題時的計畫 | 新設計 | 理由 |
| --- | --- | --- |
| Stage 4：Fractional Kelly 配置，加 2023–25 walk-forward 回測當主要證據 | 降為應用討論；時間夠再做 2025–26 的小型示範（D2） | 2023–24 在 Qwen2.5 和 GPT-4o 的訓練資料裡，等於偷看答案；事件太少，統計檢定力不足 |
| Stage 3：regime 條件權重，用 Polymarket、Metaculus 的地緣政治題校準 | 等權合成、依表現加權、溫度校準、一致性投影；用 2025 年已結算的總經市場校準 | 不偷看的時間窗裡只有一兩種 regime，條件權重估不出來；校準資料要和預測任務同領域 |
| 學派輸出自訂情境的機率，沒有答案可以對 | 改用市場定義的情境（市場的結果區間），讓學派分配機率後直接算分 | 不必重新訓練 adapter；有真實結果才能回答「多學派到底有沒有用」 |
| 學派的看法直接合成成一個預測 | 依本體論的 L3 規則：各學派並列呈現，合成只是 L5 摘要；每個預測附推理證明和分析信心 | 讓「信心」和「可解釋性」變成可以檢驗的假設（exp03 H6、H7） |
| 只用關鍵字指標評估學派 | 關鍵字指標，加 Opus 5.5 盲評，再用兩位人工評審驗證盲評 | 外審一定會問「詞彙等於推理嗎」；開題報告自己也寫了「必要但不充分」 |
| Qwen2.5-7B 的 adapter（沒有保存） | 改在 Qwen3-8B 上用同一批軌跡重新訓練（修正案 4），另用 Qwen3.5-27B 複驗 RQ1（exp01b，D7）；加上用 SAE 看模型內部的 exp06 | 反正要重訓；Qwen3-8B 有公開 SAE、回測窗口從 2025-05 起；外審會問「換更強的模型還需要微調嗎」和「微調教的是概念還是用詞」 |
| Mahalanobis 的共變異數用 141 個事件估 | 用每月指標序列（數百個月）加 Ledoit–Wolf 收縮，而且只用當時以前的資料 | 35 維對 141 個樣本估不穩，這正是江老師的專業 |
| EconCausal、EconLogicQA benchmark | 有時間才做 | 對這本論文來說，用真實結果評估比通用 benchmark 有說服力 |

題目結尾的「Cross-Asset Allocation」要跟著 D2 決定去留。

## 論文架構

2026-11-01 確定的總問題：**語言模型 agent 能不能依照明確、彼此競爭的經濟理論推理，同時做到模型內部真的照理論運作、說出來的推理可以稽核、給出的機率值得信任**？三個研究問題從三個角度回答，共用同一個實驗設計（prompt／微調 × 單次生成／用真工具並附分層證明的本體論 agent）：RQ1 比較框架怎麼教進去，RQ2 比較有沒有真工具和證明，RQ3 把每一種組合都當成預測者來比。三個學派是深入研究的主要案例。Stage 1–3 都還在，Stage 4 移到討論。暫定題目：*Macro-MOSAIC: Multi-School Language-Model Reasoning for Macroeconomic Event Analysis and Forecasting*（要不要跟著改屬於 D2）。

| RQ | 角度 | 問題 | 證據 | 章 | 優先級 |
| --- | --- | --- | --- | --- | --- |
| RQ1 | 腦中在算什麼 | 微調能不能比最強的 prompting（few-shot CoT，含模型自己的 thinking 模式）更好地教會模型一個學派的框架？改變的是模型內部的概念，還是只有寫出來的用詞？ | exp01（已登記，不動）、exp06（SAE）、exp01b（27B 複驗） | 4 | P0／P1 |
| RQ2 | 它說了什麼 | agent 必須用真工具查時點事實（L1）和歷史基準率（L2），並為每個預測寫分層證明時，它的推理能不能稽核、是不是忠實？證明是否有效、能否追溯到 L0–L4；引用的證據一改，結論會不會跟著改；證明裡宣稱的機制，模型內部有沒有真的激活？ | exp02（L2 工具的驗證）、exp07（新：證明有效性、反事實工具、證明步驟分類、SAE 證明忠實度） | 5 | P1 |
| RQ3 | 它有多確定 | 把多個彼此競爭的框架的機率預測合起來，在模型訓練之後才結算的真實總經結果上，是否勝過單一框架和其他多樣性來源（人設、多模型、重複抽樣）？是否校準、一致？框架之間的分歧和分析信心，能不能事先指出哪些預測容易出錯？ | exp03（H1–H7，加 H8 多樣性來源）、exp04、exp05（可選） | 6 | P0／P1／P2 |

決策模型（D8）是三個角度共用的量測工具，不另立問題：RQ1 當評審、RQ2 分類證明步驟、RQ3 在 exp05 當決策頭。口試必問的「這是推理還是詞彙？」，由證明、評審（決策模型和 Opus）、SAE 特徵三種獨立的工具回答。

章節：

1. 緒論：問題、三個 RQ、貢獻、和開題計畫的差異
2. 背景與文獻：開題的 80 篇綜述，補上 LLM 預測、預測市場校準、一致性、知識蒸餾、歷史類比預測、會用工具的 agent
3. 資料與工具：episode 資料庫、當時已知的總經狀態、預測市場題庫、L0–L2 工具
4. 把框架教進模型：學派 agent 和模型內部的改變（Stage 2，RQ1）
5. 有根據、可稽核的 agent：真工具、分層證明、歷史類比檢索（Stage 1）、忠實度檢驗（RQ2）
6. 從推理到校準的預測（Stage 3，RQ3）
7. 討論：限制、配置應用（Stage 4）、AI 使用、PhD 方向
8. 結論

附錄放 prompt、關鍵字表、評審標準、所有事先登記與修正案、重現方式、AI 使用聲明。

貢獻（措辭維持在這個強度，避免開題時被指出的過度宣稱）：

1. 一份「當時已知」的總經事件資料庫，和一套用已結算預測市場建的、控制偷看的預測評估方法（三個 RQ 共用）
2. 微調與 prompting 在理論專屬推理上的對照證據，並附經人工驗證的 LLM 評審和 SAE 分析（RQ1）
3. 一種用有統計依據的共變異數估計、且按時間順序評估的類比檢索方法，當作 agent 的 L2 工具（RQ2）
4. 異質推理 agent 該不該合成的證據、考慮一致性的合成方法，以及理論多樣性是否比人設、多模型、重複抽樣更好的證據（RQ3）
5. 依知識層級組織的設計（見下一節）：agent 用工具取得 L0–L2，每個預測附回溯到 L0–L4 的證明和分析信心，並檢驗證明是否忠實（RQ2、RQ3）

## 本體論分層：論文的知識架構

把 pmpol 的 L0–L5 分層當成論文的知識架構：三個學派是 L3 的「有爭議框架」，只引用、不採納，而且並列呈現。這正好說明了為什麼要一個學派一個 agent，而不是把學派混成一個模型。

| 層 | pmpol 的意思 | 在 Macro-MOSAIC 裡 | 規則 |
| --- | --- | --- | --- |
| L0 制度規則 | 硬約束 | CPI 公布到 0.1 個百分點、FOMC 以 25 bp 為單位、市場結算規則 | 用來建情境區間和一致性約束（exp04） |
| L1 現況事實 | 帶有效期間和記錄時間 | 35 個指標在預測當下已公布的版本（ALFRED） | 模型只看得到這些，絕不用修正後的數字 |
| L2 歷史基準率 | 先驗 | 歷史類比（Stage 1）、序列的歷史分布、市場校準曲線 | 模型的輔助證據和基準 |
| L3 專家共識（有爭議） | 只引用、不採納，並列不選邊 | Keynesian、Austrian、Monetarist（`kb/L3/schools.yaml`） | 一個學派一個 agent；輸出永遠並列各學派的看法 |
| L4 市場觀測 | 觀測值，不是事實 | Kalshi、Polymarket 的價格 | 只當對照基準，絕不當模型輸入 |
| L5 系統推論 | 必須回溯到 L0–L4 | 各學派的機率分布、合成預測 | 每個預測附推理證明和分析信心 |

這個架構把你要的「信心」和「可解釋性」變成可以檢驗的東西：

- **可解釋性**：每個預測都寫一份推理證明（沿用 pmpol 的 `proof.py`），列出用到的 L1 資料和版本日期、L2 類比事件、L3 學派；白話說明只能從證明產生，不會寫得比證據更多。
- **信心**：機率和分析信心分開（ICD 203，沿用 pmpol 的 `confidence.py`）。信心取最弱的一環：L1 資料不全、類比太弱、有學派的輸出解析失敗、結算規則不清楚。
- **兼檢驗**：exp03 新增兩個假設。H6：學派之間分歧越大，合成預測的誤差越大。H7：分析信心「低」的預測，誤差比「高」的大。兩個成立，就是「分歧和信心都有用」的實證證據。

這也成為論文的第 5 個貢獻：一個依知識層級組織、可回溯、信心分級的預測設計。論文裡要標明這套分層來自團隊的 pmpol。

## 模型與工具：主力換成 Qwen3-8B，前沿用 Qwen3.5-27B

開題的 Qwen2.5 adapter 沒有保存，反正要重新訓練，所以底座重新選。條件有三個：有公開的 SAE（exp06 要用）、釋出日期之後留得下夠長的已結算市場可以回測（exp03）、一張 GPU 就能做 LoRA。符合的組合是 Qwen3-8B 當主力、Qwen3.5-27B 當前沿；更新的 Qwen3.6／3.8 和 Gemma 4 都沒有 SAE，只放進 exp05 當參考。

| 選項 | 怎麼用 | 判斷 |
| --- | --- | --- |
| **Qwen3-8B**（2025-04-29，Apache-2.0），學派 LoRA 重新訓練 | 主力：exp01、exp03、exp06 | 建議（D7）。[Qwen-Scope](https://huggingface.co/collections/Qwen/qwen-scope) 有 36 層全部的 SAE；2025-05 以後結算的市場它都沒看過，exp03 有約 18 個月可以回測；LoRA 工具成熟；和開題同一級大小 |
| **Qwen3.5-27B**（2026-02-24，Apache-2.0），學派 LoRA | exp01b 前沿複驗；exp06 在大模型上複驗；exp03 只做 2026-03 以後結算的子集 | 建議（D7）。唯一有公開 SAE 的 2026 模型，而且 SAE 就是在對話版上訓練的；bf16 LoRA 約 56 GB，要 80 GB 的卡；混合式 Gated DeltaNet 架構先在 Task S4 試 |
| [Gemma 4 31B](https://ai.google.dev/gemma/docs/core/model_card_4)（Google，2026-03-31，Apache-2.0） | 可選：跨廠商複驗 H1，不做 SAE；exp05 參考 | 一張 80 GB 卡上最強的非 Qwen 模型（MMLU-Pro 85.2、GPQA 84.3）；沒有 SAE，bf16 LoRA 放不進 80 GB |
| [Qwen3.8-27B](https://www.morphllm.com/qwen-3-8)、Qwen3.6-27B | exp05 參考（只用 prompt） | 更新，但沒有 SAE，幾乎沒有可回測的窗口 |
| Gemma 3 加 [Gemma Scope 2](https://www.greaterwrong.com/posts/YQro5LyYjDzZrBCdb/announcing-gemma-scope-2) | exp06 的備案 | 對話版專用的 SAE 和 transcoder，工具最成熟；Qwen 的 SAE 過不了 S0 關卡時改用 |
| Qwen2.5-7B（開題用的模型） | 可選：重現開題的 Table 4.3（A7、C7） | 只有原始訓練軌跡還在時才做（D11） |
| 決策模型 Jev、Vega、[Kev](https://github.com/jaredpalmer/kev)（Kev 有建在 Qwen3.8 上的 27B 版） | 只當量測工具：第二位開源評審（1–5 分每一級都有機率）；在 exp05 把推理轉成各區間機率的決策頭 | 可選（D8）。優點是每個選項都有機率，溫度已校準。但廠商的校準說法要自己驗；Jev 不開源；微調要約 1,000 筆標註；底座知道 2025–26 的事，不能用在歷史評估 |
| Opus 5.5 當老師，產生新的訓練資料 | 不做 | [Claude 消費者條款](https://www.anthropic.com/legal/consumer-terms)第 3 條第 2 項不允許用服務來訓練 AI 模型。Opus 只用在 D 組、評審和 exp06 的特徵標註 |
| 用 Brier 分數當獎勵的強化學習（GRPO、ReMax） | 第 7 章未來工作、PhD 方向 | 這是前沿做法（[Turtel 等，TMLR 2025](https://arxiv.org/abs/2505.17989v4)；[Mantic，2026](https://www.thinkingmachines.ai/news/training-llms-to-predict-world-events/)），但它們用了 1 萬到 11 萬題，exp03 只有數百題。exp03 的資料正好是將來的訓練起點 |
| 學派方向的 activation steering | exp06 第三部分（可選，只在 dev） | prompting 和微調之間的第三條路；依 [AxBench](https://proceedings.mlr.press/v267/wu25a.html) 的結果，預期會輸給 prompting |

外審問「為什麼不用更新的模型」時的回答：更新的模型沒有公開的 SAE，也幾乎沒有它沒看過、又已經結算的市場可以回測；它們放在 exp05 的前瞻預測裡當參考。

## 可解釋性：用 SAE 看模型內部（exp06）

SAE（稀疏自編碼器）把模型內部的激活拆成幾萬個可以命名的特徵。exp06 用 Qwen 官方公開的 [Qwen-Scope](https://qianwen-res.oss-accelerate.aliyuncs.com/qwen-scope/Qwen_Scope.pdf) 回答兩件事：微調教會的是學派的「概念」還是只有「用詞」，以及微調和 prompting 在模型內部差在哪裡。不需要自己訓練 SAE。

| 部分 | 做什麼 | 回答哪個口試問題 |
| --- | --- | --- |
| S0 效度關卡 | 先檢查 SAE 對每種狀態（原模型、加 prompt、加 few-shot、加 LoRA）的重建品質，不過就不報告 | SAE 可信嗎？ |
| 第一部分：特徵量尺 | 用 Qwen3-8B-Base 讀所有組的輸出，算本學派和他學派特徵的比重；只採用在「不含關鍵字的改寫」上也分得出學派的概念特徵 | 關鍵字分數量得到推理嗎？（第三種量尺，和評審、人工評分對照） |
| 第二部分：機制 | 把各組的輸出餵回產生它的模型，看內部的本學派與他學派特徵；比較 LoRA 和 few-shot 各增加了哪些特徵，每個特徵對到 L3 條目 | 微調到底改了什麼？為什麼比 CoT 好（或不好）？ |
| 第三部分（可選） | 關掉特徵看分數掉多少；用特徵做 steering；用特徵篩訓練資料 | 這些特徵真的被模型用到了嗎？ |

事先登記三個假設：概念特徵分數和評審的學派忠實度正相關（S-H1）；LoRA 的概念特徵分數高於 few-shot（S-H2）；LoRA 內部的他學派特徵少於 few-shot（S-H3）。其餘都是探索性。

SAE 研究近年有不少負面結果（[Kantamneni 等，ICML 2025](https://arxiv.org/abs/2502.16681)；[AxBench，ICML 2025](https://proceedings.mlr.press/v267/wu25a.html)），所以每個量化結論都附上不用 SAE 的基準（difference-of-means、線性探針），並用兩種稀疏度的 SAE 和 27B 對話版的 SAE 複驗。每個學派的特徵卡片（對到 L3 條目的驅動因素、摩擦、政策、訊號）放在附錄，是論文可解釋性的主要展示。

成本：8B 的 GPU 不到一天；Opus 標註約 500 次，分幾天用你的額度。第一部分要和 exp01 一起在 12/6 凍結前登記，第二部分 1/17 完成。

## 各實驗設計

八個實驗都先在 dev 或校準資料上做；保留集只在你登記、凍結之後跑一次。exp01 已登記，其餘是草稿，完整規格在 repo 的 [prereg](https://github.com/Bellafc/macro-mosaic/tree/main/prereg) 和 [prereg\_drafts](https://github.com/Bellafc/macro-mosaic/tree/main/research/prereg_drafts)。

| 實驗 | 資料 | 保留集 | 主要假設 | 誰做 | 截止 |
| --- | --- | --- | --- | --- | --- |
| exp01 微調 vs prompting（Qwen3-8B） | 96 個開題時的保留事件；dev 用歷史事件；adapter 用同一批軌跡重新訓練 | 96 個 test 事件 | LoRA（C）的學派一致性勝過調到最強的 prompting（B，可開模型自己的 thinking），三個學派各檢定一次並做 Holm 校正 | agent 訓練 adapter、調 dev，你跑 test | 12/6；人工評分 12/20 |
| exp01 的 D 組（Opus 5.5） | 96 個 test 事件，只產生、不評分（修正案 3） | — | 參考組，不做假設檢定 | 你在自己電腦上跑，不需 GPU | 原始 prompt 和 test 事件一到就能跑 |
| exp06 SAE 機制分析 | exp01 各組的輸出；探針文本（訓練軌跡、不含關鍵字的改寫） | 96 個 test 事件 | 概念特徵分數和評審相關；LoRA 的概念特徵高於 few-shot；LoRA 內部的他學派特徵較少 | agent 做 S0 關卡和選特徵，你登記並跑 test | 量尺 12/4；機制 1/17 |
| exp01b 前沿複驗（Qwen3.5-27B） | 同 exp01，底座換成 Qwen3.5-27B；用它的對話版 SAE 複驗 exp06 | 96 個 test 事件 | 同 exp01 的 H1；另報告兩種底座的差距 | agent 做可行性測試和 dev，你跑 test | 測試 11/2；決定 11/20；結果 1/24 |
| exp03 已結算總經市場 | Kalshi 經濟類 2025-05 起，加上當時已公布的總經資料（ALFRED 歷史版本） | 2026 年結算的事件 | 等權合成的 RPS 低於最佳單一學派；另檢定微調學派勝過 prompt 學派、分歧和信心能否預示誤差，以及理論多樣性是否勝過人設、多模型、重複抽樣（H8） | agent 建資料，你登記並跑 test | 登記 11/25；結果 12/20 |
| exp02 歷史類比檢索（agent 的 L2 工具） | 141 個事件，只用當時已知的資料；敘事改成只寫觸發當下（避免事後描述洩漏結果） | 2005 年以後的事件 | Mahalanobis 勝過 Euclidean（History Rhymes 的做法） | agent 做 dev，你跑 test | 1/31 |
| exp07 有根據的 agent 是否忠實（新，RQ2） | 開發集和 2025 年以前的歷史事件；A-agent、C-agent 的工具軌跡 | 不需要：不用結果資料，也不碰 exp03 測試期 | 證明有效、能追溯到 L0–L4；改掉一個工具結果（L1 數據或 L2 類比）時，相關步驟和預測會跟著改；證明宣稱的機制在模型內部有對應的特徵 | agent 做，你登記 | 跑之前登記（P1） |
| exp04 一致性 | exp03 的 CPI 月增／年增、FOMC 題 | 2026 年的事件 | 合成比單一學派更一致；投影到一致集合後分數變好 | agent → 你 | 2/7 |
| exp05 即時前瞻（可選） | 每週對還沒結算的市場預測，含 Opus 5.5，以及只用 prompt 的 Qwen3.8-27B、Gemma 4 31B | 全部 | 描述性（樣本小） | 你 12/1 決定做不做 | 3/31 |

算力需求不大：三個 8B adapter 各約半小時，GPU 生成和 SAE 分析加起來估計 15–40 小時，用 48 GB 的卡；只有 Qwen3.5-27B 要 80 GB 的卡。pod 由 Claude Code 指揮按需開、跑完自己關機；exp02 只要 CPU，Opus 走你的訂閱額度。

## 口試問題對照

外審最可能問的 21 個問題，現在每一個都有對應的實驗或明說的限制。第一題就是開題時教授問過的。

| 可能的問題 | 答案在哪裡 |
| --- | --- |
| 為什麼微調，而不是用 CoT？ | exp01 H1（C 對最強的 B，B 可開模型自己的 thinking）；exp03 H5（預測準確度上的對照） |
| 開題之後為什麼換了底座模型？ | 修正案 4：adapter 沒保存、本來就要重訓；選 Qwen3-8B 是因為有公開 SAE、回測窗口長、工具成熟；原始資料還在就做 Qwen2.5 重現組 |
| 為什麼不換更新、更大的模型？ | exp01b（Qwen3.5-27B，有公開 SAE 的最新模型）；更新的模型沒有 SAE、也幾乎沒有沒看過的已結算市場，只放在 exp05 |
| 關鍵字分數真的量得到推理嗎？ | exp01 修正案 2：盲評、兩位人工評審、兩者的相關；exp06 的 SAE 特徵量尺 |
| 微調教會的是學派的概念，還是只有用詞？ | exp06 S-H2：在不含關鍵字的文字上也分得出學派的概念特徵；和評審、人工評分對照 |
| SAE 的結果可信嗎？ | exp06 的 S0 關卡、不用 SAE 的基準、兩種稀疏度、27B 對話版 SAE 複驗、人工抽查標籤 |
| 模型扮演一個學派時，內部發生了什麼？ | exp06 的特徵卡片（對到 L3 條目）；內部污染（S-H3） |
| 為什麼要好幾個學派？合成有用嗎？ | exp03 H1、exp04 H1 |
| 學派意見相反時怎麼辦？ | 本體論 L3 規則：並列、不選邊；exp03 H6 檢驗分歧能否預示誤差 |
| agent 的解釋是真的照著推理，還是事後編的故事？ | exp07：反事實工具結果（行為）、SAE 證明忠實度（模型內部）、證明有效性（Proof.check） |
| 理論多樣性比其他多樣性來源（人設、多模型、重複抽樣）好嗎？ | exp03 H8，集成大小相同 |
| 單一個預測可以信多少？看得懂它怎麼來的嗎？ | 每個預測的推理證明（回溯到 L0–L4）和分析信心；exp03 H7 檢驗信心是否有用 |
| 模型會不會早就看過答案？ | 只用模型釋出後才結算的市場（Qwen3-8B：2025-05 起）；只用當時已知的資料；訓練種子事件的日期稽核；可選的 exp05 |
| 結果在統計上可靠嗎？ | 事先登記、以事件為單位重抽樣、Holm 校正 |
| 和市場、簡單基準比起來如何？ | exp03：市場價格、歷史分布、均勻分布；H4 檢定模型有沒有市場以外的資訊 |
| 檢索方法比簡單相似度（History Rhymes）好嗎？ | exp02 H1–H3 |
| 35 維、141 個事件，共變異數怎麼估？ | exp02 的做法：每月序列加收縮估計 |
| 為什麼是這三個學派？ | 第 4 章的設計理由；L3 條目的文獻來源 |
| Stage 4 的配置去哪了？ | 「需要重新設計的地方」第一列；第 7 章 |
| 訓練資料是 GPT-4o 合成的，會不會帶進老師的偏誤？ | 第 4 章限制；exp01 的 T 組（如果有跑）；exp06 第三部分的訓練資料稽核 |
| 這份研究怎麼用 AI？ | 從 AI 使用紀錄寫成的聲明 |

## AI 使用與學術誠信

PolyU 的 GenAI 指引要求標明 AI 產生的內容，也不允許讓 AI 代寫。所以 agent 只寫程式、跑實驗、出結果表，論文內文由你寫。

- **有紀錄**：agent 的每一項產出都記在 repo 的 `research/AI_USE_LEDGER.md`。論文的 AI 使用聲明，直接從這份紀錄寫。
- **確認性證據只有一種來源**：事先登記、凍結、由你親手執行的結果。其他結果在論文裡一律標為探索性。
- **計畫和實際有出入時**：當天在 LOG 記一筆偏差（原本預期、實際結果、影響、建議）。還是草稿的實驗直接改，並同步更新設計文件；已登記的只能寫修正案，由你在正式結果出來前登記；有正式結果後，確認性的部分不再改，偏差照實寫進論文。
- **Opus 只用來評估**：Claude 消費者條款不允許用服務訓練 AI 模型，所以 D 組輸出和評審分數只做評估，不當任何模型的訓練資料。透過 Claude Code 的 `setup-token` 自動執行，是官方文件支援的用法。
- **這份設計本身也是 AI 協助的規劃**，聲明裡要涵蓋。研究問題的取捨和最後的決定，是你和張老師的。
- **學校指引沒有專門針對學位論文的條款**：送審前問張老師，系上有沒有規定的聲明格式。
- **團隊程式碼與資料授權**：pmpol（包括 L0–L5 分層、推理證明、分析信心）是團隊的程式碼，論文要標明來源。Kalshi 的條款不允許散布彙編後的資料，資料可得性聲明只能附 ID 和重建程式。

## 待決定事項

這 11 件事會改變實驗範圍或時程，建議下週和張老師見面時一次決定。同一次也問清楚：系上初審大概要多久、什麼時候交。

| 編號 | 要決定的事 | 建議 | 為什麼重要 | 最晚 |
| --- | --- | --- | --- | --- |
| D1 | 送審日期，以及 Normal Period 確切結束日 | 2027-06-15 送審 | 往回推決定 GSB/2B 和所有實驗的截止日 | Nov 8, 2026 |
| D2 | Stage 4 配置與回測：放進討論，還是做 2025–26 的小型示範 | 放進討論當未來工作；題目拿掉「Cross-Asset Allocation」 | 回測有偷看問題，示範至少多 3–4 週 | Nov 8, 2026 |
| D3 | 要不要投 IJCAI 2027（1/4 摘要、1/11 全文） | 投，內容是 exp01 加 exp06（或 exp03） | 4/21 若被接收，可以省掉系上初審；但 11 月就要開始跑 | Nov 8, 2026 |
| D4 | 有沒有外部時間限制（例如 PhD 入學日期） | 先說明有沒有 | 會讓 D1 提前 | Nov 8, 2026 |
| D5 | 第二位人工評審是誰 | 一位有經濟學背景的同學 | exp01 的評審效度需要兩人獨立評分 | Dec 1, 2026 |
| D6 | 要不要做即時前瞻 exp05 | 看 exp03 的流程 12/1 能不能跑通 | 至少要累積 3 個月的即時資料 | Dec 1, 2026 |
| D7 | 底座模型：Qwen3-8B 當主力；Qwen3.5-27B 做前沿複驗（exp01b） | 照建議；27B 等 Task S4 試跑後 11/20 再定 | 主力決定 exp01、exp03、exp06 用的模型，訓練 adapter 前要定；27B 要 80 GB 的卡、多 2–3 週 | Nov 8, 2026 |
| D8 | 要不要用決策模型（Kev-27B）當第二位評審和即時預測的決策頭 | 可選；只當量測工具 | 開源、可重現、每級都有機率；但校準說法要自己驗 | Dec 1, 2026 |
| D9 | 誰審核 L3 學派條目（兩人規則） | 你提出，張老師或一位經濟學背景的人審 | 評審的學派定義和論文的 L3 事實要一致，凍結前就要定 | Nov 29, 2026 |
| D10 | exp06 SAE 的範圍 | 做第一、二部分；第三部分時間夠再做 | 第一部分要在 exp01 凍結前登記 | Nov 29, 2026 |
| D11 | 訓練資料：開題的 1,500 條 GPT-4o 軌跡還在嗎；不在的話用哪個老師模型重產；要不要做 Qwen2.5 重現組（A7、C7） | 還在就沿用並做重現組；不在就用 GPT-4o（若還能用）或授權允許拿輸出訓練的開源模型 | 決定 adapter 什麼時候能訓練；Opus 不能當老師 | Nov 8, 2026 |

## 開始在 RunPod 上跑

前五項做完，Claude Code 就能開第一台 GPU 跑 Task S（試跑推論、訓練、SAE 和 27B，不需要你的資料）。資料和決定到齊後，agent 才開始訓練 adapter 和跑 exp01。指揮的規則和設定步驟在 repo 的 `ops/ORCHESTRATOR.md`。

- [ ] **RunPod**：建立這個專案專用的 API key；在 Secrets 建 `claude_oauth_token`（自己電腦跑 `claude setup-token` 的結果）和 `github_token`（GitHub fine-grained token，只給這個 repo，Contents 可讀寫）
- [ ] **RunPod**：在有 H100／A100 80GB 的資料中心建 200 GB 的 network volume，記下 volume id
- [ ] **GitHub**：在 repo 安裝 Claude GitHub App，確認 Claude Code 看得到它
- [ ] **claude.ai/code**：建一個 cloud environment（Trusted 網路），在 Network secrets 加 `rest.runpod.io` 的 Bearer key；key 不要貼進對話或環境變數
- [ ] 在這個環境開一個 session，請它讀 `ops/ORCHESTRATOR.md` 並開 Task S（80 GB 的卡，4 小時）
- [ ] **今天就能做**：原始 prompt 和 96 個 test 事件一備齊，在自己電腦上跑 `mosaic pregen --exp exp01 --arms D --split test`（Opus 5.5，不需 GPU）
- [ ] 確認開題的 1,500 條 GPT-4o 訓練軌跡還在（D11）；連同 test、dev 事件、episode 資料庫、開題時的生成結果，上傳到 volume 的 `/workspace/assets/`
- [ ] 開題時的原始 system prompt、user prompt 格式和關鍵字表 commit 進 repo（`configs/prompts/`、`configs/lexicons.toml`）
- [ ] 讀修正案 4 草稿，移到 `prereg/` 登記；把 backlog 的 `train` 列改成 go
- [ ] 和張老師見面：決定 D1–D4、D7、D9–D11，確認 Normal Period 截止日和系上初審時程
- [ ] 檢查畢業先備條件：GPA、兩年的 Research Seminar 報告、National Education 課程
- [ ] 讀一遍 `configs/judge.toml` 和 `kb/L3/schools.yaml` 裡的學派定義，補上文獻原文引文，凍結前要你確認
- [ ] 決定要不要跑老師組（T 組，約 15 美元）

## 來源

- [PolyU RPg Handbook 10.1 Thesis Requirement](https://www.polyu.edu.hk/gs/rpghandbook/section10-1)
- [PolyU RPg Handbook 10.2 Submission of Initial Thesis](https://www.polyu.edu.hk/gs/rpghandbook/section10-2)
- [PolyU RPg Handbook 10.3 Board of Examiners](https://www.polyu.edu.hk/gs/rpghandbook/section10-3)
- [PolyU RPg Handbook 10.4 Examination Process](https://polyu.edu.hk/gs/rpghandbook/section10-4)
- [PolyU RPg Handbook 10.5 Submission of Approved Final Thesis](https://www.polyu.edu.hk/gs/rpghandbook/section10-5)
- DSAI RPg Programme Document 2025/26（你上傳的 PDF，5.1–5.9 節）
- [PolyU Student Guide on the Use of GenAI（2026-01-05 修訂）](https://www.polyu.edu.hk/ar/docdrive/polyu-students/Student-guide-on-the-use-of-GenAI-revised-260105.pdf)
- [Claude Consumer Terms of Service（第 3 條）](https://www.anthropic.com/legal/consumer-terms)
- [IJCAI 2027 重要日期（OpenCurious 彙整，以官網為準）](https://www.opencurious.com/ai-conference-deadlines/ijcai-2027)
- [KDD 2027 重要日期（OpenCurious 彙整，第二輪日期尚未公布）](https://www.opencurious.com/ai-conference-deadlines/kdd-2027)
- [Qwen3.8-27B 規格整理（Morph，第三方）](https://www.morphllm.com/qwen-3-8)
- [Kev：可自行訓練的 Jev 式決策模型（GitHub）](https://github.com/jaredpalmer/kev)
- [Ollama 支援 Jev 式決策模型（2026-09-29）](https://ollama.com/blog/ollama-now-supports-jev-style-decision-models)
- [Turtel 等，Outcome-based Reinforcement Learning to Predict the Future（TMLR 2025）](https://arxiv.org/abs/2505.17989v4)
- [Mantic × Thinking Machines，Training LLMs to Predict World Events（2026）](https://www.thinkingmachines.ai/news/training-llms-to-predict-world-events/)
- pmpol `docs/OSS_SURVEY.md` 第十三部分（團隊內部文件，決策模型調研）與 `kb/README.md`（L0–L5 分層）
- [先前的對話：畢業答辯準備要求](https://claude.ai/chat/272fafe7-34de-4dc9-8759-1e130d5f2a3d)
- [實驗 repo（Bellafc/macro-mosaic）](https://github.com/Bellafc/macro-mosaic)
- [Qwen-Scope 技術報告（Qwen Team，2026-04-30）](https://qianwen-res.oss-accelerate.aliyuncs.com/qwen-scope/Qwen_Scope.pdf)
- [Qwen-Scope SAE 合集（Hugging Face）](https://huggingface.co/collections/Qwen/qwen-scope)
- [SAE-Res-Qwen3.5-27B-W80K-L0\_50 模型卡](https://huggingface.co/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50)
- [andyrdt/saes-qwen2.5-7b-instruct（Qwen2.5-7B-Instruct 的第三方 SAE）](https://huggingface.co/andyrdt/saes-qwen2.5-7b-instruct)
- [Li 等，Training Superior Sparse Autoencoders for Instruct Models（FAST，2025）](https://arxiv.org/abs/2506.07691)
- [He 等，Discovering Millions of Interpretable Features with Sparse Autoencoders（Qwen3-Instruct SAE，2026）](https://arxiv.org/abs/2606.26620v1)
- [Gemma 4 模型卡](https://ai.google.dev/gemma/docs/core/model_card_4)
- [Gemma 版本紀錄（Gemma 4 發布日、Gemma Scope 2）](https://ai.google.dev/gemma/docs/releases?hl=en)
- [Announcing Gemma Scope 2](https://www.greaterwrong.com/posts/YQro5LyYjDzZrBCdb/announcing-gemma-scope-2)
- [Qwen3.5-27B 規格（ApX，第三方）](https://apxml.com/models/qwen35-27b)
- [Unsloth：Qwen3.5 微調指南](https://unsloth.ai/docs/models/qwen3.5/fine-tune)
- [The Best Open Source LLMs（2026 年 10 月，Morph）](https://www.morphllm.com/best-open-source-llm)
- [Chen 等，Persona Vectors（2025）](https://arxiv.org/abs/2507.21509)
- [Minder 等，Narrow Finetuning Leaves Clearly Readable Traces in Activation Differences（ICLR 2026）](https://arxiv.org/abs/2510.13900)
- [Kantamneni 等，Are Sparse Autoencoders Useful?（ICML 2025）](https://arxiv.org/abs/2502.16681)
- [Wu 等，AxBench（ICML 2025）](https://arxiv.org/abs/2501.17148v2)
- [Claude Code：Use Claude Code in the cloud](https://code.claude.com/docs/en/claude-code-on-the-web)
- [Claude Code：Configure cloud environments（network secrets）](https://code.claude.com/docs/en/cloud-environments.md)
- [RunPod REST API：Create a Pod](https://docs.runpod.io/api-reference/pods/POST/pods)
- [RunPod：Secrets](https://docs.runpod.io/pods/templates/secrets.md)
- [RunPod：Pod 環境變數](https://docs.runpod.io/pods/templates/environment-variables.md)
