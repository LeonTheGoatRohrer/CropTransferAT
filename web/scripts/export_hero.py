"""Export the home-page field (BARC EastFarm 6-60, 2018) to web/public/data/hero.json.

Kept separate from the demo fields of the Analyse page (export_web_data.DEMO_FIELDS), so the
home page can show this field-year while the demo list changes. Reuses build_fields unchanged.
Run after export_web_data.py:  .venv\\Scripts\\python.exe web\\scripts\\export_hero.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import export_web_data as ex  # noqa: E402

# Held-out (out-of-fold) field-year with a 687-cell 10-m grid and a clear July shortfall.
HERO = {
    "id": "barc-2018", "fy_key": "BARC|BARC:EastFarm_6_60|2018", "role": "stressed",
    "place": "Beltsville, Maryland (USA)", "label": "Startseite", "title": "Juli-Stress, erkannt",
    "blurb": "Fällt im Juli unter die Referenz; der Alarm schlägt an.",
}


def main() -> None:
    ex.DEMO_FIELDS = [HERO]
    data = ex.clean(ex.build_fields())
    assert len(data["fields"]) == 1 and data["fields"][0]["id"] == HERO["id"]
    ex.OUT.mkdir(parents=True, exist_ok=True)
    p = ex.OUT / "hero.json"
    p.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":"), default=str, allow_nan=False), encoding="utf-8")
    print(f"{p.relative_to(ex.ROOT)}: {p.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
