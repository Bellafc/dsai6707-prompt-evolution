"""Teacher pipeline for the school SFT trajectories (amendment 4 draft, Change 5).

The Confirmation's 1,500 GPT-4o trajectories were not kept. This rebuilds the pipeline of Confirmation Sec. 4.2.1:
an abstract event template (configs/teacher/templates.toml, 107 templates in 14 categories) is instantiated with
random slot values and a random macro snapshot, and a teacher model writes the school's agent trajectory
[Think] -> [ToolCall: query_episode_db] -> [Observe] -> [Think] -> [ToolCall: get_macro_data] -> [Observe] -> [Think]
-> [Output]. Each kept trajectory is stored in the data contract of data/README.md: the chat messages are built with
the same function and prompt files as arm A at inference (`prompts.build_messages`), so training and inference see
identical prompts; the raw event is stored too, so the messages can be rebuilt when the prompt files change.

Change 5 filters, fixed before generation: format validity (all markers in order, scenario probabilities summing to
1, directional signals) and leakage (no year after 2024 or month of 2025 after April, since exp03's calibration
window starts 2025-05; the templates carry no real events, so "no event later than the seed episode" holds by
construction).

Prompt version 2 (after the Opus review of the first pilot, research/teacher_pilot/opus_review/): the teacher gets the
school's way of diagnosing and the cases it reads as good news instead of a list of must-use concepts; the backdrop is
labelled US/global and internally consistent; the agent may cite backdrop numbers only after get_macro_data; tool
arguments are JSON; analogs are named and dated; every signal carries a conviction and a reason, with no default
direction. The validator checks all of these; `collect` also reports direction shares per asset so a batch where one
direction dominates is visible.
"""

from __future__ import annotations

import json
import random
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from mosaic.config import ROOT
from mosaic.data import Event
from mosaic.prompts import build_messages, read_prompt

SCHOOLS = ("keynesian", "austrian", "monetarist")
PROMPT_VERSION = 2
TEMPLATES = ROOT / "configs/teacher/templates.toml"
MARKERS = ["[Think]", "[ToolCall: query_episode_db]", "[Observe]", "[Think]", "[ToolCall: get_macro_data]",
           "[Observe]", "[Think]", "[Output]"]
LEAK_CUTOFF = (2025, 4)  # nothing after April 2025 (exp03 calibration window starts 2025-05-01)
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}


@dataclass
class Item:
    school: str
    template_id: str
    category: str
    event: Event


def load_templates(path: Path = TEMPLATES) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def template_list(cfg: dict) -> list[tuple[str, str, str]]:
    """(template_id, category, text) for every template, ids stable across runs."""
    out = []
    for ci, cat in enumerate(cfg["category"], 1):
        for ti, text in enumerate(cat["templates"], 1):
            out.append((f"T{ci:02d}-{ti:02d}", cat["name"], text))
    return out


def macro_snapshot(rng: random.Random) -> dict:
    """A random US/global backdrop (no real date) that hangs together: rates, curve and spreads agree, unemployment
    and volatility move against growth (Okun-style), money growth loosely tracks inflation."""
    ffr = rng.choice([0.125, 0.5, 1.0, 1.75, 2.5, 3.25, 4.0, 4.75, 5.5])
    two = round(max(0.05, ffr + rng.uniform(-0.75, 0.5)), 2)
    ten = round(max(0.3, two + rng.uniform(-1.0, 2.0)), 2)
    growth = round(rng.uniform(-6.0, 6.0), 1)
    cpi = round(rng.uniform(-0.5, 9.0), 1)
    vix = min(60, max(11, round(22 - 2 * growth + rng.uniform(-8, 12))))
    return {
        "US policy rate (%)": ffr,
        "US 2y yield (%)": two,
        "US 10y yield (%)": ten,
        "US 2y-10y spread (bp)": round((ten - two) * 100),
        "US CPI inflation y/y (%)": cpi,
        "US core PCE y/y (%)": round(max(-0.3, cpi - rng.uniform(-0.5, 1.5)), 1),
        "US unemployment rate (%)": round(min(10.0, max(3.3, 5.2 - 0.35 * growth + rng.uniform(-1.2, 1.8))), 1),
        "US real GDP growth q/q saar (%)": growth,
        "US M2 growth y/y (%)": round(min(20.0, max(-4.0, cpi + rng.uniform(-4.0, 8.0))), 1),
        "VIX": vix,
        "US high-yield spread (bp)": round(200 + 15 * vix + rng.uniform(-80, 80)),
        "DXY": rng.randint(85, 115),
        "WTI oil ($/bbl)": rng.randint(25, 130),
    }


