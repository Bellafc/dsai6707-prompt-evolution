<!--
AI-ASSISTED DRAFT. Written by Claude (Claude Code session, 2026-10-31) at the author's request. Logged in
research/AI_USE_LEDGER.md. PolyU's Student Guide on the Use of GenAI requires AI-generated material to be
identified and the student to be accountable; THESIS_DESIGN §6 says thesis prose is the author's. Treat this
file as a scaffold: read every paragraph against the cited paper, then rewrite it in your own words. Every
citation key refers to research/thesis_drafts/references/*.bib; CITATION_VERIFICATION.md records, for each key,
the primary source it was checked against and its status (no key in this file is unverified; eleven entries
carried over from the Confirmation bibliography are marked as not re-fetched). Where this chapter condenses the
Confirmation report's survey (Chapter 2 of the report), the Confirmation is the source and its citations are
reused. Descriptions of papers are from their abstracts and primary pages as read on 2026-10-31; re-read a paper
before quoting any number from it.
-->

# Chapter 2. Background and literature

## 2.1 Scope and organisation

The thesis sits at the meeting point of four literatures that rarely cite one another: the history and
methodology of macroeconomic thought, which supplies the three "schools" the system reasons with; the
engineering of large language models (LLMs) as agents and the methods for adapting them to a task or a persona;
the statistics of probabilistic forecasting, its scoring, calibration, combination and coherence; and the
evaluation of forecasts against prediction markets and human forecasters. A fifth, younger literature on the
interpretability of language models supplies the instrument with which Chapter 4 looks inside the school
agents. This chapter reviews each in turn, at the depth the design decisions of Chapter 3 require, and closes
with the gaps the thesis addresses. The survey of LLM agents in finance written for the Confirmation of
Registration (its Chapter 2) is condensed in Section 2.3; the reader is referred to it for the full taxonomy of
agent architectures and application domains. Section 2.x (Related work) then positions the thesis against the
closest individual systems.

## 2.2 Schools of macroeconomic thought as contested frameworks

Macroeconomics has never had one theory. Its history is usually told as a succession of schools, each a
research programme with its own view of what drives output and prices, which frictions matter, and what policy
should do \citep{snowdon2005modern}. Mankiw's account of the macroeconomist as "scientist and engineer"
\citep{mankiw2006macroeconomist} makes the point that the schools were shaped as much by the policy problems of
their decades as by evidence, and that the present synthesis is a settlement rather than a resolution. The
thesis takes this plurality as a design fact: when a model is asked to interpret a macroeconomic event, there is
no single correct theory to instil, and a system that silently adopts one is making a choice its users cannot
see. The three schools chosen, Keynesian (including New Keynesian), Monetarist and Austrian, were selected
because their causal accounts of the same event differ structurally, because each remains visible in policy and
market discourse, and because each has a canonical literature from which a definition can be drawn.

### 2.2.1 Keynesian and New Keynesian economics

Keynes's *General Theory* \citep{keynes1936general} located the determination of output and employment in
aggregate (effective) demand, argued that an economy could settle at an equilibrium with involuntary
unemployment, introduced the multiplier and the marginal propensity to consume, treated investment as driven by
expectations and "animal spirits", and gave a theory of interest as the reward for parting with liquidity.
Hicks's IS-LM diagram \citep{hicks1937mr} became the textbook reduction of these ideas and the vehicle for
the demand-management policies of the post-war decades. The New Keynesian programme rebuilt the demand-driven
account on explicit microfoundations with nominal rigidities: monopolistically competitive firms that adjust
prices infrequently, a forward-looking Phillips curve, and a central bank that sets the policy rate by a rule
\citep{clarida1999science,woodford2003interest,gali2015monetary}. In that framework output responds to demand
shocks in the short run because prices are sticky, the output gap and inflation expectations are the central
state variables, forward guidance works through expectations, and the zero lower bound restores a modern form of
the liquidity trap. For the school agent, the operational content is: demand determines output in the short
run; sticky prices and wages; the multiplier, counter-cyclical stabilisation and forward guidance as policy
levers; and the output gap, the unemployment gap and demand shocks as the signals to read.

### 2.2.2 Monetarism

Friedman restated the quantity theory as a theory of the demand for money \citep{friedman1956quantity} and,
with Schwartz, read a century of United States monetary history as evidence that money growth drives nominal
income and that the Great Contraction was a failure of monetary policy \citep{friedman1963monetary}. Two
further claims define the school for present purposes. Monetary policy acts with "long and variable" lags
\citep{friedman1961lag}, so discretionary fine-tuning is as likely to destabilise as to stabilise. And there is
a natural rate of unemployment to which the economy returns: the Phillips curve is vertical in the long run,
monetary policy cannot peg real variables, and the central bank should therefore follow a stable rule for the
growth of a monetary aggregate \citep{friedman1968role}. The operational content for the agent: money growth
drives nominal income with stable velocity; long and variable lags; output returns to its natural rate; rules
rather than discretion; and money-supply growth, velocity and inflation expectations as the signals.

### 2.2.3 Austrian business cycle theory

The Austrian account of the cycle, developed by Mises \citep{mises1934theory}, first published in German in 1912, and Hayek \citep{hayek1931prices} and restated in modern capital-theoretic form by Garrison \citep{garrison2001time},
is a theory of intertemporal discoordination. Credit expansion that holds the market rate of interest below the
rate consistent with saving preferences (the "natural" rate) distorts the time structure of production:
resources are drawn into longer, more capital-intensive processes that the economy's saving cannot sustain
(malinvestment); the boom is this misallocation, the bust its liquidation, and policy that props up the boom
delays the correction. Because new money enters the economy at particular points, relative prices and the
distribution of income change before the price level does (Cantillon effects), which is why the school reads
credit growth, the term structure and the relative prices of capital goods and consumer goods as its signals,
and why it prescribes sound money rather than stimulus. The school is heterodox and much less represented in
central-bank research than the other two, a fact that matters for a language model: the Confirmation found, for the earlier base model, that spontaneous use of Austrian concepts was far rarer than use of Keynesian ones, which makes the Austrian adapter the clearest test of whether fine-tuning can instil a framework the model does not already speak (Chapter 4).

### 2.2.4 Transmission channels and the comparability of the schools

What the schools disagree about is transmission: by which channels an event moves output, prices and asset
values. The monetary-transmission taxonomy of \citet{mishkin1996channels}, with its interest-rate, exchange-rate,
asset-price and credit channels, is the common vocabulary in which the three accounts can be compared, and it is
the taxonomy behind the 19 channel labels of the episode database (Section 3.4.1). The point for the system's
design is that the schools make *different* causal claims about the *same* channels (a rate cut is a demand
stimulus, a monetary injection with a lag, or a distortion of the structure of production), so that keeping
them apart yields genuinely different causal chains, and pooling them is a test of whether their errors offset.
The ensemble argument that motivates pooling is reviewed in Section 2.6.3; whether it holds for these three
schools is an empirical question the thesis answers rather than assumes.

## 2.3 Language-model agents in finance and economics

### 2.3.1 From reinforcement learning to language-model agents

An agent perceives its environment, keeps state and acts to achieve goals \citep{wooldridge1995intelligent,
russell2010artificial}. In finance the agent paradigm arrived first through deep reinforcement learning, in
which trading policies are learned by interaction with a simulated market \citep{hambly2023recent}, with open
libraries such as FinRL standardising environments and algorithms \citep{liu2022finrl,liu2022finrlmeta}. The
second wave uses a language model as the reasoning engine: numerical, textual and sometimes visual inputs are
rendered as prompts, and the model reasons in natural language before acting \citep{yang2023fingpt,
zhang2024finagent}. Surveys organise this literature by architecture (memory-augmented, tool-augmented,
reflective and multi-agent designs) and by application (trading, portfolio management, risk, analysis and
advice, compliance) \citep{ding2024large,nie2024survey,dong2025large}. The Confirmation's survey followed the
same two-dimensional taxonomy; three of its findings bear on this thesis. Memory and retrieval are the
components most often credited with handling regime change, because they let an agent recall analogous
situations \citep{yu2023finmem,zhang2024finagent}. Multi-agent systems improve robustness by assigning roles
and by structured disagreement, from the bull-and-bear debate of TradingAgents \citep{xiao2024tradingagents}
to the information-distilling hierarchy of FinCon \citep{yu2024fincon} and the heterogeneous agents of
\citet{xing2025designing}. And evaluation is the field's weak point: most systems report backtests whose windows
lie inside the language model's training data, on proprietary models, with incomparable cost assumptions
\citep{li2026can}.

### 2.3.2 Language models and the macroeconomy

Work that applies language models to macroeconomics rather than to securities is sparser and divides into
three uses. As a *measurement instrument*, language models classify the stance of central-bank communication:
\citet{shah2023trillion} built a labelled corpus of Federal Reserve communications and a hawkish-dovish measure
that moves markets, and \citet{hansen2023can} showed that a general-purpose model classifies the stance of Federal Reserve statements with accuracy approaching that of trained human readers. As a *source of beliefs*, \citet{bybee2023ghost} generated expectations from
historical news with a language model and found them to resemble survey expectations, including their biases;
\citet{fariaecastro2024artificial} asked a language model to forecast inflation and compared it with the
Survey of Professional Forecasters. As a *simulated economy*, EconAgent \citep{li2024econagent} populated a
macroeconomic model with language-model households and reproduced stylised facts, and FOMC In Silico
\citep{kazinnik2025fomc} simulated the deliberation and vote of a committee of persona agents. Closest to the thesis's forecasting stage, \citet{hansen2025simulating} gave language-model forecaster personas the real-time macroeconomic data available at each survey date and reproduced both the accuracy and the dispersion of the Survey of Professional Forecasters, and \citet{iadisernia2025prompting} found that, for macroeconomic forecasts, persona prompts bring no accuracy gain and produce homogeneous forecasts, which is the clearest published motivation for instilling viewpoints by fine-tuning rather than by prompting. The first
econometric cautions have arrived with the applications: \citet{lopezlira2023can} showed that a frontier model
reading headlines can produce return-predictive signals, and \citet{lopezlira2025memorization} then showed that
the same models reproduce economic outcomes from their training period from memory, so that any forecasting evaluation inside the training window is uninterpretable; look-ahead bias in language-model return forecasts has been tested directly, with the conclusion that prompting cannot remove it and only training data that end before the evaluation period can \citep{glasserman2024assessing,sarkar2024lookahead}; and \citet{ludwig2026large} formalise the two conditions under which language-model outputs can be used in empirical economics, no training leakage for prediction and a validation sample for measurement, which the thesis's design meets with its post-release evaluation window and its human-validated judge. Two gaps are visible. None of these systems
conditions the model on an explicit economic theory, so a model's reading of the economy is an undifferentiated
blend of what its corpus contained. And none evaluates probabilistic forecasts of macroeconomic outcomes on a
window that is provably outside the model's training data.

### 2.3.3 Evaluation: benchmarks, backtests and leakage

Benchmarks for financial language models test reading comprehension, numerical reasoning and question
answering over documents \citep{xie2024finben,islam2023financebench}; benchmarks of economic *reasoning*
test sequential logic \citep{quan2024econlogicqa} and causal relations \citep{lee2025econcausal}. None scores a
model's probability forecasts of macroeconomic outcomes. The alternative, a backtest of trading signals,
answers a different question and suffers from look-ahead, survivorship and non-stationarity
\citep{lopezdeprado2018advances}; with language models it suffers in addition from memorisation of the test
period \citep{lopezlira2025memorization}. The thesis therefore takes its outcome-based evaluation from a
different literature, the forecasting of resolvable questions on prediction markets (Section 2.7), and ties the
evaluation window to the release date of the model under test.

## 2.4 Adapting language models to a reasoning style

The school agents must reason *as* a school. There are two broad ways to make a language model do this:
condition it at inference time (prompting) or change its weights (fine-tuning). The literature on each is
large; this section reviews what is known about their relative merits for instilling a style of reasoning, as
opposed to a task skill.

### 2.4.1 Prompting: demonstrations, chains of thought and roles

Large models learn in context: a few demonstrations in the prompt condition the model on a task without
gradient updates \citep{brown2020language}, and the mechanism and its limits have been surveyed extensively
\citep{dong2024survey}. Chain-of-thought prompting, which asks the model to write intermediate reasoning
steps, improves performance on multi-step problems \citep{wei2022chain}, even with no demonstrations at all
\citep{kojima2022large}. A system prompt that assigns a role conditions the model's persona; dialogue agents are
best understood as role-players sampling from a space of characters the training corpus contains
\citep{shanahan2023role}, and whether a given role prompt helps is an empirical matter
\citep{zheng2024helpful}. Recent open models add a native reasoning ("thinking") mode in which the model writes
an extended, hidden chain of thought before its answer; Qwen3 unifies thinking and non-thinking modes in one
model with a controllable thinking budget \citep{yang2025qwen3}. For the thesis this matters in two ways. The
strongest prompting baseline must include demonstrations, a chain of thought and the model's own thinking
mode, or the comparison with fine-tuning is unfair (Section 3.5.3). And the role-play framing predicts a
specific failure: a model told to "be an Austrian economist" will produce the *surface* of the role as its
corpus represents it, which for a thinly represented school may be little more than a few catchwords.

### 2.4.2 Parameter-efficient fine-tuning

Low-rank adaptation (LoRA) freezes the pre-trained weights and trains a low-rank update to selected weight
matrices, which reduces trainable parameters by orders of magnitude without loss on downstream tasks
\citep{hu2022lora}; QLoRA trains such adapters on a 4-bit quantised base, bringing a 7B model within a single
consumer GPU \citep{dettmers2023qlora}. Adapters can be served alongside the base model and switched per
request, which is what makes "one adapter per school" cheap at inference. The Confirmation trained its
adapters with QLoRA; the thesis trains them in bf16 (Section 3.5.2), because the quantisation step is no longer
needed on the hardware used and because 4-bit training is not recommended for the larger model of exp01b.

### 2.4.3 Distillation from a teacher's reasoning traces

The school agents are trained on synthetic trajectories written by a stronger teacher model. This is knowledge
distillation \citep{hinton2015distilling} in its "symbolic" form, in which the teacher's *outputs* rather than
its soft labels are the training signal \citep{west2022symbolic}. A series of studies showed that chain-of-
thought traces from a large teacher transfer reasoning to small students: fine-tuning on teacher rationales
\citep{ho2023large,magister2023teaching}, and using rationales as an auxiliary training signal with less data
\citep{hsieh2023distilling}. Instruction data generated by a model from seed tasks \citep{wang2023selfinstruct,
taori2023stanford} and explanation traces from a frontier model \citep{mukherjee2023orca} became the standard
recipe for aligning open models. Two cautions from the same literature frame the thesis's central question.
\citet{gudibande2024false} found that models fine-tuned to imitate a proprietary model's outputs acquire its
*style* (format, tone, confidence) while gaining little of its factual accuracy or capability, so that human
raters are fooled and targeted evaluations are not; and \citet{zhou2023lima} argued that alignment data mainly
teach format and style, the "superficial alignment hypothesis". The sharpest form of that view is
\citet{lin2024unlocking}, who aligned an untuned base model with three stylistic in-context examples and showed,
token by token, that alignment tuning mostly changes stylistic tokens such as discourse markers and
disclaimers; and \citet{ren2024learning} found that instruction fine-tuning does not teach a model new world
knowledge and works best when its examples agree with what the model already knows. If fine-tuning on school trajectories teaches
only the school's vocabulary and format, the gain in keyword consistency reported at the Confirmation would be
real but shallow. Chapter 4 is built to tell the difference: it validates the keyword metric against a blind
judge and human raters, and it reads the model's representations with features that separate the schools on
keyword-free text.

### 2.4.4 Fine-tuning versus in-context learning

Direct comparisons are fewer than the volume of either literature suggests. \citet{mosbach2023fewshot}
compared few-shot fine-tuning and in-context learning on the same models and data and found that, compared
fairly, fine-tuning generalises out of distribution as well as or better than in-context learning, with the
difference depending on model size and the number of examples. For instruction following, \citet{zhao2025incontext} found that in-context alignment lags instruction fine-tuning and plateaus after a few dozen demonstrations, and \citet{confavreux2026comparing} characterised in-context learning and fine-tuning as distinct learning algorithms with different inductive biases and representations. For role-play specifically, \citet{wang2024rolellm} compared role-conditioned
instruction tuning of open models with role prompting of a frontier model on a role-play benchmark, the
closest existing analogue of the arm B versus arm C comparison. The comparison in Chapter 4 differs from this
and from most of the literature in three ways: the quantity instilled is a *perspective* rather than a task
label; the prompting baseline is given the same demonstrations the adapter was trained on, plus the model's
reasoning mode; and the outcome is measured by three instruments, text, judge and representations, rather than
by accuracy alone.

### 2.4.5 Persona fidelity

Whether a language model can faithfully hold a viewpoint not its own has been studied for demographic and
political personas. \citet{argyle2023out} found that a model conditioned on a person's background reproduces
the distribution of that group's survey answers with "algorithmic fidelity"; \citet{santurkar2023whose} found
that models' default opinions align with particular demographic groups and that steering towards other groups
is only partly successful; \citet{salewski2023incontext} found that impersonation changes a model's measured
abilities and reveals its biases; \citet{hu2024quantifying} quantified the persona effect and found that
persona variables explain only a small share of the variance in human judgements and shift model predictions
modestly. These results, obtained with prompting, suggest that persona fidelity is uneven and depends on how
well the persona is represented in the corpus. Fine-tuning has been used to instil ideological viewpoints:
\citet{rozado2024political} produced left-leaning, right-leaning and depolarising variants of an open model
with modest supervised fine-tuning, the closest published precedent for instilling heterogeneous viewpoints by
fine-tuning, though evaluated by political-orientation tests rather than by reasoning fidelity. The thesis treats a school as a
persona of a special kind, one defined by a set of causal mechanisms rather than by opinions, and measures
fidelity at the level of mechanisms (the judge's fidelity and purity scales, the L3 entries) and of concepts
(the keyword-free probe set).

## 2.5 Measuring reasoning in generated text

### 2.5.1 Lexical measures

The Confirmation measured school fidelity with lexicons: must-have concepts, strong-signal terms and
anti-signal terms from competing schools (Section 3.5.4). Lexical measures are transparent, cheap and
reproducible, and they capture exactly the "surface" that imitation learning is known to transfer. Their
weakness is the one the panel named: a response can use a school's words without reasoning in its mechanisms,
and can reason in its mechanisms without its words. The thesis keeps the lexical measure as the registered
primary outcome, for continuity with the Confirmation and because it is pre-specified, and surrounds it with
two instruments that do not share its weakness.

### 2.5.2 Language models as judges

Using a strong language model to grade generated text has become standard. \citet{zheng2023judging} showed
that a frontier model's pairwise judgements agree with human preferences at rates comparable to inter-human
agreement, and catalogued the judge's biases (position, verbosity, self-enhancement); G-Eval formalised
rubric-based scoring with chain-of-thought and form-filling \citep{liu2023geval}; a survey organises the
design space and its failure modes \citep{gu2024survey}. Two findings determine the judge design in Chapter 4.
Language-model evaluators recognise and prefer their own generations \citep{panickssery2024llm}, so the judge
must not score the frontier reference arm, which is the same model. And a judge is a measurement instrument
whose validity must be established, not assumed: the thesis validates it against two human raters on a blinded
sample with chance-corrected agreement \citep{cohen1968weighted,landis1977measurement} and accepts a scale only
if the raters agree with each other and the judge agrees with them (Section 3.5.5).

### 2.5.3 Reading representations: sparse autoencoders and model diffing

The third instrument reads the model's activations. Language-model representations are superposed: a layer of
width $d$ encodes many more than $d$ features as nearly orthogonal directions \citep{elhage2022superposition}. Sparse
autoencoders (SAEs) recover such features by learning an overcomplete dictionary with a sparsity penalty, and
the recovered features are substantially monosemantic and human-interpretable \citep{bricken2023monosemanticity,
huben2024sparse}; the approach scales to production models \citep{templeton2024scaling} with improved
encoders such as TopK and JumpReLU \citep{gao2025scaling,rajamanoharan2024jumping}, and model developers now
release SAE suites for every layer of their open models (Gemma Scope for Gemma 2 and Gemma Scope 2 for Gemma 3, \citealp{lieberum2024gemmascope,mcdougall2025gemmascope2}; Qwen-Scope for the Qwen3 and Qwen3.5 families, \citealp{deng2026qwenscope}), so that an applied study need not train its own, and benchmarks now evaluate SAEs on downstream tasks rather than on reconstruction alone \citep{karvonen2025saebench}.
Features are labelled automatically by prompting a language model with their top-activating contexts, a
procedure introduced for neurons \citep{bills2023language} and extended to millions of SAE features with
detection and fuzzing scores that measure a label's reliability \citep{paulo2025automatically}. Such scores are necessary but not sufficient: they do not by themselves distinguish the features of a trained transformer from those of a randomly initialised one \citep{heap2026automated}, so automated labels need baselines and human checks.

Three families of negative result discipline the use of SAEs. For supervised tasks, SAE features rarely beat
linear probes or difference-of-means directions \citep{kantamneni2025sparse}, and for steering a model's
behaviour, prompting and fine-tuning beat SAE-based interventions, with a difference-of-means vector the
strongest representation-level baseline \citep{wu2025axbench}; a review of attempts to use SAEs on downstream tasks reached a similar verdict \citep{smith2025negative}. SAEs trained on a base model usually, but not always, transfer to its chat-tuned version \citep{kissane2024saes}; fine-tuning appears mostly to change when existing features fire rather than to create new ones, which is what makes base-model SAEs usable for measuring it \citep{galichin2026feature}; and encoders trained specifically for instruction-tuned models reconstruct their activations better \citep{li2026breaking}. And two SAEs trained on
the same data with different seeds learn partly different features \citep{paulo2026sparse}. The methodological
consequences, which Chapter 3 adopts, are to gate the SAE on reconstruction quality for every model state it is
applied to, to pair every SAE result with a difference-of-means baseline computed on the same data
\citep{marks2024geometry}, to repeat results across SAE variants, and to use SAEs for what baselines cannot do,
which is to *discover* and *name* what changed.

That last use is model diffing. Representation-level descriptions of fine-tuning are recent: narrow fine-tuning leaves traces in activation differences that are readable even on text unrelated to the fine-tuning domain \citep{minder2026narrow}; diffing SAE features before and after a narrow fine-tune recovers "persona" features that predict and can steer the fine-tuned behaviour \citep{wang2026persona}, although sparse diffing has artefacts of its own (sparsity penalties make shared concepts look fine-tuning-specific) that need correction \citep{minder2025overcoming}; low-rank adapters, the thesis's training method, add "intruder" directions that full fine-tuning does not \citep{shuttleworth2025lora}; character traits induced by fine-tuning move the model along identifiable "persona"
directions, extractable with contrasting prompts, which predict and can prevent trait shifts and can flag the
training examples responsible \citep{chen2026persona}; and representation engineering and activation steering
show that such directions are causally usable \citep{zou2023representation,turner2024steering,
rimsky2024steering}. No study has yet applied these tools to ask what fine-tuning changes when the quantity instilled is a theoretical perspective rather than a character trait, or compared the representational effect of fine-tuning with that of few-shot prompting on the same outputs. Chapter 4 does both, with features mapped to the fields of each
school's knowledge-base entry.

## 2.6 Probabilistic forecasting: scoring, calibration, combination and coherence

### 2.6.1 Proper scoring rules

A probability forecast is evaluated by a scoring rule; a rule is strictly proper if the forecaster's expected
score is uniquely optimised by reporting its true belief \citep{gneiting2007strictly}. The Brier score, the
squared distance between the probability vector and the outcome indicator, is the oldest in forecasting
practice \citep{brier1950verification} and decomposes into reliability, resolution and uncertainty
\citep{murphy1973vector}. For *ordered* categories the ranked probability score (RPS) sums the squared
differences between cumulative forecast and cumulative outcome distributions, so that probability placed near
the realised bin is penalised less than probability placed far from it \citep{epstein1969scoring}; it is the
natural score for a forecast over the bins of a macroeconomic release and is the thesis's primary forecasting
metric. The logarithmic score is local and strictly proper but unbounded, which is why it is reported with a
floor.

### 2.6.2 Calibration

A forecaster is calibrated if events assigned probability $p$ occur with frequency $p$. Calibration is
visualised by reliability diagrams and summarised by expected calibration error, the bin-weighted gap between
confidence and accuracy \citep{naeini2015obtaining}. Modern neural networks are systematically over-confident,
and a single post-hoc temperature on the logits, fitted on held-out data, removes much of the miscalibration
without changing the argmax \citep{guo2017calibration}; Platt scaling is the two-parameter logistic form of the
same idea \citep{platt2000probabilistic}. Language models are a special case: their verbalised probabilities are informative but imperfectly calibrated and typically over-confident \citep{kadavath2022language,tian2023just,xiong2024can}; fine-tuning a low-rank adapter on about a thousand graded examples teaches calibrated uncertainty better than prompting does \citep{kapoor2024taught}; and calibration on one question distribution need not transfer to another, the "calibration transfer" caveat the Confirmation's
reviewers raised. The thesis fits its calibration map on resolved macro markets from the same universe as the
test questions and tests the improvement as a registered hypothesis (exp03, H3).

### 2.6.3 Combining forecasts and the value of diversity

Combining forecasts has improved accuracy since the first demonstration \citep{bates1969combination}, and the
review literature finds that simple averages are hard to beat \citep{clemen1989combining}. For probability
forecasts the linear opinion pool \citep{stone1961opinion} is the basic combination. Its properties are known:
a linear pool of calibrated forecasts is itself under-confident (lacking sharpness), so the pool should be
recalibrated, for which \citet{ranjan2010combining} proposed a beta transformation and \citet{satopaa2014combining}
a logit-space aggregation with extremisation. Whether to average probabilities or quantiles is a related design
question \citep{lichtendahl2013average}. The *reason* combination works is diversity of errors: in the ambiguity
decomposition the ensemble's error equals the average member error minus the members' disagreement
\citep{krogh1994neural}, so an ensemble helps only to the extent that its members err differently \citep{dietterich2000ensemble}; a group of diverse problem solvers can outperform a group of individually better ones \citep{hong2004groups}; and the same accuracy-correlation trade-off limits the gains from pooling crowds of language models, whose errors are more correlated than those of human crowds \citep{jeddi2026crowdsourced}. Mixtures of experts turn the same principle into an architecture in which
specialised sub-models are gated per input \citep{jacobs1991adaptive,shazeer2017outrageously}. The thesis's
hypothesis that pooling three schools beats the best school (exp03, H1) is this argument applied to
theoretical rather than statistical diversity; its hypothesis that disagreement predicts error (H6) tests the
decomposition's other half, that disagreement is informative about difficulty.

### 2.6.4 Coherence

Probabilities over logically related propositions must satisfy the axioms, and de Finetti showed that a set of
previsions avoids a sure loss if and only if it is coherent, that is, lies in the convex hull of the admissible
outcome vectors \citep{definetti1974theory}. \citet{predd2009coherence} proved that, for every strictly proper scoring rule in a broad class, an incoherent probability assignment is dominated by a coherent one, and that for the Brier score the dominating assignment is the Euclidean projection onto the coherent set, which weakly improves the score in every state of the world. In prediction markets, incoherence
across related contracts is an arbitrage opportunity, and market makers can be designed to be arbitrage-free
over combinatorial outcome spaces \citep{kroer2016arbitrage}. Language-model probability judgements violate elementary probabilistic identities \citep{zhu2024incoherent}, language-model forecasters violate consistency relations across related questions, and the violations can be priced as arbitrage \citep{paleka2025consistency}; \citet{andrews2026dutch} price the incoherence of a model's forecasts as the guaranteed profit of a Dutch book, a distance to the coherent set computed by linear programming, and \citet{shi2026combinatorial} show that market prices outside the convex hull of admissible payoff vectors admit combinatorial arbitrage portfolios. Official statistics
supply coherence relations that are arithmetic rather than logical: the month-on-month and year-on-year
changes of a price index for the same month are tied by the known index levels, and a committee's meeting-by-
meeting decisions are tied to its year-end rate. The thesis measures the schools' and the market's incoherence
on such relations and tests coherent projection (exp04).

### 2.6.5 Comparing forecasters

Two forecasters are compared on the same events, so the comparison is paired. The Diebold-Mariano test of equal
predictive accuracy \citep{diebold1995comparing}, with the small-sample correction of
\citet{harvey1997testing}, is standard for point forecasts; for probability forecasts, forecast-encompassing
tests ask whether one forecast carries information the other does not, which is the form of the thesis's test
of the pool against the market price \citep{clements2010forecast}. With few events and non-normal score
differences, exact permutation tests and bootstrap intervals are preferable to asymptotic ones
\citep{efron1993bootstrap}, and families of hypotheses are controlled with Holm's step-down procedure
\citep{holm1979simple}. Pre-registration of hypotheses, metrics and decision rules before the data are seen
separates prediction from postdiction \citep{nosek2018preregistration}; the thesis registers every experiment
and reports confirmatory and exploratory results under separate labels.

## 2.7 Prediction markets and human forecasting as benchmarks

### 2.7.1 Prediction markets

A prediction market trades contracts that pay according to the outcome of a future event, so that prices are
interpretable as crowd probabilities. Reviews document their accuracy and their limits: favourite-longshot
bias, thin markets, manipulation, and the dependence of price-as-probability on risk neutrality
\citep{wolfers2004prediction,arrow2008promise}. For economic variables, market-based forecasts of data releases have been found to do at least as well as surveys of professional forecasters \citep{snowberg2013prediction}.
Regulated exchanges such as Kalshi now list ladders of contracts on United States macroeconomic releases with published resolution sources; the Federal Reserve Board has documented the accuracy of these macro markets against surveys and market-implied forecasts \citep{diercks2026kalshi}, and the calibration of market prices is known to vary by domain and horizon \citep{le2026decomposing}, which is why the thesis treats venue calibration as a base rate (L2) rather than assuming it. Each such ladder supplies, for one release, an ordered scenario set, a ground
truth and a crowd benchmark at every date before resolution: exactly the three things an outcome-based
evaluation of a macro forecaster needs. The research group's pmpol system (team code) already reads these
markets into a proposition ontology, fetches resolutions, measures venue calibration and projects incoherent
quotes onto coherent ones; the thesis reuses those components.

### 2.7.2 Human forecasters

Tetlock's long study of expert political judgement found that experts barely beat simple extrapolation and
that cognitive style predicted accuracy better than expertise \citep{tetlock2005expert}. The forecasting
tournaments that followed identified "superforecasters" and the practices that make them, including
probabilistic thinking, frequent updating, and aggregation across diverse forecasters with extremisation
\citep{mellers2014psychological,tetlock2015superforecasting}. Two lessons carry over. Aggregation of diverse
judgements is a robust source of accuracy, which supports pooling the schools. And a forecast's accuracy and
its reasoning quality are distinct: a well-argued forecast can be wrong and a lucky one right, which is why the
thesis measures reasoning fidelity (Chapter 4) and forecasting value (Chapter 6) separately and tests the link
between them (exp03, H5).

### 2.7.3 Language models as forecasters

Language models were first evaluated as forecasters on questions from platforms such as Metaculus.
\citet{halawi2024forecasting} built a system with news retrieval, reasoning prompts and fine-tuning on the
model's own best rationales, and approached the accuracy of the human crowd; \citet{schoenegger2024wisdom}
showed that an ensemble of twelve models rivals the crowd and that models improve when shown its median.
ForecastBench \citep{karger2025forecastbench} made the evaluation dynamic, collecting questions whose answers
are unknown at collection and scoring models against superforecasters as the questions resolve, which removes
training-data leakage by construction. \citet{paleka2025consistency} added consistency checks and showed that
even strong forecasters violate them. On the training side, \citet{turtel2025outcome} applied reinforcement
learning with a proper-scoring reward to about one hundred thousand resolved questions and matched frontier models with a 14-billion-parameter model; a report from Mantic and Thinking Machines Lab applied the same recipe, a Brier-score reward, to a 120-billion-parameter open-weight model and evaluated it in a Metaculus tournament \citep{jeen2026training}. Benchmarks that use prediction-market prices directly to measure language-model calibration followed \citep{nel2025kalshibench}. Two cautions apply to all of this work. \citet{paleka2026pitfalls} catalogue the pitfalls of evaluating language-model forecasters, above all the many forms of temporal leakage from training data and retrieval, and the difficulty of extrapolating from benchmark scores to real forecasting; and polls of several instances of one model are not a crowd in the human sense, because their forecasts are correlated, so that diversity has to be designed in rather than assumed \citep{gebele2026diversity,jeddi2026crowdsourced}. Three gaps remain for the thesis. These evaluations use
heterogeneous binary questions, whereas macroeconomic releases have ordered, arithmetically related outcome
spaces. They evaluate frontier or forecasting-optimised models, not models conditioned on a theory. And they
supply the model with news, so that the forecast's provenance is as opaque as the news; the thesis supplies
point-in-time statistics and analogues only, and records the provenance in a proof.

## 2.8 Analogue forecasting and point-in-time data

### 2.8.1 Analogues

Forecasting by analogue, locating past states that resemble the present and reading off their sequels, was
formalised in meteorology, where \citet{lorenz1969atmospheric} used naturally occurring analogues to estimate
the predictability of the atmosphere and found that good analogues are rare in high-dimensional state spaces.
The lesson for macroeconomics is the same: with few episodes and many indicators, the choice of state variables and of distance matters more than the retrieval algorithm. In macroeconometrics, similarity-based (nearest-neighbour) forecasting of macroeconomic series has been shown to outperform time-varying-parameter models during crises \citep{dendramis2020similarity}, the statistical precedent for retrieving analogues by state. History Rhymes \citep{khanna2025history}
is the closest recent application to financial forecasting: it retrieves historical dates whose macroeconomic
context resembles the present and uses them to improve single-stock return forecasts, with a concatenation of
standardised features as the state and a plain distance as the metric. Chapter 5 tests whether a
covariance-aware distance over discrete episodes retrieves more useful analogues.

### 2.8.2 Distance and covariance

The Mahalanobis distance \citep{mahalanobis1936generalised} measures distance in units of the data's own
covariance, so that correlated indicators (the many interest-rate series, the several inflation measures) are
not counted several times. With 35 indicators and 141 episodes the sample covariance is ill-conditioned; the
standard remedy is shrinkage towards a structured target, which yields a well-conditioned estimator with a
closed-form shrinkage intensity \citep{ledoit2004well,ledoit2004honey}. The thesis estimates the covariance on
the monthly indicator panel rather than on the episodes, which gives hundreds of observations per variable, and
re-estimates it in an expanding window so that no retrieval uses later data.

### 2.8.3 Point-in-time data

Macroeconomic data are revised, often substantially, and a forecast evaluated with revised data overstates what
could have been known. Real-time data sets record each value as it was published on each date
\citep{croushore2001realtime}, and the literature on their use shows that revisions change the apparent
performance of forecasting models and policy rules \citep{croushore2011frontiers}. The ALFRED archive supplies
vintages for the FRED series used here. The thesis uses point-in-time states for retrieval and as model inputs,
keeps revised states only for an ablation, and extends the same discipline to text through trigger-only episode
descriptions (Section 3.4.1).

## 2.9 Auditable reasoning and analytic standards

The requirement that every forecast carry a visible trail to its evidence, and a confidence grade separate
from its probability, comes from the analytic standards of the United States Intelligence Community
\citep{odni2015icd203}, which prescribe standard likelihood language and the separate expression of
confidence, and from structured analytic techniques such as the analysis of competing hypotheses
\citep{heuer1999psychology}. In the language-model literature the nearest practices are chain-of-thought
rationales, which the model generates and nobody checks, and retrieval-augmented generation, which attaches
sources without grading them. The research group's pmpol system implements the standards as a knowledge-layer
ontology with proof objects and analytic-confidence grades; the thesis adopts them (Section 3.3) and, in a
step the standards themselves do not take, tests whether the confidence grade and the schools' disagreement
predict forecast error (exp03, H6 and H7).

## 2.10 Summary of gaps

Five gaps emerge from this review and define the thesis.

1. Language models applied to the macroeconomy are not conditioned on an explicit theory, and no study has
   compared fine-tuning with the strongest prompting baselines as ways of instilling one, or measured the
   result with instruments that distinguish a theory's concepts from its vocabulary (Sections 2.3.2, 2.4, 2.5).
2. What fine-tuning changes inside a model, relative to prompting, has not been described with the tools of
   model diffing for any theoretical perspective (Section 2.5.3).
3. Analogue retrieval for macroeconomic events has not been tested with a covariance-aware metric, point-in-time
   states and a time-respecting protocol (Section 2.8).
4. Probabilistic forecasts of macroeconomic releases by language models have not been evaluated on a window
   provably outside the model's training data, against the market, with ordered scores, calibration and
   arithmetic coherence (Sections 2.6, 2.7).
5. Whether the disagreement among contested frameworks, and a graded analytic confidence, carry information
   about forecast error has not been tested (Sections 2.6.3, 2.9).

Chapter 3 sets out the design that addresses them, and the Related Work section positions the thesis against
the individual systems nearest to it.
