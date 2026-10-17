"""Alert logic (DECISIONS 2026-10-17): threshold rule and frozen-score reproduction."""
import numpy as np
import pandas as pd
import pytest

from croptransfer import alert_calibration as ac
from croptransfer.config import load_config, repo_path


def test_threshold_respects_max_fpr():
    neg = np.array([-0.2, -0.1, -0.05, 0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06])
    thr = ac.threshold_for(neg, 0.2)  # at most 2 of 10 negatives may alert
    assert thr == -0.1
    assert (neg <= thr).mean() <= 0.2


def test_threshold_none_allowed_and_nan():
    assert ac.threshold_for(np.array([0.1, 0.2, np.nan]), 0.2) == -np.inf


def test_threshold_ties_never_exceed_budget():
    neg = np.array([-0.1, -0.1, -0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    thr = ac.threshold_for(neg, 0.2)
    assert (neg <= thr).sum() <= 2


@pytest.mark.skipif(not (repo_path("data/interim/obs").exists()), reason="needs local US scene data")
def test_reference_reproduces_frozen_curve():
    cfg = load_config()
    mat = ac.us_dekad_matrix(cfg)
    lab = ac.labels(cfg)
    ref = ac.reference_from(mat, lab.index[lab.RY_descr >= ac.HEALTHY_RY])
    frozen = pd.read_csv(repo_path("reports/freeze_at/stress_reference_hls_ndvi.csv"), index_col=0)["ndvi_median"]
    assert np.nanmax(np.abs(ref.reindex(frozen.index).to_numpy() - frozen.to_numpy())) < 1e-5