def fill(text: str, slots: dict, rng: random.Random) -> str:
    return re.sub(r"\{(\w+)\}", lambda m: rng.choice(slots[m.group(1)]), text)


def make_items(n_per_school: int, seed: int = 0, cfg: dict | None = None) -> list[Item]:
    """n items per school; templates cycle so every template is used before any repeats, each with fresh slots and
    snapshot. Seeded per (school, index), so a larger run extends a smaller one with the same first items."""
    cfg = cfg or load_templates()
    temps = template_list(cfg)
    items = []
    for school in SCHOOLS:
        order = list(range(len(temps)))
        random.Random(f"{seed}:{school}:order").shuffle(order)
        for i in range(n_per_school):
            tid, cat, text = temps[order[i % len(temps)]]
            rng = random.Random(f"{seed}:{school}:{i}")
            ev = Event(id=f"syn-{school[0]}{i:04d}", text=fill(text, cfg["slots"], rng), category=cat,
                       macro_context=macro_snapshot(rng), template_id=tid)
            items.append(Item(school, tid, cat, ev))
    return items


def teacher_messages(item: Item, cfg: dict) -> list[dict]:
    """What the teacher model sees: how the school diagnoses, the event, the backdrop and the required structure."""
    sch = cfg["school"][item.school]
    ctx = "\n".join(f"- {k}: {v}" for k, v in item.event.macro_context.items())
    system = (
        "You write training data for a tool-using economist agent that reasons within one school of thought. Write "
        "only the agent's trajectory. It must read like a careful analyst at work, not a checklist: use the one or "
        "two mechanisms of the school that matter for this event, not every concept the school has. Historical "
        "analogies only from before 2025, named and dated; no real events or dates after 2024; no statistics "
        "attributed to real institutions beyond the backdrop.")
    user = (
        f"School: {item.school.capitalize()}.\n"
        f"How this school diagnoses: {sch['diagnosis']}\n"
        f"Mechanisms it may draw on (pick what fits, do not list them all): {', '.join(sch['concepts'])}.\n"
        f"Typical stance: {sch['signals']}. The school is not always bearish; it reads these as good news: "
        f"{'; '.join(sch['good_news'])}.\n\n"
        f"Event (category: {item.category}): {item.event.text}\n\n"
        f"US/global backdrop (returned by get_macro_data; cite none of these numbers before that call):\n{ctx}\n\n"
        "Blocks, in this order, each tag on its own line:\n" + "\n".join(MARKERS) + "\n\n"
        "Rules:\n"
        "1. First [Think]: say whether the event is good or bad news for growth and for inflation as this school "
        "reads it, and how large it is where the event says (bp, pp, share of GDP). Reason from the event only.\n"
        '2. [ToolCall: query_episode_db] is followed by one JSON line {"query": "..."}. The first [Observe] gives 2-3 '
        "specific episodes, each with its country or institution and year, all before 2025; no 'various episodes'.\n"
        '3. [ToolCall: get_macro_data] is followed by one JSON line {"indicators": [...]} with the backdrop\'s names. '
        "The second [Observe] reports the requested values exactly as in the backdrop.\n"
        "4. Third [Think]: combine event and data. If the event concerns another economy, say how it reaches US and "
        "global assets. If the event contradicts the backdrop (for example on the yield curve or inflation), say so "
        "in one sentence and treat the event as the newest information. Claim no trend that a single backdrop cannot "
        "show unless the event states it.\n"
        "5. [Output]:\n"
        "Causal chain: event -> ... -> outcome, in the school's terms.\n"
        "Scenarios: 2-4 lines 'S1 (event-specific name; growth up/down, inflation up/down): p', no colon inside the "
        "parentheses, probabilities summing to 1.\n"
        "Signals: one line each for equities, government bonds, US dollar, gold, oil and credit, as "
        "'asset: LONG|SHORT|NEUTRAL (conviction 1-5) - reason naming the scenario or chain step'. No asset has a "
        "default direction: use NEUTRAL when the chain gives no reason and low conviction for small or local events. "
        "The signals follow the most likely scenario.\n"
        "Do not mention other schools or these instructions.")
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


