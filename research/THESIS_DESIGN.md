# Thesis design (source of truth for priorities and dates)

MPhil, PolyU DSAI. Author: Futian Jiang. Chief supervisor: Prof. ZHANG Chengqi. Last revised 2026-10-31.
The human-facing version (Traditional Chinese, with rationale) is the design document linked in the README.

## 1. Constraints from the graduation rules

| Rule | Source | Consequence for the design |
|---|---|---|
| Initial thesis submitted before the end of the Normal Period (full-time MPhil: 2 years, max 3) | RPg Handbook 10.2; DSAI RPg 2025/26 | Enrolled Sept 2025 → Normal Period ends ≈ 2027-08-31 (**confirm exact date**) |
| Form GSB/2B + ≤ 3-page synopsis ≥ 4 months before submission | Handbook 10.2 | Title, RQs and contributions must be stable 4 months before submission |
| No accepted paper in a good venue → DSAI Thesis Assessment Committee screening before external examination | DSAI 5.7 | Duration unknown (**ask**); an accepted paper removes a whole review stage |
| Internal review ≈ 4 weeks, external review 6 weeks, ≥ 2 external (off-campus) examiners, both must agree | Handbook 10.3–10.4 | Oral ≈ 3–5 months after submission; examiners are field experts outside PolyU |
| Oral: 30 min presentation (max 40) + questions relayed by the BoE chair, ≈ 2 h | Handbook 10.4 | Every likely question needs a pre-registered experiment or an explicit limitation (§7) |
| English; format regulations; full similarity report | Handbook 10.1–10.2 | Reused paper text must be declared; Confirmation text is unpublished |
| GenAI: AI-generated material must be identified; the student is accountable; GenAI must not write the work | PolyU Student Guide on GenAI (rev. 2026-01-05) | §6: thesis prose by the author; agent output logged in `research/AI_USE_LEDGER.md` |
| Before submission: 7 credits, GPA ≥ 2.70, AIE, Research Seminars I & II (≥ 10 seminars + ≥ 1,500-word report per year), English per RLSA, National Education online course | DSAI 5.1–5.9 | Checklist item in the timeline (§5) |

## 2. Working title, research questions, contributions

**Working title**: *Macro-MOSAIC: Multi-School Language-Model Reasoning for Macroeconomic Event Analysis and
Forecasting* (the Confirmation title ended "…and Cross-Asset Allocation"; see decision D2).

