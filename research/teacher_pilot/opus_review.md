# Opus 5.5 review of the teacher pilot (prompt version 1)

Three reviewers (Claude Opus 5.5, one per school) scored every kept pilot trajectory (qwen3.8-max teacher, 59 items)
on five 1–5 criteria. Per-item scores and flags: `opus_review/review_<school>.json`. Evaluation only; Claude is not
the teacher (amendment 4 Change 5).

| School | n | school fidelity | causal coherence | event responsiveness | output consistency | factual hygiene | verdict |
|---|---|---|---|---|---|---|---|
| Keynesian | 19 | 3.79 | 3.42 | 3.21 | 3.47 | 3.74 | train with changes |
| Austrian | 20 | 4.10 | 3.45 | 3.25 | 2.90 | 3.75 | train with changes |
| Monetarist | 20 | 4.50 | 3.85 | 3.70 | 3.60 | 3.40 | train with changes |

Automatic checks (orchestrator): all 708 backdrop values echoed correctly in the second [Observe]; mean pairwise
8-gram overlap within a school 0.7–1.2 % (no copying); but equities SHORT in 52/59 and gold LONG in 56/59.

## Problems all three reviewers found

1. **Default signals.** Equities SHORT, gold LONG, credit SHORT in almost every item, also for good news (payroll beat,
   tariff truce, peace deal, oil-reserve release). The student would learn a permanent bear.
2. **Positive shocks forced into the school's crisis story**; Keynesian items always conclude "demand shortfall", even
   at 3.4–4 % unemployment and 4–6 % inflation (overheating).
3. **Checklist reasoning.** The prompt listed every school concept as must-use, so trajectories stuff them all in.
4. **Backdrop numbers used before get_macro_data** (16/19, ~17/20); the tool call looks pointless. (The student's user
   prompt does carry the backdrop, so this is a tool-honesty issue, not invented data.)
5. **Non-US events read with a US backdrop** without saying so; one wrong-sign dollar call (dovish BoE → DXY SHORT).
6. **Templated scenarios** (always four, 0.45/0.30/0.15/0.10 in 9/19 Keynesian items, recycled labels).
7. **Vague or wrong analogs** ("various episodes", 2015–16 oil called geopolitical, 1920–21 mischaracterised).
8. **Implausible or contradictory backdrops** (event says the curve inverted, backdrop spread positive).
9. **Format drift** (tool arguments as JSON / text / "query:", "SHORT (3)" without "conviction", meta phrases).

## Changes in prompt version 2 (`src/mosaic/teacher.py`, `configs/teacher/templates.toml`)

| Problem | Change |
|---|---|
| 1, 2 | per school: how it diagnoses (Keynesian output-gap check incl. overheating and supply shocks; Austrian adds/removes intervention; Monetarist money vs real growth) and the cases it reads as good news; signals must name a scenario or chain step, no default direction, NEUTRAL when no reason; batch report warns when one direction exceeds 70 % for an asset |
| 3 | concepts offered as a toolbox ("pick what fits"), one or two mechanisms per event |
| 4 | backdrop numbers may not be cited before get_macro_data; rejected if ≥ 2 distinctive backdrop values appear earlier |
| 5 | backdrop labelled US/global; foreign events must say how they reach US/global assets |
| 6 | 2–4 event-specific scenarios with growth/inflation direction |
| 7 | first [Observe] must name ≥ 2 dated episodes (country or institution, year before 2025) |
| 8 | backdrop made consistent (curve from the 2y and 10y, unemployment and VIX against growth, M2 near inflation, HY spread from VIX); event-vs-backdrop contradictions must be stated |
| 9 | tool arguments must be one JSON line; every signal `asset: DIR (conviction N) - reason`; meta phrases and mentions of other schools rejected |

# Review of pilot v2 (prompt version 2, same rubric)

Same reviewer setup and rubric on the 51 kept v2 trajectories (`opus_review/review_v2_<school>.json`). Reviewer
instances differ between rounds, so small differences are within judge noise; the direction is consistent.

| School | n | school fidelity | causal coherence | event responsiveness | output consistency | factual hygiene |
|---|---|---|---|---|---|---|
| Keynesian | 15 | 3.79 → **4.13** | 3.42 → **3.80** | 3.21 → **4.00** | 3.47 → **3.67** | 3.74 → **4.87** |
| Austrian | 19 | 4.10 → **4.42** | 3.45 → **4.05** | 3.25 → **3.58** | 2.90 → **3.53** | 3.75 → **4.58** |
| Monetarist | 17 | 4.50 → **4.59** | 3.85 → **3.88** | 3.70 → **4.18** | 3.60 → **4.06** | 3.40 → **4.53** |

