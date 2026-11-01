<!--
AI-ASSISTED DRAFT. Written by Claude (Claude Code session, 2026-10-31; revised 2026-11-01 for the three research
questions adopted that day) at the author's request, from research/THESIS_DESIGN.md,
research/DESIGN_ontology_agents.md, prereg/ and research/prereg_drafts/. Logged in research/AI_USE_LEDGER.md.
PolyU's Student Guide on the Use of GenAI requires AI-generated material to be identified and the student to be
accountable; THESIS_DESIGN §6 says thesis prose is the author's. Treat this file as a scaffold: every sentence
must be read, checked against the registered documents and rewritten in the author's own words before it enters
the thesis. Numbers and settings were copied from the design documents as of 2026-11-01; where a design is still
a DRAFT or a pending decision (amendment 4, exp02 to exp07, the agent arms, D7 to D11, design-note decisions 1 to
7), the text says so and must be updated when the registration is made. Citation keys refer to
research/thesis_drafts/references/*.bib.

Chapter map (THESIS_DESIGN §3): Sections 3.1 to 3.6 and 3.11 to 3.13 are Chapter 3 (design, data and tools);
Sections 3.7 and 3.8 are the method sections of Chapter 4 (RQ1), Section 3.9 of Chapter 5 (RQ2) and Section 3.10
of Chapter 6 (RQ3). They are kept in one file here so that the design can be reviewed as a whole.
-->

# Chapter 3. Research design, data and tools

This chapter sets out the design of the study as a whole. Section 3.1 states the overarching question, the three
research questions that read it from three angles, and the single factorial design they share. Section 3.2 gives
the problem formulation and notation. Section 3.3 describes the epistemic architecture, a knowledge-layer
ontology that types every input and output of the system. Section 3.4 describes the data, Section 3.5 the tools
through which the agents reach rules, point-in-time facts and base rates, and Section 3.6 the ways in which a
framework is instilled in a model. Sections 3.7 to 3.10 give the methods for each research question, each with
its pre-registered or proposed hypotheses. Section 3.11 gives the statistical protocol shared by all
experiments, Section 3.12 the threats to validity and the controls adopted against them, and Section 3.13 the
reproducibility, governance and AI-use arrangements.

## 3.1 One question, three angles, one design

Macro-MOSAIC (Mixture-Of-Schools Analogy-Informed Chains) analyses macroeconomic events with language-model
agents, each committed to one of three contested schools of macroeconomic thought: Keynesian, Austrian and
Monetarist. The thesis asks one overarching question:

> Can language-model agents reason through explicitly contested economic theories in a way that is
> theory-driven inside the model, auditable in what they say, and calibrated in how sure they are?

The three adjectives are the three angles of the thesis, and each is one research question. All three read the
same factorial design (Table 3.1) and the same agents, so that the chapters report one study rather than three.
The design crosses *how the framework is instilled* (prompting, supervised fine-tuning, or training beyond
supervised fine-tuning) with *how the agent works* (a single pass in which the model writes its own tool
observations, as in the Confirmation, or an ontology agent that fetches rules, point-in-time facts and base rates
through real tools and justifies each forecast with a layered proof).

**Table 3.1.** The factorial design (THESIS_DESIGN §2; design note §4a).

| How the framework is instilled | Single pass, self-simulated tools (Confirmation format) | Ontology agent: real L0 to L2 tools, L5 proof |
|---|---|---|
| Prompted | arms A (zero-shot), B (strongest prompting baseline) and D (frontier reference) of exp01 | **A-agent**: base model, framework prompt, tools |
| Fine-tuned (supervised) | arm C of exp01 (school adapter) | **C-agent**: adapter trained on multi-turn tool trajectories, tool results masked from the loss |
| Trained beyond supervised fine-tuning | none | **C-agent+RFT** (rejection-sampling fine-tuning, the main extension) and **C-agent+RL** (stretch) |

Each contrast answers one question. C against A and B asks whether fine-tuning instils the framework (exp01,
registered). A-agent against A, and C-agent against C, ask whether real tools and proofs help. C-agent against
A-agent asks whether fine-tuning still matters once the agent has tools, and the interaction asks whether
fine-tuning and tools are substitutes or complements. The three research questions read the table from three
sides.

**RQ1, inside the model: what it computes (Chapter 4).** Does fine-tuning instil a contested economic framework
beyond the best prompting baseline, and does it change what the model computes (the framework's concepts) or only
what it writes (its vocabulary)? RQ1 reads the *rows* of Table 3.1. Evidence: exp01 (registered and unchanged:
Qwen3-8B; arms A, B, C, the frontier reference D and the optional teacher arm T; keyword metrics, a validated
judge and two human raters); exp06 (a sparse-autoencoder instrument and a mechanism study); exp01b (whether the
advantage survives a stronger 2026 base model, conditional); and the agent arms C-agent and C-agent+RFT,
analysed for fidelity and with the sparse autoencoder as exploratory evidence.

**RQ2, what the agent says: auditable reasoning (Chapter 5).** When framework agents must fetch point-in-time
facts (L1) and historical base rates (L2) through real tools and justify each forecast with a layered proof, is
their reasoning auditable and faithful: are the proofs valid and traceable to L0 to L4, do the conclusions follow
the evidence when it changes, and are the mechanisms a proof claims active inside the model? RQ2 reads the
*columns*. Evidence: exp02 (the L2 tool: macro-state analogies against narrative and naive similarity) and exp07
(new: proof validity and grounding, tool-call validity, counterfactual tool results, proof-step typing and
proof faithfulness inside the model, on development and pre-2025 events only).

**RQ3, how sure: calibrated forecasts (Chapter 6).** Do probability forecasts pooled across contested frameworks
beat single frameworks and other sources of ensemble diversity (personas, multiple models, repeated sampling) on
real macroeconomic outcomes that resolved after the models' training data end; are they calibrated and coherent;
and do their uncertainty signals (disagreement among frameworks, analytic confidence) predict error? RQ3 reads
*every cell* as a forecaster. Evidence: exp03 (resolved prediction markets, 2025 to 2026; hypotheses H1 to H7 and
H8 on sources of diversity, with the agent arms as forecasters), exp04 (coherence) and exp05 (prospective live
forecasting, optional).

The examiner's question about the Confirmation, whether the school agents reason in a school's mechanisms or only
use its words, is answered by three independent instruments that the three angles supply: the layered proof
(what the agent says it used), the judges (a validated LLM judge, and optionally an open decision-model judge)
and sparse-autoencoder features (what the model computes). Their agreement on the same trajectories is itself a
result (Section 3.9.6). Decision models, classifiers that return a probability for each option of a typed
question in one forward pass, are instruments for all three angles rather than a fourth question: a second judge
for RQ1, a proof-step typer for RQ2 and, in the prospective exp05 only, a decision head over scenario bins for
RQ3 (decision D8).

Two features of the design run through every experiment. First, each experiment is **pre-registered**: the
hypotheses, metrics, decision rules and analysis plan are written and committed to the repository before the
held-out data is touched, and later changes are recorded as dated amendments rather than edits
\citep{nosek2018preregistration}. Results that follow the registered plan are reported as confirmatory;
everything else is labelled exploratory. Second, the design is **leakage-aware** throughout: model inputs are
restricted to information available at the forecast time, the forecasting benchmark contains only outcomes
resolved after the base model's release, held-out evaluation sets are frozen and accessed once, and no step of
agent training, filtering or reward ever uses the forecasting test window.

The Confirmation of Registration proposed a fourth stage, cross-asset allocation with a 2023 to 2025 walk-forward
backtest, as the main evidence, and asked one research question per pipeline stage. Both have changed. The
allocation stage has been moved to the discussion chapter (Chapter 7) as an application: the backtest window lies
inside the training period of every candidate model, so a backtest could not separate reasoning from recall
\citep{lopezlira2025memorization}; the number of events in such a window gives no statistical power; and a
benchmark of resolved prediction markets answers the same question without look-ahead. And the three questions
are now angles on one design rather than one question per stage: analogy retrieval, the Confirmation's second
question, becomes the agents' L2 tool and part of RQ2. Two reasons drove the change. The Confirmation's framing
guidance treats the three schools as one instance of a transferable principle, contested frameworks kept apart,
which calls for a wider claim. And reviews of pilot training data found that no tool in the Confirmation design
was ever executed: the teacher model wrote the observations of its own tool calls, so that a student trained on
them learns to invent evidence (Section 3.4.3). Real tools remove that defect and make faithfulness testable.

## 3.2 Problem formulation and notation

Let $e$ denote a macroeconomic event (a data release, a policy decision, a shock) and let $t$ be the time at
which the system reasons about it. The information set at $t$ is $\mathcal{I}_t$, which contains only material
published on or before $t$. The macro state is a vector $s_t \in \mathbb{R}^{35}$ of indicator values *as
published* at $t$ (Section 3.4.2). Frameworks are indexed by $k$; the three trained schools are
$k \in \{K, A, M\}$, and exp03 adds prompted frameworks and other ensemble members (Section 3.10.2).

**Single pass.** In the Confirmation's format a framework agent maps the event to one structured trajectory,

$$
\tau_k(e) = \big[\text{Think},\ \text{ToolCall},\ \text{Observe},\ \ldots,\ \text{Output}\big],
$$

generated in one pass, so that the Observe blocks are written by the model itself.

**Ontology agent.** In the agent format the trajectory is a dialogue between the model and the harness. At each
turn the model either emits a tool call $c_j$ or its final output. The harness executes the call against the
information set, $o_j = \mathrm{tool}(c_j;\, \mathcal{I}_t)$, appends $o_j$ as a tool message and returns control
to the model, up to a budget of $J_{\max}$ calls. The model never writes an observation. Every $o_j$ is a typed
record: its knowledge layer (Section 3.3), an identifier (a rule id, a series with its vintage date, an episode
id), the date it refers to and its value.

**Output.** In both formats the Output block contains (i) a causal chain naming the transmission mechanisms that
connect the event to intermediate effects and to asset impacts, (ii) a probability distribution
$p_k = (p_{k1}, \ldots, p_{kJ})$ over $J$ mutually exclusive scenarios, and (iii) directional signals (long,
short, neutral, with a conviction grade) for the major asset classes. In the agent format the causal chain is a
*proof* $\pi_k = (\sigma_1, \ldots, \sigma_n)$ whose steps $\sigma_i = (\ell_i, \text{text}_i, \text{ref}_i,
\text{as\_of}_i, \text{inputs}_i)$ carry a layer $\ell_i \in \{\mathrm{L0}, \ldots, \mathrm{L5}\}$, a reference
that should resolve to a tool result or a knowledge-base entry, the date the step refers to, and the steps it is
derived from.

In the forecasting setting of Chapter 6 the scenarios are the ordered bins $B_1 < \cdots < B_J$ of a published
statistic (for example, month-on-month CPI in steps of 0.1 percentage points), the outcome is the bin
$y \in \{1, \ldots, J\}$ that the official release falls into, and the pooled forecast is

$$
\bar p = \sum_k w_k\, p_k, \qquad \sum_k w_k = 1,\; w_k \ge 0,
$$

a linear opinion pool \citep{stone1961opinion,ranjan2010combining}, optionally followed by a calibration map
$g_\theta$ fitted on a calibration window (Section 3.10.4) and by a projection onto the set of probability vectors
that are logically coherent across related questions (Section 3.10.6).

The L2 tool maps a query state $s_t$ to the $k$ nearest historical episodes under a distance $d(s_t, s_i)$ over
the pool of episodes with trigger dates before $t$; on its own, it predicts the asset reactions to $e$ as the
similarity-weighted mean of the analogues' recorded reactions (Section 3.9.1).

Three families of outcome are measured, one per angle. *School fidelity* (RQ1) is measured on text and inside
the model: keyword-based consistency and contamination, judged fidelity on a rubric, and feature-based
consistency from a sparse autoencoder. *Auditability and faithfulness* (RQ2) are measured on proofs and tool
calls: structural validity, grounding, resolution of references, agreement of cited values with tool results,
tool-call validity, sensitivity to counterfactual tool results, and the activation of the claimed mechanisms'
features; the retrieval utility of the L2 tool is measured by the directional accuracy and rank correlation of
analogue-implied reactions. *Forecast quality* (RQ3) is measured by strictly proper scoring rules
\citep{gneiting2007strictly}: the ranked probability score for ordered bins, the logarithmic score, the Brier
score and expected calibration error on binary contracts, and by coherence distances across related questions.

## 3.3 Epistemic architecture: knowledge layers, proofs and analytic confidence

Every input and output of the system is assigned to one of six knowledge layers. The layering is taken from
pmpol, the research group's prediction-market analysis system (team code; cited as such throughout). In the
sense of knowledge engineering it is an ontology, an explicit specification of the kinds of thing the system
reasons about \citep{gruber1993translation}: it distinguishes facts by how they are known and how far they can
be trusted in inference, and it is what the tools, the proofs and the confidence grades are typed by. Table 3.2
gives the mapping to Macro-MOSAIC.

**Table 3.2.** Knowledge layers (L0 to L5), their role in Macro-MOSAIC and how the agents reach them.

| Layer | Content in Macro-MOSAIC | Reached through | Rule in inference |
|---|---|---|---|
| L0 Institutional rules | Release definitions and publication grids (CPI to 0.1 pp; FOMC target range in 25 bp steps); market resolution rules | `get_rules` | Hard constraints: they define scenario sets and the coherence checks of exp04 |
| L1 Point-in-time facts | The 35 indicators *as published* at $t$ (ALFRED vintages), with the period each value refers to and the date it became available | `get_macro_data` | The only facts a model may see; revised data are never used as inputs |
| L2 Base rates | Analogue episodes (exp02); the historical distribution of each series; venue calibration | `query_episode_db` | Priors and baselines |
| L3 Contested frameworks | The three schools, recorded as knowledge-base entries (`kb/L3/schools.yaml`) with drivers, frictions, policy prescriptions and typical signals, and with sources; optionally further frameworks (Section 3.10.2) | the agent's own framework | Cited, not adopted: one agent per framework; outputs shown side by side; no stage selects a winner silently |
| L4 Market observations | Kalshi and Polymarket prices at $t$ | never | Benchmark only; never a model input |
| L5 Inferences | Each framework's distribution; the pools; the retrieval scores | written by the agent | Must carry a proof that traces back to L0 to L4 |

The L3 rule is the design principle behind the multi-framework architecture: frameworks that contradict one
another are recorded with their sources and shown in parallel rather than merged into one "consensus" model. The
three schools were chosen because they make structurally different causal claims about the same event
(aggregate demand and multipliers; credit-driven distortion of the structure of production; money growth and
its lags), because each is represented in current policy and market discourse, and because each has a canonical
literature from which the school's definition, the judge's rubric and the lexicons can be drawn (Chapter 4 gives
the design rationale and sources). The L3 entries are a single source for everything that defines a school: the
agents' system prompts, the judge's definitions, the probe paragraphs and the fields to which sparse-autoencoder
features are mapped (Section 3.8.3).

**Facts and their status.** Each knowledge-base entry records its source with a verbatim quote, a source grade
on the two-character scale of NATO doctrine, the Admiralty Code (reliability of the source,
credibility of the information; \citealp{ukmod2023jdp200}) and a review status (proposed, reviewed or disputed), and becomes reviewed only after
a second person has checked source and quote. An L3 entry is recorded as an *attribution*, "school $S$ holds that
$X$", which can be checked against the school's canonical texts, rather than as the contested claim $X$ itself:
the review establishes that the entry describes the school faithfully, not that the school is right. The
contestedness of $X$ is expressed by the layer, not by the status, so that citing a reviewed school entry does not
by itself lower a forecast's analytic confidence (below). Who reviews the entries is decision D9.

**Proof per forecast.** Every L5 output is accompanied by a proof object in pmpol's format: an ordered list of
steps, each tagged with its layer, its kind (data, rule, match, logic or caveat), its reference (a
knowledge-base fact id, a data series and vintage, an episode id, or a school entry), the date it refers to and
the steps it is derived from; a list of competing hypotheses with a verdict on each, in the manner of the analysis
of competing hypotheses \citep{heuer1999psychology}, which is where the other frameworks' readings of the same
event are recorded; and generation metadata. The derivation links follow the W3C provenance model
\citep{lebo2013prov}, to which a proof can be exported. The plain-language summary of a forecast is generated from
the proof and from nothing else, so that the text cannot claim more than the chain supports. pmpol supplies two
checks: a structural check (valid layers and kinds, unique step identifiers, inputs that exist, a source and a
time on every L4 step) and a grounding test (the conclusion traces back, through the derivation links, to at least
one step of layers L0 to L4). Both are necessary but not sufficient for RQ2: the grounding test counts an L3 step
as grounding, and neither checks that a reference resolves to a result the agent actually received, that a cited
value equals that result, or that the cited date lies before $t$. exp07 adds these checks (Section 3.9.2).

**Analytic confidence.** Following the analytic standards of the United States Intelligence Community (ICD 203)
\citep{odni2015icd203}, the probability of an outcome and the confidence in the judgement are kept on separate
axes. Probabilities are reported numerically and with the ICD 203 likelihood words, a practice that goes back to
\citet{kent1964words}. Confidence (high, moderate, low) is read from the proof as its weakest link, with pmpol's
assessment rules: an incomplete L1 input, a weak analogue, a framework output that failed to parse, an unclear or
unverified L0 resolution rule, or a cited knowledge-base fact that is unreviewed or disputed each lower the grade,
and every downgrade is stated as a reason. Disagreement among the frameworks is deliberately *not* part of the
grade, because it is tested separately as a predictor of error (exp03, H6); confidence is tested in the same way
(H7). Both tests turn the architecture's claims about interpretability and trust into falsifiable statements.

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
author, and the original narratives are retained to measure the size of the hindsight effect (Chapter 5). Until
the database is in the repository, the L2 tool serves a vetted table of named, dated episodes before 2025, and
every result produced with it is labelled as such.

### 3.4.2 Point-in-time macro states

The macro state at any time $t$ is the vector of the 35 indicators as published on or before $t$, constructed
from ALFRED vintages with the bitemporal convention of pmpol: each value carries the period it refers to (its
valid time) and the date it became available (its publication time), which the thesis maps onto the distinction temporal databases draw
between valid time and transaction time \citep{snodgrass1985taxonomy}. The same construction supplies the L1 tool
and the model inputs of the forecasting experiments, so that a forecast made "as of $t$" never sees a value
released after $t$ or a later revision of a value released before $t$. The monthly panel of standardised
indicators, from the earliest common date to $t$, is also the sample on which the covariance matrix of the L2 tool
is estimated (Section 3.9.1).

### 3.4.3 Training data: single-pass and agent trajectories

**Single-pass trajectories (arm C of exp01).** The school adapters of exp01 are trained on synthetic agent
trajectories in the Confirmation's format: 500 per school, built from 107 abstract event templates in 14
categories, each instantiated with randomised macro snapshots so that the model learns a reasoning pattern rather
than event-specific answers. Each trajectory follows the format Think, ToolCall (episode-database query),
Observe, Think, ToolCall (macro data), Observe, Think, Output. The Confirmation's trajectories were produced by a
teacher model (GPT-4o) prompted with the school's definition and the seed material of the 117 interpreted
episodes. Whether those trajectories can be recovered, or must be regenerated, is decision D11: if they cannot,
they are regenerated from the same seeds with a teacher whose licence permits training on its outputs, with
format, leakage and quality filters fixed before generation, and the thesis says so (amendment 4, Change 5,
draft). Either way, every trajectory is audited for its seed episode's date: trajectories whose seed episode
falls after 2025-04-30 are removed before training, because the same adapters forecast outcomes from May 2025
onwards (amendment 4, Change 6, draft). The number removed per school is reported with the training-data card.

The regeneration prompt was piloted before any full run, and the pilot generations were scored blind on school
fidelity, causal coherence, responsiveness to the event, consistency of the output and factual hygiene by LLM
reviewers used for evaluation only. The reviews led to two revisions of the prompt and to one structural finding:
the teacher writes the results of its own tool calls, so that a model trained on single-pass trajectories learns
to produce plausible but invented observations. For exp01, which is registered on the single-pass format, this is
a stated limitation. For the agent arms it is removed by design.

**Agent trajectories (C-agent).** The agent adapters are trained on multi-turn trajectories in the tool format of
Section 3.5, generated by a teacher with a fourth version of the prompt (design note §4): the harness executes the
teacher's tool calls and injects the results (L1 from the point-in-time context, L2 from the episode table), the
teacher writes only its own turns, and the Output is a layered proof. In training, the loss is computed on the
agent's own turns only, so that the tool results are context the model conditions on and never text it learns to
produce, the masking used in agent fine-tuning \citep{zeng2024agenttuning,gou2024tora} and in reinforcement
learning with retrieved content \citep{jin2025searchr1}. The same seed-date audit applies, and the trajectories
of the rejection-sampling rounds (Section 3.6.4) are logged with their data and seed.

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
touched once, after registration. The data card records 149 questions built from 3,757 settled markets, 51 in
the calibration window and 98 in the test window, with the exclusions and the context coverage; no forecast on
the test window is scored before registration. Kalshi's terms do not permit redistribution of compiled market
data, so the data-availability statement lists contract identifiers and the reconstruction scripts rather than
the data.

### 3.4.6 Events for the faithfulness study (exp07)

exp07 needs no outcomes, so it runs on development events and on historical episodes with trigger dates before
2025 only, and never touches the exp01 test events or the exp03 test window. Its labelled data are of two kinds,
both produced before the study is registered: about 300 proof steps typed by hand (layer and L3 field), the gold
standard for the proof-step typer, and the counterfactual edits of Section 3.9.4, fixed in advance per event.

## 3.5 The L0 to L2 tools and the agent loop

The ontology agent works in the interleaved reason-and-act pattern of tool-using language models
\citep{yao2023react,schick2023toolformer}: it reasons, calls a tool, reads the result and continues. What is
specific to this design is that each tool returns facts of exactly one knowledge layer, as of the forecast time,
with an identifier the proof must cite; retrieval of this kind grounds generation in a corpus the model does not
have to memorise \citep{lewis2020retrieval}, and here the corpus is typed and time-stamped. Three tools are
exposed (design note §3):

- **`get_rules(event)`** returns the L0 rules of the event: the release definition, the publication grid and
  rounding, the step size of a policy rate, and the market resolution rule, from pmpol's proposition ontology.
- **`get_macro_data(names)`** returns the L1 values of the named series known at $t$, each with its reference
  period and its publication date (Section 3.4.2).
- **`query_episode_db(query)`** returns L2 evidence: the nearest historical episodes to the current state under
  the exp02 retriever frozen at that time, with their identifiers, trigger dates, similarity scores and recorded
  reactions, and the historical distribution of a series.

The harness owns the loop. It parses each call against a JSON schema, refuses any request for data after $t$,
executes valid calls, appends the typed result as a tool message, and stops after $J_{\max}$ calls or when the
agent writes its Output. Invalid, refused and redundant calls are recorded rather than repaired, because
tool-call validity is an outcome of RQ2 (Section 3.9.3) and because tool-using models are known to write invalid
or hallucinated calls \citep{patil2024gorilla,patil2025bfcl} and to misjudge whether a task can be solved with the
tools they have \citep{zhang2024toolbehonest}. The same loop serves training
(the teacher of Section 3.4.3), inference (A-agent, C-agent and their trained variants) and the counterfactual
tests of exp07, which replace one tool result with an edited one (Section 3.9.4).

## 3.6 How a framework is instilled

### 3.6.1 Base model

All open-weight arms run on Qwen3-8B, a dense, post-trained model released on 2025-04-29 under the Apache-2.0
licence \citep{yang2025qwen3}. It replaces the Confirmation's Qwen2.5-7B-Instruct for three reasons: public
sparse autoencoders exist for every one of its layers (Section 3.8), which the interpretability work needs; its
release date leaves about eighteen months of resolved markets outside its training data; and it is one model
generation newer in the same size class, so the change is one of generation, not of scale (scale is studied
separately in exp01b). The model is run in non-thinking mode (chat template with `enable_thinking = false`) in
both training and inference for arms A and C and for the agent arms, so that the trained trajectory is the only
reasoning the model writes; arm B may switch the thinking mode on (Section 3.7.1). The Hugging Face revision is
pinned at freeze.

### 3.6.2 Prompting

The prompted arms condition the base model on the framework's L3 entry through the system prompt. Arm A (zero
shot) and arm B (the strongest prompting baseline, with demonstrations drawn from the school's own training
corpus and the model's thinking mode as a tuned option) are the single-pass arms of exp01 (Section 3.7.1).
A-agent gives the base model the same framework prompt, the tools and the agent output format. The prompted
frameworks and personas of exp03 are defined in the same way (Section 3.10.2).

### 3.6.3 Supervised fine-tuning

One low-rank adapter \citep{hu2022lora} is trained per school with the recipe in Table 3.3, once, and never tuned
on development or test events; the same recipe trains the agent adapters on the agent trajectories. The recipe
keeps the Confirmation's rank, scaling and epochs and fixes the settings the Confirmation did not report.
Quantised training (QLoRA, \citealp{dettmers2023qlora}) is dropped in favour of bf16 weights, which removes a
quantisation step and matches the larger model of exp01b, for which 4-bit training is not recommended.

**Table 3.3.** LoRA recipe (amendment 4, Change 2, draft).

| Setting | Value |
|---|---|
| Data | 500 trajectories per school minus the seed-episode exclusions (agent adapters: the agent trajectories) |
| Rank, scaling, dropout | $r = 32$, $\alpha = 64$, 0.05 |
| Target modules | all linear projections of the attention and MLP blocks |
| Precision | bf16 weights |
| Schedule | 3 epochs; learning rate $2 \times 10^{-4}$, cosine decay, 3% warm-up; effective batch 16; maximum length 4,096 tokens |
| Loss | assistant tokens only (agent adapters: the agent's own turns; tool results masked) |
| Seed | 20261030 |

The freeze record stores the SHA-256 of every adapter file, and the generation cache key includes them, so that
outputs of an earlier adapter can never be reused for a retrained one.

### 3.6.4 Rejection-sampling fine-tuning

Supervised fine-tuning imitates the teacher. The main extension trains the agent on its own successful
behaviour: the supervised agent samples $k$ trajectories per event, the trajectories that pass verifiable checks
are kept, and the adapter is fine-tuned again on them, for one or two rounds. This is rejection-sampling
fine-tuning in the sense of STaR and its successors \citep{zelikman2022star,yuan2023scaling,singh2024beyond},
applied to tool-using trajectories as in \citet{gou2024tora}. The
filters are rule-based or come from realised outcomes, never from a language-model judgement: the proof passes
the structural, grounding, resolution and value checks of Section 3.9.2; every tool call is well formed; the
scenario probabilities respect the L0 grid; and, on historical episodes before 2025, the signalled direction of
the asset reaction agrees with the reaction recorded in the episode database. The events are development events
and pre-2025 episodes; the exp03 test window is never used for sampling, filtering or reward. Each round is logged
with its data, filters, acceptance rates and seed. The resulting arm is C-agent+RFT.

### 3.6.5 Reinforcement learning with verifiable rewards (stretch)

A stretch arm, C-agent+RL, trains the agent in the tool environment with a policy-gradient method of the GRPO
family \citep{shao2024deepseekmath,guo2025deepseekr1}, with rewards that can be computed by rule, the setting
called reinforcement learning with verifiable rewards \citep{lambert2025tulu3}, extended to multi-turn tool use
\citep{jin2025searchr1,qian2025toolrl}: proof validity, format, and a proper scoring rule on resolved historical
outcomes, the reward used by outcome-based training of forecasters \citep{turtel2025outcome}; open libraries
support the multi-turn setting \citep{vonwerra2020trl,sheng2025hybridflow}. Outcome data are the
binding limit: the episode database has 141 episodes, and the exp03 calibration window is reserved for
calibration. Full outcome-based reinforcement learning, which published systems ran on tens of thousands of
resolved questions, therefore stays future work. The depth of agent training (supervised only; with rejection
sampling, as recommended; or with reinforcement learning as well) is design-note decision 7.

## 3.7 RQ1, inside the model: fine-tuning versus prompting (exp01, exp01b)

### 3.7.1 Arms

All arms answer the same events with the same user template and, for A, B and C, the same sampling settings
(temperature 0.7, top-p 0.9, at most 2,048 answer tokens, fixed seed). exp01 and its registration are unchanged by
the 2026-11-01 redesign.

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
- **Arm T (teacher, optional).** The teacher that generated the training trajectories (GPT-4o for the
  Confirmation's trajectories; the regeneration teacher otherwise, decision D11), with the messages of arm A,
  run only if budget allows. T answers the question "why not use the teacher directly?"; if T is not run, the
  thesis says so.
- **Arms A7 and C7 (optional, descriptive).** If the original trajectories are available, the Confirmation's
  model (Qwen2.5-7B-Instruct) is run with arm A's messages and with adapters retrained by the Confirmation's own
  recipe, on the same 96 events, and compared with the Confirmation's Table 4.3 to link Chapter 4 to the
  Confirmation.

Arms whose inputs are fixed by the registration (A, C, D, T) may have their test outputs *generated* before the
freeze by a human-gated command that writes only to the generation cache, computes no score and logs the access;
nobody reads those outputs before the freeze, and the official run reads them back from the cache (amendment
3). Arm B cannot be pre-generated because its configuration is tuned on the development set.

### 3.7.2 Text-level metrics

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

### 3.7.3 Judged fidelity and its validation

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
- **Second, open judge (decision D8).** If adopted, an open decision model answers the same rubric as a typed
  question and returns a probability for each score level in one forward pass, which makes the judgement
  reproducible and its uncertainty readable. It is validated against the Opus judge and the two human raters on
  the same items, and its outputs, like the machine feature labels of Section 3.8.3, are proposals that never
  approve a fact. Vendor calibration claims are measured, not quoted.

### 3.7.4 Hypotheses and decision rules (registered)

Tests are paired over the 96 events (Section 3.11).

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
for at least two schools, this is reported as a negative result and the school-agent stage is re-examined.

### 3.7.5 Replication on a stronger base (exp01b, conditional)

A stronger 2026 base model prompts better, so the fine-tuning advantage may shrink. exp01b repeats arms A, B
and C with the same trajectories, recipe, tuning budget, events and metrics on Qwen3.5-27B \citep{qwen2026qwen35}
(released 2026-02-24, Apache-2.0; 64 layers, three in four of them linear-attention layers), the only 2026 open
model with a public sparse autoencoder trained on the post-trained model itself. The primary hypothesis is
exp01's H1; the interaction (whether the C minus B gap is smaller on the larger model) is reported with a
confidence interval and no test claim. The experiment proceeds only if a feasibility spike (bf16 LoRA on the
hybrid architecture, served with the adapter) succeeds (decision D7); otherwise the thesis keeps an 8B-only RQ1
and reports the reason.

### 3.7.6 Agent arms (exploratory)

The agent arms of Table 3.1 are scored for school fidelity with the same metrics, judge and sparse-autoencoder
instrument on development events, as exploratory evidence for RQ1: whether an adapter trained on agent
trajectories, and then on its own filtered trajectories, keeps the school fidelity of arm C once its reasoning is
anchored in tool results. The question is not registered, because the agent arms are trained after the exp01
freeze; it links the rows of Table 3.1 to its columns.

## 3.8 RQ1, inside the model: the sparse-autoencoder instrument (exp06, draft)

### 3.8.1 Purpose

Keyword scores and judged scores are both read off the text. A third instrument reads the model's internal
representations, for two purposes: *measurement*, a score of school fidelity at the level of concepts rather
than words, validated against the judge and the human raters; and *mechanism*, a description of what
fine-tuning adds relative to prompting (the school's concepts, the output format, or style) and whether
fine-tuning separates the schools internally more than few-shot prompting does. An optional third part asks
whether the identified features are causally used. The same frozen instrument serves RQ2 by checking whether
the mechanisms a proof step claims are active on that step's tokens (Section 3.9.6). The scope of exp06 is
decision D10.

### 3.8.2 Sparse autoencoders and the validity gate

A sparse autoencoder (SAE) decomposes a residual-stream activation $x \in \mathbb{R}^d$ into a sparse code over
a wide dictionary of directions \citep{bricken2023monosemanticity,huben2024sparse}. The thesis uses the
Qwen-Scope SAEs released for Qwen3-8B (TopK encoders \citep{gao2025scaling}, 65,536 features, every one of the
36 layers, at two sparsities, $L_0 = 50$ and $100$) and, for the replication, the Qwen3.5-27B SAEs (81,920
features, 64 layers). With $z = \mathrm{TopK}(W_{\text{enc}}\, x + b_{\text{enc}})$ and
$\hat x = W_{\text{dec}}\, z + b_{\text{dec}}$, each feature $f$ has an activation $a_f(x) = z_f$ and a decoder
direction $W_{\text{dec},f}$. No SAE is trained for the thesis.

The Qwen3-8B SAEs were trained on the *base* model and on pre-training text. Chat formatting and LoRA adaptation
shift activations, and SAEs do not always transfer across such shifts \citep{kissane2024saes,galichin2026feature},
so a **validity gate (S0)** is run before anything else, for each *state* of the model (the reader,
Section 3.8.3; arm A; arm B; arm C) and every fourth layer, on development and probe data only. Two quantities
are computed on response tokens: the fraction of variance unexplained by the reconstruction,

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

### 3.8.3 Probe sets, feature selection and feature cards

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
held-out contexts, \citealp{paulo2025automatically}); because such scores do not by themselves separate
meaningful features from those of a random network \citep{heap2026automated}, the author checks thirty labels at
random and labels are never used as evidence on their own. Labels are mapped to a field of the L3 entry or to
format, style or other. The resulting **feature cards** are the thesis's main display of what the agents'
internal school concepts are, and the field mapping is what the proof-faithfulness analysis of Section 3.9.6
uses.

### 3.8.4 Scores and baseline

For a text $x$ and school $s$, averaged over the analysis layers,

$$
\mathrm{mass}_s(x) = \frac{1}{Z_s}\,\frac{1}{|x|}\sum_{t \in x}\sum_{f \in F_s} a_f(x_t), \qquad
\mathrm{FC}_s(x) = \frac{\mathrm{mass}_s(x)}{\sum_{s'} \mathrm{mass}_{s'}(x)}, \qquad
\text{feature contamination}_s(x) = \sum_{s' \ne s} \mathrm{mass}_{s'}(x),
$$

where $Z_s$ normalises by the mean mass on school $s$'s probe documents; $\mathrm{FC}^{\text{kf}}$ and
contamination$^{\text{kf}}$ use $F^{\text{kf}}$. Because SAE-based methods have repeatedly failed to beat simple
supervised baselines \citep{kantamneni2025sparse,wu2025axbench}, every quantitative claim is paired with a
non-SAE baseline computed on the same probe data: a difference-of-means school direction $d_s$, scored as the
projection margin. The feature lists, normalisers, layers and SAE variant are written to a configuration file and
locked with the exp01 freeze; Part I is then computed on the cached outputs of every exp01 arm, including D and T,
because the reader can read any text.

### 3.8.5 Mechanism (Part II)

The cached test outputs of arms A, B and C are fed back through the model that generated them (base plus
school prompt; plus exemplars; plus adapter), teacher-forced, so that the activations equal those during
generation and nothing is re-sampled. On response tokens at the analysis layers the **internal** own-school and
other-school masses (the frozen $F_s$) and the difference-of-means projections are recorded. As an exploratory
model-diffing analysis, the mean activation difference C minus A on development events and on the neutral
corpus (narrow fine-tunes leave readable traces even on unrelated text, \citealp{minder2026narrow}) is decomposed
into the thirty SAE features with the largest change, labelled and classified as own-school concept, other-school
concept, format, economics-generic or other; the same is done for the exemplar effect B minus A. The
decomposition is read with the known artefacts of sparse model diffing in mind
\citep{minder2025overcoming,wang2026persona}, and with the caveat that low-rank adapters change representations
differently from full fine-tuning \citep{shuttleworth2025lora}.

### 3.8.6 Hypotheses (registered with Part I)

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

## 3.9 RQ2, what the agent says: grounded and faithful reasoning (exp02, exp07)

RQ2 asks two things of the agent's explanation: that it is *auditable*, meaning that every step can be checked
against a source the reader can inspect, and that it is *faithful*, meaning that it reflects what actually drove
the forecast rather than a plausible story written alongside it. The literature separates the two: an
explanation can be plausible to a reader without being faithful to the model's computation
\citep{jacovi2020towards}; chains of thought can omit factors that demonstrably changed the answer
\citep{turpin2023language}, and models differ widely in how much their answers depend on the chain they wrote
\citep{lanham2023measuring}. Auditability is tested by checking proofs against the tool
results the harness logged; faithfulness is tested by intervention, on the tool results (behaviour) and inside
the model (features). Section 3.9.1 validates the L2 tool itself; Sections 3.9.2 to 3.9.6 describe exp07, which
is a design to be registered before it runs (backlog priority P1).

### 3.9.1 The L2 tool: structural analogy retrieval (exp02, draft)

The analogues an agent cites are only as good as the retriever that supplies them, so exp02 validates the L2
evidence before any proof cites it. Its protocol is unchanged by the redesign; its retriever, frozen at the
registration, becomes `query_episode_db`.

**Distance and covariance.** The structural channel measures the distance between the query state $s_t$ and each
candidate episode's point-in-time state $s_i$ by the Mahalanobis distance \citep{mahalanobis1936generalised}

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

**Protocol.** Queries are processed in date order. The candidate pool for query $q$ is every episode with a
trigger date strictly before $q$'s, and $\Sigma_t$ uses only data up to $q$'s date, so that no retrieval looks
ahead. Methods compared: structural (Mahalanobis); Euclidean distance on standardised indicators (the plain
concatenation used by History Rhymes, \citealp{khanna2025history}); semantic (cosine on trigger-only
descriptions); hybrid; and the baselines unconditional pool mean, same-category mean and random $k$. The
prediction for each instrument and horizon is the similarity-weighted mean of the top-$k$ analogues' recorded
reactions ($k = 5$ by default). The hyper-parameters ($\alpha$, $k \in \{3, 5, 10\}$, kernel bandwidth) are tuned
on development queries (trigger date before 2005-01-01) only; test queries have trigger dates from 2005-01-01.

**Metrics and hypotheses.** Per query, the directional hit rate over available instrument-horizon cells (primary)
and the Spearman correlation between predicted and realised reactions (secondary), averaged over queries and
compared pairwise over test queries with sign-flip permutation tests and Holm correction across H1 to H3:

- **H1.** Structural $>$ Euclidean (hit rate).
- **H2.** Hybrid $>$ semantic-only.
- **H3.** The best analogy method $>$ the unconditional pool mean.

Two descriptive comparisons measure leakage: point-in-time versus revised states, and trigger-only versus
original narratives. A large gain from the original narratives is evidence of hindsight leakage in narrative
retrieval and is reported as such.

### 3.9.2 Proof validity and grounding (exp07)

Every proof produced by an agent arm on the exp07 events is checked against the harness's log of the tool calls
and results of the same trajectory. Five properties are measured per proof and per step:

1. **Structure**: pmpol's structural check passes (Section 3.3).
2. **Grounding**: the conclusion traces back to at least one step of layers L0 to L4; reported both with pmpol's
   definition and with a stricter one that excludes L3, so that a conclusion resting only on the agent's own
   framework is not counted as grounded in evidence.
3. **Resolution**: the reference of every L0 to L2 step names a result the agent actually received in this
   trajectory, or a reviewed knowledge-base entry.
4. **Value agreement**: every number a data step states equals, up to published rounding, the value in the
   result it cites.
5. **Time**: every date a step cites lies on or before $t$.

A step fails resolution if it cites evidence the agent never fetched, which is the behaviour the single-pass
trajectories train (Section 3.4.3); the single-pass arms are therefore scored on the same properties as a
reference, with their self-written observations treated as unresolved. These checks are the agent-level analogue
of attribution evaluation in text generation, where each statement is checked against the source it is
attributed to \citep{rashkin2023measuring,gao2023enabling}.

### 3.9.3 Tool-call validity

For each trajectory: the share of calls that parse against the schema, the share that execute, the share refused
by the time guard, the share of redundant calls (repeating an earlier call), and whether the series and episode
queries are relevant to the event (judged by rule: the requested series belong to the event's family or to the
L3 entry's typical signals). Reliability is reported over repeated runs of the same event, because tool agents
that succeed once often fail on a repeat \citep{yao2025taubench}; the evaluation of call validity by structure
rather than by text follows function-calling benchmarks \citep{patil2024gorilla,patil2025bfcl}.

### 3.9.4 Counterfactual tool results

Real tools make a behavioural test of faithfulness possible. Each agent is re-run on each exp07 event with one
tool result edited: one L1 value moved by a fixed number of grid steps in a direction specified in advance, or
one L2 analogue replaced by an episode with the opposite recorded reaction. A grounded agent changes the steps
that depend on the edited fact and moves its forecast in the direction the edit implies; an agent that ignores
its tools does not. The measures are the shift of the forecast distribution (the change in its mean bin and the
Jensen-Shannon divergence between the original and the edited forecast), the share of dependent steps that
change, and the sign agreement with the direction implied by the framework's L3 entry. Two controls separate
faithfulness from noise: the same event re-run with no edit (sampling variation), and an edit of a value the
original proof did not cite (which should change little). Intervening on the input and checking whether the
explanation reflects what changed the prediction is the logic of counterfactual faithfulness tests for natural
language explanations \citep{atanasova2023faithfulness,matton2025walk}, of context attribution by ablation
\citep{cohenwang2024contextcite} and of intervention studies of language-model agents \citep{zhao2026agents}; here
the intervention is on evidence the harness controls, so the counterfactual is exact.

### 3.9.5 Proof-step typing

Auditing proofs at scale needs a typer: a classifier that assigns each step a layer and, for L3 steps, the field
of the school's entry it invokes (drivers, frictions, policy, typical signals). If decision D8 is adopted, an open
decision model types each step as a typed question with a probability per option, so that ungrounded or mistyped
steps are flagged automatically; it is validated against about 300 hand-typed steps (Section 3.4.6) with
chance-corrected agreement and per-class accuracy, and it is used only to read text. The decision models whose
training data cover 2025 to 2026 never forecast the exp03 test window.

### 3.9.6 Proof faithfulness inside the model

When a proof step claims a mechanism of the school's L3 entry (for example, the fiscal multiplier as a Keynesian
driver), are the sparse-autoencoder features mapped to that field active on that step's tokens? With the frozen
reader, features and field mapping of exp06 (Section 3.8.3), and with teacher forcing so that the activations are
those of generation, three quantities are computed per typed step: the mass of the claimed field's features, the
mass of the school's other fields, and the mass of the other schools' features (internal contamination). Each is
compared with the same quantity on steps of other types and with the difference-of-means baseline. A causal
version, patching or ablating the claimed field's features and measuring the change in the forecast, follows
established activation-patching practice \citep{zhang2024towards} and sparse feature circuits
\citep{marks2025sparse}, and is optional; the closest precedent verifies each step of a chain of thought through the
attribution graph of its computation \citep{zhao2026verifying}. The analysis then compares three views of the same trajectory: what the
proof says the agent used, what the features show, and what the judges score. Agreement across the three answers
the question whether the agent reasons in the school's mechanisms or only uses its words with instruments that do
not share their failure modes.

### 3.9.7 Candidate hypotheses (exp07, to be registered)

The following are proposals for the registration, not registered hypotheses; their wording, tests and families
are fixed when exp07 is registered, before it runs.

- **E-H1 (grounding).** The share of proofs that pass the structure, strict grounding, resolution, value and time
  checks is higher for C-agent than for A-agent, and higher for C-agent+RFT than for C-agent.
- **E-H2 (counterfactual faithfulness).** For each agent arm, the forecast shift after an edit of a cited fact
  exceeds the shift after an edit of an uncited fact and the shift with no edit.
- **E-H3 (mechanisms inside).** On steps typed as invoking an L3 field, the mass of that field's features exceeds
  its mass on steps of other types.
- **E-H4 (fine-tuning with tools).** C-agent's school fidelity (Section 3.7.6) is not lower than arm C's, so that
  grounding in tools does not cost the framework.

## 3.10 RQ3, how sure: calibrated, coherent forecasts (exp03 to exp05)

### 3.10.1 Information set and generation

For each event the forecast time is $t$ = seven days before the market's close (one day as a secondary horizon).
The information set contains the event description (series, reference period, release date, the scenario set
in canonical wording), the point-in-time macro context (the 35 indicators as published on or before $t$ and the
target series' latest published values), and, except in the no-retrieval ablation, the top-three analogues from
the episode database with trigger dates before $t$, chosen by the retrieval method frozen at that time. Single-pass
systems receive this information in the prompt; agent systems receive the event description and fetch the rest
through the tools, under the same time guard. No news, no market prices and no text written after $t$ are
supplied.

Each system is sampled three times per event (temperature 0.7, top-p 0.9). Per sample the probabilities are
parsed per bin and renormalised if their sum lies in $[0.8, 1.2]$; otherwise the sample is invalid. The system's
forecast is the mean of the valid samples. An event with no valid sample receives the uniform forecast and
counts as a format failure, which is reported per system; the uniform fallback penalises format failure in the
scores rather than hiding it.

### 3.10.2 Systems and sources of diversity

**Table 3.4.** Systems compared in exp03 (agent arms and diversity sources to be added to the registration).

| System | Description |
|---|---|
| base | Qwen3-8B, non-thinking, school-neutral system prompt |
| K, A, M | each school adapter with its school system prompt |
| K$'$, A$'$, M$'$ | the base model with each school's system prompt, no adapter (prompted schools) |
| agent arms | A-agent, C-agent and C-agent+RFT per school, if trained by the cut-off date named in the registration |
| pool-eq | equal-weight linear pool of K, A, M |
| pool-prompt | equal-weight linear pool of K$'$, A$'$, M$'$ |
| pool-skill | weights $w_k \propto \exp(-\lambda\, \overline{\mathrm{RPS}}_k)$ estimated on the calibration window, $\lambda$ chosen there |
| pool-cal | pool-eq after temperature scaling fitted on the calibration window |
| diversity pools (H8) | equal-size pools whose members differ by another source of diversity (below) |
| uniform | equal probability on every bin |
| history | the empirical point-in-time distribution of the series' historical changes (pmpol baseline) |
| market | Kalshi prices at $t$ (daily close), normalised over bins; a benchmark, not a competitor to beat |

**Sources of diversity (H8).** The value of a pool comes from the diversity of its members' errors
\citep{krogh1994neural,wood2023unified}, and there are cheaper ways to obtain diversity than training three
adapters. exp03 therefore compares pools of equal size, three members each sampled the same number of times,
whose members differ by: the trained schools (pool-eq); the prompted schools (pool-prompt); prompted agents that
reason with one of pmpol's quantitative L3 frameworks, such as the Sahm rule, the New York Fed's yield-curve
probit or the OECD leading-indicator phases (design-note decision 2); three personas that differ in role and
background but not in economic theory \citep{hu2024quantifying,iadisernia2025prompting}; three open models of
similar size from different developers, each released before the resolution window opens, so that none has seen
the outcomes; and repeated sampling of one model \citep{wang2023selfconsistency,lyu2025calibrating}. Ensembles of
different language models can rival human crowds \citep{schoenegger2024wisdom}, but the errors of different models
are correlated \citep{kim2025correlated}, which is why the comparison is empirical; and it is made at equal size
because the best composition of a forecasting group depends on its size \citep{lamberson2012optimal}. The repeated-sampling pool also controls for
the number of samples: the three-school pool averages three times as many samples as one school, and averaging
alone improves proper scores.

Frontier API models are not evaluated on the historical windows, because their training data covers 2025 to
2026; they appear only in the prospective exp05. Qwen3.5-27B, if exp01b runs, enters as a secondary descriptive
analysis on test events resolving on or after 2026-03-01.

### 3.10.3 Scores

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

### 3.10.4 Pooling and calibration

The equal-weight linear pool is the registered primary aggregate: it needs no estimation, and linear pools of
calibrated forecasts are in general under-confident rather than over-confident, which the calibration map can
correct \citep{ranjan2010combining}. Two estimated variants are compared with it. Skill weighting uses the
calibration-window RPS of each school with a softmax temperature $\lambda$. Temperature scaling
\citep{guo2017calibration} rescales the pooled log-probabilities by a single parameter $T$ fitted by minimising
the logarithmic score on the calibration window; with one parameter it cannot reorder bins, so it corrects
over- or under-confidence without changing what the pool believes most likely. The Confirmation's plan for
regime-conditional weights was dropped because regime cells would be nearly empty in a leakage-free window;
its Platt-scaling layer trained on geopolitical questions was replaced by same-domain calibration data. The pool is
an L5 summary: every output shows the per-framework distributions beside it, with their proofs and confidence
grades, and the pool never replaces them.

### 3.10.5 Hypotheses

On the test window, paired over events. H1 to H7 are as drafted in the exp03 registration document; H8 is to be
added before registration, with its comparisons and its place in the Holm family.

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
  flags harder events, in the way that disagreement among macroeconomic forecasters is a component of their
  forecast uncertainty \citep{lahiri2010measuring} and disagreement among repeated samples of one model flags
  wrong answers \citep{farquhar2024detecting}.
- **H7 (analytic confidence is informative).** Mean RPS is higher for events graded low than for events graded
  high analytic confidence (one-sided permutation test).
- **H8 (theoretical diversity, draft).** At equal ensemble size, the pool of the trained schools has a lower RPS
  than the pool of each other source of diversity of Section 3.10.2.

Market versus pool is reported descriptively; the market is expected to win. Secondary analyses: with and without
retrieved analogues, single pass against agent systems, the one-day horizon, per-series breakdowns, and school
weights by series family. As an exploratory link to exp06, the agents' internal own-school and other-school
masses at forecast time are recorded and related to disagreement and error. If the agent arms are not trained by
the cut-off date the registration names, exp03 runs without them, and RQ2 rests on exp02 and exp07.

### 3.10.6 Coherence and coherent aggregation (exp04)

A set of probabilities over related propositions is coherent if and only if it lies in the convex hull of the
admissible outcome vectors \citep{definetti1974theory}; an incoherent set admits a sure loss, and projecting an
incoherent forecast onto the coherent set never increases its Brier score, whatever the outcome
\citep{predd2009coherence}. Consistency checks of this kind have been applied to LLM forecasters on generic
questions \citep{paleka2025consistency} and priced as Dutch books \citep{andrews2026dutch}; here they are grounded
in arithmetic identities of official statistics, which the proposition ontology records as L0 relations. The main
check is **CPI month-on-month versus year-on-year** for the same reference month: with the index levels for months
$m-1$ and $m-12$ known at $t$, each year-on-year bin maps to an interval of month-on-month values (exact up to
published rounding), so the month-on-month forecast implies a year-on-year distribution. Incoherence is the
total-variation distance between the stated and the implied year-on-year distribution. A second, optional check
relates the distribution over each FOMC meeting's decision to the year-end rate ladder, given the meetings
remaining. Each question is asked in a separate prompt, as in exp03, so coherence is not enforced by shared
context.

Systems: K, A, M, pool-eq, base, and the market itself, whose month-on-month and year-on-year ladders at $t$ can
also be incoherent. Measures: incoherence; RPS and Brier before and after Euclidean projection onto the coherent
joint (Dykstra's alternating projections, as in pmpol's coherence module). Hypotheses on exp03's test window:
**H1**, pool-eq is less incoherent than the mean single school; **H2**, projection improves RPS (not guaranteed by
the theorem, unlike Brier, which is reported as a check). Model incoherence versus market incoherence is
descriptive.

### 3.10.7 Prospective forecasting (exp05, optional)

If the exp03 pipeline runs end to end by the go/no-go date, the pipeline is frozen and, every week until the
end of the window, forecasts every open in-universe market closing 3 to 21 days later, with the information set
of exp03; the systems are pool-eq, pool-cal, base, the frontier reference (Claude Opus 5.5) and the market
snapshot at the same minute, optionally with the newest open models as prompted references and, if D8 is adopted,
a decision head that returns a probability per scenario bin in one forward pass. Each week's forecasts are
committed to the repository, timestamped and hashed, before the events resolve. Scoring follows exp03 and is
descriptive (30 to 60 events expected; low power); its value is that no model, including the frontier model and
the decision models, can have seen the answers.

## 3.11 Statistical protocol

All experiments share one protocol, implemented once in the harness and frozen with the registrations.

**Paired design.** Every arm or system answers the same events (or queries), so comparisons are paired. For a
comparison of B against A the unit is the per-event difference $d_i = m_i^{B} - m_i^{A}$ of the metric.
Dependence within an event (for example, several binary contracts of one market, three schools' answers to one
event, or the original and edited runs of one exp07 event) is respected by resampling at the event level.

**Estimation.** The mean difference is reported with a 95% percentile bootstrap interval over events (2,000
resamples, \citealp{efron1993bootstrap}) and with the paired win rate (the fraction of events with
$d_i > 0$).

**Testing.** The $p$-value comes from a sign-flip permutation test over events (10,000 permutations): under the
null of no systematic difference, each $d_i$ is equally likely to have either sign, and the observed
$|\bar d|$ is compared with the permutation distribution of $|\bar d|$. This exact test needs no distributional
assumption beyond exchangeability of the signs. Where a hypothesis is tested once per school or once per
comparison, $p$-values within the family are adjusted with Holm's step-down procedure \citep{holm1979simple},
which controls the family-wise error rate at $\alpha = 0.05$ without assuming independence. Families are
declared in the registrations (for example, exp01 H1 across three schools; exp03 H1 to H7, with H8 to be placed;
exp06 S-H1 to S-H3; exp07 when registered). Secondary and exploratory analyses are reported with intervals and
unadjusted $p$-values and are labelled.

**Noise and honest reporting.** Before any comparison is interpreted, the run-to-run noise of each metric is
estimated by repeating a configuration with another seed on the development set; differences smaller than that
noise are reported as no change. Failures, format errors, invalid samples and invalid tool calls are reported as
prominently as successes, per system.

**Power.** exp01 has 96 paired events per school. exp03 has 98 questions in the test window, pooled across
series, with per-series counts and intervals reported because single series are small; with a family of eight
hypotheses, only moderate effects can be detected, which is why the primary hypothesis is fixed in advance and
the minimum detectable effect is estimated on the calibration window before registration. exp07's power is set
by the number of development and pre-2025 events and of edits per event. exp05 is explicitly under-powered and
descriptive. No post hoc power claims are made.

## 3.12 Threats to validity and controls

**Leakage through training data.** The base model's release date fixes the start of the forecasting benchmark;
the seed-episode audit removes trajectories that could carry information from the calibration window; model
inputs and tool results are point-in-time vintages; no news or later text is supplied; frontier models whose
training covers the benchmark period, and decision models that know 2025 to 2026, are confined to the prospective
experiment or to reading text; agent training, filtering and reward never use the test window. The memorisation
problem documented for LLM economic forecasts \citep{lopezlira2025memorization} and the look-ahead bias that
prompting cannot remove \citep{sarkar2024lookahead} are addressed by design rather than by detection, in line with
the no-training-leakage condition that \citet{ludwig2026large} state for the use of language-model predictions in
empirical economics.

**Leakage through evaluation.** Held-out sets (the 96 events, the exp03 test window, the exp02 test queries)
are frozen and accessed once by a human at an interactive terminal; the harness refuses test-split commands
from the automated agent, logs every access, and ties every result row to the registration documents, the code
version, the prompts, the lexicons and the adapter hashes in force at the time.

**Self-simulated tools in the registered arms.** exp01 keeps the Confirmation's single-pass format for
comparability, so its trajectories contain observations the model wrote itself. This is stated as a limitation of
RQ1's evidence, and it is measured rather than assumed: the single-pass arms are scored on the resolution checks of
exp07 as a reference (Section 3.9.2).

**Teacher bias.** The training trajectories were generated by one teacher model and may carry its biases or
its own reading of each school. Arm T measures the teacher directly when run; the L3 entries and the judge's
definitions are drawn from the schools' canonical literature rather than from the trajectories; and the optional
training-data audit (exp06, Part III) scores each trajectory's school purity with the SAE instrument.

**Gaming of filters and rewards.** Rejection sampling and reinforcement learning optimise whatever the filters
reward. The filters are rule-based checks that a proof cannot satisfy without fetching and citing the evidence,
the realised-direction filter uses pre-2025 outcomes only, and every round reports what it kept and rejected.

**Measurement validity.** Keyword metrics are validated against a blind judge, the judge against two human
raters, and both against an instrument that reads representations rather than text; the proof-step typer is
validated against hand-typed steps; acceptance thresholds are fixed in advance. The judge never scores the model
it is.

**Instrument validity (SAEs).** The gate S0, the reader design, the non-SAE baselines, two sparsities, the
replication with an SAE trained on the post-trained model, human-checked labels and the keyword-free probe set
each address a known failure mode of SAE-based analysis (poor transfer, weak baselines, feature instability,
unreliable labels, circularity).

**Diversity arms that match the schools.** Persona, multi-model or sampling pools may forecast as well as the
schools. That is a result, not a failure: H8 is open by design and is reported whichever way it falls.

**Dependence and multiplicity.** Event-level resampling and declared families with Holm correction.

**Small samples and single series.** Per-series counts and intervals are reported; the primary test pools
series; the prospective experiment is labelled descriptive.

**Generality.** Three schools, one language, United States releases, one model family for the trained arms (with
other families only as ensemble members and as a low-priority cross-family check). These limits are stated in
Chapter 7 rather than argued away.

## 3.13 Reproducibility, governance and the use of AI

**Registration and freezing.** Each experiment has a registration file whose first commit is its registration
record; amendments are dated and never overwrite. A freeze command records the hashes of the prompts, lexicons,
judge rubric, feature configuration, code and adapters; a run on the test split is refused unless a matching
freeze exists and is logged.

**Caching and provenance.** Every generation is cached under a key that includes the exact model and revision,
the message list, the sampling settings, the chat-template options and the adapter hashes; every tool call and
result of an agent trajectory is logged with the trajectory; every score is a row in an append-only results table
with the run identifier, the registration documents and the code version.

**Data and licences.** Market data are reconstructed from contract identifiers and scripts; the episode database
construction pipeline, prompts and scripts are released; the team's pmpol components (ontology, proofs,
confidence, coherence projection, baselines, ground-truth fetchers, knowledge-base format) are cited as team code
with their export notes. Frontier-model outputs are used for evaluation only, in line with the provider's consumer
terms, and no reward or filter in agent training uses them.

**AI assistance.** Automated agents (Claude Code) wrote the experiment harness, ran development-set and
calibration-window work under a fixed protocol with budgets, and produced result tables and factual summaries.
Every substantive contribution is logged in an AI-use ledger from which the thesis's AI-use statement is
written, in accordance with the university's guide on generative AI. Research decisions, interpretations and
the thesis text are the author's; confirmatory results come only from registered, frozen, human-run steps.

**Status of the design (as of 2026-11-01).** The three research questions were adopted on 2026-11-01. exp01 and its
amendments 1 to 3 are registered and unchanged; amendment 4 (new base model, retrained adapters, training data),
exp01b and exp02 to exp06 are drafts; exp07 and the H8 and agent-arm additions to exp03 are still to be drafted;
the tool layer is the priority before the exp03 registration; design-note decisions 1 to 7 and decisions D7 to
D11 are open. Each draft becomes binding when the author registers it, which must happen before any score on the
respective held-out data. The thesis reports, for every result, whether it followed a registration in force at
the time.
