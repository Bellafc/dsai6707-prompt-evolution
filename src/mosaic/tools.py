"""Tools of the framework agents (THESIS_DESIGN §2a; research/DESIGN_ontology_agents.md §3). Standard library only:
scripts/teacher_api.py imports this module on the human's computer.

The harness executes every tool call; the model never writes a tool result. Two tools, one per knowledge layer that
RQ2 asks about:
  get_macro_data   L1 point-in-time facts: indicator values known at the analysis date (the teacher item's backdrop,
                   or ALFRED vintages for exp03)
  query_episode_db L2 base rates: named, dated historical episodes before the analysis date (a vetted stand-in table
                   until the human uploads the episode database; later the exp02 retriever)
L0 rules and resolution conditions belong to the task prompt (exp03 passes the scenario set), not to a tool.

Every result carries its layer, citable refs and the as-of date, so that an L5 proof can point at it.
"""

from __future__ import annotations

import json
import math
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EPISODES = ROOT / "configs/tools/episodes_standin.toml"

TOOL_SPECS = [
    {"type": "function", "function": {
        "name": "query_episode_db",
        "description": "Historical analog episodes (L2 base rates): dated, named episodes from before the analysis "
                       "date that resemble a situation, each with what happened.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string", "description": "the situation to match, in a few words"},
            "k": {"type": "integer", "minimum": 1, "maximum": 5, "description": "number of episodes, default 3"}},
            "required": ["query"]}}},
    {"type": "function", "function": {
        "name": "get_macro_data",
        "description": "Point-in-time macro and market indicators (L1 facts) as known at the analysis date.",
        "parameters": {"type": "object", "properties": {
            "indicators": {"type": "array", "items": {"type": "string"},
                           "description": "indicator names; unknown names are reported with the available ones"}},
            "required": ["indicators"]}}},
]
TOOL_NAMES = tuple(t["function"]["name"] for t in TOOL_SPECS)


@dataclass(frozen=True)
class ToolResult:
    tool: str
    layer: str  # "L1" | "L2" | "error"
    text: str  # what the model sees
    refs: tuple[str, ...] = ()  # citable ids: indicator names (L1), episode ids (L2)
    as_of: str = ""  # analysis date the facts are known at ("" = the item's own analysis date)
    source: str = ""  # provenance, kept out of the model's view

    def to_dict(self) -> dict:
        return {"tool": self.tool, "layer": self.layer, "text": self.text, "refs": list(self.refs),
                "as_of": self.as_of, "source": self.source}


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


class MacroFacts:
    """L1: indicator values known at `as_of`. Names match exactly or, failing that, by a unique normalised
    substring ("CPI" finds "US CPI inflation y/y (%)"); an ambiguous or unknown name is reported back."""

    def __init__(self, values: dict, *, as_of: str = "", source: str = "synthetic backdrop"):
        self.values, self.as_of, self.source = dict(values), as_of, source

    def resolve(self, name: str) -> str | None:
        if name in self.values:
            return name
        n = _norm(name)
        exact = [k for k in self.values if _norm(k) == n]
        if exact:
            return exact[0]
        hits = [k for k in self.values if n and n in _norm(k)]
        return hits[0] if len(hits) == 1 else None

    def lookup(self, names: list[str]) -> ToolResult:
        found: dict[str, object] = {}
        unknown = []
        for name in names:
            key = self.resolve(str(name))
            if key is None:
                unknown.append(str(name))
            else:
                found[key] = self.values[key]
        lines = [f"L1 indicators (known at {self.as_of or 'the analysis date'}):"]
        lines += [f"- {k}: {v}" for k, v in found.items()] or ["- none of the requested names is available"]
        if unknown:
            lines.append(f"Unknown: {', '.join(unknown)}. Available: {', '.join(self.values)}.")
        return ToolResult("get_macro_data", "L1", "\n".join(lines), tuple(found), self.as_of, self.source)


STOP = set("the a an of and or in on to for with by from at as is are was were be been into over under after before "
           "its it this that than then their there what when which who how new large major sharp sharply far above "
           "below more less than markets".split())
SYNONYMS = {"hike": "tightening", "hikes": "tightening", "raise": "tightening", "raises": "tightening",
            "cut": "easing", "cuts": "easing", "dovish": "easing", "hawkish": "tightening", "tariff": "tariffs",
            "war": "conflict", "invasion": "conflict", "default": "default", "defaults": "default",
            "crash": "crash", "selloff": "crash", "peg": "peg", "devalue": "devaluation", "devalues": "devaluation",
            "stimulus": "stimulus", "qe": "asset purchases", "purchases": "asset purchases", "oil": "oil",
            "crude": "oil", "jobs": "employment", "payrolls": "employment", "unemployment": "employment",
            "cpi": "inflation", "prices": "inflation", "bank": "banking", "banks": "banking", "run": "bank run",
            "property": "housing", "mortgage": "housing", "pandemic": "pandemic", "lockdown": "pandemic",
            "expected": "surprise", "unexpected": "surprise", "priced": "surprise", "unscheduled": "surprise",
            "governor": "new governor", "chair": "new governor", "head": "new governor"}


