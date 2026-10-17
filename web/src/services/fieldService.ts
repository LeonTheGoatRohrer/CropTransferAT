import { getJson } from '../api/client'
import type { FieldAnalysis, FieldsPayload, Polygon } from '../api/types'
import { simulateAnalysis } from '../data/demo/simulatedAnalysis'
import i18n from '../i18n'
import { cumulative, dekadLabel, phaseName } from '../lib/dekads'
import { fmt, fmtDate, fmtInt, fmtSigned } from '../lib/format'
import { PIPELINE, type FieldSelection, type PipelineStage, type StageFacts } from '../state/analysisMachine'
import { api, backendAvailable, type LiveResult } from './backendService'

/** Prepared demo fields: real held-out field-years from the US training sites. */
export const getPreparedFields = () => getJson<FieldsPayload>('fields.json')

export type AnalysisCallbacks = {
  onStage: (stage: PipelineStage) => void
  onStageDone: (stage: PipelineStage, facts: StageFacts) => void
}

export type AnalysisOptions = { year: number; cutoff: string }

/** UI pacing per stage (ms) for replayed results. */
const STAGE_MS: Record<PipelineStage, number> = {
  loadingSatellite: 1100,
  processingSatellite: 1000,
  loadingWeather: 900,
  loadingEnvironment: 750,
  featureEngineering: 950,
  runningModel: 1150,
}

const wait = (ms: number, signal: AbortSignal) =>
  new Promise<void>((resolve, reject) => {
    const t = setTimeout(resolve, ms)
    signal.addEventListener('abort', () => {
      clearTimeout(t)
      reject(new DOMException('aborted', 'AbortError'))
    })
  })

/**
 * Run the field analysis. Prepared fields replay the project's stored results. Drawn fields are computed by
 * the local backend (frozen model, real Sentinel-2/HLS, ERA5-Land, SoilGrids); without backend the labelled
 * in-browser simulation runs.
 */
export async function runAnalysis(selection: FieldSelection, cb: AnalysisCallbacks, signal: AbortSignal, opts: AnalysisOptions): Promise<FieldAnalysis> {
  const payload = await getPreparedFields()
  if (selection.kind === 'prepared') {
    const f = payload.fields.find((x) => x.id === selection.id)
    if (!f) throw new Error(`Prepared field "${selection.id}" not found in fields.json.`)
    return replay(f, cb, signal)
  }
  if (await backendAvailable()) return runLive(selection.polygon, cb, signal, opts, selection.fieldId)
  const base = payload.fields[0]
  const sim = simulateAnalysis(selection.polygon, { reference: base.reference, normalWeather: base.weather.normal, threshold: base.stress?.threshold ?? 0.53 })
  return replay(sim, cb, signal)
}

async function replay(result: FieldAnalysis, cb: AnalysisCallbacks, signal: AbortSignal): Promise<FieldAnalysis> {
  const facts = stageFacts(result)
  const reduced = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  for (const stage of PIPELINE) {
    cb.onStage(stage)
    await wait(reduced ? 120 : STAGE_MS[stage], signal)
    cb.onStageDone(stage, facts[stage])
  }
  return result
}

async function runLive(polygon: Polygon, cb: AnalysisCallbacks, signal: AbortSignal, opts: AnalysisOptions, fieldId?: string): Promise<FieldAnalysis> {
  const id = fieldId ?? (await api.createField(i18n.t('analyse.drawnField'), polygon)).id
  const job = await api.startAnalysis(id, opts.year, opts.cutoff)
  let last: PipelineStage | null = null
  for (;;) {
    await wait(800, signal)
    const a = await api.getAnalysis(job.id)
    const stage = (PIPELINE as readonly string[]).includes(a.stage ?? '') ? (a.stage as PipelineStage) : null
    if (stage && stage !== last) {
      if (last) cb.onStageDone(last, { headline: '…', items: [] })
      cb.onStage(stage)
      last = stage
    }
    if (a.status === 'error') throw new Error(a.error ?? 'Backend error')
    if (a.status === 'completed' && a.result) {
      const f = fromLive(a.result, id, polygon)
      const facts = stageFacts(f)
      for (const s of PIPELINE) cb.onStageDone(s, facts[s])
      return f
    }
  }
}

