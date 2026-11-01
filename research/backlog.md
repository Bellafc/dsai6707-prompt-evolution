# Research backlog

Priorities and dates follow `research/THESIS_DESIGN.md`. AUTO = the agent may work on it without asking;
HUMAN = needs a person (assets, registration, freeze, final run, or a decision).

| ID | Experiment | RQ / chapter | Priority | Due | Owner now | Status | Depends on |
|---|---|---|---|---|---|---|---|
| spikes | Task S: Qwen3-8B serving, `mosaic train`, SAE reader check, Qwen3.5-27B LoRA (dummy data only) | infra | **P0** | 11-02 | AUTO | ready | a GPU pod (80 GB for S4) |
| train | Qwen3-8B school adapters (amendment 4 recipe), seed-episode audit | RQ1 / Ch. 4 | **P0** | 11-12 | AUTO when this row says `go` | wait (D7, D11) | trajectories, amendment 4 registered |
| exp01 | Fine-tuning vs prompting on Qwen3-8B (A/B/C, D = Opus 5.5, T optional) + judge validation | RQ1 / Ch. 4 | **P0** | final 12-06, ratings 12-20 | AUTO (Task 0–1 on dev) | registered (+3 amendments; amendment 4 draft) | adapters, original prompts/lexicons, events |
| exp01-D | Arm D (Opus 5.5) pre-generation on test, generation only (amendment 3) | RQ1 / Ch. 4 | **P0** | as soon as prompts + test events exist (no GPU) | HUMAN (`mosaic pregen`) | ready to run | original prompts, 96 test events, `claude` login |
| exp06 | SAE instrument (Part I) and mechanism (Part II) on exp01's arms; Qwen-Scope SAEs | RQ1 / Ch. 4 (proof faithfulness: RQ2) | **P1** (D10) | instrument 12-04, Part II 01-17 | AUTO (Task 5 on dev/probes) | draft | adapters; register with the exp01 freeze |
| exp03 | Multi-school forecasts on resolved macro markets (calibration 2025-05 → 12, test 2026), with L0–L5 proofs and analytic confidence (H6–H7) and diversity sources (H8: personas, multi-model, sampling, prompted frameworks) | RQ3 / Ch. 6 | **P0** | registered 11-25, final 12-20 | AUTO (Task 2 data build) | draft (H8 and agent arms to add) | pmpol ground truth + ALFRED + proof/confidence modules; adapters; design note decisions 1–2 |
| tools | L0–L2 tool layer (`get_rules`, `get_macro_data`, `query_episode_db`) and the multi-turn agent format with harness-injected tool results | RQ2–3 / Ch. 3, 5 | **P0** | before the exp03 registration (11-25) | AUTO | proposed | design note decision 3; episode DB (vetted episode table until then) |
| exp07 | Grounded-agent faithfulness: proof validity and grounding, tool-call validity, counterfactual tool results, proof-step typing, SAE proof faithfulness | RQ2 / Ch. 5 | P1 | register before it runs | AUTO (dev, pre-2025 events) | to draft | tools; agents; exp06 SAE reader; D8 for the typer |
| exp01b | Qwen3.5-27B school LoRA vs prompting + exp06 replication (27B SAE) | RQ1 / Ch. 4 | P1 (D7) | spike 11-02, go/no-go 11-20, final 01-24 | AUTO spike → HUMAN | draft | 80 GB GPU; LoRA on Gated DeltaNet layers |
| kb-L3 | School entries as L3 facts with verbatim quotes; second-person review | Ch. 2–4 | P1 | before exp01 freeze | HUMAN (D9) | proposed | sources |
| exp02 | Analogy retrieval, expanding window, point-in-time states; the agents' L2 tool (`query_episode_db`) | RQ2 / Ch. 5 | P1 | 01-31 | AUTO (Task 3, dev queries) | draft | episode DB export; human spot-check of trigger-only descriptions |
| exp04 | Coherence (CPI MoM↔YoY, FOMC↔year-end) and projection | RQ3 / Ch. 6 | P1 | 02-07 | AUTO after exp03 registration | draft | exp03 question set |
| exp05 | Prospective live forecasting incl. Opus 5.5; newest open models as prompted references | RQ3 / Ch. 6 | P2 (go/no-go 12-01) | 03-31 | HUMAN | draft | exp03 pipeline |
| repro | Qwen2.5-7B reproduction arms A7/C7 vs Confirmation Table 4.3 (amendment 4, Change 4) | Ch. 4 | P2 (D11) | with exp01 final | AUTO training → HUMAN | idea | original trajectories |
| gemma4 | Gemma 4 31B cross-family check of H1 (no SAE) | Ch. 4 | P2 | — | — | idea | 4-bit LoRA or > 80 GB GPU |
| stage4 | Allocation demo on 2025–26 events | Ch. 7 | P2 (decision D2) | — | HUMAN | not planned | D2 |
| judge2 | Kev-27B as a second, open judge (score type) next to Opus | Ch. 4 | P2 (D8) | — | AUTO if D8 = yes | idea | 80 GB GPU |
| rl | GRPO/ReMax with Brier/RPS reward on exp03 data | Ch. 7 / PhD | future | — | — | future work | far more resolved questions |
| bench | EconCausal / EconLogicQA | Ch. 4 | P2 | — | — | dropped unless time remains | — |

Related-work anchors: Paleka et al. (ICLR 2025, 2026), ForecastBench (ICLR 2025), Halawi et al. (NeurIPS 2024),
Le (2026), Gebele & Matthes (2026), Shi & Zhai (2026), Predd et al. (2009), Hsieh et al. (2023),
Khanna et al. "History Rhymes" (2025). Interpretability (exp06): Qwen-Scope (2026), Gao et al. (2024),
Chen et al. "Persona vectors" (2025), Minder et al. (ICLR 2026), Kissane et al. (2024), Kantamneni et al.
(ICML 2025), Wu et al. "AxBench" (ICML 2025), Paulo et al. (ICML 2025), Paulo & Belrose (2025).
