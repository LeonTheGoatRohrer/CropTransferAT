"""Web export (web/scripts/export_web_data.py): strict JSON and the Austria rule."""
import importlib.util
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "web" / "scripts" / "export_web_data.py"


def _load():
    spec = importlib.util.spec_from_file_location("export_web_data", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_clean_makes_strict_json():
    mod = _load()
    out = mod.clean({"a": float("nan"), "b": [np.float64(1.5), np.inf], "c": np.int64(3), "d": np.bool_(True)})
    assert out == {"a": None, "b": [1.5, None], "c": 3, "d": True}
    json.dumps(out, allow_nan=False)


def test_round_helper():
    mod = _load()
    assert mod.r(math.nan) is None
    assert mod.r(0.12345) == 0.123


def test_export_reads_no_austrian_data_files():
    src = SCRIPT.read_text(encoding="utf-8").lower()
    for forbidden in ("interim/at", "interim\" / \"at", "admin_at", "at_trials", "invekos", "stat_at", "freeze_at/"):
        assert forbidden not in src, forbidden
