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

Prompt version 4 (real tools, research/DESIGN_ontology_agents.md §3-4a): the teacher no longer sees the backdrop. It
calls query_episode_db and get_macro_data through function calling, the runner executes them (`mosaic.tools`), and
the results come back as tool messages, so the model writes no observation. The final message adds a [Proof] block
(steps typed by knowledge layer, citing the returned ids) and a confidence line. One run gives two training formats:
the Confirmation single-pass text for exp01 arm C (`flatten`, proof removed, observations inline as the tools returned
them) and the multi-turn agent conversation for C-agent. Items version 3 recentres the backdrop (unemployment around
the 4.5% natural rate, inflation skewed towards the 2% target) after the pilot-v2 review found 72% of backdrops above
4.5% unemployment.

Prompt version 5 (after the Opus review of pilot v4, research/teacher_pilot/opus_review.md): no instruction that the
teacher echoed ("weigh the event more", "as this school reads it"); the data are declared pre-event and may not be read
as the event's effect; scenario probabilities and confidence levels get definitions instead of defaults; signals name
their asset referents and may not rest on minority scenarios; foreign events may not be judged with US data. The
validator rejects the echoes, proofs over 8 lines and proofs whose L5 step misses the most likely scenario, and the
batch report flags repeated probability tuples, one dominant confidence level and phrases shared by many items.
Items version 4: fewer negative-growth backdrops, the curve tied to the policy path and inflation, oil tied to CPI,
lagged and smoothed series (M2 a year earlier, 4-quarter growth, nominal GDP), and levels the event states imposed on
the backdrop.
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
from mosaic.tools import EPISODES, TOOL_SPECS, EpisodeTable, MacroFacts, ToolBox

SCHOOLS = ("keynesian", "austrian", "monetarist")
PROMPT_VERSION = 5  # 5: pilot-v4 review fixes; 4: real tools through function calling, [Proof] block
ITEMS_VERSION = 4  # the item generator (templates, backdrop); imports rebuild items, so this must match
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
    """A random US/global backdrop (no real date) that hangs together: the 2y follows the expected policy path, the
    10y stays near inflation plus a term premium, unemployment and volatility move against growth (Okun-style), oil
    and money growth loosely track inflation, and smoothed or lagged series let the agent see direction."""
    ffr = rng.choice([0.125, 0.5, 1.0, 1.75, 2.5, 3.25, 4.0, 4.75, 5.5])
    growth = round(rng.triangular(-6.0, 6.0, 2.0), 1)
    trend = round(min(4.0, max(-3.0, 0.5 * growth + 1.0 + rng.uniform(-0.8, 0.8))), 1)
    cpi = round(rng.triangular(-0.5, 8.0, 2.2), 1)
    unemp = round(min(10.0, max(3.3, 4.4 - 0.35 * growth + rng.uniform(-1.0, 1.2))), 1)
    two = round(max(0.05, ffr + 0.12 * growth - 0.15 * max(0.0, unemp - 4.5) + rng.uniform(-0.4, 0.4)), 2)
    ten = round(max(0.3, 0.5 * two + 0.5 * (cpi + 1.0) + rng.uniform(-0.8, 1.2)), 2)
    vix = min(60, max(11, round(22 - 2 * growth + rng.uniform(-8, 12))))
    m2 = round(min(20.0, max(-4.0, cpi + rng.uniform(-4.0, 8.0))), 1)
    return {
        "US policy rate (%)": ffr,
        "US 2y yield (%)": two,
        "US 10y yield (%)": ten,
        "US 2y-10y spread (bp)": round((ten - two) * 100),
        "US CPI inflation y/y (%)": cpi,
        "US core PCE y/y (%)": round(max(-0.3, cpi - rng.uniform(-0.5, 1.5)), 1),
        "US unemployment rate (%)": unemp,
        "US real GDP growth q/q saar (%)": growth,
        "US real GDP growth 4-quarter average (%)": trend,
        "US nominal GDP growth y/y (%)": round(trend + cpi, 1),
        "US M2 growth y/y (%)": m2,
        "US M2 growth y/y a year earlier (%)": round(min(20.0, max(-4.0, m2 + rng.uniform(-4.0, 4.0))), 1),
        "VIX": vix,
        "US high-yield spread (bp)": round(200 + 15 * vix + rng.uniform(-80, 80)),
        "DXY": rng.randint(85, 115),
        "WTI oil ($/bbl)": int(min(140, max(25, 45 + 8 * cpi + rng.uniform(-20, 25)))),
    }


