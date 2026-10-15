"""Phase-0 inspection of the One Acre Fund maize survey (Zenodo 10.5281/zenodo.11115815).

Only the survey table is inspected; no satellite data is touched (PLAN.md §3.1: the
pre-filters are fixed before satellite data is seen).

Usage:  python -m croptransfer.one_acre_fund      (prints the summary tables as Markdown)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from croptransfer.config import load_config, repo_path

# The CSV has no "location precision" column. The dataset description says soil data
# (WISE + iSDA) was only retrieved "for observations with field-level coordinates",
# so a present soil value marks an exact GPS position (proxy, checked against the 70 %
# given in the description).
SOIL_COLUMNS = ["soil_rzpawhc", "soil_clay", "soil_pH", "soil_orgC", "soil_ECEC"]
FIELD_SIZE_CANDIDATES = ["field_size_ha", "field_ha", "area_ha", "plot_size_ha", "field_size"]


def load(path: str | Path | None = None) -> pd.DataFrame:
    """Read the survey CSV (default path from config.yaml)."""
    if path is None:
        cfg = load_config()
        path = repo_path(cfg["paths"]["raw"]) / cfg["one_acre_fund"]["file"]
    return pd.read_csv(path)


def exact_location(df: pd.DataFrame) -> pd.Series:
    """True where all soil columns are present (= field-level GPS, see module note)."""
    return df[SOIL_COLUMNS].notna().all(axis=1)


def max_decimals(values: pd.Series) -> int:
    """Largest number of decimal places in a float column (coordinate rounding)."""
    def _dec(x: float) -> int:
        text = repr(float(x))
        return len(text.split(".")[1].rstrip("0")) if "." in text else 0
    return int(values.dropna().map(_dec).max())


def rounding_error_m(decimals: int, lat_deg: float = 0.0) -> tuple[float, float]:
    """Max. position error (m) from rounding to `decimals` places: (north-south, east-west)."""
    half_step = 0.5 * 10.0 ** (-decimals)
    m_per_deg = 111_320.0
    return half_step * m_per_deg, half_step * m_per_deg * np.cos(np.radians(lat_deg))


def field_size_column(df: pd.DataFrame) -> str | None:
    """Name of the field-size column, or None if the file has none."""
    return next((c for c in FIELD_SIZE_CANDIDATES if c in df.columns), None)


def prefilter(df: pd.DataFrame, min_field_ha: float) -> pd.DataFrame:
    """Apply the PLAN.md §3.1 pre-filters step by step.

    Returns one row per step with the number of fields left. A step that cannot be
    applied (column missing) is reported with n = NaN instead of being skipped silently.
    """
    steps = [("alle Felder", len(df))]
    exact = exact_location(df)
    steps.append(("exakte GPS-Position", int(exact.sum())))
    size_col = field_size_column(df)
    if size_col is None:
        steps.append((f"Feldgröße ≥ {min_field_ha} ha", np.nan))
    else:
        steps.append((f"Feldgröße ≥ {min_field_ha} ha", int((exact & (df[size_col] >= min_field_ha)).sum())))
    return pd.DataFrame(steps, columns=["Schritt", "n"])


def damage_rates(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Share of fields with a reported damage per country × year (NaN = not in data)."""
    out = {}
    for col in columns:
        reported = df[col].map({True: 1.0, False: 0.0, "True": 1.0, "False": 0.0})
        out[col] = reported.groupby([df["country"], df["year"]]).mean()
    return pd.DataFrame(out)


def likely_not_asked(rates: pd.DataFrame) -> pd.DataFrame:
    """Country-years where a damage share is exactly 0 – probably the question was not asked."""
    return rates.eq(0.0)


def neighbour_groups(df: pd.DataFrame, min_other: int) -> pd.Series:
    """Fields per climate zone × season × year; RY_nb needs ≥ min_other other fields."""
    sizes = df.groupby(["cz", "season", "year"]).size()
    return sizes[sizes >= min_other + 1]


def summary(df: pd.DataFrame, cfg: dict) -> dict[str, pd.DataFrame | dict]:
    """All Phase-0 key figures as tables."""
    oaf = cfg["one_acre_fund"]
    exact = exact_location(df)
    plant = pd.to_datetime(df["plant_date"], errors="coerce")
    harvest = pd.to_datetime(df["harvest_date"], errors="coerce")
    shared = df[exact].groupby(["lon", "lat", "year", "season"])["year"].transform("size")
    dec = max(max_decimals(df["lon"]), max_decimals(df["lat"]))
    groups = neighbour_groups(df[exact], oaf["ry_nb_min_other_fields"])
    facts = {
        "rows": len(df),
        "columns": len(df.columns),
        "years": sorted(df["year"].unique().tolist()),
        "exact_location": int(exact.sum()),
        "exact_share": round(float(exact.mean()), 3),
        "coord_decimals": dec,
        "rounding_error_m": tuple(round(v) for v in rounding_error_m(dec)),
        "field_size_column": field_size_column(df),
        "moisture_column": next((c for c in df.columns if "moist" in c.lower()), None),
        "exact_sharing_point": int((shared > 1).sum()),
        "exact_max_per_point": int(shared.max()),
        "zero_yield": int((df["yield_kg_ha"] == 0).sum()),
        "plant_date_present": int(plant.notna().sum()),
        "harvest_date_present": int(harvest.notna().sum()),
        "plant_year_differs": int((plant.dt.year != df["year"])[plant.notna()].sum()),
        "earliest_plant_date": str(plant.min().date()),
        "ry_nb_groups": len(groups),
        "ry_nb_fields": int(groups.sum()),
    }
    by_year = pd.crosstab(df["country"], df["year"], margins=True, margins_name="Summe")
    exact_by_year = pd.crosstab(df["country"], df["year"], values=exact, aggfunc="sum").fillna(0).astype(int)
    yield_med = df.groupby(["country", exact.rename("exakt")])["yield_kg_ha"].median().unstack().round(0)
    rates = damage_rates(df, oaf["damage_columns"]).round(2)
    return {
        "facts": facts,
        "prefilter": prefilter(df, oaf["min_field_ha"]),
        "by_year": by_year,
        "exact_by_year": exact_by_year,
        "yield_median_by_exact": yield_med,
        "damage_rates": rates,
        "damage_likely_not_asked": likely_not_asked(rates),
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    cfg = load_config()
    result = summary(load(), cfg)
    for name, value in result.items():
        print(f"\n### {name}\n")
        if isinstance(value, dict):
            for key, val in value.items():
                print(f"- {key}: {val}")
        else:
            print(value.to_string())


if __name__ == "__main__":
    main()
