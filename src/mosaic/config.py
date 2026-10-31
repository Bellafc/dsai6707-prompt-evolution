"""TOML config loading. Paths are resolved relative to the repo root."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[2]


def load_toml(path: str | Path) -> dict:
    with open(ROOT / path if not Path(path).is_absolute() else path, "rb") as f:
        return tomllib.load(f)


def paths() -> dict:
    """configs/paths.toml (machine-specific, not versioned) falling back to the example."""
    p = ROOT / "configs/paths.toml"
    cfg = load_toml(p if p.exists() else ROOT / "configs/paths.example.toml")
    return {k: (ROOT / v if isinstance(v, str) and not Path(v).is_absolute() else v) for k, v in cfg.items()}


def stable_hash(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()


def file_sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
