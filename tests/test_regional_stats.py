"""Parsers for Statistik Austria (.ods) and Eurostat (JSON-stat) on synthetic files."""

import json
import zipfile

import pytest

from croptransfer.regional_stats import LANDS, eurostat_rows, parse_feldfr_ods, parse_jsonstat

T = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
X = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
O = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"


def _cell(v):
    if isinstance(v, float):
        return f'<table:table-cell office:value-type="float" office:value="{v}"><text:p>{v}</text:p></table:table-cell>'
    return f"<table:table-cell><text:p>{v}</text:p></table:table-cell>"


def _write_ods(path, rows):
    body = "".join("<table:table-row>" + "".join(_cell(v) for v in r) + "</table:table-row>" for r in rows)
    xml = (f'<office:document-content xmlns:office="{O}" xmlns:table="{T}" xmlns:text="{X}">'
           f'<office:body><office:spreadsheet><table:table table:name="Tab1">{body}'
           "</table:table></office:spreadsheet></office:body></office:document-content>")
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("content.xml", xml)


def test_parse_feldfr_ods(tmp_path):
    # layout: name | other crop yield | Körnermais area | production | yield (dt/ha)
    rows = [["", "", "Körnermais inkl. CCM"]]
    lands = [n for n in LANDS if n != "Österreich"]
    for i, name in enumerate(lands):
        rows.append([name, 50.0, 1000.0 + i, 10000.0 + i, 100.0 + i])
    rows.append(["Österreich\xa02025", 60.0, 9999.0, 99999.0, 110.0])
    rows.append(["Österreich 2024", 60.0, 8888.0, 88888.0, 99.0])  # must be skipped
    path = tmp_path / "Feldfr2025endg.ods"
    _write_ods(path, rows)

    df = parse_feldfr_ods(path, 2025)
    assert len(df) == len(LANDS)
    at = df.set_index("bundesland").loc["Österreich"]
    assert at["area_ha"] == 9999.0 and at["yield_dt_ha"] == 110.0
    assert df.set_index("bundesland").loc["Burgenland", "production_t"] == 10000.0


def test_parse_feldfr_ods_rejects_missing_rows(tmp_path):
    path = tmp_path / "bad.ods"
    _write_ods(path, [["", "Körnermais"], ["Burgenland", 1.0, 2.0, 3.0]])
    with pytest.raises(ValueError):
        parse_feldfr_ods(path, 2025)


def test_jsonstat_and_eurostat_yield(tmp_path):
    # 2 strucpro x 1 geo x 2 years, row-major in id order
    d = {
        "id": ["strucpro", "geo", "time"],
        "dimension": {
            "strucpro": {"category": {"index": {"AR_THS_HA": 0, "HPRD_HUMD_EU_THS_T": 1}}},
            "geo": {"category": {"index": {"AT22": 0}}},
            "time": {"category": {"index": {"2017": 0, "2018": 1}}},
        },
        "value": {"0": 50.0, "1": 40.0, "2": 600.0, "3": 400.0},
    }
    path = tmp_path / "es.json"
    path.write_text(json.dumps(d), encoding="utf-8")

    flat = parse_jsonstat(path)
    assert flat[("AR_THS_HA", "AT22", 2018)] == 40.0
    assert flat[("HPRD_HUMD_EU_THS_T", "AT22", 2017)] == 600.0

    # restrict the mapping to the one region in the fixture
    import croptransfer.regional_stats as rs
    old = rs.NUTS2_TO_LAND
    rs.NUTS2_TO_LAND = {"AT22": "Steiermark"}
    try:
        df = eurostat_rows(path, range(2017, 2019))
    finally:
        rs.NUTS2_TO_LAND = old
    # 600 kt / 50 kha = 12 t/ha = 120 dt/ha
    assert df.loc[df.year == 2017, "yield_dt_ha"].item() == pytest.approx(120.0)
    assert df.loc[df.year == 2018, "area_ha"].item() == pytest.approx(40_000.0)
