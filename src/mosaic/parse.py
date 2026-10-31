"""Parse a trajectory into the pieces the metrics need.

The Confirmation report (Sec. 4.2.3) scores seven structural elements:
  [Think], [ToolCall], [Observe], [Output], a causal reasoning chain, scenario probabilities, asset signals.
The exact output format of the original trajectories is not reproduced here; the regexes below accept the
common variants (0.35 / 35%, "SPX: LONG" / "SPX - long (0.6)"). Task 0 in program.md checks parity against the
Confirmation numbers before anything else is trusted; any parser change needs a test in tests/test_parse.py.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

TAGS = ("Think", "ToolCall", "Observe", "Output")
DIRECTIONS = {
    "long": "long", "buy": "long", "overweight": "long", "bullish": "long",
    "short": "short", "sell": "short", "underweight": "short", "bearish": "short",
    "neutral": "neutral", "hold": "neutral", "flat": "neutral",
}
_TAG = {t: re.compile(rf"\[\s*{t}\b", re.I) for t in TAGS}
_OUTPUT = re.compile(r"\[\s*Output\s*\]", re.I)
_PROB = re.compile(r"(?<![\w.])(0?\.\d+|1\.0+|\d{1,3}(?:\.\d+)?\s*%)(?![\w.])")
_SIGNAL = re.compile(
    r"^[\s\-*•\d.)]*([A-Za-z][A-Za-z0-9/&.\- ]{0,24}?)\s*[:\-–=]\s*\**\s*("
    + "|".join(DIRECTIONS) + r")\b", re.I | re.M)
_ARROW = re.compile(r"->|→|=>|⇒|leads to|causes|transmits", re.I)


@dataclass
class Parsed:
    tags: dict[str, bool]
    output: str
    causal_chain: bool
    scenarios: list[tuple[str, float]] = field(default_factory=list)
    signals: dict[str, str] = field(default_factory=dict)  # asset -> long/short/neutral

    @property
    def has_scenarios(self) -> bool:
        return len(self.scenarios) >= 2

    @property
    def has_signals(self) -> bool:
        return len(self.signals) >= 1

    @property
    def scenario_sum(self) -> float:
        return sum(p for _, p in self.scenarios)

    def completeness(self) -> float:
        parts = [*self.tags.values(), self.causal_chain, self.has_scenarios, self.has_signals]
        return sum(parts) / len(parts)


def _prob(tok: str) -> float:
    tok = tok.strip()
    return float(tok.rstrip("%").strip()) / 100 if tok.endswith("%") else float(tok)


def norm_asset(name: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", name.upper())


def parse(text: str) -> Parsed:
    tags = {t: bool(_TAG[t].search(text)) for t in TAGS}
    m = list(_OUTPUT.finditer(text))
    output = text[m[-1].end():] if m else ""
    scenarios = []
    in_scen = False
    for line in output.splitlines():
        low = line.lower()
        if "scenario" in low or "probabilit" in low:
            in_scen = True
        if re.search(r"signal|allocation|position", low) and not _PROB.search(line):
            in_scen = False
        p = _PROB.search(line)
        if in_scen and p and not _SIGNAL.search(line):
            name = line[:p.start()].strip(" -*•:\t")
            val = _prob(p.group(1))
            if name and 0.0 <= val <= 1.0:
                scenarios.append((name, val))
    signals = {}
    for sm in _SIGNAL.finditer(output):
        asset = norm_asset(sm.group(1))
        if asset and not re.fullmatch(r"(SCENARIO|PROBABILITY|CAUSALCHAIN|CONVICTION)\w*", asset):
            signals.setdefault(asset, DIRECTIONS[sm.group(2).lower()])
    causal = bool(re.search(r"causal", output, re.I)) or len(_ARROW.findall(output)) >= 2
    return Parsed(tags, output, causal, scenarios, signals)