Overall mean 3.61 → 4.12. All three verdicts still "train with changes".

Fixed by v2: good news gets risk-on signals (trade truce, SPR release, easing); overheating diagnosed; analogs real,
specific and pre-2025 (15/15, 19/19, 17/17); clean JSON tool calls; no backdrop numbers before get_macro_data (one
exception); event-vs-backdrop contradictions and foreign channels stated.

Remaining, for prompt version 4:
1. **The teacher writes the tool results.** Nothing in `src/` executes query_episode_db or get_macro_data, so the
   student learns to produce [Observe] text from memory in varying formats. Options: real tools (episode DB, ALFRED
   contexts) with [Observe] injected and masked from the loss, or one fixed schema and a stated "self-simulated
   tools" limitation. Human decision (affects exp01 and exp03).
2. **Signals follow S1 only** (86/90, 97/102 reasons cite S1) and ignore 45–55 % of the probability mass; use
   probability-weighted signals and cut conviction when other scenarios point the other way.
3. **Templated probabilities** (S1 always 0.45–0.55; 0.55/0.25/0.20 in 8/17 M, 0.45 in 14/19 A).
4. **Undefined asset referents and horizon** (local vs US assets); define US/global benchmarks and a horizon.
5. **Prompt echoes** the student would learn ("the event gives no bp, pp or share of GDP" in 12–15 of each school,
   "newest information", "a single backdrop cannot show a trend").
6. **Backdrop skew** (unemployment above 4.5 % in ~72 % of draws pushes Keynesian items to "support, bonds LONG");
   Monetarist money growth compared with one quarter's GDP instead of trend growth; no lagged series.
7. **Residual defaults**: Keynesian bonds LONG 12/15 (never SHORT), gold LONG from the Austrian "favours hard assets",
   gold never SHORT for any school.
8. **School toolkits** to sharpen: Keynesian real rate and zero bound, Austrian real policy rate, Monetarist trend
   growth, velocity and the natural rate (now absent).

# Review of pilot v4 (prompt version 4: real tools, [Proof] block)

Three Opus 5.5 reviewers (evaluation only), the v1/v2 rubric plus a sixth criterion, **grounding** (uses the returned
episodes and indicators correctly, cites nothing else, proof steps match the reasoning). 57 kept conversations
(`opus_review/review_v4_<school>.json`; data `data/trajectories/pilot-v4/agent/`, not versioned). Verdict of all
three: train "with changes".

| School | n | school fidelity | causal coherence | event responsiveness | output consistency | factual hygiene | grounding |
|---|---|---|---|---|---|---|---|
| Keynesian | 20 | 4.30 | 3.80 | 3.95 | 3.40 | 4.30 | 3.50 |
| Austrian | 18 | 4.78 | 3.83 | 4.06 | 3.39 | 4.22 | 3.67 |
| Monetarist | 19 | 4.79 | 3.79 | 3.89 | 3.58 | 4.11 | 3.47 |
| all, v4 | 57 | 4.61 | 3.81 | 3.96 | 3.46 | 4.21 | 3.54 |
| all, v2 (n-weighted) | 51 | 4.39 | 3.92 | 3.90 | 3.75 | 4.65 | — |

Mean of the five shared criteria: v1 3.61, v2 4.12, v4 4.01. The v4 reviewers could check every number against the
tool results, so factual hygiene and output consistency were judged more strictly than in v2; different reviewer
instances add noise.

