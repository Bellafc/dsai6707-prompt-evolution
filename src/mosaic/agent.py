"""The framework agent's loop at inference (A-agent and C-agent; RQ2/RQ3, research/DESIGN_ontology_agents.md §4a).

Each conversation alternates model turns and tool results: the model replies, its <tool_call> blocks (the Qwen chat
template's format) are parsed and executed by `mosaic.tools`, the results go back as tool messages, until a reply
without a call or `max_rounds` replies. Conversations advance in lockstep, one batched `backend.generate` per round,
so vLLM keeps its batching. The checks of teacher prompt version 4 (`teacher.check_v4`) score the result: protocol,
tool-call validity, the Change 5 text filters and the grounded [Proof].
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from mosaic.backends import Request
from mosaic.tools import TOOL_SPECS, EpisodeTable, MacroFacts, ToolBox, parse_tool_calls


@dataclass
class AgentJob:
    tag: str
    messages: list[dict]  # system + user
    toolbox: ToolBox
    adapter: str | None = None
    turns: list[dict] = field(default_factory=list)
    malformed: int = 0  # tool-call blocks that did not parse
    done: bool = False


def run_agents(backend, jobs: list[AgentJob], max_rounds: int = 4, tools: list[dict] = TOOL_SPECS) -> list[AgentJob]:
    """Advance every job until it answers without a tool call or reaches max_rounds model replies."""
    for rnd in range(max_rounds):
        active = [j for j in jobs if not j.done]
        if not active:
            break
        reqs = [Request(messages=[*j.messages, *j.turns], adapter=j.adapter, tag=f"{j.tag}|r{rnd}", tools=tools)
                for j in active]
        for j, out in zip(active, backend.generate(reqs)):
            content, calls = parse_tool_calls(out.get("text", ""))
            good = [c for c in calls if "error" not in c]
            j.malformed += len(calls) - len(good)
            turn: dict = {"role": "assistant", "content": content}
            if good:
                turn["tool_calls"] = [{"id": f"call_{rnd}_{k}", "type": "function",
                                       "function": {"name": c["name"], "arguments": json.dumps(c["arguments"])}}
                                      for k, c in enumerate(good)]
            j.turns.append(turn)
            if not good:
                j.done = True
                continue
            for c in turn["tool_calls"]:
                res = j.toolbox.execute(c["function"]["name"], c["function"]["arguments"])
                j.turns.append({"role": "tool", "tool_call_id": c["id"], "name": c["function"]["name"],
                                "content": res.text})
    return jobs


PLACEHOLDER_LINE = re.compile(r"^<<PLACEHOLDER:.*?>>\s*$", re.M)


def spike_jobs(n_per_school: int, seed: int = 7) -> list[tuple]:
    """(item, AgentJob) pairs for the agent spike: template events with a backdrop (a seed other than the teacher's
    training items), the agent prompt of the C-agent format, provisional school prompts without their PLACEHOLDER
    line. Seed 7 keeps the spike's events apart from the training items (seed 0)."""
    from mosaic import teacher

    items = teacher.make_items(n_per_school, seed=seed)
    episodes = EpisodeTable.load()
    out = []
    for it in items:
        msgs = teacher.agent_messages(it)
        msgs[0] = {"role": "system", "content": PLACEHOLDER_LINE.sub("", msgs[0]["content"]).strip()}
        box = ToolBox(MacroFacts(it.event.macro_context), episodes)
        out.append((it, AgentJob(tag=f"agent|{it.school}|{it.event.id}", messages=msgs, toolbox=box)))
    return out


def score(pairs: list[tuple]) -> dict:
    """Shares of conversations that pass each part of the v4 checks, and the problems counted."""
    from collections import Counter

    from mosaic import teacher

    episodes = EpisodeTable.load()
    n = len(pairs)
    passed = protocol = proof_ok = text_ok = 0
    malformed = 0
    kinds: Counter = Counter()
    rows = []
    for it, job in pairs:
        problems, _ = teacher.check_v4(it, job.turns, episodes)
        malformed += job.malformed
        rows.append({"tag": job.tag, "problems": problems, "rounds": sum(t["role"] == "assistant" for t in job.turns)})
        passed += not problems
        protocol += not any(p.startswith("protocol") for p in problems)
        proof_ok += not any("proof" in p for p in problems)
        text_ok += not any(not (p.startswith("protocol") or "proof" in p or p.startswith("tool")) for p in problems)
        kinds.update(p.split(":")[0] for p in problems)
    share = (lambda k: round(k / n, 3)) if n else (lambda k: 0.0)
    return {"n": n, "all_checks": share(passed), "protocol": share(protocol), "proof": share(proof_ok),
            "text_filters": share(text_ok), "malformed_tool_calls": malformed,
            "problems": dict(kinds.most_common()), "rows": rows}
