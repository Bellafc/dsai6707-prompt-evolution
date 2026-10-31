<!--
AI-ASSISTED DRAFT. Written by Claude (Claude Code session, 2026-10-31) at the author's request, from
research/THESIS_DESIGN.md, prereg/ and research/prereg_drafts/. Logged in research/AI_USE_LEDGER.md.
PolyU's Student Guide on the Use of GenAI requires AI-generated material to be identified and the student to be
accountable; THESIS_DESIGN §6 says thesis prose is the author's. Treat this file as a scaffold: every sentence
must be read, checked against the registered documents and rewritten in the author's own words before it enters
the thesis. Numbers and settings below were copied from the design documents as of 2026-10-31; where a design
is still a DRAFT (amendment 4, exp02–exp06), the text says so and must be updated when the registration is made.
Citation keys refer to research/thesis_drafts/references/*.bib.
-->

# Chapter 3. Research design and methodology

This chapter sets out the design of the study as a whole. Section 3.1 states the research questions and the
logic of the evidence. Section 3.2 gives the problem formulation and notation. Section 3.3 describes the
epistemic architecture, a knowledge-layer ontology that organises every input and output of the system.
Sections 3.4 to 3.8 describe the data, the school agents, the interpretability instrument, the analogy-retrieval
method and the forecasting and aggregation stage, each with its pre-registered hypotheses. Section 3.9 gives
the statistical protocol shared by all experiments, Section 3.10 the threats to validity and the controls
adopted against them, and Section 3.11 the reproducibility, governance and AI-use arrangements. The later
chapters (4 to 6) report the experiments; they refer back to this chapter for the design and do not repeat it.

## 3.1 Research questions and the logic of the evidence

Macro-MOSAIC (Mixture-Of-Schools Analogy-Informed Chains) is a three-stage system for the analysis of
macroeconomic events: (Stage 1) retrieval of historical analogues from a structured episode database;
(Stage 2) parallel interpretation of the event by three language-model agents, each specialised to one school
of macroeconomic thought (Keynesian, Austrian, Monetarist); and (Stage 3) conversion of the schools' reasoning
into calibrated, coherent probability forecasts with an explicit record of the evidence each forecast rests on.
The thesis asks three questions, each answered by one stage and one chapter.

**RQ1 (Chapter 4).** Does parameter-efficient fine-tuning instil distinct, theory-consistent school reasoning
beyond the best prompting baseline, including the base model's own reasoning ("thinking") mode? What changes
inside the model when it is fine-tuned rather than prompted? Does the advantage survive a stronger, newer base
model? Evidence: exp01 (fine-tuning versus prompting on Qwen3-8B, with keyword metrics and an LLM judge
validated against two human raters), exp06 (a sparse-autoencoder instrument and mechanism study) and exp01b
(replication on Qwen3.5-27B, conditional on feasibility).

**RQ2 (Chapter 5).** Do historical episodes that are similar in macroeconomic *state* predict how assets react
to a new episode better than episodes that are similar in narrative, or than naive similarity and
unconditional averages? Evidence: exp02 (expanding-window retrieval on the episode database with point-in-time
states).

**RQ3 (Chapter 6).** Do pooled school forecasts beat single schools and prompted schools on real
macroeconomic outcomes that resolved after the models' training cut-off? Are the forecasts calibrated and
logically coherent? Is disagreement among the schools informative about error? Evidence: exp03 (resolved
prediction markets, 2025 to 2026), exp04 (coherence), and exp05 (prospective live forecasting, optional).

Two features of the design run through every experiment. First, each experiment is **pre-registered**: the
hypotheses, metrics, decision rules and analysis plan are written and committed to the repository before the
held-out data is touched, and later changes are recorded as dated amendments rather than edits
\citep{nosek2018preregistration}. Results that follow the registered plan are reported as confirmatory;
everything else is labelled exploratory. Second, the design is **leakage-aware** throughout: model inputs are
restricted to information available at the forecast time, the forecasting benchmark contains only outcomes
resolved after the base model's release, and the held-out evaluation sets are frozen and accessed once.

The Confirmation of Registration proposed a fourth stage, cross-asset allocation with a 2023 to 2025 walk-forward
backtest, as the main evidence. That stage has been moved to the discussion chapter (Chapter 7) as an
application, for reasons set out in Chapter 1: the backtest window lies inside the training period of every
candidate model, so a backtest could not separate reasoning from recall \citep{lopezlira2025memorization}; the
number of events in such a window gives no statistical power; and a benchmark of resolved prediction markets
answers the same question (does the system produce useful probabilities about macroeconomic outcomes?) without
look-ahead.

## 3.2 Problem formulation and notation

Let $e$ denote a macroeconomic event (a data release, a policy decision, a shock) and let $t$ be the time at
which the system reasons about it. The information set at $t$ is $\mathcal{I}_t$, which contains only material
published on or before $t$. The macro state is a vector $s_t \in \mathbb{R}^{35}$ of indicator values *as
published* at $t$ (Section 3.4.2). The schools are indexed by $k \in \{K, A, M\}$.

Stage 2 maps $(e, s_t, \mathcal{R}_t)$, where $\mathcal{R}_t$ is the set of retrieved analogues, to one
structured trajectory per school,

$$
\tau_k(e) = \big[\text{Think} \rightarrow \text{ToolCall} \rightarrow \text{Observe} \rightarrow \ldots
\rightarrow \text{Output}\big],
$$

whose Output block contains (i) a causal chain naming the transmission mechanisms that connect the event to
intermediate effects and to asset impacts, (ii) a probability distribution $p_k = (p_{k1}, \ldots, p_{kJ})$ over
$J$ mutually exclusive scenarios, and (iii) directional signals (long, short, neutral, with a conviction grade)
for the major asset classes. In the forecasting setting of Chapter 6 the scenarios are the ordered bins
$B_1 < \cdots < B_J$ of a published statistic (for example, month-on-month CPI in steps of 0.1 percentage points),
the outcome is the bin $y \in \{1, \ldots, J\}$ that the official release falls into, and the pooled forecast is

$$
\bar p = \sum_k w_k\, p_k, \qquad \sum_k w_k = 1,\; w_k \ge 0,
$$

a linear opinion pool \citep{stone1961opinion,ranjan2010combining}, optionally followed by a calibration map
$g_\theta$ fitted on a calibration window (Section 3.8.4) and by a projection onto the set of probability
vectors that are logically coherent across related questions (Section 3.8.6).

Stage 1 maps a query state $s_t$ to the $k$ nearest historical episodes under a distance $d(s_t, s_i)$ over the
pool of episodes with trigger dates before $t$, and predicts the asset reactions to $e$ as the similarity-weighted
mean of the analogues' recorded reactions (Section 3.7).

Three families of outcome are measured. *School fidelity* (Chapter 4) is measured on text: keyword-based
consistency and contamination, judged fidelity on a rubric, and feature-based consistency from a sparse
autoencoder. *Retrieval utility* (Chapter 5) is measured by the directional accuracy and rank correlation of the
analogue-implied reactions. *Forecast quality* (Chapter 6) is measured by strictly proper scoring rules
\citep{gneiting2007strictly}: the ranked probability score for ordered bins, the logarithmic score, the Brier
score and expected calibration error on binary contracts, and by coherence distances across related questions.

## 3.3 Epistemic architecture: knowledge layers, proofs and analytic confidence

Every input and output of the system is assigned to one of six knowledge layers. The layering is taken from
pmpol, the research group's prediction-market analysis system (team code; cited as such throughout), whose
ontology distinguishes facts by how they are known and how far they can be trusted in inference. Table 3.1
gives the mapping to Macro-MOSAIC.

**Table 3.1.** Knowledge layers (L0 to L5) and their role in Macro-MOSAIC.

| Layer | Content in Macro-MOSAIC | Rule in inference |
|---|---|---|
| L0 Institutional rules | Release definitions and publication grids (CPI to 0.1 pp; FOMC target range in 25 bp steps); market resolution rules | Hard constraints: they define scenario sets and the coherence checks of exp04 |
| L1 Point-in-time facts | The 35 indicators *as published* at $t$ (ALFRED vintages), with validity and record times | The only facts a model may see; revised data are never used as inputs |
| L2 Base rates | Analogue episodes (Stage 1); the historical distribution of each series; venue calibration slopes | Priors and baselines |
| L3 Contested frameworks | The three schools, recorded as knowledge-base entries (`kb/L3/schools.yaml`) with drivers, frictions, policy prescriptions and typical signals, and with sources | Cited, not adopted: one agent per school; outputs shown side by side; no stage selects a winner silently |
| L4 Market observations | Kalshi and Polymarket prices at $t$ | Benchmark only; never a model input |
| L5 Inferences | Each school's distribution; the pools; the retrieval scores | Must carry a proof that traces back to L0 to L4 |

The L3 rule is the design principle behind the multi-school architecture: frameworks that contradict one
another are recorded with their sources and shown in parallel rather than merged into one "consensus" model.
The three schools were chosen because they make structurally different causal claims about the same event
(aggregate demand and multipliers; credit-driven distortion of the structure of production; money growth and
its lags), because each is represented in current policy and market discourse, and because each has a
canonical literature from which the school's definition, the judge's rubric and the lexicons can be drawn
(Chapter 4 gives the design rationale and sources).

**Proof per forecast.** Every L5 output is accompanied by a proof object in pmpol's format: an ordered list of
steps, each tagged with its layer, its source (a knowledge-base fact id, a data series and vintage date, an
episode id with its similarity score, or a school entry) and the time it refers to. The plain-language summary
of a forecast is generated from the proof and from nothing else, so that the text cannot claim more than the
chain supports. A conclusion that does not trace back to at least one L0 to L4 step is labelled ungrounded.

**Analytic confidence.** Following the analytic standards of the United States Intelligence Community (ICD 203)
\citep{odni2015icd203}, the probability of an outcome and the analyst's confidence in the judgement are kept
on separate axes. Probabilities are reported numerically and with the ICD 203 likelihood words. Confidence
(high, moderate, low) is read from the proof as its weakest link: incomplete L1 inputs, weak analogues, a
school output that failed to parse, or an unclear L0 resolution rule each lower the grade, and every downgrade
is stated. Disagreement among the schools is deliberately *not* part of the confidence grade, because it is
tested separately as a predictor of error (exp03, H6); confidence is tested in the same way (H7). Both tests
turn the architecture's claims about interpretability and trust into falsifiable statements.

## 3.4 Data

### 3.4.1 The macro episode database

The retrieval corpus is a database of 141 macroeconomic episodes between 1971 and 2025, built for the
Confirmation and audited for this thesis. Each episode is anchored to a trigger date and records: (i) the
macro context, 35 indicators from the Federal Reserve Economic Data (FRED) system at the trigger date, covering
interest rates and the term structure, inflation and inflation expectations, employment, money and credit,
financial conditions, the fiscal position and housing; (ii) closing levels of 22 instruments across equities,
rates, currencies, commodities and volatility on the trigger date; (iii) realised reactions of those 22
instruments at five horizons (1 week, 1, 3, 6 and 12 months), giving 13,571 reaction cells after removing cells
for instruments that did not yet exist or horizons that had not yet elapsed; (iv) categorical tags and labels
from a taxonomy of 19 transmission channels; and (v) for 117 episodes, a narrative summary and three parallel
school-specific interpretations generated with an LLM at construction time. Episodes fall into eight
categories (central-bank decisions, banking and credit crises, geopolitical shocks, commodity shocks, currency
crises, inflation and stagflation, fiscal events, pandemics and other black-swan events); the temporal
distribution is skewed towards recent decades.

Two changes are made for the thesis. **Point-in-time states.** The indicator values recorded at construction
were final (revised) values. For retrieval and for forecasting, each episode's state is rebuilt from the
ALFRED archive of data vintages \citep{croushore2001realtime} as the values that had been published on the
trigger date; where no vintage exists the revised value is used and flagged. The revised-data states are kept
for an ablation. **Trigger-only descriptions.** The narratives describe the episode including its aftermath and
market moves, which would leak the outcome into any text-based retrieval. A second description of each episode
is written that contains only what was known at the trigger date; twenty of these are spot-checked by the
author, and the original narratives are retained to measure the size of the hindsight effect (Chapter 5).

### 3.4.2 Point-in-time macro states

The macro state at any time $t$ is the vector of the 35 indicators as published on or before $t$, constructed
from ALFRED vintages with the bitemporal convention of pmpol (each value carries the period it refers to and
the date it became available). The same construction supplies the model inputs for the forecasting experiments,
so that a forecast made "as of $t$" never sees a value released after $t$ or a later revision of a value
released before $t$. The monthly panel of standardised indicators, from the earliest common date to $t$, is also
the sample on which the covariance matrix for Stage 1 is estimated (Section 3.7).

### 3.4.3 Training data for the school agents

The adapters are trained on synthetic agent trajectories generated for the Confirmation: 500 per school, built
from 107 abstract event templates in 14 categories, each instantiated with randomised macro snapshots so that
the model learns a reasoning pattern rather than event-specific answers. Each trajectory follows the format
Think, ToolCall (episode-database query), Observe, Think, ToolCall (macro data), Observe, Think, Output. The
trajectories were produced by a teacher model (GPT-4o) prompted with the school's definition and the seed
material of the 117 interpreted episodes. For the thesis, every trajectory is audited for its seed episode's
date: trajectories whose seed episode falls after 2025-04-30 are removed before training, because the same
adapters forecast outcomes from May 2025 onwards (amendment 4, Change 6, draft). The number removed per school
is reported with the training-data card. If the original trajectories cannot be recovered, they are regenerated
from the same seeds and prompts with a teacher whose licence permits training on its outputs, with format,
leakage and quality filters fixed before generation, and the thesis says so (amendment 4, Change 5, draft).

### 3.4.4 Evaluation events for school fidelity (exp01)

The held-out set for RQ1 consists of the 96 synthetic events of the Confirmation, written to be structurally
distinct from the training templates: multi-factor contradictory events, unprecedented policy actions and
complex data surprises, labelled by difficulty (medium 42, hard 47, very hard 7). A development set of events
disjoint from the test set (historical episodes from the database) is used for tuning the prompting baseline
and for debugging; exemplars for few-shot prompting are never drawn from the same template as the event being
evaluated. The test set is frozen before the final run and accessed once, by the author, for all arms.

### 3.4.5 The market question set (exp03 to exp05)

The forecasting benchmark is built from settled prediction-market contracts on United States macroeconomic
releases, primarily Kalshi's Economics and Financials categories, with Polymarket economy markets as a
secondary source. Each market is a ladder of mutually exclusive outcome contracts with a published resolution
source, which supplies both a ground truth and a crowd benchmark \citep{wolfers2004prediction}. An *event* is a
pair (series, reference period or meeting). Series in scope: month-on-month CPI (headline and core),
year-on-year CPI, the unemployment rate, the FOMC target-range decision, the advance estimate of real GDP
growth, and the foreign central-bank decisions already covered by pmpol's proposition ontology. The contracts of
each event are mapped, through the L0 publication grid, to one ordered set of mutually exclusive bins (the
*scenario set*); events whose contracts do not partition the outcome space after mapping are excluded and
listed.

The resolution window begins on 2025-05-01, two days after the release of the base model, so that every
outcome post-dates the model's training data. The **calibration window** (2025-05-01 to 2025-12-31) is used to
fit pool weights and calibration maps and to pilot format compliance; the **test window** (from 2026-01-01) is
touched once, after registration. Counts per series and window, exclusions and context coverage are reported
in a data card before registration; no forecast on the test window is scored before then. Kalshi's terms do
not permit redistribution of compiled market data, so the data-availability statement lists contract
identifiers and the reconstruction scripts rather than the data.

## 3.5 Stage 2: school agents and the fine-tuning versus prompting comparison (exp01)

### 3.5.1 Base model

Arms A, B and C run on Qwen3-8B, a dense, post-trained open-weight model released on 2025-04-29 under the
Apache-2.0 licence \citep{yang2025qwen3}. It replaces the Confirmation's Qwen2.5-7B-Instruct for three reasons:
public sparse autoencoders exist for every one of its layers (Section 3.6), which the interpretability study
needs; its release date leaves about eighteen months of resolved markets outside its training data; and it is
one model generation newer in the same size class, so the change is one of generation, not of scale (scale is
studied separately in exp01b). The model is run in non-thinking mode (chat template with `enable_thinking =
false`) in both training and inference for arms A and C, so that the trained trajectory is the only reasoning
the model writes; arm B may switch the thinking mode on (Section 3.5.3). The Hugging Face revision is pinned at
freeze.

### 3.5.2 Adapter training

One low-rank adapter \citep{hu2022lora} is trained per school with the recipe in Table 3.2, once, and never
tuned on development or test events. The recipe keeps the Confirmation's rank, scaling and epochs and fixes the
settings the Confirmation did not report. Quantised training (QLoRA, \citealp{dettmers2023qlora}) is dropped in
favour of bf16 weights, which removes a quantisation step and matches the larger model of exp01b, for which
4-bit training is not recommended.

**Table 3.2.** LoRA recipe (amendment 4, Change 2, draft).

| Setting | Value |
|---|---|
| Data | 500 trajectories per school minus the seed-episode exclusions |
| Rank, scaling, dropout | $r = 32$, $\alpha = 64$, 0.05 |
| Target modules | all linear projections of the attention and MLP blocks |
| Precision | bf16 weights |
| Schedule | 3 epochs; learning rate $2 \times 10^{-4}$, cosine decay, 3% warm-up; effective batch 16; maximum length 4,096 tokens |
| Loss | assistant tokens only |
| Seed | 20261030 |

The freeze record stores the SHA-256 of every adapter file, and the generation cache key includes them, so that
outputs of an earlier adapter can never be reused for a retrained one.

### 3.5.3 Arms

All arms answer the same events with the same user template and, for A, B and C, the same sampling settings
(temperature 0.7, top-p 0.9, at most 2,048 answer tokens, fixed seed).

- **Arm A (zero-shot chain of thought).** The base model with the school's system prompt, which states the
  school's principles and requests the trajectory format. This is the Confirmation's "base" condition.
- **Arm B (few-shot chain of thought, the strongest prompting baseline).** Arm A plus $k$ exemplar trajectories
  drawn from the school's own training corpus, so that the prompt carries the same demonstrations the adapter
  was trained on. The configuration is tuned on the development set only, within a fixed budget of at most 12
  configurations on at most 40 events: $k \in \{1, 2, 3, 5\}$, exemplar selection (random or matched by
  category), truncation length, optional extra school guidance written from textbook definitions, and the
  model's own thinking mode on or off (up to 4,096 thinking tokens in addition to the answer; only the answer
  after the thinking block is scored). Every configuration tried and the one chosen are listed in the
  development summary before the freeze.
- **Arm C (fine-tuned).** The base model with the school's adapter and the messages of arm A.
- **Arm D (frontier reference).** Claude Opus 5.5 with the messages of arm A, called through the Claude Code
  command-line interface with the default system prompt replaced, no tools, reasoning effort fixed at medium.
  The interface exposes no sampling controls, so D does not share A to C's sampling settings; comparisons with D
  are descriptive, with confidence intervals and no hypothesis. D is a reference for how far a current frontier
  model is from an 8B adapter, not a teacher: the service's consumer terms do not permit using its outputs to
  train models, and D's outputs and the judge's scores are used for evaluation only.
- **Arm T (teacher, optional).** GPT-4o, the model that generated the training trajectories, with the messages
  of arm A, run only if budget allows. T answers the question "why not use the teacher directly?"; if T is not
  run, the thesis says so.
- **Arms A7 and C7 (optional, descriptive).** If the original trajectories are available, the Confirmation's
  model (Qwen2.5-7B-Instruct) is run with arm A's messages and with adapters retrained by the Confirmation's own
  recipe, on the same 96 events, and compared with the Confirmation's Table 4.3 to link Chapter 4 to the
  Confirmation.

Arms whose inputs are fixed by the registration (A, C, D, T) may have their test outputs *generated* before the
freeze by a human-gated command that writes only to the generation cache, computes no score and logs the access;
nobody reads those outputs before the freeze, and the official run reads them back from the cache (amendment
3). Arm B cannot be pre-generated because its configuration is tuned on the development set.

### 3.5.4 Text-level metrics

The metrics are the Confirmation's, re-implemented and frozen with the registration; the keyword lists are the
Confirmation's original lists, and a parity check against the Confirmation's reported numbers is run before the
freeze.

**School consistency.** For school $s$ with a must-have pool $\mathcal{M}_s$ (6 to 7 core concepts), a
strong-signal list $\mathcal{S}_s$ and an anti-signal list $\mathcal{A}_s$ of competing schools' terms,

$$
C_s(x) = \max\!\Big(0,\;
\tfrac{1}{2}\,\frac{|\text{hits}(x, \mathcal{M}_s)|}{|\mathcal{M}_s|}
+ \tfrac{1}{2}\,\min\!\Big(\frac{|\text{hits}(x, \mathcal{S}_s)|}{5}, 1\Big)
- 0.15\,|\text{hits}(x, \mathcal{A}_s)|\Big),
$$

where hits are counted as distinct terms present in the response (word-boundary matching, case-insensitive).

**Cross-school contamination.** The mean number of anti-signal hits per response.

**Structural completeness.** The fraction of seven elements present: the Think, ToolCall, Observe and Output
tags, a causal chain, a scenario distribution with at least two probabilities, and at least one asset signal.
The presence of the Output block is also reported on its own, because downstream stages require it.

**Inter-school diversity.** For each event, with $S_i$ the set of (asset, direction) pairs produced by school
$i$,

$$
D = \binom{K}{2}^{-1} \sum_{i<j} \Big(1 - \frac{|S_i \cap S_j|}{|S_i \cup S_j|}\Big), \qquad K = 3.
$$

Keyword metrics measure school fidelity, not forecasting accuracy; forecasting quality is the subject of
Chapter 6 and is not claimed from exp01.

### 3.5.5 Judged fidelity and its validation

Keyword hits measure vocabulary. To answer whether they also track reasoning, a blind LLM judge scores a
stratified subset of the test outputs on four 1 to 5 scales, and the judge itself is validated against humans
(amendment 2):

- **Judge.** Claude Opus 5.5, shown the designated school, a one-paragraph definition of the school (identical
  to the L3 entry), the task and the answer, and nothing that identifies the arm or model. Scales: *fidelity*
  (reasoning driven by the school's mechanisms), *purity* (no competing-school drivers), *coherence* (event to
  mechanisms to scenarios to signals) and *plausibility* (economically sound). Items: arms A, B and C on a
  difficulty-stratified subset of 48 test events for each of the three schools (432 judgements). Ten per cent
  of items are judged twice to estimate test-retest reliability. Arm D is excluded because the judge is the same
  model as arm D, and LLM evaluators favour their own generations \citep{panickssery2024llm}.
- **Human validation.** Two raters (the author and an economics-trained colleague) independently score a
  blinded sample of 60 judged items, stratified by arm and school, with the same rubric. Reported: quadratic
  weighted kappa between the raters per scale \citep{cohen1968weighted}, and the Spearman correlation between
  the judge and the mean human score per scale.
- **Acceptance rule.** A scale is accepted as a measure if inter-rater weighted kappa $\ge 0.40$ and
  judge-human Spearman $\ge 0.50$; accepted scales are secondary evidence for H1 and H2, the rest exploratory.
- **Convergent validity.** The Spearman correlation between $C_s$ and judged fidelity over all judged items is
  reported; if it is below 0.30, the thesis states that keyword consistency does not track judged fidelity and
  gives the judge results equal weight in the discussion of RQ1.

### 3.5.6 Hypotheses and decision rules (registered)

Tests are paired over the 96 events (Section 3.9).

- **H1 (primary).** $C_s$: arm C $>$ arm B, per school, Holm-corrected across the three schools at
  $\alpha = 0.05$.
- **H2.** Contamination: C $<$ B for at least two of three schools (secondary, unadjusted).
- **H3.** Output presence: C $\ge$ B, descriptive with 95% bootstrap intervals.
- **H4.** Diversity: $D(\text{C}) > D(\text{B})$, paired over events.
- Judge comparisons (C vs B, C vs A, B vs A per school and accepted scale) form a secondary family with its own
  Holm correction.

Interpretation, fixed before any result: if H1 holds for at least two schools, fine-tuning adds school fidelity
beyond the best prompting baseline; if C $\approx$ B, the thesis argues for fine-tuning on cost, latency,
reproducibility and control of the knowledge cut-off, not on fidelity, and says so; if B $>$ C significantly
for at least two schools, this is reported as a negative result and Stage 2 is re-examined.

### 3.5.7 Replication on a stronger base (exp01b, conditional)

A stronger 2026 base model prompts better, so the fine-tuning advantage may shrink. exp01b repeats arms A, B
and C with the same trajectories, recipe, tuning budget, events and metrics on Qwen3.5-27B \citep{qwen2026qwen35} (released
2026-02-24, Apache-2.0; 64 layers, three in four of them linear-attention layers), the only 2026 open model with
a public sparse autoencoder trained on the post-trained model itself. The primary hypothesis is exp01's H1; the
interaction (whether the C minus B gap is smaller on the larger model) is reported with a confidence interval and
no test claim. The experiment proceeds only if a feasibility spike (bf16 LoRA on the hybrid architecture, served
with the adapter) succeeds; otherwise the thesis keeps an 8B-only RQ1 and reports the reason.

## 3.6 What fine-tuning changes inside the model: the sparse-autoencoder instrument (exp06, draft)

### 3.6.1 Purpose

Keyword scores and judged scores are both read off the text. A third instrument reads the model's internal
representations, for two purposes: *measurement*, a score of school fidelity at the level of concepts rather
than words, validated against the judge and the human raters; and *mechanism*, a description of what
fine-tuning adds relative to prompting (the school's concepts, the output format, or style) and whether
fine-tuning separates the schools internally more than few-shot prompting does. An optional third part asks
whether the identified features are causally used.

### 3.6.2 Sparse autoencoders and the validity gate

A sparse autoencoder (SAE) decomposes a residual-stream activation $x \in \mathbb{R}^d$ into a sparse code over
a wide dictionary of directions \citep{bricken2023monosemanticity,huben2024sparse}. The thesis uses the
Qwen-Scope SAEs released for Qwen3-8B (TopK encoders \citep{gao2025scaling}, 65,536 features, every one of the
36 layers, at two sparsities, $L_0 = 50$ and $100$) and, for the replication, the Qwen3.5-27B SAEs (81,920
features, 64 layers). With $z = \mathrm{TopK}(W_{\text{enc}}\, x + b_{\text{enc}})$ and
$\hat x = W_{\text{dec}}\, z + b_{\text{dec}}$, each feature $f$ has an activation $a_f(x) = z_f$ and a decoder
direction $W_{\text{dec},f}$. No SAE is trained for the thesis.

The Qwen3-8B SAEs were trained on the *base* model and on pre-training text. Chat formatting and LoRA adaptation shift activations, and SAEs do not always transfer across such shifts \citep{kissane2024saes,galichin2026feature}, so a **validity gate (S0)** is run before anything else, for each *state* of the model
(the reader, Section 3.6.3; arm A; arm B; arm C) and every fourth layer, on development and probe data only.
Two quantities are computed on response tokens: the fraction of variance unexplained by the reconstruction,

$$
\mathrm{FVU} = \frac{\mathbb{E}\,\|x - \hat x\|^2}{\mathbb{E}\,\|x - \bar x\|^2},
$$

and the cross-entropy recovered when the layer's residual stream is replaced by its reconstruction,

$$
\text{CE recovered} = 1 - \frac{\mathrm{CE}_{\text{splice}} - \mathrm{CE}_{\text{clean}}}
{\mathrm{CE}_{\text{mean-ablate}} - \mathrm{CE}_{\text{clean}}}.
$$

A layer passes for a state if FVU $\le 0.40$, CE recovered $\ge 0.80$ and FVU is at most 1.5 times the reader's
FVU at that layer (thresholds confirmed at registration from the reader's own values, never from test data). The
analysis layers are the three layers, at least four apart, with the highest school separability (below) among
those that pass for every state. If the fine-tuned state fails everywhere, the mechanism part is reported as not
valid; the fallback is a short continuation of SAE training on activations of all states from the training
trajectories and a neutral corpus, followed by a re-run of the gate.

### 3.6.3 Probe sets, feature selection and feature cards

Three probe sets are frozen before registration: (a) the school texts, the Think and Output parts of the
training trajectories, split 80/20 by seed episode into selection and validation parts; (b) **keyword-free
paraphrases**, twenty paragraphs per school, five for each field of the school's L3 entry (drivers, frictions,
policy, typical signals), 60 to 120 words each, containing no term from the lexicons, anti-signals included,
checked automatically, plus twenty neutral paragraphs that describe data releases without a causal theory;
(c) a neutral corpus of development event texts and the neutral paragraphs. Drafting of (b) may be AI-assisted;
the author approves every paragraph.

For the **reader** (the base model reading plain text, so that the SAE is applied to its own model and data
type) and each analysis layer, every feature's document-level AUROC for school $s$ versus the other two is
computed on the selection part of (a). $F_s$ is the set of the 50 highest-AUROC features with AUROC $\ge 0.75$
on selection and $\ge 0.70$ on validation, excluding features with more than half of their activation mass on
structural markers (the trajectory tags and role tokens) and features active on more than 20% of neutral
tokens. The **concept features** $F_s^{\text{kf}} \subseteq F_s$ are those that also reach AUROC $\ge 0.70$ on the
keyword-free set (b). Each selected feature receives a label from an automated interpretation step (an LLM
explains its top-activating contexts, blind to the school, and the label is scored by a detection test on
held-out contexts, \citealp{paulo2025automatically}); because such scores do not by themselves separate meaningful features from those of a random network \citep{heap2026automated}, the author checks thirty labels at random and labels are never used as evidence on their own. Labels are mapped
to a field of the L3 entry or to format, style or other. The resulting **feature cards** are the thesis's main
display of what the agents' internal school concepts are.

### 3.6.4 Scores and baseline

For a text $x$ and school $s$, averaged over the analysis layers,

$$
\mathrm{mass}_s(x) = \frac{1}{Z_s}\,\frac{1}{|x|}\sum_{t \in x}\sum_{f \in F_s} a_f(x_t), \qquad
\mathrm{FC}_s(x) = \frac{\mathrm{mass}_s(x)}{\sum_{s'} \mathrm{mass}_{s'}(x)}, \qquad
\text{feature contamination}_s(x) = \sum_{s' \ne s} \mathrm{mass}_{s'}(x),
$$

where $Z_s$ normalises by the mean mass on school $s$'s probe documents; $\mathrm{FC}^{\text{kf}}$ and
contamination$^{\text{kf}}$ use $F^{\text{kf}}$. Because SAE-based methods have repeatedly failed to beat simple
supervised baselines \citep{kantamneni2025sparse,wu2025axbench}, every quantitative claim is paired with a non-SAE
baseline computed on the same probe data: a difference-of-means school direction $d_s$, scored as the projection
margin. The feature lists, normalisers, layers and SAE variant are written to a configuration file and locked
with the exp01 freeze; Part I is then computed on the cached outputs of every exp01 arm, including D and T,
because the reader can read any text.

### 3.6.5 Mechanism (Part II)

The cached test outputs of arms A, B and C are fed back through the model that generated them (base plus
school prompt; plus exemplars; plus adapter), teacher-forced, so that the activations equal those during
generation and nothing is re-sampled. On response tokens at the analysis layers the **internal** own-school and
other-school masses (the frozen $F_s$) and the difference-of-means projections are recorded. As an exploratory
model-diffing analysis, the mean activation difference C minus A on development events and on the neutral
corpus (narrow fine-tunes leave readable traces even on unrelated text, \citealp{minder2026narrow}) is decomposed
into the thirty SAE features with the largest change, labelled and classified as own-school concept, other-school concept, format, economics-generic or other; the same is done for the exemplar effect B minus A. The decomposition is read with the known artefacts of sparse model diffing in mind \citep{minder2025overcoming,wang2026persona}, and with the caveat that low-rank adapters change representations differently from full fine-tuning \citep{shuttleworth2025lora}.

### 3.6.6 Hypotheses (registered with Part I)

- **S-H1 (validity).** Over the judged items of exp01, Spearman$(\mathrm{FC}^{\text{kf}}, \text{judged
  fidelity}) > 0$ (one-sided permutation); if the judge fails its acceptance rule on fidelity, the 60 human-rated
  items are used instead. Reported beside Spearman$(C_s, \text{judged fidelity})$ and the partial correlation
  controlling for $C_s$.
- **S-H2 (concepts, not only words).** $\mathrm{FC}^{\text{kf}}(\text{C}) > \mathrm{FC}^{\text{kf}}(\text{B})$ per
  school, sign-flip permutation, Holm across schools.
- **S-H3 (internal separation).** Internal other-school mass is lower for C than for B per school, same test.

Holm correction across S-H1 to S-H3 as one family. Interpretation, fixed in advance: H1 and S-H2 both holding
means fine-tuning instils school concepts and not only vocabulary; H1 holding and S-H2 failing means the
advantage is lexical or stylistic as far as SAE features can tell, and the thesis says so; S-H3 holding where
textual contamination does not differ means prompting suppresses the other schools' words but not their concepts.
Every main result is repeated with the second sparsity ($L_0 = 100$) and, if exp01b runs, with the SAE trained on
the post-trained 27B model; a result is reported as robust only if its sign agrees. An optional Part III
(ablating the top own-school features during generation against random features of matched frequency;
steering arm A with $d_s$ or the decoder directions; a training-data audit) is run on development data only.

## 3.7 Stage 1: structural analogy retrieval (exp02, draft)

### 3.7.1 Distance and covariance

The structural channel measures the distance between the query state $s_t$ and each candidate episode's
point-in-time state $s_i$ by the Mahalanobis distance \citep{mahalanobis1936generalised}

$$
d_M(s_t, s_i) = \sqrt{(s_t - s_i)^\top \Sigma_t^{-1} (s_t - s_i)}.
$$

Estimating a $35 \times 35$ covariance from 141 episodes is ill-conditioned, a concern raised at the
Confirmation. $\Sigma_t$ is therefore estimated not from the episodes but from the **monthly** standardised
indicator panel up to $t$ (hundreds of months), with Ledoit-Wolf shrinkage towards a structured target
\citep{ledoit2004well}. Indicators missing at $t$ (series that did not yet exist) are handled by computing the
distance on the observed subspace. The semantic channel scores the cosine similarity of sentence embeddings of
the trigger-only descriptions; the hybrid score is $\alpha \cdot \text{structural} + (1 - \alpha) \cdot
\text{semantic}$ with the structural term transformed to a similarity.

### 3.7.2 Protocol

Queries are processed in date order. The candidate pool for query $q$ is every episode with a trigger date
strictly before $q$'s, and $\Sigma_t$ uses only data up to $q$'s date, so that no retrieval looks ahead. Methods
compared: structural (Mahalanobis); Euclidean distance on standardised indicators (the plain concatenation used
by History Rhymes, \citealp{khanna2025history}); semantic (cosine on trigger-only descriptions); hybrid; and the
baselines unconditional pool mean, same-category mean and random $k$. The prediction for each instrument and
horizon is the similarity-weighted mean of the top-$k$ analogues' recorded reactions ($k = 5$ by default). The
hyper-parameters ($\alpha$, $k \in \{3, 5, 10\}$, kernel bandwidth) are tuned on development queries (trigger
date before 2005-01-01) only; test queries have trigger dates from 2005-01-01.

### 3.7.3 Metrics and hypotheses

Per query, the directional hit rate over available instrument-horizon cells (primary) and the Spearman
correlation between predicted and realised reactions (secondary), averaged over queries and compared pairwise
over test queries with sign-flip permutation tests and Holm correction across H1 to H3:

- **H1.** Structural $>$ Euclidean (hit rate).
- **H2.** Hybrid $>$ semantic-only.
- **H3.** The best analogy method $>$ the unconditional pool mean.

Two descriptive comparisons measure leakage: point-in-time versus revised states, and trigger-only versus
original narratives. A large gain from the original narratives is evidence of hindsight leakage in narrative
retrieval and is reported as such.

## 3.8 Stage 3: from reasoning to calibrated, coherent forecasts (exp03 to exp05, drafts)

### 3.8.1 Information set and generation

For each event the forecast time is $t$ = seven days before the market's close (one day as a secondary horizon).
The information set contains the event description (series, reference period, release date, the scenario set
in canonical wording), the point-in-time macro context (the 35 indicators as published on or before $t$ and the
target series' latest published values), and, except in the no-retrieval ablation, the top-three analogues from
the episode database with trigger dates before $t$, chosen by the Stage 1 method frozen at that time. No news,
no market prices and no text written after $t$ are supplied.

Each system is sampled three times per event (temperature 0.7, top-p 0.9). Per sample the probabilities are
parsed per bin and renormalised if their sum lies in $[0.8, 1.2]$; otherwise the sample is invalid. The system's
forecast is the mean of the valid samples. An event with no valid sample receives the uniform forecast and
counts as a format failure, which is reported per system; the uniform fallback penalises format failure in the
scores rather than hiding it.

### 3.8.2 Systems

**Table 3.3.** Systems compared in exp03.

| System | Description |
|---|---|
| base | Qwen3-8B, non-thinking, school-neutral system prompt |
| K, A, M | each school adapter with its school system prompt |
| K$'$, A$'$, M$'$ | the base model with each school's system prompt, no adapter (prompted schools) |
| pool-eq | equal-weight linear pool of K, A, M |
| pool-prompt | equal-weight linear pool of K$'$, A$'$, M$'$ |
| pool-skill | weights $w_k \propto \exp(-\lambda\, \overline{\mathrm{RPS}}_k)$ estimated on the calibration window, $\lambda$ chosen there |
| pool-cal | pool-eq after temperature scaling fitted on the calibration window |
| uniform | equal probability on every bin |
| history | the empirical point-in-time distribution of the series' historical changes (pmpol baseline) |
| market | Kalshi prices at $t$ (daily close), normalised over bins; a benchmark, not a competitor to beat |

Frontier API models are not evaluated on the historical windows, because their training data covers 2025 to
2026; they appear only in the prospective exp05. Qwen3.5-27B, if exp01b runs, enters as a secondary descriptive
analysis on test events resolving on or after 2026-03-01.

### 3.8.3 Scores

Bins are ordered, so the primary score is the **ranked probability score** \citep{epstein1969scoring}

$$
\mathrm{RPS}(p, y) = \frac{1}{J - 1} \sum_{j=1}^{J-1} \Big( \sum_{i \le j} p_i - \sum_{i \le j} \mathbb{1}[y \le i]
\Big)^{2},
$$

which, unlike the Brier score over bins, penalises probability mass by its distance from the realised bin.
Secondary scores: the logarithmic score $-\log \max(p_y, \varepsilon)$ with $\varepsilon = 0.01$; the Brier score
\citep{brier1950verification} on the binary contracts; expected calibration error on binary contracts with ten
equal-width bins \citep{naeini2015obtaining,guo2017calibration}; and the format-failure rate. All are strictly
proper or standard diagnostics \citep{gneiting2007strictly}, so a system cannot improve its expected score by
reporting anything other than its belief.

### 3.8.4 Pooling and calibration

The equal-weight linear pool is the registered primary aggregate: it needs no estimation, and linear pools of
calibrated forecasts are in general under-confident rather than over-confident, which the calibration map can
correct \citep{ranjan2010combining}. Two estimated variants are compared with it. Skill weighting uses the
calibration-window RPS of each school with a softmax temperature $\lambda$. Temperature scaling
\citep{guo2017calibration} rescales the pooled log-probabilities by a single parameter $T$ fitted by minimising
the logarithmic score on the calibration window; with one parameter it cannot reorder bins, so it corrects
over- or under-confidence without changing what the pool believes most likely. The Confirmation's plan for
regime-conditional weights was dropped because regime cells would be nearly empty in a leakage-free window;
its Platt-scaling layer trained on geopolitical questions was replaced by same-domain calibration data.

### 3.8.5 Hypotheses (test window; paired over events; Holm across H1 to H7)

- **H1 (primary).** RPS(pool-eq) $<$ RPS(best single school), the best school chosen on the calibration window.
- **H2.** RPS(pool-eq) $<$ RPS(base): school fine-tuning does not destroy forecasting value.
- **H3.** ECE(pool-cal) $<$ ECE(pool-eq).
- **H4 (information beyond the market).** In the logistic regression
  $\Pr(y = 1) = \sigma\big(a + b_1\,\mathrm{logit}(p_{\text{market}}) + b_2\,\mathrm{logit}(p_{\text{pool-eq}})\big)$
  over binary contracts, with standard errors clustered by event, $b_2 > 0$: the pool carries information the
  market price does not. This is a forecast-encompassing test in the spirit of \citet{clements2010forecast}.
- **H5 (links RQ1 and RQ3).** RPS(pool-eq) $<$ RPS(pool-prompt): fine-tuned schools forecast better than
  prompted schools, not only sound more school-specific.
- **H6 (disagreement as a signal).** Across test events, the mean pairwise Jensen-Shannon divergence among K, A
  and M correlates positively with the pool's RPS (Spearman $> 0$): disagreement among contested frameworks
  flags harder events.
- **H7 (analytic confidence is informative).** Mean RPS is higher for events graded low than for events graded
  high analytic confidence (one-sided permutation test).

Market versus pool is reported descriptively; the market is expected to win. Secondary analyses: with and without
retrieved analogues, the one-day horizon, per-series breakdowns, and school weights by series family. As an
exploratory link to exp06, the agents' internal own-school and other-school masses at forecast time are recorded
and related to disagreement and error.

### 3.8.6 Coherence and coherent aggregation (exp04)

A set of probabilities over related propositions is coherent if and only if it lies in the convex hull of the
admissible outcome vectors \citep{definetti1974theory}; an incoherent set admits a sure loss, and projecting an
incoherent forecast onto the coherent set never increases its Brier score, whatever the outcome
\citep{predd2009coherence}. Consistency checks of this kind have been applied to LLM forecasters on generic questions \citep{paleka2025consistency} and priced as Dutch books \citep{andrews2026dutch}; here they are grounded in arithmetic identities of official statistics.
The main check is **CPI month-on-month versus year-on-year** for the same reference month: with the index levels
for months $m-1$ and $m-12$ known at $t$, each year-on-year bin maps to an interval of month-on-month values
(exact up to published rounding), so the month-on-month forecast implies a year-on-year distribution.
Incoherence is the total-variation distance between the stated and the implied year-on-year distribution. A
second, optional check relates the distribution over each FOMC meeting's decision to the year-end rate ladder,
given the meetings remaining. Each question is asked in a separate prompt, as in exp03, so coherence is not
enforced by shared context.

Systems: K, A, M, pool-eq, base, and the market itself, whose month-on-month and year-on-year ladders at $t$ can
also be incoherent. Measures: incoherence; RPS and Brier before and after Euclidean projection onto the coherent
joint (Dykstra's alternating projections, as in pmpol's coherence module). Hypotheses on exp03's test window:
**H1**, pool-eq is less incoherent than the mean single school; **H2**, projection improves RPS (not guaranteed by
the theorem, unlike Brier, which is reported as a check). Model incoherence versus market incoherence is
descriptive.

### 3.8.7 Prospective forecasting (exp05, optional)

If the exp03 pipeline runs end to end by the go/no-go date, the pipeline is frozen and, every week until the
end of the window, forecasts every open in-universe market closing 3 to 21 days later, with the information set
of exp03; the systems are pool-eq, pool-cal, base, the frontier reference (Claude Opus 5.5) and the market
snapshot at the same minute, optionally with the newest open models as prompted references. Each week's forecasts
are committed to the repository, timestamped and hashed, before the events resolve. Scoring follows exp03 and is
descriptive (30 to 60 events expected; low power); its value is that no model, including the frontier model, can
have seen the answers.

## 3.9 Statistical protocol

All experiments share one protocol, implemented once in the harness and frozen with the registrations.

**Paired design.** Every arm or system answers the same events (or queries), so comparisons are paired. For a
comparison of B against A the unit is the per-event difference $d_i = m_i^{B} - m_i^{A}$ of the metric.
Dependence within an event (for example, several binary contracts of one market, or three schools' answers to
one event) is respected by resampling at the event level.

**Estimation.** The mean difference is reported with a 95% percentile bootstrap interval over events (2,000
resamples, \citealp{efron1993bootstrap}) and with the paired win rate (the fraction of events with
$d_i > 0$).

**Testing.** The $p$-value comes from a sign-flip permutation test over events (10,000 permutations): under the
null of no systematic difference, each $d_i$ is equally likely to have either sign, and the observed
$|\bar d|$ is compared with the permutation distribution of $|\bar d|$. This exact test needs no distributional
assumption beyond exchangeability of the signs. Where a hypothesis is tested once per school or once per
comparison, $p$-values within the family are adjusted with Holm's step-down procedure \citep{holm1979simple},
which controls the family-wise error rate at $\alpha = 0.05$ without assuming independence. Families are
declared in the registrations (for example, exp01 H1 across three schools; exp03 H1 to H7; exp06 S-H1 to S-H3).
Secondary and exploratory analyses are reported with intervals and unadjusted $p$-values and are labelled.

**Noise and honest reporting.** Before any comparison is interpreted, the run-to-run noise of each metric is
estimated by repeating a configuration with another seed on the development set; differences smaller than that
noise are reported as no change. Failures, format errors and invalid samples are reported as prominently as
successes, per system.

**Power.** exp01 has 96 paired events per school; exp03 has hundreds of events in the test window pooled across
series, with per-series counts and intervals reported because single series are small; exp05 is explicitly
under-powered and descriptive. No post hoc power claims are made.

## 3.10 Threats to validity and controls

**Leakage through training data.** The base model's release date fixes the start of the forecasting benchmark;
the seed-episode audit removes trajectories that could carry information from the calibration window; model
inputs are point-in-time vintages; no news or later text is supplied; frontier models whose training covers the
benchmark period are confined to the prospective experiment. The memorisation problem documented for LLM economic forecasts \citep{lopezlira2025memorization} and the look-ahead bias that prompting cannot remove \citep{sarkar2024lookahead} are addressed by design rather than by detection, in line with the no-training-leakage condition that \citet{ludwig2026large} state for the use of language-model predictions in empirical economics.

**Leakage through evaluation.** Held-out sets (the 96 events, the exp03 test window, the exp02 test queries)
are frozen and accessed once by a human at an interactive terminal; the harness refuses test-split commands
from the automated agent, logs every access, and ties every result row to the registration documents, the code
version, the prompts, the lexicons and the adapter hashes in force at the time.

**Teacher bias.** The training trajectories were generated by one teacher model and may carry its biases or
its own reading of each school. Arm T measures the teacher directly when run; the L3 entries and the judge's
definitions are drawn from the schools' canonical literature rather than from the trajectories; and the optional
training-data audit (exp06, Part III) scores each trajectory's school purity with the SAE instrument.

**Measurement validity.** Keyword metrics are validated against a blind judge, the judge against two human
raters, and both against an instrument that reads representations rather than text; acceptance thresholds are
fixed in advance. The judge never scores the model it is.

**Instrument validity (SAEs).** The gate S0, the reader design, the non-SAE baselines, two sparsities, the
replication with an SAE trained on the post-trained model, human-checked labels and the keyword-free probe set
each address a known failure mode of SAE-based analysis (poor transfer, weak baselines, feature instability,
unreliable labels, circularity).

**Dependence and multiplicity.** Event-level resampling and declared families with Holm correction.

**Small samples and single series.** Per-series counts and intervals are reported; the primary test pools
series; the prospective experiment is labelled descriptive.

**Generality.** Three schools, one language, United States releases, one model family (with one cross-family
check as a low-priority option). These limits are stated in Chapter 7 rather than argued away.

## 3.11 Reproducibility, governance and the use of AI

**Registration and freezing.** Each experiment has a registration file whose first commit is its registration
record; amendments are dated and never overwrite. A freeze command records the hashes of the prompts, lexicons,
judge rubric, feature configuration, code and adapters; a run on the test split is refused unless a matching
freeze exists and is logged.

**Caching and provenance.** Every generation is cached under a key that includes the exact model and revision,
the message list, the sampling settings, the chat-template options and the adapter hashes; every score is a row
in an append-only results table with the run identifier, the registration documents and the code version.

**Data and licences.** Market data are reconstructed from contract identifiers and scripts; the episode database
construction pipeline, prompts and scripts are released; the team's pmpol components (ontology, proofs,
confidence, coherence projection, baselines, ground-truth fetchers) are cited as team code with their export
notes. Frontier-model outputs are used for evaluation only, in line with the provider's consumer terms.

**AI assistance.** Automated agents (Claude Code) wrote the experiment harness, ran development-set and
calibration-window work under a fixed protocol with budgets, and produced result tables and factual summaries.
Every substantive contribution is logged in an AI-use ledger from which the thesis's AI-use statement is
written, in accordance with the university's guide on generative AI. Research decisions, interpretations and
the thesis text are the author's; confirmatory results come only from registered, frozen, human-run steps.

**Status of the design (as of 2026-10-31).** exp01 and its amendments 1 to 3 are registered; amendment 4 (new
base model, retrained adapters), exp01b and exp02 to exp06 are drafts that become binding when the author
registers them, which must happen before any score on the respective held-out data. The thesis reports, for
every result, whether it followed a registration in force at the time.
