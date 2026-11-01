# Common brief for citation-verification agents (Macro-MOSAIC MPhil thesis, PolyU)

Goal: produce a BibTeX file whose every entry has been checked against a PRIMARY source page
(arXiv abstract page, OpenReview, ACL Anthology, PMLR, NeurIPS proceedings, publisher DOI page, JSTOR,
university working-paper page, official model card / technical report page). This is for a graduation
thesis: a wrong or invented reference is worse than a missing one.

Rules
1. For every item in your list: WebSearch, then WebFetch the primary page, and read the metadata (authors in
   order, exact title, venue, year, volume/pages if published, DOI or arXiv id, URL).
2. Write the BibTeX entry with a stable key (firstauthorYEARkeyword, lowercase ascii), full author list
   (no "et al."), braces around capitalised acronyms in titles, and a `note = {verified: <URL>, <date>}` field.
   Prefer the peer-reviewed published version over the arXiv preprint when one exists (give the arXiv id in an
   `eprint` field as well).
3. Status per item, in the verification log: VERIFIED (all core fields read from a primary page),
   PARTIAL (found, but one field could not be confirmed: say which), NOT FOUND (could not locate a primary
   page; do NOT write a BibTeX entry for it; say what you searched). If a 2026 item cannot be found, it may be
   that the cited venue/year in my list is wrong: report what you did find (e.g. "exists as arXiv 2601.xxxxx,
   no ICLR acceptance found").
4. Never invent authors, pages, DOIs or arXiv ids. If you are unsure about a detail, leave the field out and
   mark PARTIAL.
5. Discoveries: at the end, add up to 6 ADDITIONAL references you found that are highly relevant to your
   cluster for this thesis (see context below), each VERIFIED the same way, with a one-line note on relevance.
   Prefer peer-reviewed venues (NeurIPS/ICLR/ICML/ACL/EMNLP/KDD/AAAI, JASA, JRSS, IJF, AER, JEP, JFE, Science,
   Nature, PNAS) or official technical reports from the model developers.
6. Output files (write them, do not paste them into your reply):
   - <OUTDIR>/cluster_<X>.bib
   - <OUTDIR>/cluster_<X>_verification.md   (a table: key | status | what was verified | URL | notes)
   Reply with a short summary only: counts per status, items NOT FOUND, and the discoveries' keys.
7. Budget: be efficient, but completeness and accuracy matter more than speed. Use "extended" search mode only
   when a standard search fails.

Thesis context (for judging relevance)
Macro-MOSAIC: three LLM agents fine-tuned (LoRA) to reason as three schools of macroeconomic thought
(Keynesian, Austrian, Monetarist) on Qwen3-8B; compared with the best prompting baselines (zero-shot and
few-shot chain of thought, the model's thinking mode) and a frontier model; an LLM judge validated by two human
raters; sparse-autoencoder (SAE) features used to measure "school concepts vs vocabulary" and to see what
fine-tuning changes inside the model; historical-analogy retrieval over a 141-episode macro database with
point-in-time (ALFRED vintage) indicators and Mahalanobis distance with Ledoit–Wolf shrinkage; probabilistic
forecasts of US macro releases evaluated on resolved Kalshi prediction markets (2025–26) with ranked probability
score, Brier, calibration (ECE, temperature scaling), linear opinion pools of the schools, coherence checks
(CPI month-on-month vs year-on-year) and projection onto coherent probabilities; an L0–L5 knowledge-layer
ontology (rules, point-in-time facts, base rates, contested frameworks, market observations, inferences) with
proofs per forecast and ICD 203 analytic-confidence grades; pre-registration, event-level bootstrap and
sign-flip permutation tests with Holm correction.
