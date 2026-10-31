"""Score saved outputs without generating anything: the parity check against the Confirmation (Task 0).

  mosaic rescore --file data/legacy/sft_austrian.jsonl --school austrian

Expected for the Confirmation SFT Austrian outputs: consistency 0.319, must-have hits 1.9/6, anti-signal 0.59.
"""

from __future__ import annotations

import json

import numpy as np

from mosaic.data import read_jsonl
from mosaic.metrics import score_response
from mosaic.parse import parse

KEYS = ["consistency", "must_hits", "strong_hits", "anti_hits", "completeness", "has_output", "has_scenarios",
        "has_signals"]


def rescore(path: str, school: str) -> dict:
    rows = read_jsonl(path)
    scores = []
    for r in rows:
        text = r.get("text") or r.get("response") or r.get("output") or ""
        scores.append(score_response(text, parse(text), school))
    out = {"n": len(scores), **{k: round(float(np.mean([s[k] for s in scores])), 4) for k in KEYS}}
    print(json.dumps(out))
    return out