/** Backend result -> the FieldAnalysis shape all result components render. */
export function fromLive(r: LiveResult, fieldId: string, polygon: Polygon): FieldAnalysis {
  const sc = r.scores[r.cutoff]?.score ?? null
  const phases = r.phases
  const main = (Object.entries(phases) as ['Jun' | 'Jul' | 'Aug', number][]).sort((a, b) => a[1] - b[1])[0]
  const b = r.baseline
  return {
    id: `live-${fieldId}`,
    fy_key: `live|${fieldId}|${r.year}`,
    role: 'custom',
    label: i18n.t('analyse.fields.custom.label'),
    title: i18n.t('analyse.fields.custom.title'),
    blurb: i18n.t('analyse.fields.custom.blurb'),
    site: 'Live',
    field_id: fieldId,
    year: r.year,
    treatment: null,
    geometry: polygon,
    centroid: r.centroid,
    area_m2: r.area_m2,
    measured: {
      yield_t_ha: b?.yield_t_ha ?? null,
      relative_yield: b?.ry ?? null,
      at_risk: b?.ry != null ? b.ry < 0.85 : null,
    },
    satellite: {
      dekad_dates: r.satellite.dekad_dates,
      indices: r.satellite.indices,
      n_scenes: r.satellite.n_scenes,
      n_clear_scenes: r.satellite.n_clear_scenes,
      n_observed_dekads: r.satellite.n_observed_dekads,
      first_scene: r.satellite.first_scene,
      last_scene: r.satellite.last_scene,
    },
    reference: r.reference,
    stress: {
      score: sc,
      risk_p: null,
      alarm: r.alert.state === 'warning' || r.alert.state === 'hint',
      threshold: null,
      phases,
      main_phase: main && main[1] < 0 ? { Jun: 'June', Jul: 'July', Aug: 'August' }[main[0]] : null,
      rank_in_site_year: null,
      fold: null,
    },
    weather: {
      era5_cell: r.weather.era5_cell,
      climatology_years: r.weather.climatology_years,
      n_climatology_years: r.weather.n_climatology_years,
      dekads: r.weather.dekads as unknown as FieldAnalysis['weather']['dekads'],
      normal: r.weather.normal as unknown as FieldAnalysis['weather']['normal'],
    },
    soil: r.soil,
    pixels: null,
    live: true,
    cutoff: r.cutoff,
    alert: r.alert,
    weatherHints: r.weather_hints,
  }
}

const sum = (xs: (number | null)[] | undefined) => (xs ?? []).reduce<number>((a, b) => a + (b ?? 0), 0)

