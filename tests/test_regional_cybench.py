"""Offline tests for the CY-Bench EU regional model (synthetic fixtures only; no Austrian data)."""

import copy
import json

import numpy as np
import pandas as pd
import pytest

from croptransfer import regional_cybench as rc
from croptransfer.config import load_config


@pytest.fixture(scope="module")
def cfg():
    return load_config()


@pytest.fixture()
def small_cfg(cfg):
    """Config with a tiny LightGBM grid so that tuning is fast in tests."""
    c = copy.deepcopy(cfg)
    c["cybench"]["lightgbm"]["grid"] = {"max_depth": [2, 3], "min_child_samples": [5], "n_estimators": [10, 30]}
    c["cybench"]["n_jobs"] = 1
    return c


def synthetic_panel(n_per_country=80, countries=("A", "B", "C", "D"), seed=0):
    """YAS depends on f1 (signal) and not on f2 (noise)."""
    rng = np.random.default_rng(seed)
    rows = []
    for c in countries:
        f1, f2 = rng.normal(size=n_per_country), rng.normal(size=n_per_country)
        yas = 1 + 0.25 * f1 + 0.05 * rng.normal(size=n_per_country)
        rows.append(pd.DataFrame({"country": c, "adm_id": [f"{c}{i % 8}" for i in range(n_per_country)],
                                  "year": 2003 + np.arange(n_per_country) // 8, "f1": f1, "f2": f2,
                                  "yas": yas, "yas_trend": 1.0}))
    return pd.concat(rows, ignore_index=True)


# ---------------------------------------------------------------- YAS (hand example)
def test_olympic_mean_drops_max_and_min():
    assert rc.olympic_mean([5, 6, 7, 8, 20]) == pytest.approx(7.0)
    assert rc.olympic_mean([20, 5, 8, 7, 6]) == pytest.approx(7.0)  # order irrelevant


def test_yas_hand_example_uses_only_previous_years():
    years = list(range(2000, 2007))
    y = pd.DataFrame({"country": "XX", "adm_id": "R1", "year": years, "yield": [5, 6, 7, 8, 20, 10, 12.0]})
    out = rc.add_yas(y, n_prior=5).set_index("year")
    # 2005: previous years 2000-2004 = 5,6,7,8,20 -> olympic mean (6+7+8)/3 = 7
    assert out.loc[2005, "expectation"] == pytest.approx(7.0)
    assert out.loc[2005, "yas"] == pytest.approx(10 / 7)
    # 2006: previous years 2001-2005 = 6,7,8,20,10 -> sorted 6,7,8,10,20 -> (7+8+10)/3
    assert out.loc[2006, "yas"] == pytest.approx(12 / (25 / 3))
    assert out.loc[2000:2004, "yas"].isna().all()  # fewer than 5 previous years -> dropped
    # trend baseline of 2005 = OLS line through 2000-2004, expressed as YAS
    slope, icpt = np.polyfit([2000, 2001, 2002, 2003, 2004], [5, 6, 7, 8, 20], 1)
    assert out.loc[2005, "yas_trend"] == pytest.approx((icpt + slope * 2005) / 7.0)


def test_yas_and_trend_ignore_the_year_itself_and_the_future():
    years = list(range(2000, 2008))
    base = pd.DataFrame({"country": "XX", "adm_id": "R1", "year": years, "yield": np.arange(8, dtype=float) + 5})
    changed = base.copy()
    changed.loc[changed["year"] >= 2006, "yield"] = 99.0  # own year and future of 2006 changed
    a = rc.add_yas(base).set_index("year")
    b = rc.add_yas(changed).set_index("year")
    for col in ("expectation", "yas_trend"):
        assert a.loc[2006, col] == pytest.approx(b.loc[2006, col])
    assert a.loc[2006, "yas"] != pytest.approx(b.loc[2006, "yas"])  # only the numerator changes


def test_yas_requires_five_consecutive_valid_previous_years():
    years = [2000, 2001, 2002, 2004, 2005, 2006]  # 2003 missing (e.g. zero yield removed)
    y = pd.DataFrame({"country": "XX", "adm_id": "R1", "year": years, "yield": [5, 6, 7, 8, 9, 10.0]})
    out = rc.add_yas(y).set_index("year")
    assert out["yas"].isna().all()


