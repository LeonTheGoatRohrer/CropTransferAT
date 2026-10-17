"""Styria test machinery on synthetic data (no Styrian yield is read)."""

import numpy as np
import pandas as pd
import pytest

from croptransfer import at_test_stmk
from croptransfer.config import load_config, repo_path


def _frame():
    rng = np.random.default_rng(1)
    rows = []
    for site in ["wagna", "kalsdorf"]:
        for y in range(2018, 2025):
            rows.append({"site": site, "year": y, "score_09-01": -0.01 * (y - 2017), "pred_09-01": 1.0, "ndvi_base": 0.8,
                         "yas_site": 1.2 - 0.03 * (y - 2017) + rng.normal(0, 0.01), "baseline_kind": "baseline_short"})
    d = pd.DataFrame(rows)
    for c in ["07-15", "08-01", "08-15"]:
        d[f"score_{c}"], d[f"pred_{c}"] = d["score_09-01"], d["pred_09-01"]
    return d


def test_evaluate_counts_and_verdicts():
    cfg = load_config()
    r = at_test_stmk.evaluate(_frame(), cfg)
    assert r["n_site_years"] == 14 and r["per_site"] == {"kalsdorf": 7, "wagna": 7}
    a = r["cutoffs"]["09-01"]["S-A_stress_score"]
    assert a["rho"] > 0.9 and a["verdict"] == "nicht auswertbar"      # n = 14 < 15: only descriptive


def test_verdict_becomes_testable_with_enough_site_years():
    cfg = load_config()
    d = pd.concat([_frame(), _frame().assign(site="hatzendorf")], ignore_index=True)
    assert at_test_stmk.evaluate(d, cfg)["cutoffs"]["09-01"]["S-A_stress_score"]["verdict"] in {"bestanden", "nicht belegt"}


def test_config_registered_types_exclude_variety_trials():
    sc = load_config()["at_test_stmk"]
    assert set(sc["trial_types_primary"]) <= set(sc["trial_types_sensitivity"])
    assert not {"sorten", "praxisversuch_sorten"} & set(sc["trial_types_sensitivity"])


def test_registered_hashes_of_second_protocol():
    import re

    from croptransfer import regional_cybench as rc
    text = repo_path("reports/freeze_protocol_at2.md").read_text(encoding="utf-8")
    rows = re.findall(r"\|\s*`((?:reports|results)/[^`]+)`\s*\|\s*`([0-9a-f]{64})`\s*\|", text)
    assert len(rows) == 2
    for rel, digest in rows:
        assert rc.sha256_file(repo_path(rel)) == digest, rel


def test_frozen_stmk_config_matches_config_yaml():
    import json
    frozen = json.loads(repo_path("reports/freeze_at/at_test_stmk_config.json").read_text(encoding="utf-8"))
    assert load_config()["at_test_stmk"] == frozen
