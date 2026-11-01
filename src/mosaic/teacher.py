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
    """A random but internally plausible macro state (no real date attached)."""
    ffr = rng.choice([0.125, 0.5, 1.0, 1.75, 2.5, 3.25, 4.0, 4.75, 5.5])
    cpi = round(rng.uniform(-0.5, 9.0), 1)
    return {
        "policy rate (%)": ffr,
        "CPI inflation y/y (%)": cpi,
        "core PCE y/y (%)": round(max(-0.3, cpi - rng.uniform(-0.5, 1.5)), 1),
        "unemployment rate (%)": round(rng.uniform(3.3, 9.5), 1),
        "real GDP growth q/q saar (%)": round(rng.uniform(-6.0, 6.0), 1),
        "M2 growth y/y (%)": round(rng.uniform(-4.0, 20.0), 1),
        "10y yield (%)": round(max(0.4, ffr + rng.uniform(-1.5, 2.0)), 2),
        "2y-10y spread (bp)": rng.randint(-110, 250),
        "VIX": rng.randint(11, 55),
        "DXY": rng.randint(85, 115),
        "WTI oil ($/bbl)": rng.randint(25, 130),
        "high-yield spread (bp)": rng.randint(280, 1100),
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
    """What the teacher model sees: the school's profile, the event, the snapshot and the required structure."""
    sch = cfg["school"][item.school]
    ctx = "\n".join(f"- {k}: {v}" for k, v in item.event.macro_context.items())
    system = (
        "You write training data for a tool-using economist agent that reasons strictly within one school of thought. "
        "Write the agent's full trajectory, nothing else. Simulated tool observations must be plausible and generic: "
        "historical analogies only from before 2025, no real events or dates after 2024, no invented statistics "
        "attributed to real institutions beyond what the snapshot gives.")
    user = (
        f"School: {item.school.capitalize()}.\n"
        f"Core concepts to reason with: {', '.join(sch['concepts'])}.\n"
        f"Transmission mechanisms: {'; '.join(sch['mechanisms'])}.\n"
        f"Typical stance: {sch['signals']}.\n\n"
        f"Event (category: {item.category}): {item.event.text}\n\nMacro snapshot:\n{ctx}\n\n"
        "Write the trajectory with exactly these blocks in this order, each tag on its own line:\n"
        + "\n".join(MARKERS) + "\n"
        "In [ToolCall: query_episode_db] give a short query for historical analog episodes; in the first [Observe] "
        "summarise 2-3 analog episodes from before 2025. In [ToolCall: get_macro_data] request indicators; in the "
        "second [Observe] report values consistent with the snapshot. The [Output] block must contain:\n"
        "Causal chain: event -> mechanism -> ... -> outcome, in the school's terms.\n"
        "Scenarios: 3-4 named scenarios as 'S1 (name): p' lines, probabilities summing to 1.\n"
        "Signals: one line each for equities, government bonds, the US dollar, gold, oil and credit, as "
        "'asset: LONG|SHORT|NEUTRAL (conviction 1-5)'.\n"
        "Stay inside the school's framework; do not mention other schools.")
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


PROB = re.compile(r"^\s*S\d+[^:\n]*:\s*([01](?:\.\d+)?|\.\d+)\s*$", re.M)
SIGNAL = re.compile(r"\b(LONG|SHORT|NEUTRAL)\b")
YEAR = re.compile(r"\b(20[2-9]\d)\b")


def leaks(text: str) -> list[str]:
    """Dates after the cutoff: any year >= 2026, 2025 unless every month named next to it is January-April."""
    found = []
    for m in YEAR.finditer(text):
        y = int(m.group(1))
        if y > LEAK_CUTOFF[0]:
            found.append(m.group(0))
        elif y == LEAK_CUTOFF[0]:
            window = text[max(0, m.start() - 12):m.end() + 12].lower()
            months = [v for k, v in MONTHS.items() if k in window or k[:3] + " " in window]
            if not months or max(months) > LEAK_CUTOFF[1]:
                found.append(window.strip())
    return found


def validate(text: str) -> list[str]:
    """Reasons to reject a trajectory (empty list = keep)."""
    problems = []
    pos = 0
    for mk in MARKERS:
        i = text.find(mk, pos)
        if i < 0:
            problems.append(f"missing or out of order: {mk}")
            break
        pos = i + len(mk)
    out = text[text.rfind("[Output]"):] if "[Output]" in text else ""
    probs = [float(p) for p in PROB.findall(out)]
    if len(probs) < 2:
        problems.append("fewer than 2 scenario probabilities")
    elif abs(sum(probs) - 1) > 0.02:
        problems.append(f"scenario probabilities sum to {sum(probs):.2f}")
    if len(SIGNAL.findall(out)) < 4:
        problems.append("fewer than 4 directional signals")
    if "<think>" in text:
        problems.append("teacher reasoning block left in the reply")
    for leak in leaks(text):
        problems.append(f"date after the leakage cutoff: {leak}")
    return problems


def record(item: Item, reply: str, teacher: str) -> dict:
    """One training example in the data contract: arm-A messages plus the teacher's reply as the assistant turn."""
    msgs = build_messages("A", item.school, item.event, system=read_prompt(f"{item.school}.system.txt"),
                          user_template=read_prompt("user_template.txt"))
    return {"messages": [*msgs, {"role": "assistant", "content": reply.strip()}], "template_id": item.template_id,
            "category": item.category, "teacher": teacher,
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
        problems = validate(reply)
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
    counts = {s: len(v) for s, v in kept.items()}
    counts["rejected"] = len(rejects)
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
                                                       "requests": len(items)}, indent=1) + "\n")
    return len(items)


def reply_of(line: dict) -> tuple[str, str, str]:
    """(custom_id, reply text, model) from an OpenAI Batch output line or a scripts/teacher_api.py line."""
    body = (line.get("response") or {}).get("body") or line
    msg = ((body.get("choices") or [{}])[0].get("message") or {})
    return line.get("custom_id", ""), msg.get("content") or line.get("content") or "", body.get("model", "")


def import_results(jobs_dir: Path, results: Path, out_dir: Path) -> dict:
    man = json.loads((jobs_dir / "manifest.json").read_text())
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
