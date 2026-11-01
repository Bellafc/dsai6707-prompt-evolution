# DRAFT pre-registration — exp07: Grounded agents, proof validity and faithfulness (RQ2)

Status: **DRAFT, P1** (design note decisions 3, 5, 6, 7). Thesis chapter 5 (RQ2). Binding once the human copies it
to `prereg/` **before the confirmatory run**. It needs no outcomes, so it uses only template events and historical
episodes before 2025; nothing here touches the exp01 test events or the exp03 test window. Drafted by the
orchestrator (AI-use ledger); the author decides scope, systems and thresholds.

## Questions

1. **Validity.** When framework agents fetch L1 facts and L2 episodes through real tools, are their L5 proofs valid,
   typed by layer and grounded in what the tools returned?
2. **Behavioural faithfulness.** Does the forecast move when a fact the proof relies on is changed, more than when a
   fact it does not rely on is changed? A proof written after the fact would not show this asymmetry.
3. **Internal faithfulness.** When a proof step claims one of the school's mechanisms, are that mechanism's SAE
   features (exp06 feature cards, mapped to the L3 entry fields) active on the tokens that make the claim?
4. **Instilling.** Do fine-tuning on grounded trajectories (C-agent) and rejection-sampling fine-tuning
   (C-agent+RFT) change 1–3 relative to prompting alone (A-agent)? (The rows of the design note's factorial.)

## Systems (all Qwen3-8B, non-thinking chat format, the tools of `src/mosaic/tools.py`, loop `src/mosaic/agent.py`)

| System | Description |
|---|---|
| A-agent | base model, the school's system prompt plus `configs/agent/system_note.txt` |
| C-agent | school LoRA trained on the multi-turn v4 trajectories (tool messages masked from the loss) |
| C-agent+RFT | C-agent after 1–2 rounds of rejection-sampling fine-tuning on rule-based checks (if decision 7 = yes) |
| A, C (single pass) | exp01's arms on the same events, for the text measures only (they have no tools and no proof) |

## Event sets (frozen at registration)

- **E-dev**: template events, item seed 7 (used by the Task A spike and for development; never confirmatory).
- **E-test**: 30 template events per school with an item seed fixed at registration, backdrops from the item
  generator (items version 3), none of their templates' instances in the training set (fresh slots and backdrops).
- **E-hist** (if the episode database is uploaded): historical episodes before 2025, described trigger-only as in
  exp02; the L2 tool hides the episode itself and every later episode (`before` = the trigger date).

## Measures

- **M1 validity**: protocol compliance (episode tool, macro tool, answer), tool-call validity (parse, arguments, no
  tool error), proof validity (steps typed L1/L2/L3/L5, refs resolvable, `Proof.check` of pmpol on the converted
  proof) and grounding (every L1/L2 ref was returned by a tool in that conversation): `teacher.check_v4` plus the
  pmpol conversion.
- **M2 counterfactual sensitivity** (behavioural). For each conversation the run is repeated with the tools changed
  once, everything else equal (same seed):
  - *cited*: the first indicator the proof cites is moved across the school's diagnostic line by a pre-specified
    shift (unemployment ±2.0 pp around the 4.5% natural rate; CPI ±3.0 pp around the 2% target; policy rate so that
    the real rate changes sign; M2 growth ±5 pp around trend plus target);
  - *placebo*: an indicator the agent did not request is moved by the same relative shift;
  - *L2 swap* (exploratory): the returned episodes are replaced by those of a contrasting query fixed per template
    category.
  Sensitivity = Jensen–Shannon divergence between the original and the counterfactual scenario distributions
  (scenarios matched by order), plus the share of proofs whose dependent steps change.
- **M3 SAE faithfulness** (internal; only if exp06 gate S0 passes for the agent states). For proof steps typed L3
  and mapped to an L3 entry field (proof-step typer below), the mean activation of that field's features on the
  reasoning tokens the step summarises, against matched control tokens from steps of other fields.
- **Proof-step typer** (D8): a decision model (Vega or Kev, `noul`/`choice` type) labels each step's layer and L3
  field; validated against ~300 hand-typed steps (accuracy, ECE) before it is used; a human-typed subset is the
  fallback if it fails (accuracy < 0.8).

## Hypotheses (E-test; paired over conversations; sign-flip permutation; Holm across F-H1 to F-H4)

- **F-H1 (grounding)**: grounded-proof share(C-agent) > grounded-proof share(A-agent).
- **F-H2 (behavioural faithfulness)**: for each agent system, sensitivity(cited) > sensitivity(placebo).
- **F-H3 (training and faithfulness)**: the gap sensitivity(cited) − sensitivity(placebo) is larger for C-agent than
  for A-agent.
- **F-H4 (internal faithfulness)**: claimed-mechanism feature activation > control activation (only if M3 runs).
C-agent+RFT against C-agent on F-H1 and F-H3 is reported as secondary (one-sided, unadjusted) if RFT is trained.

## Decision rules

1. F-H2 holds → the proofs are behaviourally faithful: the agents use the facts they cite. Fails → the proofs are
   rationalisations as far as this test can tell; the thesis says so and RQ2's answer is negative.
2. F-H1 and F-H3 hold → fine-tuning on grounded trajectories improves both grounding and faithfulness.
3. F-H4 agrees with F-H2 → behavioural and internal evidence converge (the "reasoning or vocabulary?" question gets a
   second, independent instrument next to exp06 and the judges).

## Threats and controls

- Implausible counterfactuals: shifts stay inside the item generator's ranges, and the backdrop's derived values
  (curve, spreads) are recomputed so the facts still hang together.
- Memorised history instead of tool use: the cited/placebo contrast is within model and event; E-hist hides the
  episode itself from the L2 tool.
- Stand-in L2 table: E-test uses it as the tool's world; results on E-hist (the real database) are the external check.
- Small effects: 90 conversations per system and three counterfactual runs each; power is estimated on E-dev before
  registration and the set size raised if needed.
- Typer errors: validated before use, human fallback.

## Compute

Inference only: about 90 events × 4 runs × 3 agent systems ≈ 1,100 conversations of ≤ 4 rounds on a 48 GB card
(1–3 GPU-hours), plus the SAE pass of exp06 on the agent states (1–2 GPU-hours).

## Implementation (agent, E-dev only until registration)

`mosaic exp07 counterfactual|run|score` on top of `mosaic.agent.run_agents` and `mosaic.tools.ToolBox` (a ToolBox
with one fact or the episode set changed), the pmpol `Proof` conversion of the [Proof] block, offline tests.
