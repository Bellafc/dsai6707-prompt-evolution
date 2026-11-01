# 論文草稿（AI 協助）：文獻綜述、Related Work、方法論

2026-10-31，由 Claude Code 依你的要求寫的第一版草稿。**這些是 AI 產生的論文內文**，已記在
`research/AI_USE_LEDGER.md`。PolyU 的 GenAI 學生指引要求標明 AI 產生的內容、學生負全責；`THESIS_DESIGN.md` §6
原本的規則是 agent 不寫論文內文，這次是你明確要求的例外。建議的用法：把它們當作「有來源的鷹架」，逐段對照
原文獻後用自己的話重寫；送審前的 AI 使用聲明要涵蓋這份草稿。

2026-10-31 補記：作者已確認，AI 產生的內容只要自己重寫一遍即可使用。重寫後仍請在送審的 AI 使用聲明中載明
這份草稿的角色（鷹架與查證過的書目），並保留 `AI_USE_LEDGER.md` 的紀錄。

**2026-11-01 改版：對齊三個新 RQ。** 你在 11-01 採用了新的總問題和三個 RQ（同一個設計的三個角度：模型內部、
它說了什麼、它有多確定），第三章也改成「資料與工具」。三份草稿、書目和文獻庫都已對齊新設計。改了什麼、
寫進草稿時做了哪些假設、哪些需要你確認，請先看 `NOTES_2026-11-01_zh.md`。

## 檔案

| 檔案 | 內容 | 字數 |
|---|---|---|
| `ch2_literature_review.md` | 第 2 章「背景與文獻」：學派原典；金融與總經的 LLM agent；評估與資料洩漏；工具與根據（2.3.4）；prompting、LoRA、蒸餾、微調 vs ICL、persona 忠實度、agent 訓練：從模仿到可驗證獎勵（2.4.6）；量測推理的三種工具與推理忠實度（2.5.4）；評分規則、校準、合成與多樣性來源、一致性、比較檢定；預測市場與人類預測；LLM 預測；類比預測與即時資料；本體論、溯源與分析標準（2.9）；按三個 RQ 排列的八個研究缺口；表 2.1 各節對應哪個 RQ | ≈ 8,500 |
| `ch2_related_work.md` | 第 2 章末「Related work」：按三個角度排列的十項判準；多觀點的總經推理；RQ1 微調灌輸了什麼、改了模型內部什麼；RQ2 有根據、可稽核、忠實的 agent 與類比檢索；RQ3 預測、預測市場與多樣性來源；十欄比較表；本論文不主張什麼 | ≈ 3,900 |
| `ch3_methodology.md` | 第 3 章「研究設計、資料與工具」，加上第 4–6 章的方法：總問題、三個角度與析因設計；記號；L0–L5 知識架構、證明、分析信心；資料；L0–L2 工具與 agent 迴圈；prompt、SFT、RFT、RL；RQ1（exp01、exp01b、agent arms、exp06）；RQ2（exp02、exp07）；RQ3（exp03 含 H8、exp04、exp05）；統計協定；效度威脅；重現性、治理與 AI 使用 | ≈ 12,800 |
| `NOTES_2026-11-01_zh.md` | 這次改版的內容、寫進草稿的八個假設（請確認）、依新 RQ 更新的論文評估、pmpol 本體論的使用狀況，以及兩份原始評估的全文 | — |
| `CITATION_VERIFICATION.md` | 逐筆查證紀錄：key、狀態、cluster、原始來源網址、備註；以及查證時發現的更正清單 | — |
| `verification/` | 查證代理的工作紀錄：共用說明，以及 A–D、G–J 各群的逐筆紀錄（讀了哪個原始頁面、核對了什麼、摘要原句） | — |
| `references/*.bib` | 同一份書目依主題分成十個檔（預測／市場／校準；可解釋性與評審；微調與 prompting；經濟與金融；統計；開題的金融 agent；工具型 agent 與訓練；忠實度與可稽核性；集成多樣性；本體論、溯源與分析標準），共 280 筆（草稿引用 261 筆、查證過但尚未引用 19 筆），每筆 `note` 欄寫明查證的原始來源；LaTeX 用 `\bibliography{references/forecasting_markets_calibration,...}` 或 `cat references/*.bib > references.bib` | — |
| `LIBRARY.md` | 文獻庫索引：每篇一行（key、作者、年份、標題、出處、查證狀態、連結、`#tags`），每筆都標了 `#RQ1`／`#RQ2`／`#RQ3`。把 `research/thesis_drafts/` 當 Obsidian vault 打開就能依 RQ 或主題篩選；`.bib` 可直接匯入 Zotero（裝 Better BibTeX 可保留 key） | — |

