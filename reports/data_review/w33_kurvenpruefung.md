# W3.3 Kurvenprüfung und Gate G2 (h = 30)

Regel vorab in DECISIONS.md (2026-10-16). Erzeugt mit `python -m croptransfer.curve_check`.

```
        crop  site_years  curve_ok  share_ok  cell_years_ok  rho_k1_ndvi_max  rho_k2_ndvi_auc  rho_k3_evi_max  rho_k4_ndmi_mean60  rho_k5_ndvi_last  k1_worst_q  k1_best_q  n_pos_rho  g2_pass
   field_pea         176        74     0.420             62           -0.093           -0.015          -0.013               0.025             0.060    0.870692   0.816578          2    False
       maize         112        99     0.884             80            0.079            0.005           0.071               0.008            -0.001    0.775094   0.813829          4     True
winter_wheat         196        99     0.505             99            0.058            0.046          -0.024               0.033             0.076    0.606661   0.664389          4     True
```

**G2 gesamt: bestanden** (mindestens 2 Kulturen müssen bestehen; bestanden: maize, winter_wheat).

Abbildung: `reports/figures/w33_k1_by_ry_quartile.png`.
