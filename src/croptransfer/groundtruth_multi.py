"""Multi-crop site-year ground truth (reports/plan_mehrkultur.md, steps W2.1-W2.3; D1-D4 PROVISIONAL).

One row per dataset x crop x site x harvest year (mean over plots/cultivars of the trial),
written to data/processed/gt_site_years.parquet. Label tiers (plan section 2):
  S1 field map >= 1 ha | S2 trial site mean, coordinate <= 100 m | S3 coarse coordinate | S4 modelled (BLUP)
Targets (D1): RY = Y / mean(Y of the OTHER years of the same site and crop, >= 2 other years);
RY_nb = Y / mean(Y of the other sites of the same crop, year and dataset, >= 10 other sites).
Counting unit (D2): ERA5-Land cell (0.1 deg) x harvest year (``count_cells``).

AUSTRIA RULE: loaders refuse Austrian rows (``assert_no_austria``); no Austrian file is read.
Usage:  python -m croptransfer.groundtruth_multi
"""

from __future__ import annotations

import glob
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from croptransfer.config import load_config, repo_path

CELL_DEG = 0.1
MIN_YEAR = 2013                      # HLS era (config years.groundtruth)
RY_MIN_OTHER_YEARS = 2               # D1
RY_NB_MIN_OTHER_SITES = 10           # D1
AT_LAT, AT_LON = (46.3, 49.1), (9.5, 17.2)   # bounding box used only as a guard, never to select data

COLUMNS = [
    "dataset", "package", "crop", "crop_variant", "site", "country", "year", "Y_t_ha", "moisture_basis",
    "tier", "label_type", "lat", "lon", "coord_digits", "cell_id", "n_plots", "harvest_date", "sow_date",
]


def cell_id(lat: pd.Series, lon: pd.Series) -> pd.Series:
    """0.1-degree grid cell label (ERA5-Land resolution)."""
    return (np.floor(lat / CELL_DEG).astype(int).astype(str) + "_" + np.floor(lon / CELL_DEG).astype(int).astype(str))


def assert_no_austria(df: pd.DataFrame) -> None:
    """Hard guard of the Austria rule for this module's output."""
    if "country" in df and df["country"].astype(str).str.contains("Austria|^AT$", regex=True).any():
        raise AssertionError("Austrian rows are not allowed before the freeze")
    inside = df["lat"].between(*AT_LAT) & df["lon"].between(*AT_LON) & (df["country"] == "Austria")
    assert not inside.any()


def coord_digits(x: pd.Series) -> pd.Series:
    """Decimal digits of a coordinate (rounded to 6 places first; used to grade the tier)."""
    s = x.round(6).astype(str).str.split(".").str[1].fillna("")
    return s.str.rstrip("0").str.len()


def _excel_date(s: pd.Series) -> pd.Series:
    return pd.to_datetime(pd.to_numeric(s, errors="coerce"), unit="D", origin="1899-12-30")


