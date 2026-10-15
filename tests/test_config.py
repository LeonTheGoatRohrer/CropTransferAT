"""Config sanity checks: values must match the binding definitions in PLAN.md."""

from datetime import date

import pytest

from croptransfer.config import REPO_ROOT, cutoff_dates, load_config, repo_path


@pytest.fixture(scope="module")
def cfg():
    return load_config()


def test_config_loads_and_has_seed(cfg):
    assert isinstance(cfg["seed"], int)


def test_year_ranges(cfg):
    assert cfg["years"]["groundtruth"] == [2013, 2025]
    assert cfg["years"]["austria"] == [2018, 2025]
    for lo, hi in cfg["years"].values():
        assert lo <= hi


def test_cutoffs_sorted_and_inside_season(cfg):
    season_start = date.fromisoformat(f"2022-{cfg['season']['start_mmdd']}")
    season_end = date.fromisoformat(f"2022-{cfg['season']['end_mmdd']}")
    for mmdd_list in cfg["cutoffs"].values():
        dates = cutoff_dates(2022, mmdd_list)
        assert dates == sorted(dates)
        assert all(season_start <= d <= season_end for d in dates)


def test_self_supervised_cutoffs_before_august_target(cfg):
    # The self-supervised target window starts 1 August -> all cutoffs must be earlier.
    assert all(d < date(2022, 8, 1) for d in cutoff_dates(2022, cfg["cutoffs"]["self_supervised"]))


def test_thresholds(cfg):
    assert cfg["targets"]["at_risk_threshold"] == 0.85
    assert cfg["groundtruth"]["moisture_standard"] == 0.155
    assert 0 < cfg["gee"]["s2_cloudscore_min"] < 1
    assert cfg["field"]["inner_buffer_m"] < 0


def test_paths_are_relative(cfg):
    for rel in cfg["paths"].values():
        assert not rel.startswith(("/", "\\")) and ":" not in rel
        assert repo_path(rel).is_relative_to(REPO_ROOT)
