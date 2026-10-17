/**
 * Static project copy (English). Every number here is taken from the project's
 * curated result register app/versions.yaml / reports/results.md and points to
 * its source file. Live charts read the same numbers from evidence.json.
 */
import type { Strength } from '../../components/ui/Badge'

export const PROJECT = {
  name: 'CropTransfer AT',
  competition: 'Bundeswettbewerb Künstliche Intelligenz (BWKI) Austria',
  question:
    'Can satellite time series, weather and soil reveal stress and yield loss in individual maize fields before harvest — learned where yields were measured, then tested unchanged in Austria?',
  fieldYears: 365,
  sites: 'KBS (Michigan), BARC (Maryland), Akron (Colorado)',
}

/* ------------------------------------------------------------------ */
/* Data sources                                                        */
/* ------------------------------------------------------------------ */

export type DataSource = {
  name: string
  provider: string
  role: string
  detail: string
  scale: string
  license: string
  group: 'yield' | 'satellite' | 'weather' | 'soil' | 'regional' | 'austria'
}

export const DATA_SOURCES: DataSource[] = [
  { group: 'yield', name: 'KBS LTER', provider: 'Kellogg Biological Station, Michigan', role: 'Measured plot yields (labels)', detail: '294 maize plot-years incl. organic and cover-crop treatments T1–T4', scale: '≈ 0.6 ha plots', license: 'Use with written permission only' },
  { group: 'yield', name: 'BARC Gridded Yield Archive', provider: 'USDA-ARS Beltsville, Maryland', role: 'Combine yield maps (labels, within-field)', detail: '61 maize field-years, kriged to 10 m blocks', scale: '2–14 ha fields', license: 'U.S. public domain' },
  { group: 'yield', name: 'Akron Dryland', provider: 'USDA-ARS, Colorado', role: 'Sampled yield points', detail: '10 maize sub-field-years, 2019–2022', scale: 'points', license: 'CC0' },
  { group: 'yield', name: 'Kayad maize field', provider: 'Kayad et al. 2019, Po valley, Italy', role: 'Second within-field site', detail: '3 field-years of raw combine points', scale: '22 ha field', license: 'CC BY 4.0' },
  { group: 'satellite', name: 'Sentinel-2 L2A', provider: 'ESA / Copernicus via Google Earth Engine', role: 'Vegetation indices per 10-day dekad', detail: 'NDVI, EVI, NDMI, NDRE, GNDVI · Cloud Score+ masking', scale: '10 m · since 2017', license: 'Copernicus open licence' },
  { group: 'satellite', name: 'HLS v2', provider: 'NASA (Landsat 8/9 + Sentinel-2 harmonised)', role: 'Longer index history for small plots', detail: 'Used from 2013; Landsat 5/7 failed the harmonisation check', scale: '30 m', license: 'NASA open data' },
  { group: 'weather', name: 'ERA5-Land', provider: 'ECMWF / Copernicus', role: 'Daily temperature, rain, soil moisture', detail: 'GDD (10/30 °C), heat days, water balance, VPD', scale: '≈ 9 km grid', license: 'Copernicus licence' },
  { group: 'soil', name: 'SoilGrids 2.0 + Copernicus DEM', provider: 'ISRIC · ESA', role: 'Soil texture, carbon, water capacity, terrain', detail: 'Clay, sand, SOC, AWC, pH; elevation, slope, TPI, TWI', scale: '250 m · 30 m', license: 'CC BY 4.0' },
  { group: 'soil', name: 'SSURGO', provider: 'USDA NRCS', role: 'US crop productivity index (control)', detail: 'NCCPI maize', scale: 'map units', license: 'U.S. public domain' },
  { group: 'regional', name: 'CY-Bench v1.10', provider: 'Kallenberg et al.', role: 'EU regional maize yields + predictors', detail: '16 countries, 8 371 region-years, Austria excluded', scale: 'NUTS-2/3 regions', license: 'EUPL-1.2' },
  { group: 'austria', name: 'INVEKOS field parcels, Statistik Austria, Hatzendorf trials', provider: 'AMA · Statistik Austria · Land Steiermark', role: 'Austrian test data — held back until the freeze', detail: 'Never used for training, features, thresholds or model choice. Opened once after freeze-at-1 for the exploratory test.', scale: 'parcels · states · trial sites', license: 'CC BY 4.0 / public' },
]

/* ------------------------------------------------------------------ */
/* Pipeline                                                            */
/* ------------------------------------------------------------------ */

