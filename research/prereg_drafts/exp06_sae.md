# DRAFT pre-registration — exp06: What does fine-tuning change inside the model? (sparse autoencoders)

Status: **DRAFT, P1** (decision D10). Thesis chapter 4 (RQ1, mechanism); the proof-faithfulness analysis on agent proofs serves RQ2 (exp07). Part I must be registered **before the
exp01 freeze**, because it re-scores exp01's test outputs with a new instrument; its feature lists are chosen on
probe and dev data only. Part II is registered at the same time and run after the exp01 final run.

## Questions

1. **Measurement.** Can sparse-autoencoder (SAE) features measure school fidelity and cross-school contamination
   at the level of concepts rather than vocabulary, and does that measure agree with the judge and the human
   raters (exp01 amendment 2)? This answers the examiner question "do keyword scores measure reasoning?" with a
   third, independent instrument.
2. **Mechanism.** Where fine-tuning beats prompting (exp01 H1), what changed inside the model: the school's own
   L3 concepts, the output format, or style? Does fine-tuning separate the schools internally (less activation of
   the other schools' concepts) more than few-shot prompting does?
3. **Causal check (optional).** Are those features used: does ablating them lower school fidelity, and can adding
   them (steering) replace fine-tuning?

## Models and SAEs (public, no SAE training needed)

| Role | Model | SAE (Hugging Face) | Notes |
|---|---|---|---|
| Generating model, main | `Qwen/Qwen3-8B` (exp01 arms A, B, C; amendment 4) | `Qwen/SAE-Res-Qwen3-8B-Base-W64K-L0_50` (and `_L0_100`) | Qwen-Scope; residual stream, all 36 layers, TopK, 65,536 features. Trained on the **base** model; transfer to the post-trained model and its LoRA adapters is checked by gate S0 |
| Reader (Part I) | `Qwen/Qwen3-8B-Base` reading plain text | same SAE | the SAE's own model and data type, so Part I needs no transfer assumption |
| Replication | `Qwen/Qwen3.5-27B` (exp01b arms A, B, C) | `Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50` (and `_L0_100`) | the only Qwen-Scope SAE trained on a post-trained model; 64 layers, 81,920 features |
| Not used | Qwen3.8-27B | none exists | — |

Qwen-Scope weights are `.pt` files per layer (`W_enc`, `W_dec`, `b_enc`, `b_dec`), TopK encoder; licence "qwen"
with a scientific-research-use condition, which this thesis meets. The encoder formula and the layer-index
convention are checked empirically by gate S0 (a wrong formula shows up as a high unexplained variance).

## S0 — validity gate (dev and probe data only; blocks everything else)

For each **state** — reader; A (school prompt); B (school prompt + exemplars); C (LoRA) — and every 4th layer:

- **FVU**: fraction of variance of the residual stream unexplained by the SAE reconstruction, on response tokens.
- **CE recovered**: 1 − (CE_splice − CE_clean) / (CE_mean-ablate − CE_clean), next-token cross-entropy on response
  tokens when the layer's residual is replaced by its reconstruction.

A layer passes for a state if FVU ≤ 0.40, CE recovered ≥ 0.80 and FVU ≤ 1.5 × the reader's FVU at that layer
(thresholds to be confirmed at registration from the reader's own values, never from test data). Analysis layers:
the three layers with the highest school separability (DiffMean AUROC on the keyword-free probe set, below) among
those that pass for every state, at least 4 layers apart.

**No SAE is trained, continued or fine-tuned in this thesis, and no other SAE suite is substituted** (human decision,
2026-11-01: use the public Qwen-Scope SAEs and do not persist when they fit badly). If a state fails at every scanned
layer, its SAE results are not reported as evidence: Part II drops that state, Part I (reader) and the non-SAE
baselines (DiffMean, linear probes) carry the analysis, and the failure is reported as a limitation. Effort cap: gate
S0 and the layer scan take at most one pod session (6 GPU-hours); there are no further attempts.

## Probe sets (built and frozen before registration)

- **(a) School texts**: the SFT trajectories of each school (the `[Think]` and `[Output]` parts), split 80/20 by
  seed episode into selection and validation parts.
- **(b) Keyword-free paraphrases**: 20 paragraphs per school (5 for each field of the school's L3 entry in
  `kb/L3/schools.yaml`: drivers, frictions, policy, typical signals), 60–120 words each, containing **no term**
  from `configs/lexicons.toml` (checked automatically, anti-signals included). Drafting may be AI-assisted; the
  author approves every paragraph (logged in the AI-use ledger). Plus 20 neutral paragraphs describing data
  releases without a causal theory.
- **(c) Neutral corpus**: dev event texts and the neutral paragraphs.

## Part I — SAE features as a measurement instrument (reader model)

**Feature selection** (per school s and analysis layer): document-level AUROC of each feature's mean activation,
school s versus the other two schools.

- F_s = the 50 features with the highest AUROC on (a)-selection, each with AUROC ≥ 0.75 there and ≥ 0.70 on
  (a)-validation; excluding features with more than half of their activation mass on structural markers
  (`[Think]`, `[ToolCall]`, `[Observe]`, `[Output]`, role tokens) and features active on more than 20% of neutral
  tokens.
- F_s^kf ("concept features") = members of F_s with AUROC ≥ 0.70 on the keyword-free set (b).
- Every selected feature gets a label: its top-activating contexts are explained by Claude Opus 5.5 (blind to the
  school; analysis only, never training data) and scored by a detection test on held-out contexts (Paulo et al.
  2025); the author checks 30 random labels. Each label is mapped to a field of the L3 entry (drivers, frictions,
  policy, signals) or to "format", "style" or "other". These **feature cards** go into a thesis appendix.

**Scores** for a text x (mean over the analysis layers):
mass_s(x) = mean over tokens of Σ_{f ∈ F_s} a_f, divided by its mean on school s's probe documents;
**feature consistency** FC_s(x) = mass_s / Σ_{s'} mass_{s'}; **feature contamination** = Σ_{s' ≠ s} mass_{s'};
FC^kf and contamination^kf use F^kf. Non-SAE baseline (required by Kantamneni et al. 2025 and Wu et al. 2025):
a difference-of-means school direction d_s on the same probe data, scored as the projection margin.

Feature lists, normalisers, layers and the SAE variant are written to `configs/sae_features.toml` and locked by
`mosaic freeze` with exp01. Part I is computed on all exp01 arms (A, B, C, D, T): the reader can read any text,
so the Opus 5.5 reference is placed on the same scale.

## Part II — mechanism (each arm's own model, teacher-forced on its cached test outputs)

The cached exp01 outputs are fed back through the model that generated them (base + school prompt, + exemplars, or
+ LoRA), so the activations equal those during generation and nothing is re-sampled. On the response tokens, at
the analysis layers: **internal** own-school mass and other-school mass (the frozen F_s from Part I), and the
DiffMean projections.

**Model diffing** (exploratory): for each adapter, the mean activation difference C − A on (i) the dev events and
(ii) the neutral corpus (narrow fine-tunes leave readable traces even on unrelated text; Minder et al., ICLR 2026),
decomposed into the 30 SAE features with the largest change, labelled and classified as own-school L3 concept /
other-school concept / format / economics-generic / other. The same for the exemplar effect B − A. Reported as the
composition of "what each kind of adaptation adds".

## Hypotheses (registered with Part I; test events; paired over events; event-level resampling)

- **S-H1 (validity)**: over the judged items of exp01 amendment 2, Spearman(FC^kf, judge fidelity) > 0
  (one-sided permutation). If the judge fails its acceptance rule on fidelity, the 60 human-rated items are used
  instead. Reported beside Spearman(C_s, judge fidelity) and the partial correlation controlling for C_s.
- **S-H2 (concepts, not only words)**: FC^kf(C) > FC^kf(B) per school, sign-flip permutation, Holm across schools.
- **S-H3 (internal separation)**: internal other-school mass(C) < internal other-school mass(B) per school, same
  test and correction.

Holm across S-H1 to S-H3 as one family. Everything else is exploratory, including the Qwen3.5-27B replication.

Interpretation, fixed in advance:

1. exp01 H1 and S-H2 both hold → fine-tuning instils school concepts, not only school vocabulary.
2. H1 holds, S-H2 fails → the advantage is lexical or stylistic as far as SAE features can tell; the thesis says so.
3. S-H3 holds where textual contamination (exp01 H2) does not differ → prompting suppresses the other schools'
   words but not their concepts; fine-tuning separates them internally (reported with the divergence
   internal − textual contamination per arm).
4. S0 fails for the C state → Part II not reported as evidence; Part I stands (reader only).

## Part III — optional (dev only unless separately registered; P2)

- **Ablation**: zero the top 10 / 30 own-school features in C during generation on dev events; change in C_s and
  judge fidelity (judge pilot budget), against ablating as many random features of matched frequency.
- **Steering**: add α·d_s (DiffMean) or the decoder directions of F_s to arm A at one analysis layer, α tuned on
  dev; compared with B and C on dev. Expected from AxBench (Wu et al., ICML 2025): prompting ≥ steering.
- **Training-data audit**: score every trajectory with FC and feature contamination; compare with its keyword
  contamination; optionally retrain C without the 10% most contaminated trajectories and compare on dev.
- **Links to exp03**: internal school mass at forecast time versus inter-school disagreement (H6).

## Threats and controls

| Threat | Control |
|---|---|
| SAE trained on the base model and on pretraining text; chat format and LoRA shift activations (cf. Kissane et al. 2024; FAST, Li et al. 2025) | Gate S0 per state and layer; reader = the SAE's own model; replication with an SAE trained on the post-trained model (Qwen3.5-27B) |
| SAE-based methods often fail to beat simple baselines (Kantamneni et al., ICML 2025; Wu et al., ICML 2025; Smith et al. 2025) | Every quantitative claim paired with a DiffMean or linear-probe baseline; SAEs used where baselines cannot help: unsupervised discovery (diffing) and labelled, ontology-mapped explanations |
| Features differ between SAE runs (Paulo & Belrose, 2025) | Main results repeated with the L0 = 50 and L0 = 100 SAEs; a result is reported as robust only if the sign agrees |
| Circularity: features selected on the trajectories that trained C (and supply B's exemplars) | Confirmatory claims use F^kf, which must also separate the schools on keyword-free text written independently of the trajectories |
| LLM feature labels can be wrong | Detection scores, 30 labels checked by the author, labels never used as evidence on their own |
| Teacher-forced activations differ from generation | Checked on 10 dev outputs by comparing next-token logits |

## Compute and budget

8B: activation passes over ≈ 3 M probe tokens + ≈ 1.5 M exp01 output tokens per state; only the top-k SAE codes
are stored (≈ 1–2 GB). Well under one GPU-day on a 48 GB card. 27B replication: ≈ 1 GPU-day on an 80 GB card.
Opus calls (feature labels and detection tests): ≈ 500 in total, spread over several days of the subscription.

## Implementation (agent, dev and probe data only)

`src/mosaic/sae.py` (Qwen-Scope loader, TopK encode/decode, FVU and CE-recovered, activation capture with hooks for
base and PEFT models, teacher forcing, AUROC selection, scores) and `mosaic sae gate|select|score|internal|diff`,
with offline tests on small random tensors. Test-split steps run only through `scripts/final.sh` (human).

## Literature anchors

Qwen-Scope (Qwen Team, 2026); Gao et al. 2024 (TopK SAEs); persona vectors (Chen et al. 2025: difference-of-means
trait directions, fine-tuning shifts along them, training-data screening); Minder et al. ICLR 2026 (narrow
fine-tuning leaves readable activation differences); Kissane et al. 2024 (SAEs usually transfer between base and
chat models); Kantamneni et al. ICML 2025 and Wu et al. ICML 2025 (AxBench) (strong baselines); Paulo et al. 2025
(automatic interpretation); Paulo & Belrose 2025 (feature instability).