PROB = re.compile(r"^\s*S\d+[^:\n]*:\s*([01](?:\.\d+)?|\.\d+)\s*$", re.M)
SIGNAL = re.compile(r"\b(LONG|SHORT|NEUTRAL)\b")
YEAR = re.compile(r"\b(20[2-9]\d)\b")
BEFORE = re.compile(r"(before|pre-?|prior to|earlier than)\s*$", re.I)


def leaks(text: str) -> list[str]:
    """Dates after the cutoff: any year >= 2026, 2025 unless every month named next to it is January-April."""
    found = []
    for m in YEAR.finditer(text):
        y = int(m.group(1))
        if y > LEAK_CUTOFF[0]:
            found.append(m.group(0))
        elif y == LEAK_CUTOFF[0]:
            if BEFORE.search(text[max(0, m.start() - 12):m.start()]):
                continue  # "before 2025", "pre-2025": the boundary the prompt itself asks for, not a later date
            window = text[max(0, m.start() - 12):m.end() + 12].lower()
            months = [v for k, v in MONTHS.items() if k in window or k[:3] + " " in window]
            if not months or max(months) > LEAK_CUTOFF[1]:
                found.append(window.strip())
    return found


ANALOG_YEAR = re.compile(r"\b(1[89]\d\d|20[01]\d|202[0-4])\b")
ASSETS = {"equities": r"equit(?:y|ies)", "government bonds": r"(?:government |sovereign |treasury )?bonds?|treasuries",
          "US dollar": r"(?:the )?(?:us |u\.s\. )?dollar|usd|dxy", "gold": r"gold", "oil": r"(?:crude )?oil",
          "credit": r"credit|high[- ]yield"}
META = re.compile(r"\b(as instructed|the (?:prompt|instructions)|I (?:must|should|need to) (?:reason|stay|think|write)"
                  r" (?:as|within|in))\b", re.I)


def _segment(text: str, start: str, after: int = 0) -> str:
    """Text from the first `start` marker at or after `after` up to the next block tag."""
    i = text.find(start, after)
    if i < 0:
        return ""
    ends = [j for j in (text.find(tag, i + len(start)) for tag in set(MARKERS)) if j >= 0]
    return text[i + len(start):min(ends, default=len(text))]


def _tool_json(text: str, marker: str, key: str, kind: type) -> bool:
    arg = _segment(text, marker).strip().splitlines()
    try:
        return bool(arg) and isinstance(json.loads(arg[0]).get(key), kind)
    except (ValueError, AttributeError):
        return False


