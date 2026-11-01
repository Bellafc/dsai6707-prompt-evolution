import math

from evo_prompt.moo import crowding, dominates, fronts, hv2d, hv3, knee, nondominated_objectives, select


def test_dominates_pareto_and_feasibility():
    assert dominates(((0, 0, 0), 0.0), ((1, 1, 1), 0.0))
    assert not dominates(((0, 1, 0), 0.0), ((1, 0, 0), 0.0))  # incomparable
    assert dominates(((9, 9, 9), 0.0), ((0, 0, 0), 0.2))  # feasible beats infeasible
    assert dominates(((9, 9, 9), 0.1), ((0, 0, 0), 0.2))  # smaller violation wins among infeasible


def test_fronts_and_selection():
    pts = [((0.0, 1.0, 0.5), 0.0), ((1.0, 0.0, 0.5), 0.0), ((0.5, 0.5, 0.5), 0.0), ((0.9, 0.9, 0.9), 0.0)]
    f = fronts(pts)
    assert sorted(f[0]) == [0, 1, 2]
    assert f[1] == [3]
    assert sorted(select(pts, 3)) == [0, 1, 2]


def test_crowding_boundaries_infinite():
    pts = [((0.0, 1.0), 0.0), ((0.5, 0.5), 0.0), ((1.0, 0.0), 0.0)]
    d = crowding(pts, [0, 1, 2])
    assert math.isinf(d[0]) and math.isinf(d[2]) and math.isfinite(d[1])


def test_hv2d_known_value():
    # (0.2,0.5) and (0.5,0.2) with reference (1,1): 0.4 + 0.15 = 0.55
    assert abs(hv2d([(0.2, 0.5), (0.5, 0.2)], 1, 1) - 0.55) < 1e-12


def test_hv3_single_point_and_dominated_point():
    assert abs(hv3([(0.5, 0.5, 0.5)]) - 0.125) < 1e-12
    assert abs(hv3([(0.5, 0.5, 0.5), (0.7, 0.7, 0.7)]) - 0.125) < 1e-12  # dominated point adds nothing
    assert hv3([(1.0, 0.0, 0.0)]) == 0.0  # outside the reference box


def test_hv3_two_points_inclusion_exclusion():
    a, b = (0.2, 0.5, 0.5), (0.5, 0.2, 0.5)
    # volume of union of two boxes [x,1]x[y,1]x[z,1]: va + vb - overlap
    va, vb = 0.8 * 0.5 * 0.5, 0.5 * 0.8 * 0.5
    overlap = 0.5 * 0.5 * 0.5
    assert abs(hv3([a, b]) - (va + vb - overlap)) < 1e-12


def test_knee_and_nondominated():
    pts = [(0.0, 1.0, 0.0), (0.3, 0.3, 0.3), (1.0, 0.0, 0.0)]
    assert knee(pts) == 1
    assert nondominated_objectives(pts) == [0, 1, 2]
