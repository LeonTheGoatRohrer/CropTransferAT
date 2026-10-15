"""Official Austrian grain-maize statistics per Bundesland -> data/raw/stat_at_maize.csv.

Sources (see DATA_SOURCES.md):
- 2019 onwards: Statistik Austria crop tables `Feldfr<year>endg.ods` (yield in dt/ha).
- 2010-2018:    Eurostat `apro_cpshr` (NUTS-2, JSON-stat), reported by Statistik Austria.
All yields refer to 14 % grain moisture (Austrian = EU standard for grain maize).

Usage:  python -m croptransfer.regional_stats
"""

from __future__ import annotations

import json
import zipfile
import xml.etree.ElementTree as ET
from itertools import product
from pathlib import Path

import pandas as pd

from croptransfer.config import load_config, repo_path

NUTS2_TO_LAND = {
    "AT11": "Burgenland", "AT12": "Niederösterreich", "AT13": "Wien",
    "AT21": "Kärnten", "AT22": "Steiermark", "AT31": "Oberösterreich",
    "AT32": "Salzburg", "AT33": "Tirol", "AT34": "Vorarlberg", "AT": "Österreich",
}
LANDS = list(NUTS2_TO_LAND.values())
MOISTURE_NOTE = "14 % Kornfeuchte"
SMALL_AREA_HA = 1000  # below this, yields from rounded Eurostat values are unreliable

_NS = {
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
}


def _q(prefix: str, tag: str) -> str:
    return f"{{{_NS[prefix]}}}{tag}"


def read_ods_sheet(path: str | Path, sheet: str) -> list[list[str]]:
    """Read one sheet of an .ods file as rows of strings (numbers as their raw value)."""
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("content.xml"))
    for table in root.iter(_q("table", "table")):
        if table.get(_q("table", "name")) != sheet:
            continue
        rows = []
        for row in table.iter(_q("table", "table-row")):
            cells: list[str] = []
            for cell in row:
                if cell.tag not in (_q("table", "table-cell"), _q("table", "covered-table-cell")):
                    continue
                value = cell.get(_q("office", "value"))
                if value is None:
                    value = " ".join("".join(p.itertext()) for p in cell.findall(_q("text", "p")))
                # repeated empty cells can be huge -> cap the repetition
                repeat = min(int(cell.get(_q("table", "number-columns-repeated"), "1")), 50)
                cells.extend([value] * repeat)
            while cells and cells[-1] == "":
                cells.pop()
            rows.append(cells)
        return rows
    raise KeyError(f"sheet {sheet!r} not found in {path}")


def parse_feldfr_ods(path: str | Path, year: int) -> pd.DataFrame:
    """Grain-maize area (ha), production (t) and yield (dt/ha) per Land for `year`.

    The table has one block per crop; the grain-maize block is the column whose
    header contains 'Körnermais'. Columns: area, production, yield (dt/ha).
    The block also contains a previous-year Austria row, which is skipped.
    """
    rows = read_ods_sheet(path, "Tab1")
    for h, row in enumerate(rows):
        col = next((j for j, v in enumerate(row) if "Körnermais" in v), None)
        if col is not None:
            break
    else:
        raise ValueError(f"no 'Körnermais' column in {path}")

    records = []
    for row in rows[h + 1 : h + 12]:
        name = row[0].replace("\xa0", " ").strip()
        if name.startswith("Österreich"):
            if name != f"Österreich {year}":
                continue  # previous-year comparison row
            name = "Österreich"
        if name not in LANDS:
            continue
        records.append({
            "year": year,
            "bundesland": name,
            "area_ha": float(row[col]),
            "production_t": float(row[col + 1]),
            "yield_dt_ha": float(row[col + 2]),
        })
    if len(records) != len(LANDS):
        raise ValueError(f"{path}: expected {len(LANDS)} rows, got {len(records)}")
    return pd.DataFrame(records)


def parse_jsonstat(path: str | Path) -> dict[tuple[str, str, int], float]:
    """Flatten a Eurostat JSON-stat 2.0 file into {(strucpro, geo, year): value}."""
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    labels = []
    for dim in d["id"]:
        index = d["dimension"][dim]["category"]["index"]
        labels.append(sorted(index, key=index.get))
    out = {}
    for i, combo in enumerate(product(*labels)):
        value = d["value"].get(str(i))
        if value is not None:
            key = dict(zip(d["id"], combo))
            out[key["strucpro"], key["geo"], int(key["time"])] = float(value)
    return out


def eurostat_rows(path: str | Path, years: range) -> pd.DataFrame:
    """Area, production and derived yield per Land from Eurostat apro_cpshr (C1500)."""
    data = parse_jsonstat(path)
    records = []
    for year in years:
        for geo, name in NUTS2_TO_LAND.items():
            area = data[("AR_THS_HA", geo, year)] * 1000
            prod = data[("HPRD_HUMD_EU_THS_T", geo, year)] * 1000
            records.append({"year": year, "bundesland": name, "area_ha": area,
                            "production_t": prod, "yield_dt_ha": 10 * prod / area})
    return pd.DataFrame(records)


def build(raw_dir: Path, first_year: int = 2010, last_year: int = 2026) -> pd.DataFrame:
    """Combine Eurostat (until 2018) and Statistik Austria (2019+) into one table."""
    sa_dir = raw_dir / "statistik_austria"
    eurostat = eurostat_rows(sa_dir / "eurostat" / "apro_cpshr_C1500_AT_nuts2.json",
                             range(first_year, 2019))
    eurostat["source"] = "Eurostat apro_cpshr (crops=C1500), Meldung Statistik Austria"
    eurostat["status"] = "endgültig"

    parts = [eurostat]
    for year in range(2019, last_year + 1):
        final = sa_dir / f"Feldfr{year}endg.ods"
        path = final if final.exists() else sa_dir / f"Feldfr{year}vorl.ods"
        df = parse_feldfr_ods(path, year)
        df["source"] = f"Statistik Austria, Ernteerhebung, {path.name}"
        df["status"] = "endgültig" if path == final else "vorläufig"
        parts.append(df)

    out = pd.concat(parts, ignore_index=True)
    out["yield_t_ha"] = out["yield_dt_ha"] / 10
    out["notes"] = MOISTURE_NOTE
    small = (out["area_ha"] < SMALL_AREA_HA) & (out["year"] < 2019)
    out.loc[small, "notes"] += "; Fläche < 1000 ha: Ertrag aus gerundeten Eurostat-Werten unzuverlässig"
    cols = ["year", "bundesland", "area_ha", "yield_t_ha", "production_t", "source", "status", "notes"]
    return out[cols].sort_values(["year", "bundesland"]).reset_index(drop=True)


def main() -> None:
    cfg = load_config()
    raw = repo_path(cfg["paths"]["raw"])
    df = build(raw)
    target = raw / "stat_at_maize.csv"
    df.to_csv(target, index=False, encoding="utf-8")
    print(f"wrote {len(df)} rows -> {target}")


if __name__ == "__main__":
    main()