引用格式用 natbib（`\citep{}`、`\citet{}`、`\citealp{}`），直接可貼進 LaTeX。Markdown 裡的公式用 `$…$`。

## 查證結果

**第一輪（2026-10-31）。** 四個查證 sub-agent（預測／市場／校準；可解釋性；微調 vs prompting；經濟與金融）逐筆對照
原始出處（出版社或 DOI 記錄、arXiv、ACL Anthology、NeurIPS／ICLR／PMLR 論文集、官方技術報告與 model card、圖書館
目錄）。當時草稿引用的 179 個 key：163 筆 VERIFIED、5 筆 PARTIAL（只缺頁碼之類的一個欄位：Platt 2000、
Naeini 2015、Tetlock 2005、Holm 1979、Friedman 1956）、11 筆沿用開題書目未重新抓取（FinMem、FinAgent、FinGPT、
FinBen、FinanceBench、FinRL、FinRL-Meta、Hambly 2023、Russell & Norvig、Wooldridge & Jennings、Xing 2025）。

**第二輪（2026-11-01，為三個新 RQ）。** 另外四個查證代理用同一份共用說明，查了四群新文獻：G 工具型 agent 與
agent 訓練、H 忠實度與可稽核性、I 集成多樣性、J 本體論、溯源與分析標準。共 80 筆，其中 16 筆是查證時新發現的文獻：78 筆 VERIFIED、2 筆 PARTIAL（ToolRL 與 Kent 1964 的頁碼），沒有查無此文。

**合計。** 草稿現在引用 261 個 key：243 筆 VERIFIED、7 筆 PARTIAL、11 筆沿用開題書目；書目總共 280 筆。 **兩輪都沒有任何一筆查無此文**；原本記憶有誤的幾篇都改成真實存在的論文，或改寫句子。

第一輪查證時發現、需要你知道的更正（完整清單在 `CITATION_VERIFICATION.md`）：

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

第二輪查證時發現、已照原文改正的地方：

- **Davis-Stober et al. (2014)** 的結論是「群眾平均非常穩健」：即使判斷有偏誤又彼此相關，也幾乎要確定挑到高手，
  個人才可能贏過平均。我原本寫成「要滿足條件群眾才有智慧」，方向寫反了，已改正。
- **Kuncheva & Whitaker (2003)** 的結論是多樣性指標在實務上建構集成的用處存疑，已照原文改寫。
- **Wang et al. (NAACL 2024)** 的多人設協作只在 GPT-4 上出現，GPT-3.5 和 Llama2-13b 都沒有，所以不能直接拿來支持
  8B 模型的人設多樣性；草稿已加註。
- **Lightman et al. (ICLR 2024)** 的「過程監督勝過結果監督」只在 MATH 上驗證；**Ameisen et al. (2025)** 的
  attribution graph 是在近似原模型的替代模型上計算的；**Atanasova et al. (ACL 2023)** 的反事實測試、
  **Parcalabescu & Frank (ACL 2024)** 的主張都已照原文重寫。
- **只有 arXiv 版、沒有同儕審查版本**：FireAct、Yuan et al.（RFT）、DeepSeekMath（GRPO）、Lanham et al. (2023)、
  Chen et al. (2025)。引用時請寫成 arXiv preprint。
