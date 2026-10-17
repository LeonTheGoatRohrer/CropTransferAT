"""Registered Austria-test freeze: hashes in the protocol match the frozen files; Austria stays out of training."""

import json
import re

import pandas as pd
import pytest

from croptransfer import regional_cybench as rc
from croptransfer.config import load_config, repo_path

PROTOCOL = repo_path("reports/freeze_protocol_at.md")


def test_registered_hashes_match_files():
    text = PROTOCOL.read_text(encoding="utf-8")
    rows = re.findall(r"\|\s*`(reports/freeze_at/[^`]+)`\s*\|\s*`([0-9a-f]{64})`\s*\|", text)
    assert len(rows) == 3
    for rel, digest in rows:
        assert rc.sha256_file(repo_path(rel)) == digest, rel


def test_config_section_is_the_frozen_one():
    cfg = load_config()["at_test"]
    frozen = json.loads(repo_path("reports/freeze_at/at_test_config.json").read_text(encoding="utf-8"))
    assert cfg == frozen


def test_reference_curve_is_complete_and_plausible():
    ref = pd.read_csv(repo_path("reports/freeze_at/stress_reference_hls_ndvi.csv"), index_col=0)["ndvi_median"]
    assert list(ref.index) == list(range(21))
    assert ref.between(0, 1).all()
    assert ref.loc[10:16].min() > 0.6          # canopy peak of healthy maize


def test_sites_have_known_municipalities():
    cent = json.loads(repo_path("reports/freeze_at/site_centroids.json").read_text(encoding="utf-8"))
    assert set(cent) == set(load_config()["at_test"]["sites"])
    for c in cent.values():
        assert 46 < c["lat"] < 49 and 13 < c["lon"] < 17