def align_backdrop(text: str, snap: dict, rng: random.Random) -> dict:
    """Impose levels the event text states on the backdrop (pilot-v4 review: an event saying inflation is 2.5pp above
    target came with a CPI of 1.6%). Only US-level statements are imposed; foreign events keep the US backdrop."""
    snap = dict(snap)
    cpi_key = "US CPI inflation y/y (%)"
    m = re.search(r"the Federal Reserve cuts rates by \d+bp while inflation is still ([\d.]+)pp above target", text)
    if m:
        snap[cpi_key] = round(2.0 + float(m.group(1)) + rng.uniform(-0.2, 0.3), 1)
    if "Headline CPI turns negative year on year" in text:
        snap[cpi_key] = round(-rng.uniform(0.1, 1.0), 1)
    if "Volatility indices spike above 40" in text:
        snap["VIX"] = rng.randint(41, 60)
        snap["US high-yield spread (bp)"] = round(200 + 15 * snap["VIX"] + rng.uniform(-80, 80))
    if "The yield curve inverts to its deepest level in decades" in text:
        snap["US 2y yield (%)"] = round(max(snap["US 2y yield (%)"], 2.5 + rng.uniform(0, 2.5)), 2)
        snap["US 10y yield (%)"] = round(snap["US 2y yield (%)"] - rng.uniform(0.8, 1.5), 2)
    if "Mortgage rates rise to their highest level in two decades" in text:
        snap["US 10y yield (%)"] = round(max(snap["US 10y yield (%)"], rng.uniform(4.5, 5.5)), 2)
    snap["US 2y-10y spread (bp)"] = round((snap["US 10y yield (%)"] - snap["US 2y yield (%)"]) * 100)
    snap["US core PCE y/y (%)"] = round(min(snap["US core PCE y/y (%)"], snap[cpi_key] + 1.5) if snap[cpi_key] < 0
                                        else snap["US core PCE y/y (%)"], 1)
    snap["US nominal GDP growth y/y (%)"] = round(snap["US real GDP growth 4-quarter average (%)"] + snap[cpi_key], 1)
    return snap


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
            event_text = fill(text, cfg["slots"], rng)
            ev = Event(id=f"syn-{school[0]}{i:04d}", text=event_text, category=cat,
                       macro_context=align_backdrop(event_text, macro_snapshot(rng), rng), template_id=tid)
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
        "Between the first [Observe] and [ToolCall: get_macro_data] comes the second [Think]: what the episodes imply "
        "for this event and which data would decide between the readings. Never skip a block.\n"
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
# Asset labels on signal lines; prompt version 5 named the referents ("government bonds (US Treasuries)"), and the
# teachers then wrote "US Treasuries:" or "Credit (US high yield):", so a US prefix and a parenthesis are accepted.
_US = r"(?:(?:the |broad )?(?:us |u\.s\. )?)"
ASSETS = {"equities": _US + r"equit(?:y|ies)", "government bonds":
          _US + r"(?:(?:government |sovereign |treasury )?bonds?|treasuries)",
          "US dollar": r"(?:the )?(?:us |u\.s\. )?dollar|usd|dxy", "gold": r"gold", "oil": r"(?:wti |crude )?oil",
          "credit": _US + r"(?:credit|high[- ]yield)(?: credit| bonds)?"}
ASSET_TAIL = r"(?:[ \t]*\([^)\n]*\))?"  # an optional "(US high yield)" between the label and the colon
META = re.compile(r"\b(as instructed|the (?:prompt|instructions)|I (?:must|should|need to) (?:reason|stay|think|write)"
                  r" (?:as|within|in))\b", re.I)
# Phrases the pilot-v4 teachers echoed from the prompt or the school profile (rejected from prompt version 5 on).
ECHO = re.compile(r"\bweigh(?:t|s|ing)?\b[^.\n]{0,25}\bthe event\b|\bthe event dominates\b|\bone sentence on\b|"
                  r"\b(?:this|the) school(?:'s)?\b|\bschool's rule\b", re.I)
