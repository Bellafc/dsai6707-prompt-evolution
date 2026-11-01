# What the project reuses from Macro-MOSAIC (read-only imports)

Everything below is imported, never edited. Cite it in the report as "the author's thesis harness (Macro-MOSAIC)";
`pmpol` code, if used, is team code and must be credited as such.

| Need in the project | Reuse | Where | Notes |
|---|---|---|---|
| Synthetic macro events (task instances) | `mosaic.teacher.make_items(n, seed)` → `item.event` (id, text, category, `macro_context`) | `src/mosaic/teacher.py` | Seeds already used by the thesis: 0 (teacher training items), 7 (agent spike), 11 (disagreement matrix). **Project: seed 23 = search set, seed 29 = held-out evaluation set.** |
| School definitions = initial population genes | `mosaic.divergence.profiles()` (label, diagnosis, concepts, signals, good_news) | `configs/teacher/templates.toml`, `configs/frameworks.toml` | Three schools + three candidate frameworks (NK, New Classical, Post-Keynesian) |
| Prompt → messages (output format with Think / Causal chain / Scenarios / Signals) | `mosaic.divergence.messages(prof, event)` | `src/mosaic/divergence.py` | The baseline prompt = this function unchanged |
| Parse a response (signals per asset, scenario probabilities) | `mosaic.divergence.parse(text)`; `mosaic.teacher.normalize` | `src/mosaic/divergence.py` | Returns `None` when the format breaks → validity rate is a metric |
| Pairwise disagreement between two frameworks | `mosaic.divergence.distance(a, b)` (signal disagreement, Kuncheva–Whitaker share, macro gap) | same | Fitness objective 2 |
| School fidelity (keyword consistency) | `mosaic.metrics.lexicons()`, `consistency(text, lex)` (must / strong / anti hits) | `src/mosaic/metrics.py`, `configs/lexicons.toml` | Fitness objective 1. Lexicon marked PROVISIONAL in the thesis; fine for a course project, say so |
| Model calls | `mosaic.backends.VLLMBackend` (Qwen3-8B on a pod), `OpenAIBackend` (any OpenAI-compatible API, with a USD budget), `FakeBackend` (offline tests), on-disk `Cache` | `src/mosaic/backends.py` | `Request` / `generate(reqs)` batch interface; cache makes reruns free |
| Statistics | `mosaic.stats.paired` (bootstrap CI + permutation p), `holm` | `src/mosaic/stats.py` | Method comparisons over seeds |
| Batch API runner | `scripts/teacher_api.py` (requests.jsonl → results.jsonl) | `scripts/` | The disagreement matrix (`research/divergence/`) ran 240 requests on `qwen3.8-max` this way |
| GPU pods | `python -m mosaic pod create/list/stop` + `scripts/pod_bootstrap.sh`, `setup/runpod_setup.sh` (vLLM + Qwen3-8B) | `src/mosaic/runpod.py`, `ops/ORCHESTRATOR.md` | Rules: one pod, human confirms GPU class and hours, no secrets in text |
| Evidence for the motivation | Disagreement-matrix results: the three schools disagree ≈ 2× the run-to-run noise; New Keynesian collapses onto Keynesian (diversity collapse) | `research/divergence/RESULTS.md` | Motivates "diversity as an objective" |
| Related work (non-EC part) | bib files: ensemble diversity, prompting/personas, agents, calibration | `research/thesis_drafts/references/*.bib` | EC papers (2024–26) still have to be added: Promptbreeder, EvoPrompt, LLM-as-ES, OPRO, quality-diversity prompting, etc. |

Not reused (out of scope or thesis-only): exp01 trajectories and adapters, exp03 market questions, the Opus judge,
SAE code, `prereg/`, `locks/`.
