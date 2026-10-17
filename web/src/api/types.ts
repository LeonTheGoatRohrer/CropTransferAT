/**
 * Shared types for everything the UI renders.
 *
 * `fields.json`, `evidence.json` and `explorer.json` are produced by
 * web/scripts/export_web_data.py from the project's real results. A future
 * backend should return the same shapes, so components never change.
 */

export type Nullable<T> = T | null

export type Ci = { value: Nullable<number>; lo: Nullable<number>; hi: Nullable<number> }

export type Polygon = { type: 'Polygon'; coordinates: number[][][] }

export type MultiPolygon = { type: 'MultiPolygon'; coordinates: number[][][][] }

/** Field outlines may consist of several parts; drawn fields are always one Polygon. */
export type FieldGeometry = Polygon | MultiPolygon

export type FieldRole = 'healthy' | 'stressed' | 'average' | 'edge' | 'missed' | 'custom'

export type IndexName = 'ndvi' | 'evi' | 'ndmi' | 'ndre' | 'gndvi'

export type ReferenceBand = {
  p25: Nullable<number>[]
  median: Nullable<number>[]
  p75: Nullable<number>[]
  n_fieldyears: number
}

export type WeatherSeries = {
  tmean: Nullable<number>[]
  tmax: Nullable<number>[]
  prec: Nullable<number>[]
  gdd: Nullable<number>[]
  heat?: Nullable<number>[]
  swvl: Nullable<number>[]
  vpd: Nullable<number>[]
}

export type PixelGrid = {
  n_cells: number
  cell_m: number
  window: string
  weak_threshold: number
  rho: number
  precision_weak: number
  prevalence_problem: number
  lift: number
  recall_weak: number
  grid: { w: number; h: number }
  /** [lon, lat, gx, gy, ndvi (B0 window), relative yield] */
  cells: [number, number, number, number, Nullable<number>, number][]
  cell_fields: string[]
  /** ndvi_by_dekad[dekad][cell] */
  ndvi_by_dekad: Nullable<number>[][]
}

export type FieldStress = {
  score: Nullable<number>
  risk_p: number
  alarm: boolean
  threshold: number
  phases: { Jun: Nullable<number>; Jul: Nullable<number>; Aug: Nullable<number> }
  main_phase: Nullable<string>
  rank_in_site_year: Nullable<number>
  fold: Nullable<string>
}

export type FieldAnalysis = {
  id: string
  fy_key: string
  role: FieldRole
  label: string
  title: string
  blurb: string
  site: string
  field_id: string
  year: number
  treatment: Nullable<string>
  geometry: FieldGeometry
  centroid: [number, number]
  area_m2: number
  measured: { yield_t_ha: Nullable<number>; relative_yield: Nullable<number>; at_risk: Nullable<boolean> }
  satellite: {
    dekad_dates: string[]
    indices: Partial<Record<IndexName, Nullable<number>[]>>
    n_scenes: number
    n_clear_scenes: number
    n_observed_dekads: number
    first_scene: Nullable<string>
    last_scene: Nullable<string>
  }
  reference: { ndvi: ReferenceBand; evi: ReferenceBand; ndmi: ReferenceBand }
  stress: Nullable<FieldStress>
  weather: {
    era5_cell: string
    climatology_years: Nullable<[number, number]>
    n_climatology_years: number
    dekads: WeatherSeries
    normal: WeatherSeries
  }
  soil: Nullable<{
    clay_pct: number
    sand_pct: number
    soc: number
    awc: number
    ph: number
    elev_m: number
    slope_deg: number
    twi: number
    nccpi_corn: Nullable<number>
  }>
  pixels: Nullable<PixelGrid>
  /** true for results produced by the in-browser simulation (no backend yet) */
  simulated?: boolean
}

export type FieldsPayload = { fields: FieldAnalysis[]; dekad_count: number; season_start: string }

export type PrMetrics = {
  n?: number
  positives?: number
  prevalence: number
  pr_auc: number
  pr_auc_lo: number
  pr_auc_hi: number
  recall_at_20fpr?: number
}

export type SiteSummary = {
  n_fy: number
  n_clusters: number
  descriptive: boolean
  rho_median: number
  frac_rho_pos: number
  lift_median: number
  rho_min: number
  rho_max: number
  rho_ci?: [number, number]
}

export type EuCutoff = {
  cutoff: string
  n: number
  countries: number
  spearman: Ci
  r2: Ci
  rmse: Ci
  mae: Ci
  skill_vs_normal: Ci
  within_year: Ci
  baselines: {
    normal_year: { rmse: Ci; mae: Ci; r2: Ci }
    trend: { rmse: Ci; mae: Ci; r2: Ci; spearman: Ci }
  }
  yearly_mean_spearman: number
  n_features: number
}

export type Phase2Row = {
  model: string
  kind: string
  basis: string
  cutoff: string
  variant: string
  n: number
  clusters: number
  rho: number
  rho_lo: number
  rho_hi: number
  median_within_year_rho: Nullable<number>
  rmse: number
  r2: number
  skill_b0: number
  d_rmse_b0: number
  d_rmse_b0_lo: number
  d_rmse_b0_hi: number
}