# ---------------------------------------------------------------- as-of rule
def _daily(var="tmax", year=2005, start="2005-03-20", end="2005-09-30", lag=0):
    dates = pd.date_range(start, end)
    df = pd.DataFrame({"adm_id": "R1", "date": dates, var: np.arange(len(dates), dtype=float)})
    df["avail"] = df["date"] + pd.Timedelta(days=lag)
    return df


def test_aggregate_asof_hand_values_and_month_columns():
    daily = pd.DataFrame({"adm_id": "R1", "date": pd.to_datetime(["2005-04-01", "2005-04-02", "2005-04-03", "2005-05-01"]),
                          "prec": [1.0, 2.0, 3.0, 10.0]})
    daily["avail"] = daily["date"]
    out = rc.aggregate_asof(daily, ["prec"], ["prec"], "05-01", "04-01").iloc[0]
    assert out["prec_mean_m04"] == pytest.approx(2.0)
    assert out["prec_min_m04"] == 1.0 and out["prec_max_m04"] == 3.0 and out["prec_sum_m04"] == 6.0
    assert out["prec_sum_m05"] == 10.0  # cutoff day itself is included (<= cutoff)


def test_aggregate_asof_ignores_everything_after_the_cutoff():
    a = _daily()
    b = a.copy()
    b.loc[b["date"] > "2005-07-01", "tmax"] = -999.0  # future garbage must not matter
    fa = rc.aggregate_asof(a, ["tmax"], [], "07-01", "04-01")
    fb = rc.aggregate_asof(b, ["tmax"], [], "07-01", "04-01")
    pd.testing.assert_frame_equal(fa, fb)
    assert not any(c.endswith("m08") or c.endswith("m09") for c in fa.columns)
    mask = rc.asof_mask(a["date"], a["avail"], "07-01", "04-01")
    assert a.loc[mask, "avail"].max() <= pd.Timestamp("2005-07-01")
    assert a.loc[mask, "date"].min() >= pd.Timestamp("2005-04-01")


def test_composite_with_start_label_is_usable_only_after_its_window_ends():
    comp = _daily(var="fpar", lag=9)
    mask = rc.asof_mask(comp["date"], comp["avail"], "06-01", "04-01")
    assert comp.loc[mask, "date"].max() == pd.Timestamp("2005-05-23")  # label 05-23 + 9 d = 06-01
    assert (comp.loc[mask, "avail"] <= pd.Timestamp("2005-06-01")).all()


def test_asof_assertion_fires_on_violation():
    avail = pd.Series(pd.to_datetime(["2005-05-30", "2005-06-02"]))
    cutoff = pd.Series(pd.to_datetime(["2005-06-01", "2005-06-01"]))
    with pytest.raises(AssertionError):
        rc.check_asof(avail, cutoff)
    rc.check_asof(avail.iloc[:1], cutoff.iloc[:1])  # a valid selection passes