export const PIPELINE_STEPS = [
  { key: 'field', title: 'Field', body: 'A field polygon and a season. Training fields come with a measured yield.', meta: 'polygon · year' },
  { key: 'pixels', title: 'Satellite pixels', body: 'Every Sentinel-2 scene of the season. Scenes with less than 70 % clear pixels are dropped.', meta: '≈ 35–45 scenes' },
  { key: 'dekads', title: '10-day composites', body: 'Median index per 10-day dekad from 1 April. Missing dekads stay missing — no interpolation.', meta: '21 dekads' },
  { key: 'reference', title: 'Healthy reference', body: 'The median curve of healthy training field-years (≥ 95 % of their normal yield).', meta: '77 field-years (HLS)' },
  { key: 'fusion', title: 'Weather and soil', body: 'ERA5-Land daily weather, SoilGrids and terrain, aggregated with an as-of rule: nothing after the forecast date.', meta: '≈ 9 km · 250 m' },
  { key: 'model', title: 'Scores and models', body: 'Stress score (shortfall below the reference), risk model, within-field map and the EU regional model.', meta: 'pre-registered' },
  { key: 'insight', title: 'Field-level insight', body: 'Which part of the field falls behind, whether the field is unusual, and how the region’s year compares.', meta: 'map · alarm · rank' },
]

export const FEATURE_GROUPS = [
  { title: 'Vegetation indices', items: ['NDVI, EVI, NDMI, NDRE, GNDVI per dekad', 'Peak value and peak date', 'Season integral (EVI area)'], source: 'Sentinel-2 / HLS' },
  { title: 'Relative-to-reference', items: ['Shortfall below the healthy reference (stress score)', 'Deviation per phase: June, July, August', 'Relative to the same field in other years'], source: 'src/croptransfer/stress.py' },
  { title: 'Within-field windows', items: ['Median NDVI of 10 Jul – 18 Aug per 10-m cell (rule B0)', 'Peak-centred NDVI/NDRE windows w1–w3 (model M1)', 'z-scored within each field-year'], source: 'innerfeld_features.py' },
  { title: 'Weather accumulation', items: ['Growing degree days (10/30 °C)', 'Rain, 30-day rain, climatic water balance', 'Heat days > 32 °C during flowering', 'June VPD and max temperature'], source: 'features.daily_weather' },
  { title: 'Soil and terrain', items: ['Clay, sand, organic carbon, pH', 'Available water capacity', 'Elevation, slope, TPI, wetness index'], source: 'SoilGrids, Copernicus DEM' },
  { title: 'Deliberately excluded', items: ['Coordinates, field or region IDs, year', 'Anything observed after the forecast date', 'Any Austrian value before the freeze'], source: 'tests/test_no_leakage.py' },
]

/* ------------------------------------------------------------------ */
/* Experiments (chronological)                                         */
/* ------------------------------------------------------------------ */

export type Experiment = {
  id: string
  date: string
  phase: string
  title: string
  changed: string
  result: string
  numbers: { label: string; value: string }[]
  status: Strength
  source: string
}

