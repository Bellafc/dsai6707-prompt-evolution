# Citation verification record (thesis drafts, 2026-10-31)

Every citation key used in `ch2_literature_review.md`, `ch2_related_work.md` and `ch3_methodology.md` resolves to an
entry in `references/*.bib` (one file per topic cluster). Entries were checked against a primary source (publisher or DOI record, arXiv abstract page,
ACL Anthology, NeurIPS/ICLR/PMLR proceedings, official technical reports or model cards, library catalogues for
books) by four research sub-agents working from `scratchpad/bib/COMMON_BRIEF.md` (clusters A: forecasting, markets,
scoring, calibration, coherence; B: interpretability and LLM-as-judge; C: fine-tuning versus prompting, distillation,
personas, ensembles, model reports; D: economics and finance), plus four entries checked directly by the main session
(E) and eleven entries carried over from the Confirmation report's bibliography without re-fetching (F).

Status values: **VERIFIED** = all core fields read from a primary page; **PARTIAL** = found, one field left out
because it could not be read from a primary page (the note says which); **FROM-CONFIRMATION** = taken from
`docs/project/survey_pqe/references.bib` as checked during the Confirmation revisions, not re-fetched here.
No item in the drafts was left with an unverifiable citation; items that could not be matched to a real paper
were rewritten (see "Corrections" below).

Counts over the 179 keys cited in the drafts: {'VERIFIED': 163, 'PARTIAL': 5, 'FROM-CONFIRMATION': 11}. Over all 200 entries in
the topic files (including verified entries not yet cited): {'VERIFIED': 184, 'PARTIAL': 5, 'FROM-CONFIRMATION': 11}.

## Corrections made while verifying (the author should know these)

- **"Shi & Zhai (2026)"** as cited in the exp04 draft for "the guaranteed arbitrage equals the distance to the coherent
  set": the paper that exists under that name is Shi and Zhai, *Combinatorial Arbitrage in Prediction Markets*
  (arXiv 2610.23517), whose theorem is that prices outside the convex hull of admissible payoff vectors admit
  arbitrage, constructed by integer programming. The distance-to-coherence statement matches Andrews and Sarkar,
  *Dutch Books for Language Models* (arXiv 2609.02797). The drafts cite both for what each says; the exp04 draft's
  attribution should be corrected by the author (`research/prereg_drafts/exp04_coherence.md`, "Why this is principled").
- **"Le (2026)"** is Nam Anh Le, *Decomposing Crowd Wisdom: Domain-Specific Calibration Dynamics in Prediction
  Markets* (arXiv 2602.19520): about the calibration of human-trader prices on Kalshi and Polymarket, not about LLM
  forecasting. Cited accordingly (prediction-market calibration as an L2 base rate).
- **"Gebele & Matthes (2026)"** has three authors (Gebele, Till, Matthes): *Diversity and Deliberation in Homogeneous
  LLM Prediction Polls*, REALM 2026 workshop (ACL Anthology 2026.realm-1.85). Cite as Gebele et al.
- **Paleka et al. (2026)** is *Pitfalls in Evaluating Language Model Forecasters* (ICLR 2026; Paleka, Goel, Geiping,
  Tramer), about evaluation pitfalls and temporal leakage, not a sequel on consistency checks. Paleka et al. (2025)
  has the authors Paleka, Pallavi Sudhir, Alvarez, Bhat, Shen, Wang, Tramer.
- **Turtel et al. (2025)**: authors Turtel, Franklin, Skotheim, Hewitt, Schoenegger; TMLR (December 2025).
- **Mantic (2026)** is a guest post on Thinking Machines Lab's site by Scott Jeen, Matthew Aitchison and Mantic
  (19 March 2026; RL with a Brier reward on gpt-oss-120b, evaluated on a Metaculus tournament). Not peer-reviewed.
- **Persona vectors** (Chen et al.) is a NeurIPS 2026 paper, not ICLR 2026; **Paulo and Belrose** (feature
  instability) was published at ICLR 2026; **Minder et al.** (narrow fine-tuning traces) ICLR 2026 confirmed.
- **Cunningham et al. (2024)**: the ICLR 2024 version lists Huben as first author (Huben, Cunningham, Smith, Ewart,
  Sharkey); key `huben2024sparse`.
- **Qwen-Scope**: arXiv 2605.11887 (May 2026), 18 named authors, "Qwen Team". The Qwen3-8B SAEs are trained on the
  *base* model (as the exp06 draft assumes); the Qwen3.5-27B SAE is trained on the post-trained model. Licence tag
  "qwen" with Apache-2.0 licence text.
- **Qwen3.5** has no text-model technical report on arXiv as of 2026-10-31; cite the official release
  (`qwen2026qwen35`, Qwen Team, Feb 2026) and the Qwen3.5-27B model card.
- **Smith et al. (2025)** (negative results for SAEs on downstream tasks) is an AI Alignment Forum post (26 March
  2025), joint first authors Smith and Rajamanoharan; cited as such.
- **FAST** (Li et al.) was retitled *Breaking the Block: ...* (ICML 2026); key `li2026breaking`.
- **Zheng et al. ("helpful assistant")** is Findings of EMNLP 2024 (key `zheng2024helpful`); **Krogh and Vedelsby**
  is NIPS 7 (1994 conference, printed 1995; key `krogh1994neural`).
- **Bybee**: arXiv 2305.02823 carries the earlier title *Surveying Generative AI's Economic Expectations*; *The Ghost
  in the Machine* is the retitled December 2023 working paper. **Faria-e-Castro and Leibovici**: the published title
  is *Artificial Intelligence and Inflation Forecasts*, FRB St. Louis Review 106(12), 2024.
- **History Rhymes** (Khanna, Berger, Chopra, Berghaus, Sifa): IEEE BigData 2025, pp. 7196-7203; arXiv 2511.09754.
- **Kazinnik and Sinclair (FOMC In Silico)**: later drafts (October 2025, July 2026) exist with different headline
  numbers; the drafts cite the GWU working paper 2025-005 and quote no numbers.
