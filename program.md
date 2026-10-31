# program.md — auto-research protocol for Macro-MOSAIC

You are running experiments for an MPhil thesis (Macro-MOSAIC, PolyU DSAI). You work in a loop: pick the next
task by priority and due date, change one thing, run it on **dev / calibration data only**, log it, decide,
repeat. A human owns registration, freezing, final runs and every thesis sentence.

Read first, in this order: `CLAUDE.md` → `research/THESIS_DESIGN.md` (priorities, dates, rules for AI use) →
this file → `research/backlog.md` → the end of `research/LOG.md` (to resume where the last session stopped).

## Rules (non-negotiable)

1. **Held-out data is not yours.** Never run `--split test`, `mosaic freeze`, `--final`, `--allow-rerun`, or
   `mosaic judge --split test`; they need a human at a terminal and will refuse you. For exp02–exp05 the held-out
   parts are defined in their drafts (exp02: test queries ≥ 2005; exp03/04: the 2026 test window; exp05:
   everything): build data for them, but compute **no score of any system or baseline** on them.
2. **Do not touch the measurement.** No edits to `prereg/`, `locks/`, `experiments/results.tsv`,
   `src/mosaic/metrics.py`, `src/mosaic/judge.py`, `configs/lexicons.toml`, `configs/judge.toml`, or the arm
   A/C/D prompts (`configs/prompts/*.system.txt`, `user_template.txt`). If one looks wrong, write it under
   "For the human" in `research/LOG.md` and stop that line of work. Drafts in `research/prereg_drafts/` you may
   edit (counts, field names, mapping rules); log every edit.
3. **Parser fixes** (`src/mosaic/parse.py`) only with a failing test first and a before/after rescore in the log.
4. **Budgets.** exp01 arm B: ≤ 12 configurations on dev, ≤ 40 events each. GPU: stop after 6 hours of
   generation per session. Claude Opus 5.5 calls (arm D smoke test, judge pilot, trigger-only descriptions) share
   the human's subscription with your own session: arm D `--limit 3` once; judge `--split dev --limit 5` once;
   descriptions ≤ 150 calls in total. Arm T (GPT-4o, paid) is never run by you.
5. **Log everything** in `research/LOG.md` before the next run (format below). Never delete or rewrite entries.
6. **AI-use ledger.** Every substantive thing you produce (code module, data transformation, analysis, edited
   draft) gets one line in `research/AI_USE_LEDGER.md`: date, what, files, how a human can verify it.
7. **No thesis prose.** You write code, data cards, result tables and factual summaries. You do not draft thesis
   chapters, abstracts or the GSB/2B synopsis (PolyU GenAI rules; see THESIS_DESIGN §6).
8. **Commit** after each logged iteration (`git add -A && git commit -m "<exp>: <change> (<run_id>)"`). Never push.
9. **No leakage.** Do not open `data/events/test.jsonl`. Inputs to any forecast must be point-in-time (published
   on or before the forecast time). No news or text written after the forecast time.
10. **Data etiquette.** When fetching from Kalshi, Polymarket, FRED/ALFRED: use pmpol's User-Agent, stop on HTTP
    429 (no retries), keep raw data under `data/` (never committed; Kalshi terms forbid redistribution).
11. **Honest reporting.** Improvements smaller than run-to-run noise (rerun once with another seed) are
    "no change". Report failures and format errors as prominently as successes.
12. **Commands.** Run things as `python -m mosaic <command>` or `python -m pytest`; add new steps as `mosaic`
    subcommands with tests. Other shell commands may be denied by the session's permission settings.
13. **Deadlines.** If a due date in `research/backlog.md` is at risk, say so under "For the human" with the reason.

## Task 0 — parity (first; blocks Task 1)

1. `mosaic doctor --arms A,B,C` and fix what you can. Report what only the human can provide.
2. If `data/legacy/{base,sft}_{school}.jsonl` exist, `mosaic rescore` all six and compare with Confirmation
   Table 4.3 (consistency base / SFT: K 0.368 / 0.338, A 0.146 / 0.319, M 0.230 / 0.528; anti-signal hits
   K 0.44 / 0.00, A 1.21 / 0.59, M 0.88 / 0.02; `[Output]` presence K 59 / 97 %, A 81 / 93 %, M 51 / 99 %).
   Within ±0.01 consistency and ±2 pp presence = passed. Otherwise diagnose (count mode, scope, parser, lists) in
   `scratch/` and recommend the fix to the human; do not edit the lexicon yourself.
3. Without legacy generations: run A and C on dev (`--limit 20`) and check the Confirmation's ordering holds
   (C fewer anti-signal hits and higher `[Output]` presence than A for every school). Log "qualitative parity".

## Task 1 — exp01 dev loop (strongest prompting baseline), then hand-off

Find the best arm B configuration on dev within budget, optimising mean consistency while keeping `[Output]`
presence ≥ arm A's. Run A and C once on the same dev events first, then iterate on B:

```
mosaic run --exp exp01 --arms B --split dev --limit 40 --set arms.B.k=3 --set arms.B.strategy=category --note "B: k=3 category"
mosaic report --exp exp01 --split dev
```

Order: k ∈ {1, 3, 5} random → best k with category → max_chars → extra guidance (`--set
arms.B.extra_dir=configs/prompts/b_extra`, one `.txt` per school written from textbook definitions, never from
events). Then: arm D smoke test (`--arms D --limit 3`), judge pilot (`python -m mosaic judge --exp exp01 --split dev
--limit 5`, check the parse rate). Hand-off: `research/exp01_dev_summary.md` (every configuration, chosen one,
noise estimate, Task 0 status, judge parse rate, worries), chosen values in `[arms.B]`, commit, and log
`READY FOR HUMAN: scripts/final.sh exp01`.

## Task 2 — exp03 data build (P0; CPU + network; may run while waiting for the human)

Follow `research/prereg_drafts/exp03_market_forecasting.md`.

1. `python -m mosaic vendor` extracts the pmpol archive to `vendor/` (read its `EXPORT_NOTES.md`; cite it as team code).
   Extend its ground-truth fetchers to Kalshi Economics/Financials and Polymarket economy markets with daily prices
   before close. Add tests for every new parser (offline fixtures).
2. Build the question set: events → ordered scenario sets (bins) using pmpol's proposition grids; list exclusions.
3. Build point-in-time contexts (ALFRED vintages as of each forecast time) for the 35 indicators.
4. Write `research/exp03_data_card.md`: counts per series × window, exclusions and reasons, coverage of contexts.
5. Implement the exp03 runner and scorers in `src/mosaic/` with offline tests (fake backend). Pilot format
   compliance of adapters on ≤ 10 **calibration-window** events; record parse rates. Nothing on the test window.
6. Hand-off: log `READY FOR HUMAN: register exp03` with the open questions.

## Task 3 — exp02 retrieval (P1; CPU)

Needs `data/episodes/` from the human. Build point-in-time states and trigger-only descriptions (≤ 150 Opus calls;
the human spot-checks 20), implement the expanding-window protocol from the draft with tests, tune on dev queries
(trigger date < 2005) only, write `research/exp02_dev_summary.md`, log `READY FOR HUMAN: register exp02`.

## Task 4 — exp04 coherence (P1; only after exp03 is registered)

Implement the checks from the draft with tests; run on the calibration window only; summary + hand-off.

## Log entry format (`research/LOG.md`)

```
### <UTC time> — <exp>: <short title>
- hypothesis: …
- change: … (files / --set)
- command: …
- run_ids: …
- result: … (numbers, vs best so far, vs noise)
- decision: keep | discard | inconclusive
- next: …
```
