# CLAUDE.md — DSAI6707 course project (branch `course/dsai6707-ec-project`)

This folder is a **course project**, not thesis work. It reuses the Macro-MOSAIC harness read-only.
Read `README.md` (teacher requirements, in Traditional Chinese) and `PLAN.md` (design, 10-hour schedule) first.

## Hard rules

1. **Never touch thesis held-out or registered material**: `data/events/test.jsonl`, `data/events/dev.jsonl`,
   exp03 questions (calibration or test window), `prereg/`, `locks/`, `experiments/results.tsv`, `adapters/`.
   The project uses **synthetic events only** (`mosaic.divergence` / `mosaic.spikes` generators with a new seed, ≠ 11).
2. **Do not edit `src/mosaic/`, `configs/` or `tests/`.** Import from `mosaic` instead; all new code lives in
   `courses/dsai6707/code/`. Project results must never be used to set thesis arms (e.g. exp01 arm B).
3. Code, comments and commits in English. Notes for the human may be in Traditional Chinese (台灣華語).
4. Everything in `code/` must run offline with a fake backend: `python -m pytest -q courses/dsai6707/code` before
   each commit; the repo's own `python -m pytest -q` must still pass.
5. No secrets in text (see `ops/ORCHESTRATOR.md` rule 1). GPU spending only after the human confirms GPU class
   and hour limit (`PLAN.md` §6).
6. Log AI-generated artefacts in `courses/dsai6707/AI_USE.md` (the course and PolyU GenAI guide require
   disclosure). The human writes/edits the final report prose.
7. Raw outputs go to `courses/dsai6707/results/` (JSONL + CSV, committed; they are deliverable 3).
