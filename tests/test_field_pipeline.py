"""On-demand field pipeline (DECISIONS 2026-10-17): same features as in training, frozen score, alert rules."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from croptransfer import field_pipeline as fp
from croptransfer import stress
from croptransfer.config import load_config

FIX = Path(__file__).parent / "fixtures"
CFG = load_config()


def test_dekads_from_scenes_match_training():
    """Scene table of a US training field -> exactly the stored training dekads (gt_dekads, HLS, NDVI)."""
    obs = pd.read_csv(FIX / "field_pipeline_barc_2018_hls.csv", parse_dates=["date"])
    exp = json.loads((FIX / "field_pipeline_barc_2018_expected.json").read_text())
    got = fp.dekad_rows(obs, CFG)["ndvi"]
    assert [g is None for g in got] == [e is None for e in exp["ndvi_dekads"]]
    for g, e in zip(got, exp["ndvi_dekads"]):
        if e is not None:
            assert abs(g - e) < 1e-4


def test_frozen_score_equals_training_formula():
    """Score of the pipeline == croptransfer.stress.stress_score (training definition) with the frozen reference."""
    exp = json.loads((FIX / "field_pipeline_barc_2018_expected.json").read_text())
    nd = exp["ndvi_dekads"]
    dek = pd.DataFrame({"fy_key": "f", "index": "ndvi", "basis": "HLS", "dekad": range(21),
                        "value": [np.nan if v is None else v for v in nd], "is_observed": [v is not None for v in nd]})
    got = fp.frozen_scores(nd, CFG)
    for c in ("08-01", "08-15", "09-01"):
        ref_score = stress.stress_score(dek, "f", fp.frozen_reference(), c, basis="HLS", first_dekad=6)
        assert got[c]["score"] == pytest.approx(ref_score, abs=1e-5)
    # fewer than 4 observed dekads from June -> no score
    assert got["07-15"]["score"] is None


def test_alert_no_statement_before_mid_august():
    a = fp.evaluate_alert(-0.5, "08-01", 20, 30)
    assert a["state"] == "no_statement"
    assert all(not lv["triggered"] for lv in a["levels"])


def test_alert_levels_use_frozen_thresholds():
    thr = fp.calibration()["frozen_thresholds"]
    s_warn = thr["09-01|30"]
    low = fp.evaluate_alert(s_warn - 0.01, "09-01", 20, 30)
    assert low["state"] == "warning"
    high = fp.evaluate_alert(0.0, "09-01", 20, 30)
    assert high["state"] == "none"
    w = next(lv for lv in low["levels"] if lv["level"] == "warning")
    assert w["k_hit"] is not None and w["n_alert"] >= 10


def test_alert_without_score():
    assert fp.evaluate_alert(None, "09-01", 20, 30)["state"] == "no_statement"


def test_weather_hints_rules():
    h = fp.weather_hints({"cwb_30d": -80.0, "rzwsi_flower": 0.1, "heat32_flower": 6, "prec_spring": 100})
    keys = {x["key"] for x in h}
    assert keys == {"drought", "heat_flowering"}
    assert fp.weather_hints({"cwb_30d": 10.0, "rzwsi_flower": 0.0, "heat32_flower": 0, "prec_spring": 0}) == []


def test_prepare_polygon_buffers_and_validates():
    sq = {"type": "Polygon", "coordinates": [[[15.0, 47.0], [15.002, 47.0], [15.002, 47.002], [15.0, 47.002], [15.0, 47.0]]]}
    g = fp.prepare_polygon(sq, "t", CFG)
    assert g.area_buffered_m2.iloc[0] < g.area_m2.iloc[0]
    bow = {"type": "Polygon", "coordinates": [[[15.0, 47.0], [15.002, 47.002], [15.002, 47.0], [15.0, 47.002], [15.0, 47.0]]]}
    with pytest.raises(ValueError):
        fp.prepare_polygon(bow, "t", CFG)
