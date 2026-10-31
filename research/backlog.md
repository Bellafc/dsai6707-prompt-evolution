# Research backlog

AUTO = the agent may start it when exp01 is waiting on the human. HUMAN = needs a decision or assets first.

| # | Experiment | Thesis role | Status | Needs |
|---|---|---|---|---|
| exp01 | Fine-tuning vs prompting (A/B/C/D) | answers the Confirmation panel question; Stage 2 justification | **active** | original prompts + lexicons (Task 0), dev/test events, trajectories, adapters |
| exp02 | Stage 1 retrieval: semantic vs Mahalanobis, α sweep, leave-one-out over the 141 episodes; real-time (ALFRED) vs revised state vectors | Stage 1 | HUMAN | episode database export (`data/episodes/`) |
| exp03 | Calibration data: extend `pmpol` ground truth from politics to Kalshi Economics/Financials and Polymarket economy markets; reliability, slope b per venue and horizon | Stage 3 calibration set; extends Le (2026) to economics | AUTO (code + public read-only APIs; follow pmpol's User-Agent and no-retry-on-429 rules) | network on the pod |
| exp04 | Coherence of school forecasts on ladder markets (CPI, Fed path): ℓ1 distance to the coherent set, before/after projection (Predd et al. 2009; Shi & Zhai 2026) | Stage 3 aggregation theory | HUMAN (depends on exp03 question set) | exp03 |
| exp05 | Prospective logging v0: Stage 2 + equal-weight aggregation forecasts on live macro markets, weekly, pre-registered | leakage-free evaluation | HUMAN (registration must be signed off) | exp03, prereg |

Related-work anchors for each item are in the thesis notes (Paleka et al. ICLR 2025/2026, ForecastBench,
Halawi et al. 2024, Le 2026, Gebele & Matthes 2026, Shi & Zhai 2026).
