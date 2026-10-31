"""mosaic <command>: doctor | run | report | freeze | verify | status"""

from __future__ import annotations

import argparse
import csv
import sys

from mosaic import locks
from mosaic import run as runmod


def human_gate(exp: str) -> None:
    """Freezing and final test runs are irreversible: they need a person at a terminal (the agent has no tty)."""
    if not sys.stdin.isatty():
        raise SystemExit("this step needs a human at an interactive terminal (program.md, rule 1)")
    if input(f"Type the experiment id ({exp}) to confirm: ").strip() != exp:
        raise SystemExit("not confirmed")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="mosaic")
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("doctor", help="check GPU, packages, data and prompts")
    d.add_argument("--arms", default="A,B,C,D")

    r = sub.add_parser("run", help="run arms on a split and log the result")
    r.add_argument("--exp", required=True)
    r.add_argument("--arms", required=True, help="comma list, e.g. A,B,C")
    r.add_argument("--split", choices=["dev", "test"], required=True)
    r.add_argument("--schools", default=None)
    r.add_argument("--limit", type=int, default=None)
    r.add_argument("--set", action="append", default=[], dest="overrides", help="dotted override, e.g. arms.B.k=5")
    r.add_argument("--backend", choices=["fake"], default=None)
    r.add_argument("--final", action="store_true")
    r.add_argument("--allow-rerun", default=None)
    r.add_argument("--note", default="")

    rp = sub.add_parser("report", help="paired comparison of the latest run of each arm")
    rp.add_argument("--exp", required=True)
    rp.add_argument("--split", choices=["dev", "test"], required=True)

    f = sub.add_parser("freeze", help="lock prompts, metrics, config and test data before the final run")
    f.add_argument("--exp", required=True)
    v = sub.add_parser("verify", help="check the lock")
    v.add_argument("--exp", required=True)

    rs = sub.add_parser("rescore", help="score saved outputs (e.g. the Confirmation generations) with this harness")
    rs.add_argument("--file", required=True, help="jsonl with a 'text' or 'response' field per line")
    rs.add_argument("--school", required=True)

    st = sub.add_parser("status", help="last rows of experiments/results.tsv")
    st.add_argument("-n", type=int, default=15)

    a = ap.parse_args(argv)
    if a.cmd == "freeze" or (a.cmd == "run" and (a.final or a.allow_rerun)):
        human_gate(a.exp)
    if a.cmd == "doctor":
        from mosaic.doctor import doctor
        return doctor(a.arms.split(","))
    if a.cmd == "run":
        from mosaic.run import run
        run(a.exp, a.arms.split(","), a.split, schools=a.schools.split(",") if a.schools else None, limit=a.limit,
            overrides=a.overrides, backend=a.backend, final=a.final, allow_rerun=a.allow_rerun, note=a.note)
        return 0
    if a.cmd == "report":
        from mosaic.report import report
        report(a.exp, a.split)
        return 0
    if a.cmd == "freeze":
        lock = locks.freeze(a.exp)
        print(f"frozen {len(lock['files'])} files at {lock['frozen_at']} (commit {lock['commit']}); "
              "commit locks/ now")
        return 0
    if a.cmd == "verify":
        probs = locks.verify(a.exp)
        print("\n".join(probs) or "lock OK")
        return 1 if probs else 0
    if a.cmd == "rescore":
        from mosaic.rescore import rescore
        rescore(a.file, a.school)
        return 0
    if a.cmd == "status":
        if not runmod.RESULTS.exists():
            print("no runs yet")
            return 0
        with open(runmod.RESULTS, encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh, delimiter="\t"))
        cols = ["run_id", "status", "consistency_mean", "contamination_mean", "output_rate", "diversity", "note"]
        print("\t".join(cols))
        for row in rows[-a.n:]:
            print("\t".join(str(row.get(c, "")) for c in cols))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
