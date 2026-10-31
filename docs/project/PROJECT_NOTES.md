# Project notes (archived from the claude.ai Project "PolyU", 2026-10-31)

Until 2026-10-31 the work was coordinated in a claude.ai Project. This file keeps what that Project knew that is
not already in `research/THESIS_DESIGN.md`, so that Claude Code sessions on this repository start with the same
context. Where the two disagree, `research/THESIS_DESIGN.md` and the pre-registrations win: the notes below
describe the Confirmation-era plan (June 2026), much of which has since been redesigned.

## People

- Author: Futian Jiang, full-time MPhil, PolyU Department of Data Science and AI (DSAI), enrolled September 2025.
- Chief supervisor: Prof. ZHANG Chengqi.
- Support: Bella (Zheng Chen), PhD student, HKUST CSE (owner of this repository and of the claude.ai account).
- Confirmation reviewers: Bo (nine major comments), Andrew (second-round comments), Zhanke (senior student; signed
  off on the revisions).
- Confirmation panel: Prof. ZHANG Chengqi (Chair Professor; distributed AI, data mining); Prof. HUANG Jiaxing
  (agentic multimodal AI, RL-driven reasoning such as MCTS and GRPO); Prof. JIANG Binyan (statistics,
  high-dimensional data, network statistics).

## Confirmation of Registration (completed, June 2026)

Files in `docs/project/confirmation/`:

| File | What it is |
|---|---|
| `jft_confirmation_final.pdf` | Final Confirmation report, "AI Agents in Finance: A Survey" + Macro-MOSAIC proposal (65 pages) |
| `jft_confirmation_final.txt` | Full text of the report (`pdftotext -layout`), for searching and quoting |
| `macro_mosaic_confirmation.html` | 30-slide static HTML deck (16:9, IEEE citations [1]–[49]); Chinese speaker notes toggle with the N key |
| `phd_motivation_and_plan.md` | Spoken statement "Why PhD & Research Plan" used at the Confirmation (Chinese) |

The Confirmation literature review grew out of Bella's HKUST PQE survey, kept in `docs/project/survey_pqe/`
(`main.tex`, `references.bib`, 112 entries).

Not archived, by decision of the human (2026-10-31): the LaTeX source of the report, the 36-slide PowerPoint deck
and the Chinese translation. The thesis text and any new slides are written from scratch; the report's content is
taken from the PDF and its text version above. The DSAI programme rules that matter are summarised in
THESIS_DESIGN §1.

### Confirmation-era design (superseded where THESIS_DESIGN.md says so)

Macro-MOSAIC = Mixture-Of-Schools Analogy-Informed Chains, a four-stage pipeline:

1. Historical analogy retrieval: dual-channel score (semantic cosine + Mahalanobis distance over a 35-dimensional
   FRED macro state vector). Planned.
2. Multi-school causal chains: three LoRA adapters (Keynesian, Austrian, Monetarist; r = 32) on
   Qwen2.5-7B-Instruct. Done, but **the adapters were not saved**; they are retrained on Qwen3-8B (amendment 4).
3. Bayesian aggregation with regime-conditional weights and Platt-scaling calibration. Planned.
4. Cross-asset allocation with fractional Kelly and walk-forward backtesting 2023–2025. Planned (dropped from the
   thesis core; see THESIS_DESIGN decision D2).

Data: 141 macro episodes (1971–2025), 35 FRED indicators per episode, 22 instruments, 13,571 asset-reaction data
points, 19 transmission channels. Training: 500 synthetic trajectories per school (1,500 in total, GPT-4o as
teacher). Test: 96 held-out events (stratified).

Preliminary results reported at the Confirmation: school-specific consistency +59.3 % on average; Austrian
0.146 → 0.319 (+118.8 %), Monetarist 0.230 → 0.528 (+129.7 %); inter-school Jaccard diversity 0.778 → 0.853
(p < 0.01); cross-school contamination reduced to near zero; the Keynesian composite score dropped, explained as
specialisation into the New Keynesian framework.

