# Zahlen zur Datenkritik Mehr-Kulturen (automatisch erzeugt, `python -m croptransfer.review_multi`)

## counts

```
      dataset          crop tier  site_years  sites  years  cells  y_min  y_med  y_max  n_plots_med  with_RY  with_RY_nb
      briwecs  winter_wheat   S2          25      6      5      6   4.10   6.60   9.20       1320.0       25           0
          g2f         maize   S2         135     38      8     34   2.17   9.52  14.61        483.0      112         127
          g2f         maize   S3           1      1      1      1   9.37   9.37   9.37        479.0        1           0
       invite  winter_wheat   S2         177     35      6     35   2.76   7.35  12.41         37.0      171         177
       invite  winter_wheat   S3         412    152      8     60   4.25   8.12  11.51         15.0      302         412
nordic_barley spring_barley   S4         715    460     12    214   1.60   5.69  10.08         27.0      273         715
      peas_fr     field_pea   S2         318    142     12    111   1.95   4.95   8.29         13.0      176         239
```

## ry

```
      dataset tier   n   p05  median   p95  share_at_risk
      briwecs   S2  25 0.765   1.007 1.250          0.120
          g2f   S2 112 0.680   1.022 1.381          0.259
          g2f   S3   1 0.948   0.948 0.948          0.000
       invite   S2 171 0.661   1.022 1.311          0.199
       invite   S3 302 0.666   1.015 1.243          0.129
nordic_barley   S4 273 0.598   1.010 1.433          0.234
      peas_fr   S2 176 0.595   0.983 1.488          0.267
```

## per_year

```
dataset  briwecs  g2f  invite  nordic_barley  peas_fr
year                                                 
2013.0         0    0      92             37       18
2014.0         0    9      85             72       15
2015.0         6   14      89             71       44
2016.0         6   18      86             65       10
2017.0         6   18      81             64       34
2018.0         3   21      87             54       33
2019.0         4   21      49             63       32
2020.0         0   16      20             60       29
2021.0         0   19       0             62       24
2022.0         0    0       0             60       29
2023.0         0    0       0             57       30
2024.0         0    0       0             50       20
```

## cells

```
         crop tier  cell_years
    field_pea   S2         257
        maize   S2         104
        maize   S3           1
spring_barley   S4         711
 winter_wheat   S2         202
 winter_wheat   S3         224
```

## duplicates

```
 duplicate_site_years
                    0
```

