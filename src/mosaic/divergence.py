"""Disagreement matrix between L3 frameworks (research/DESIGN_ontology_agents.md, decision 2).

Each framework analyses the same dev template events in one pass (no tools); the signals and the scenario mass are
compared pairwise. Two frameworks are run twice, so between-framework distances can be read against the noise of
running the same framework again. Evaluation only: nothing here becomes training data. Standard library only.

The measures are established ones: the pairwise disagreement measure of ensemble diversity (Kuncheva & Whitaker 2003,
the share of items on which two members' outputs differ), here over events x assets; and forecast dispersion across
forecasters (Mankiw, Reis & Wolfers 2003), here the standard deviation across frameworks of the expected growth and
inflation direction per event. The frameworks' positions on two literature dimensions (configs/frameworks.toml,
expert-coded as in the Chapel Hill Expert Survey) are compared with the measured disagreement, as text-based party
positions are validated against expert surveys (Laver, Benoit & Garry 2003).
"""

from __future__ import annotations

import json
import re
import tomllib
from itertools import combinations
from pathlib import Path

from mosaic.config import ROOT
from mosaic.teacher import ASSET_TAIL, ASSETS, load_templates, make_items, normalize

FRAMEWORKS = ROOT / "configs/frameworks.toml"
DIRECTION = {"LONG": 1, "SHORT": -1, "NEUTRAL": 0}
STEP = {"up": 1, "flat": 0, "down": -1}
SCEN = re.compile(r"^[ \t]*S\d+[ \t]*\(([^()\n]*)\)[ \t]*:[ \t]*([01](?:\.\d+)?|\.\d+)[ \t]*$", re.M)


def profiles() -> dict[str, dict]:
    """The three trained schools (templates.toml) and the candidate frameworks (frameworks.toml)."""
    out = {}
    for name, sch in load_templates()["school"].items():
        out[name] = {"label": name.capitalize(), **sch}
    for name, fw in tomllib.loads(FRAMEWORKS.read_text(encoding="utf-8"))["framework"].items():
        out[name] = fw
    return out


def messages(prof: dict, event) -> list[dict]:
    ctx = "\n".join(f"- {k}: {v}" for k, v in event.macro_context.items())
    system = ("You are an economist who reasons strictly within one framework. Analyse the event as that framework "
              "does, in its own terms, and cite no other framework.")
    user = (f"Framework: {prof['label']}.\n"
            f"How it diagnoses: {prof['diagnosis']}\n"
            f"Mechanisms to draw on (pick what fits): {', '.join(prof['concepts'])}.\n"
            f"Typical stance: {prof['signals']}. It reads these as good news: {'; '.join(prof['good_news'])}.\n\n"
            f"Event (category: {event.category}): {event.text}\n\n"
            f"US/global data known before the event:\n{ctx}\n\n"
            "Write, each tag on its own line:\n"
            "[Think]\n3-6 sentences of reasoning within the framework.\n"
            "[Output]\n"
            "Causal chain: event -> ... -> outcome.\n"
            "Scenarios: 2-4 lines 'S1 (event-specific name; growth up/down/flat, inflation up/down/flat): 0.xx' for "
            "the US/global economy against a no-event baseline, the numbers summing to 1.\n"
            "Signals: one line each, labelled exactly equities, government bonds, US dollar, gold, oil, credit, as "
            "'asset: LONG|SHORT|NEUTRAL (conviction 1-5) - reason'. No asset has a default direction.")
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def export(out_dir: Path, n_events: int = 30, seed: int = 11, model: str = "qwen3.8-max",
           repeats: tuple[str, ...] = ("keynesian", "new_keynesian")) -> int:
    """requests.jsonl for scripts/teacher_api.py: every framework on the same events (seed 11: neither the teacher's
    training items, seed 0, nor the agent spike's, seed 7), the `repeats` frameworks a second time."""
    events = [it.event for it in make_items(n_events, seed=seed) if it.school == "keynesian"][:n_events]
    profs = profiles()
    out_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    with (out_dir / "requests.jsonl").open("w", encoding="utf-8") as f:
        for name, prof in profs.items():
            for rep in range(2 if name in repeats else 1):
                for ev in events:
                    body = {"model": model, "messages": messages(prof, ev), "temperature": 0.8, "top_p": 0.95,
                            "max_tokens": 1500}
                    f.write(json.dumps({"custom_id": f"{name}|{rep}|{ev.id}", "body": body}, ensure_ascii=False) + "\n")
                    n += 1
    (out_dir / "manifest.json").write_text(json.dumps({"n_events": n_events, "seed": seed, "model": model,
                                                       "frameworks": list(profs), "repeats": list(repeats),
                                                       "requests": n}, indent=1) + "\n")
    return n


