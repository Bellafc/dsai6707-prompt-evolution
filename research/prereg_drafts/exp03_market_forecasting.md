# DRAFT pre-registration — exp03: Multi-school forecasts on resolved macro prediction markets

Status: **DRAFT** (not registered). The agent may refine this file during the data build (counts, field names,
mapping rules). It becomes binding when the human copies it to `prereg/exp03_market_forecasting.md` and commits,
**before any forecast on the test window is scored**. Thesis chapter 6 (RQ3). Priority **P0**.

## Question

Do school-specialised agents produce useful probabilistic forecasts of macroeconomic releases, and does pooling
heterogeneous schools beat the best single school? (The Confirmation's "−Multi-school" ablation, now testable
on real outcomes without look-ahead.)

## Why prediction markets, and why 2025–2026

Each Kalshi macro market is a ladder of mutually exclusive outcomes with a published resolution source, i.e. a
ground truth plus a crowd benchmark. Qwen2.5 was released in September 2024 and the school adapters were trained
on template events with randomised macro states (no instance-level information), so events resolving on or after
**2025-01-01** are outside every local model's training data. Frontier API models are *not* evaluated here
(their training data covers 2025–2026); they appear only in the prospective exp05.

## Knowledge layers (pmpol ontology, L0–L5)

Every input and output has a layer, and forecasts must trace back to L0–L4 (pmpol rule for L5 inferences):

| Layer | Here | Role |
|---|---|---|
| L0 rules | release definitions, publication grids (CPI 0.1 pp, FOMC 25 bp), market resolution rules | builds the scenario sets; coherence constraints (exp04) |
| L1 point-in-time facts | the 35 indicators as published on or before t (ALFRED vintages) | model input; never revised data |
| L2 base rates | analog episodes (exp02), historical distribution of the series, venue calibration slopes | model input (analogues); baselines |
| L3 contested frameworks | the three schools (`kb/L3/schools.yaml`) | one agent per school; cited, not adopted; shown side by side |
| L4 market observations | Kalshi prices at t | benchmark only; **never** a model input |
| L5 inferences | each school's distribution, the pools | must carry a proof |

**Proof per forecast** (pmpol `Proof` format, `vendor/pmpol-academic/src/pmpol/proof.py`): steps citing the L0 rule,
the L1 series and vintage dates given, the L2 analogues (episode ids, similarity), the L3 school entry, each
school's distribution, the pool, plus **analytic confidence** (ICD 203, separate from probability): the weakest
link among L1 completeness, analog strength, parse validity of every school and L0 rule clarity — **not**
disagreement, which is tested separately. The plain-language summary is generated from the proof only.

## Question universe (built by the agent, Task 2 in program.md)

- Kalshi settled markets in the Economics / Financials categories (extend `pmpol.ground_truth.kalshi.CATEGORIES`;
  keep pmpol's User-Agent and no-retry-on-429 rules), Polymarket closed economy markets as a secondary source.
- Event = (series, reference period or meeting). Series in scope: US CPI MoM (headline, core), US CPI YoY,
  US unemployment rate, FOMC target-range decision, US real GDP advance estimate (QoQ SAAR), and the foreign
  central-bank decisions that pmpol's proposition ontology already reads (step grids in
  `pmpol/propositions/indicators.py`).
- Each event's contracts are mapped to one ordered set of mutually exclusive bins (the **scenario set**).
  Events whose contracts do not partition the outcome space after mapping are excluded and listed.
- Resolution window 2025-01-01 → last settled date at build time. **Calibration window**: 2025-01-01 → 2025-12-31.
  **Test window**: 2026-01-01 → end. Counts per series and window are reported in `research/exp03_data_card.md`
  before registration (counts only; no forecasts scored).

## Information set at forecast time t (= 7 days before market close; 1 day as a secondary horizon)

1. Event description: series, reference period, release date, the scenario set (bins, in canonical wording).
2. Point-in-time macro context: the 35 indicators **as published on or before t** (ALFRED vintages; pmpol's
   `realtime.py` pattern), plus the target series' latest published values.
3. (Ablation −RAG only) the top-3 analog episodes from the episode database with trigger date before t, chosen by
   the exp02 retrieval method frozen at that time.
No news, no market prices, no text written after t.

## Systems

| System | Description |
|---|---|
| base | Qwen2.5-7B-Instruct, school-neutral system prompt (arm-A style) |
| K, A, M | each school adapter (arm C) with its school system prompt |
| K′, A′, M′ | base model with each school's system prompt, no adapter (arm-A style) |
| pool-eq | equal-weight linear pool of K, A, M |
| pool-prompt | equal-weight linear pool of K′, A′, M′ |
| pool-skill | weights ∝ exp(−λ·mean RPS) estimated on the calibration window (λ chosen there) |
| pool-cal | pool-eq after temperature scaling fitted on the calibration window |
| uniform | equal probability on every bin |
| history | empirical distribution of the series' historical changes, point-in-time (pmpol `baseline.py`) |
| market | Kalshi prices at t (daily close), normalised over bins — benchmark, not a competitor to beat |

Generation: the scenario set is passed as the [Output] scenario list; 3 samples per (event, system) at
T = 0.7 / top-p 0.9; per sample the probabilities are parsed per bin and renormalised if their sum is in
[0.8, 1.2], otherwise the sample is invalid; the system's forecast is the mean of valid samples; an event with no
valid sample gets the uniform forecast and counts as a format failure (reported per system).

## Metrics

Primary: **ranked probability score (RPS)** per event (bins are ordered). Secondary: log score (ε = 0.01 floor),
Brier score on the binary contracts, ECE on binary contracts (10 bins), format-failure rate.

## Hypotheses (test window, paired over events, event-level bootstrap and sign-flip permutation)

- **H1 (primary)**: RPS(pool-eq) < RPS(best single school), the best school chosen on the calibration window.
- **H2**: RPS(pool-eq) < RPS(base): school fine-tuning does not destroy forecasting value.
- **H3**: ECE(pool-cal) < ECE(pool-eq).
- **H4**: in logit(y) = a + b₁·logit(p_market) + b₂·logit(p_pool-eq) over binary contracts (standard errors
  clustered by event), b₂ > 0, i.e. the pool carries information the market price does not.
- **H5 (links RQ1 and RQ3)**: RPS(pool-eq) < RPS(pool-prompt): fine-tuned schools forecast better than prompted
  schools, not only sound more school-specific.
- **H6 (L3 disagreement as a signal)**: across test events, inter-school disagreement (mean pairwise
  Jensen–Shannon divergence of K, A, M) correlates positively with the pool's RPS (Spearman > 0): disagreement
  among contested frameworks flags harder events.
- **H7 (analytic confidence is informative)**: mean RPS is higher for events graded low than for events graded
  high analytic confidence (one-sided permutation test).
Holm correction across H1–H7. Market vs pool is reported descriptively (we expect the market to win).

## Ablations (secondary, P1)

−RAG vs +RAG analogues; horizon 7d vs 1d; per-series breakdown; school weights by series family.

## Threats and controls

Leakage (cutoff policy; point-in-time inputs; no news) · format failure of adapters on market-defined scenarios
(measured; uniform fallback penalises it) · dependence within events (event-level resampling) · small number of
events per series (report per-series counts and CIs; pool series for the primary test).
