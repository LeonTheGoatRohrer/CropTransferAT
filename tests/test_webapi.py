"""Local FastAPI backend with a fake analysis (no GEE in tests)."""
import time

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from croptransfer import webapi  # noqa: E402

SQ = {"type": "Polygon", "coordinates": [[[15.0, 47.0], [15.004, 47.0], [15.004, 47.003], [15.0, 47.003], [15.0, 47.0]]]}


def fake_analyse(geometry, year, cutoff, hint, warn, progress=None, key="x"):
    for s in ["loadingSatellite", "processingSatellite", "loadingWeather", "loadingEnvironment", "featureEngineering", "runningModel"]:
        progress(s, {"ok": True})
    return {"year": year, "cutoff": cutoff, "alert": {"state": "warning", "levels": []}, "scores": {}}


@pytest.fixture()
def client(tmp_path):
    return TestClient(webapi.create_app(str(tmp_path / "a.sqlite"), analyse_fn=fake_analyse))


def test_field_flow(client):
    assert client.get("/api/health").json()["ok"]
    r = client.post("/api/fields", json={"label": "Feld A", "geometry": SQ})
    assert r.status_code == 201, r.text
    fid = r.json()["id"]
    r = client.put(f"/api/fields/{fid}/yields", json={"unit": "t/ha", "entries": [{"year": y, "value": v} for y, v in
                                                                                   [(2019, 10), (2020, 11), (2021, 9), (2022, 10), (2023, 6)]]})
    assert r.status_code == 200
    assert client.put(f"/api/fields/{fid}/alert", json={"cutoff": "09-01", "hint_pct": 20, "warn_pct": 30}).status_code == 200
    b = client.get(f"/api/fields/{fid}/baseline", params={"year": 2023}).json()
    assert b["state"] == "warning" and b["normal_t_ha"] == 10.0
    aid = client.post(f"/api/fields/{fid}/analyses", json={"year": 2023}).json()["id"]
    for _ in range(50):
        a = client.get(f"/api/analyses/{aid}").json()
        if a["status"] in ("completed", "error"):
            break
        time.sleep(0.05)
    assert a["status"] == "completed", a
    assert a["result"]["baseline"]["state"] == "warning"
    assert client.get("/api/notifications").json()[0]["level"] == "warning"


def test_validation_errors(client):
    big = {"type": "Polygon", "coordinates": [[[15, 47], [15.5, 47], [15.5, 47.5], [15, 47.5], [15, 47]]]}
    assert client.post("/api/fields", json={"label": "x", "geometry": big}).status_code == 422
    fid = client.post("/api/fields", json={"label": "F", "geometry": SQ}).json()["id"]
    assert client.put(f"/api/fields/{fid}/yields", json={"unit": "t/ha", "entries": [{"year": 2020, "value": 40}]}).status_code == 422
    assert client.put(f"/api/fields/{fid}/alert", json={"cutoff": "09-10", "hint_pct": 20, "warn_pct": 30}).status_code == 422
    assert client.put(f"/api/fields/{fid}/alert", json={"cutoff": "09-01", "hint_pct": 30, "warn_pct": 20}).status_code == 422