def parse(text: str) -> dict | None:
    """Signal directions per asset and the expected growth and inflation direction of the scenario mass."""
    text = normalize(text or "")
    out = text[text.rfind("[Output]"):] if "[Output]" in text else text
    sig = {}
    for asset, pat in ASSETS.items():
        m = re.search(rf"^[ \t]*[-*]?[ \t]*(?:{pat}){ASSET_TAIL}[ \t]*:[ \t]*(LONG|SHORT|NEUTRAL)", out, re.I | re.M)
        if m:
            sig[asset] = DIRECTION[m.group(1).upper()]
    g = i = total = 0.0
    for inner, p in SCEN.findall(out):
        gm = re.search(r"growth\s+(up|down|flat)", inner, re.I)
        im = re.search(r"inflation\s+(up|down|flat)", inner, re.I)
        if gm and im:
            p = float(p)
            g += p * STEP[gm.group(1).lower()]
            i += p * STEP[im.group(1).lower()]
            total += p
    if len(sig) < 6 or total < 0.8:
        return None
    return {"signals": sig, "growth": g / total, "inflation": i / total}


def distance(a: dict, b: dict) -> dict:
    """Over the events both parsed: signal disagreement (0 same, 0.5 one NEUTRAL, 1 opposite, averaged over assets),
    the share of opposite calls, and the gap in expected growth plus expected inflation direction (0-4)."""
    common = sorted(set(a) & set(b))
    if not common:
        return {"n": 0}
    sig = opp = macro = kw = 0.0
    for e in common:
        da, db = a[e]["signals"], b[e]["signals"]
        sig += sum(abs(da[x] - db[x]) / 2 for x in ASSETS) / len(ASSETS)
        kw += sum(da[x] != db[x] for x in ASSETS) / len(ASSETS)
        opp += sum(da[x] * db[x] == -1 for x in ASSETS) / len(ASSETS)
        macro += abs(a[e]["growth"] - b[e]["growth"]) + abs(a[e]["inflation"] - b[e]["inflation"])
    k = len(common)
    return {"n": k, "disagreement": round(kw / k, 3), "signals": round(sig / k, 3), "opposite": round(opp / k, 3),
            "macro": round(macro / k, 3)}


def dispersion(runs: dict[str, dict]) -> dict:
    """Mean over events of the standard deviation across frameworks of expected growth and inflation direction."""
    import statistics

    events = set.intersection(*(set(r) for r in runs.values())) if runs else set()
    out = {}
    for key in ("growth", "inflation"):
        sds = [statistics.pstdev([r[e][key] for r in runs.values()]) for e in events]
        out[key] = round(sum(sds) / len(sds), 3) if sds else None
    return {"events": len(events), **out}


def spearman(x: list[float], y: list[float]) -> float | None:
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2
            i = j + 1
        return r
    if len(x) < 3:
        return None
    rx, ry = ranks(x), ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return round(num / den, 3) if den else None


def position_test(pairs: dict, names: list[str], pos: dict, measure: str = "disagreement") -> dict:
    """Spearman between literature distance and measured disagreement, per axis and summed, with an exact one-sided
    permutation p-value over relabellings of the frameworks (a Mantel-type test: pairs share frameworks, so they are not
    independent and the usual Spearman p-value would be too small)."""
    from itertools import permutations

    named = [n for n in names if n in pos]
    combos = list(combinations(named, 2))
    if len(named) < 4 or len(named) > 8:
        return {}
    y = [(pairs.get(f"{a}|{b}") or pairs.get(f"{b}|{a}"))[measure] for a, b in combos]
    out = {}
    for label, axes in (("both", ("state_market", "orthodoxy")), ("state_market", ("state_market",)),
                        ("orthodoxy", ("orthodoxy",))):
        def theory(lab):
            return [sum(abs(pos[lab[a]][d] - pos[lab[b]][d]) for d in axes) for a, b in combos]
        rho = spearman(theory({n: n for n in named}), y)
        if rho is None:
            continue
        hits = total = 0
        for perm in permutations(named):
            r = spearman(theory(dict(zip(named, perm))), y)
            total += 1
            hits += r is not None and r >= rho - 1e-12
        out[label] = {"rho": rho, "p_one_sided": round(hits / total, 3), "permutations": total}
    return out