def _write_fake_country(root, cc="XX", scale_after=None):
    """Tiny CY-Bench-like folder: 2 regions, yields 2000-2008, daily data Mar-Oct 2003-2008."""
    d = root / cc
    d.mkdir(parents=True)
    years = range(2000, 2009)
    pd.DataFrame([{"crop_name": "maize", "country_code": cc, "adm_id": r, "harvest_year": y, "yield": 6 + 0.1 * y % 3 + i}
                  for i, r in enumerate(["XX1", "XX2"]) for y in years]).to_csv(d / f"yield_maize_{cc}.csv", index=False)
    pd.DataFrame({"adm_id": ["XX1", "XX2"], "awc": [14.0, 15.0], "bulk_density": [1.4, 1.5],
                  "drainage_class": [3, 4]}).to_csv(d / f"soil_maize_{cc}.csv", index=False)
    pd.DataFrame({"adm_id": ["XX1", "XX2"], "latitude": [48.0, 47.0], "longitude": [10.0, 11.0],
                  "region_area": [100, 200]}).to_csv(d / f"location_maize_{cc}.csv", index=False)

    def table(variables, step):
        rows = []
        for r in ["XX1", "XX2"]:
            for y in range(2003, 2009):
                for k, day in enumerate(pd.date_range(f"{y}-03-01", f"{y}-10-31", freq=f"{step}D")):
                    base = 10 + (k % 7) + (0 if r == "XX1" else 1)
                    vals = {v: base * (0.5 if scale_after is not None and day > pd.Timestamp(f"{y}-{scale_after}") else 1.0)
                            for v in variables}
                    rows.append({"adm_id": r, "date": int(day.strftime("%Y%m%d")), **vals})
        return pd.DataFrame(rows)

    table(["tmin", "tmax", "prec", "cwb"], 1).to_csv(d / f"meteo_maize_{cc}.csv", index=False)
    table(["ssm", "rsm"], 1).assign(rsm=lambda t: t["rsm"] * 10).to_csv(d / f"soil_moisture_maize_{cc}.csv", index=False)
    table(["fpar"], 10).to_csv(d / f"fpar_maize_{cc}.csv", index=False)
    table(["ndvi"], 8).assign(ndvi=lambda t: t["ndvi"] / 100).to_csv(d / f"ndvi_maize_{cc}.csv", index=False)


def test_build_country_features_do_not_depend_on_data_after_the_cutoff(tmp_path, cfg):
    _write_fake_country(tmp_path / "a")
    _write_fake_country(tmp_path / "b", scale_after="07-01")  # everything after 07-01 is different
    ta = rc.build_country("XX", cfg, tmp_path / "a")["tables"]
    tb = rc.build_country("XX", cfg, tmp_path / "b")["tables"]
    feats = [c for c in rc.feature_columns("07-01", cfg, cfg["season"]["start_mmdd"]) if c in ta["07-01"].columns]
    assert feats
    # at 07-01 everything labelled up to 07-01 is identical, except composites whose window ends later
    unaffected = [c for c in feats if not c.startswith(("fpar_", "ndvi_")) or c.endswith(("m04", "m05"))]
    pd.testing.assert_frame_equal(ta["07-01"][unaffected], tb["07-01"][unaffected])
    # a later cutoff does see the change
    assert not ta["09-01"]["tmax_mean_m08"].equals(tb["09-01"]["tmax_mean_m08"])


def test_composites_not_yet_complete_at_the_cutoff_are_excluded(tmp_path, cfg):
    _write_fake_country(tmp_path / "a")
    _write_fake_country(tmp_path / "b", scale_after="06-25")  # changes labels 06-29 (fPAR dekad, NDVI 8-day)
    ta = rc.build_country("XX", cfg, tmp_path / "a")["tables"]["07-01"]
    tb = rc.build_country("XX", cfg, tmp_path / "b")["tables"]["07-01"]
    comp = [c for c in ta.columns if c.startswith(("fpar_", "ndvi_"))]
    assert comp
    pd.testing.assert_frame_equal(ta[comp], tb[comp])  # composites labelled 06-29 end after 07-01 -> unused
    assert not ta["tmax_mean_m06"].equals(tb["tmax_mean_m06"])  # daily meteo of 06-26..06-30 is used


def test_feature_columns_follow_cutoff_month(cfg):
    jun = rc.feature_columns("06-01", cfg, "04-01")
    sep = rc.feature_columns("09-01", cfg, "04-01")
    assert set(jun) < set(sep)
    assert "tmax_mean_m06" in jun and "tmax_mean_m07" not in jun
    assert "prec_sum_m05" in jun and "tmax_sum_m05" not in jun  # sums only for prec/cwb
    assert {"awc", "bulk_density"} <= set(jun)


# ---------------------------------------------------------------- Austria exclusion
def test_austria_is_excluded(cfg, tmp_path):
    countries = cfg["cybench"]["countries"]
    assert "AT" not in countries
    assert not set(countries) & set(cfg["cybench"]["zero_only_countries"])
    with pytest.raises(AssertionError):
        rc.assert_no_austria(["DE", "AT"])
    with pytest.raises(AssertionError):
        rc.load_yields("AT", tmp_path)  # refuses before opening any file
    with pytest.raises(AssertionError):
        rc.build_country("AT", cfg, tmp_path)
    with pytest.raises(AssertionError):
        rc.build_eu_dataset(cfg, tmp_path, ["DE", "AT"])