- Toolformer 的 NeurIPS 版有 9 位作者（多了 Eric Hambro）；DeepSeek-R1 的 Nature 版標題和 arXiv 版不同；Search-R1
  兩個版本的提升幅度不同（24% 與 41%），草稿沒有引用數字。ToolRL（NeurIPS 2025）兩個官方紀錄的頁碼不一致，頁碼
  留空，標為 PARTIAL。
- **Irwin & Mandel (2019)** 的摘要批評的是情報資訊評估方法本身，沒有點名 Admiralty 分級。Admiralty 分級的出處
  改引英國國防部準則 JDP 2-00（2023，內有完整的 NATO 分級表），並加上 Kelly et al. (2025) 對 Admiralty Code 的實驗。
- **Snodgrass & Ahn (1985)** 的第二條時間軸是「交易時間」，也就是事實存進資料庫的時間。把資料版本的公布日期對應到
  這條軸，是論文自己的對應，草稿已寫明。
- **Friedman & Zeckhauser (2012)** 主張分析者應明確評估不確定性，而不是試圖消除它；**Dhami et al. (2015)** 建議情報
  體系定期量化監測預測準確度。草稿已照原文改寫。
- **Kent (1964)** 的 CIA 頁面沒有頁碼，所以頁碼留空，標為 PARTIAL；CIA 1994 年的 Kent 文集重印在 pp. 127–141。
  Toulmin 引的是 1958 年初版。

## 查證時新發現、已補進草稿的重要文獻

第一輪：

- Hansen et al. (2025) *Simulating the Survey of Professional Forecasters*（LLM 預測者 persona 餵即時總經資料，重現
  SPF 的準確度與分歧）；Iadisernia et al. (ICAIF 2025) persona prompting 對總經預測沒有準確度增益、且預測同質。
  這兩篇是 exp03 最近的對照，也是「用微調而不是 prompt 來灌輸觀點」最直接的動機。
- Ludwig, Mullainathan & Rambachan (Annual Review of Economics 2026)：LLM 用於預測要「無訓練洩漏」、用於量測要有
  驗證樣本，正好對應 exp03 的時間窗和 exp01 的人工驗證評審。Glasserman & Lin (JFDS 2024)、Sarkar & Vafa (2024)：
  LLM 的 look-ahead bias 無法靠 prompt 消除。
- Wang et al. (ICLR 2026) SAE diffing 找到微調後的 persona 特徵；Galichin et al. (EACL 2026) 微調主要改變既有特徵的
  觸發而非新增特徵；Minder et al. (NeurIPS 2025) sparse diffing 的假象；Shuttleworth et al. (NeurIPS 2025) LoRA 的
  intruder dimensions；Heap et al. (ICLR 2026) 自動特徵解釋分不出訓練過和隨機初始化的模型。
- Lin et al. (ICLR 2024, URIAL) 對齊主要改變風格 token；Zhao et al. (ICLR 2025) ICL 落後於指令微調；Rozado
  (PLOS ONE 2024) 用 SFT 做出左／右傾的 LLM；Wang et al. (Findings ACL 2024, RoleLLM) 角色微調 vs 角色 prompt。
- Diercks et al. (FEDS 2026-010) Kalshi 總經市場的準確度（用 Kalshi 當基準的官方依據）；Jeddi et al. (Phil. Trans.
  R. Soc. B 2026) LLM 群體預測的相關性限制合成增益；Kapoor et al. (NeurIPS 2024) LoRA 微調可教會校準；
  Dendramis et al. (JRSS-A 2020) 相似度（最近鄰）總經預測。

第二輪：

- **exp07 最接近的前例。** Zhao et al. (ICML 2026) 對 LLM agent 拿到的經驗做受控干預，檢驗決策是否真的依賴它，
  這就是「反事實工具結果」在 agent 層級的對應。Zhao et al. (ICLR 2026, CRV) 用每個推理步驟的計算圖驗證推理，
  是「證明步驟宣稱的機制在模型內部有沒有激活」最接近的前例。Arcuschin et al. (ICML 2026) 在自然提示下也找到不忠實的
  推理；Cohen-Wang et al. (NeurIPS 2024, ContextCite) 用消融找出是哪段脈絡產生了某句話。
