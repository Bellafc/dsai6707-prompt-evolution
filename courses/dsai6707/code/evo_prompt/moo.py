"""Constrained multi-objective machinery for minimisation (Deb et al., 2002).

Items are (objectives, violation) pairs. Dominance follows Deb's rule: a feasible item beats an infeasible one, among
infeasible items the smaller violation wins, and among feasible items ordinary Pareto dominance applies.
Provided: fast non-dominated sort, crowding distance, NSGA-II environmental selection, exact 3-D hypervolume and the
knee point (closest to the ideal point 0,0,0 in normalised space).
"""

from __future__ import annotations

import math


def dominates(a, b) -> bool:
    (oa, va), (ob, vb) = a, b
    if va == 0 and vb > 0:
        return True
    if va > 0 and vb == 0:
        return False
    if va > 0 and vb > 0:
        return va < vb
    return all(x <= y for x, y in zip(oa, ob)) and any(x < y for x, y in zip(oa, ob))


def fronts(items: list) -> list[list[int]]:
    n = len(items)
    dominated_by_p: list[list[int]] = [[] for _ in range(n)]
    count = [0] * n
    first: list[int] = []
    for p in range(n):
        for q in range(n):
            if p == q:
                continue
            if dominates(items[p], items[q]):
                dominated_by_p[p].append(q)
            elif dominates(items[q], items[p]):
                count[p] += 1
        if count[p] == 0:
            first.append(p)
    out = [first]
    while out[-1]:
        nxt = []
        for p in out[-1]:
            for q in dominated_by_p[p]:
                count[q] -= 1
                if count[q] == 0:
                    nxt.append(q)
        out.append(nxt)
    return [f for f in out if f]


def crowding(items: list, idx: list[int]) -> dict[int, float]:
    dist = {i: 0.0 for i in idx}
    if len(idx) <= 2:
        return {i: math.inf for i in idx}
    m = len(items[idx[0]][0])
    for k in range(m):
        order = sorted(idx, key=lambda i: items[i][0][k])
        lo, hi = items[order[0]][0][k], items[order[-1]][0][k]
        dist[order[0]] = dist[order[-1]] = math.inf
        if hi - lo <= 0:
            continue
        for a in range(1, len(order) - 1):
            dist[order[a]] += (items[order[a + 1]][0][k] - items[order[a - 1]][0][k]) / (hi - lo)
    return dist


def rank_and_crowding(items: list) -> tuple[list[int], list[float]]:
    rank = [0] * len(items)
    cd = [0.0] * len(items)
    for r, f in enumerate(fronts(items)):
        d = crowding(items, f)
        for i in f:
            rank[i] = r
            cd[i] = d[i]
    return rank, cd


def select(items: list, k: int) -> list[int]:
    """NSGA-II environmental selection: fill fronts in order, break the last front by crowding distance."""
    chosen: list[int] = []
    for f in fronts(items):
        if len(chosen) + len(f) <= k:
            chosen += f
        else:
            d = crowding(items, f)
            chosen += sorted(f, key=lambda i: -d[i])[: k - len(chosen)]
            break
        if len(chosen) == k:
            break
    return chosen


def nondominated_objectives(points: list[tuple]) -> list[int]:
    return fronts([(p, 0.0) for p in points])[0] if points else []


def hv2d(pts: list[tuple[float, float]], ry: float, rz: float) -> float:
    area = 0.0
    prev = rz
    for y, z in sorted(pts):
        if y < ry and z < prev:
            area += (ry - y) * (prev - z)
            prev = z
    return area


def hv3(points: list[tuple[float, float, float]], ref: tuple[float, float, float] = (1.0, 1.0, 1.0)) -> float:
    """Exact hypervolume of the region dominated by the points and bounded by ref (minimisation, slicing on x)."""
    pts = sorted(p for p in points if all(c < r for c, r in zip(p, ref)))
    total = 0.0
    for i, p in enumerate(pts):
        nx = pts[i + 1][0] if i + 1 < len(pts) else ref[0]
        if nx > p[0]:
            total += (nx - p[0]) * hv2d([(q[1], q[2]) for q in pts[: i + 1]], ref[1], ref[2])
    return total


def knee(points: list[tuple[float, ...]]) -> int:
    """Index of the point closest to the ideal point (all zeros). Fixed before any held-out result is seen."""
    return min(range(len(points)), key=lambda i: sum(c * c for c in points[i]))