SCENARIO = re.compile(r"^[ \t]*(S\d+)[^:\n]*:[ \t]*([01](?:\.\d+)?|\.\d+)[ \t]*$", re.M)
CONF_LEVEL = re.compile(r"^[ \t]*Confidence[ \t]*:[ \t]*(high|moderate|low)\b", re.I | re.M)


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
        m = re.search(rf"^[ \t]*[-*]?[ \t]*(?:{pat}){ASSET_TAIL}[ \t]*:[ \t]*(LONG|SHORT|NEUTRAL)[ \t]*\([ \t]*conviction[ \t]*"
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


def normalize(text: str) -> str:
    """Deterministic format clean-up before validation: 'SHORT (2)' or 'SHORT (conviction: 2)' becomes
    'SHORT (conviction 2)' on signal lines, and 'S1 (...): p 0.50' or ': probability 0.5' becomes 'S1 (...): 0.50' on
    scenario lines. Wording and content are untouched."""
    text = re.sub(r"^([ \t]*S\d+[^:\n]*:[ \t]*)(?:p|probability)[ \t]*[=:]?[ \t]*([01](?:\.\d+)?|\.\d+)[ \t]*$",
                  r"\1\2", text, flags=re.I | re.M)
    # "S1 (name): growth down, inflation flat: 0.38" -> "S1 (name; growth down, inflation flat): 0.38"
    text = re.sub(r"^([ \t]*S\d+[ \t]*)\(([^()\n]*)\)[ \t]*:[ \t]*(growth[^:\n]*?)[ \t]*:[ \t]*([01](?:\.\d+)?|\.\d+)[ \t]*$",
                  r"\1(\2; \3): \4", text, flags=re.I | re.M)
    for pat in ASSETS.values():
        text = re.sub(rf"^([ \t]*[-*]?[ \t]*(?:{pat}){ASSET_TAIL}[ \t]*:[ \t]*(?:LONG|SHORT|NEUTRAL)[ \t]*\()[ \t]*"
                      rf"(?:conviction[ \t]*:?[ \t]*)?([1-5])[ \t]*\)", r"\1conviction \2)", text, flags=re.I | re.M)
    return text


def signal_report(kept: dict[str, list[dict]], dominant: float = 0.7) -> dict:
    """Direction shares per school and asset, and warnings where one direction exceeds `dominant` (n >= 10)."""
    report: dict = {"shares": {}, "warnings": []}
    for school, recs in kept.items():
        counts: dict[str, dict[str, int]] = {a: {"LONG": 0, "SHORT": 0, "NEUTRAL": 0} for a in ASSETS}
        for r in recs:
            out = r["messages"][-1]["content"].split("[Output]")[-1]
            for asset, pat in ASSETS.items():
                m = re.search(rf"^[ \t]*[-*]?[ \t]*(?:{pat}){ASSET_TAIL}[ \t]*:[ \t]*(LONG|SHORT|NEUTRAL)", out, re.I | re.M)
                if m:
                    counts[asset][m.group(1).upper()] += 1
        report["shares"][school] = counts
        for asset, c in counts.items():
            n = sum(c.values())
            top = max(c, key=c.get)
            if n >= 10 and c[top] / n > dominant:
                report["warnings"].append(f"{school}: {asset} {top} in {c[top]}/{n}")
    return report


def record(item: Item, reply: str, teacher: str, prompt_version: int = PROMPT_VERSION) -> dict:
    """One training example in the data contract: arm-A messages plus the teacher's reply as the assistant turn."""
    msgs = build_messages("A", item.school, item.event, system=read_prompt(f"{item.school}.system.txt"),
                          user_template=read_prompt("user_template.txt"))
    return {"messages": [*msgs, {"role": "assistant", "content": reply.strip()}], "template_id": item.template_id,
            "category": item.category, "teacher": teacher, "teacher_prompt_version": prompt_version,
            "event": {"id": item.event.id, "text": item.event.text, "category": item.category,
                      "macro_context": item.event.macro_context}}


def generate(backend, items: list[Item], cfg: dict, teacher: str, out_dir: Path) -> dict:
    """Ask the teacher (a local backend) for every item and keep the valid replies (see `collect`)."""
    from mosaic.backends import Request

    reqs = [Request(messages=teacher_messages(it, cfg), tag=f"teacher|{it.school}|{it.event.id}") for it in items]
    outs = backend.generate(reqs)
    return collect(items, [o.get("text", "") for o in outs], teacher, out_dir)


def collect(items: list[Item], replies: list[str], teacher: str, out_dir: Path,
            prompt_version: int = PROMPT_VERSION) -> dict:
    """Keep valid replies, write <school>.jsonl and rejects.jsonl to out_dir; return counts per school."""
    from mosaic.backends import split_reasoning

    out_dir.mkdir(parents=True, exist_ok=True)
    kept: dict[str, list[dict]] = {s: [] for s in SCHOOLS}
    rejects = []
    for it, reply in zip(items, replies):
        reply = split_reasoning(reply or "")[1] if "<think>" in (reply or "") else (reply or "")
        reply = normalize(reply)
        problems = validate(reply, it)
        if problems:
            rejects.append({"school": it.school, "event_id": it.event.id, "template_id": it.template_id,
                            "problems": problems, "reply": reply})
        else:
            kept[it.school].append(record(it, reply, teacher, prompt_version))
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
                cfg: dict | None = None, prompt_version: int = PROMPT_VERSION) -> int:
    """Requests for scripts/teacher_api.py (or a Batch API for version 3). Version 4 requests carry the tool specs
    and the item's backdrop, which the runner needs to execute get_macro_data; the backdrop is not in the prompt."""
    cfg = cfg or load_templates()
    items = make_items(n_per_school, seed=seed, cfg=cfg)
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "requests.jsonl").open("w", encoding="utf-8") as f:
        for it in items:
            line = {"custom_id": f"{it.school}|{it.event.id}", "method": "POST", "url": "/v1/chat/completions"}
            if prompt_version >= 4:
                body = {"model": model, "messages": teacher_messages_v4(it, cfg), "tools": TOOL_SPECS,
                        "parallel_tool_calls": False, "temperature": 0.8, "top_p": 0.95, "max_tokens": max_tokens}
                line.update(body=body, protocol=4, backdrop=it.event.macro_context)
            else:
                line["body"] = {"model": model, "messages": teacher_messages(it, cfg), "temperature": 0.8,
                                "top_p": 0.95, "max_tokens": max_tokens}
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
    man = {"n_per_school": n_per_school, "seed": seed, "model": model, "requests": len(items),
           "prompt_version": prompt_version, "items_version": ITEMS_VERSION}
    if prompt_version >= 4:
        man["episodes"] = {"source": EpisodeTable.load().source, "sha256": _sha256(EPISODES)}
    (out_dir / "manifest.json").write_text(json.dumps(man, indent=1) + "\n")
    return len(items)


