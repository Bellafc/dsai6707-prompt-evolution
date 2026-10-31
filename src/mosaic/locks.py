"""Freezing an experiment before it may touch the test split.

`mosaic freeze --exp exp01` records the SHA-256 of everything that defines the measurement (prereg, experiment
config, prompts, lexicons, parser, metrics, the test events) in locks/<exp>.json, which is committed. A test run
then refuses to start if any of those files changed, if a prompt still has a placeholder, or if a final run of the
experiment already exists (one shot; `--allow-rerun "<reason>"` overrides and the reason is logged).
Every access to the test split is appended to locks/test_access.log.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from mosaic.config import ROOT, file_sha256, load_toml, paths
from mosaic.prompts import has_placeholder

MEASUREMENT_CODE = ["src/mosaic/metrics.py", "src/mosaic/parse.py", "src/mosaic/prompts.py"]


def git_state() -> dict:
    def run(*a):
        try:
            return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
        except Exception:  # noqa: BLE001
            return ""
    return {"commit": run("rev-parse", "--short", "HEAD") or "unknown", "dirty": bool(run("status", "--porcelain"))}


def tracked_files(exp: str) -> list[Path]:
    cfg = load_toml(ROOT / f"configs/{exp}.toml")
    files = [ROOT / f"configs/{exp}.toml", ROOT / cfg["prereg"], ROOT / "configs/lexicons.toml"]
    files += sorted((ROOT / "configs/prompts").glob("*.txt"))
    files += [ROOT / f for f in MEASUREMENT_CODE]
    files.append(Path(paths()["events_dir"]) / "test.jsonl")
    return files


def _rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def freeze(exp: str) -> dict:
    problems = [f"placeholder left in {_rel(f)}" for f in (ROOT / "configs/prompts").glob("*.txt")
                if has_placeholder(f.read_text(encoding="utf-8"))]
    missing = [_rel(f) for f in tracked_files(exp) if not f.exists()]
    if problems or missing:
        raise SystemExit("cannot freeze:\n  " + "\n  ".join(problems + [f"missing {m}" for m in missing]))
    lock = {"exp": exp, "frozen_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **git_state(),
            "files": {_rel(f): file_sha256(f) for f in tracked_files(exp)}}
    out = ROOT / f"locks/{exp}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(lock, indent=2) + "\n")
    return lock


def verify(exp: str) -> list[str]:
    f = ROOT / f"locks/{exp}.json"
    if not f.exists():
        return [f"no lock: run `mosaic freeze --exp {exp}` first (after dev work is finished)"]
    lock = json.loads(f.read_text())
    problems = []
    for rel, h in lock["files"].items():
        p = ROOT / rel if not Path(rel).is_absolute() else Path(rel)
        if not p.exists():
            problems.append(f"locked file missing: {rel}")
        elif file_sha256(p) != h:
            problems.append(f"locked file changed since freeze: {rel}")
    return problems


def log_test_access(exp: str, run_id: str, note: str) -> None:
    f = ROOT / "locks/test_access.log"
    f.parent.mkdir(exist_ok=True)
    with open(f, "a", encoding="utf-8") as fh:
        fh.write(f"{datetime.now(timezone.utc).isoformat(timespec='seconds')}\t{exp}\t{run_id}\t{note}\n")
