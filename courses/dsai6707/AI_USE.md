# AI use log (DSAI6707 project)

Disclosure of AI assistance, as required by the course and the PolyU GenAI guide. Each row names what the AI produced
and what the student checked. "Pending" means the check has not been done yet and must be done before submission.

| Date | Tool | What it produced | Human check |
|---|---|---|---|
| 2026-11-01 | Claude (claude.ai session) | Course-material sync, requirements checklist (`README.md`), reuse inventory (`REUSE.md`), research plan (`PLAN.md`) | to review |
| 2026-11-01 | Claude Code (cloud session) | `code/evo_prompt/` (genome, evaluator, operators, constrained NSGA-II, GA, random search, hypervolume, cached runner, analysis, figures) and `code/tests/` (20 offline tests) | Pending: line-by-line review of the operators and the hypervolume code. Tests pass (`python -m pytest -q courses/dsai6707/code`). |
| 2026-11-01 | Claude sub-agents, four runs | Literature search and verification by theme (LLM-driven EC, multi-objective and quality-diversity, diversity and persona fidelity, model merging and self-evolving LMs); BibTeX drafts | Pending: check each entry in `report/references.bib` against its publisher page. Entries flagged in the sub-agent reports as resting on search snippets (for example the Wu2025evolutionary and Liu2026systematic volume and DOI, the Qiu2026es venue, the Li2026evolm author list and the Akiba2025merging volume and pages) need confirmation. |
| 2026-11-01 | Claude Code (cloud session) | Experiment orchestration: API smoke test, full matrix run (2,743 model calls, estimated USD 20.20 at assumed prices), analysis tables and tests, figures | Pending: confirm the price assumption against the provider's price sheet; the raw outputs are in `results/`. |
| 2026-11-01 | Claude Code (cloud session) | Draft of `report/report.md` (English) and `report/report.pdf`, `report/slides_outline.md`, `code/README.md` | Pending: the student writes or edits the final prose, checks every number against `results/`, and checks every citation. |
| 2026-11-01 | Claude Code (cloud session) | Interpretation notes: the knee rule, the statistical choices (exact sign-flip over held-out events, Holm correction), the limitations section | Pending: the student decides whether to keep the interpretation. The protocol (`code/PROTOCOL.md`) was fixed before the full matrix ran. |
