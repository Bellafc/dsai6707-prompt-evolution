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