def reply_of(line: dict) -> tuple[str, str | list, str]:
    """(custom_id, reply, model) from an OpenAI Batch output line or a scripts/teacher_api.py line; for version 4 the
    reply is the list of turns (assistant and tool messages) after the prompt."""
    if "turns" in line:
        return line.get("custom_id", ""), line["turns"], line.get("model", "")
    body = (line.get("response") or {}).get("body") or line
    msg = ((body.get("choices") or [{}])[0].get("message") or {})
    return line.get("custom_id", ""), msg.get("content") or line.get("content") or "", body.get("model", "")


def import_results(jobs_dir: Path, results: Path, out_dir: Path) -> dict:
    man = json.loads((jobs_dir / "manifest.json").read_text())
    items_version = man.get("items_version", 1 if man.get("prompt_version", 1) < 2 else 2)
    if items_version != ITEMS_VERSION:  # items are rebuilt from (n, seed) with the current generator
        raise SystemExit(f"{jobs_dir} was made with item generator version {items_version}, the code is at "
                         f"{ITEMS_VERSION}; import it from the matching commit or regenerate")
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
    replies = [got.get(f"{it.school}|{it.event.id}", "") for it in items]
    if man.get("prompt_version", 1) >= 4:
        sha = (man.get("episodes") or {}).get("sha256")
        if sha and sha != _sha256(EPISODES):
            raise SystemExit(f"{EPISODES} changed since {jobs_dir} was run; import from the matching commit")
        counts = collect_v4(items, [r if isinstance(r, list) else [] for r in replies], teacher, out_dir,
                            man["prompt_version"])
    else:
        counts = collect(items, replies, teacher, out_dir, man.get("prompt_version", 1))
    counts["missing"] = sum(f"{it.school}|{it.event.id}" not in got for it in items)
    return counts


# ---- Prompt version 4: real tools (research/DESIGN_ontology_agents.md §3-4a) ----

