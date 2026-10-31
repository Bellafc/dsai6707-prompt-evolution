# Research backlog

Priorities and dates follow `research/THESIS_DESIGN.md`. AUTO = the agent may work on it without asking;
HUMAN = needs a person (assets, registration, freeze, final run, or a decision).

| ID | Experiment | RQ / chapter | Priority | Due | Owner now | Status | Depends on |
|---|---|---|---|---|---|---|---|
| exp01 | Fine-tuning vs prompting (A/B/C, D = Opus 5.5, T = GPT-4o optional) + judge validation | RQ1 / Ch. 4 | **P0** | final 11-29, ratings 12-13 | AUTO (Task 0–1 on dev) | registered (+2 amendments) | assets, original prompts/lexicons |
| exp03 | Multi-school forecasts on resolved macro markets (2025 calibration, 2026 test) | RQ3 / Ch. 6 | **P0** | registered 11-25, final 12-20 | AUTO (Task 2 data build) | draft | pmpol ground truth + ALFRED; adapters |
| exp02 | Analogy retrieval, expanding window, point-in-time states | RQ2 / Ch. 5 | P1 | 01-31 | AUTO (Task 3, dev queries) | draft | episode DB export; human spot-check of trigger-only descriptions |
| exp04 | Coherence (CPI MoM↔YoY, FOMC↔year-end) and projection | RQ3 / Ch. 6 | P1 | 02-07 | AUTO after exp03 registration | draft | exp03 question set |
| exp05 | Prospective live forecasting incl. Opus 5.5 | RQ3 / Ch. 6 | P2 (go/no-go 12-01) | 03-31 | HUMAN | draft | exp03 pipeline |
| stage4 | Allocation demo on 2025–26 events | Ch. 7 | P2 (decision D2) | — | HUMAN | not planned | D2 |
| bench | EconCausal / EconLogicQA | Ch. 4 | P2 | — | — | dropped unless time remains | — |

Related-work anchors: Paleka et al. (ICLR 2025, 2026), ForecastBench (ICLR 2025), Halawi et al. (NeurIPS 2024),
Le (2026), Gebele & Matthes (2026), Shi & Zhai (2026), Predd et al. (2009), Hsieh et al. (2023),
Khanna et al. "History Rhymes" (2025).
