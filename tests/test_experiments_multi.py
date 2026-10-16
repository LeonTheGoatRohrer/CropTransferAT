"""experiments_multi on synthetic data: signal is recovered, no train/test overlap, D8 uses training rows only."""

import numpy as np
import pandas as pd

from croptransfer import experiments_multi as em
from croptransfer.splits import lofyo


def _synth(n_per=60, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for crop in ("maize", "winter_wheat"):
        for i in range(n_per):
            x = rng.normal(size=len(em.WEATHER))
            row = dict(zip(em.WEATHER, x))
            row.update({s: rng.normal() for s in em.SAT})
            row.update(crop=crop, year=2014 + i % 6, lat=45 + (i % 10) * 0.7, lon=10 + (i % 7) * 0.9,
                       cell_id=f"{i % 10}_{i % 7}", RY=1 + 0.1 * row["cwb_30d"] + rng.normal(0, 0.03))
            rows.append(row)
    d = pd.DataFrame(rows)
    d["cluster"] = d.cell_id + "_" + d.year.astype(str)
    d["field_group"] = em.add_group(d)
    return d


def test_lofyo_no_overlap_in_year_or_group():
    d = _synth()
    for _, tr, te in lofyo(d):
        assert set(d.loc[tr, "year"]).isdisjoint(d.loc[te, "year"])
        assert set(d.loc[tr, "field_group"]).isdisjoint(d.loc[te, "field_group"])


def test_models_recover_signal_and_beat_b0():
    d = _synth()
    oof = em.run_cv(d, ["B0", "B1", "M-Kultur", "M-Pool"], sat=False)
    for m in ("B1", "M-Kultur", "M-Pool"):
        assert np.sqrt(np.mean((oof.RY - oof[f"pred_{m}"]) ** 2)) < np.sqrt(np.mean((oof.RY - oof.pred_B0) ** 2))


def test_crop_transfer_runs_with_unsupervised_scaling():
    d = _synth()
    te = em.run_transfer(d, "maize", sat=False)
    assert len(te) == (d.crop == "maize").sum() and te["pred_M-Pool-ohne-Mais"].notna().all()
    assert np.corrcoef(te["pred_M-Pool-ohne-Mais"], te.RY)[0, 1] > 0.5     # shared signal transfers


def test_relative_sat_uses_training_reference_only():
    d = _synth()
    tr, te = d.iloc[:60].copy(), d.iloc[60:].copy()
    te2 = te.copy()
    te2[em.SAT] = 99.0                                     # test features must not change the reference
    a, _ = em.relative_sat(tr, te)
    b, _ = em.relative_sat(tr, te2)
    pd.testing.assert_frame_equal(a, b)
