"""Fixed protocol constants for the DSAI6707 project. Changing any value after a run has started invalidates that run.

Events are synthetic (mosaic.teacher.make_items): search set = seed 23, held-out set = seed 29. Seed 11 (the thesis
disagreement matrix) and the thesis held-out files are never used.
"""

from pathlib import Path

COURSE_DIR = Path(__file__).resolve().parents[2]  # courses/dsai6707
RESULTS_DIR = COURSE_DIR / "results"
CACHE_PATH = RESULTS_DIR / "cache" / "llm_cache.jsonl"

SEARCH_SEED = 23
HELDOUT_SEED = 29
N_SEARCH = 5
N_HELDOUT = 10

FEASIBILITY = 0.9  # minimum share of parseable school outputs for a feasible prompt set (Deb's rule)
LENGTH_REF_WORDS = 600  # objective 3 is normalised by this fixed word count (capped at 1)
REF_POINT = (1.0, 1.0, 1.0)  # hypervolume reference point in normalised minimisation space

P_CROSS = 0.7  # probability that a child is produced by structural crossover
P_MUT = 0.9  # probability that a child is mutated after crossover/copy
P_LLM = 0.5  # share of mutations that are LLM-guided (only in methods with use_llm)

TEMPERATURE = 0.7
TOP_P = 0.9
MAX_TOKENS = 1024
MODEL = "qwen3.8-max"  # the same model id the thesis used for the disagreement matrix
BASE_URL = "https://token-plan.maas.qianwenaiapi.com/compatible-mode/v1"
# ASSUMED list prices (USD per million tokens). Replace with the provider's price sheet; the measured token counts
# are stored per call so the real cost can be recomputed later.
PRICE_IN_PER_MTOK = 2.4
PRICE_OUT_PER_MTOK = 9.6
BUDGET_USD = 30.0

# Second-model replication (results/haiku/). Claude Haiku 5.5 through the official Anthropic SDK. The model rejects
# non-default temperature/top_p, so the provider's default sampling is used; thinking is disabled as for qwen. The
# sampling seed is kept in the cache key (so the three seeds draw independent samples) but is not sent to the API.
HAIKU = {
    "model": "claude-haiku-5-5",
    "max_tokens": MAX_TOKENS,
    "price_in": 0.10,  # USD per million tokens, Anthropic list price (prompts up to 100K tokens)
    "price_out": 0.50,
    "results": RESULTS_DIR / "haiku",
}
