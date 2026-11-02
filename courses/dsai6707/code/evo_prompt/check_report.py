"""Check that the numbers and key statements in report/report.md agree with the files in results/.

Run from courses/dsai6707/code:  python -m evo_prompt.check_report
Each line prints PASS or FAIL with the detail. The script reads files only; it makes no model calls.
"""

from __future__ import annotations

import csv
import json
import re
import statistics
from pathlib import Path

from .config import COURSE_DIR, RESULTS_DIR

REPORT = COURSE_DIR / "report" / "report.md"
BIB = COURSE_DIR / "report" / "references.bib"
CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(ok), detail))


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    rep = REPORT.read_text(encoding="utf-8")
    runs = RESULTS_DIR / "runs"

    # 1. literature: 2024–2026 entries, all cited
    bib = BIB.read_text(encoding="utf-8")
    entries = re.findall(r"@\w+\{([^,]+),(.*?)\n\}", bib, re.S)
    years = {k: int(re.search(r"year\s*=\s*\{?(\d{4})", b).group(1)) for k, b in entries if "year" in b}
    inrange = [k for k, y in years.items() if 2024 <= y <= 2026]
    cited = set()
    for grp in re.findall(r"\[(@[^\]]+)\]", rep):
        cited |= set(re.findall(r"@([A-Za-z0-9_]+)", grp))
    check("literature: 2024–2026 entries = 34", len(inrange) == 34, f"found {len(inrange)}")
    check("literature: every 2024–2026 entry is cited", all(k in cited for k in inrange),
          f"uncited: {sorted(set(inrange) - cited)}")

    # 2. summary table cells appear verbatim in the report (one known exception: B0 word SD)
    summ = (RESULTS_DIR / "summary_table.md").read_text(encoding="utf-8")
    missing = []
    for line in summ.splitlines():
        if line.startswith("|") and not line.startswith(("|---", "| Method", "| Comparison")):
            for cell in [c.strip() for c in line.strip("|").split("|")][1:]:
                if re.search(r"\d", cell) and cell not in rep:
                    missing.append(cell)
    check("tables: summary_table.md numbers appear in report", missing in ([], ["438 ± 0"]),
          f"not verbatim: {missing}")

    # 3. paired tests: report Table 4 equals heldout_tests.csv
    tests = read_csv(RESULTS_DIR / "heldout_tests.csv")
    min_holm = min(float(t["p_holm"]) for t in tests)
    check("held-out: smallest Holm-adjusted p = 0.305 (report)", f"{min_holm:.3f}" == "0.305" and "0.305" in rep,
          f"{min_holm:.4f}")
    for t in tests:
        row = f"{float(t['p_raw']):.4f}"
        if row not in rep:
            check(f"held-out: p_raw {t['comparison']} {t['metric']} in report", False, row)

    # 4. sensitivity (duplicate event removed): the three numbers quoted in §5.2
    sens = {(r["comparison"], r["metric"]): float(r["p_exact"]) for r in read_csv(RESULTS_DIR / "heldout_sensitivity.csv")}
    for key, quoted in [(("ga - b0", "fidelity"), "0.059"), (("random - b0", "fidelity"), "0.051"),
                        (("nsga2_rule - b0", "fidelity"), "0.109"), (("ga_rule - b0", "fidelity"), "0.066"),
                        (("nsga2_llmu - b0", "fidelity"), "0.082")]:
        ok = f"{sens[key]:.3f}" == quoted and quoted in rep
        check(f"sensitivity: {key[0]} {key[1]} p = {quoted}", ok, f"file {sens[key]:.4f}")
    dup = read_csv(RESULTS_DIR / "heldout_sensitivity.csv")[0]["excluded_events"]
    check("sensitivity: duplicated held-out event named in report", dup in rep, dup)

    # 5. budget: calls and spend in the matrix ledger
    ledger = [ln for ln in (RESULTS_DIR / "logs" / "matrix.log").read_text(encoding="utf-8").splitlines()
              if ln.startswith("ledger:")]
    calls = int(re.search(r"calls (\d+)", ledger[-1]).group(1))
    spend = float(re.search(r"spend \$([\d.]+)", ledger[-1]).group(1))
    check("budget: 2,743 calls in report", f"{calls:,}" in rep and calls == 2743, f"log {calls}")
    qrows = [json.loads(x) for x in (RESULTS_DIR / "cache" / "llm_cache.jsonl").read_text(encoding="utf-8").splitlines()
             if x.strip()]
    qusd = sum(2.4 * (r.get("usage") or {}).get("prompt_tokens", 0) + 9.6 * (r.get("usage") or {}).get(
        "completion_tokens", 0) for r in qrows) / 1e6
    check("budget: main matrix USD 20.20 (log); qwen total USD 27.31 quoted", spend == 20.20 and f"{qusd:.2f}" == "27.31"
          and "USD 27.31" in rep, f"log {spend:.2f}, cache {qusd:.2f}")

    # 6. LLM-guided children and rejections (origin suffix L / f)
    for m in ("nsga2", "ga"):
        rows = [json.loads(x) for s in (1, 2, 3)
                for x in (runs / f"{m}_s{s}" / "evaluations.jsonl").read_text(encoding="utf-8").splitlines() if x]
        llm = [r for r in rows if "L" in r["origin"]]
        rej = [r for r in rows if r["origin"].endswith("f")]
        want = {"nsga2": (30, 8), "ga": (34, 10)}[m]
        check(f"LLM children: {m} {want[0]} children, {want[1]} rejected",
              (len(llm), len(rej)) == want, f"found {len(llm)} children, {len(rej)} rejected")

    # 7. hypervolume per generation quoted in §5.1
    gl = {m: [read_csv(runs / f"{m}_s{s}" / "gen_log.csv") for s in (1, 2, 3)]
          for m in ("nsga2", "ga", "random", "nsga2_rule")}
    hv = {m: [statistics.mean(float(rs[g]["hv"]) for rs in gl[m]) for g in range(5)] for m in gl}
    check("hypervolume gen 0 quoted (0.071, 0.073)",
          f"{hv['nsga2'][0]:.3f}" == "0.071" and f"{hv['random'][0]:.3f}" == "0.073", str({m: round(v[0], 4) for m, v in hv.items()}))
    check("hypervolume gen 4 quoted (0.121, 0.122, 0.098, 0.098)",
          [f"{hv[m][4]:.3f}" for m in ("nsga2", "ga", "random", "nsga2_rule")] == ["0.121", "0.122", "0.098", "0.098"],
          str({m: round(v[4], 4) for m, v in hv.items()}))

    # 8. lengths quoted in §5.2 (B0 438; knees 305–350)
    srows = read_csv(RESULTS_DIR / "summary.csv")
    b0_words = {r["heldout_words"] for r in srows if r["method"] == "b0"}
    means = {}
    for m in ("nsga2", "ga", "random", "nsga2_rule", "ga_rule", "nsga2_llmu"):
        means[m] = round(statistics.mean(float(r["heldout_words"]) for r in srows if r["method"] == m))
    check("length: B0 438 words", b0_words == {"438"}, str(b0_words))
    check("length: method means are 305–356 (report: '305 to 356 words')",
          min(means.values()) == 305 and max(means.values()) == 356 and "305 to 356" in rep, str(means))

    # 8b. measured latency quoted in §4.7 (median and call counts from the cache)
    import statistics as _st
    rows_c = [json.loads(x) for x in (RESULTS_DIR / "cache" / "llm_cache.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    lat = [r["seconds"] for r in rows_c if isinstance(r.get("seconds"), (int, float)) and r["seconds"] > 0]
    check("latency: median 14.9 s and 3,709 recorded qwen calls quoted in §4.7",
          f"{_st.median(lat):.1f}" == "14.9" and len(rows_c) == 3709 and "14.9 s" in rep and "3,709" in rep,
          f"median {_st.median(lat):.2f}, calls {len(rows_c)}")

    # 8c. numbers added in the review pass (§4.8, §5.1, §5.2, Figure 2)
    fam = read_csv(RESULTS_DIR / "heldout_tests_protocol.csv")
    minf = min(float(t["p_holm_family"]) for t in fam)
    check("protocol family (qwen): 42 tests, smallest Holm p = 1.0", len(fam) == 42 and minf == 1.0
          and "12 + 30 = 42" in rep, f"n={len(fam)}, min={minf}")
    hv4 = {m: [f"{float(rs[4]['hv']):.3f}" for rs in gl[m]] for m in gl}
    check("per-seed hv quoted (nsga2 vs nsga2_rule, random s2)",
          all(f"{a} against {b}" in rep for a, b in zip(hv4["nsga2"], hv4["nsga2_rule"]))
          and hv4["random"][1] == "0.112" and hv4["nsga2"][1] == "0.108", str(hv4))
    b0d = sorted(f"{float(r['heldout_disagreement']):.3f}" for r in srows if r["method"] == "b0")
    check("B0 held-out disagreement range quoted", f"{b0d[0]} to {b0d[-1]}" in rep, str(b0d))
    fw = {m: [json.loads(x)["words"] for s in (1, 2, 3)
              for x in (runs / f"{m}_s{s}" / "front.jsonl").read_text().splitlines() if x.strip()]
          for m in ("random", "nsga2_rule", "ga_rule", "nsga2", "ga", "nsga2_llmu")}
    rule_lo = min(min(fw[m]) for m in ("random", "nsga2_rule", "ga_rule"))
    llm_lo = sorted(min(fw[m]) for m in ("nsga2", "ga", "nsga2_llmu"))
    check("Figure 2 text: LLM arms 242–256 words, rule arms >= 292", rule_lo == 292 and llm_lo[0] == 242
          and llm_lo[-1] == 256 and "242 to 256 words" in rep and "292 words or more" in rep, f"{rule_lo} {llm_lo}")

    # 8d. addendum questions (qwen Q1-Q3, Haiku Q1-Q5) and the Haiku replication
    norm = rep.replace("−", "-")
    for r in read_csv(RESULTS_DIR / "addendum_a_search.csv"):
        cells = [f"{float(r[f'diff_s{s}']):+.4f}" for s in (1, 2, 3)]
        check(f"qwen {r['question'].split()[0]}: per-seed differences quoted", all(c in norm for c in cells), str(cells))
    H = RESULTS_DIR / "haiku"
    hfin = lambda m, s: json.loads((H / "runs" / f"{m}_s{s}" / "final.json").read_text())["hv_final"]  # noqa: E731
    for r in read_csv(H / "addendum_a_search.csv"):
        a, b = r["comparison"].split(" - ")
        cells = ", ".join(f"{hfin(a, s) - hfin(b, s):+.3f}".replace("-0.000", "+0.000") for s in (1, 2, 3, 4, 5))
        p1 = f"{float(r['p_sign_flip_one_sided']):.3f}"
        check(f"Haiku {r['question'].split()[0]}: five differences (unrounded source) and p quoted",
              cells in norm and p1 in rep, cells)
    hsum = (H / "summary_table.md").read_text(encoding="utf-8")
    hv_cells = [ln.split("|")[2].strip() for ln in hsum.split("## Held-out")[0].splitlines()
                if ln.startswith("| ") and "Method" not in ln]
    check("Haiku: every hypervolume cell of Table 5 quoted", all(c in rep for c in hv_cells), str(hv_cells))
    htests = read_csv(H / "heldout_tests.csv")
    hmin = min(float(t["p_holm"]) for t in htests)
    check("Haiku held-out: 16 tests, smallest Holm p = 0.125 quoted", len(htests) == 16 and f"{hmin:.3f}" == "0.125"
          and "adjusted 0.125 over 16 tests" in rep, f"{len(htests)} {hmin}")
    hfam = read_csv(H / "heldout_tests_protocol.csv")
    check("Haiku protocol family: 72 tests, smallest Holm p = 0.425 quoted",
          len(hfam) == 72 and f"{min(float(t['p_holm_family']) for t in hfam):.3f}" == "0.425" and "0.425" in rep,
          str(len(hfam)))
    import glob as _glob
    hrows = []
    for f in [H / "cache" / "llm_cache.jsonl"] + sorted(Path(x) for x in _glob.glob(str(H / "cache" / "layers" / "*.jsonl"))):
        hrows += [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]
    ti = sum((r.get("usage") or {}).get("prompt_tokens", 0) for r in hrows)
    to = sum((r.get("usage") or {}).get("completion_tokens", 0) for r in hrows)
    usd = (ti * 0.10 + to * 0.50) / 1e6
    check("Haiku totals: 9,412 calls and USD 5.28 quoted", len(hrows) == 9412 and f"{usd:.2f}" == "5.28"
          and "9,412" in rep and "USD 5.28" in rep, f"{len(hrows)} {usd:.2f}")
    ep = {m: [json.loads(x) for s in (1, 2, 3, 4, 5)
              for x in (H / "runs" / f"{m}_s{s}" / "evaluations.jsonl").read_text().splitlines() if x.strip()]
          for m in ("evoprompt_ga", "evoprompt_ga_lc")}
    kid = {m: [r for r in v if r["gen"] > 0] for m, v in ep.items()}
    w = {m: sorted(r["words"] for r in v) for m, v in kid.items()}
    feas = {m: sum(r["feasible"] for r in v) for m, v in kid.items()}
    check("EvoPrompt children: 668–1,132 words, 3 of 120 feasible; bounded 396–608, 60 of 120",
          (w["evoprompt_ga"][0], w["evoprompt_ga"][-1], feas["evoprompt_ga"]) == (668, 1132, 3)
          and (w["evoprompt_ga_lc"][0], w["evoprompt_ga_lc"][-1], feas["evoprompt_ga_lc"]) == (396, 608, 60)
          and "668 to 1,132 words" in rep and "396 to 608 words" in rep and "60 of 120" in rep, f"{w} {feas}")

    # 9. structure and deliverables
    heads = re.findall(r"^#+ (.+)$", rep, re.M)
    for name in ["Abstract", "Introduction", "Related Work", "Method", "Experimental Setup",
                 "Results and Analysis", "Discussion", "Conclusion", "References"]:
        check(f"chapter present: {name}", any(name.lower() in h.lower() for h in heads))
    check("AI-use appendix present", any("AI tools" in h for h in heads))
    for f in ["hv_vs_generation.png", "pareto_fronts.png", "heldout_bars.png"]:
        check(f"figure file exists: {f}", (RESULTS_DIR / "figures" / f).exists())

    width = max(len(n) for n, _, _ in CHECKS)
    for name, ok, detail in CHECKS:
        print(f"{'PASS' if ok else 'FAIL'}  {name:<{width}}  {detail if not ok else ''}")
    failed = [n for n, ok, _ in CHECKS if not ok]
    print(f"\n{len(CHECKS) - len(failed)}/{len(CHECKS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
