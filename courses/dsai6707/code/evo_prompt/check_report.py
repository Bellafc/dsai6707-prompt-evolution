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
    check("held-out: smallest Holm-adjusted p = 0.203 (report)", f"{min_holm:.3f}" == "0.203", f"{min_holm:.4f}")
    for t in tests:
        row = f"{float(t['p_raw']):.4f}"
        if row not in rep:
            check(f"held-out: p_raw {t['comparison']} {t['metric']} in report", False, row)

    # 4. sensitivity (duplicate event removed): the three numbers quoted in §5.2
    sens = {(r["comparison"], r["metric"]): float(r["p_exact"]) for r in read_csv(RESULTS_DIR / "heldout_sensitivity.csv")}
    for key, quoted in [(("ga - b0", "fidelity"), "0.059"), (("random - b0", "fidelity"), "0.051"),
                        (("nsga2_rule - b0", "fidelity"), "0.109")]:
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
    check("budget: USD 20.20 spend in report", f"{spend:.2f}" in rep and spend == 20.20, f"log {spend:.2f}")

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
    for m in ("nsga2", "ga", "random", "nsga2_rule"):
        means[m] = round(statistics.mean(float(r["heldout_words"]) for r in srows if r["method"] == m))
    check("length: B0 438 words", b0_words == {"438"}, str(b0_words))
    check("length: method means are 305–350 (report: '305 to 350 words')",
          min(means.values()) == 305 and max(means.values()) == 350 and "305 to 350" in rep, str(means))

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
