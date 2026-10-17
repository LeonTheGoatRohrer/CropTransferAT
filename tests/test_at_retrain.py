"""Mechanics of the regional re-training (EU rows as stand-in for Austrian rows; no Austrian value is used)."""

import json

import numpy as np
import pytest

from croptransfer import at_retrain
from croptransfer import regional_cybench as rc
from croptransfer.config import load_config, repo_path


def test_fit_linear_recovers_line_and_handles_constant():
    p = np.array([0.8, 0.9, 1.0, 1.1])
    a, b = at_retrain.fit_linear(p, 0.5 + 0.5 * p)
    assert a == pytest.approx(0.5) and b == pytest.approx(0.5)
    assert at_retrain.fit_linear(np.ones(4), np.array([1.0, 2.0, 3.0, 2.0])) == (2.0, 0.0)


def test_retrain_predict_uses_frozen_features_and_weight():
    cfg = load_config()
    if not (repo_path(cfg["cybench"]["raw_dir"]) / "CZ" / "yield_maize_CZ.csv").exists():
        pytest.skip("CY-Bench data not available (data/ is not in the repository)")
    data, _ = rc.load_dataset(cfg)
    c = "09-01"
    meta = json.loads((repo_path(cfg["cybench"]["freeze"]["dir"]) / "lgbm_0901_meta.json").read_text(encoding="utf-8"))
    df = data[c].dropna(subset=["yas"])
    eu = df[df.country == "DE"].head(400)
    stand_in = df[df.country == "HU"].head(25)
    test = df[df.country == "HU"].tail(5)
    p1 = at_retrain.retrain_predict(eu, stand_in, test, meta, cfg, weight=1.0)
    p50 = at_retrain.retrain_predict(eu, stand_in, test, meta, cfg, weight=50.0)
    assert p1.shape == (5,) and np.isfinite(p1).all()
    assert not np.allclose(p1, p50)       # the weight matters
