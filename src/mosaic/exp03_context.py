"""exp03 point-in-time contexts (Task 2, step 3): the 35 indicators as published on or before the forecast time.

Source: ALFRED's keyless CSV (pattern of pmpol `realtime.py`): `alfredgraph.csv?id=X,X&vintage_date=d1,d2` returns one
column `X_<yyyymmdd>` per vintage date, i.e. the series as it stood then. At most 12 dates per request. Responses are
cached under data/exp03/alfred/ (not committed); a cached batch is never fetched twice. HTTP errors (including 429)
stop the run: no retries (program.md, rule 10).
"""

from __future__ import annotations

import csv
import io
import time
import tomllib
from datetime import date
from pathlib import Path

from mosaic.config import ROOT

ALFRED = "https://alfred.stlouisfed.org/graph/alfredgraph.csv?id={ids}&vintage_date={dates}"
CACHE = ROOT / "data" / "exp03" / "alfred"
INDICATORS = ROOT / "configs" / "exp03_indicators.toml"
BATCH = 12
USER_AGENT = "pmpol/0.1 (https://github.com/bellafc/polymarket_politics; research, read-only)"


def load_indicators(path: Path = INDICATORS) -> list[dict]:
    with open(path, "rb") as f:
        return tomllib.load(f)["indicator"]


def _get(url: str) -> str:
    import httpx

    r = httpx.get(url, timeout=90, headers={"User-Agent": USER_AGENT}, follow_redirects=True)
    r.raise_for_status()
    return r.text


def parse_vintages(text: str, series: str) -> dict[str, list[tuple[str, float]]]:
    """ALFRED CSV -> {vintage 'YYYY-MM-DD': [(observation date, value), ...] oldest first}. Missing values ('.' or
    empty) are dropped; the first column is the observation date."""
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        return {}
    head, out = rows[0], {}
    for j, name in enumerate(head):
        if j == 0 or not name.startswith(series + "_") or len(name) != len(series) + 9:
            continue
        stamp = name[len(series) + 1:]
        v = f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:]}"
        out[v] = [(r[0], float(r[j])) for r in rows[1:] if len(r) > j and r[j] not in ("", ".")]
    return out


def fetch_asof(series: str, dates: list[str], cache: Path = CACHE, get=None, pause: float = 2.0) -> dict[str, dict]:
    """{requested date: {"vintage": vintage date used, "obs": [(obs date, value)...]}} for one series.

    The vintage used for a requested date is the latest vintage column on or before it. If ALFRED returns no such
    column (series not yet published, discontinued) the date maps to {"vintage": None, "obs": []}."""
    get = get or _get
    cache.mkdir(parents=True, exist_ok=True)
    out, ds = {}, sorted(set(dates))
    for i in range(0, len(ds), BATCH):
        batch = ds[i:i + BATCH]
        path = cache / f"{series}_{batch[0]}_{batch[-1]}_{len(batch)}.csv"
        if path.exists():
            text = path.read_text(encoding="utf-8")
        else:
            text = get(ALFRED.format(ids=",".join([series] * len(batch)), dates=",".join(batch)))
            path.write_text(text, encoding="utf-8")
            time.sleep(pause)
        vint = parse_vintages(text, series)
        for d in batch:
            ok = [v for v in vint if v <= d]
            if not ok:
                out[d] = {"vintage": None, "obs": []}
                continue
            v = max(ok)
            out[d] = {"vintage": v, "obs": [(o, x) for o, x in vint[v] if o <= d]}
    return out


def context_rows(spec: dict, asof: dict, n_last: int = 6) -> dict:
    """The context entry of one indicator at one forecast time: last `n_last` observations plus the number of
    observations available, the vintage date and the freshness of the latest observation (days before t)."""
    obs = asof["obs"][-n_last:]
    return {"id": spec["id"], "name": spec["name"], "group": spec["group"], "vintage": asof["vintage"],
            "last": obs, "n_obs": len(asof["obs"])}


def staleness_days(last_obs_date: str, t: str) -> int:
    return (date.fromisoformat(t) - date.fromisoformat(last_obs_date[:10])).days