export const EXPERIMENTS: Experiment[] = [
  { id: 'v0.1.0', date: '2026-10-15', phase: 'Phase 0', title: 'Data access and rules', changed: '13 data sources screened; working rules fixed before any modelling.', result: 'The Austria rule: Austrian data stays closed until a model is frozen.', numbers: [{ label: 'Sources', value: '13' }, { label: 'Data requests', value: '7' }], status: 'done', source: 'reports/data_review/phase0_data_access.md' },
  { id: 'v0.2.0', date: '2026-10-16', phase: 'Phase 1', title: 'Ground truth assembled', changed: 'All yields in one schema (t/ha at 15.5 % moisture), joined with curves, weather and soil.', result: 'A first signal exists, but on very few independent site-years. Landsat 5/7 failed the harmonisation check.', numbers: [{ label: 'Field-years', value: '365' }, { label: 'EVI integral vs relative yield', value: 'ρ 0.44 [0.10, 0.75]' }], status: 'limited', source: 'results/2026-10-16_phase1/metrics.json' },
  { id: 'v0.3.0', date: '2026-10-16', phase: 'Phase 2', title: 'Base models: satellite, weather, soil', changed: 'Model family trained per feature group, validated on unseen field and unseen year.', result: 'Year-to-year differences do not transfer to unseen years. Within a field, the satellite finds the weak zones.', numbers: [{ label: 'Unseen field + year', value: 'ρ −0.04 [−0.29, 0.37]' }, { label: 'Within field', value: 'ρ 0.68 [0.54, 0.72]' }], status: 'limited', source: 'results/2026-10-16_phase2/criteria_main.json' },
  { id: 'rounds', date: '2026-10-16', phase: 'Phase 4', title: 'Three pre-registered improvement rounds', changed: 'Relative features, fewer features, stronger regularisation — written down before running.', result: 'Relative features help, but no round beats the “normal year” baseline on error.', numbers: [{ label: 'Round 1', value: 'ρ 0.37' }, { label: 'Round 2', value: 'ρ −0.01' }, { label: 'Round 3', value: 'ρ 0.37' }], status: 'failed', source: 'results/2026-10-16_round{1,2,3}/criteria.json' },
  { id: 'v0.4.0', date: '2026-10-16', phase: 'Phase 3 + 4', title: 'Problem fields and the “strong enough?” verdict', changed: 'Fields at risk (≥ 15 % below normal) detected with a reference-curve stress score.', result: 'The simplest method wins. The pre-registered criterion is missed, so the field model was not frozen.', numbers: [{ label: 'Stress score PR-AUC', value: '0.71 (chance 0.33)' }, { label: 'Learned model PR-AUC', value: '0.40' }], status: 'failed', source: 'results/2026-10-16_round3/phase3.json' },
  { id: 'freeze-cybench-1', date: '2026-10-16', phase: 'Phase 5', title: 'EU regional model frozen', changed: 'Independent check: LightGBM on 16 EU countries, Austria excluded, files frozen with checksums.', result: 'A small but statistically certain signal about which years turn out worse.', numbers: [{ label: 'Spearman ρ, 1 Sep', value: '0.38 [0.36, 0.40]' }, { label: 'Skill vs normal year', value: '0.07' }], status: 'certain-small', source: 'results/2026-10-16_cybench_eu/metrics.json' },
  { id: 'side', date: '2026-10-16', phase: 'Side analyses', title: 'Absolute yield, time axis, African fields', changed: 'Three side questions answered with the existing pipeline.', result: 'The satellite sees a field’s yield level, not whether this year is better than usual.', numbers: [{ label: 'Absolute yield (t/ha)', value: 'ρ 0.52 [0.22, 0.76]' }, { label: 'One Acre Fund R²', value: '0.05–0.07' }], status: 'limited', source: 'results/2026-10-16_phase2_Y/metrics.csv' },
  { id: 'multicrop', date: '2026-10-16', phase: 'Data extension', title: 'Training on maize, wheat and peas', changed: 'Four open datasets added; models trained on all crops and per crop.', result: 'No signal beyond the mean; knowledge from wheat and peas does not transfer to maize.', numbers: [{ label: 'Crop transfer to maize', value: 'ρ 0.01 [−0.26, 0.32]' }], status: 'failed', source: 'results/2026-10-16_mehrkultur_h030/criteria.json' },
  { id: 'finetune', date: '2026-10-16', phase: 'Fine-tuning', title: 'Radar, land-surface temperature, GDD axis, green-up date', changed: 'Each source added alone under a keep-rule fixed in advance.', result: 'All four made detection worse. The case review showed the score flags late-sown organic plots.', numbers: [{ label: 'Radar', value: 'ΔPR-AUC −0.14' }, { label: 'Temperature + ET', value: '−0.22' }], status: 'failed', source: 'results/2026-10-16_feinjust_ablation/metrics.csv' },
  { id: 'innerfeld', date: '2026-10-17', phase: 'Within-field', title: 'The field map at three sites', changed: 'Map checked on Italy and Colorado; trained model M1 compared with the raw NDVI rule.', result: 'Same direction at all three sites (49 of 50 field-years positive); conclusive only for BARC.', numbers: [{ label: 'BARC raw rule', value: 'ρ 0.67 [0.59, 0.74]' }, { label: 'Kayad · Colorado', value: '0.60 · 0.63' }], status: 'robust', source: 'results/2026-10-17_innerfeld/metrics.json' },
  { id: 'ceiling', date: '2026-10-17', phase: 'Within-field', title: 'How much is left?', changed: 'Estimated the ceiling set by noise in the combine yield map itself.', result: 'At Kayad the map reaches 0.60 against a ceiling of 0.72–0.94: some room, likely a few hundredths.', numbers: [{ label: 'Kayad ceiling', value: '0.72–0.94' }], status: 'limited', source: 'results/2026-10-17_innerfeld_ceiling/metrics.json' },
  { id: 'smoothing', date: '2026-10-17', phase: 'Within-field', title: 'Smoothing does not help', changed: 'Tested 30-m smoothing of the prediction under pre-registered gates.', result: 'No gain; the map stays at 10-m cells. Earlier block-average gains came from the measurement side.', numbers: [{ label: 'BARC Δρ', value: '−0.013 [−0.017, 0.001]' }], status: 'failed', source: 'results/2026-10-17_innerfeld_runde2/metrics.json' },
  { id: 'freeze-at-1', date: '2026-10-17', phase: 'Phase 7', title: 'Austria test frozen', changed: 'Stress score and EU model frozen side by side, test rules written before any Austrian value was opened.', result: 'Exploratory first test — no winner is chosen on Austrian data.', numbers: [{ label: 'Tag', value: 'freeze-at-1' }], status: 'frozen', source: 'reports/freeze_protocol_at.md' },
  { id: 'at-test-1', date: '2026-10-17', phase: 'Phase 7', title: 'First Austria result', changed: 'The frozen protocol was run once on Upper Austrian variety trials and on Austrian state statistics.', result: 'Good and bad years rank correctly, but the score does no better than plain NDVI and does not separate sites within a year. Styria had no matching trials.', numbers: [{ label: 'Stress score, Upper Austria', value: 'ρ 0.50 [0.19, 0.68]' }, { label: 'EU model, states', value: 'ρ 0.52 [0.13, 0.75]' }], status: 'limited', source: 'results/2026-10-17_at_test/metrics.json' },
]

