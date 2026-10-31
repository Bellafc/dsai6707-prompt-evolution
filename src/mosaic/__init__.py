"""Macro-MOSAIC experiment harness.

Layout of a run:  config (TOML) -> prompts -> backend (vLLM+LoRA | OpenAI | fake) -> cached generations
-> parser ([Think]/[ToolCall]/[Observe]/[Output]) -> metrics -> runs/<run_id>/ + experiments/results.tsv.
"""

SCHOOLS = ("keynesian", "austrian", "monetarist")
__version__ = "0.1.0"
