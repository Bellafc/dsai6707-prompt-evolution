# Related-work and future-work scan (2026-11-01)

Requested by the human after the test-time-training decision (THESIS_DESIGN D12). Three searches were run in
parallel, one each for RQ1 plus TTT, RQ2/RQ3, and economics/ideology/future work. Each entry was checked against a
primary record (proceedings, DOI or Crossref, arXiv abs, ACL Anthology, publisher or library catalogue) and against
`research/thesis_drafts/LIBRARY.md` and `references/*.bib`. Everything below is **missing from the library** unless
marked. Status: VERIFIED means the authors, year, title and venue were confirmed on such a record; notes say where
only part was confirmed.
**Hand-off:** the reference session adds BibTeX entries and runs its own verification (CITATION_VERIFICATION.md)
before anything is cited in a chapter.

Priority: **A** = cite in Ch. 2 or the method; **B** = cite if space; **F** = future work only.

## 1. RQ1 (inside the model) and test-time training

### Test-time training (D12: considered, deliberately not adopted)
| Pri | Work | Record | Why it matters here |
|---|---|---|---|
| A | Sun, Wang, Liu, Miller, Efros, Hardt (2020). *Test-Time Training with Self-Supervision for Generalization under Distribution Shifts.* ICML 2020, PMLR 119:9229–9248 | https://proceedings.mlr.press/v119/sun20b.html | The original TTT; template for "adapt the adapter per input" |
| A | Wang, Shelhamer, Liu, Olshausen, Darrell (2021). *Tent: Fully Test-Time Adaptation by Entropy Minimization.* ICLR 2021 | https://iclr.cc/virtual/2021/poster/2874 | Label-free entropy minimisation; source of the calibration risk |
| A | Akyürek, Damani, Zweiger, Qiu, Guo, Pari, Kim, Andreas (2025). *The Surprising Effectiveness of Test-Time Training for Few-Shot Learning.* ICML 2025, PMLR 267:942–963 | https://proceedings.mlr.press/v267/akyurek25a.html | Per-task LoRA at test time beats few-shot prompting; the LLM-era case |
| A | Hardt & Sun (2024). *Test-Time Training on Nearest Neighbors for Large Language Models.* ICLR 2024 | https://proceedings.iclr.cc/paper_files/paper/2024/hash/f02f1185b97518ab5bd7ebde466992d3-Abstract-Conference.html | Fine-tunes on retrieved neighbours; our L2 puts the same neighbours in the context instead, which keeps them checkable |
| A | Yoon et al. (2024). *C-TPT: Calibrated Test-Time Prompt Tuning for Vision-Language Models via Text Feature Dispersion.* ICLR 2024 | https://proceedings.iclr.cc/paper_files/paper/2024/hash/23ff02034404b65776080cbf7148addd-Abstract-Conference.html | Entropy-minimising test-time tuning raises ECE (CLIP-RN50 5.61 → 11.7; ViT-B/16 4.43 → 11.6, Table 1): evidence for the RQ3 reason |
| B | Amin & Kim (2025). *The Over-Certainty Phenomenon in Modern Test-Time Adaptation Algorithms.* TMLR | https://openreview.net/forum?id=AGQRij8iUC | Same point, classification only (analogy) |