AGENT = ROOT / "configs/agent"
V4_TURNS = ["assistant", "tool", "assistant", "tool", "assistant"]
V4_CALLS = {0: "query_episode_db", 2: "get_macro_data"}
PROOF_STEP = re.compile(r"^[ \t]*-[ \t]*(L[0-5])[ \t]*((?:\[[^\]\n]+\][^\[\n:]*)+):[ \t]*(\S.*)$", re.M)
PROOF_BARE = re.compile(r"^[ \t]*-[ \t]*(L[0-5])[ \t]+([^\[\]\n:]+?):[ \t]+(\S.*)$", re.M)  # refs without brackets
PROOF_REF = re.compile(r"\[([^\]\n]+)\]")
REF_SPLIT = re.compile(r"\s*(?:[,;&]|\s/\s|\bvs\.?\b|\band\b|\bwith\b|\bagainst\b)\s*")  # not the / of y/y
REF_VALUE = re.compile(r"(?:\s+[-+]?\d[\d.,]*\s*(?:%|bp|pp)?)+$")
CONFIDENCE = re.compile(r"^[ \t]*Confidence[ \t]*:[ \t]*(high|moderate|low)\b[^\n]*weakest link[ \t]*:[ \t]*\S", re.I | re.M)


def _sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def teacher_messages_v4(item: Item, cfg: dict) -> list[dict]:
    """The teacher's prompt for a real-tool trajectory (prompt version 5): the school, the event and the protocol,
    no backdrop values (they come from get_macro_data). The wording avoids every phrase the pilot-v4 teachers echoed
    ("weigh the event more", "as this school reads it") and defines probabilities, confidence and the asset referents
    instead of leaving defaults to the teacher."""
    sch = cfg["school"][item.school]
    name = item.school.capitalize()
    names = ", ".join(item.event.macro_context)
    system = (
        "You write training data for a tool-using economist agent that reasons within one school of thought. You act "
        "as the agent: your visible text is its reasoning, and your tool calls are executed for real, with the results "
        "returned to you. It must read like a careful analyst at work, not a checklist: use the one or two mechanisms "
        "that matter for this event, not every concept the school has. Write in the first person as the economist; never "
        "call yourself the school. Never state an indicator value or a historical episode that a tool did not return; "
        "nothing after 2024 exists for you.")
    user = (
        f"School: {name}.\n"
        f"How a {name} economist diagnoses: {sch['diagnosis']}\n"
        f"Mechanisms to draw on (pick what fits, do not list them all): {', '.join(sch['concepts'])}.\n"
        f"Typical stance: {sch['signals']}. It is not always bearish; it reads these as good news: "
        f"{'; '.join(sch['good_news'])}.\n\n"
        f"Event (category: {item.category}): {item.event.text}\n\n"
        "Tools: query_episode_db returns dated historical episodes, all earlier than the event; get_macro_data returns "
        f"US/global indicators known before the event (there are no data for other economies). Indicator names: {names}."
        "\n\n"
        "Work in three messages, one tool call per message:\n"
        '1. Start with "[Think]" on its own line: is the event good or bad news for growth and for inflation, and how '
        "large is it, judged from what the event says? Then call query_episode_db with a short description of the "
        "situation.\n"
        '2. Start with "[Think]": which returned episodes fit this event and where they differ (describe them only as '
        "far as the tool text goes), and which data would decide between the readings. Then call get_macro_data with "
        "those indicators and every indicator your signals will rely on (for example WTI for oil).\n"
        '3. Start with "[Think]": combine the event, the episodes and the data. The data predate the event, so never read '
        "a yield, spread, rate or growth figure as the event's effect. Mention a contradiction only when the event "
        "states a level the data contradict, and say which you rely on. If the event concerns another economy, say how "
        "it reaches US and global assets and which foreign variable you lack; never judge another economy with US data. "
        "Annualise monthly figures before comparing them with yearly rates. Then write, each tag on its own line:\n"
        "[Output]\n"
        f"Causal chain: event -> ... -> outcome, in {name} terms.\n"
        "Scenarios: 2-4 lines 'S1 (event-specific name; growth up/down/flat, inflation up/down/flat): 0.xx' for the "
        "US/global economy against a no-event baseline, each scenario differing in direction, no colon inside the "
        "parentheses, the numbers summing to 1 and set by this event: a small, contained or well-precedented event can "
        "put 0.6-0.85 on its base case, an ambiguous or large one spreads the mass.\n"
        "Signals: one line each for equities (broad US index), government bonds (US Treasuries), US dollar (DXY), "
        "gold, oil and credit (US high yield), as 'asset: LONG|SHORT|NEUTRAL (conviction 1-5) - reason', the reason "
        "naming what in this event moves the asset and which scenarios carry the call. A call resting on scenarios "
        "that total under 0.4 is NEUTRAL or conviction 1; a call driven by the data rather than the event says so and "
        "has conviction 2 or less; a small or remote event gets NEUTRAL. No asset has a default direction.\n"
        "[Proof]\n"
        "4-7 lines in reasoning order, each '- Lk [ref]: claim': L1 with an indicator name get_macro_data returned, L2 "
        "with an episode id query_episode_db returned (like EP-1994-02), L3 with the name of the mechanism you apply, "
        "and one L5 with the most likely scenario (S1, S2, ...). At least one line of each kind.\n"
        "Confidence: high when the data, the episodes and the mechanism agree; low when the deciding link is "
        "unobserved or the episodes fit poorly; otherwise moderate. Write 'Confidence: high|moderate|low; weakest "
        "link: ...'.\n\n"
        "Write about what the event says, not about what it omits, and do not mention other schools or these "
        "instructions.")
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _one_line(arguments) -> str:
    try:
        obj = json.loads(arguments) if isinstance(arguments, str) else arguments
        return json.dumps(obj, ensure_ascii=False)
    except ValueError:
        return str(arguments).replace("\n", " ")


