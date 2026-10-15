import numpy as np
import pandas as pd

from croptransfer import stress


def test_last_complete_dekad():
    assert stress.last_complete_dekad("09-01") == 14      # 1.4.+150 d = 29.8. -> dekads 0..14 end before 1.9.
    assert stress.last_complete_dekad("06-01") == 5


def test_abrupt_drop_rule():
    s = pd.DataFrame({"dekad": [9, 10, 11, 12], "value": [0.80, 0.82, 0.60, 0.62]})
    assert stress.abrupt_drop(s)
    recovered = pd.DataFrame({"dekad": [9, 10, 11, 12], "value": [0.80, 0.82, 0.60, 0.80]})
    assert not stress.abrupt_drop(recovered)
    outside = pd.DataFrame({"dekad": [16, 17], "value": [0.8, 0.4]})   # September senescence
    assert not stress.abrupt_drop(outside)


def test_causes():
    r = pd.Series({"rzwsi_flower": 0.5, "cwb_30d": 0, "heat32_flower": 6, "prec_spring": 100})
    assert stress.causes(r, None) == ["Trockenstress", "Hitze"]
    r2 = pd.Series({"rzwsi_flower": 0.0, "cwb_30d": 10, "heat32_flower": 0, "prec_spring": 300})
    assert stress.causes(r2, None) == ["Nässe"]
    r3 = pd.Series({"rzwsi_flower": np.nan, "cwb_30d": 0, "heat32_flower": 0, "prec_spring": 0})
    assert stress.causes(r3, None) == ["Ursache unklar"]


def test_stress_score_as_of():
    dek = pd.DataFrame({"fy_key": "a", "index": "ndvi", "basis": "HLS", "is_observed": True,
                        "dekad": range(21), "value": [0.5] * 21})
    ref = pd.Series(0.6, index=range(21))
    s1 = stress.stress_score(dek, "a", ref, "07-01")
    dek.loc[dek.dekad > 8, "value"] = 0.0          # after 1.7. -> must not matter
    assert stress.stress_score(dek, "a", ref, "07-01") == s1
