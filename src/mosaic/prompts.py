"""Chat messages for each experimental arm.

  A  zero-shot   school system prompt + user template             (the Confirmation "base" condition)
  B  few-shot    A + k exemplar (user, assistant) pairs drawn from that school's SFT trajectories
  C  sft         same messages as A, Qwen2.5-7B-Instruct + the school's LoRA adapter
  D  teacher     same messages as A, sent to the API teacher model (GPT-4o)

A, C and D share messages on purpose: the only difference between A and C is the weights, between A and D the
model. Prompt files live in configs/prompts/; a file still containing PLACEHOLDER is refused on the test split.
"""

from __future__ import annotations

import random
from pathlib import Path

from mosaic.config import ROOT
from mosaic.data import Event, Trajectory

PLACEHOLDER = "<<PLACEHOLDER"


def read_prompt(name: str, prompts_dir: Path | None = None) -> str:
    return ((prompts_dir or ROOT / "configs/prompts") / name).read_text(encoding="utf-8")


def has_placeholder(text: str) -> bool:
    return PLACEHOLDER in text


def render_context(ctx) -> str:
    if ctx is None:
        return "(not provided)"
    if isinstance(ctx, dict):
        return "\n".join(f"- {k}: {v}" for k, v in ctx.items())
    return str(ctx)


def user_message(template: str, ev: Event) -> str:
    return template.format(event_id=ev.id, event_text=ev.text, macro_context=render_context(ev.macro_context),
                           category=ev.category or "unspecified")


def pick_exemplars(pool: list[Trajectory], ev: Event, k: int, strategy: str, seed: int,
                   max_chars: int | None = None) -> list[Trajectory]:
    """k exemplars for one event. Never one built from the same template as the event (leakage);
    'random' is seeded per event so reruns are identical; 'category' prefers exemplars whose prompt
    mentions the event's category, filling up at random."""
    cand = [t for t in pool if not (ev.template_id and t.template_id == ev.template_id)]
    rng = random.Random(f"{seed}:{ev.id}")
    if strategy == "category" and ev.category:
        same = [t for t in cand if ev.category.lower() in t.prompt.lower()]
        rest = [t for t in cand if t not in same]
        rng.shuffle(same)
        rng.shuffle(rest)
        chosen = (same + rest)[:k]
    elif strategy == "random":
        chosen = rng.sample(cand, min(k, len(cand)))
    else:
        raise ValueError(f"unknown exemplar strategy {strategy!r}")
    if max_chars:
        chosen = [Trajectory(t.school, t.prompt, t.response[:max_chars], t.template_id) for t in chosen]
    return chosen


def build_messages(arm: str, school: str, ev: Event, *, system: str, user_template: str,
                   exemplars: list[Trajectory] | None = None) -> list[dict]:
    msgs = [{"role": "system", "content": system}]
    if arm == "B":
        for t in exemplars or []:
            msgs += [{"role": "user", "content": t.prompt}, {"role": "assistant", "content": t.response}]
    elif arm not in ("A", "C", "D"):
        raise ValueError(f"unknown arm {arm!r}")
    msgs.append({"role": "user", "content": user_message(user_template, ev)})
    return msgs
