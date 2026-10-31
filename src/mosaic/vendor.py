"""Extract the team's pmpol archive into vendor/ (read-only reference code for exp03/exp04).

  python -m mosaic vendor

Safe extraction: regular files and directories only, no absolute paths, no `..`, no links.
"""

from __future__ import annotations

import tarfile
from pathlib import Path

from mosaic.config import ROOT

ARCHIVE = ROOT / "pmpol-academic-2026-10-21.tar.gz"
DEST = ROOT / "vendor"


def extract(archive: Path = ARCHIVE, dest: Path = DEST) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as tf:
        members = []
        for m in tf.getmembers():
            p = Path(m.name)
            if p.is_absolute() or ".." in p.parts or not (m.isfile() or m.isdir()):
                raise SystemExit(f"refusing unsafe archive member: {m.name}")
            members.append(m)
        try:
            tf.extractall(dest, members=members, filter="data")  # Python >= 3.12 (and recent 3.10/3.11 patches)
        except TypeError:
            tf.extractall(dest, members=members)
    top = sorted({Path(m.name).parts[0] for m in members})
    print(f"extracted {len(members)} entries to {dest} ({', '.join(top)})")
    return dest
