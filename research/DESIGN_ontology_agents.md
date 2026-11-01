# DRAFT (2026-11-01): ontology-grounded multi-framework agents

Status: proposal for the author and Prof. Zhang. Nothing here is adopted until the author decides;
`research/THESIS_DESIGN.md` stays the source of truth. Prepared by the orchestrator (AI-use ledger, planning
assistance) after the author asked to widen the thesis scope and to build on pmpol's L0–L5 ontology.

## 1. Why

Two findings push in the same direction:

1. **Scope.** "Can an 8B model reason like a Keynesian, an Austrian or a Monetarist?" is a narrow question. The
   Confirmation framing guidance already says the three schools are one instance of a transferable principle.
2. **The tools are not real.** Two Opus reviews of the teacher pilots (`research/teacher_pilot/opus_review.md`)
   found that nothing in `src/` executes `query_episode_db` or `get_macro_data`: the teacher writes the
   observations and the student learns to invent them. This was already true of the Confirmation design.

pmpol's ontology (`vendor/pmpol-academic/docs/ARCHITECTURE.md` §0, `PROPOSITION_ONTOLOGY.md`, `src/pmpol/proof.py`,
`confidence.py`, `kb/`) gives both a principled fix and the wider claim: every input is a typed, sourced,
time-stamped fact of a knowledge layer, contested theories are L3 frameworks kept side by side, and every inference
is an L5 proof that must trace back to L0–L4.

## 2. Proposed thesis question (wording is the author's)

> Do agents that reason through explicitly contested theoretical frameworks (L3), over point-in-time facts (L1) and
> base rates (L2) fetched by real tools, produce analyses that are more auditable and forecasts that are better
> calibrated, and is theoretical diversity a better source of ensemble diversity than personas, models or sampling?

The three trained schools stay the deep case; the ontology makes them one instance of a general architecture.

## 3. Architecture

```
L0 rules ─────────► get_rules(event)        release grids, FOMC step sizes, resolution rules (pmpol propositions)
L1 facts (as of t) ► get_macro_data(names)  ALFRED vintages known at t (exp03_context, pmpol known_at)
L2 base rates ─────► query_episode_db(q)    analog episodes (Stage 1 / exp02), historical distributions
L3 frameworks ─────► one agent per framework: 3 trained schools (LoRA) + prompted frameworks (below)
                         │  each agent writes an L5 proof: steps tagged with layer, ref (fact id, series@vintage,
                         │  episode id) and as_of; scenarios; signals; competing readings
L4 markets ────────► benchmark only, never an input
L5 ─────────────────► per-framework distributions → pool (L5 summary, never replaces the per-framework views)
                       proof checked by pmpol Proof.check() + grounded; analytic confidence = weakest link
```

| pmpol piece | Use here |
|---|---|
| Knowledge layers L0–L5 | the type system of every tool result, step and output |
| Proposition ontology (variable ∈ set, resolution conditions) | exp03 question set (already used for bins), exp04 coherence relations |
| `Proof` (layered steps, refs, as_of, alternatives, PROV export) | the agent's output format and the training target |
| `confidence.assess` (weakest link, ICD 203 wording) | analytic confidence per forecast (exp03 H7) |
| `kb/` (reviewed facts, Admiralty grades, two-person rule) | L3 school entries (`kb/L3/schools.yaml`), L2 base rates, L0 release rules |
| Competing hypotheses (Heuer, `Proof.alt`) | other frameworks' readings shown with each proof (exp03 H6) |
| `kb/L3/macro_frameworks.yaml` (Sahm rule, NY Fed probit, OECD CLI phases, investment clock, Kondratiev datings) | extra L3 frameworks of a different kind: quantitative rules next to narrative schools |

## 4. What changes per experiment

| Exp | Change | Registration |
|---|---|---|
| exp01 (registered) | unchanged: single-pass arms A/B/C/D on the 96 events, for comparability with the Confirmation; the self-simulated tool calls become a stated limitation | none |
| exp06 | unchanged; feature cards still map SAE features to the L3 entries | with exp01 freeze |
| Training data (D11) | teacher prompt v4: multi-turn trajectories, tool results injected by the harness (L1 from the backdrop, L2 from the episode table), masked from the loss; Output as a layered proof | amendment 4 (training data) |
| exp02 | its retriever becomes the `query_episode_db` tool | unchanged protocol |
| exp03 (draft, register by 11-25) | main stage of the new design: tool-using agents per framework; H-new **diversity sources**: trained schools vs prompted schools vs quantitative L3 frameworks vs personas vs multi-model (Qwen, DeepSeek, GLM) vs sampling, equal ensemble size; H6/H7 as drafted | before 11-25 |
| exp04 | coherence constraints come from the proposition ontology (L0) | unchanged |

## 5. Cost and risks

- **Effort**: tool layer and multi-turn format ≈ 2–3 days of agent work; teacher v4 + pilot + review ≈ 1 day;
  exp03 arms are prompt/API runs on 149 questions (token plan; no extra GPU).
- **Needs from the human**: the episode database (141 episodes, 117 narratives) for a real `query_episode_db`;
  until then the L2 tool uses a vetted episode table (named, dated, pre-2025), labelled as such.
- **Risks**: (i) more moving parts before the 12-06 exp01 freeze (mitigated: exp01 untouched); (ii) the student may
  call tools badly at inference (measured: tool-call validity is a reported outcome); (iii) persona and multi-model
  arms may match the schools, which is a result, not a failure (the question is open by design).

## 6. Decisions for the author

1. Adopt the ontology-grounded agent as the architecture of exp03 (and the thesis framing)?
2. Which extra L3 frameworks: prompted schools (which), pmpol's quantitative frameworks, or both?
3. Real tools for the teacher data now (v4), with the episode table as a stand-in until the episode DB is uploaded?
4. exp01: keep single-pass (recommended) or amend to the agent loop?