def per_asset(runs: dict[str, dict], names: list[str]) -> dict:
    """Share of events on which two frameworks make a different call, per asset, averaged over all pairs."""
    out = {}
    for x in ASSETS:
        vals = []
        for a, b in combinations(names, 2):
            common = set(runs[a]) & set(runs[b])
            if common:
                vals.append(sum(runs[a][e]["signals"][x] != runs[b][e]["signals"][x] for e in common) / len(common))
        out[x] = round(sum(vals) / len(vals), 3) if vals else None
    return out


def space(pairs: dict, names: list[str], pos: dict) -> dict:
    """How many dimensions the measured disagreement needs, and whether both literature axes explain it.

    Classical multidimensional scaling of the pairwise disagreement matrix (as spatial models in political science
    recover positions from votes, e.g. Poole & Rosenthal's NOMINATE) gives each framework coordinates and the share of
    variance per dimension; an OLS of pairwise disagreement on the distance along each literature axis shows whether
    the axes are separate dimensions (both coefficients positive) or one (the second adds nothing). Needs numpy."""
    try:
        import numpy as np
    except ImportError:
        return {}
    n = len(names)
    d = np.zeros((n, n))
    for i, a in enumerate(names):
        for j, b in enumerate(names):
            if i != j:
                v = pairs.get(f"{a}|{b}") or pairs.get(f"{b}|{a}")
                d[i, j] = v["disagreement"]
    j = np.eye(n) - np.ones((n, n)) / n
    b = -0.5 * j @ (d ** 2) @ j
    vals, vecs = np.linalg.eigh(b)
    order = np.argsort(vals)[::-1]
    vals, vecs = vals[order], vecs[:, order]
    pos_vals = np.clip(vals, 0, None)
    share = (pos_vals / pos_vals.sum()).round(3).tolist() if pos_vals.sum() > 0 else []
    coords = {nm: [round(float(vecs[i, k] * np.sqrt(pos_vals[k])), 3) for k in range(2)] for i, nm in enumerate(names)}
    out = {"variance_share_by_dimension": share[:4], "coordinates_2d": coords}
    rows = [(abs(pos[a]["state_market"] - pos[b]["state_market"]), abs(pos[a]["orthodoxy"] - pos[b]["orthodoxy"]),
             (pairs.get(f"{a}|{b}") or pairs.get(f"{b}|{a}"))["disagreement"])
            for i, a in enumerate(names) for b in names[i + 1:] if a in pos and b in pos]
    if len(rows) >= 5:
        x = np.array([[1.0, r[0], r[1]] for r in rows])
        y = np.array([r[2] for r in rows])
        beta, *_ = np.linalg.lstsq(x, y, rcond=None)
        pred = x @ beta
        r2 = 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum() if ((y - y.mean()) ** 2).sum() else None
        out["ols_disagreement_on_axes"] = {"intercept": round(float(beta[0]), 3),
                                           "state_market": round(float(beta[1]), 3),
                                           "orthodoxy": round(float(beta[2]), 3),
                                           "r2": round(float(r2), 3) if r2 is not None else None, "pairs": len(rows)}
    return out


