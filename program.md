# program.md — auto-research protocol for Macro-MOSAIC

You are running experiments for an MPhil thesis (Macro-MOSAIC, PolyU DSAI). You work in a loop: pick the next
hypothesis, change one thing, run it on the **dev** split, log it, decide, repeat. A human owns the irreversible
steps. Read `CLAUDE.md` first, then this file, then `research/LOG.md` (to pick up where the last session stopped).

## Rules (non-negotiable)

1. **The test split is not yours.** Never run `--split test`, `mosaic freeze`, `--final` or `--allow-rerun`; they
   need a human at a terminal and will refuse you anyway. When dev work is finished, prepare the hand-off (below)
   and stop.
2. **Do not touch the measurement.** No edits to `prereg/`, `locks/`, `experiments/results.tsv`,
   `src/mosaic/metrics.py`, `configs/lexicons.toml`, or the arm A/C/D prompts (`configs/prompts/*.system.txt`,
   `user_template.txt`). If you believe one is wrong, write it in `research/LOG.md` under "For the human" and stop
   that line of work.
3. **Parser fixes** (`src/mosaic/parse.py`) are allowed only with a failing test first in `tests/` and a
   before/after rescore in the log. A parser change applies to every arm equally.
4. **Budgets.** Arm B: at most 12 distinct configurations on dev, ≤ 40 events each (prereg). GPU: stop after
   6 hours of generation in one session. Arm D (API): only `--limit 5` smoke runs on dev, total ≤ 2 USD.
5. **Log everything.** Every run command, its `run_id`, the result and your decision go into `research/LOG.md`
   before the next run. Never delete or rewrite earlier log entries; append corrections.
6. **Commit** after each logged iteration: `git add -A && git commit -m "exp01: <what changed> (<run_id>)"`.
   Never push; the human pushes.
7. **No look-ahead, no leakage.** Do not copy test events into dev or prompts; do not open `data/events/test.jsonl`.
8. **Honest reporting.** A dev improvement smaller than the run-to-run noise (rerun the same config once with a
   different `--set sampling.seed=` to estimate it) is "no change", not a win.

## Task 0 — parity (do this first; blocks everything else)

The harness must reproduce the Confirmation before its numbers mean anything.

1. `mosaic doctor --arms A,B,C` and fix what you can (installs, paths). Report what only the human can provide.
2. If `data/legacy/` has the Confirmation's saved generations (`{base,sft}_{school}.jsonl`), run
   `mosaic rescore --file … --school …` for all six and compare with Table 4.3 (base / SFT consistency:
   K 0.368 / 0.338, A 0.146 / 0.319, M 0.230 / 0.528; anti-signal hits K 0.44 / 0.00, A 1.21 / 0.59,
   M 0.88 / 0.02; `[Output]` presence K 59 / 97 %, A 81 / 93 %, M 51 / 99 %).
   - All within ±0.01 (consistency) and ±2 pp (presence): parity passed, log it.
   - Otherwise: diagnose (count mode, scope, parser, keyword lists) and write the exact discrepancy for the
     human. Lexicons and prompts are the human's to restore. To test a hypothesis about `[options]`, copy the
     lexicon file to `scratch/lexicons_try.toml`, score with a throwaway script, and recommend the setting that
     reproduces the table in "For the human"; do not edit `configs/lexicons.toml` yourself.
3. If there are no legacy generations, run arms A and C on dev (`--limit 20`) and check the ordering matches the
   Confirmation (C has fewer anti-signal hits and higher `[Output]` presence than A for every school). Log that
   parity is "qualitative only".

## Task 1 — exp01 dev loop (strongest prompting baseline)

Goal: find the best arm B configuration on dev within the budget, so the final comparison is against a real
baseline, not a straw man. Optimise the prereg's primary metric (mean consistency) **and** keep
`[Output]` presence ≥ arm A's; report contamination alongside.

Iteration template:

```
mosaic run --exp exp01 --arms B --split dev --limit 40 --set arms.B.k=3 --set arms.B.strategy=category \
  --note "B: k=3 category"
mosaic status -n 5
```

Run arm A and C once on the same dev events first (they are fixed; the cache makes later report calls free), then
iterate on B. Suggested order: k ∈ {1, 3, 5} with random → best k with category → max_chars → extra guidance
(`--set arms.B.extra_dir=configs/prompts/b_extra`, one `.txt` per school with a short description of the school's
core mechanisms; write it from the school's textbook definition, not from test events). Use
`mosaic report --exp exp01 --split dev` to see paired comparisons.

Stop when the budget is spent or two consecutive configurations do not beat the best by more than the noise.

## Hand-off (end of Task 1)

Write `research/exp01_dev_summary.md`: every B configuration tried (run_ids, metrics), the chosen one, the noise
estimate, Task 0 status, and anything that worries you. Write the chosen configuration into `configs/exp01.toml`
(`[arms.B]`), commit, and add to `research/LOG.md`:

> READY FOR HUMAN: run `scripts/final.sh exp01`

Then stop, or continue with an AUTO item from `research/backlog.md`.

## Log entry format (`research/LOG.md`)

```
### <UTC time> — <short title>
- hypothesis: …
- change: … (files / --set)
- command: …
- run_ids: …
- result: … (numbers, vs best so far, vs noise)
- decision: keep | discard | inconclusive
- next: …
```
