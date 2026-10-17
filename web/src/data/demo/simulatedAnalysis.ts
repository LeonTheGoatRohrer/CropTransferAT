/**
 * DEMO / SIMULATED DATA — NOT A MODEL RESULT.
 *
 * Fields the visitor draws on the map have no Sentinel-2, ERA5 or soil
 * extraction yet (that needs the Python backend + Google Earth Engine).
 * Until the backend is connected, this module produces a plausible,
 * deterministic stand-in so the whole interface can be explored.
 *
 * What is real here: the healthy reference curve (median of the project's
 * healthy US field-years) and the stress-score formula from
 * src/croptransfer/stress.py. Everything else (curve shape, weather, soil,
 * pixel pattern, risk probability) is invented and flagged `simulated: true`.
 *
 * Replace `simulateAnalysis` with a call to the backend in
 * src/services/fieldService.ts — the return type stays FieldAnalysis.
 */
import type { FieldAnalysis, Nullable, PixelGrid, Polygon, ReferenceBand, WeatherSeries } from '../../api/types'
import i18n from '../../i18n'
import { N_DEKADS, lastCompleteDekad } from '../../lib/dekads'
import { areaM2, bbox, centroid, hashPolygon, metresPerDegree, pointInPolygon, rng } from '../../lib/geo'

const SIM_YEAR = 2025
const FIRST_SCORE_DEKAD = 6 // as in croptransfer.stress.stress_score
const MAX_CELLS = 2400

function dates(year: number) {
  return Array.from({ length: N_DEKADS }, (_, i) => {
    const d = new Date(Date.UTC(year, 3, 1 + 10 * i))
    return d.toISOString().slice(0, 10)
  })
}

const bump = (i: number, mu: number, sigma: number) => Math.exp(-((i - mu) ** 2) / (2 * sigma ** 2))

/** Project formula: mean of min(NDVI − reference, 0) over observed dekads 6..cutoff. */
export function stressScore(ndvi: Nullable<number>[], ref: Nullable<number>[], lastDekad: number): number | null {
  const dev: number[] = []
  for (let i = FIRST_SCORE_DEKAD; i <= lastDekad; i++) {
    const v = ndvi[i]
    const r = ref[i]
    if (v != null && r != null) dev.push(Math.min(v - r, 0))
  }
  return dev.length ? dev.reduce((a, b) => a + b, 0) / dev.length : null
}

