# DSAI6707 project submission: index

Project: Multi-objective evolution of a prompt set for three competing economic-school LLM agents (NSGA-II with LLM-guided mutation).
Student: Alexander JIANG, Futian (25084392R) | Course: DSAI6707 Advanced Computational Intelligence

| Required deliverable (README §2 / Project PDF §7) | Path in this archive |
|---|---|
| 1. Project report (PDF) | `1_report/report.pdf` (source `1_report/report.md`, bibliography `1_report/references.bib`) |
| 2. Source code and README (environment, dependencies, data preparation, execution, evaluation) | `2_code/README.md`, `2_code/evo_prompt/`, `2_code/tests/` |
| 3. Experimental data and results (raw, logs, result files) | `3_results/runs/` (per-run `gen_log.csv`, `evaluations.jsonl`, `front.jsonl`, `final.json`), `3_results/cache/llm_cache.jsonl` (every model response), `3_results/logs/matrix.log` (run log and ledger), `3_results/summary_table.md`, `3_results/summary.csv` (one row per run), `3_results/summary_search.csv`, `3_results/heldout_per_event.csv`, `3_results/heldout_tests.csv`, `3_results/heldout_tests_protocol.csv` (protocol family), `3_results/addendum_a_search.csv` (Q1 to Q5), `3_results/haiku/` (Claude Haiku 5.5 replication: runs, caches, logs, tables, figures), `3_results/heldout_sensitivity.csv`, `3_results/smoke/` (API smoke test) |
| 4. Supplementary (configs, prompts, figures, model outputs) | `3_results/best_prompts/` (knee prompt sets), `3_results/figures/` (three figures), `4_supplementary/PROTOCOL.md` and `PROTOCOL_ADDENDUM_A.md` to `_D.md` (analysis protocol and addenda; deviations in report §4.8), `4_supplementary/AI_USE.md` (AI use log), `1_report/slides_outline.md` (6-minute talk) |

## Reproducing the reported numbers (no new model calls)
1. `cd 2_code && python -m evo_prompt.analyze` rewrites the tables in `3_results/` from the runs and the cache.
2. `python -m evo_prompt.figures` rewrites `3_results/figures/`.
3. `python -m pytest -q 2_code` runs the 27 offline tests. For the Haiku replication add `--profile haiku` to steps 1 and 2.

API use: qwen 3,709 calls on a prepaid Token Plan subscription (about USD 27.31 estimated at assumed list prices; not a charge); Claude Haiku 5.5 9,412 calls (USD 5.28 at list prices). Token counts are measured.

## Known gap
`configs/` (lexicons, school templates, framework positions) is not inside this archive. These files are in the repository at `configs/lexicons.toml`, `configs/teacher/templates.toml` and `configs/frameworks.toml`; they are inputs to `mosaic.metrics` and `mosaic.divergence` and are not modified.
