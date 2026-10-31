"""Environment and data checks. Exit code 0 only if everything needed for the requested arms is present."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess

from mosaic import SCHOOLS
from mosaic.config import ROOT, paths
from mosaic.data import validate
from mosaic.prompts import has_placeholder


def doctor(arms: list[str]) -> int:
    ok = True

    def line(good: bool, msg: str, hard: bool = True):
        nonlocal ok
        print(("  OK   " if good else ("  FAIL " if hard else "  WARN ")) + msg)
        if not good and hard:
            ok = False

    print("environment")
    gpu = shutil.which("nvidia-smi") is not None
    if gpu:
        q = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                           capture_output=True, text=True).stdout.strip()
        line(True, f"GPU: {q}")
    local = any(a in arms for a in "ABC")
    line(gpu or not local, "nvidia-smi found (needed for arms A/B/C)", hard=local)
    if local:
        line(importlib.util.find_spec("vllm") is not None, "vllm importable")
    if "D" in arms:
        cli = shutil.which("claude")
        line(cli is not None, "claude CLI on PATH (arm D: Claude Opus 5.5)")
        if cli:
            st = subprocess.run([cli, "auth", "status"], capture_output=True, text=True)
            method = ""
            try:
                method = json.loads(st.stdout).get("authMethod", "")
            except json.JSONDecodeError:
                pass
            line(st.returncode == 0, f"claude logged in (authMethod: {method or 'unknown'}; "
                 "subscription = claude.ai or oauth_token)")
            line(method in ("claude.ai", "oauth_token"), "arm D will use your subscription, not API billing",
                 hard=False)
    if "T" in arms:
        line(importlib.util.find_spec("openai") is not None, "openai importable (arm T)")
        line(bool(os.environ.get("OPENAI_API_KEY")), "OPENAI_API_KEY set (arm T)")
    line(bool(os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")),
         "HF token set (only needed if the base model download is gated)", hard=False)

    print("data")
    probs = validate(paths())
    needed = [p for p in probs if ("adapter" not in p or "C" in arms) and ("trajector" not in p or "B" in arms)]
    for p in probs:
        if p in needed:
            line(False, p)
        else:
            print(f"  SKIP {p} (not needed for arms {','.join(arms)})")
    if not probs:
        line(True, "events (dev, test), trajectories and adapters present")

    print("prompts")
    for name in ["user_template.txt", *[f"{s}.system.txt" for s in SCHOOLS]]:
        f = ROOT / "configs/prompts" / name
        line(f.exists() and not has_placeholder(f.read_text(encoding="utf-8")),
             f"configs/prompts/{name} is the original Confirmation prompt (no placeholder)", hard=False)
    lex = (ROOT / "configs/lexicons.toml").read_text(encoding="utf-8")
    line("PROVISIONAL" not in lex, "configs/lexicons.toml holds the original keyword lists", hard=False)
    print("\nresult:", "ready" if ok else "not ready (fix FAIL lines)")
    return 0 if ok else 1