function simulatePixels(polygon: Polygon, seed: number, windowNdvi: number, curve: Nullable<number>[]): PixelGrid {
  const rand = rng(seed ^ 0x9e3779b9)
  const [x0, y0, x1, y1] = bbox(polygon)
  const k = metresPerDegree((y0 + y1) / 2)
  const area = areaM2(polygon)
  const cell = Math.max(10, Math.ceil(Math.sqrt(area / MAX_CELLS) / 10) * 10)
  const dx = cell / k.x
  const dy = cell / k.y
  const phase = [rand() * 6, rand() * 6, rand() * 6, rand() * 6]
  const freq = [1.5 + rand() * 2, 1 + rand() * 2.5]
  const cells: PixelGrid['cells'] = []
  let gyMax = 0
  let gxMax = 0
  for (let gy = 0, lat = y1 - dy / 2; lat > y0; gy++, lat -= dy) {
    for (let gx = 0, lon = x0 + dx / 2; lon < x1; gx++, lon += dx) {
      if (!pointInPolygon(lon, lat, polygon)) continue
      const u = (lon - x0) / (x1 - x0)
      const v = (lat - y0) / (y1 - y0)
      const pattern =
        0.55 * Math.sin(freq[0] * Math.PI * u + phase[0]) * Math.cos(freq[1] * Math.PI * v + phase[1]) +
        0.35 * Math.sin(2.7 * Math.PI * (u + v) + phase[2]) +
        0.25 * (rand() - 0.5)
      const ndvi = Math.max(0.2, Math.min(0.92, windowNdvi + 0.07 * pattern))
      const rel = Math.max(0.3, Math.min(1.45, 1 + 2.4 * (ndvi - windowNdvi) + 0.12 * (rand() - 0.5)))
      cells.push([lon, lat, gx, gy, +ndvi.toFixed(3), +rel.toFixed(3)])
      gxMax = Math.max(gxMax, gx)
      gyMax = Math.max(gyMax, gy)
    }
  }
  const nd = cells.map((c) => c[4] as number).sort((a, b) => a - b)
  const thr = nd[Math.floor(nd.length * 0.25)] ?? windowNdvi
  const weak = cells.filter((c) => (c[4] as number) <= thr)
  const problem = cells.filter((c) => c[5] < 0.85)
  const weakProblem = weak.filter((c) => c[5] < 0.85)
  const byDekad = curve.map((m) =>
    cells.map((c) => (m == null ? null : +Math.max(0.05, m + ((c[4] as number) - windowNdvi) * Math.min(1, m / 0.8)).toFixed(3))),
  )
  return {
    n_cells: cells.length,
    cell_m: cell,
    window: 'NDVI (simulated)',
    weak_threshold: thr,
    rho: NaN,
    precision_weak: weak.length ? weakProblem.length / weak.length : NaN,
    prevalence_problem: cells.length ? problem.length / cells.length : NaN,
    lift: NaN,
    recall_weak: problem.length ? weakProblem.length / problem.length : NaN,
    grid: { w: gxMax + 1, h: gyMax + 1 },
    cells,
    cell_fields: ['lon', 'lat', 'gx', 'gy', 'ndvi', 'rel_yield'],
    ndvi_by_dekad: byDekad,
  }
}

function simulateWeather(seed: number, normal: WeatherSeries): { dekads: WeatherSeries; normal: WeatherSeries } {
  const rand = rng(seed ^ 0x51ed27)
  const wet = 0.55 + rand() * 0.9
  const warm = (rand() - 0.4) * 2.2
  const scale = (xs: Nullable<number>[], f: (v: number, i: number) => number) => xs.map((v, i) => (v == null ? null : +f(v, i).toFixed(1)))
  return {
    normal,
    dekads: {
      tmean: scale(normal.tmean, (v) => v + warm + (rand() - 0.5) * 1.6),
      tmax: scale(normal.tmax, (v) => v + warm * 1.2 + (rand() - 0.5) * 2),
      prec: scale(normal.prec, (v) => Math.max(0, v * wet * (0.4 + rand() * 1.2))),
      gdd: scale(normal.gdd, (v) => Math.max(0, v + warm * 9 + (rand() - 0.5) * 8)),
      heat: normal.tmax.map(() => (rand() < 0.15 + warm * 0.05 ? Math.round(rand() * 3) : 0)),
      swvl: scale(normal.swvl, (v) => +(v * (0.8 + 0.3 * wet)).toFixed(2)),
      vpd: scale(normal.vpd, (v) => +(v * (1.15 - 0.2 * wet)).toFixed(2)),
    },
  }
}

export type SimulationInputs = {
  reference: { ndvi: ReferenceBand; evi: ReferenceBand; ndmi: ReferenceBand }
  normalWeather: WeatherSeries
  threshold: number
}