def validate(text: str, item: Item | None = None) -> list[str]:
    """Reasons to reject a trajectory (empty list = keep). With the item, also the checks that need its event."""
    problems = []
    pos = 0
    for mk in MARKERS:
        i = text.find(mk, pos)
        if i < 0:
            problems.append(f"missing or out of order: {mk}")
            break
        pos = i + len(mk)
    if not (_tool_json(text, "[ToolCall: query_episode_db]", "query", str)
            and _tool_json(text, "[ToolCall: get_macro_data]", "indicators", list)):
        problems.append("tool call arguments are not the required JSON line")
    first_obs = _segment(text, "[Observe]")
    if len(set(ANALOG_YEAR.findall(first_obs))) < 2:
        problems.append("fewer than 2 dated analog episodes")
    out = text[text.rfind("[Output]"):] if "[Output]" in text else ""
    probs = [float(p) for p in PROB.findall(out)]
    if not 2 <= len(probs) <= 4:
        problems.append(f"{len(probs)} scenario probabilities (2-4 required)")
    elif abs(sum(probs) - 1) > 0.02:
        problems.append(f"scenario probabilities sum to {sum(probs):.2f}")
    for asset, pat in ASSETS.items():
        m = re.search(rf"^[ \t]*[-*]?[ \t]*(?:{pat})[ \t]*:[ \t]*(LONG|SHORT|NEUTRAL)[ \t]*\([ \t]*conviction[ \t]*"
                      rf"[1-5][ \t]*\)[ \t]*[-\u2013\u2014:]?[ \t]*(.*)$", out, re.I | re.M)
        if not m:
            problems.append(f"signal missing or malformed: {asset}")
        elif len(m.group(2).split()) < 3:
            problems.append(f"signal without a reason: {asset}")
    if META.search(text):
        problems.append("talks about its instructions")
    if "<think>" in text:
        problems.append("teacher reasoning block left in the reply")
    for leak in leaks(text):
        problems.append(f"date after the leakage cutoff: {leak}")
    if item is not None:
        others = [s for s in SCHOOLS if s != item.school and re.search(rf"\b{s}", text, re.I)]
        if others:
            problems.append(f"mentions another school: {', '.join(others)}")
        before = text[:text.find("[ToolCall: get_macro_data]")] if "[ToolCall: get_macro_data]" in text else text
        early = [v for v in early_values(item) if re.search(rf"(?<![\d.]){re.escape(v)}(?!\d)", before)]
        if len(early) >= 2:
            problems.append(f"backdrop numbers cited before get_macro_data: {', '.join(early[:4])}")
    return problems


def early_values(item: Item) -> list[str]:
    """Backdrop values distinctive enough to spot (decimals or 3+ digits) that the event text does not contain."""
    vals = {str(v) for v in item.event.macro_context.values()}
    return sorted(v for v in vals if ("." in v or len(v.lstrip("-")) >= 3) and v not in item.event.text)


def signal_report(kept: dict[str, list[dict]], dominant: float = 0.7) -> dict:
    """Direction shares per school and asset, and warnings where one direction exceeds `dominant` (n >= 10)."""
    report: dict = {"shares": {}, "warnings": []}
    for school, recs in kept.items():
        counts: dict[str, dict[str, int]] = {a: {"LONG": 0, "SHORT": 0, "NEUTRAL": 0} for a in ASSETS}
        for r in recs:
            out = r["messages"][-1]["content"].split("[Output]")[-1]
            for asset, pat in ASSETS.items():
                m = re.search(rf"^[ \t]*[-*]?[ \t]*(?:{pat})[ \t]*:[ \t]*(LONG|SHORT|NEUTRAL)", out, re.I | re.M)
                if m:
                    counts[asset][m.group(1).upper()] += 1
        report["shares"][school] = counts
        for asset, c in counts.items():
            n = sum(c.values())
            top = max(c, key=c.get)
            if n >= 10 and c[top] / n > dominant:
                report["warnings"].append(f"{school}: {asset} {top} in {c[top]}/{n}")
    return report


def record(item: Item, reply: str, teacher: str) -> dict:
    """One training example in the data contract: arm-A messages plus the teacher's reply as the assistant turn."""
    msgs = build_messages("A", item.school, item.event, system=read_prompt(f"{item.school}.system.txt"),
                          user_template=read_prompt("user_template.txt"))
    return {"messages": [*msgs, {"role": "assistant", "content": reply.strip()}], "template_id": item.template_id,
            "category": item.category, "teacher": teacher, "teacher_prompt_version": PROMPT_VERSION,
            "event": {"id": item.event.id, "text": item.event.text, "category": item.category,
                      "macro_context": item.event.macro_context}}


def generate(backend, items: list[Item], cfg: dict, teacher: str, out_dir: Path) -> dict:
    """Ask the teacher (a local backend) for every item and keep the valid replies (see `collect`)."""
    from mosaic.backends import Request

    reqs = [Request(messages=teacher_messages(it, cfg), tag=f"teacher|{it.school}|{it.event.id}") for it in items]
    outs = backend.generate(reqs)
    return collect(items, [o.get("text", "") for o in outs], teacher, out_dir)


