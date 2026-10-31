"""Paired statistics over events (every arm answers the same events, so comparisons are paired).

  paired(a, b)  mean difference b - a, 95% bootstrap CI over events, sign-flip permutation p-value, win rate
  holm(ps)      Holm–Bonferroni adjusted p-values
"""

from __future__ import annotations

import numpy as np


def paired(a, b, *, n_boot: int = 2000, n_perm: int = 10000, seed: int = 0) -> dict:
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = ~(np.isnan(a) | np.isnan(b))
    a, b = a[ok], b[ok]
    d = b - a
    n = len(d)
    if n == 0:
        return {"n": 0}
    rng = np.random.default_rng(seed)
    boots = d[rng.integers(0, n, size=(n_boot, n))].mean(axis=1)
    signs = rng.choice([-1.0, 1.0], size=(n_perm, n))
    perm = np.abs((signs * d).mean(axis=1))
    p = (1 + np.sum(perm >= abs(d.mean()) - 1e-12)) / (n_perm + 1)
    return {"n": n, "mean_a": float(a.mean()), "mean_b": float(b.mean()), "diff": float(d.mean()),
            "ci_lo": float(np.percentile(boots, 2.5)), "ci_hi": float(np.percentile(boots, 97.5)),
            "p": float(p), "win_rate": float(np.mean(d > 0)), "tie_rate": float(np.mean(d == 0))}


def holm(ps: list[float]) -> list[float]:
    m = len(ps)
    order = np.argsort(ps)
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * ps[i]))
        adj[i] = running
    return adj.tolist()
