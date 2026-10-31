# 論文草稿（AI 協助）：文獻綜述、Related Work、方法論

2026-10-31，由 Claude Code 依你的要求寫的第一版草稿。**這些是 AI 產生的論文內文**，已記在
`research/AI_USE_LEDGER.md`。PolyU 的 GenAI 學生指引要求標明 AI 產生的內容、學生負全責；`THESIS_DESIGN.md` §6
原本的規則是 agent 不寫論文內文，這次是你明確要求的例外。建議的用法：把它們當作「有來源的鷹架」，逐段對照
原文獻後用自己的話重寫；送審前的 AI 使用聲明要涵蓋這份草稿。

2026-10-31 補記：作者已確認，AI 產生的內容只要自己重寫一遍即可使用。重寫後仍請在送審的 AI 使用聲明中載明
這份草稿的角色（鷹架與查證過的書目），並保留 `AI_USE_LEDGER.md` 的紀錄。

## 檔案

| 檔案 | 內容 | 字數 |
|---|---|---|
| `ch2_literature_review.md` | 第 2 章「背景與文獻」：學派原典（Keynesian／New Keynesian、Monetarist、Austrian、傳導管道）；金融與總經的 LLM agent（濃縮開題的 survey）；LLM 用於總經；評估與資料洩漏；prompting、LoRA、蒸餾、微調 vs ICL、persona 忠實度；量測推理的三種工具（詞典、LLM 評審、SAE 與 model diffing）；評分規則、校準、合成、一致性、比較檢定；預測市場與人類預測；LLM 預測；類比預測、Mahalanobis／收縮估計、即時資料；分析標準；五個研究缺口 | ≈ 6,200 |
| `ch2_related_work.md` | 第 2 章末「Related work」：七項判準；對照最接近的系統（TradingAgents／FinCon、EconAgent、FOMC In Silico、Simulated SPF、persona prompting、Halawi／Turtel／Mantic、ForecastBench／KalshiBench、Paleka、History Rhymes、Minder／persona vectors／SAE diffing）；比較表；本論文不主張什麼 | ≈ 3,000 |
| `ch3_methodology.md` | 第 3 章「研究設計與方法」：RQ 與證據邏輯；問題定式與符號；L0–L5 知識架構、推理證明、分析信心；資料（episode DB、即時狀態、訓練軌跡、96 個 test 事件、市場題庫）；學派 agent（底座、LoRA 配方、A/B/C/D/T/A7/C7 各組、文字指標公式、評審與人工驗證、H1–H4、exp01b）；SAE 工具（S0 關卡、探針集、特徵選取與 feature cards、分數與 DiffMean 基準、Part II、S-H1–3）；類比檢索（exp02）；預測／合成／校準（exp03 H1–H7）、一致性（exp04）、前瞻（exp05）；統計協定；效度威脅；重現性、治理與 AI 使用；設計狀態 | ≈ 8,300 |
| `references.bib` | 200 筆 BibTeX：第一節是草稿引用的 179 筆，第二節是查證過但尚未引用的 21 筆。每筆 `note` 欄寫明查證的原始來源 | — |
| `CITATION_VERIFICATION.md` | 逐筆查證紀錄：key、狀態、cluster、原始來源網址、備註；以及查證時發現的更正清單 | — |
| `references/*.bib` | 同一份書目依主題分成六個檔（預測／市場／校準；可解釋性與評審；微調與 prompting；經濟與金融；統計；開題的金融 agent），LaTeX 用 `\bibliography{references/forecasting_markets_calibration,...}` 或直接用合併版 `references.bib` | — |
| `LIBRARY.md` | 文獻庫索引：每篇一行（key、作者、年份、標題、出處、查證狀態、連結、`#tags`）。把 `research/thesis_drafts/` 當 Obsidian vault 打開就能用標籤篩選；`.bib` 可直接匯入 Zotero（裝 Better BibTeX 可保留 key） | — |

引用格式用 natbib（`\citep{}`、`\citet{}`、`\citealp{}`），直接可貼進 LaTeX。Markdown 裡的公式用 `$…$`。

## 查證結果

四個查證 sub-agent（預測／市場／校準；可解釋性；微調 vs prompting；經濟與金融）逐筆對照原始出處（出版社或 DOI
記錄、arXiv、ACL Anthology、NeurIPS／ICLR／PMLR 論文集、官方技術報告與 model card、圖書館目錄）。草稿引用的 179 個
key：**163 筆 VERIFIED、5 筆 PARTIAL**（只缺頁碼之類的一個欄位：Platt 2000、Naeini 2015、Tetlock 2005、Holm 1979、
Friedman 1956）、**11 筆沿用開題書目未重新抓取**（FinMem、FinAgent、FinGPT、FinBen、FinanceBench、FinRL、FinRL-Meta、
Hambly 2023、Russell & Norvig、Wooldridge & Jennings、Xing 2025）。**沒有任何一筆查無此文**；原本記憶有誤的幾篇都改成
真實存在的論文，或改寫句子。

查證時發現、需要你知道的更正（完整清單在 `CITATION_VERIFICATION.md`）：

- **exp04 草稿**把「保證套利等於到一致集合的距離」歸給 Shi & Zhai (2026)。實際上 Shi & Zhai 的論文是
  *Combinatorial Arbitrage in Prediction Markets*（arXiv 2610.23517，凸包外的價格可套利、整數規劃組合）；
  「距離」那個陳述對應的是 Andrews & Sarkar, *Dutch Books for Language Models*（arXiv 2609.02797）。草稿兩篇都引、
  各引其所言；`research/prereg_drafts/exp04_coherence.md` 的歸屬請你改。