def strip_proof(text: str) -> str:
    i = text.find("[Proof]")
    return text[:i].rstrip() if i >= 0 else text


def flatten(turns: list[dict], proof: bool = False) -> str:
    """The Confirmation single-pass text of a v4 conversation: each tool call becomes a [ToolCall: name] line with its
    JSON arguments and each tool result an [Observe] block, in the order they happened. Without `proof` the [Proof]
    block is dropped (exp01's registered output format ends with [Output])."""
    parts = []
    for t in turns:
        if t.get("role") == "assistant":
            parts.append((t.get("content") or "").strip())
            for c in t.get("tool_calls") or []:
                fn = c.get("function") or {}
                parts.append(f"[ToolCall: {fn.get('name', '')}]\n{_one_line(fn.get('arguments', '{}'))}")
        elif t.get("role") == "tool":
            parts.append(f"[Observe]\n{(t.get('content') or '').strip()}")
    text = "\n".join(p for p in parts if p)
    return text if proof else strip_proof(text)


def proof_problems(final: str, l1: set[str], l2: set[str], facts: MacroFacts, max_steps: int = 10,
                   modal: str | None = None) -> list[str]:
    """The [Proof] block must type every step by layer and cite only what the tools returned (grounded); from prompt
    version 5 on it has at most 8 steps and an L5 step naming the most likely scenario (`modal`)."""
    i = final.find("[Proof]")
    if i < 0:
        return ["missing [Proof] block"]
    block = final[i + len("[Proof]"):]
    steps = PROOF_STEP.findall(block) + [(k, f"[{r}]", c) for k, r, c in PROOF_BARE.findall(block)]
    problems = [] if 4 <= len(steps) <= max_steps else [f"{len(steps)} proof steps (4-{max_steps} accepted)"]
    if modal and not any(k == "L5" and modal in REF_SPLIT.split(" ".join(PROOF_REF.findall(refs)))
                         for k, refs, _ in steps):
        problems.append(f"no L5 step names the most likely scenario {modal}")
    kinds = {k for k, _, _ in steps}
    problems += [f"proof has no {k} step" for k in ("L1", "L2", "L3", "L5") if k not in kinds]
    for k, refs, _ in steps:
        for ref in (r.strip() for r in PROOF_REF.findall(refs)):
            # "[A, B]", "[A / B]", "[A 1.0 vs B 5.5]" cite two refs when the whole is not one name; values are dropped
            parts = [ref] if (k == "L1" and facts.resolve(ref)) or (k == "L2" and ref in l2) else \
                [REF_VALUE.sub("", x).strip() for x in REF_SPLIT.split(ref) if x.strip()]
            for part in (x for x in parts if x):
                if k == "L1" and facts.resolve(part) not in l1:
                    problems.append(f"proof cites an indicator the tool did not return: {part}")
                elif k == "L2" and part not in l2:
                    problems.append(f"proof cites an episode the tool did not return: {part}")
    if not CONFIDENCE.search(block):
        problems.append("proof has no confidence line")
    return problems