Planned at the Confirmation: five ablations (highest priority −Multi-school), four external baselines (incl. BVAR
and GPT-4o zero-shot), EconCausal and EconLogicQA evaluations.

### Revisions made after reviewer feedback (keep them in the thesis)

- Novelty claims softened throughout ("validates the core design hypothesis", "first open dataset", "entirely
  absent from the literature" removed); abstract made consistent with the body.
- Post-Keynesian school removed everywhere (three schools, not four); table statistics updated (mean length 935).
- Calibration language unified (Platt scaling vs isotonic regression); temperature scaling cites Guo et al. 2017.
- Six bibliography errors fixed (TradingAgents, TradingGPT, MarketSenseAI, QuantAgent, FinMem, an orphan entry);
  wrong or invented keys replaced (Trillion Dollar Words ACL 2023, FINSABER = Li et al. KDD 2026, López de Prado
  2018 for walk-forward, "The Memorization Problem" arXiv:2504.14765, KalshiBench arXiv:2512.16030, FOMC In Silico
  = Kazinnik & Sinclair 2025 GWU WP 2025-005).
- Contradiction fixed: the 500 synthetic trajectories (not the 117 episode interpretations) were the fine-tuning
  data; derivation of the 13,571 data points documented.
- Added: data-leakage paragraphs (§4.2.1, §5.3), calibration-transfer caveat, justification of the three schools,
  ensemble-theory mechanism linking school diversity to calibration (hedged; to be tested), statistical rigour on
  the ablation plan (Diebold–Mariano, Ledoit–Wolf Sharpe test, 95 % bootstrap CIs), a Risk, Governance and
  Auditability section.

## Framing guidance (from the Confirmation preparation)

- Frame contributions as methodological, not architectural: the three-school structure is one instance of a
  transferable principle (as MoE papers are cited for routing, not for one implementation).
- SFT rather than RL was a de-risking choice; RL is the natural PhD-stage follow-on (for Prof. Huang).
- For Prof. Jiang, state the statistical limitations explicitly: covariance estimation with 35 dimensions and 141
  samples, heuristic scoring weights, calibration sample size, missing-data assumptions.
- A panel member asked why fine-tuning rather than chain-of-thought prompting: the thesis must answer it (exp01).
- Known methodological risks: data leakage (model training cut-offs overlap the backtest period; split results by
  cut-off) and sparse regime-conditional calibration data.
- Closest prior work: "History Rhymes" (Khanna et al., Nov 2025), macro-conditioned analogy retrieval for daily
  single-stock forecasting. Differences: discrete macro episodes vs continuous daily snapshots; covariance-aware
  Mahalanobis distance vs plain concatenation; downstream multi-school causal reasoning vs a logistic classifier.
  Other comparators: TradingAgents (five roles at single-stock level), FOMC In Silico (personas of Fed members
  voting on the funds rate), EconAgent (bottom-up household simulation, not event analysis).
- Writing style requested by Futian: professional, deferential to Prof. Zhang, no templated AI phrasing (no
  em-dash constructions).

## Earlier claude.ai chats in the Project (reference only; open them on claude.ai)

| Date | Topic |
|---|---|
| 2026-10-29 | Graduation requirements: RPg Handbook §10, DSAI programme 5.7/5.9 (summarised in THESIS_DESIGN §1) — https://claude.ai/chat/272fafe7-34de-4dc9-8759-1e130d5f2a3d |
| 2026-07-30 | Where the experimental data lives (answer: not in the Project; see `data/README.md`) |
| 2026-06-22 | Confirmation presentation strategy, 36-slide deck, panel preparation, History Rhymes |
| 2026-06-17 | 25-slide deck, 5-minute deck, PhD motivation and three-year plan |
| 2026-06-16 | 30-slide HTML deck (`macro_mosaic_confirmation.html`) |
| 2026-05-25 – 06-01 | Confirmation report revisions, citation fixes, final compile, Chinese translation, emails |
| 2026-04-18 | MPhil timeline, Confirmation deadline, first summary of the report |
| 2026-04-08 – 04-10 | Bella's PQE survey (`survey_pqe/`) and the research-direction brainstorm that led to Macro-MOSAIC |