- 「Le (2026)」其實是 Nam Anh Le 關於 Kalshi／Polymarket **人類交易者**價格校準的論文，不是 LLM 預測；已改放在
  預測市場校準（L2 基準率）的脈絡。
- 「Gebele & Matthes (2026)」有三位作者（Gebele, Till, Matthes），是 REALM 2026 workshop 論文，講同質 LLM 預測民調的
  多樣性；請寫成 Gebele et al.
- Paleka et al. (2026) 是 *Pitfalls in Evaluating Language Model Forecasters*（ICLR 2026；評估陷阱、時間洩漏），
  不是一致性檢查的續篇；Paleka et al. (2025) 的作者是 Paleka, Pallavi Sudhir, Alvarez, Bhat, Shen, Wang, Tramèr。
- Turtel et al. (2025) 作者是 Turtel, Franklin, Skotheim, Hewitt, Schoenegger（TMLR，2025 年 12 月）。
  Mantic 2026 是 Thinking Machines Lab 網站上的 guest post（Jeen, Aitchison & Mantic），非同儕審查。
- Persona vectors (Chen et al.) 是 **NeurIPS 2026**，不是 ICLR 2026；Paulo & Belrose 已發表在 ICLR 2026；
  Minder et al. ICLR 2026 確認。Cunningham et al. 的 ICLR 2024 版第一作者是 Huben（key `huben2024sparse`）。
- Qwen-Scope：arXiv 2605.11887（2026-05），Qwen Team；Qwen3-8B 的 SAE 是在 **base** 模型上訓練的（和 exp06 草稿的
  假設一致），Qwen3.5-27B 的 SAE 是在對話版上訓練的。Qwen3.5 到 2026-10-31 為止沒有文字模型的技術報告，引官方
  發布頁與 model card。
- FAST（Li et al.）改名 *Breaking the Block*（ICML 2026）；Smith et al. 2025 是 Alignment Forum 文章；
  Faria-e-Castro & Leibovici 的真實標題是 *Artificial Intelligence and Inflation Forecasts*（St. Louis Fed Review
  2024）；Bybee 的 arXiv 2305.02823 是舊標題；History Rhymes 是 IEEE BigData 2025，五位作者；FOMC In Silico 有
  2025-10 與 2026-07 的新版草稿，數字不同，草稿沒有引用任何數字。

## 查證時新發現、已補進草稿的重要文獻

- Hansen et al. (2025) *Simulating the Survey of Professional Forecasters*（LLM 預測者 persona 餵即時總經資料，重現
  SPF 的準確度與分歧）；Iadisernia et al. (ICAIF 2025) persona prompting 對總經預測沒有準確度增益、且預測同質
  —— 這兩篇是 exp03 最近的對照，也是「用微調而不是 prompt 來灌輸觀點」最直接的動機。
- Ludwig, Mullainathan & Rambachan (Annual Review of Economics 2026)：LLM 用於預測要「無訓練洩漏」、用於量測要有
  驗證樣本 —— 正好對應 exp03 的時間窗和 exp01 的人工驗證評審。Glasserman & Lin (JFDS 2024)、Sarkar & Vafa (2024)：
  LLM 的 look-ahead bias 無法靠 prompt 消除。
- Wang et al. (ICLR 2026) SAE diffing 找到微調後的 persona 特徵；Galichin et al. (EACL 2026) 微調主要改變既有特徵的
  觸發而非新增特徵；Minder et al. (NeurIPS 2025) sparse diffing 的假象；Shuttleworth et al. (NeurIPS 2025) LoRA 的
  intruder dimensions；Heap et al. (ICLR 2026) 自動特徵解釋分不出訓練過和隨機初始化的模型 —— exp06 的方法段落已引用。
- Lin et al. (ICLR 2024, URIAL) 對齊主要改變風格 token；Zhao et al. (ICLR 2025) ICL 落後於指令微調；Rozado
  (PLOS ONE 2024) 用 SFT 做出左／右傾的 LLM；Wang et al. (Findings ACL 2024, RoleLLM) 角色微調 vs 角色 prompt。
- Diercks et al. (FEDS 2026-010) Kalshi 總經市場的準確度（用 Kalshi 當基準的官方依據）；Jeddi et al. (Phil. Trans.
  R. Soc. B 2026) LLM 群體預測的相關性限制合成增益；Kapoor et al. (NeurIPS 2024) LoRA 微調可教會校準；
  Dendramis et al. (JRSS-A 2020) 相似度（最近鄰）總經預測。

## 寫作上的取捨（請核對）

- 方法論以 2026-10-31 的設計為準：exp01 與修正案 1–3 已登記；修正案 4、exp01b、exp02–06 仍是草稿，文中都標明
  「draft」。登記後要把狀態和任何改動同步回草稿。
- 內文完全沒有引用實驗結果（結果章節是你的），只有開題 Table 4.3 的定性描述（Austrian 基礎模型用詞最少）。
- 貢獻的措辭維持 THESIS_DESIGN §2 的強度；「to the author's knowledge」的新穎性主張都限定在具體的組合上。
- 風格：沒有 em-dash 構句、沒有模板式 AI 用語；英式學術英文。
- pmpol 的 L0–L5、proof、confidence、coherence projection 一律寫成團隊程式碼（team code），沒有當成文獻引用。

## 下一步建議

1. 逐段核對後改寫（尤其是對他人論文的描述與每一個數字）；把 `references.bib` 併進論文的 LaTeX 專案。
2. 修正 `research/prereg_drafts/exp04_coherence.md` 的 Shi & Zhai 歸屬（見上）。
3. 和張老師確認系上對 AI 使用聲明的格式；把這份草稿列入聲明。
4. 第 1 章（動機、與開題的差異）、第 4–6 章的結果與討論、第 7 章限制，由你在實驗完成後撰寫。