def test_training_entry_points_reject_austrian_rows(small_cfg, tmp_path):
    df = synthetic_panel()
    df.loc[df["country"] == "D", "country"] = "AT"
    with pytest.raises(AssertionError):
        rc.run_loco(df, ["f1", "f2"], small_cfg, seed=1)
    with pytest.raises(AssertionError):
        rc.freeze_models({"09-01": df}, small_cfg, tmp_path, 1, {"09-01": ["f1", "f2"]})


# ---------------------------------------------------------------- splits
def test_loco_splits_never_share_a_country():
    countries = np.array(list("AABBBCCCCD"))
    seen = []
    for c, tr, te in rc.loco_splits(countries):
        assert set(countries[tr]).isdisjoint(set(countries[te]))
        assert set(countries[te]) == {c}
        assert len(np.intersect1d(tr, te)) == 0 and len(tr) + len(te) == len(countries)
        seen.append(c)
    assert seen == ["A", "B", "C", "D"]


def test_tuning_only_sees_the_rows_it_is_given(small_cfg):
    df = synthetic_panel()
    feats = ["f1", "f2"]
    tr = df[df["country"] != "D"]
    best = rc.tune_hyperparameters(tr[feats].to_numpy(np.float32), tr["yas"].to_numpy(), tr["country"].to_numpy(),
                                   feats, small_cfg, seed=1)
    assert best["max_depth"] <= 3 and best["n_estimators"] in (10, 30)
    with pytest.raises(AssertionError):
        rc.lgb_params(small_cfg, 4, 5, 1)  # depth cap


def test_run_loco_predicts_every_row_once_and_beats_baseline(small_cfg):
    df = synthetic_panel()
    pred, params = rc.run_loco(df, ["f1", "f2"], small_cfg, seed=1)
    assert len(pred) == len(df) and len(params) == 4
    assert sorted(pred["country"].unique()) == ["A", "B", "C", "D"]
    m = rc.metrics_joint(pred["yas"].to_numpy(), pred["pred"].to_numpy(), pred["yas_trend"].to_numpy())
    assert m["model_spearman"] > 0.8 and m["skill_vs_yas1"] > 0.5


def test_label_shuffle_drops_to_baseline(small_cfg):
    df = synthetic_panel()
    fixed = {"max_depth": 2, "min_child_samples": 5, "n_estimators": 30}
    pred, _ = rc.run_loco(df, ["f1", "f2"], small_cfg, seed=1, fixed=fixed, shuffle_seed=123)
    m = rc.metrics_joint(pred["yas"].to_numpy(), pred["pred"].to_numpy())
    assert abs(m["model_spearman"]) < 0.3
    assert m["skill_vs_yas1"] < 0.2


# ---------------------------------------------------------------- metrics
def test_metrics_hand_example_and_bootstrap_ci():
    y = np.array([1.0, 2.0, 3.0, 4.0])
    m = rc.metrics_joint(y, y.copy(), trend=np.full(4, 2.5))
    assert m["model_r2"] == pytest.approx(1.0) and m["model_rmse"] == pytest.approx(0.0)
    assert m["model_spearman"] == pytest.approx(1.0)
    assert m["yas1_rmse"] == pytest.approx(np.sqrt(((y - 1) ** 2).mean()))
    assert m["skill_vs_yas1"] == pytest.approx(1.0)
    df = synthetic_panel().assign(pred=lambda d: d["yas"] + 0.02, yas1=1.0)
    bm = rc.bootstrap_metrics(df, n_boot=50, level=0.95, seed=1)
    for k in ("model_r2", "model_spearman", "skill_vs_yas1"):
        assert bm[k]["lo"] <= bm[k]["value"] + 1e-9 <= bm[k]["hi"] + 2e-9