### What fine-tuning changes inside the model
| Pri | Work | Record | Why it matters here |
|---|---|---|---|
| A | Jain et al. (2024). *Mechanistically Analyzing the Effects of Fine-Tuning on Procedurally Defined Tasks.* ICLR 2024 | https://proceedings.iclr.cc/paper_files/paper/2024/hash/29b5de0a8925cb4920d9c64542108335-Abstract-Conference.html | Fine-tuning as a thin "wrapper" over existing capabilities: the null hypothesis for RQ1 |
| A | Prakash, Shaham, Haklay, Belinkov, Bau (2024). *Fine-Tuning Enhances Existing Mechanisms: A Case Study on Entity Tracking.* ICLR 2024 | https://arxiv.org/abs/2402.14811 (venue from the arXiv comment) | Circuits survive and strengthen: a prediction for the SFT vs SFT+RFT diffs |
| A | Biderman et al. (2024). *LoRA Learns Less and Forgets Less.* TMLR | https://arxiv.org/abs/2405.09673 (venue from the arXiv comment) | Prior that LoRA changes are small; frames a small prompted-vs-SFT diff |
| A | Betley et al. (2026). *Training Large Language Models on Narrow Tasks Can Lead to Broad Misalignment.* Nature 649:584–589 (earlier: *Emergent Misalignment*, ICML 2025) | https://doi.org/10.1038/s41586-025-09937-5 | Narrow SFT shifts behaviour far outside the domain: the analogue of internal contamination (exp06 S-H3). Cite one version consistently |
| B | Lindsey et al. (2024). *Sparse Crosscoders for Cross-Layer Features and Model Diffing.* Transformer Circuits Thread (not peer reviewed) | https://transformer-circuits.pub/2024/crosscoders/index.html | The base-vs-fine-tuned diffing method we deliberately do not train (D10) |
| B | Arditi et al. (2024). *Refusal in Language Models Is Mediated by a Single Direction.* NeurIPS 2024 | https://proceedings.neurips.cc/paper_files/paper/2024/hash/f545448535dfde4f9786555403ab7c49-Abstract.html | The standard DiffMean-then-ablate/add recipe for our direction baselines |
| B | Soligo, Turner, Rajamanoharan, Nanda (2025). *Convergent Linear Representations of Emergent Misalignment.* arXiv preprint | https://arxiv.org/abs/2506.11618 | Separate narrow SFT runs share one direction: template for comparing the three schools' directions |

### Ideology and economic concepts in activations
| Pri | Work | Record | Why it matters here |
|---|---|---|---|
| A | Kim, Evans, Schein (2025). *Linear Representations of Political Perspective Emerge in Large Language Models.* ICLR 2025 | https://iclr.cc/virtual/2025/poster/28160 | Probes predict DW-NOMINATE and steering shifts ideology: the closest precedent for probing school identity |
| B | Zhang (2025). *Probing Political Ideology in LLMs.* Findings of EMNLP 2025 | https://aclanthology.org/2025.findings-emnlp.1267/ | Linear probes for ideology (record seen, not read in full) |
| B | Kabir (2026). *When Models Refuse: Political Steerability and Feature Richness as Measures of Ideological Depth.* arXiv preprint, single author | https://arxiv.org/abs/2508.21448 | The only SAE-on-ideology study found; low weight |

**Gap:** no peer-reviewed SAE study of economic-school concepts was found, so exp06 would be the first; say so
carefully in Ch. 2 ("we found no...").

Already in the library (not repeated): chen2026persona, kissane2024saes, zou2023representation, minder2025overcoming,
minder2026narrow, wang2026persona, galichin2026feature, turner2024steering, rimsky2024steering, marks2024geometry,
deng2026qwenscope, shuttleworth2025lora, wu2025axbench, guo2017calibration.

## 2. RQ2 (what the agent says) and RQ3 (how sure)

