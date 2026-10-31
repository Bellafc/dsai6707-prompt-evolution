# AI-use ledger

Source for the thesis AI-use statement (PolyU Student Guide on the Use of GenAI: AI-generated material must be
identified; the student is accountable). One line per substantive contribution by an AI tool. Human decisions,
research questions, interpretations and all thesis prose are the author's and are not listed here.

| Date | Tool | Contribution | Files | How verified |
|---|---|---|---|---|
| 2026-10-30 | Claude (Opus 5.5, Claude Code) | Experiment harness: data contract, backends, parser, Confirmation metrics re-implemented from Sec. 4.2.3, statistics, CLI, locks | `src/mosaic/*`, `tests/*` | 20 offline tests; parity check against Confirmation Table 4.3 (Task 0) pending |
| 2026-10-30 | Claude | Drafted exp01 pre-registration and amendment 1 (arm D = Opus 5.5) for the author's review | `prereg/exp01_*` | Author review before first real run |
| 2026-10-31 | Claude | LLM-judge module and rubric (provisional school definitions), amendment 2 draft | `src/mosaic/judge.py`, `configs/judge.toml`, `prereg/exp01_amendment_2.md` | Author checks rubric and definitions before freeze; human-rater validation built in |
| 2026-10-31 | Claude | Planning assistance: thesis design, timeline, exp02–05 draft protocols, defence question matrix | `research/THESIS_DESIGN.md`, `research/prereg_drafts/*` | Author and supervisor review (decisions D1–D6) |
| 2026-10-31 | Claude | Research summary on frontier options (Qwen3.8-27B, Jev/Vega/Kev decision models, outcome-based RL) and the Claude Consumer Terms check; design of the L0–L5 ontology integration | `research/THESIS_DESIGN.md` §2a, §4a; `research/prereg_drafts/exp01b_*`, exp03 H6–H7 | Author review; sources listed in the design doc |
| 2026-10-31 | Claude | `mosaic pregen` (generation-only, human-gated) and amendment 3 draft; L3 school entries drafted without quotes | `src/mosaic/run.py`, `prereg/exp01_amendment_3.md`, `kb/L3/schools.yaml` | Tests; quotes and second-person review pending (D9) |