def test_bootstrap_variants_run_and_are_reproducible():
    df = synthetic_panel().assign(pred=lambda d: d["yas"] * 0.8 + 0.2)
    a = rc.bootstrap_metrics(df, 30, 0.95, seed=5, balanced=True)
    b = rc.bootstrap_metrics(df, 30, 0.95, seed=5, balanced=True)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    c = rc.bootstrap_metrics(df, 30, 0.95, seed=5, cluster_by="country_year")
    assert c["model_spearman"]["value"] == pytest.approx(1.0)
    w = rc.group_spearman(df, ["year"], 5, 30, 0.95, seed=1)
    assert w["n_groups"] > 0 and w["mean_rho"] == pytest.approx(1.0)


# ---------------------------------------------------------------- freeze
def _freeze_fixture(small_cfg, tmp_path):
    df = synthetic_panel()
    feats = ["f1", "f2"]
    files = rc.freeze_models({"09-01": df}, small_cfg, tmp_path / "freeze", 1, {"09-01": feats})
    protocol = tmp_path / "protocol.md"
    rows = "\n".join(f"| `{n}` | `{f['sha256']}` |" for n, f in files.items())
    protocol.write_text("| Datei | SHA-256 |\n|---|---|\n" + rows + "\n", encoding="utf-8")
    return df, feats, files, protocol


def test_freeze_roundtrip_checksums_and_identical_predictions(small_cfg, tmp_path):
    df, feats, files, protocol = _freeze_fixture(small_cfg, tmp_path)
    fdir = tmp_path / "freeze"
    assert rc.verify_freeze(fdir, protocol) == sorted(files)
    p1 = rc.predict_zero_shot(df.head(20), "09-01", fdir, protocol)
    p2 = rc.predict_zero_shot(df.head(20), "09-01", fdir, protocol)
    np.testing.assert_array_equal(p1, p2)
    meta = json.loads((fdir / "lgbm_0901_meta.json").read_text(encoding="utf-8"))
    assert meta["features"] == feats and meta["hyperparameters"]["max_depth"] <= 3
    # training again reproduces the same files bit by bit
    files2 = rc.freeze_models({"09-01": df}, small_cfg, tmp_path / "freeze2", 1, {"09-01": feats})
    assert {n: f["sha256"] for n, f in files.items()} == {n: f["sha256"] for n, f in files2.items()}


def test_freeze_detects_tampering(small_cfg, tmp_path):
    df, _, _, protocol = _freeze_fixture(small_cfg, tmp_path)
    model = tmp_path / "freeze" / "lgbm_0901.txt"
    model.write_text(model.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(AssertionError):
        rc.verify_freeze(tmp_path / "freeze", protocol)
    with pytest.raises(AssertionError):
        rc.predict_zero_shot(df.head(5), "09-01", tmp_path / "freeze", protocol)


def test_freeze_protocol_is_written_with_registered_hashes_and_at_protocol(small_cfg, tmp_path):
    df, feats, files, _ = _freeze_fixture(small_cfg, tmp_path)
    ci = {"value": 0.1, "lo": 0.0, "hi": 0.2}
    metrics = {"09-01": {"n_region_years": len(df), "pooled": {"model_r2": ci, "model_spearman": ci, "skill_vs_yas1": ci},
                         "within_year": {"mean_rho": 0.1, "lo": 0.0, "hi": 0.2}}}
    path = tmp_path / "protocol.md"
    rc.write_freeze_protocol(path, small_cfg, files, metrics, {"09-01": feats}, {"09-01": df}, "2026-01-01_cybench_eu",
                             {"commit": "abc", "dirty": False}, tmp_path / "freeze")
    text = path.read_text(encoding="utf-8")
    assert rc.read_registered_hashes(path) == {n: f["sha256"] for n, f in files.items()}
    assert rc.verify_freeze(tmp_path / "freeze", path)
    for needle in ("2006–2020", "Wien (AT13)", "Offen, Projektinhaber entscheidet vor dem Test", "ρ > 0", "n = 5 × 15 = 75"):
        assert needle in text


def test_freeze_importance_shares_sum_to_one(small_cfg, tmp_path):
    _freeze_fixture(small_cfg, tmp_path)
    share = rc.freeze_importance(tmp_path / "freeze", ["09-01"], static=[])["09-01"]
    assert sum(share.values()) == pytest.approx(1.0, abs=1e-3)
    assert share["f1"] > share.get("f2", 0)  # the informative feature carries the gain