### RQ2: faithful, grounded output
| Pri | Work | Record | Why it matters here |
|---|---|---|---|
| A | Xu et al. (2025). *Beyond Correctness: Rewarding Faithful Reasoning in Retrieval-Augmented Generation.* TMLR (per arXiv comment) | https://arxiv.org/abs/2510.13272 | Closest analogue: Think–Search, Information–Think and Think–Answer faithfulness for tool-using agents map onto [Think]→tool call, tool return→[Think], [Proof]→probabilities |
| A | Wu et al. (2024). *ClashEval: Quantifying the Tug-of-War between an LLM's Internal Prior and External Evidence.* NeurIPS 2024 D&B | https://neurips.cc/virtual/2024/poster/97658 | Precedent for exp07's counterfactual tool results: perturbations from subtle to blatant; models resist implausible edits |
| A | Chen et al. (2024). *Do Models Explain Themselves? Counterfactual Simulatability of Natural Language Explanations.* ICML 2024, PMLR 235:7880–7904 | https://proceedings.mlr.press/v235/chen24bl.html | Precision and generality of an explanation on counterfactual inputs: does [Proof] predict which conclusion moves? |
| A | Korbak et al. (2025). *Chain of Thought Monitorability: A New and Fragile Opportunity for AI Safety.* arXiv preprint | https://arxiv.org/abs/2507.11473 | Visible reasoning as a monitorable channel that training can erode |
| B | Ling et al. (2023). *Deductive Verification of Chain-of-Thought Reasoning.* NeurIPS 2023 | https://proceedings.neurips.cc/paper_files/paper/2023/hash/72393bd47a35f5b3bee4c609e7bba733-Abstract-Conference.html | Steps that cite their premises (Natural Program): nearest format to the layer-typed [Proof]; their verifier is an LLM, ours is code |
| B | Song et al. (2025). *Measuring and Enhancing Trustworthiness of LLMs in RAG through Grounded Attributions and Learning to Refuse.* ICLR 2025 | https://proceedings.iclr.cc/paper_files/paper/2025/hash/4c88827decab6c046b881a2c3a99c76f-Abstract-Conference.html | Trust-Score (answer, citation, refusal) on small open models incl. Qwen2.5-7B: comparison point for code-checked grounding |
| F | Baker et al. (2025). *Monitoring Reasoning Models for Misbehavior and the Risks of Promoting Obfuscation.* arXiv preprint | https://arxiv.org/abs/2503.11926 | Rewarding the CoT monitor makes reasoning obfuscated: any future RL reward must leave [Think] alone |

### RQ3: calibration, uncertainty and diversity
| Pri | Work | Record | Why it matters here |
|---|---|---|---|
| A | Kuhn, Gal, Farquhar (2023). *Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in Natural Language Generation.* ICLR 2023 | https://arxiv.org/abs/2302.09664 | Origin of semantic entropy (Farquhar 2024 is in the library, this is not): disagreement at the level of meaning for the sampling and school arms |
| A | Lin, Hilton, Evans (2022). *Teaching Models to Express Their Uncertainty in Words.* TMLR (venue via MLAnthology) | https://arxiv.org/abs/2205.14334 | Fine-tuning can calibrate verbalised probabilities: precedent for trained agents emitting scenario probabilities |
| A | He et al. (2025). *Chronologically Consistent Large Language Models.* arXiv preprint | https://arxiv.org/abs/2502.21206 | Models trained only on text available at each date: the strict alternative to our claimed cutoff; a limitation to state |
| A | Choi et al. (2025). *Debate or Vote: Which Yields Better Decisions in Multi-Agent Large Language Models?* NeurIPS 2025 | https://arxiv.org/abs/2508.17536 | Voting explains most debate gains: supports pooling independent school outputs and keeping debate out of H8 |
| A | Jiang et al. (2025). *Artificial Hivemind: The Open-Ended Homogeneity of Language Models (and Beyond).* NeurIPS 2025 | https://arxiv.org/abs/2510.22954 | Different models give similar outputs: the "different models" arm may carry little real diversity; report pairwise error correlation per arm |
| B | Hou et al. (2024). *Decomposing Uncertainty for Large Language Models through Input Clarification Ensembling.* ICML 2024, PMLR 235:19023–19042 | https://proceedings.mlr.press/v235/hou24b.html | Aleatoric/epistemic split by ensembling input variants: template for the persona arm |
| B | Zhang et al. (2025). *Stop Overvaluing Multi-Agent Debate — We Must Rethink Evaluation and Embrace Model Heterogeneity.* arXiv preprint | https://arxiv.org/abs/2502.08788 | Debate rarely beats self-consistency; heterogeneity helps: equal-compute baselines |
| B | Benhenda (2026). *Look-Ahead-Bench: A Standardized Benchmark of Look-ahead Bias in Point-in-Time LLMs for Finance.* arXiv preprint, single author | https://arxiv.org/abs/2601.13770 | Look-ahead bias as decay across periods: template for a pre/post-cutoff negative control |
| F | Schoenegger et al. (2025). *AI-Augmented Predictions: LLM Assistants Improve Human Forecasting Accuracy.* ACM TiiS 15(1) (from the economics search) | https://doi.org/10.1145/3707649 | Template for a human study: do analysts forecast better when they read the proof? |