def check_v4(item: Item, turns: list[dict], episodes: EpisodeTable,
             prompt_version: int = PROMPT_VERSION) -> tuple[list[str], list[dict]]:
    """(problems, normalised turns) for one v4 conversation. The tool calls are executed again here, so a result that
    does not match the deterministic tools (or an edited table) is caught, and the proof is checked against the refs
    the tools really returned. The text checks of version 3 run on the flattened conversation."""
    roles = [t.get("role") for t in turns]
    if roles != V4_TURNS:
        return [f"protocol: turns {roles}, expected {V4_TURNS}"], turns
    problems = []
    for i, name in V4_CALLS.items():
        calls = turns[i].get("tool_calls") or []
        if len(calls) != 1 or (calls[0].get("function") or {}).get("name") != name:
            problems.append(f"protocol: message {i // 2 + 1} must call {name} once")
    if turns[4].get("tool_calls"):
        problems.append("protocol: the final message calls a tool")
    if problems:
        return problems, turns
    turns = [dict(t) for t in turns]
    turns[4]["content"] = normalize(turns[4].get("content") or "")
    for i in (0, 2, 4):
        if not (turns[i].get("content") or "").lstrip().startswith("[Think]"):
            problems.append(f"protocol: message {i // 2 + 1} does not start with [Think]")
    facts = MacroFacts(item.event.macro_context)
    box = ToolBox(facts, episodes)
    refs: dict[str, set[str]] = {"L1": set(), "L2": set()}
    for i in V4_CALLS:
        fn = turns[i]["tool_calls"][0]["function"]
        res = box.execute(fn["name"], fn.get("arguments", "{}"))
        if res.layer == "error":
            problems.append(f"tool error: {res.text}")
        elif (turns[i + 1].get("content") or "").strip() != res.text.strip():
            problems.append(f"tool result of {fn['name']} differs from a re-run of the tool")
        refs.setdefault(res.layer, set()).update(res.refs)
    problems += validate(flatten(turns), item)
    final = turns[4]["content"]
    if prompt_version >= 5:
        said = " ".join(turns[i].get("content") or "" for i in (0, 2, 4))
        echoes = sorted({m.group(0).lower() for m in ECHO.finditer(said)})
        if echoes:
            problems.append(f"repeats a prompt phrase: {', '.join(echoes)}")
        scen = SCENARIO.findall(final[final.rfind("[Output]"):]) if "[Output]" in final else []
        modal = max(scen, key=lambda x: float(x[1]))[0] if scen else None
        problems += proof_problems(final, refs["L1"], refs["L2"], facts, max_steps=10, modal=modal)
    else:
        problems += proof_problems(final, refs["L1"], refs["L2"], facts)
    return problems, turns


def agent_messages(item: Item) -> list[dict]:
    """System and user messages of the agent format: the school's prompt plus the tool note; the event without the
    backdrop, which the agent has to fetch."""
    note = (AGENT / "system_note.txt").read_text(encoding="utf-8").strip()
    system = read_prompt(f"{item.school}.system.txt").strip() + "\n\n" + note.format(
        indicators=", ".join(item.event.macro_context))
    user = (AGENT / "user_template.txt").read_text(encoding="utf-8").strip().format(
        event_id=item.event.id, category=item.category or "unspecified", event_text=item.event.text)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _clean(turn: dict) -> dict:
    keep = ("role", "content", "tool_calls", "tool_call_id", "name")
    out = {k: turn[k] for k in keep if k in turn}
    if "tool_calls" in out:
        out["tool_calls"] = [{"id": c.get("id", ""), "type": "function",
                              "function": {"name": c["function"]["name"],
                                           "arguments": _one_line(c["function"].get("arguments", "{}"))}}
                             for c in out["tool_calls"]]
    return out


def record_v4(item: Item, turns: list[dict], teacher: str, prompt_version: int = PROMPT_VERSION) -> tuple[dict, dict]:
    """(single-pass record for exp01 arm C, agent record for C-agent) from one checked conversation."""
    single = record(item, flatten(turns), teacher, prompt_version)
    single["format"] = "single"
    agent = {k: v for k, v in single.items() if k != "messages"}
    agent.update(messages=[*agent_messages(item), *(_clean(t) for t in turns)], tools=TOOL_SPECS, format="agent")
    return single, agent


