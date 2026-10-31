"""exp03 runner and scorers (Task 2, step 5): prompts from question + point-in-time context, per-bin probability
parsing, RPS / log score / Brier / ECE, pools, and a calibration-window pilot of format compliance.

  python -m mosaic exp03 pilot --limit 10 [--backend fake] [--systems K,A,M]

Rules (program.md): nothing here ever reads a question of the test window. `load_questions` refuses it unless the
caller passes `allow_test=True`, which only the registered, human-run final may do (it does not exist yet), and the
pilot passes window="calibration" with at most 10 questions. The scorers are the draft's primary and secondary
metrics; the pre-registration (human) is what makes them binding.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

from mosaic.config import ROOT

RAW_DIR = ROOT / "data" / "exp03"
MAX_PILOT = 10
SAMPLES = 3
LOG_FLOOR = 0.01
SUM_RANGE = (0.8, 1.2)

# --- questions ---------------------------------------------------------------------------------------------


def load_questions(window: str = "calibration", limit: int | None = None, path: Path | None = None,
                   allow_test: bool = False) -> list[dict]:
    if window == "test" and not allow_test:
        raise SystemExit("the test window is not yours (program.md, rule 1)")
    path = path or RAW_DIR / "questions.jsonl"
    qs = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    qs = [q for q in qs if q["window"] == window]
    return qs[:limit] if limit else qs


def scenario_ids(q: dict) -> list[str]:
    return [f"S{i + 1}" for i in range(len(q["bins"]))]


SERIES_TEXT = {
    "us_cpi_mom": "US consumer price index (CPI-U, all items), month-over-month change, first print",
    "us_core_cpi_mom": "US core CPI (all items less food and energy), month-over-month change, first print",
    "us_cpi_yoy": "US CPI-U (all items), year-over-year change, first print",
    "us_core_cpi_yoy": "US core CPI, year-over-year change, first print",
    "us_unemployment": "US unemployment rate (U-3), first print",
    "us_real_gdp_qoq_saar": "US real GDP growth, quarterly, annualised, advance estimate",
    "fed_change": "change of the Fed's target range at the FOMC meeting",
}


def event_text(q: dict, horizon: str = "7") -> str:
    """Description plus the scenario list in the [Output] format the schools were trained on. No market prices."""
    what = SERIES_TEXT.get(q["series"], q["series"].replace("_", " ").replace("change", "policy rate decision"))
    lines = [f"Forecast question: {what}; reference period {q['period'] or 'n/a'}.",
             f"Resolution: the published value falls in exactly one of the scenarios below. "
             f"Forecast date: {q['forecast_date'][horizon]} (information up to this date only).", "",
             "Scenarios (mutually exclusive, ordered from lowest to highest):"]
    lines += [f"{sid}: {b['label']}" for sid, b in zip(scenario_ids(q), q["bins"])]
    lines += ["", "In your [Output] block, under 'Scenario probabilities', write one line per scenario in the form "
                  "'S1: 0.25' (a probability between 0 and 1); the probabilities must sum to 1."]
    return "\n".join(lines)


def macro_block(ctx: list[dict] | None) -> dict | str:
    """macro_context for `prompts.user_message`: 'name: v1 (date), ...' per indicator, only what was published."""
    if not ctx:
        return "(not provided)"
    out = {}
    for c in ctx:
        if c["last"]:
            out[c["name"]] = ", ".join(f"{v:g} ({d})" for d, v in c["last"])
    return out or "(not provided)"


# --- parsing -----------------------------------------------------------------------------------------------

_NUM = r"(0?\.\d+|1(?:\.0+)?|0|\d{1,3}(?:\.\d+)?\s*%)"


def _val(tok: str) -> float:
    tok = tok.strip()
    return float(tok.rstrip("%")) / 100 if tok.endswith("%") else float(tok)


def parse_bins(text: str, q: dict) -> list[float] | None:
    """Per-bin probabilities from the [Output] block ('S3: 0.25' or 'S3 ... 25%'), renormalised when their sum is
    within SUM_RANGE; None when invalid (a bin missing, a value outside [0,1], or the sum out of range)."""
    heads = list(re.finditer(r"\[\s*Output\s*\]", text, re.I))
    out = text[heads[-1].end():] if heads else text
    got = {}
    for sid in scenario_ids(q):
        m = re.search(rf"(?<![A-Za-z0-9])\**{sid}\b\**[^\n\d]*?[:=\-–)]*\s*\**\s*{_NUM}(?![\d.]*\d)", out)
        if not m:
            return None
        v = _val(m.group(1))
        if not 0.0 <= v <= 1.0:
            return None
        got[sid] = v
    total = sum(got.values())
    if not SUM_RANGE[0] <= total <= SUM_RANGE[1]:
        return None
    return [got[s] / total for s in scenario_ids(q)]


def forecast_from_samples(samples: list[list[float] | None], k: int) -> tuple[list[float], bool]:
    """(forecast, format_failure): the mean of valid samples, uniform when none is valid."""
    ok = [s for s in samples if s is not None]
    if not ok:
        return [1.0 / k] * k, True
    return [sum(c) / len(ok) for c in zip(*ok)], False


# --- scorers -----------------------------------------------------------------------------------------------

def rps(p: list[float], k: int) -> float:
    """Ranked probability score of one forecast with realised bin index k (ordered bins; 0 = perfect)."""
    n, cp, co, s = len(p), 0.0, 0.0, 0.0
    for j in range(n - 1):
        cp += p[j]
        co += 1.0 if j >= k else 0.0
        s += (cp - co) ** 2
    return s / (n - 1)


def log_score(p: list[float], k: int, floor: float = LOG_FLOOR) -> float:
    return -math.log(max(p[k], floor))


def contract_prob(p: list[float], q: dict, c: dict) -> float:
    """Model probability of one binary contract: the mass of the elementary bins inside its span."""
    tot = 0.0
    for pi, b in zip(p, q["bins"]):
        lo = -math.inf if b["lo"] is None else b["lo"]
        hi = math.inf if b["hi"] is None else b["hi"]
        clo = -math.inf if c["lo"] is None else c["lo"]
        chi = math.inf if c["hi"] is None else c["hi"]
        if clo <= lo and hi <= chi:
            tot += pi
    return tot


def brier(p: list[float], q: dict) -> float:
    cs = q["contracts"]
    return sum((contract_prob(p, q, c) - c["result"]) ** 2 for c in cs) / len(cs)


def ece(pairs: list[tuple[float, int]], bins: int = 10) -> float:
    """Expected calibration error over (probability, outcome) pairs, equal-width bins."""
    if not pairs:
        return float("nan")
    tot, n = 0.0, len(pairs)
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        sel = [(p, y) for p, y in pairs if lo <= p < hi or (b == bins - 1 and p == 1.0)]
        if sel:
            tot += len(sel) / n * abs(sum(p for p, _ in sel) / len(sel) - sum(y for _, y in sel) / len(sel))
    return tot


def pool_equal(forecasts: list[list[float]]) -> list[float]:
    return [sum(c) / len(forecasts) for c in zip(*forecasts)]


def uniform(k: int) -> list[float]:
    return [1.0 / k] * k


# --- pilot -------------------------------------------------------------------------------------------------

def pilot(systems: list[str], limit: int = MAX_PILOT, backend: str | None = None, window: str = "calibration") -> dict:
    """Format-compliance pilot on <= 10 calibration questions: parse rate per system. Scores nothing, writes
    runs/exp03-pilot-<utc>/ with the raw generations. Adapters need `mosaic train` (Task 0): a missing adapter dir
    stops the pilot for that system and says so."""
    from datetime import datetime, timezone

    from mosaic.backends import Cache, FakeBackend, Request, VLLMBackend
    from mosaic.config import adapters_root, load_toml, paths
    from mosaic.data import Event
    from mosaic.prompts import build_messages, read_prompt

    if window != "calibration":
        raise SystemExit("the pilot runs on the calibration window only")
    limit = min(limit, MAX_PILOT)
    qs = load_questions("calibration", limit)
    ctxf = RAW_DIR / "contexts.jsonl"
    ctx = {}
    if ctxf.exists():
        for x in ctxf.read_text(encoding="utf-8").splitlines():
            r = json.loads(x)
            ctx[(r["question_id"], r["horizon"])] = r["indicators"]
    cfg = load_toml(ROOT / "configs/exp01.toml")
    user_t = read_prompt("user_template.txt")
    short = {"K": "keynesian", "A": "austrian", "M": "monetarist"}
    cache = Cache(ROOT / "cache/generations.jsonl")
    utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = ROOT / "runs" / f"exp03-pilot-{utc}"
    out_dir.mkdir(parents=True)
    report, rows = {}, []
    for sysname in systems:
        school = short.get(sysname.rstrip("'")) or SCHOOLS_OK(sysname)
        adapter = school if (sysname in short and "'" not in sysname) else None
        system = (read_prompt(f"{school}.system.txt") if school != "neutral"
                  else read_prompt("neutral.txt", ROOT / "configs/exp03_prompts"))
        samples_p = []
        for i in range(SAMPLES):
            sampling = {**cfg["sampling"], "seed": int(cfg["sampling"]["seed"]) + i}
            if backend == "fake":
                be = FakeBackend(sampling, cache)
            else:
                m = cfg["model"]
                root = adapters_root(m, paths())
                if adapter and not (root / adapter).exists():
                    report[sysname] = f"adapter {root / adapter} missing: run Task 0 `mosaic train` first"
                    break
                be = VLLMBackend(sampling, cache, base_model=m["base"],
                                 adapters={adapter: str(root / adapter)} if adapter else {},
                                 max_model_len=m.get("max_model_len", 16384),
                                 gpu_memory_utilization=m.get("gpu_memory_utilization", 0.9),
                                 max_lora_rank=m.get("max_lora_rank", 32),
                                 chat_template_kwargs=m.get("chat_template_kwargs"))
            reqs = []
            for q in qs:
                ev = Event(q["question_id"], event_text(q), category="macro release",
                           macro_context=macro_block(ctx.get((q["question_id"], "7"))))
                reqs.append(Request(build_messages("C" if adapter else "A", school, ev, system=system,
                                                   user_template=user_t), adapter=adapter,
                                    tag=f"exp03|{sysname}|{q['question_id']}|{i}"))
            gens = be.generate(reqs)
            samples_p.append([parse_bins(g["text"], q) for g, q in zip(gens, qs)])
            rows += [{"system": sysname, "question_id": q["question_id"], "sample": i, "text": g["text"],
                      "valid": s is not None} for g, q, s in zip(gens, qs, samples_p[-1])]
        if samples_p and len(samples_p) == SAMPLES:
            flat = [s for ss in samples_p for s in ss]
            ev_fail = sum(all(samples_p[i][j] is None for i in range(SAMPLES)) for j in range(len(qs)))
            report[sysname] = {"parse_rate": round(sum(s is not None for s in flat) / len(flat), 3),
                               "format_failures": f"{ev_fail}/{len(qs)} events with no valid sample"}
    (out_dir / "generations.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
                                               encoding="utf-8")
    (out_dir / "report.json").write_text(json.dumps({"window": window, "n_questions": len(qs), "systems": report,
                                                     "backend": backend or "vllm"}, indent=1), encoding="utf-8")
    return {"run_dir": str(out_dir), "n_questions": len(qs), "systems": report}


def SCHOOLS_OK(name: str) -> str:
    if name == "base":
        return "neutral"
    raise SystemExit(f"unknown system {name!r}: use base, K, A, M, K', A', M'")