| RQ | Question | Evidence | Chapter |
|---|---|---|---|
| RQ1 | Does parameter-efficient fine-tuning instill distinct, theory-consistent school reasoning beyond the best prompting baseline (including the model's own thinking mode); what changes inside the model; and does the advantage survive a stronger 2026 base? | exp01 (Qwen3-8B; A/B/C, D, T; keyword metrics + validated judge); exp06 (sparse-autoencoder instrument and mechanism); exp01b (Qwen3.5-27B, D7) | 4 |
| RQ2 | Do macro-state analogies predict asset reactions better than narrative or naive similarity? | exp02 (expanding-window retrieval on the episode DB) | 5 |
| RQ3 | Do pooled school forecasts beat single schools and prompted schools on real, post-cutoff macro outcomes; are they calibrated and coherent; and is disagreement among schools (contested L3 frameworks) informative? | exp03 (resolved markets 2025–26, H1–H7), exp04 (coherence), exp05 (live, optional) | 6 |

Contributions (claim wording must stay at this strength):
1. A point-in-time macro episode database and a leakage-controlled forecasting benchmark built from resolved
   prediction markets (data and evaluation methodology).
2. Evidence on fine-tuning versus prompting for theory-specific reasoning, with a validated LLM judge and a
   sparse-autoencoder analysis of what fine-tuning changes inside the model (school concepts versus vocabulary;
   internal cross-school contamination), with features mapped to the L3 school entries.
3. An analogy-retrieval method with a principled covariance estimate and a time-respecting evaluation.
4. Evidence on whether heterogeneous reasoning agents should be pooled, with coherence-aware aggregation.
5. An epistemically layered design (pmpol's L0–L5 ontology): contested theories are L3 frameworks kept as separate
   agents and shown side by side; every forecast carries a proof back to L0–L4 and an analytic-confidence grade,
   and both disagreement and confidence are tested as predictors of error (exp03 H6–H7).

### 2a. Knowledge layers (the thesis's epistemic architecture)

| Layer (pmpol) | Macro-MOSAIC | Rule |
|---|---|---|
| L0 rules | release definitions and grids, FOMC step sizes, market resolution rules | hard constraints: scenario sets, coherence checks |
| L1 point-in-time facts | indicators as published at t (ALFRED vintages; bitemporal) | the only facts a model sees; never revised data |
| L2 base rates | analog episodes (Stage 1), historical distributions, venue calibration | priors and baselines |
| L3 contested frameworks | Keynesian, Austrian, Monetarist (`kb/L3/schools.yaml`) | cited, not adopted; one agent each; side by side |
| L4 market observations | Kalshi / Polymarket prices | benchmark only; never a model input |
| L5 inferences | school distributions, pools | must carry a proof; ICD 203 likelihood words; analytic confidence = weakest link |

The pooled forecast is an L5 summary and never replaces the per-school views in any output. pmpol's `proof.py` and
`confidence.py` (vendor/) are reused, credited as team code. exp06 adds an internal view of L3: SAE features that
separate the schools are labelled and mapped to the fields of each L3 entry (drivers, frictions, policy, signals),
giving "feature cards" that show which school concepts a model activates while it reasons.

## 3. Chapter map

1 Introduction · 2 Background and literature (Confirmation survey + forecasting, prediction-market calibration,
coherence, distillation, analog forecasting) · 3 Data (episode DB, point-in-time states, market question set) ·
4 School agents (Stage 2, RQ1) · 5 Analogy retrieval (Stage 1, RQ2) · 6 From reasoning to calibrated forecasts
(Stage 3, RQ3) · 7 Discussion (limitations, allocation as application, AI use, PhD directions) · 8 Conclusion ·
Appendices: prompts, lexicons, judge rubric, pre-registrations and amendments, reproducibility, AI-use statement.

## 4. Changes from the Confirmation plan (to be explained in the thesis, Ch. 1 and 7)

| Confirmation plan | Now | Why |
|---|---|---|
| Stage 4 Kelly allocation + 2023–2025 walk-forward backtest as main evidence | Application discussion / optional demo (D2) | 2023–24 lies inside the models' pretraining period (look-ahead); few events → no power; resolved-market evaluation answers the same question cleanly |
| Stage 3 regime-conditional weights calibrated on Polymarket/Metaculus geopolitical questions | Pooling + skill weights + temperature scaling + coherence projection, calibrated on resolved **macro** markets | Regime cells would be nearly empty in a leakage-free window; same-domain calibration data |
| Keyword metrics only | Keyword metrics + LLM judge validated by two human raters | Examiner question: does vocabulary equal reasoning? |
| EconCausal / EconLogicQA benchmarks | Dropped unless time remains (P2) | Lower value than outcome-based evaluation for this thesis |
| Covariance for Mahalanobis estimated on 141 episodes | Ledoit–Wolf on the monthly indicator panel, expanding window | 35 dimensions vs 141 samples (Prof. Jiang's concern) |
| School adapters on Qwen2.5-7B-Instruct (4-bit QLoRA) | Retrained on Qwen3-8B (bf16 LoRA, same r/α/epochs/data), exp01 amendment 4; optional reproduction on Qwen2.5-7B (A7/C7) | The Confirmation adapters were not kept, so retraining was needed anyway; Qwen3-8B has public SAEs and keeps a long leakage-free window |
| Outputs only (keywords, judge) | + SAE features as a third instrument and a look inside the model (exp06) | Examiner question: vocabulary or reasoning? Interpretability of the school agents |

## 4a. Models and tools (revised 2026-10-31, pending D7, D10, D11)

The Confirmation's adapters were not kept, so every base model is retrained anyway. Choice rule: a public sparse
autoencoder (exp06), a leakage-free history long enough for exp03, and LoRA tooling that works on one GPU.

| Option | Use in the thesis | Why / limits |
|---|---|---|
| **Qwen3-8B** (2025-04-29, Apache-2.0) + school LoRA retrained (amendment 4 draft) | Primary for exp01, exp03, exp06 | One generation newer than the Confirmation's model, same size class; public SAEs for all 36 layers (Qwen-Scope, trained on Qwen3-8B-Base, transfer checked by gate S0); leakage-free history from 2025-05 (≈ 18 months of resolved markets); mature LoRA tooling |
| Qwen2.5-7B-Instruct (Confirmation) | Optional reproduction arms A7/C7 (amendment 4, Change 4) | Continuity with Confirmation Table 4.3, only if the original trajectories exist |
| **Qwen3.5-27B** (2026-02-24, Apache-2.0) + school LoRA | exp01b (RQ1 on a stronger 2026 base) and the exp06 replication; exp03 secondary subset (≥ 2026-03) and exp05 (D7) | The only 2026 model with a public SAE trained on the post-trained model itself (64 layers); bf16 LoRA ≈ 56 GB (80 GB card); hybrid Gated DeltaNet needs spike S4 |
| Qwen3.6-27B, Qwen3.8-27B, Gemma 4 31B (Google, 2026-03-31, Apache-2.0) | exp05 prompted references (optional); Gemma 4 31B as an optional cross-family check of H1 (P2) | Newer or comparable, but no public SAE and little or no leakage-free history; Gemma 4 31B bf16 LoRA exceeds 80 GB |
| Gemma 3 (2025-03) + Gemma Scope 2 (Google, 2025-12: SAEs for PT and IT models, transcoders) | Fallback for exp06 if the Qwen-Scope base-model SAEs fail gate S0 | The most mature open SAE suite (SAELens, Neuronpedia) |
| Qwen-Scope SAEs (Qwen, 2026-05) | exp06 instrument (Part I reader) and mechanism (Part II) | Residual stream, every layer, TopK (L0 50 / 100), 64K–80K features; "qwen" licence, research use |
| Decision models (TypeSafe Jev; open Vega, Kev incl. Kev-27B on Qwen3.8; Ollama `/v1/systemone`) | Measurement only (D8): a second, open, reproducible judge (score type, per-level probabilities); a decision head over scenario bins in exp05 only | Per-option probabilities with a fitted temperature; vendor calibration claims must be verified (pmpol survey §13); Jev is closed; Kev fine-tuning needs ~1,000 labels; Qwen3.5/3.8 bases know 2025–26, so not for historical exp03 |
| Claude Opus 5.5 | Arm D (frontier reference), the exp01 judge, exp06 feature labels | Evaluation and analysis only. Not a teacher: the Consumer Terms (§3.2) bar using the service to train models |
| RL with proper-scoring rewards (GRPO/ReMax on Brier; Turtel et al., TMLR 2025; Mantic 2026) | Future work / PhD | Published systems used ~10k–110k resolved questions; exp03 yields hundreds. exp03's dataset is the seed for it |
| Activation steering of school directions | exp06 Part III (optional, dev only) | A third way between prompting and fine-tuning; expected to trail prompting (AxBench, ICML 2025) |

## 5. Timeline (target submission 2027-06-15; hard limit = end of Normal Period)

| By | Milestone | Owner |
|---|---|---|
| 2026-11-02 | RunPod pod up; Task S spikes: Qwen3-8B serving, `mosaic train`, SAE reader check, Qwen3.5-27B LoRA | agent |
| 2026-11-08 | Assets in hand (prompts, lexicons, trajectories or the D11 teacher choice, 96 test events, dev events, episode DB); decisions D1–D11; amendment 4 registered; meeting with Prof. Zhang | human |
| 2026-11-12 | Qwen3-8B school adapters trained (Task 0), seed-episode audit | agent |
| 2026-11-20 | exp01b go/no-go (D7) from spike S4 | human |
| 2026-11-22 | exp01 parity + dev tuning (arm B incl. thinking switch); exp03 data build and data card | agent |
| 2026-11-25 | exp03 registered (counts known, no scores) | human |
| 2026-12-01 | exp05 go/no-go | human |
| 2026-12-04 | exp06 instrument ready (gate S0, features, labels) | agent |
| 2026-12-06 | exp01 + exp06 registered and frozen; exp01 final (with exp06 Part I) + judge (test) | human |
| 2026-12-20 | exp01 human ratings (2 raters); exp03 final (test window) | human runs, agent prepares |
| 2027-01-04 / 01-11 | IJCAI 2027 abstract / paper (if D3 = yes): exp01 + exp06, or exp01 + exp03 | human writes |
| 2027-01-17 | exp06 Part II (mechanism) final | human runs, agent prepares |
| 2027-01-24 | exp01b final (if go), with the exp06 replication | human |
| 2027-01-31 | exp02 final; exp03 ablations | agent → human |
| 2027-02-07 | exp04 final | agent → human |
| 2027-02-15 | **GSB/2B + 3-page synopsis**; supervisor nominates ≥ 2 external examiners; prerequisites checked | human + supervisor |
| 2027-04-21 | IJCAI decision (accepted → no DSAI screening) | — |
| 2027-04-30 | Full thesis draft | human |
| 2027-05-31 | Supervisor review done; similarity report; format check; AI-use statement | human |
| 2027-06-15 | **Initial thesis submission** | human |
| ≈ 2027-09/10 | Oral examination (30–40 min talk) | human |

## 6. Rules for AI assistance (applies to every Claude session)

- Thesis prose, research decisions and interpretations are the author's. Agents write code, run experiments, and
  produce result tables and factual summaries; they do not draft thesis chapters.
- Every substantive agent contribution (code module, data transformation, analysis, design draft) is logged in
  `research/AI_USE_LEDGER.md`. The thesis AI-use statement is written from that ledger.
- Confirmatory results come only from pre-registered, frozen, human-run steps. Everything else is labelled
  exploratory in the thesis.

## 7. Oral-examination question matrix

| Likely question | Answer lives in |
|---|---|
| Why fine-tune instead of chain-of-thought prompting? | exp01 H1 (C vs best B), exp03 H5 |
| Do keyword scores measure reasoning? | exp01 amendment 2 (judge + human validation, convergent validity) |
| Why several schools? Does pooling help? | exp03 H1, exp04 H1 |
| Could the models have seen the answers? | Cutoff policy; point-in-time inputs; exp05 if run |
| Are the results statistically reliable? | Pre-registration, event-level resampling, Holm |
| How does it compare with markets / simple baselines? | exp03 market, history, uniform; H4 encompassing test |
| Is the retrieval better than simple similarity (History Rhymes)? | exp02 H1–H3 |
| Covariance with 35 dimensions and 141 episodes? | exp02 protocol (monthly panel, shrinkage) |
| Why these three schools? | Ch. 4 design rationale |
| What happened to allocation (Stage 4)? | §4 above; Ch. 7 |
| Synthetic GPT-4o training data: teacher bias? | Ch. 4 limitations; exp01 arm T (if run) |
| How was AI used in this work? | AI-use statement from the ledger |
| Why not a newer, larger model? | exp01b (Qwen3.5-27B, the newest model with a public SAE); §4a (newer models have no SAE and little leakage-free history; they appear in exp05) |
| Why did the base model change after the Confirmation? | Amendment 4: adapters not kept, retraining needed anyway; Qwen3-8B chosen for public SAEs, the leakage window and tooling; reproduction arms A7/C7 if the original data exist |
| Does fine-tuning teach the school's concepts or only its words? | exp06 S-H2 (concept features that also separate the schools on keyword-free text), next to the judge and human ratings |
| Can SAE features be trusted? | exp06 gate S0, DiffMean and probe baselines, two SAE sparsities, replication with an SAE trained on the post-trained 27B model, human-checked labels |
| What happens inside the model when it argues as a school? | exp06 feature cards mapped to the L3 entries; internal contamination (S-H3) |
| How much should a reader trust one forecast? Is it interpretable? | Proof per forecast (L0–L4 trail) + analytic confidence, validated by exp03 H7 |
| What do you do when the schools disagree? | L3 rule (side by side, not adopted); exp03 H6 tests disagreement as an uncertainty signal |

## 8. Decisions pending (human)

- **D1** Target submission date and exact Normal Period end (default 2027-06-15).
- **D2** Stage 4: future work (default) vs small descriptive demo on 2025–26 events; thesis title follows.
- **D3** IJCAI 2027 attempt (Jan 11) with exp01 + exp03, or later venue (KDD 2027 cycle 2 ≈ Feb, ICAIF 2027).
- **D4** Any external constraint (e.g. PhD start date) that moves D1.
- **D5** Second human rater for exp01.
- **D6** exp05 go/no-go on 2026-12-01.
- **D7** Base models (revised 2026-10-31): Qwen3-8B as the primary model (amendment 4) and Qwen3.5-27B for exp01b
  and the exp06 replication (go/no-go after spike S4, by 2026-11-20). Gemma 4 31B cross-family check: P2.
- **D8** Decision models as measurement tools (second judge Kev-27B; decision head in exp05): yes/no.
- **D9** Who reviews the L3 school entries (`kb/L3/schools.yaml`, two-person rule) before freeze.
- **D10** exp06 scope: Parts I and II (default; Part I registered with the exp01 freeze) or Part I only;
  Part III (ablation, steering, data audit) optional.
- **D11** Training data: the original 1,500 GPT-4o trajectories if they were kept (preferred), otherwise
  regenerated (GPT-4o if still offered, or an open-weight teacher whose licence allows training on its outputs);
  and whether to run the Qwen2.5-7B reproduction arms A7/C7.