def collect_v4(items: list[Item], results: list[list[dict]], teacher: str, out_dir: Path,
               prompt_version: int = PROMPT_VERSION) -> dict:
    """Check every conversation; write <school>.jsonl (single-pass, exp01 arm C), agent/<school>.jsonl (C-agent),
    rejects.jsonl and report.json to out_dir; return counts per school."""
    episodes = EpisodeTable.load()
    (out_dir / "agent").mkdir(parents=True, exist_ok=True)
    single: dict[str, list[dict]] = {s: [] for s in SCHOOLS}
    agent: dict[str, list[dict]] = {s: [] for s in SCHOOLS}
    rejects = []
    for it, turns in zip(items, results):
        problems, turns = check_v4(it, turns, episodes, prompt_version) if turns else (["no reply"], turns)
        if problems:
            rejects.append({"school": it.school, "event_id": it.event.id, "template_id": it.template_id,
                            "problems": problems, "turns": turns})
            continue
        a, b = record_v4(it, turns, teacher, prompt_version)
        single[it.school].append(a)
        agent[it.school].append(b)
    for school in SCHOOLS:
        for path, recs in ((out_dir / f"{school}.jsonl", single[school]),
                           (out_dir / "agent" / f"{school}.jsonl", agent[school])):
            with path.open("w", encoding="utf-8") as f:
                f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in recs)
    with (out_dir / "rejects.jsonl").open("w", encoding="utf-8") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rejects)
    report = signal_report(single, dominant=0.65 if prompt_version >= 5 else 0.7)
    report["batch"] = batch_report(agent)
    report["warnings"] += report["batch"]["warnings"]
    (out_dir / "report.json").write_text(json.dumps(report, indent=1) + "\n")
    counts: dict = {s: len(v) for s, v in single.items()}
    counts["rejected"] = len(rejects)
    counts["warnings"] = report["warnings"]
    return counts


STRUCTURAL = set("think output proof signals signal scenarios scenario causal chain confidence weakest link conviction "
                 "long short neutral growth inflation up down flat equities bonds government dollar us gold oil credit "
                 "the a an of and to in on for is it as by with that this from at or be".split())


def batch_report(kept: dict[str, list[dict]], phrase_share: float = 0.25) -> dict:
    """Calibration and repetition per school (pilot-v4 review): the share of items whose most likely scenario sits in
    0.40-0.55, probability tuples used more than twice, the confidence levels, and 5-word phrases (not made of format
    words) shared by more than `phrase_share` of the items. Records in the agent format."""
    from collections import Counter

    out: dict = {"schools": {}, "warnings": []}
    for school, recs in kept.items():
        if not recs:
            continue
        tops, tuples, conf, grams = [], Counter(), Counter(), Counter()
        for r in recs:
            said = [m.get("content") or "" for m in r["messages"] if m["role"] == "assistant"]
            final = said[-1]
            probs = [float(p) for _, p in SCENARIO.findall(final[final.rfind("[Output]"):])] if "[Output]" in final else []
            if probs:
                tops.append(max(probs))
                tuples[tuple(sorted(probs, reverse=True))] += 1
            m = CONF_LEVEL.search(final)
            conf[m.group(1).lower() if m else "missing"] += 1
            words = re.findall(r"[a-z][a-z']*", " ".join(said).lower())
            grams.update({tuple(words[i:i + 5]) for i in range(len(words) - 4)})
        n = len(recs)
        mid = sum(0.40 <= t <= 0.55 for t in tops) / n
        repeated = {"/".join(f"{x:g}" for x in k): v for k, v in tuples.items() if v > 2}
        common = [(" ".join(g), round(c / n, 2)) for g, c in grams.most_common(2000)
                  if c / n > phrase_share and sum(w in STRUCTURAL for w in g) <= 2][:10]
        top_level, top_n = conf.most_common(1)[0]
        out["schools"][school] = {"n": n, "modal_in_0.40_0.55": round(mid, 2), "repeated_tuples": repeated,
                                  "confidence": dict(conf), "common_phrases": common}
        if mid > 0.6:
            out["warnings"].append(f"{school}: most likely scenario at 0.40-0.55 in {mid:.0%} of items")
        if repeated:
            out["warnings"].append(f"{school}: probability tuples used more than twice: {repeated}")
        if top_n / n > 0.7:
            out["warnings"].append(f"{school}: confidence '{top_level}' in {top_n / n:.0%} of items")
        out["warnings"] += [f"{school}: phrase '{g}' in {sh:.0%} of items" for g, sh in common[:5]]
    return out
