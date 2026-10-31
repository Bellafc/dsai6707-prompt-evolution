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
| RQ1 | Does parameter-efficient fine-tuning instill distinct, theory-consistent school reasoning beyond the best prompting baseline? | exp01 (A/B/C, D, T; keyword metrics + validated judge) | 4 |
| RQ2 | Do macro-state analogies predict asset reactions better than narrative or naive similarity? | exp02 (expanding-window retrieval on the episode DB) | 5 |
| RQ3 | Do pooled school forecasts beat single schools and prompted schools on real, post-cutoff macro outcomes, and are they calibrated and coherent? | exp03 (resolved markets 2025–26), exp04 (coherence), exp05 (live, optional) | 6 |

Contributions (claim wording must stay at this strength):
1. A point-in-time macro episode database and a leakage-controlled forecasting benchmark built from resolved
   prediction markets (data and evaluation methodology).
2. Evidence on fine-tuning versus prompting for theory-specific reasoning, with a validated LLM judge.
3. An analogy-retrieval method with a principled covariance estimate and a time-respecting evaluation.
4. Evidence on whether heterogeneous reasoning agents should be pooled, with coherence-aware aggregation.

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

## 5. Timeline (target submission 2027-06-15; hard limit = end of Normal Period)

| By | Milestone | Owner |
|---|---|---|
| 2026-11-08 | Assets in hand (prompts, lexicons, adapters, trajectories, 96 test events, episode DB); decisions D1–D6; meeting with Prof. Zhang | human |
| 2026-11-22 | exp01 Task 0 parity + dev tuning; exp03 data build and data card | agent |
| 2026-11-25 | exp03 registered (counts known, no scores) | human |
| 2026-11-29 | exp01 freeze + final + judge (test) | human |
| 2026-12-01 | exp05 go/no-go | human |
| 2026-12-13 | exp01 human ratings (2 raters) | human |
| 2026-12-20 | exp03 final (test window) | human runs, agent prepares |
| 2027-01-04 / 01-11 | IJCAI 2027 abstract / paper (if D3 = yes): exp01 + exp03 | human writes |
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

## 8. Decisions pending (human)

- **D1** Target submission date and exact Normal Period end (default 2027-06-15).
- **D2** Stage 4: future work (default) vs small descriptive demo on 2025–26 events; thesis title follows.
- **D3** IJCAI 2027 attempt (Jan 11) with exp01 + exp03, or later venue (KDD 2027 cycle 2 ≈ Feb, ICAIF 2027).
- **D4** Any external constraint (e.g. PhD start date) that moves D1.
- **D5** Second human rater for exp01.
- **D6** exp05 go/no-go on 2026-12-01.
