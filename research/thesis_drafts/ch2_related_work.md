<!--
AI-ASSISTED DRAFT. Written by Claude (Claude Code session, 2026-10-31) at the author's request. Logged in
research/AI_USE_LEDGER.md. PolyU's Student Guide on the Use of GenAI requires AI-generated material to be
identified and the student to be accountable; THESIS_DESIGN §6 says thesis prose is the author's. Treat this
file as a scaffold to be checked and rewritten in the author's own words. Every citation key refers to
research/thesis_drafts/references/*.bib, and CITATION_VERIFICATION.md records the primary source and status of
each key. Descriptions of other systems are from their primary papers as read on 2026-10-31; re-read the papers
before quoting numbers from them, and note the corrections listed in CITATION_VERIFICATION.md (for example,
which 2026 paper says what about arbitrage and coherence).
-->

# 2.x Related work: positioning Macro-MOSAIC

This section places the thesis against the work closest to it. Section 2.x.1 states the criteria for
closeness. Sections 2.x.2 to 2.x.7 take each criterion in turn: systems that reason about macroeconomic events
with several perspectives; language-model forecasting on prediction markets; the comparison of fine-tuning with
prompting as a way of instilling a reasoning style; interpretability studies of what fine-tuning changes;
analogue retrieval; and auditable, layered reasoning. Section 2.x.8 summarises the comparison in a table and
Section 2.x.9 states what the thesis does not claim.

## 2.x.1 Criteria

A piece of work is close to this thesis if it does at least one of the following: (i) analyses macroeconomic
events, as opposed to single securities, with language models; (ii) keeps several theoretical perspectives
apart rather than merging them; (iii) instils a reasoning style by fine-tuning and compares it with prompting;
(iv) retrieves historical analogues by macroeconomic state; (v) evaluates probabilistic forecasts on outcomes
that resolved after the model's training data ends; (vi) checks the logical coherence of a model's
probabilities; (vii) reads a model's internal representations to say what fine-tuning changed. No prior system
does more than two of these at once; the thesis's contribution is the combination, with each component tested
on its own terms.

## 2.x.2 Multi-perspective reasoning about macroeconomic events

**Role-based multi-agent systems for trading.** TradingAgents \citep{xiao2024tradingagents} organises
language-model agents into the roles of a trading firm: fundamental, sentiment, technical and news analysts,
bull and bear researchers who debate, a trader and a risk team. FinCon \citep{yu2024fincon} adds a hierarchical
manager-analyst structure with "conceptual verbal reinforcement" that distils lessons between episodes;
MarketSenseAI 2.0 \citep{fatouros2025marketsenseai} combines retrieval over filings and news with a chain of
agents for equity analysis. These systems share two properties that distinguish them from Macro-MOSAIC. Their
unit of analysis is the individual security and their objective is a trading signal, so macroeconomic
transmission appears, if at all, as one analyst's commentary. And their agents are differentiated by *task*
(what data they read) rather than by *theory* (how they explain the data): the bull and bear researchers argue
opposite positions on the same evidence, but no agent is committed to a framework such as a demand-driven or a
credit-driven account of the cycle. Their evaluation is a backtest on a historical window that lies inside the
training data of the language model used, a concern raised by the memorisation study of
\citet{lopezlira2025memorization} and by the long-run evaluation of LLM strategies in \citet{li2026can}.

**Heterogeneous agents by design.** \citet{xing2025designing} shows, for financial sentiment classification,
that a set of agents built to hold *different* cognitive dispositions and reconciled by debate is more robust
than a single agent; the design principle, heterogeneity before aggregation, is the one this thesis adopts, but
the heterogeneity there is psychological rather than theoretical and the task is classification rather than
causal reasoning. Multi-agent debate in general \citep{du2024improving,liang2024encouraging} improves factual
accuracy by letting agents converge; Macro-MOSAIC does the opposite on purpose. Its three agents are contested
frameworks in the sense of the knowledge-layer ontology (Section 3.3): they are never asked to converge, their
disagreement is preserved in the output, and whether that disagreement predicts error is itself a registered
hypothesis (exp03, H6).

**Agents as economic actors.** EconAgent \citep{li2024econagent} uses language-model agents as households in
a macroeconomic simulation, with perception, memory and decisions about work and consumption, and reproduces
stylised macro facts bottom-up. FOMC In Silico \citep{kazinnik2025fomc} assigns personas of individual Federal
Open Market Committee members, with their dovish or hawkish leanings, to agents that deliberate and vote on the
policy rate. Both are the closest work on macroeconomics with multiple language-model agents, and both differ
from this thesis in the same way: their agents represent *actors* (households, committee members) whose
heterogeneity is a matter of preferences and information, and the object is to reproduce an aggregate outcome
of their interaction. Macro-MOSAIC's agents represent *theories*; the object is to interpret an exogenous event
through each theory and to test whether the theories' pooled probabilities are better than any one of them.
FOMC In Silico is also restricted to one policy variable; the school agents are applied to any macro event and
to any series with an ordered scenario set. Neither prior system fine-tunes its agents, and neither reports a calibration or coherence analysis of their probabilities. Nearest to the forecasting stage are \citet{hansen2025simulating}, who simulate the Survey of Professional Forecasters with language-model personas fed real-time data and reproduce its accuracy and dispersion, and \citet{iadisernia2025prompting}, who find that persona prompting yields homogeneous macroeconomic forecasts with no accuracy gain. The first shows that point-in-time macro inputs suffice for competent language-model macro forecasts; the second shows that prompted heterogeneity is shallow. Neither fine-tunes, neither conditions on an economic theory, and neither is evaluated against prediction markets or for coherence.

**Language models reading macroeconomic text.** A separate line uses language models as instruments for
macroeconomic measurement: classifying Federal Reserve communication as hawkish or dovish
\citep{shah2023trillion,hansen2023can}, generating expectations from news as a substitute for survey beliefs
\citep{bybee2023ghost}, and forecasting inflation from a model's own knowledge \citep{fariaecastro2024artificial}.
These studies ask whether a model's reading of the economy is informative; they do not condition the model on a
theory, and their forecasting evaluations are exposed to the look-ahead problem that the leakage-free window of
Chapter 6 is designed to remove.

## 2.x.3 Language-model forecasting and prediction markets

**Systems.** \citet{halawi2024forecasting} built a retrieval-augmented forecasting system (news retrieval,
reasoning, and ensembling of language models fine-tuned on their own best rationales) and showed that it
approaches the accuracy of a human forecasting crowd on questions from platforms such as Metaculus.
\citet{schoenegger2024wisdom} showed that an ensemble of twelve language models rivals a human crowd and that
exposure to the crowd's median improves individual models. \citet{turtel2025outcome} trained a 14-billion-
parameter model with reinforcement learning on a proper-scoring reward over about one hundred thousand resolved
questions and matched frontier models on calibration and Brier score; \citet{jeen2026training} report a larger-scale application of the same recipe to a 120-billion-parameter open-weight model. These systems are the state of the art in general-purpose
forecasting. They differ from this thesis in three respects. Their questions are heterogeneous binary
propositions about politics, technology and sport; the questions here are the ordered bins of official
macroeconomic releases, where the outcome space is defined by a publication grid (L0), neighbouring bins are
related by arithmetic, and related questions (month-on-month versus year-on-year inflation; a meeting decision
versus the year-end rate) are tied by identities that can be checked. Their forecasters are frontier or
RL-trained models prompted to forecast; the forecasters here are small open models fine-tuned to *reason as a
school*, and the forecasting experiment asks whether that reasoning carries forecasting value (exp03, H2 and
H5) rather than optimising the forecaster for the score. And their training sets are tens of thousands of
questions, which the macro domain cannot supply; the thesis treats outcome-based reinforcement learning as
future work and its benchmark as the seed for it.

**Benchmarks and evaluation.** ForecastBench \citep{karger2025forecastbench} is a dynamic benchmark that
collects questions whose answers are not yet known, from markets and from data series, and compares language
models with superforecasters as the questions resolve; it establishes the leakage-free, forward-looking
evaluation that Chapter 6 adopts in a retrospective form (a window that opens at the base model's release date)
and that exp05 adopts prospectively. KalshiBench \citep{nel2025kalshibench} evaluates the epistemic calibration of language models directly against Kalshi markets, and the Federal Reserve Board has documented the accuracy of Kalshi's macroeconomic markets themselves \citep{diercks2026kalshi}. These benchmarks score frontier models on market questions in general; the thesis
restricts the universe to macroeconomic releases with ordered bins, builds the information set from point-in-time
vintages rather than from news, and uses the market price as a benchmark and as a regressor in an encompassing
test (H4) rather than as an input.

**Consistency and arbitrage.** \citet{paleka2025consistency} showed that language-model forecasters violate
elementary consistency relations (negation, paraphrase, monotonicity, conditional probability) and proposed
arbitrage-based metrics that price the violations; the same group's later catalogue of pitfalls in evaluating language-model forecasters, above all temporal leakage, motivates the strict evaluation windows of Chapter 6 \citep{paleka2026pitfalls}. The approach
descends from de Finetti's coherence criterion \citep{definetti1974theory}, from the result that projecting an
incoherent forecast onto the coherent set never worsens its Brier score \citep{predd2009coherence}, and
from arbitrage-free market making over related contracts \citep{kroer2016arbitrage}; \citet{andrews2026dutch} price the incoherence of language-model forecasts as the guaranteed profit of a Dutch book, and \citet{shi2026combinatorial} construct combinatorial arbitrage portfolios from prices outside the convex hull of admissible payoffs. Chapter 6 applies the same ideas
to relations that are not merely logical but arithmetic (the identities of official statistics), measures the
schools' incoherence and the market's own, and tests whether coherent projection improves the ranked
probability score (exp04).

## 2.x.4 Fine-tuning versus prompting for a reasoning style

Whether to fine-tune a model or to prompt it is a recurring question, and the evidence depends on what is
being instilled. For task accuracy with equal data, fine-tuning and in-context learning generalise comparably
when compared fairly \citep{mosbach2023fewshot}. For *style*, imitation of a stronger model's outputs is known
to be easy: models fine-tuned on a proprietary model's responses acquire its tone and format while gaining
little of its factual accuracy or capability \citep{gudibande2024false}, and a small amount of high-quality
instruction data suffices to shape a model's style \citep{zhou2023lima}. Distillation of reasoning traces from
a large teacher, by contrast, does transfer reasoning ability to small students \citep{ho2023large,
magister2023teaching,hsieh2023distilling}. The Confirmation's panel asked which of these applies to the school
agents: is the measured gain in school consistency a gain in reasoning or in vocabulary? Chapter 4 answers it
with three instruments and a registered comparison against the strongest prompting baseline, including
few-shot demonstrations drawn from the very corpus the adapters were trained on and the base model's own
reasoning mode. The related literature on persona conditioning, in which models simulate demographic or
ideological groups with measurable fidelity and bias \citep{argyle2023out,santurkar2023whose,
shanahan2023role}, frames the agents as role-players of a theory; the thesis's L3 rule makes the role explicit
and measurable, and the keyword-free probe set (Section 3.6.3) tests the role at the level of concepts.

## 2.x.5 What fine-tuning changes inside a model

The interpretability study of Chapter 4 draws on three strands. Sparse autoencoders decompose activations into
interpretable features \citep{bricken2023monosemanticity,huben2024sparse,gao2025scaling}, and suites of
pretrained SAEs now exist for open model families, including Qwen-Scope for the Qwen3 models used here
\citep{deng2026qwenscope}. Model-diffing studies show that narrow fine-tuning leaves readable traces in activation differences even on unrelated text \citep{minder2026narrow}, that character traits induced by fine-tuning move along identifiable "persona" directions, which can be used to screen training data \citep{chen2026persona}, and that diffing SAE features before and after a narrow fine-tune recovers persona features that predict and steer the fine-tuned behaviour \citep{wang2026persona}. And a growing body of negative results shows that SAE features often fail to beat
simple supervised baselines for probing and steering \citep{kantamneni2025sparse,wu2025axbench}, that SAEs do not always transfer across base and chat models \citep{kissane2024saes,galichin2026feature}, that sparse model diffing has artefacts of its own \citep{minder2025overcoming}, and that features are unstable across training runs \citep{paulo2026sparse}. The thesis's position is the one these results recommend: SAEs are used
where supervised baselines cannot help (unsupervised discovery of what an adapter added, and labelled features
mapped to an ontology of the school's concepts), every quantitative claim is paired with a difference-of-means
baseline, the instrument passes a validity gate before use, and results are reported as robust only if they
replicate across sparsities and across an SAE trained on the post-trained model. The closest prior work, \citet{wang2026persona}, diffs SAE features to find the persona a narrow fine-tune instils; no prior work, to the author's knowledge, has used SAE features to compare fine-tuning with few-shot prompting as ways of instilling a *theoretical* perspective, has mapped the features to an ontology of that perspective's concepts, or has validated them against an LLM judge and human raters on the same items.

## 2.x.6 Analogue retrieval by macroeconomic state

Forecasting by analogue, finding past states of a system that resemble the present and reading off what
followed, has a long history in the atmospheric sciences \citep{lorenz1969atmospheric} and an informal one in
macro-financial commentary ("this looks like 1994"). History Rhymes \citep{khanna2025history} is the closest
recent work: it retrieves historical days whose macroeconomic context resembles the current one and uses them
to improve daily single-stock return forecasts. The differences are in the unit, the metric and the use of the
retrieved set. The thesis retrieves discrete *episodes* (events with documented transmission channels and
multi-horizon, multi-asset reactions) rather than daily snapshots; it measures similarity with a Mahalanobis
distance under a shrinkage covariance estimated on the monthly indicator panel \citep{ledoit2004well}, which
accounts for the strong correlation among macro indicators, rather than with a plain concatenation of
standardised features; it enforces point-in-time states built from data vintages \citep{croushore2001realtime}
and trigger-only descriptions so that neither revisions nor hindsight enter the retrieval; and the analogues
feed a causal-reasoning stage rather than a classifier. Chapter 5 tests the metric against the plain
concatenation directly (exp02, H1).

## 2.x.7 Auditable, layered reasoning

The proof-per-forecast and analytic-confidence design (Section 3.3) comes from intelligence-analysis practice
rather than from machine learning: the Intelligence Community's analytic standards require that likelihood and
confidence be expressed separately and that uncertainties be explained \citep{odni2015icd203}, and structured
techniques such as the analysis of competing hypotheses \citep{heuer1999psychology} require alternatives to be
listed and tested. The knowledge-layer ontology and the proof objects are inherited from the research group's
pmpol system (team code). In the language-model literature the nearest ideas are chain-of-thought rationales
\citep{wei2022chain}, which are explanations generated by the model and not checked against sources, and
retrieval-augmented generation, which supplies sources but does not grade them. The thesis's forecasts carry a
typed trail from the conclusion back to rules, vintage-dated facts, analogues and school entries, and the grade
attached to that trail is tested as a predictor of error (exp03, H7).

## 2.x.8 Summary comparison

**Table 2.x.** Closest prior work and Macro-MOSAIC on the criteria of Section 2.x.1. "Yes/No" entries describe
the published system; "partial" means the property holds in a weaker form noted in the text.

| Work | Unit of analysis | Several theoretical perspectives kept apart | Perspective instilled by | State-based analogue retrieval | Outcome-based probabilistic evaluation, leakage-free | Coherence checks | Reads internal representations | Proof and confidence per output |
|---|---|---|---|---|---|---|---|---|
| TradingAgents \citep{xiao2024tradingagents}; FinCon \citep{yu2024fincon} | single securities | No (roles, not theories) | prompting | No | No (backtest inside training data) | No | No | partial (agent transcripts) |
| EconAgent \citep{li2024econagent} | households in a simulated economy | No (actors) | prompting | No | No (stylised facts) | No | No | No |
| FOMC In Silico \citep{kazinnik2025fomc} | the policy rate | partial (individual leanings) | prompting | No | partial | No | No | No |
| Simulated SPF \citep{hansen2025simulating}; persona prompting for macro forecasts \citep{iadisernia2025prompting} | macro series (SPF variables) | partial (forecaster personas) | prompting | No | partial (real-time data; survey comparison) | No | No | No |
| Halawi et al. \citep{halawi2024forecasting}; Turtel et al. \citep{turtel2025outcome} | general forecasting questions | No | fine-tuning / RL for accuracy | No (news retrieval) | Yes | No | No | partial (rationales) |
| ForecastBench \citep{karger2025forecastbench}; KalshiBench \citep{nel2025kalshibench} | general or market questions | n/a (benchmarks) | n/a | No | Yes | No | No | n/a |
| Paleka et al. \citep{paleka2025consistency} | general questions | No | n/a | No | partial | Yes (logical) | No | No |
| History Rhymes \citep{khanna2025history} | daily single-stock returns | No | n/a | Yes (Euclidean on daily snapshots) | partial | No | No | No |
| Minder et al. \citep{minder2026narrow}; persona vectors \citep{chen2026persona} | model internals | n/a | fine-tuning | n/a | n/a | n/a | Yes | n/a |
| **Macro-MOSAIC (this thesis)** | macroeconomic events and releases | Yes (three schools, L3 rule) | fine-tuning, compared with prompting and the thinking mode | Yes (Mahalanobis, shrinkage, point-in-time) | Yes (resolved markets after the model's release; prospective option) | Yes (arithmetic identities; projection) | Yes (SAE instrument with gate and baselines) | Yes (L0–L5 proof; ICD 203 confidence; both tested) |

## 2.x.9 What the thesis does not claim

The thesis does not claim that the three schools exhaust macroeconomic thought, that a school agent is a
faithful substitute for a human economist of that school, or that the system is a trading strategy. It does not
claim that school fine-tuning makes a small model a better general forecaster than a frontier model; the frontier
reference (arm D) and the prospective experiment are there to measure the distance, not to close it. It does not
claim that sparse-autoencoder features are "the" concepts the model uses; they are an instrument whose validity
is tested and whose results are reported with baselines. And it does not claim that the market can be beaten:
the market is the benchmark, and the registered question is whether the pooled schools carry information the
price does not.