def _tokens(text: str) -> set[str]:
    out = set()
    for w in _norm(text).replace("central bank", "centralbank").split():
        if len(w) < 2 or w in STOP:
            continue
        out.add(w)
        if w in SYNONYMS:
            out.update(SYNONYMS[w].split())
        if len(w) > 4 and w.endswith("s"):
            out.add(w[:-1])
    return out


@dataclass(frozen=True)
class Episode:
    id: str
    date: str  # ISO date (YYYY-MM-DD; YYYY-MM-01 when only the month is certain)
    name: str
    country: str
    tags: tuple[str, ...]
    what: str


class EpisodeTable:
    """L2: analog episodes ranked by word overlap with the query, each shared word weighted by its rarity across
    episodes (idf) and doubled when it is a tag word, so generic words ("bank", "policy") decide little. The stand-in
    table is a draft the human checks; `before` hides episodes on or after the analysis date (exp03)."""

    def __init__(self, episodes: list[Episode], *, source: str = "stand-in table"):
        self.episodes, self.source = episodes, source
        self._tags = [set().union(*(_tokens(t) for t in e.tags)) if e.tags else set() for e in episodes]
        self._words = [_tokens(f"{e.name} {e.what} {e.country}") | t for e, t in zip(episodes, self._tags)]
        n = len(episodes)
        df: dict[str, int] = {}
        for ws in self._words:
            for w in ws:
                df[w] = df.get(w, 0) + 1
        self._idf = {w: math.log((n + 1) / (c + 1)) + 0.1 for w, c in df.items()}

    @classmethod
    def load(cls, path: Path = EPISODES) -> "EpisodeTable":
        cfg = tomllib.loads(path.read_text(encoding="utf-8"))
        eps = [Episode(e["id"], e["date"], e["name"], e["country"], tuple(e["tags"]), e["what"])
               for e in cfg["episode"]]
        return cls(eps, source=cfg.get("source", "stand-in table"))

    def query(self, query: str, k: int = 3, before: str = "") -> ToolResult:
        q = _tokens(query)
        scored = []
        for e, tags, words in zip(self.episodes, self._tags, self._words):
            if before and e.date >= before:
                continue
            score = sum(self._idf[w] * (2 if w in tags else 1) for w in q & words)
            if score > 0:
                scored.append((round(score, 6), e.date, e))
        scored.sort(key=lambda x: (-x[0], x[1]))
        top = [e for _, _, e in scored[:max(1, min(int(k or 3), 5))]]
        lines = [f"L2 episodes (before {before or 'the analysis date'}):"]
        lines += [f"- [{e.id}] {e.date}, {e.country}: {e.name}. {e.what}" for e in top]
        if not top:
            tags = sorted({t for e in self.episodes for t in e.tags})
            lines.append(f"- no episode matched; known tags: {', '.join(tags)}")
        return ToolResult("query_episode_db", "L2", "\n".join(lines), tuple(e.id for e in top), before, self.source)


class ToolBox:
    """Executes the agent's tool calls against one analysis date's facts and episodes."""

    def __init__(self, facts: MacroFacts, episodes: EpisodeTable, *, before: str = ""):
        self.facts, self.episodes, self.before = facts, episodes, before

    def execute(self, name: str, arguments: str | dict | None) -> ToolResult:
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments or "{}")
            except ValueError:
                return ToolResult(name, "error", "Error: the arguments are not valid JSON.")
        args = arguments if isinstance(arguments, dict) else {}
        if name == "get_macro_data":
            names = args.get("indicators")
            if isinstance(names, str):
                names = [names]
            if not isinstance(names, list) or not names:
                return ToolResult(name, "error", 'Error: pass {"indicators": [names]}.')
            return self.facts.lookup(names)
        if name == "query_episode_db":
            if not isinstance(args.get("query"), str) or not args["query"].strip():
                return ToolResult(name, "error", 'Error: pass {"query": "situation"}.')
            return self.episodes.query(args["query"], args.get("k") or 3, before=self.before)
        return ToolResult(name, "error", f"Error: unknown tool {name!r}; tools: {', '.join(TOOL_NAMES)}.")


TOOL_CALL = re.compile(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", re.S)


def parse_tool_calls(text: str) -> tuple[str, list[dict]]:
    """(content before the first call, calls) from a Qwen-style reply with <tool_call>{"name", "arguments"}</tool_call>
    blocks (the format the Qwen3 chat template teaches). Malformed blocks come back as {"error": ...}."""
    calls = []
    for m in TOOL_CALL.finditer(text):
        try:
            obj = json.loads(m.group(1))
            calls.append({"name": obj.get("name", ""), "arguments": obj.get("arguments", {})})
        except ValueError:
            calls.append({"error": "malformed tool call", "raw": m.group(1)})
    i = text.find("<tool_call>")
    return (text if i < 0 else text[:i]).strip(), calls