Already in the library (not repeated): turpin2023language, lanham2023measuring, chen2025reasoning,
arcuschin2026chain, matton2025walk, gao2023enabling, rashkin2023measuring, cohenwang2024contextcite, zhao2026agents,
zhao2026verifying, tian2023just, xiong2024can, kadavath2022language, farquhar2024detecting, lyu2025calibrating,
schoenegger2024wisdom, sarkar2024lookahead, glasserman2024assessing, lopezlira2025memorization, paleka2026pitfalls,
du2024improving, liang2024encouraging, gebele2026diversity, kim2025correlated, zheng2024helpful, hu2024quantifying.

### Small, cheap uses inside the current design (proposals, not adopted)
1. exp07: grade the counterfactual tool edits from subtle to blatant (ClashEval) and score whether [Proof] predicts
   which scenario moves (Chen et al. 2024). A null response to a blatant edit can be sanity-checking, not ignoring.
2. exp03 H8: report pairwise error correlation within each diversity arm (Artificial Hivemind; already the
   Kuncheva–Whitaker logic).
3. Disagreement matrix: state Gordon & Dahl (2013) as the counter-hypothesis (disagreement need not follow ideology)
   and control for the base model's interventionist tilt (Lee et al. 2026).
4. Limitations: the knowledge cutoff is claimed, not enforced (He et al. 2025); a pre/post-cutoff check on the
   exp03 events would bound the leakage.

## 3. Economics, ideology, the disagreement matrix

### LLMs as economic agents and forecasters
| Pri | Work | Record | Why it matters here |
|---|---|---|---|
| A | Horton, Filippas, Manning (2023). *Large Language Models as Simulated Economic Agents: What Can We Learn from Homo Silicus?* NBER WP 31122 | https://www.nber.org/papers/w31122 | Founding claim that prompted LLMs can stand in for economic agents; licenses prompted-only frameworks |
| A | Alam, Boyle, Li, Sekhposyan (2026). *ChatMacro: Evaluating Inflation Forecasts of Generative AI.* FRBSF WP 2026-04 | https://doi.org/10.24148/wp2026-04 | Out-of-sample ChatGPT inflation forecasts are mostly inaccurate and stale: motivation for leakage-free, real-time evaluation (finding from a summary, check the PDF) |
| B | Anesti, Hill, Joseph (2026). *Inflation Attitudes of Large Language Models.* Bank of England SWP 1190 | https://arxiv.org/abs/2512.14306 | Central-bank test; no consistent model of inflation; Shapley attribution to prompt content |
| B | Zarifhonarvar (2024). *Generating Inflation Expectations with Large Language Models.* SSRN 4825076 | https://doi.org/10.2139/ssrn.4825076 | Disagreement differs between proprietary and open models: model diversity as a confound for H8 |

