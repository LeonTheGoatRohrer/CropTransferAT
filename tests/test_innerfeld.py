"""Offline tests for the common within-field table (synthetic data, no raw files)."""

import numpy as np
import pandas as pd
import pytest

from croptransfer import innerfeld as inf


def test_cell_center_is_on_10m_grid_offset_5():
    c = inf.cell_center(np.array([0.0, 4.9, 10.0, 754285.08, -3.0]))
    assert c.tolist() == [5.0, 5.0, 15.0, 754285.0, -5.0]


def test_aggregate_points_mean_min_points_and_cap():
    pts = pd.DataFrame({"g": "a", "x": [1.0, 2.0, 3.0, 11.0], "y": [1.0, 1.0, 9.0, 1.0],
                        "yield_t_ha": [10.0, 18.0, 14.0, 5.0]})
    out = inf.aggregate_points(pts, ["g"], min_points=2, cap=18.0)
    assert len(out) == 1                                   # the single point in cell (15, 5) is dropped
    r = out.iloc[0]
    assert (r.x, r.y, r.n_points) == (5.0, 5.0, 3)
    assert r.yield_t_ha == pytest.approx(14.0)
    assert r.frac_cap == pytest.approx(1 / 3)


def test_relative_yield_per_field_year_and_cell_count():
    df = pd.DataFrame({"fy_key": ["A", "A", "B", "B", "B"], "yield_t_ha": [8.0, 12.0, 1.0, 2.0, 3.0]})
    out = inf.add_relative_yield(df)
    assert out.rel.tolist() == pytest.approx([0.8, 1.2, 0.5, 1.0, 1.5])
    assert out.n_cells_fy.tolist() == [2, 2, 3, 3, 3]


def test_hull_edge_distance_sign_and_value():
    hx, hy = np.array([0, 100, 100, 0.0]), np.array([0, 0, 100, 100.0])
    d = inf.hull_edge_distance(np.array([50.0, 10.0, 130.0]), np.array([50.0, 50.0, 50.0]), hx, hy)
    assert d.tolist() == pytest.approx([50.0, 10.0, -30.0])


def test_schema_columns_are_unique():
    assert len(inf.SCHEMA) == len(set(inf.SCHEMA))