- **Mahalanobis (1936)**: original spelling "Generalized" (entry title follows the scan; key keeps the draft spelling).
- **Platt scaling**: the book chapter is dated 2000 (key `platt2000probabilistic`); **Hayek**: entry is the 1931 first
  edition (George Routledge & Sons); **Mises**: entry is the 1934 Jonathan Cape translation (key `mises1934theory`).
- PARTIAL entries: `platt2000probabilistic` (chapter pages), `naeini2015obtaining` (pages), `tetlock2005expert`
  (2005 edition page not reachable; date confirmed via a 2006 review), `holm1979simple` (no DOI; vol/pages from
  OpenAlex/JSTOR cover sheet), `friedman1956quantity` (essay page range).

## Entries that the drafts do not cite (verified, available)

bereska2024mechanistic, blanchard2009state, chan2024chateval, fama1970efficient, gemma2025gemma3, gemma2026gemma4, giannone2015prior, he2026discovering, kwon2023efficient, lester2021power, mangrulkar2022peft, marks2025sparse, olah2020zoom, ouyang2022training, park2023generative, predd2008aggregating, qwen2026omni, snell2025scaling, vonwerra2020trl, xu2024survey, yang2024qwen25

## Per-key table

| key | status | cluster | primary source | note |
|---|---|---|---|---|