### Ideology in LLMs and among economists
| Pri | Work | Record | Why it matters here |
|---|---|---|---|
| A | Lee et al. (2026). *Ideological Bias in LLMs' Economic Causal Reasoning.* COLM 2026 (per arXiv comment) | https://arxiv.org/abs/2604.21334 | 17 of 20 models do better when the verified effect matches interventionist expectations: a base-model tilt on the state–market axis to control for |
| A | Feng, Park, Liu, Tsvetkov (2023). *From Pretraining Data to Language Models to Downstream Tasks: Tracking the Trails of Political Biases Leading to Unfair NLP Models.* ACL 2023 | https://aclanthology.org/2023.acl-long.656/ | Political lean comes from pretraining data and can survive in school adapters (RQ1) |
| A | Röttger et al. (2024). *Political Compass or Spinning Arrow? Towards More Meaningful Evaluations for Values and Opinions in LLMs.* ACL 2024 | https://aclanthology.org/2024.acl-long.816/ | Forced-choice compass tests are fragile: why we position frameworks by behaviour (forecast distance), not by questionnaires |
| A | Javdani & Chang (2023). *Who Said or What Said? Estimating Ideological Bias in Views among Economists.* Cambridge Journal of Economics 47(2):309–339 | https://doi.org/10.1093/cje/beac071 | **Cited in configs/frameworks.toml but missing from the library.** School labels themselves are cues |
| A | Gordon & Dahl (2013). *Views among Economists: Professional Consensus or Point-Counterpoint?* AER P&P 103(3):629–635 | https://doi.org/10.1257/aer.103.3.629 | IGM panel: broad consensus, residual differences not left–right. A risk for "position distance predicts disagreement"; discuss as a limitation |
| B | Jelveh, Kogut, Naidu (2024). *Political Language in Economics.* Economic Journal 134(662):2439–2469 | https://doi.org/10.1093/ej/ueae026 | Predicts economists' partisanship from text: template for validating positions from text |
| B | Iazdi (2023). *Ortho-Heterodox Biases and the Economist Algorithms of ChatGPT.* Iberian Journal of the History of Economic Thought 10(2):79–90 | https://doi.org/10.5209/ijhe.91545 | Only direct orthodox/heterodox test of an LLM; economists disagreed on what "orthodox" means (caution for axis 2) |
| B | Aldahoul et al. (2025). *The Political Ideology of LLMs: Measurement, Inconsistency, and Persuasive Influence.* arXiv preprint | https://arxiv.org/abs/2505.04171 | A single left–right score hides topic-specific stances |

### Pluralistic alignment (framing for the motivation)
| Pri | Work | Record | Why it matters here |
|---|---|---|---|
| A | Sorensen et al. (2024). *Position: A Roadmap to Pluralistic Alignment.* ICML 2024, PMLR 235:46280–46302 | https://proceedings.mlr.press/v235/sorensen24a.html | Overton / steerable / distributional pluralism = show every school's scenarios / school adapters / a calibrated mixture |
| B | Feng et al. (2024). *Modular Pluralism: Pluralistic Alignment via Multi-LLM Collaboration.* EMNLP 2024 | https://aclanthology.org/2024.emnlp-main.240/ | Small community models plugged into a large one: structurally close to school adapters |

### Positions and scaling (method sources for the disagreement matrix)
| Pri | Work | Record | Why it matters here |
|---|---|---|---|
| A | Lavoie (2014). *Post-Keynesian Economics: New Foundations.* Edward Elgar | https://openlibrary.org/isbn/9781847204837 (catalogue) | **Cited in configs/frameworks.toml but missing from the library.** Source of the orthodox–heterodox axis |
| A | Jolly et al. (2022). *Chapel Hill Expert Survey Trend File, 1999–2019.* Electoral Studies 75:102420 (earlier: Bakker et al. 2015, Party Politics 21(1)) | https://doi.org/10.1016/j.electstud.2021.102420 | Citable CHES source for the economic left–right axis and the expert-coding protocol |
| A | Laver, Benoit, Garry (2003). *Extracting Policy Positions from Political Texts Using Words as Data.* APSR 97(2) | https://doi.org/10.1017/S0003055403000698 | Validation by reference texts; already the analogy in the divergence design |
| A | Poole & Rosenthal (1985). *A Spatial Model for Legislative Roll Call Analysis.* AJPS 29(2) | https://doi.org/10.2307/2111172 | Recovering low-dimensional structure from (dis)agreement; choosing the number of dimensions |
| B | Slapin & Proksch (2008). *A Scaling Model for Estimating Time-Series Party Positions from Texts.* AJPS 52(3):705–722 | https://doi.org/10.1111/j.1540-5907.2008.00338.x | Scaling without reference texts: an independent check of the hand-coded axes |
| B | Kruskal (1964). *Multidimensional Scaling by Optimizing Goodness of Fit to a Nonmetric Hypothesis.* Psychometrika 29(1):1–27 | https://doi.org/10.1007/BF02289565 | MDS stress for the disagreement map |