**Fixed by the real tools**: no backdrop value before get_macro_data, no episode id or value the tools did not return
(0/57), every real-rate computation correct; analogs are weighed (fit and misfit) instead of listed; signal reasons
weigh the scenario distribution (S1-only reasons fell from ~90% to under 10%); the v2 echoes ("no bp", "newest
information") and the 0.55/0.25/0.20 tuple are gone; good news gets risk-on calls.

**Problems found by all three reviewers** (the prompt-v5 work list):
1. A new prompt echo: step 3's "say so in one sentence and weigh the event more" gives "weigh the event" (or "the
   event dominates") in 52/57 by a regex count, mostly on manufactured tensions; "this/the school" in 44/57;
   school-profile sentences quoted near-verbatim.
2. Pre-event backdrop values read as the event's effects (the curve as "the market's verdict" on the event).
3. Templated calibration: S1 at 0.40–0.50 in most items, repeated probability tuples (0.45/0.30/0.25), "Confidence:
   moderate" in 57/57.
4. Directional defaults remain in part: credit SHORT 44/57, Keynesian bonds LONG 16/20, Austrian gold LONG 15/18;
   reviewers judged about a third of them defaults. New failure mode: a signal takes the school's direction from a
   minority scenario with reduced conviction instead of NEUTRAL; some reasons cite scenarios whose tags point the
   other way; some assets are signalled without their indicator having been requested.
5. One stock mechanism per school (Austrian: policy rate minus CPI in 18/18; Monetarist: "relative-price shock,
   inflation only if money accommodates" in 19/19; Keynesian: the paradox of thrift in 11/20, often misused).
6. The US backdrop applied to foreign events (US real rate to judge the BoE or RBA).
7. Claims beyond the tool text bring errors (SVB, Malaysia, Plaza, 2019 money growth); the stand-in table lacks
   money-substitute runs, RRR cuts, mortgage relief and an SNB floor.
8. Backdrop generator: implausible mixes (low CPI with high oil), negative GDP in about half the draws, no lagged
   series (lags only asserted), event-stated levels not reflected (inflation "2.5pp above target" vs CPI 1.6%).
9. Proofs longer than the prompt's 4–7 lines in 16/57 (the validator accepted up to 10); an L5 naming a tail.

The Task A spike (`research/agent_spike.md`) found the prompted Qwen3-8B at 0/30 on the same contract (tool calls
valid, format contract failed), so the format the teacher sets is what agent SFT must teach.

# Review of pilot v5 (prompt version 5, items version 4)

Same rubric and setup (three Opus 5.5 reviewers, evaluation only; `opus_review/review_v5_<school>.json`). The three
reviewers were cut off by the subscription's spend limit after writing their files; the files are complete (items and
summaries). Verdict of all three: "with changes".

| School | n | school fidelity | causal coherence | event responsiveness | output consistency | factual hygiene | grounding |
|---|---|---|---|---|---|---|---|
| Keynesian | 17 | 4.18 | 3.65 | 4.47 | 3.59 | 4.29 | 3.82 |
| Austrian | 19 | 4.79 | 3.74 | 4.32 | 3.74 | 4.21 | 3.84 |
| Monetarist | 19 | 4.53 | 3.89 | 4.11 | 3.79 | 3.84 | 3.84 |
| all, v5 | 55 | 4.51 | 3.76 | 4.29 | 3.71 | 4.11 | 3.84 |
| all, v4 | 57 | 4.61 | 3.81 | 3.96 | 3.46 | 4.21 | 3.54 |

Mean of the five shared criteria: v1 3.61, v2 4.12, v4 4.01, v5 4.08; grounding 3.54 → 3.84.

**Fixed since v4** (all three reviewers): the echoes ("weigh the event" 0/55, "this/the school" 0/55); no pre-event
value read as the event's effect; foreign events no longer judged with US data and the missing foreign variables
named; gold and credit defaults broken (Austrian gold LONG 15/18 → 9/19, credit SHORT 15/18 → 9/19; Keynesian credit
SHORT 15/20 → 9/17); calls on minority scenarios mostly NEUTRAL or conviction 1; Monetarist velocity computed from
nominal GDP minus M2 in 19/19, the backdrop oil level no longer a live shock.

**Remaining** (the prompt-v7 work list):
1. Calibration still templated (v5: modal at 0.35-0.55 in most items, "Confidence: moderate" 52/55, repeated
   tuples). v6 added the evidence label; the v6 pilot labels 21/26 "mixed".
2. Rule narration replaces the old echoes: "nothing contradicts the data / the event states no level", pre-event
   disclaimers, "the oil level is not a live shock", annualisation remarks without a monthly figure, "not a liquidity
   trap" at policy rates of 2.5-5.5% (Keynesian 13/17), "velocity is not stable".
3. New stock diagnoses: Austrian real rate against the 4-quarter average and "necessary liquidation" without a boom
   (15/19); Monetarist 4-quarter average used as trend growth, moving the money benchmark with the cycle.
4. Signals: the "data-driven, conviction 2 or less" clause used as a licence for backdrop-only calls; reasons citing
   scenarios whose tags point the other way; scenarios with identical tags (Keynesian 7/17).
5. Backdrop: inflation drawn independently of the gap (low unemployment with low core PCE in 6/17 Keynesian items),
   which feeds easing calls.
6. Claims about money growth in past episodes from memory (several wrong); the stand-in table carries no money context.
