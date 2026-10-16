"""Tests for groundtruth_multi: targets on hand examples, cell ids, Austria guard, counting."""

import numpy as np
import pandas as pd
import pytest

from croptransfer import groundtruth_multi as gm


def _frame(ys, years=None, site="A", crop="winter_wheat"):
    years = years or list(range(2014, 2014 + len(ys)))
    return pd.DataFrame({"dataset": "d", "crop": crop, "crop_variant": "w", "site": site, "country": "X",
                         "year": years, "Y_t_ha": ys})


def test_ry_uses_only_other_years_and_needs_two():
    d = gm.add_targets(_frame([6.0, 8.0, 10.0]))
    # other years of 2014 = (8+10)/2 = 9
    assert d.loc[0, "RY"] == pytest.approx(6.0 / 9.0)
    assert d.loc[2, "RY"] == pytest.approx(10.0 / 7.0)
    two = gm.add_targets(_frame([6.0, 8.0]))
    assert two["RY"].isna().all()


def test_ry_nb_needs_ten_other_sites_and_excludes_self():
    sites = [_frame([5.0 + i * 0.1], years=[2015], site=f"s{i}") for i in range(12)]
    d = gm.add_targets(pd.concat(sites, ignore_index=True))
    others = d["Y_t_ha"].sum() - d.loc[0, "Y_t_ha"]
    assert d.loc[0, "RY_nb"] == pytest.approx(d.loc[0, "Y_t_ha"] / (others / 11))
    few = gm.add_targets(pd.concat(sites[:5], ignore_index=True))
    assert few["RY_nb"].isna().all()


def test_cell_id_and_coord_digits():
    lat, lon = pd.Series([47.236, 49.2]), pd.Series([5.103, 4.2])
    assert gm.cell_id(lat, lon).tolist() == ["472_51", "492_42"]
    assert gm.coord_digits(lat).tolist() == [3, 1]


def test_count_cells_counts_cell_years_once():
    d = pd.DataFrame({"crop": "winter_wheat", "tier": "S2", "cell_id": ["1_1", "1_1", "1_2"],
                      "year": [2015, 2015, 2015]})
    assert gm.count_cells(d)["cell_years"].tolist() == [2]


def test_austria_guard():
    d = pd.DataFrame({"country": ["Austria"], "lat": [48.0], "lon": [16.0]})
    with pytest.raises(AssertionError):
        gm.assert_no_austria(d)
    gm.assert_no_austria(pd.DataFrame({"country": ["Hungary"], "lat": [47.0], "lon": [19.0]}))
