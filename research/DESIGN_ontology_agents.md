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

## 2. Proposed research questions: one design, three angles (wording is the author's)

Overarching question:

> Can language-model agents reason through explicitly contested economic theories in a way that is theory-driven
> inside the model, auditable in what they say, and calibrated in how sure they are?

The three interpretability angles of §4b become the three RQs. All three read the same factorial design (§4a) and
the same agents, so the chapters remain one study rather than three.

| RQ | Angle | Question | Evidence | Ch. |
|---|---|---|---|---|
| RQ1 | Inside the model: what it computes | Does fine-tuning instil a contested economic framework beyond the best prompting baseline, and does it change what the model computes (the framework's concepts) or only what it writes (its vocabulary)? | exp01 (registered, unchanged: A/B/C, D; keyword metrics, validated judge, two human raters); exp06 (SAE, S-H1 to S-H3); exp01b (Qwen3.5-27B, D7); agent arms C-agent and C-agent+RFT (fidelity and SAE, exploratory) | 4 |
| RQ2 | What the agent says: auditable reasoning | When framework agents must fetch point-in-time facts (L1) and historical base rates (L2) through real tools and justify each forecast with a layered proof, is their reasoning auditable and faithful: are the proofs valid and traceable to L0–L4, do the conclusions follow the evidence when it changes, and are the mechanisms a proof claims active inside the model? | exp02 (the L2 tool: macro-state analogies vs narrative and naive similarity, protocol unchanged); exp07 (new: proof validity and grounding, tool-call validity, counterfactual tool results, proof-step typing by a decision model, SAE proof faithfulness; dev and pre-2025 events only) | 5 |
| RQ3 | How sure: calibrated forecasts | Do probability forecasts pooled across contested frameworks beat single frameworks and other sources of ensemble diversity (personas, multiple models, repeated sampling) on real post-cutoff macro outcomes; are they calibrated and coherent; and do their uncertainty signals (disagreement among frameworks, analytic confidence) predict error? | exp03 (H1–H7 as drafted, H8 diversity sources, the agent arms of §4a as forecasters); exp04 (coherence); exp05 (live, optional; decision head) | 6 |

What changes against THESIS_DESIGN §2:
- **RQ1** keeps its evidence. "Concepts or vocabulary" moves from a sub-question to the core, so exp06 becomes half
  of the answer (D10 matters more). exp01 and its amendments are untouched; amendment 2's "discussion of RQ1" still
  applies.
- **RQ2** changes most: the analogy question (exp02) becomes one part, the quality of the L2 tool, inside a wider
  question about grounded and faithful reasoning. Chapter 5 becomes "Grounded, auditable agents".
- **RQ3** keeps H1–H7 and gains the diversity-source comparison (H8); disagreement and analytic confidence move from
  secondary hypotheses into the question.
- Contributions 1–5 stay, regrouped: 2 → RQ1; 3 and 5 → RQ2; 4 → RQ3; 1 serves all three.
- Decision models (D8) are instruments for all three angles, not a fourth question: judge (RQ1), proof-step typer
  (RQ2), decision head (RQ3, exp05 only).
- The examiner question "reasoning or vocabulary?" is answered by three independent instruments (§4b).

Priorities if time runs short: exp01 and the exp03 primary hypothesis stay P0; exp06, exp02, exp07 and RFT are P1;
RL is P2. If the agent arms are not trained by the exp03 final run, exp03 runs without them (the registration names
the cut-off date) and RQ2 still rests on exp07 and exp02.

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
| exp02 | its retriever becomes the `query_episode_db` tool; its result validates the L2 evidence (RQ2) | unchanged protocol |
| exp03 (draft, register by 11-25) | main stage of the new design: tool-using agents per framework; **H8 diversity sources**: trained schools vs prompted schools vs quantitative L3 frameworks vs personas vs multi-model (Qwen, DeepSeek, GLM) vs sampling, equal ensemble size; H6/H7 as drafted | before 11-25 |
| exp04 | coherence constraints come from the proposition ontology (L0) | unchanged |
| exp07 (new, RQ2) | grounded-agent faithfulness: proof validity and grounding, tool-call validity, counterfactual tool results (one L1 value or L2 episode changed), proof-step typing, SAE proof faithfulness; needs no outcomes, so dev and pre-2025 events only | draft, register before it runs (P1) |

## 4a. Fine-tuning vs the ontology agent, and how to train the agent

The author asked to compare the fine-tuned schools with the ontology agent, and whether agents can be trained.
Both fit one factorial design: **how the framework is instilled** (prompting vs training) × **how the agent works**
(single pass vs ontology agent with real tools and a proof).

| | Single pass, self-simulated tools (Confirmation format) | Ontology agent: real L0/L1/L2 tools, L5 proof |
|---|---|---|
| **Prompted** | exp01 arm A (registered) | **A-agent**: base Qwen3-8B + framework prompt + tools |
| **Fine-tuned (SFT)** | exp01 arm C (registered) | **C-agent**: LoRA trained on multi-turn tool trajectories (teacher v4), tool results masked from the loss |
| **Agent training beyond SFT** | — | **C-agent+RFT** (main extension) and **C-agent+RL** (stretch) |

What each contrast answers: C vs A = does fine-tuning instil the framework (exp01 H1, unchanged); A-agent vs A and
C-agent vs C = do real tools and proofs help; C-agent vs A-agent = does fine-tuning still matter once the agent has
tools; the interaction = are they substitutes or complements.

Each RQ (§2) reads this table from one angle: RQ1 the rows (how the framework is instilled, seen from inside the
model), RQ2 the columns (what real tools and proofs change in what the agent says), RQ3 every cell as a forecaster.

Methods for training the agent (established literature: ReAct, Yao et al. 2023; FireAct, Chen et al. 2023;
AgentTuning, Zeng et al. 2023; STaR, Zelikman et al. 2022; RL with verifiable rewards and GRPO, DeepSeek 2024–25;
tool-using RL such as Search-R1 and ToolRL, 2025; outcome-based RL for forecasting, Turtel et al. 2025):

| Method | How | Data and reward | Cost | Status in this design |
|---|---|---|---|---|
| **Agent SFT** | imitate teacher trajectories in the multi-turn tool format; loss on the agent's own turns only | 1,500 teacher trajectories (v4) | same as the school SFT (minutes per adapter on one GPU) | core |
| **Rejection-sampling fine-tuning (RFT / STaR)** | the SFT agent samples k trajectories per event; keep those that pass verifiable checks; fine-tune again (1–2 rounds) | verifiable, no human or Claude labels: proof valid and grounded (`Proof.check`), tool calls well-formed, scenario probabilities coherent with L0 grids, and on historical episodes the realised asset-reaction direction (episode DB, pre-2025, so no test leakage) | a few GPU-hours of sampling + one more SFT | **recommended extension** |
| **RL with verifiable rewards (GRPO, multi-turn with tools)** | the agent acts in the tool environment; reward = proof validity + format + proper scoring rule (Brier/RPS) on resolved historical outcomes | same rewards; outcome data is the binding limit (141 episodes; exp03's 58 calibration questions are reserved for calibration) | 1–2 days of engineering (TRL or verl multi-turn) + 10–30 H100-hours | stretch; full outcome-RL stays PhD work (THESIS_DESIGN §4a) |

Rules: rewards and filters are rule-based or come from realised outcomes, never from a Claude model's judgement
(the same reason Claude is not the teacher); the exp03 test window is never used for training, filtering or
reward; every round is logged with its data and seed.

## 4b. Interpretability: three views that check each other

The ontology gives every claim a type (layer, source, time). That makes three kinds of interpretability measurable
on the same objects, and their agreement is itself a result.

| View | Question | Instrument | Ontology hook |
|---|---|---|---|
| **What the agent says** (epistemic) | Can a reader audit why it forecasts what it forecasts? | the L5 proof: layered steps with refs, competing readings, analytic confidence (pmpol `Proof`, `confidence.assess`) | proof validity (`Proof.check`, grounded) and exp03 H7 (low confidence ⇒ larger error) |
| **How sure, in a calibrated, typed way** (decision models: Jev, open Vega/Kev) | Can each judgement be read off with a usable probability instead of sampled text? | System One decision models answer typed questions (`choice`, `score`, `noul`) with per-option probabilities in one forward pass | (a) second, open, reproducible **judge** of school fidelity (exp01 secondary outcome, decision D8), validated against Opus and the two human raters; (b) **proof-step typer**: which layer each step belongs to and which L3 entry field it invokes (drivers / frictions / policy / signals), so ungrounded or mistyped steps are caught automatically; (c) **decision head** over scenario bins (exp05 only) |
| **What the model computes** (mechanistic, SAE, exp06) | Does the model use the school's concepts, or only its words? | Qwen-Scope SAEs on Qwen3-8B (spike S3: reader passes at layers 18 and 27; chat model at 27; layer 9 fails CE) | feature cards map features to the fields of each L3 entry; **new: proof faithfulness**, i.e. when a step claims an L3 mechanism (e.g. the fiscal multiplier), are that field's features active on those tokens? Internal contamination = other frameworks' features on the same tokens |

Two tests only real tools make possible:
- **Counterfactual tool results.** Re-run an agent with one L1 value or one L2 episode changed. A grounded agent
  changes the dependent steps and the forecast; one that ignores its tools does not. This is a behavioural
  faithfulness test of the proof, and SAE activations show where in the model the change enters.
- **Proof vs inside vs judge.** For each trajectory: proof says framework X; SAE shows X's features (or not); the
  decision-model judge and Opus score fidelity. Agreement across the three answers the examiner question "is it
  reasoning or vocabulary?" with three independent instruments instead of one.

Rules carried over from pmpol: decision-model outputs and machine feature labels are L5 proposals with probability,
model and commit; they never approve a fact. Vendor calibration claims are measured (ECE, reliability), not quoted.
Leakage: Vega (Qwen3.5-0.8B base) and Kev-27B (Qwen3.8) know 2025–26, so they read text (judge, typer) but never
forecast the exp03 test window; forecasting with them is exp05 (prospective) only.

Cost: SAE work is exp06 as planned (Task 5, after the adapters) plus the faithfulness analysis on tagged proof
steps; decision models run on a pod (ollajev, Vega 0.8B/4B on CPU or GPU, Kev-27B on one 80 GB card), Jev hosted
as an upper-bound reference only. Gold labels come from exp01's two human raters (judge) and ~300 hand-typed proof
steps (typer); Kev fine-tuning (~1,000 labels) is optional.

## 5. Cost and risks

- **Effort**: tool layer and multi-turn format ≈ 2–3 days of agent work; teacher v4 + pilot + review ≈ 1 day;
  exp03 arms are prompt/API runs on 149 questions (token plan; no extra GPU); exp07 is inference only (agents on a
  pod, a few GPU-hours) plus the SAE pass of exp06.
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
5. D8: decision models as measurement tools (judge, proof-step typer; decision head in exp05)?
6. D10: exp06 Parts I + II, plus the proof-faithfulness analysis and the counterfactual-tool test?
7. Agent training depth: SFT only, SFT + RFT (recommended), or SFT + RFT + RL (stretch)?
8. Adopt the three RQs of §2 (wording to be finalised by the author)? Then THESIS_DESIGN §2–3 and §7, README,
   DESIGN_DOC_zh, the backlog and the RQ labels of the drafts are updated; the title follows (D2).