export function simulateAnalysis(polygon: Polygon, inputs: SimulationInputs): FieldAnalysis {
  const seed = hashPolygon(polygon)
  const rand = rng(seed)
  const ref = inputs.reference.ndvi.median
  const depth = rand() < 0.4 ? 0.04 + rand() * 0.16 : rand() * 0.04
  const mu = 10 + rand() * 3
  const ndvi = ref.map((r, i) => {
    if (r == null) return null
    const observed = rand() > 0.35 || i === 0
    if (!observed) return null
    const v = r - depth * bump(i, mu, 2.2) + (rand() - 0.5) * 0.04
    return +Math.max(0.1, Math.min(0.93, v)).toFixed(3)
  })
  const derive = (a: number, b: number) => ndvi.map((v) => (v == null ? null : +(a * v + b).toFixed(3)))
  const last = lastCompleteDekad(9, 1)
  const score = stressScore(ndvi, ref, last)
  // Illustrative mapping only — the real risk model (A0) is a logistic regression fitted on US field-years.
  const p = score == null ? 0.3 : 1 / (1 + Math.exp(2 + 30 * score))
  const phaseMean = (from: number, to: number) => {
    const xs: number[] = []
    for (let i = Math.ceil(from); i < to; i++) if (ndvi[i] != null && ref[i] != null) xs.push(Math.min((ndvi[i] as number) - (ref[i] as number), 0))
    return xs.length ? +(xs.reduce((a, b) => a + b, 0)).toFixed(3) : 0
  }
  const phases = { Jun: phaseMean(6.1, 9.1), Jul: phaseMean(9.1, 12.2), Aug: phaseMean(12.2, 15.3) }
  const main = (Object.entries(phases) as [keyof typeof phases, number][]).sort((a, b) => a[1] - b[1])[0][0]
  const windowVals = [10, 11, 12, 13].map((i) => ndvi[i] ?? ref[i]).filter((v): v is number => v != null)
  const windowNdvi = windowVals.reduce((a, b) => a + b, 0) / Math.max(1, windowVals.length)
  const weather = simulateWeather(seed, inputs.normalWeather)
  const c = centroid(polygon)
  const nObs = ndvi.filter((v) => v != null).length
  const nScenes = 28 + Math.floor(rand() * 20)
  return {
    id: `custom-${seed.toString(16)}`,
    fy_key: `custom|${seed.toString(16)}|${SIM_YEAR}`,
    role: 'custom',
    label: i18n.t('analyse.fields.custom.label'),
    title: i18n.t('analyse.fields.custom.title'),
    blurb: i18n.t('common.simulated'),
    site: 'Custom',
    field_id: seed.toString(16),
    year: SIM_YEAR,
    treatment: null,
    geometry: polygon,
    centroid: c,
    area_m2: Math.round(areaM2(polygon)),
    measured: { yield_t_ha: null, relative_yield: null, at_risk: null },
    satellite: {
      dekad_dates: dates(SIM_YEAR),
      indices: { ndvi, evi: derive(0.68, -0.03), ndmi: derive(0.62, -0.12), ndre: derive(0.66, -0.06) },
      n_scenes: nScenes,
      n_clear_scenes: Math.round(nScenes * (0.4 + rand() * 0.2)),
      n_observed_dekads: nObs,
      first_scene: `${SIM_YEAR}-04-02`,
      last_scene: `${SIM_YEAR}-10-27`,
    },
    reference: inputs.reference,
    stress: {
      score,
      risk_p: +p.toFixed(3),
      alarm: p >= inputs.threshold,
      threshold: inputs.threshold,
      phases,
      main_phase: { Jun: 'June', Jul: 'July', Aug: 'August' }[main],
      rank_in_site_year: null,
      fold: null,
    },
    weather: { era5_cell: `${c[0].toFixed(1)}_${c[1].toFixed(1)}`, climatology_years: [1989, 2023], n_climatology_years: 34, ...weather },
    soil: {
      clay_pct: +(12 + rand() * 22).toFixed(1),
      sand_pct: +(20 + rand() * 40).toFixed(1),
      soc: +(1 + rand() * 2).toFixed(2),
      awc: +(0.1 + rand() * 0.08).toFixed(3),
      ph: +(5.6 + rand() * 1.6).toFixed(1),
      elev_m: +(200 + rand() * 300).toFixed(1),
      slope_deg: +(rand() * 6).toFixed(2),
      twi: +(6 + rand() * 6).toFixed(2),
      nccpi_corn: null,
    },
    pixels: simulatePixels(polygon, seed, windowNdvi, ndvi.map((v, i) => v ?? ref[i])),
    simulated: true,
  }
}
