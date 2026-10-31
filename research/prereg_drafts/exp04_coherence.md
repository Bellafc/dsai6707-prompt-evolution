# DRAFT pre-registration — exp04: Coherence of school forecasts and coherent aggregation

Status: **DRAFT**. Thesis chapter 6 (theory section of Stage 3). Priority **P1**. Depends on exp03's question set.

## Question

Are the schools' probability forecasts logically coherent across related questions, and does projecting
incoherent forecasts onto the coherent set improve them?

## Why this is principled

A set of probabilities is coherent iff it lies in the convex hull of admissible outcome vectors (de Finetti);
incoherent prices admit arbitrage, and the guaranteed arbitrage equals the distance to that set (Shi & Zhai 2026).
Projecting an incoherent forecast onto the coherent set lowers its Brier score in every possible world
(Predd et al. 2009, IEEE Trans. Inf. Theory). Paleka et al. (ICLR 2025) used such checks for LLM forecasters on
generic questions; here they are grounded in arithmetic identities of official statistics.

## Coherence checks

1. **CPI MoM ↔ YoY** (same reference month): with index levels for m−1 and m−12 known at t, each YoY bin maps to
   an interval of MoM values (exact up to published rounding). The MoM forecast therefore implies a YoY
   distribution. Incoherence = total-variation distance between the stated and the implied YoY distribution.
2. **FOMC meeting ↔ year-end rate** (optional, if exp03 has both ladders for the same date): the meeting decision
   distributions and the year-end ladder must be consistent given the meetings remaining.
Each item is asked in a separate prompt (no cross-question context), as in exp03.

## Systems and measures

K, A, M, pool-eq, base and the **market itself** (Kalshi's MoM and YoY ladders at t can be incoherent too).
Measures: incoherence (TV distance); Brier and RPS before vs after Euclidean projection onto the coherent joint.

## Hypotheses (test window of exp03)

- **H1**: pool-eq is less incoherent than the mean single school.
- **H2**: projection improves RPS (not guaranteed by the theorem, unlike Brier, which is reported as a check).
- Descriptive: model incoherence vs market incoherence.
