"""Smoke test for the Streamlit demo and a pure test of the traffic-light function."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app" / "streamlit_app.py"


def _load_app_module():
    spec = importlib.util.spec_from_file_location("streamlit_app_under_test", APP)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # __name__ != "__main__" -> main() does not run
    return mod


@pytest.mark.parametrize("ry, emoji", [
    (1.20, "🟢"), (0.95, "🟢"), (0.9499, "🟡"), (0.85, "🟡"), (0.8499, "🟠"),
    (0.75, "🟠"), (0.7499, "🔴"), (0.0, "🔴"), (-0.1, "🔴"),
    (float("nan"), "⚪"), (None, "⚪"),
])
def test_ampel_thresholds(ry, emoji):
    assert _load_app_module().ampel(ry)[0] == emoji


def test_cutoff_and_dekad_dates():
    mod = _load_app_module()
    assert mod.cutoff_date(2020, "09-01").isoformat() == "2020-09-01"
    assert mod.dekad_date(2020, 0).isoformat() == "2020-04-01"
    assert mod.dekad_date(2020, 10).isoformat() == "2020-07-10"
    assert mod.fmt(float("nan")) == "–"
    assert mod.fmt(0.5) == "0,50"


def test_app_smoke():
    if not (ROOT / "data" / "app").exists():
        pytest.skip("data/app/ fehlt (python app/precompute.py ausführen)")
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(APP), default_timeout=60).run(timeout=60)
    assert not at.exception, [e.value for e in at.exception]
    assert [t.label for t in at.tabs] == ["US-Ertragsfelder", "Fortschritt", "Österreich"]
