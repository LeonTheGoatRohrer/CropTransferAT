"""AT feasibility test (separate from the proof): leave-one-year-out never trains on the test year."""
import numpy as np
import pandas as pd

from croptransfer import at_feasibility as af


def test_loyo_excludes_test_year():
    rng = np.random.default_rng(0)
    d = pd.DataFrame({"site": ["a", "b"] * 6, "year": np.repeat([2018, 2019, 2020, 2021, 2022, 2023], 2),
                      af.SCORE: rng.normal(-0.03, 0.02, 12), "yas_site": rng.normal(1, 0.1, 12)})
    p = af.loyo(d)
    assert len(p) == 12
    for y, g in p.groupby("year"):
        train_mean = d[d.year != y].yas_site.mean()
        assert np.allclose(g.train_mean, train_mean)


def test_metrics_shapes():
    p = pd.DataFrame({"year": np.repeat([1, 2, 3, 4, 5], 2), "yas": np.linspace(0.8, 1.2, 10), "pred": np.linspace(0.9, 1.1, 10),
                      "train_mean": 1.0, "site": "a", "score": 0.0})
    m = af.metrics(p)
    assert m["rho"] > 0.99 and m["n"] == 10 and len(m["rho_ci"]) == 2