| `andrews2026dutch` | VERIFIED | A | https://arxiv.org/abs/2609.02797 | Added because it is the paper that actually matches the "guaranteed Dutch-book/arbitrage profit as a distance-to-coherence measure (de Finetti)" description, ap |
| `argyle2023out` | VERIFIED | C | https://www.cambridge.org/core/journals/political-analysis/article/out-of-one-many-using-language-models-to-simulate-human-samples/035D7C8A55B237942FB6DBAD7CAA4E49 | journal lists "Joshua R. Gubler" |
| `arrow2008promise` | VERIFIED | A | https://api.crossref.org/works/10.1126/science.1157679 | Science.org returned 403. |
| `bates1969combination` | VERIFIED | A | https://api.crossref.org/works/10.1057/jors.1969.103 | Deposit names the journal by its current title (Journal of the Operational Research Society); the entry keeps Operational Research Quarterly, the title in 1969. |
| `bereska2024mechanistic` (not cited) | VERIFIED | B | https://openreview.net/forum?id=ePUVetPKu6 | Entry uses "Efstratios Gavves" (arXiv/paper spelling); OpenReview display name is "Stratis Gavves". |
| `bills2023language` | VERIFIED | B | https://openaipublic.blob.core.windows.net/neuron-explainer/paper/index.html | openai.com/research/... returned HTTP 403; the paper page itself is the primary source. |
| `blanchard2009state` (not cited) | VERIFIED | D | https://api.crossref.org/works/10.1146/annurev.economics.050708.142952 | annualreviews.org returned 403. |
| `bricken2023monosemanticity` | VERIFIED | B | https://transformer-circuits.pub/2023/monosemantic-features/index.html | Page is 20 MB; metadata extracted with curl. Authors as the page's suggested BibTeX (Bricken … Olah). |
| `brier1950verification` | VERIFIED | A | https://api.crossref.org/works/10.1175/1520-0493(1950)078%3C0001:VOFEIT%3E2.0.CO;2 | AMS site returned 403. |
| `brown2020language` | VERIFIED | C | https://proceedings.neurips.cc/paper/2020/hash/1457c0d6bfcb4967418bfb8ac142f64a-Abstract.html | - |
| `bybee2023ghost` | VERIFIED | D | https://conference.nber.org/conf_papers/f194779/f194779.pdf | Correction: the arXiv id 2305.02823 corresponds to the earlier title. No SSRN page or published version found (searched SSRN/Google for the new title; only the  |
| `chan2024chateval` (not cited) | VERIFIED | C | https://iclr.cc/virtual/2024/poster/19065 | - |
| `chen2026persona` | VERIFIED | B | https://arxiv.org/abs/2507.21509 | No ICLR 2026 listing; accepted at NeurIPS 2026. Volume/pages do not exist yet (not a missing-field problem). If the thesis prefers, cite the 2025 arXiv preprint |
| `clarida1999science` | VERIFIED | D | https://www.aeaweb.org/articles?id=10.1257/jel.37.4.1661 |  |
| `clemen1989combining` | VERIFIED | A | https://api.crossref.org/works/10.1016/0169-2070(89)90012-5 | ScienceDirect returned 403. |
| `clements2010forecast` | VERIFIED | E | https://wrap.warwick.ac.uk/id/eprint/4972 | verified directly by the main session |
| `cohen1968weighted` | VERIFIED | B | https://pubmed.ncbi.nlm.nih.gov/19673146/ | — |
| `confavreux2026comparing` | VERIFIED | B |  | see the cluster log (row not parsed) |
| `croushore2001realtime` | VERIFIED | D | https://api.crossref.org/works/10.1016/S0304-4076(01)00072-0 | ScienceDirect returned 403. |
| `croushore2011frontiers` | VERIFIED | D | https://www.aeaweb.org/articles?id=10.1257/jel.49.1.72 |  |
| `definetti1974theory` | VERIFIED | E |  | verified directly by the main session |
| `dendramis2020similarity` | VERIFIED | D | https://api.crossref.org/works/10.1111/rssa.12574 | (d) Similarity/nearest-neighbour macro forecasting that outperforms time-varying-parameter models in crises; the canonical statistical reference for analogue re |
| `deng2026qwenscope` | VERIFIED | B | https://arxiv.org/abs/2605.11887 | Proper citation: Deng, Wang, Wang, Wan, Ma, Yang, … Zhou (Qwen Team), "Qwen-Scope: Turning Sparse Features into Development Tools for Large Language Models", ar |
| `dettmers2023qlora` | VERIFIED | C | https://proceedings.neurips.cc/paper_files/paper/2023/hash/1feb87871436031bdc0f2beaa62a049b-Abstract.html | NeurIPS lists both poster and oral pages |
| `diebold1995comparing` | VERIFIED | A | https://api.crossref.org/works/10.1080/07350015.1995.10524599 | tandfonline returned 403. |
| `diercks2026kalshi` | VERIFIED | A | https://www.federalreserve.gov/econres/feds/kalshi-and-the-rise-of-macro-markets.htm | (a) accuracy of Kalshi macro markets (CPI, FOMC) vs surveys and market-implied forecasts; the official evidence base for using resolved Kalshi macro markets as  |
| `dietterich2000ensemble` | VERIFIED | C | https://link.springer.com/chapter/10.1007/3-540-45014-9_1 | volume editors (Kittler & Roli) not shown on the chapter page, so omitted rather than asserted |
| `ding2024large` | VERIFIED | D |  | see the cluster log (row not parsed) |
| `dong2024survey` | VERIFIED | C | https://aclanthology.org/2024.emnlp-main.64/ | two distinct authors named Lei Li |
| `dong2025large` | VERIFIED | D |  | see the cluster log (row not parsed) |
| `du2024improving` | VERIFIED | C | https://proceedings.mlr.press/v235/du24e.html | - |
| `efron1993bootstrap` | VERIFIED | A | https://api.crossref.org/works/10.1007/978-1-4899-4541-9 | The CRC reissue (DOI 10.1201/9780429246593) is dated 1994; the series number (57) was not shown on either page and is omitted. |
| `elhage2022superposition` | VERIFIED | B | https://transformer-circuits.pub/2022/toy_model/index.html | As recollected. |
| `epstein1969scoring` | VERIFIED | A | https://api.crossref.org/works/10.1175/1520-0450(1969)008%3C0985:ASSFPF%3E2.0.CO;2 | AMS site returned 403. |
| `fama1970efficient` (not cited) | VERIFIED | D | https://api.crossref.org/works/10.2307/2325486 | Wiley page returned 403. |
| `fariaecastro2024artificial` | VERIFIED | A | https://www.stlouisfed.org/publications/review/2024/nov/artificial-intelligence-and-inflation-forecasts | (a) LLM (PaLM) inflation forecasts vs. Survey of Professional Forecasters, 2019-2023; lower MSE at most horizons. Fed journal, not a refereed academic journal. |
| `fatouros2025marketsenseai` | VERIFIED | D | https://arxiv.org/abs/2502.00415 |  |
| `friedman1956quantity` | PARTIAL | D | https://sol.unibo.it/SebinaOpac/query/ISBN%3A0226264068 | The essay's page range (commonly pp. 3-21) could not be read from a primary page: HathiTrust search-only and Internet Archive full text returned 401/403 and Goo |
| `friedman1961lag` | VERIFIED | D | https://api.crossref.org/works/10.1086/258537 | journals.uchicago.edu returned 403. |
| `friedman1963monetary` | VERIFIED | D | https://www.nber.org/books-and-chapters/monetary-history-united-states-1867-1960 | ISBN on the NBER page (9780691003542) belongs to a later paperback printing, so it was omitted. |
| `friedman1968role` | VERIFIED | D | https://www.aeaweb.org/aer/top20/58.1.1-17.pdf | JSTOR (stable/1831652) not fetchable; no DOI registered with Crossref for this article. |
| `gali2015monetary` | VERIFIED | D | https://press.princeton.edu/books/hardcover/9780691164786/monetary-policy-inflation-and-the-business-cycle | Publisher page shows no subtitle; the cover subtitle was left out of the entry rather than taken on trust. |
| `galichin2026feature` | VERIFIED | B |  | see the cluster log (row not parsed) |
| `gao2025scaling` | VERIFIED | B | https://proceedings.iclr.cc/paper_files/paper/2025/hash/42ef3308c230942d223c411adf182c88-Abstract-Conference.html | As recollected (TopK SAEs). |
| `garrison2001time` | VERIFIED | D | https://www.routledge.com/Time-and-Money-The-Macroeconomics-of-Capital-Structure/Garrison/p/book/9780415771221 | ISBN not shown on either page; omitted. |
| `gebele2026diversity` | VERIFIED | A | https://aclanthology.org/2026.realm-1.85/ | Three authors, so "Gebele & Matthes (2026)" should be "Gebele, Till and Matthes (2026)" / "Gebele et al.". Workshop paper (not a main-conference benchmark). Top |
| `gemma2025gemma3` (not cited) | VERIFIED | C | https://arxiv.org/abs/2503.19786 | bib uses the team author form as in Google's own citation |
| `gemma2026gemma4` (not cited) | VERIFIED | C | https://arxiv.org/abs/2607.02770 | Gemma 4 exists; the ai.google.dev docs say they are deprecated in favour of gemma.ai but the model card is still live |
| `giannone2015prior` (not cited) | VERIFIED | D | https://api.crossref.org/works/10.1162/REST_a_00483 | direct.mit.edu returned 403. |
| `glasserman2024assessing` | VERIFIED | D | https://api.crossref.org/works/10.3905/jfds.2023.1.143 | (c) Peer-reviewed test of look-ahead bias in GPT-based return forecasts (anonymisation design). |
| `gneiting2007strictly` | VERIFIED | A | https://api.crossref.org/works/10.1198/016214506000001437 | tandfonline returned 403. |
| `gu2024survey` | VERIFIED | B | https://arxiv.org/abs/2411.15594 | No journal version found. |
| `gudibande2024false` | VERIFIED | C | https://iclr.cc/virtual/2024/poster/18877 | venue confirmed. Published title is "...Imitating Proprietary Language Models" (arXiv says "LLMs") |
| `guo2017calibration` | VERIFIED | A | https://proceedings.mlr.press/v70/guo17a.html | PMLR BibTeX read directly. |
| `halawi2024forecasting` | VERIFIED | A | https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a5acfd0876c940d81619c1dc60e7748-Abstract-Conference.html | Third author printed as "Chen Yueh-Han"; kept in braces to preserve the printed form. OpenReview id FlcdW7NPRY. |
| `hambly2023recent` | FROM-CONFIRMATION | F |  | taken from the Confirmation report bibliography; not re-fetched |
| `hansen2023can` | VERIFIED | D |  | see the cluster log (row not parsed) |
| `hansen2025simulating` | VERIFIED | D | https://api.crossref.org/works/10.2139/ssrn.5066286 | (a)/(b) LLM forecaster personas fed real-time macro data reproduce SPF accuracy and dispersion; the closest benchmark to Macro-MOSAIC's point-in-time macro fore |
| `harvey1997testing` | VERIFIED | D | https://api.crossref.org/works/10.1016/S0169-2070(96)00719-4 | ScienceDirect returned 403. |
| `hayek1931prices` | VERIFIED | D |  | see the cluster log (row not parsed) |
| `he2026discovering` (not cited) | VERIFIED | B | https://arxiv.org/abs/2606.26620 | Existence **confirmed**; no venue. |
| `heap2026automated` | VERIFIED | B |  | see the cluster log (row not parsed) |
| `heuer1999psychology` | VERIFIED | D | https://www.cia.gov/resources/csi/books-monographs/psychology-of-intelligence-analysis-2/ |  |
| `hicks1937mr` | VERIFIED | D |  | see the cluster log (row not parsed) |
| `hinton2015distilling` | VERIFIED | C | https://arxiv.org/abs/1503.02531 | no formal proceedings; cite as arXiv/workshop |
| `ho2023large` | VERIFIED | C | https://aclanthology.org/2023.acl-long.830/ | - |
| `holm1979simple` | PARTIAL | A | https://api.openalex.org/works/W2121044470 | JSTOR and a university-hosted JSTOR copy could not be loaded; issue/pages from the OpenAlex record and the JSTOR cover-sheet text quoted in search results. The  |
| `hong2004groups` | VERIFIED | A | https://api.crossref.org/works/10.1073/pnas.0403723101 | PNAS site returned 403. |
| `hsieh2023distilling` | VERIFIED | C | https://aclanthology.org/2023.findings-acl.507/ | Anthology spells "Chih-kuan Yeh", "Alex Ratner" |
| `hu2022lora` | VERIFIED | C | https://iclr.cc/virtual/2022/poster/6319 | OpenReview id nZeVKeeFYf9 confirmed on the iclr.cc page |
| `hu2024quantifying` | VERIFIED | C | https://aclanthology.org/2024.acl-long.554/ | quantifies how much persona variables explain human annotation variance (<10%) and how much persona prompting changes LLM predictions -- a methodology for measu |
| `huben2024sparse` | VERIFIED | B | https://proceedings.iclr.cc/paper_files/paper/2024/hash/1fa1ab11f4bd5f94b2ec20e794dbfa3b-Abstract-Conference.html | **Author order differs**: the ICLR 2024 version lists Robert Huben, Hoagy Cunningham, Logan Smith, Aidan Ewart, Lee Sharkey; the arXiv version lists Cunningham, |
| `iadisernia2025prompting` | VERIFIED | D | https://arxiv.org/abs/2511.02458 | (b) Persona prompts give no accuracy gain and produce homogeneous macro forecasts: direct motivation for fine-tuned school adapters rather than prompted viewpoi |
| `islam2023financebench` | FROM-CONFIRMATION | F |  | taken from the Confirmation report bibliography; not re-fetched |
| `jacobs1991adaptive` | VERIFIED | C | https://api.crossref.org/works/10.1162/neco.1991.3.1.79 | direct.mit.edu 403; Crossref record used |
| `jeddi2026crowdsourced` | VERIFIED | A | https://api.crossref.org/works/10.1098/rstb.2024.0456 | (d) aggregation of LLM "crowds" vs human crowds; accuracy-correlation effect (correlated LLM forecasts limit pooling gains), the issue behind pooling three adap |
| `jeen2026training` | VERIFIED | A | https://thinkingmachines.ai/news/training-llms-to-predict-world-events/ | Guest post on Thinking Machines Lab's site; the page's own BibTeX key is scott2026forecasting with author "Scott Jeen, Matthew Aitchison, and Mantic". Not peer- |
| `kadavath2022language` | VERIFIED | A | https://arxiv.org/abs/2207.05221 | No journal reference listed. |
| `kantamneni2025sparse` | VERIFIED | B | https://proceedings.mlr.press/v267/kantamneni25a.html | As recollected. |
| `kapoor2024taught` | VERIFIED | A | https://proceedings.neurips.cc/paper_files/paper/2024/hash/9c20f16b05f5e5e70fa07e2a4364b80e-Abstract-Conference.html | (b) LLM calibration: LoRA fine-tuning on ~1,000 graded examples gives calibrated uncertainty, beating prompting; directly relevant to calibrating LoRA school ad |
| `karger2025forecastbench` | VERIFIED | A | https://proceedings.iclr.cc/paper_files/paper/2025/hash/ea74e45a229dac70b5b63b28d8934db6-Abstract-Conference.html | OpenReview id lfPkGWXLLf. |
| `karvonen2025saebench` | VERIFIED | B | https://proceedings.mlr.press/v267/karvonen25a.html | ICML 2025 **confirmed**. |
| `kazinnik2025fomc` | VERIFIED | D | https://econpapers.repec.org/paper/gwcwpaper/2025-005.htm | Later drafts (Oct 2025, July 2026) exist on the Stanford Digital Economy Lab and NBER conference sites with different headline numbers; check which draft is quo |
| `keynes1936general` | VERIFIED | D | https://ci.nii.ac.jp/ncid/BA00760008 | CiNii Books record of the 1936 Macmillan (London)/Harcourt Brace (New York) edition. Collected Writings vol. 7 (1973) is a separate record (BA00871461). |
| `khanna2025history` | VERIFIED | D | https://arxiv.org/abs/2511.09754 | Primary pages found as requested. |
| `kissane2024saes` | VERIFIED | B | https://www.alignmentforum.org/posts/fmwk6qxrpW8d4jvbd/saes-usually-transfer-between-base-and-chat-models | Primary URL and date found. Interim research report (Mistral-7B, Qwen 1.5 0.5B; Gemma v1 2B is the exception). |
| `kojima2022large` | VERIFIED | C | https://proceedings.neurips.cc/paper/2022/hash/8bb0d291acd4acf06ef112099c16f326-Abstract-Conference.html | - |
| `kroer2016arbitrage` | VERIFIED | A | https://api.crossref.org/works/10.1145/2940716.2940767 | ACM DL page not fetched (Crossref deposit used). |
| `krogh1994neural` | VERIFIED | C | https://proceedings.neurips.cc/paper/1994/hash/b8c37e33defde51cf91e1e03e51657da-Abstract.html | proceedings site dates it 1994 (conference); printed volume is 1995 - either year is defensible, bib uses 1994 as on the primary page |
| `kwon2023efficient` (not cited) | VERIFIED | C | https://api.crossref.org/works/10.1145/3600006.3613165 | dl.acm.org 403; Crossref record used |
| `landis1977measurement` | VERIFIED | B | https://pubmed.ncbi.nlm.nih.gov/843571/ | — |
| `le2026decomposing` | VERIFIED | A | https://arxiv.org/abs/2602.19520 | This is the only 2026 "Le" paper on Kalshi/Polymarket calibration found. It is about calibration of human-trader market prices (353M trades, 429k contracts), no |
| `ledoit2004honey` | VERIFIED | D | https://api.crossref.org/works/10.3905/jpm.2004.110 |  |
| `ledoit2004well` | VERIFIED | D |  | see the cluster log (row not parsed) |
| `lee2025econcausal` | VERIFIED | D | https://arxiv.org/abs/2510.07231 | No venue listed on arXiv. |
| `lester2021power` (not cited) | VERIFIED | C | https://aclanthology.org/2021.emnlp-main.243/ | - |
| `li2024econagent` | VERIFIED | D | https://aclanthology.org/2024.acl-long.829/ |  |
| `li2026breaking` | VERIFIED | B | https://arxiv.org/abs/2506.07691 | PMLR volume for ICML 2026 not yet listed on proceedings.mlr.press (checked 2026-10-31). Method = FAST; SAEs for Qwen2.5-7B-Instruct and Llama-3.2-3B-Instruct. |
| `li2026can` | VERIFIED | D |  | see the cluster log (row not parsed) |
| `liang2024encouraging` | VERIFIED | C | https://aclanthology.org/2024.emnlp-main.992/ | - |
| `lichtendahl2013average` | VERIFIED | A | https://api.crossref.org/works/10.1287/mnsc.1120.1667 | INFORMS site returned 403. |
| `lieberum2024gemmascope` | VERIFIED | B | https://aclanthology.org/2024.blackboxnlp-1.19/ | The workshop version exists and is used as the published version. |
| `lin2024unlocking` | VERIFIED | C | https://iclr.cc/virtual/2024/poster/17473 | URIAL: alignment via 3 stylistic in-context examples; token-level analysis shows SFT/RLHF mostly changes stylistic tokens -- the sharpest statement of the "supe |
| `liu2022finrl` | FROM-CONFIRMATION | F |  | taken from the Confirmation report bibliography; not re-fetched |
| `liu2022finrlmeta` | FROM-CONFIRMATION | F |  | taken from the Confirmation report bibliography; not re-fetched |
| `liu2023geval` | VERIFIED | B | https://aclanthology.org/2023.emnlp-main.153/ | Anthology renders the title "…using Gpt-4…"; entry uses "GPT-4" in braces. |
| `lopezdeprado2018advances` | VERIFIED | D | https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086 | Wiley-VCH lists May 2018; year 2018 either way. |
| `lopezlira2023can` | VERIFIED | D |  | see the cluster log (row not parsed) |
| `lopezlira2025memorization` | VERIFIED | D | https://arxiv.org/abs/2504.14765 |  |
| `lorenz1969atmospheric` | VERIFIED | D | https://api.crossref.org/works/10.1175/1520-0469(1969)26%3C636:APARBN%3E2.0.CO;2 | journals.ametsoc.org returned 403. |
| `ludwig2026large` | VERIFIED | D | https://api.crossref.org/works/10.1146/annurev-economics-120925-105620 | (c) Formal "no training leakage" condition for LLM prediction and validation-sample condition for LLM measurement: underpins the post-cutoff Kalshi evaluation a |
| `magister2023teaching` | VERIFIED | C | https://aclanthology.org/2023.acl-short.151/ | - |
| `mahalanobis1936generalised` | VERIFIED | D |  | see the cluster log (row not parsed) |
| `mangrulkar2022peft` (not cited) | VERIFIED | C | https://github.com/huggingface/peft | - |
| `mankiw2006macroeconomist` | VERIFIED | D | https://www.aeaweb.org/articles?id=10.1257/jep.20.4.29 |  |
| `marks2024geometry` | VERIFIED | B | https://arxiv.org/abs/2310.06824 | OpenReview (id aajyHYjjsk per a secondary index) could not be opened; COLM has no page numbers, so none are given. |
| `marks2025sparse` (not cited) | VERIFIED | B | https://proceedings.iclr.cc/paper_files/paper/2025/hash/3ba4d47a83e498c2b1a0868cba20f6de-Abstract-Conference.html | As recollected. |
| `mcdougall2025gemmascope2` | VERIFIED | B | https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/gemma-scope-2-helping-the-ai-safety-community-deepen-understanding-of-complex-language-model-behavior/Gemma_Scope_2_Technical_Paper.pdf | Covers JumpReLU SAEs and skip-transcoders on all layers/sub-layers of Gemma 3 (270M–27B, base and instruction-tuned) plus multi-layer models (crosscoders / cros |
| `mellers2014psychological` | VERIFIED | A | https://api.crossref.org/works/10.1177/0956797614524255 | SAGE site returned 403. |
| `minder2025overcoming` | VERIFIED | B |  | see the cluster log (row not parsed) |
| `minder2026narrow` | VERIFIED | B | https://proceedings.iclr.cc/paper_files/paper/2026/hash/3b939edfdf9c1211fb764a888078f13d-Abstract-Conference.html | ICLR 2026 **confirmed**. Authors: Julian Minder, Clément Dumas, Stewart Slocum, Helena Casademunt, Cameron Holmes, Robert West, Neel Nanda. |
| `mises1934theory` | VERIFIED | D | https://ci.nii.ac.jp/ncid/BA17629030 | German publisher of the 1912 edition not verified and omitted. The thesis key says 1912 but the entry's year is 1934 (first English edition, the verified record |
| `mishkin1996channels` | VERIFIED | D | https://www.nber.org/papers/w5464 | Entry cites the NBER WP and notes the Banque de France publication. |
| `mosbach2023fewshot` | VERIFIED | C | https://aclanthology.org/2023.findings-acl.779/ | - |
| `mukherjee2023orca` | VERIFIED | C | https://arxiv.org/abs/2306.02707 | arXiv only |
| `murphy1973vector` | VERIFIED | A | https://api.crossref.org/works/10.1175/1520-0450(1973)012%3C0595:ANVPOT%3E2.0.CO;2 | AMS site returned 403. |
| `naeini2015obtaining` | PARTIAL | A | https://api.crossref.org/works/10.1609/aaai.v29i1.9602 | Page numbers (usually 2901-2907) not confirmed and omitted. |
| `nel2025kalshibench` | VERIFIED | A | https://arxiv.org/abs/2512.16030 | arXiv spells the benchmark "Kalshibench" in the title; no venue found. |
| `nie2024survey` | VERIFIED | D | https://arxiv.org/abs/2406.11903 |  |
| `nosek2018preregistration` | VERIFIED | E | https://www.pnas.org/doi/10.1073/pnas.1708274114 | verified directly by the main session |
| `odni2015icd203` | VERIFIED | A | https://www.dni.gov/files/documents/ICD/ICD-203.pdf | Text extracted from the downloaded official PDF (pdftotext). The older URL ".../ICD%20203%20Analytic%20Standards.pdf" now 404s. |
| `olah2020zoom` (not cited) | VERIFIED | B | https://distill.pub/2020/circuits/zoom-in/ | Optional item; included. |
| `ouyang2022training` (not cited) | VERIFIED | C | https://proceedings.neurips.cc/paper_files/paper/2022/hash/b1efde53be364a73914f58805a001731-Abstract-Conference.html | - |
| `paleka2025consistency` | VERIFIED | A | https://proceedings.iclr.cc/paper_files/paper/2025/hash/5107a33432b9a5cffafd0a53ef6c6a18-Abstract-Conference.html | Your list had "Paleka, Pawar, Blaz, Schoenegger": the actual authors are Paleka, Pallavi Sudhir, Alvarez, Bhat, Shen, Wang, Tramer. OpenReview id r5IXBlTCGc. |
| `paleka2026pitfalls` | VERIFIED | A | https://iclr.cc/virtual/2026/poster/10006489 | The 2026 Paleka et al. ICLR paper exists and is "Pitfalls in Evaluating Language Model Forecasters" (evaluation pitfalls, temporal leakage), not a sequel on con |
| `panickssery2024llm` | VERIFIED | B | https://papers.nips.cc/paper_files/paper/2024/hash/7f1f0218e45f5414c79c0679633e47bc-Abstract-Conference.html | As recollected (NeurIPS 2024 oral per neurips.cc). |
| `park2023generative` (not cited) | VERIFIED | C | https://api.crossref.org/works/10.1145/3586183.3606763 | dl.acm.org 403; ACM article number not confirmed so omitted |
| `paulo2025automatically` | VERIFIED | B | https://proceedings.mlr.press/v267/paulo25a.html | ICML 2025 venue **confirmed**. PMLR gives full names Gonçalo Santos Paulo and Alex Troy Mallen. |
| `paulo2026sparse` | VERIFIED | B | https://proceedings.iclr.cc/paper_files/paper/2026/hash/3c1fe56b043848b211030c202764c6a7-Abstract-Conference.html | Recollected as arXiv 2025; it was **published at ICLR 2026** — entry uses the published version. |
| `platt2000probabilistic` | PARTIAL | A | https://mitpress.mit.edu/9780262194488/advances-in-large-margin-classifiers/ | Could not read a publisher page: chapter pages (commonly 61-74) and the book's exact date were not confirmed, so pages are omitted. The MIT Press book is dated  |
| `predd2008aggregating` (not cited) | VERIFIED | A | https://api.crossref.org/works/10.1287/deca.1080.0119 | INFORMS page lists the paper but hides author names; Crossref deposit gives them. |
| `predd2009coherence` | VERIFIED | A | https://api.crossref.org/works/10.1109/TIT.2009.2027573 | Key result for the thesis (projection onto coherent set does not worsen, and for incoherent forecasts improves, any proper score). |
| `quan2024econlogicqa` | VERIFIED | D | https://aclanthology.org/2024.findings-emnlp.125/ | Correction: author surnames are Quan and Liu (first names Yinzhu, Zefang). |
| `qwen2026omni` (not cited) | VERIFIED | C | https://arxiv.org/abs/2604.15804 | separate Omni model; only cite if that model is used |
| `qwen2026qwen35` | VERIFIED | C | https://huggingface.co/Qwen/Qwen3.5-27B | NO Qwen3.5 text-model technical report on arXiv as of 2026-10-31 (arXiv title search returns only the Omni report). The blog page itself is JS-rendered (fetch r |
| `rajamanoharan2024jumping` | VERIFIED | B | https://arxiv.org/abs/2407.14435 | No peer-reviewed venue found (searched OpenReview/proceedings). |
| `ranjan2010combining` | VERIFIED | A | https://api.crossref.org/works/10.1111/j.1467-9868.2009.00726.x | Crossref deposit now held by OUP. |
| `ren2024learning` | VERIFIED | C | https://aclanthology.org/2024.acl-long.330/ | knowledge-intervention study of what instruction fine-tuning teaches: new world knowledge is not learned (and hurts), consistency with parametric knowledge matt |
| `rimsky2024steering` | VERIFIED | B | https://aclanthology.org/2024.acl-long.828/ | Published version credits **Nina Rimsky** (arXiv: Nina Panickssery — same person) and "Alexander Turner". |
| `rozado2024political` | VERIFIED | C | https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0306621 | fine-tunes an LLM into LeftWingGPT / RightWingGPT / DepolarizingGPT with modest SFT -- closest published analogue to instilling heterogeneous ideological/theore |
| `russell2010artificial` | FROM-CONFIRMATION | F |  | taken from the Confirmation report bibliography; not re-fetched |
| `salewski2023incontext` | VERIFIED | C | https://proceedings.neurips.cc/paper_files/paper/2023/hash/e3fe7b34ba4f378df39cb12a97193f41-Abstract.html | - |
| `santurkar2023whose` | VERIFIED | C | https://proceedings.mlr.press/v202/santurkar23a.html | - |
| `sarkar2024lookahead` | VERIFIED | D | https://api.crossref.org/works/10.2139/ssrn.4754678 | (c) Direct tests of temporal lookahead bias in pretrained LMs; argues prompting cannot fix it, only pre-period training data can. Workshop-reviewed, not a journ |
| `satopaa2014combining` | VERIFIED | A | https://api.crossref.org/works/10.1016/j.ijforecast.2013.09.009 | Your list had "Satopaa et al."; full list is Satopaa, Baron, Foster, Mellers, Tetlock, Ungar. |
| `schoenegger2024wisdom` | VERIFIED | A | https://api.crossref.org/works/10.1126/sciadv.adp1528 | Your list omitted Tuminauskaite and Bastos: the journal version has five authors (Schoenegger, Tuminauskaite, Park, Valdece Sousa Bastos, Tetlock); arXiv v6 lis |
| `shah2023trillion` | VERIFIED | D | https://aclanthology.org/2023.acl-long.368/ |  |
| `shanahan2023role` | VERIFIED | C | https://api.crossref.org/works/10.1038/s41586-023-06647-8 | nature.com redirected to a cookie wall; metadata from the Crossref DOI record. Issue number 7987 added |
| `shazeer2017outrageously` | VERIFIED | C | https://arxiv.org/abs/1701.06538 | OpenReview (id B1ckMDqlg) behind browser check; no ICLR-2017 proceedings page exists |
| `shi2026combinatorial` | VERIFIED | A | https://arxiv.org/abs/2610.23517 | The abstract's theorem is "prices outside the convex hull of admissible payoff vectors admit arbitrage" plus integer-programming arbitrage portfolios on Polymar |
| `shuttleworth2025lora` | VERIFIED | B |  | see the cluster log (row not parsed) |
| `smith2025negative` | VERIFIED | B | https://www.alignmentforum.org/posts/4uXCAJNuPKtKBsi28/negative-results-for-saes-on-downstream-tasks | Resolves the "Smith, Rajamanoharan? or …" uncertainty: it is a blog post, not a paper; both Smith and Rajamanoharan are joint first authors. |
| `snell2025scaling` (not cited) | VERIFIED | C | https://proceedings.iclr.cc/paper_files/paper/2025/hash/1b623663fd9b874366f3ce019fdfdd44-Abstract-Conference.html | published title differs: "...Can be More Effective than Scaling Parameters for Reasoning"; OpenReview id 4FWAwZtd2n not re-confirmed (blocked) |
| `snowberg2013prediction` | VERIFIED | A | https://api.crossref.org/works/10.1016/B978-0-444-53683-9.00011-6 | Volume is "2A" (the 2013 Handbook vol. 2 was issued as 2A and 2B). |
| `snowdon2005modern` | VERIFIED | D | https://www.cambridge.org/core/journals/journal-of-the-history-of-economic-thought/article/abs/brian-snowdon-and-howard-r-vane-modern-macroeconomics-its-origins-development-and-current-state-cheltenham-uk-and-northampton-ma-usa-edward-elgar-2005-pp-xviii-807-225-isbn-1-84376-394-x/C6D661D35C4F32474DAB704C3DBAC4D6 | e-elgar.com returned 403. Paperback ISBN 9781845422080 seen only in secondary listings. |
| `stone1961opinion` | VERIFIED | E | https://projecteuclid.org/euclid.aoms/1177704873 | verified directly by the main session |
| `taori2023stanford` | VERIFIED | C | https://github.com/tatsu-lab/stanford_alpaca | blog post dated 13 Mar 2023 (date from URL/image paths; the post shows no explicit date line) |
| `templeton2024scaling` | VERIFIED | B | https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html | The page byline lists 26 names; the page's own BibTeX lists 22 (omits Alex Tamkin, Esin Durmus, Tristan Hume, Francesco Mosconi). Entry uses the page's BibTeX l |
| `tetlock2005expert` | PARTIAL | A | https://press.princeton.edu/books/paperback/9780691175973/expert-political-judgment | No publisher page for the 2005 printing could be loaded (press.princeton.edu hardcover URL 403; De Gruyter 405). If you want a fully verified entry, cite the 20 |
| `tetlock2015superforecasting` | VERIFIED | A | https://www.penguinrandomhouse.com/books/227815/superforecasting-by-philip-e-tetlock-and-dan-gardner/ | Hardcover ISBN not on the publisher page, so no ISBN in the entry. |
| `tian2023just` | VERIFIED | A | https://aclanthology.org/2023.emnlp-main.330/ | ACL Anthology BibTeX read directly. |
| `turner2024steering` | VERIFIED | B | https://arxiv.org/abs/2308.10248 | The authors' own mirror calls v5 "the ICLR 2025 version" (OpenReview 2XBPdPIcFK) but marks it `type: preprint`; the title is **not** in the ICLR 2025 proceeding |
| `turtel2025outcome` | VERIFIED | A | https://jmlr.org/tmlr/papers/ | TMLR acceptance confirmed. Your list had "Schroeder?" and omitted Luke Hewitt: the fifth author is Philipp Schoenegger (LSE), fourth is Luke Hewitt (Stanford).  |
| `vonwerra2020trl` (not cited) | VERIFIED | C | https://github.com/huggingface/trl | README year is 2020 |
| `wang2023selfinstruct` | VERIFIED | C | https://aclanthology.org/2023.acl-long.754/ | - |
| `wang2024rolellm` | VERIFIED | C | https://aclanthology.org/2024.findings-acl.878/ | role-conditioned instruction tuning (RoleLLaMA/RoleGLM) vs role prompting (RoleGPT) on a role-play benchmark -- fine-tuning vs prompting for persona adoption |
| `wang2026persona` | VERIFIED | B |  | see the cluster log (row not parsed) |
| `wei2022chain` | VERIFIED | C | https://proceedings.neurips.cc/paper/2022/hash/9d5609613524ecf4f15af0f7b31abca4-Abstract-Conference.html | - |
| `west2022symbolic` | VERIFIED | C | https://aclanthology.org/2022.naacl-main.341/ | - |
| `wolfers2004prediction` | VERIFIED | A | https://www.aeaweb.org/articles?id=10.1257/0895330041371321 | AEA page read directly. |
| `woodford2003interest` | VERIFIED | D | https://press.princeton.edu/books/hardcover/9780691010496/interest-and-prices | Subtitle "Foundations of a Theory of Monetary Policy" taken from library catalogue listings in search results; the Princeton page heading shows the short title. |
| `wooldridge1995intelligent` | FROM-CONFIRMATION | F |  | taken from the Confirmation report bibliography; not re-fetched |
| `wu2025axbench` | VERIFIED | B | https://proceedings.mlr.press/v267/wu25a.html | **Author list correction**: Zhengxuan Wu, Aryaman Arora, Atticus Geiger, Zheng Wang, **Jing Huang**, Dan Jurafsky, Christopher D. Manning, Christopher Potts (re |
| `xiao2024tradingagents` | VERIFIED | D | https://arxiv.org/abs/2412.20138 | No archival proceedings version found. |
| `xie2024finben` | FROM-CONFIRMATION | F |  | taken from the Confirmation report bibliography; not re-fetched |
| `xing2025designing` | FROM-CONFIRMATION | F |  | taken from the Confirmation report bibliography; not re-fetched |
| `xiong2024can` | VERIFIED | A | https://iclr.cc/virtual/2024/poster/18135 | (b) calibration of verbalized confidence (ECE/AUROC); LLMs overconfident when stating probabilities. |
| `xu2024survey` (not cited) | VERIFIED | C | https://arxiv.org/abs/2402.13116 | arXiv only |
| `yang2023fingpt` | FROM-CONFIRMATION | F |  | taken from the Confirmation report bibliography; not re-fetched |
| `yang2024qwen25` (not cited) | VERIFIED | C | https://arxiv.org/abs/2412.15115 | year 2024 (first posting; QwenLM README cites 2024); v2 appeared 3 Jan 2025 |
| `yang2025qwen3` | VERIFIED | C | https://arxiv.org/abs/2505.09388 | arXiv lists named individuals, not "Qwen Team" |
| `yu2023finmem` | FROM-CONFIRMATION | F |  | taken from the Confirmation report bibliography; not re-fetched |
| `yu2024fincon` | VERIFIED | D | https://proceedings.neurips.cc/paper/2024/hash/f7ae4fe91d96f50abc2211f09b6a7e49-Abstract-Conference.html | Proceedings page shows no page numbers. arXiv 2407.06567 given as eprint. |
| `zhang2024finagent` | FROM-CONFIRMATION | F |  | taken from the Confirmation report bibliography; not re-fetched |
| `zhao2025incontext` | VERIFIED | C | https://iclr.cc/virtual/2025/poster/29602 | direct ICL-vs-instruction-fine-tuning comparison on MT-Bench; ICL alignment plateaus after 10-30 demonstrations and lags SFT for stronger base models -- support |
| `zheng2023judging` | VERIFIED | B | https://proceedings.neurips.cc/paper_files/paper/2023/hash/91f18a1287b398d378ef22505bf41832-Abstract.html | As recollected. |
| `zheng2024helpful` | VERIFIED | C | https://aclanthology.org/2024.findings-emnlp.888/ | brief's title and venue were wrong: published as "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of La |
| `zhou2023lima` | VERIFIED | C | https://proceedings.neurips.cc/paper_files/paper/2023/hash/ac662d74829e4407ce1d126477f4a03a-Abstract.html | - |
| `zhu2024incoherent` | VERIFIED | A | https://escholarship.org/uc/item/2r68p98c | (c) coherence of LLM probability judgments: systematic violations of probabilistic identities; precedent for the CPI m/m vs y/y checks. |
| `zou2023representation` | VERIFIED | B | https://arxiv.org/abs/2310.01405 | No peer-reviewed version found. |