- **H6 的前例。** Lahiri & Sheng (J. Applied Econometrics 2010) 證明 SPF 預測者之間的分歧在什麼條件下能代表不確定性；
  Farquhar et al. (Nature 2024) 重複抽樣的語意熵能抓出 LLM 的錯誤答案。
- **H8 的理論依據。** Lamberson & Page (Management Science 2012)：最佳預測群體的組成取決於群體大小，所以 H8 要在
  相同集成大小下比較；Wood et al. (JMLR 2023) 多樣性是集成損失偏差-變異分解裡隱藏的一維；Kim et al. (ICML 2025)
  不同 LLM 的錯誤高度相關；Lyu et al. (AAAI 2025) 重複抽樣的一致性可做校準。
- **agent 訓練。** ToRA (ICLR 2024) 只對推理和動作計算損失、工具輸出當脈絡，並保留有效的取樣軌跡，是「工具結果
  不進損失」和「工具軌跡上做 RFT」的前例；Gorilla (NeurIPS 2024) 用 AST 比對檢查 API 呼叫；另有工具學習
  (ACM Computing Surveys 2025) 與 LLM agent (Frontiers of Computer Science 2024) 兩篇同儕審查的綜述。
- **本體論與溯源。** 英國國防部 JDP 2-00（2023）公開了 NATO 情報分級表；Kelly et al. (Judgment and Decision Making
  2025) 用情報分析師做 Admiralty Code 的實驗；Think-on-Graph (ICLR 2024) 讓 LLM 在知識圖譜上搜尋可追溯的推理路徑；
  Stark & Croushore (J. Macroeconomics 2002) 指出用最新修訂資料評估預測，誤差會看起來比用即時資料小。

## 寫作上的取捨（請核對）

- 方法論以 2026-11-01 的設計為準：exp01 與修正案 1–3 已登記，內容不變；修正案 4、exp01b、exp02–06 仍是草稿；
  exp07、exp03 的 H8 和 agent arms 還沒寫成登記文件，文中都標明。exp07 的 E-H1 到 E-H4 是我提的草案，登記前由你定稿。
  登記後要把狀態和任何改動同步回草稿。
- 第三章的章節對應：3.1–3.6 和 3.11–3.13 是論文第 3 章；3.7–3.8 是第 4 章（RQ1）的方法，3.9 是第 5 章（RQ2），
  3.10 是第 6 章（RQ3）。為了方便整體審閱，暫時放在同一個檔案。
- 內文完全沒有引用實驗結果（結果章節是你的），只有開題 Table 4.3 的定性描述（Austrian 基礎模型用詞最少）。
- 貢獻的措辭維持 THESIS_DESIGN §2 的強度；「to the author's knowledge」的新穎性主張都限定在具體的組合上。
- 風格：沒有 em-dash 構句、沒有模板式 AI 用語；英式學術英文。
- pmpol 的 L0–L5、proof、confidence、coherence projection、知識庫格式一律寫成團隊程式碼（team code），沒有當成文獻引用。

## 下一步建議

1. 先看 `NOTES_2026-11-01_zh.md` 第 2 節，確認寫進草稿的八個假設，尤其是 L3 學派條目寫成「歸屬命題」這一點。
2. 逐段核對後改寫（尤其是對他人論文的描述與每一個數字）；把 `references/*.bib` 併進論文的 LaTeX 專案。
3. 修正 `research/prereg_drafts/exp04_coherence.md` 的 Shi & Zhai 歸屬（見上）。
4. 和張老師確認系上對 AI 使用聲明的格式；把這份草稿列入聲明。
5. 第 1 章（動機、與開題的差異）、第 4–6 章的結果與討論、第 7 章限制，由你在實驗完成後撰寫。