def _site_year(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    """Mean yield over plots of one trial; keep coordinates and dates of the first row."""
    g = df.groupby(keys, dropna=False)
    out = g.agg(Y_t_ha=("y", "mean"), n_plots=("y", "size"), lat=("lat", "first"), lon=("lon", "first"),
                harvest_date=("harvest_date", "first"), sow_date=("sow_date", "first")).reset_index()
    return out


# ------------------------------------------------------------------------------- loaders -----
def load_invite(raw: Path) -> pd.DataFrame:
    """INVITE winter-wheat variety trials (CZ/HU/CH full coordinates = S2, FR 0.1 deg = S3)."""
    rows = []
    for folder in sorted((raw / "invite" / "unpacked" / "csv").iterdir()):
        fields = pd.read_csv(glob.glob(str(folder / "*Fields.csv"))[0], sep="\t", skiprows=[1, 2], dtype=str)
        plots = pd.read_csv(glob.glob(str(folder / "23_*"))[0], sep="\t", skiprows=[1, 2], dtype=str)
        key = [c for c in fields.columns if c.startswith("experiment_ID")][0]
        pkey = [c for c in plots.columns if c.startswith("experiment_ID")][0]
        fields = fields.rename(columns={key: "eid", "field_latitude": "lat", "field_longitude": "lon",
                                        "site_name": "site"})
        plots = plots.rename(columns={pkey: "eid"})
        plots["y"] = pd.to_numeric(plots["grain_dry_wt_at_maturity"], errors="coerce") / 1000.0  # kg DM/ha -> t/ha
        plots["harvest_date"] = _excel_date(plots["harvest_date"])
        plots["sow_date"] = _excel_date(plots["planting_date"])
        plots = plots[plots["y"].between(1.0, 15.0)]
        fields = fields.drop_duplicates("eid")[["eid", "site", "lat", "lon"]]
        m = plots.merge(fields, on="eid", how="inner")
        m["lat"], m["lon"] = pd.to_numeric(m["lat"]), pd.to_numeric(m["lon"])
        m["year"] = m["harvest_date"].dt.year
        m = m.dropna(subset=["year", "lat", "lon"])
        # French site-years hold two trial types (eid suffix after the year, e.g. NA1Y2 vs NA1Y0): keep them
        # apart so that RY compares like with like (found in W1.3: 312 rows had a twin trial)
        m["trial_type"] = m["eid"].str.extract(r"\d{4}(.*)$")[0].fillna("")
        m["site"] = m["site"] + np.where(m["trial_type"] != "", "|" + m["trial_type"], "")
        sy = _site_year(m, ["eid", "site", "year"])
        sy["country"] = folder.name
        sy["tier"] = np.where(folder.name.endswith("France"), "S3", "S2")
        rows.append(sy.drop(columns="eid"))
    d = pd.concat(rows, ignore_index=True)
    d["year"] = d["year"].astype(int)
    return d.assign(dataset="invite", package="A1", crop="winter_wheat", crop_variant="winter",
                    moisture_basis="dry matter", label_type="Sortenversuchs-Standortmittel")


def load_briwecs(raw: Path) -> pd.DataFrame:
    """BRIWECS winter wheat, 6 German stations; Seedyield in dt/ha at 100 % dry mass."""
    base = raw / "briwecs" / "unpacked" / "Briwecs_data"
    coords = pd.read_csv(base / "metadata" / "BRIWECS_location_coordinates.csv", encoding="utf-8-sig")
    coords = coords.rename(columns={"Location": "site", "Long": "lon", "Lat": "lat"})
    frames = [pd.read_csv(f, sep=";", encoding="latin-1") for f in sorted((base / "data" / "locations").glob("*.csv"))]
    d = pd.concat(frames, ignore_index=True).rename(columns={"Location": "site", "Year": "year"})
    d["y"] = pd.to_numeric(d["Seedyield"], errors="coerce") / 10.0
    d = d[d["y"] > 0].merge(coords, on="site", how="inner")
    d["harvest_date"] = pd.NaT
    d["sow_date"] = pd.NaT
    sy = _site_year(d, ["site", "year"])
    return sy.assign(dataset="briwecs", package="A2", crop="winter_wheat", crop_variant="winter", country="Germany",
                     moisture_basis="dry matter", tier="S2", label_type="Parzellenmittel")


def load_peas(raw: Path) -> pd.DataFrame:
    """French field-pea trials (yield_14 in q/ha at 14 % moisture); coordinates to 0.001 deg."""
    base = raw / "peas_fr"
    obs = pd.read_csv(base / "pea_764685", sep=None, engine="python", encoding="utf-8-sig")
    trials = pd.read_csv(base / "pea_764684", sep=None, engine="python", encoding="utf-8-sig")
    y = obs[obs["variable"] == "yield_14"].copy()
    y["y"] = pd.to_numeric(y["value"], errors="coerce") / 10.0      # q/ha -> t/ha
    y = y[y["y"].between(0.2, 9.0)]
    y = y.drop_duplicates(["site_name", "genotype", "harvest_year", "situation_id"])
    meta = trials.drop_duplicates("site_name")[["site_name", "latitude", "longitude"]]
    y = y.merge(meta, on="site_name", how="left").rename(
        columns={"site_name": "site", "latitude": "lat", "longitude": "lon", "harvest_year": "year",
                 "pea_type": "crop_variant"})
    y["harvest_date"] = pd.to_datetime(y["harvest_date"], errors="coerce")
    y["sow_date"] = pd.to_datetime(y["sowing_date"], errors="coerce")
    y = y.dropna(subset=["lat", "lon"])
    sy = _site_year(y, ["site", "crop_variant", "year"])
    return sy.assign(dataset="peas_fr", package="A9", crop="field_pea", country="France",
                     moisture_basis="14 %", tier="S2", label_type="Parzellenmittel")


def load_nordic(raw: Path) -> pd.DataFrame:
    """Nordic spring-barley trials (BLUP / adjusted values -> tier S4, additional use only)."""
    d = pd.read_csv(raw / "nordic_barley" / "nordic_268105")
    d = d.rename(columns={"latitude": "lat", "longitude": "lon", "country": "country", "region": "site"})
    d["y"] = pd.to_numeric(d["dry_matter_yield"], errors="coerce") / 10.0     # hkg/ha at 15 % moisture -> t/ha (README)
    d["harvest_date"] = pd.to_datetime(d["measure_date"], errors="coerce")
    d["sow_date"] = pd.to_datetime(d["sowing_date"], errors="coerce")
    d["year"] = d["year"].astype(int)
    d = d.dropna(subset=["y", "lat", "lon"])
    d["site"] = d["lat"].round(3).astype(str) + "_" + d["lon"].round(3).astype(str)   # trial ids are per year
    sy = _site_year(d, ["site", "country", "year"])
    return sy.assign(dataset="nordic_barley", package="A11", crop="spring_barley", crop_variant="spring",
                     moisture_basis="15 %", tier="S4", label_type="BLUP/bereinigt")


def load_g2f(raw: Path) -> pd.DataFrame:
    """Genomes to Fields grain maize (curated PHENO.csv): plot yield in t/ha at 15.5 % moisture, 2014-2021.

    Location coordinates are partly estimated by the curators (plan A3) -> tier S3 when the coordinate has
    <= 2 decimals, else S2. Mean over genotypes/replicates per location x year (hybrid trials).
    """
    d = pd.read_csv(raw / "g2f" / "unpacked" / "data" / "PHENO.csv",
                    usecols=["year", "location", "yield", "date_plant", "date_harvest", "latitude", "longitude", "irrigated"])
    d = d.rename(columns={"yield": "y", "latitude": "lat", "longitude": "lon", "location": "site"})
    d = d.dropna(subset=["y", "lat", "lon"])
    d = d[d["y"].between(1.0, 20.0)]
    d["harvest_date"] = pd.to_datetime(d["date_harvest"], errors="coerce")
    d["sow_date"] = pd.to_datetime(d["date_plant"], errors="coerce")
    sy = _site_year(d, ["site", "year"])
    sy["country"] = "North America"
    sy["tier"] = np.where(coord_digits(sy["lat"]) <= 2, "S3", "S2")
    return sy.assign(dataset="g2f", package="A3", crop="maize", crop_variant="grain",
                     moisture_basis="15.5 %", label_type="Hybrid-Versuchsmittel")


LOADERS = {"invite": load_invite, "g2f": load_g2f, "briwecs": load_briwecs, "peas_fr": load_peas, "nordic_barley": load_nordic}


# ------------------------------------------------------------------------------- targets -----
def add_targets(df: pd.DataFrame) -> pd.DataFrame:
    """RY (other years, same site/crop/dataset) and RY_nb (other sites, same crop/year/dataset), D1."""
    df = df.copy()
    site_key = ["dataset", "crop", "crop_variant", "site", "country"]
    g = df.groupby(site_key, dropna=False)["Y_t_ha"]
    n, s = g.transform("count"), g.transform("sum")
    other_n, other_mean = n - 1, (s - df["Y_t_ha"]) / (n - 1)
    df["RY"] = np.where(other_n >= RY_MIN_OTHER_YEARS, df["Y_t_ha"] / other_mean, np.nan)
    yk = ["dataset", "crop", "crop_variant", "year"]
    gy = df.groupby(yk, dropna=False)["Y_t_ha"]
    ny, sy = gy.transform("count"), gy.transform("sum")
    nb_mean = (sy - df["Y_t_ha"]) / (ny - 1)
    df["RY_nb"] = np.where(ny - 1 >= RY_NB_MIN_OTHER_SITES, df["Y_t_ha"] / nb_mean, np.nan)
    return df


def build(cfg: dict[str, Any] | None = None, packages: list[str] | None = None) -> pd.DataFrame:
    """Load all available packages (since MIN_YEAR), add cell id, coordinate digits and targets."""
    cfg = cfg or load_config()
    raw = repo_path(cfg["paths"]["raw"])
    parts = []
    for name, fn in LOADERS.items():
        if (packages and name not in packages) or not (raw / name).exists():
            continue
        parts.append(fn(raw))
    d = pd.concat(parts, ignore_index=True)
    d = d[d["year"] >= MIN_YEAR].copy()
    d["coord_digits"] = coord_digits(d["lat"])
    d["cell_id"] = cell_id(d["lat"], d["lon"])
    assert_no_austria(d)
    d = add_targets(d)
    return d[COLUMNS + ["RY", "RY_nb"]]


def count_cells(df: pd.DataFrame) -> pd.DataFrame:
    """Independent weather-cell x year units per crop and tier (D2, step W2.3)."""
    return (df.drop_duplicates(["crop", "tier", "cell_id", "year"])
              .groupby(["crop", "tier"]).size().rename("cell_years").reset_index())


def main() -> None:
    cfg = load_config()
    d = build(cfg)
    out = repo_path(cfg["paths"]["processed"]) / "gt_site_years.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    d.to_parquet(out, index=False)
    print(d.groupby(["dataset", "crop", "tier"]).agg(site_years=("Y_t_ha", "size"), with_RY=("RY", "count")))
    print(count_cells(d).to_string(index=False))


if __name__ == "__main__":
    main()
