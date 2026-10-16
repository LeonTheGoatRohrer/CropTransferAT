"""Tests for the website: pure helpers, the version registry, and a smoke run of every page."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.ui.common import FIG_DIR, GLOSSARY, STATUS, ampel, cutoff_date, cutoff_label, dekad_date, fmt  # noqa: E402

APP = ROOT / "app" / "streamlit_app.py"
VERSIONS = ROOT / "app" / "versions.yaml"


@pytest.mark.parametrize("ry, emoji", [
    (1.20, "🟢"), (0.95, "🟢"), (0.9499, "🟡"), (0.85, "🟡"), (0.8499, "🟠"),
    (0.75, "🟠"), (0.7499, "🔴"), (0.0, "🔴"), (-0.1, "🔴"),
    (float("nan"), "⚪"), (None, "⚪"),
])
def test_ampel_thresholds(ry, emoji):
    assert ampel(ry)[0] == emoji


def test_formatting_helpers():
    assert cutoff_date(2020, "09-01").isoformat() == "2020-09-01"
    assert dekad_date(2020, 0).isoformat() == "2020-04-01"
    assert dekad_date(2020, 10).isoformat() == "2020-07-10"
    assert cutoff_label("09-01") == "1.9."
    assert fmt(float("nan")) == "–"
    assert fmt(0.5) == "0,50"
    assert fmt(-0.25) == "−0,25"


def test_versions_registry_is_consistent():
    reg = yaml.safe_load(VERSIONS.read_text(encoding="utf-8"))
    versions = reg["versions"]
    ids = [v["id"] for v in versions]
    assert len(ids) == len(set(ids)), "doppelte Versions-IDs"
    dates = [str(v["date"]) for v in versions]
    assert dates == sorted(dates, reverse=True), "Versionen müssen neueste zuerst stehen"
    for v in versions:
        for key in ("id", "date", "phase", "title", "status", "changed", "plain"):
            assert v.get(key), f"{v.get('id')}: Feld {key} fehlt"
        assert v["status"] in STATUS, f"{v['id']}: unbekannter Status {v['status']}"
        for m in v.get("metrics") or []:
            assert m.get("label") and m.get("value") and m.get("plain"), f"{v['id']}: Kennzahl unvollständig"
        for f in v.get("figures") or []:
            assert (FIG_DIR / f["file"]).exists(), f"{v['id']}: Abbildung fehlt {f['file']}"
        for link in v.get("links") or []:
            assert (ROOT / link["path"]).exists(), f"{v['id']}: Pfad fehlt {link['path']}"
    for run in reg["benchmark_runs"]:
        assert (ROOT / run["dir"] / "metrics.csv").exists(), run["dir"]
        assert (ROOT / run["dir"] / run["criteria"]).exists(), run["dir"]
    assert set(GLOSSARY)  # glossary is non-empty


def _page_script(root: str, module: str) -> None:
    """Run one page module standalone (executed by AppTest.from_function)."""
    import importlib
    import inspect
    import sys

    if root not in sys.path:
        sys.path.insert(0, root)
    from app.ui.common import APP_DATA, load_app_data

    mod = importlib.import_module(f"app.ui.{module}")
    if inspect.signature(mod.page).parameters:
        mod.page(load_app_data(str(APP_DATA)))
    else:
        mod.page()


PAGES = ["page_home", "page_approach", "page_versions", "page_benchmarks", "page_fields", "page_train", "page_log"]


def test_app_entry_smoke():
    if not (ROOT / "data" / "app" / "benchmarks.csv").exists():
        pytest.skip("data/app/ fehlt oder veraltet (python app/precompute.py ausführen)")
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(APP), default_timeout=90).run(timeout=90)
    assert not at.exception, [e.value for e in at.exception]
    assert at.title[0].value.startswith("🌽 CropTransfer AT")


@pytest.mark.parametrize("module", PAGES)
def test_each_page_renders(module):
    if not (ROOT / "data" / "app" / "benchmarks.csv").exists():
        pytest.skip("data/app/ fehlt oder veraltet (python app/precompute.py ausführen)")
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_function(_page_script, default_timeout=120, kwargs={"root": str(ROOT), "module": module})
    at.run(timeout=120)
    assert not at.exception, (module, [e.value for e in at.exception])
    assert at.title, module
