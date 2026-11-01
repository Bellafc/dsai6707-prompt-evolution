"""Multi-objective evolution of a prompt SET for three competing economic-school LLM agents (DSAI6707 project).

Modules: config (protocol constants), genome (representation), evaluate (objectives), operators (rule, crossover and
LLM-guided variation), moo (constrained NSGA-II machinery, hypervolume, knee), algorithms (NSGA-II, GA, random, B0),
backend (cached, concurrent OpenAI-compatible client with a USD ledger), offline (deterministic test model),
runner (command line). The harness code is imported from mosaic and never modified.
"""