def collect(items: list[Item], replies: list[str], teacher: str, out_dir: Path) -> dict:
    """Keep valid replies, write <school>.jsonl and rejects.jsonl to out_dir; return counts per school."""
    from mosaic.backends import split_reasoning

    out_dir.mkdir(parents=True, exist_ok=True)
    kept: dict[str, list[dict]] = {s: [] for s in SCHOOLS}
    rejects = []
    for it, reply in zip(items, replies):
        reply = split_reasoning(reply or "")[1] if "<think>" in (reply or "") else (reply or "")
        problems = validate(reply, it)
        if problems:
            rejects.append({"school": it.school, "event_id": it.event.id, "template_id": it.template_id,
                            "problems": problems, "reply": reply})
        else:
            kept[it.school].append(record(it, reply, teacher))
    for school, recs in kept.items():
        with (out_dir / f"{school}.jsonl").open("w", encoding="utf-8") as f:
            f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in recs)
    with (out_dir / "rejects.jsonl").open("w", encoding="utf-8") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rejects)
    report = signal_report(kept)
    (out_dir / "report.json").write_text(json.dumps(report, indent=1) + "\n")
    counts = {s: len(v) for s, v in kept.items()}
    counts["rejected"] = len(rejects)
    counts["warnings"] = report["warnings"]
    return counts


# A run through a hosted API, done by the human outside this repository: `export_jobs` writes the requests in the
# OpenAI Batch format (also read by scripts/teacher_api.py), `import_results` validates the replies with the same
# filters and writes the training files. The items are rebuilt from (n, seed) in manifest.json, so the jobs file is
# the only thing that travels.

def export_jobs(n_per_school: int, seed: int, model: str, out_dir: Path, max_tokens: int = 2048,
                cfg: dict | None = None) -> int:
    cfg = cfg or load_templates()
    items = make_items(n_per_school, seed=seed, cfg=cfg)
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "requests.jsonl").open("w", encoding="utf-8") as f:
        for it in items:
            body = {"model": model, "messages": teacher_messages(it, cfg), "temperature": 0.8, "top_p": 0.95,
                    "max_tokens": max_tokens}
            f.write(json.dumps({"custom_id": f"{it.school}|{it.event.id}", "method": "POST",
                                "url": "/v1/chat/completions", "body": body}, ensure_ascii=False) + "\n")
    (out_dir / "manifest.json").write_text(json.dumps({"n_per_school": n_per_school, "seed": seed, "model": model,
                                                       "requests": len(items), "prompt_version": PROMPT_VERSION},
                                                      indent=1) + "\n")
    return len(items)


def reply_of(line: dict) -> tuple[str, str, str]:
    """(custom_id, reply text, model) from an OpenAI Batch output line or a scripts/teacher_api.py line."""
    body = (line.get("response") or {}).get("body") or line
    msg = ((body.get("choices") or [{}])[0].get("message") or {})
    return line.get("custom_id", ""), msg.get("content") or line.get("content") or "", body.get("model", "")


def import_results(jobs_dir: Path, results: Path, out_dir: Path) -> dict:
    man = json.loads((jobs_dir / "manifest.json").read_text())
    if man.get("prompt_version", 1) != PROMPT_VERSION:  # items and prompts are rebuilt from the current code
        raise SystemExit(f"{jobs_dir} was made with teacher prompt version {man.get('prompt_version', 1)}, the code "
                         f"is at {PROMPT_VERSION}; import it from the matching commit or regenerate")
    items = make_items(man["n_per_school"], seed=man["seed"])
    got = {}
    models = set()
    for raw in results.read_text(encoding="utf-8").splitlines():
        if raw.strip():
            cid, text, model = reply_of(json.loads(raw))
            got[cid] = text
            if model:
                models.add(model)
    teacher = ", ".join(sorted(models)) or man["model"]
    if any(m.lower().startswith(("claude", "anthropic")) for m in models | {man["model"]}):
        raise SystemExit("Claude models are excluded as teacher (amendment 4 Change 5, THESIS_DESIGN 4a)")
    counts = collect(items, [got.get(f"{it.school}|{it.event.id}", "") for it in items], teacher, out_dir)
    counts["missing"] = sum(f"{it.school}|{it.event.id}" not in got for it in items)
    return counts