/* ------------------------------------------------------------------ */
/* Limitations and roadmap                                             */
/* ------------------------------------------------------------------ */

export const LIMITATIONS = [
  { title: 'Few independent seasons', body: 'Field-level data cover only 8–11 independent site-years. That is too few to learn how one year differs from another, which is why the field model missed its pre-registered criterion.', next: 'More site-years: data requests to YIPEEO, DWFI, SwissYield, Mead and YieldSAT are prepared.' },
  { title: 'One conclusive within-field site', body: 'The field map is conclusive only for BARC (41 field-years). Italy and Colorado point the same way but are too small to judge transfer.', next: 'Validate on new combine yield maps as soon as they arrive.' },
  { title: 'An alarm means “unusual curve”', body: 'The stress score flags KBS organic plots every year, including 2020 when they yielded normally — late sowing after a cover crop looks like stress.', next: 'Add sowing dates where known; report alarms as “curve below reference”, not as diagnosis.' },
  { title: 'Austria tested only coarsely', body: 'The first, exploratory test ranks years in Upper Austria (ρ 0.50) but not sites within a year, is no better than plain NDVI, and has no Styrian trials. Nothing has been tested at field level in Austria.', next: 'Austrian field yields for a field-level test (V3); exact trial coordinates for Styria.' },
  { title: 'Coarse environmental layers', body: 'ERA5-Land (≈ 9 km) and SoilGrids (250 m) describe the surroundings, not the single field. They are never interpreted as field-exact.', next: 'Use national soil maps (Bodenklimazahl) for the Austrian check.' },
  { title: 'Clouds and gaps', body: 'Mid-summer often has only 1–3 clear Sentinel-2 scenes per dekad. Gaps stay gaps; the score uses only observed dekads.', next: 'Radar was tested and did not help; keep optical-only for now.' },
]

export const ROADMAP: { stage: 'Done' | 'Now' | 'Next' | 'Later'; title: string; body: string }[] = [
  { stage: 'Done', title: 'US field-level ground truth', body: '365 maize field-years with curves, weather and soil in one schema.' },
  { stage: 'Done', title: 'Within-field weak-zone map', body: 'Median ρ 0.68 against measured yield maps, robust at BARC.' },
  { stage: 'Done', title: 'EU regional model frozen', body: 'LightGBM, 16 countries, checksummed (freeze-cybench-1).' },
  { stage: 'Done', title: 'Stress score with alarm threshold', body: 'At most 20 % false alarms on not-at-risk fields (conformal threshold).' },
  { stage: 'Done', title: 'First Austria test', body: 'Exploratory, freeze-at-1: years rank (ρ ≈ 0.5), fields not yet testable.' },
  { stage: 'Next', title: 'Austrian field yields', body: 'Field-level yields and trial coordinates, to run a field-level test (V3).' },
  { stage: 'Next', title: 'More measured seasons', body: 'Data requests for field yield maps in Europe and the US.' },
  { stage: 'Next', title: 'Analysis backend', body: 'On-demand Sentinel-2 and ERA5 extraction for any drawn field.' },
  { stage: 'Later', title: 'More crops, operational monitoring', body: 'Only after the maize map has been validated outside BARC.' },
]
