"""Offline tests for the helper functions of the noise-ceiling analysis (synthetic data)."""

import numpy as np
import pandas as pd
import pytest

from croptransfer import innerfeld_ceiling as ce


def test_spearman_brown_known_values():
    assert ce.spearman_brown(0.5) == pytest.approx(2 / 3)
    assert ce.spearman_brown(1.0) == pytest.approx(1.0)
    assert np.isnan(ce.spearman_brown(np.nan))


def test_pass_ids_split_on_gaps_and_keep_input_order():
    # two passes of 3 points, far apart; rows deliberately shuffled
    df = pd.DataFrame(dict(number=[5, 1, 4, 2, 6, 3], x=[22.0, 0.0, 21.0, 1.0, 23.0, 2.0], y=0.0))
    ids = ce.pass_ids(df)
    assert ids[df.number.to_numpy().argsort()].tolist() == [0, 0, 0, 1, 1, 1]
    assert ids[1] == ids[3] == ids[5] and ids[0] == ids[2] == ids[4] and ids[1] != ids[0]


def test_neighbour_mean_uses_queen_neighbours_and_min_count():
    x = np.array([5.0, 15.0, 25.0, 15.0, 95.0])
    y = np.array([5.0, 5.0, 5.0, 15.0, 95.0])
    v = np.array([1.0, 2.0, 3.0, 4.0, 9.0])
    out = ce.neighbour_mean(x, y, v, min_nb=3)
    assert out[1] == pytest.approx((1 + 3 + 4) / 3)          # the middle cell has three neighbours
    assert np.isnan(out[4]) and np.isnan(out[0])             # isolated cell / only two neighbours


def test_block_means_average_cells_of_a_block():
    b = ce.block_means(np.array([1.0, 9.0, 31.0]), np.array([1.0, 9.0, 1.0]), 20,
                       dict(a=np.array([1.0, 3.0, 10.0])))
    assert sorted(b.a.tolist()) == [2.0, 10.0]
