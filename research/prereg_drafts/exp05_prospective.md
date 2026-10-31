# DRAFT pre-registration — exp05: Prospective (live) forecasting

Status: **DRAFT, OPTIONAL (P2)**. Go/no-go by the human on **2026-12-01**: only worth starting if the exp03
pipeline runs end to end by then (needs ≥ 3 months of live questions before writing starts).

## Question

Do the exp03 conclusions hold on questions that resolve after the forecasts are made, and how far is a frontier
model (Claude Opus 5.5, arm D) from the Qwen3-8B school pool when neither can have seen the answers?

## Protocol

- Freeze the exp03 pipeline (v0 = configuration chosen on the exp03 calibration window) at registration.
- Every Monday: forecast every open in-universe Kalshi macro event that closes 3–21 days later, with the
  point-in-time information set of exp03. Systems: pool-eq, pool-cal, base, D (Opus 5.5 via the CLI), market
  snapshot at the same minute. Optional, prompted only (no adapters): the newest open models that fit one GPU
  (Qwen3.8-27B, Gemma 4 31B), as "latest open model" references, and the Qwen3.5-27B pool if exp01b is go.
- Each week's forecasts are committed to git (timestamped, hashed) **before** the events resolve.
- Window: registration date → 2027-03-31. Scoring after the window closes, with the exp03 metrics.

## Hypotheses

Same direction as exp03 H1–H2, reported **descriptively** (expected 30–60 events; low power). D vs pool-eq and
D vs market are descriptive.
