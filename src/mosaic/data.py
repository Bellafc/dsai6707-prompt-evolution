"""Data contract: events, training trajectories, adapters.

events/<split>.jsonl      one event per line: {"id", "text", optional "difficulty", "category", "macro_context"}
trajectories/<school>.jsonl  SFT training data, either {"messages": [{"role", "content"}, ...]}
                          or {"prompt": ..., "response": ...}; optional "template_id" (used to keep few-shot
                          exemplars and dev events from sharing a template)
adapters/<school>/        PEFT LoRA adapter directory (adapter_config.json + weights)

`validate()` returns a list of problems; `mosaic doctor` prints them.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from mosaic import SCHOOLS


@dataclass
class Event:
    id: str
    text: str
    difficulty: str = ""
    category: str = ""
    macro_context: dict | str | None = None
    template_id: str = ""
    extra: dict = field(default_factory=dict)


@dataclass
class Trajectory:
    school: str
    prompt: str
    response: str
    template_id: str = ""


def read_jsonl(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def load_events(path: Path) -> list[Event]:
    out = []
    for r in read_jsonl(path):
        known = {k: r.get(k) for k in ("id", "text", "difficulty", "category", "macro_context", "template_id")}
        extra = {k: v for k, v in r.items() if k not in known}
        out.append(Event(id=str(known["id"]), text=known["text"], difficulty=known["difficulty"] or "",
                         category=known["category"] or "", macro_context=known["macro_context"],
                         template_id=str(known["template_id"] or ""), extra=extra))
    return out


def load_trajectories(path: Path, school: str) -> list[Trajectory]:
    out = []
    for r in read_jsonl(path):
        if "messages" in r:
            user = [m["content"] for m in r["messages"] if m["role"] == "user"]
            asst = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
            if not user or not asst:
                continue
            prompt, response = user[0], asst[-1]
        else:
            prompt, response = r["prompt"], r["response"]
        out.append(Trajectory(school, prompt, response, str(r.get("template_id", ""))))
    return out


def validate(p: dict) -> list[str]:
    """Problems with the data on disk, as human-readable strings (empty list = OK)."""
    problems = []
    for split in ("dev", "test"):
        f = Path(p["events_dir"]) / f"{split}.jsonl"
        if not f.exists():
            problems.append(f"missing {f}")
            continue
        try:
            ev = load_events(f)
        except Exception as e:  # noqa: BLE001
            problems.append(f"{f}: unreadable ({e})")
            continue
        ids = [e.id for e in ev]
        if len(ids) != len(set(ids)):
            problems.append(f"{f}: duplicate ids")
        if any(not e.text for e in ev):
            problems.append(f"{f}: events with empty text")
    dev, test = Path(p["events_dir"]) / "dev.jsonl", Path(p["events_dir"]) / "test.jsonl"
    if dev.exists() and test.exists():
        d, t = load_events(dev), load_events(test)
        overlap = {e.id for e in d} & {e.id for e in t}
        if overlap:
            problems.append(f"dev and test share {len(overlap)} ids")
        same_text = {e.text.strip() for e in d} & {e.text.strip() for e in t}
        if same_text:
            problems.append(f"dev and test share {len(same_text)} identical event texts")
    for s in SCHOOLS:
        tf = Path(p["trajectories_dir"]) / f"{s}.jsonl"
        if not tf.exists():
            problems.append(f"missing {tf} (needed for few-shot arm B)")
        ad = Path(p["adapters_dir"]) / s
        if not (ad / "adapter_config.json").exists():
            problems.append(f"missing LoRA adapter {ad}/adapter_config.json (needed for arm C)")
    return problems