### Development economics (candidate L3 extension; future work)
Catalogue-confirmed: Williamson (1990), "What Washington Means by Policy Reform", in *Latin American Adjustment*
(Institute for International Economics); Chang (2002), *Kicking Away the Ladder* (Anthem); Rodrik (2007), *One
Economics, Many Recipes* (Princeton) and Rodrik (2006), "Goodbye Washington Consensus, Hello Washington Confusion?",
JEL 44(4):973–987, https://doi.org/10.1257/jel.44.4.973; Wade (1990), *Governing the Market* (Princeton); Amsden
(1989), *Asia's Next Giant* (Oxford); Johnson (1982), *MITI and the Japanese Miracle* (Stanford). For the
regime-type axis (the Nordic and Singapore quadrants): Esping-Andersen (1990), *The Three Worlds of Welfare
Capitalism*, catalogue only, to be checked.

Already in the library (not repeated): li2024econagent, bybee2023ghost, hansen2025simulating, hansen2023can,
fariaecastro2024artificial, iadisernia2025prompting, kazinnik2025fomc, santurkar2023whose, rozado2024political,
argyle2023out, park2023generative, lee2025econcausal, halawi2024forecasting, schoenegger2024wisdom,
karger2025forecastbench, turtel2025outcome, du2024improving, liang2024encouraging, chan2024chateval,
lahiri2010measuring, tetlock2005expert, mankiw2006macroeconomist, blanchard2009state.

Dropped as unverifiable: an unreachable PDF auditing 15 LLMs against the IGM panel; Mantel (1967), the
distance-matrix correlation test (no record located; if the divergence analysis uses a Mantel-type permutation test,
the reference session should find the source).

## 4. Future work (for Ch. 7)

Ranked by fit with the thesis; each is anchored to verified work above.

1. **Development-economics schools in L3** (Williamson 1990; Johnson 1982; Wade 1990; Amsden 1989; Rodrik 2006,
   2007; Chang 2002). Washington Consensus, developmental state and institutional pluralism as prompted-only
   frameworks first, placed by the same disagreement matrix; a regime-type axis (democratic vs authoritarian) needs its
   own anchor (CHES-style coding; Esping-Andersen for the welfare-state quadrant, to be checked).
2. **Reinforcement learning on proper scoring rules** (turtel2025outcome, in the library), with the reward on the
   probabilities and the [Proof] references only, never on [Think] (Baker et al. 2025; Korbak et al. 2025). Needs
   10k+ resolved questions; exp03 is the seed.
3. **Live, out-of-sample evaluation** of the school agents (karger2025forecastbench; Alam et al. 2026 show why only
   live evaluation is credible), with a chronologically consistent base model (He et al. 2025) to remove leakage by
   construction.
4. **Retrieval-based test-time training as a comparison, gated by calibration** (Hardt & Sun 2024; Akyürek et al.
   2025; C-TPT and Amin & Kim on over-confidence): a throwaway LoRA on retrieved episodes versus the frozen adapter with
   the same episodes in context.
5. **Human–AI teaming** (Schoenegger et al. 2025, TiiS): do analysts forecast better reading a school's proof than its
   probabilities alone? Tests the auditability claim of RQ2 with people.
6. **Inside-the-model extensions** (Soligo et al. 2025; Betley et al. 2026; Jain et al. 2024; Prakash et al. 2024):
   a shared "school-adopted" direction across the three schools, a spillover audit on non-macro prompts, and wrapper
   versus new mechanism — only with public SAEs (D10).
7. **Scaling the agents' texts** (Slapin & Proksch 2008; Laver et al. 2003; Jelveh et al. 2024): position the schools
   from their proofs alone and compare with the expert coding.