export type Evidence = {
  within_field_indices: { index: string; n_fy: number; n_fields: number; rho_median: number; frac_rho_pos: number; pr_auc_median: number; prevalence_median: number }[]
  innerfeld_main: {
    untrained: Record<string, Record<string, SiteSummary>>
    E: Record<string, Record<string, SiteSummary>>
    T: Record<string, Record<string, SiteSummary>>
    L: Record<string, Record<string, SiteSummary>>
  }
  innerfeld_gates: Record<string, { n_fy: number; delta: number; ci: [number, number] }>
  innerfeld_label_shuffle: Record<string, { mean: number; sd: number; max_abs: number; frac_positive: number }>
  innerfeld_per_fy: { model: string; scheme: string; site: string; year: number; fy_key: string; rho: Nullable<number>; lift: Nullable<number>; n: number }[]
  within_field_map: { n_fy: number; median_precision: number; median_prevalence: number; median_lift: number; median_recall: number }
  stress_models: Record<string, PrMetrics>
  stress_sensitivity: Record<string, PrMetrics & { median?: number; n_groups?: number }>
  ablation: { feature_set: string; pr_auc: number; pr_auc_lo: number; pr_auc_hi: number; dA: number; dA_lo: number; dA_hi: number; dB: Nullable<number>; dB_lo: Nullable<number>; dB_hi: Nullable<number>; keep: boolean }[]
  alarm: {
    alarm_threshold_oof: number
    alarm_recall: number
    alarm_fpr: number
    alarm_precision: number
    n: number
    n_alarm: number
    main_model: string
    main_phase_alarms: Record<string, number>
    main_phase_at_risk: Record<string, number>
    phase_sum_mean: Record<'at_risk' | 'not_at_risk', Record<string, number>>
  }
  field_years: { fy_key: string; site: string; year: number; score: Nullable<number>; ry: number; p: number; alarm: boolean; risk: boolean; treatment: Nullable<string> }[]
  early_warning_field: ({ cutoff: string } & Record<string, PrMetrics | string>)[]
  phase2_models: Phase2Row[]
  phase4_stages: { stage: string; model: string; kind: string; basis: string; n: number; clusters: number; rho: number; rho_lo: number; rho_hi: number; skill_b0: Nullable<number>; criteria: Record<string, boolean>; strong_enough: boolean }[]
  eu_cutoffs: EuCutoff[]
  eu_per_country: Record<string, { n: number; r2: number; spearman: number; rmse: number; skill_vs_yas1: number; reported: boolean }>
  eu_controls: Record<string, unknown>
  eu_scatter: [number, number, string][]
  eu_residuals: { edges: number[]; model: number[]; normal_year: number[] }
  eu_by_year: { year: number; n: number; mae_model: number; mae_normal: number; mean_yas: number; mean_pred: number }[]
  eu_by_range: { bin: string; n: number; mae_model: number; mae_normal: number; bias_model: number }[]
  eu_meta: { commit: string; freeze: string; n_features_by_cutoff: Record<string, number> }
  absolute_yield: (Phase2Row & Record<string, unknown>)[]
  /** Exploratory Austria test after freeze-at-1 (aggregated results only). */
  austria?: AustriaTest
}

export type RhoCi = { n: number; clusters: number; rho: number; lo: number; hi: number; verdict?: string }

export type AustriaCutoff = {
  'V2-A_stress_score': RhoCi
  'V2-A_within_site': { median: number; n_groups: number; per_group: Record<string, number> }
  'V2-A_within_year': { median: number; n_groups: number; per_group: Record<string, number> }
  'V2-B_regional_model': RhoCi
  'V2-baseline_NDVI': RhoCi | null
  V1_regional_model: RhoCi & { rmse_model: number; rmse_yas1: number; rmse_diff: number; rmse_diff_lo: number; rmse_diff_hi: number }
  'V1-A_stress_score_region': RhoCi
  V1_within_year_regional_model: { median: number; n_groups: number }
}

export type RetrainRow = RhoCi & { rmse: number; rmse_diff_vs_yas1: number; rmse_diff_vs_yas1_lo: number; rmse_diff_vs_yas1_hi: number }

export type AustriaTest = {
  tag: string
  counts: { site_years_with_yas: number; site_years_with_score: number; region_years: number; sites_with_ge6_years: number }
  cutoffs: Record<string, AustriaCutoff>
  retrain?: Record<string, { pred_r0: RetrainRow; pred_r1: RetrainRow; pred_r2: RetrainRow }>
}

export type ExplorerRow = {
  fy_key: string
  dataset: string
  year: number
  treatment: Nullable<string>
  sensor_era: string
  Y_t_ha: Nullable<number>
  RY_descr: Nullable<number>
  area_ha: Nullable<number>
  ndvi_peak: Nullable<number>
  ndvi_jul_aug: Nullable<number>
  n_obs_dekads: Nullable<number>
  gdd: Nullable<number>
  prec: Nullable<number>
  heat32: Nullable<number>
  tmax_jun: Nullable<number>
  vpd_jun: Nullable<number>
  prec_30d: Nullable<number>
  clay: Nullable<number>
  soc: Nullable<number>
  awc: Nullable<number>
}

export type ExplorerPayload = {
  rows: ExplorerRow[]
  columns: string[]
  counts: { field_years: number; by_site: Record<string, number>; years: [number, number]; with_relative_yield: number }
}