def analyze(jobs_dir: Path) -> dict:
    """Read <jobs>/results.jsonl, write matrix.json and matrix.md, return the summary."""
    man = json.loads((jobs_dir / "manifest.json").read_text())
    runs: dict[tuple[str, int], dict] = {}
    failed = 0
    for raw in (jobs_dir / "results.jsonl").read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        line = json.loads(raw)
        name, rep, eid = line["custom_id"].split("|")
        parsed = parse(line.get("content", ""))
        if parsed is None:
            failed += 1
            continue
        runs.setdefault((name, int(rep)), {})[eid] = parsed
    names = [n for n in man["frameworks"] if (n, 0) in runs]
    pairs = {f"{a}|{b}": distance(runs[(a, 0)], runs[(b, 0)]) for a, b in combinations(names, 2)}
    noise = {n: distance(runs[(n, 0)], runs[(n, 1)]) for n in man["repeats"] if (n, 1) in runs}
    nearest = {}
    for n in names:
        others = [(v["signals"], next(x for x in k.split("|") if x != n)) for k, v in pairs.items()
                  if n in k.split("|")]
        nearest[n] = min(others) if others else None
    pos = tomllib.loads(FRAMEWORKS.read_text(encoding="utf-8")).get("positions", {})
    theory, measured = [], []
    for k, v in pairs.items():
        a, b = k.split("|")
        if a in pos and b in pos:
            theory.append(sum(abs(pos[a][d] - pos[b][d]) for d in ("state_market", "orthodoxy")))
            measured.append(v["disagreement"])
    summary = {"parsed": sum(len(v) for v in runs.values()), "failed": failed, "pairs": pairs, "noise": noise,
               "nearest": nearest, "dispersion": dispersion({n: runs[(n, 0)] for n in names}),
               "dispersion_schools_only": dispersion({n: runs[(n, 0)] for n in names
                                                      if n in ("keynesian", "austrian", "monetarist")}),
               "position_vs_disagreement_spearman": spearman(theory, measured), "pairs_with_positions": len(theory),
               "position_test": position_test(pairs, names, pos),
               "per_asset_all": per_asset({n: runs[(n, 0)] for n in names}, names),
               "per_asset_schools_only": per_asset({n: runs[(n, 0)] for n in names},
                                                   [n for n in names if n in ("keynesian", "austrian", "monetarist")]),
               "space": space(pairs, names, pos)}
    (jobs_dir / "matrix.json").write_text(json.dumps(summary, indent=1) + "\n")
    lines = ["# Disagreement matrix", "", f"Parsed {summary['parsed']} analyses, {failed} unparsable.", "",
             "Signal disagreement (0 = same calls, 1 = all opposite), above the diagonal; macro gap (expected growth "
             "plus inflation direction, 0-4), below it.", "",
             "| | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for a in names:
        row = []
        for b in names:
            if a == b:
                row.append("–")
            else:
                d = pairs.get(f"{a}|{b}") or pairs.get(f"{b}|{a}")
                row.append(f"{d['signals']:.2f}" if names.index(b) > names.index(a) else f"{d['macro']:.2f}")
        lines.append(f"| {a} | " + " | ".join(row) + " |")
    lines += ["", "Noise (the same framework run twice):", ""]
    lines += [f"- {n}: signals {d['signals']:.2f}, opposite {d['opposite']:.2f}, macro {d['macro']:.2f} (n={d['n']})"
              for n, d in noise.items()]
    lines += ["", f"Forecast dispersion across all frameworks: {summary['dispersion']}; three schools only: "
              f"{summary['dispersion_schools_only']}.",
              f"Literature distance (state-market + orthodoxy) vs measured disagreement, Spearman over "
              f"{summary['pairs_with_positions']} pairs: {summary['position_vs_disagreement_spearman']}."]
    if summary["position_test"]:
        lines += ["Exact permutation test (frameworks relabelled, one-sided): " + "; ".join(
            f"{k} rho {v['rho']:+.3f}, p {v['p_one_sided']:.3f}" for k, v in summary["position_test"].items())
            + f" ({next(iter(summary['position_test'].values()))['permutations']} permutations)."]
    lines += ["", f"Different calls per asset, mean over pairs: all frameworks {summary['per_asset_all']}; "
              f"three schools {summary['per_asset_schools_only']}."]
    sp = summary["space"]
    if sp:
        lines += ["", f"Multidimensional scaling: variance share by dimension {sp['variance_share_by_dimension']}; "
                  f"2-D coordinates {sp['coordinates_2d']}.",
                  f"OLS of pairwise disagreement on the distance along each axis: {sp.get('ols_disagreement_on_axes')}."]
    lines += ["", "Nearest framework by signal disagreement:", ""]
    lines += [f"- {n}: {v[1]} ({v[0]:.2f})" for n, v in nearest.items() if v]
    (jobs_dir / "matrix.md").write_text("\n".join(lines) + "\n")
    return summary
