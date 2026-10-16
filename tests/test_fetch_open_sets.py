"""Tests for fetch_open_sets: safe unzip, manifest, offline (download is monkeypatched)."""

import json
import zipfile

import pytest

from croptransfer import fetch_open_sets as fos


def _make_zip(path, members):
    with zipfile.ZipFile(path, "w") as zf:
        for name, data in members.items():
            zf.writestr(name, data)


def test_safe_extract_skips_prefix(tmp_path):
    z = tmp_path / "a.zip"
    _make_zip(z, {"data/x.csv": "a", "SiriusQyality/run.exe": "bin"})
    out = fos.safe_extract(z, tmp_path / "out", ["SiriusQyality/"])
    assert out == ["data/x.csv"]
    assert not (tmp_path / "out" / "SiriusQyality").exists()


def test_safe_extract_rejects_path_traversal(tmp_path):
    z = tmp_path / "evil.zip"
    _make_zip(z, {"../escape.txt": "x"})
    with pytest.raises(ValueError):
        fos.safe_extract(z, tmp_path / "out")


def test_fetch_package_writes_manifest(tmp_path, monkeypatch):
    def fake_download(url, target):
        _make_zip(target, {"f.csv": "1,2"})
        return target.stat().st_size

    monkeypatch.setattr(fos, "download", fake_download)
    m = fos.fetch_package("briwecs", tmp_path)
    saved = json.loads((tmp_path / "briwecs" / "MANIFEST.json").read_text(encoding="utf-8"))
    assert saved["files"][0]["sha256"] == m["files"][0]["sha256"]
    assert m["files"][0]["unpacked_files"] == 1
    # second call must not download again
    monkeypatch.setattr(fos, "download", lambda *a: (_ for _ in ()).throw(AssertionError))
    assert fos.fetch_package("briwecs", tmp_path)["package"] == "briwecs"


def test_large_packages_flagged():
    assert fos.PACKAGES["nvt_au"]["large"] is True
    assert not fos.PACKAGES["invite"].get("large")