export function stageFacts(f: FieldAnalysis): Record<PipelineStage, StageFacts> {
  const t = i18n.t.bind(i18n)
  const sat = f.satellite
  const ndvi = sat.indices.ndvi ?? []
  let peakI = -1
  ndvi.forEach((v, i) => {
    if (v != null && (peakI < 0 || v > (ndvi[peakI] as number))) peakI = i
  })
  const w = f.weather
  const prec = sum(w.dekads.prec)
  const precN = sum(w.normal.prec)
  const gdd = cumulative(w.dekads.gdd ?? []).at(-1) ?? 0
  const gddN = cumulative(w.normal.gdd ?? []).at(-1) ?? 0
  const heat = sum(w.dekads.heat)
  const s = f.stress
  const px = f.pixels
  const indices = Object.keys(sat.indices).filter((k) => k !== 'gndvi').map((k) => k.toUpperCase())
  const alertKey = f.alert ? { warning: 'alertWarning', hint: 'alertHint', none: 'alertNone', no_statement: 'alertNoStatement' }[f.alert.state] : null
  return {
    loadingSatellite: {
      headline: t('pipeline.facts.scenes', { n: sat.n_scenes, c: sat.n_clear_scenes }),
      items: [
        { label: t('pipeline.facts.sensor'), value: f.live ? t('pipeline.facts.sensorHls') : t('pipeline.facts.sensorS2') },
        { label: t('pipeline.facts.period'), value: `${fmtDate(sat.first_scene)} → ${fmtDate(sat.last_scene)}` },
        { label: t('pipeline.facts.clearRule'), value: t('pipeline.facts.clearRuleV') },
      ],
    },
    processingSatellite: {
      headline: t('pipeline.facts.dekads', { n: sat.n_observed_dekads }),
      items: [
        { label: t('pipeline.facts.indices'), value: indices.join(' · ') },
        { label: t('pipeline.facts.peak'), value: peakI >= 0 ? `${fmt(ndvi[peakI], 2)} · ${dekadLabel(peakI, f.year)}` : '–' },
        { label: t('pipeline.facts.gaps'), value: t('pipeline.facts.gapsV') },
      ],
    },
    loadingWeather: {
      headline: t('pipeline.facts.rain', { r: fmtInt(prec), g: fmtInt(gdd) }),
      items: [
        { label: t('pipeline.facts.rainVsNormal'), value: precN ? `${fmtSigned(((prec - precN) / precN) * 100, 0)} %` : '–' },
        { label: t('pipeline.facts.gddVsNormal'), value: gddN ? `${fmtSigned(gdd - gddN, 0)} °C·d` : '–' },
        { label: t('pipeline.facts.hotDays'), value: fmtInt(heat) },
        { label: t('pipeline.facts.cell'), value: w.era5_cell },
        { label: t('pipeline.facts.normalPeriod'), value: w.climatology_years?.join('–') ?? '–' },
      ],
    },
    loadingEnvironment: {
      headline: f.soil ? t('pipeline.facts.soilHead', { c: fmt(f.soil.clay_pct, 0), a: fmt(f.soil.awc, 2) }) : t('pipeline.facts.noSoil'),
      items: f.soil
        ? [
            { label: t('pipeline.facts.soc'), value: `${fmt(f.soil.soc, 1)} %` },
            { label: t('pipeline.facts.ph'), value: fmt(f.soil.ph, 1) },
            { label: t('pipeline.facts.elevSlope'), value: `${fmt(f.soil.elev_m, 0)} m · ${fmt(f.soil.slope_deg, 1)}°` },
            { label: t('pipeline.facts.resolution'), value: t('pipeline.facts.resolutionV') },
          ]
        : [],
    },
    featureEngineering: {
      headline: s?.score != null ? t('pipeline.facts.score', { v: fmtSigned(s.score, 3) }) : t('pipeline.facts.noScore'),
      items: [
        { label: t('pipeline.facts.reference'), value: t('pipeline.facts.referenceV', { n: f.reference.ndvi.n_fieldyears }) },
        ...(s ? [{ label: t('pipeline.facts.shortfall'), value: `${fmt(s.phases.Jun, 2)} · ${fmt(s.phases.Jul, 2)} · ${fmt(s.phases.Aug, 2)}` }] : []),
        ...(px ? [{ label: t('pipeline.facts.cells'), value: `${fmtInt(px.n_cells)} × ${px.cell_m} m` }] : []),
      ],
    },
    runningModel: {
      headline: alertKey
        ? `${t('pipeline.facts.alertState')}: ${t(`pipeline.facts.${alertKey}`)}`
        : s
          ? s.alarm
            ? t('pipeline.facts.alarm')
            : t('pipeline.facts.noAlarm')
          : t('pipeline.facts.notScored'),
      items: s
        ? [
            ...(s.risk_p != null ? [{ label: t('pipeline.facts.risk'), value: t('pipeline.facts.riskV', { p: fmt(s.risk_p, 2), t: fmt(s.threshold, 2) }) }] : []),
            { label: t('pipeline.facts.mainDev'), value: phaseName(s.main_phase) },
            {
              label: t('pipeline.facts.model'),
              value: f.simulated ? t('pipeline.facts.modelSim') : f.live ? t('pipeline.facts.modelFrozen') : t('pipeline.facts.modelA0'),
            },
          ]
        : [],
    },
  }
}
