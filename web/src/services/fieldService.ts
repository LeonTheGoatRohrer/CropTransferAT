import { getJson } from '../api/client'
import type { FieldAnalysis, FieldsPayload } from '../api/types'
import { simulateAnalysis } from '../data/demo/simulatedAnalysis'
import { cumulative, dekadLabel } from '../lib/dekads'
import { fmt, fmtInt, fmtSigned } from '../lib/format'
import { PIPELINE, type FieldSelection, type PipelineStage, type StageFacts } from '../state/analysisMachine'

/** Prepared demo fields: real held-out field-years from the US training sites. */
export const getPreparedFields = () => getJson<FieldsPayload>('fields.json')

export type AnalysisCallbacks = {
  onStage: (stage: PipelineStage) => void
  onStageDone: (stage: PipelineStage, facts: StageFacts) => void
}

/** UI pacing per stage (ms). Results are precomputed; pacing makes each stage readable. */
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
 * Run the field analysis. Prepared fields replay the project's real results;
 * drawn fields use the in-browser simulation until a backend exists.
 *
 * Backend integration: replace the body with a POST /analyses (polygon) and
 * map the server's progress events onto onStage/onStageDone.
 */
export async function runAnalysis(selection: FieldSelection, cb: AnalysisCallbacks, signal: AbortSignal): Promise<FieldAnalysis> {
  const payload = await getPreparedFields()
  let result: FieldAnalysis
  if (selection.kind === 'prepared') {
    const f = payload.fields.find((x) => x.id === selection.id)
    if (!f) throw new Error(`Prepared field "${selection.id}" not found in fields.json.`)
    result = f
  } else {
    const base = payload.fields[0]
    result = simulateAnalysis(selection.polygon, {
      reference: base.reference,
      normalWeather: base.weather.normal,
      threshold: base.stress?.threshold ?? 0.53,
    })
  }
  const facts = stageFacts(result)
  const reduced = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  for (const stage of PIPELINE) {
    cb.onStage(stage)
    await wait(reduced ? 120 : STAGE_MS[stage], signal)
    cb.onStageDone(stage, facts[stage])
  }
  return result
}

const sum = (xs: (number | null)[]) => xs.reduce<number>((a, b) => a + (b ?? 0), 0)

export function stageFacts(f: FieldAnalysis): Record<PipelineStage, StageFacts> {
  const sat = f.satellite
  const ndvi = sat.indices.ndvi ?? []
  let peakI = -1
  ndvi.forEach((v, i) => {
    if (v != null && (peakI < 0 || v > (ndvi[peakI] as number))) peakI = i
  })
  const w = f.weather
  const prec = sum(w.dekads.prec)
  const precN = sum(w.normal.prec)
  const gdd = cumulative(w.dekads.gdd).at(-1) ?? 0
  const gddN = cumulative(w.normal.gdd).at(-1) ?? 0
  const heat = sum(w.dekads.heat ?? [])
  const s = f.stress
  const px = f.pixels
  const indices = Object.keys(sat.indices).filter((k) => k !== 'gndvi').map((k) => k.toUpperCase())
  return {
    loadingSatellite: {
      headline: `${sat.n_scenes} scenes · ${sat.n_clear_scenes} clear`,
      items: [
        { label: 'Sensor', value: 'Sentinel-2 L2A · 10 m' },
        { label: 'Period', value: `${sat.first_scene ?? '–'} → ${sat.last_scene ?? '–'}` },
        { label: 'Clear-sky rule', value: '≥ 70 % clear pixels' },
      ],
    },
    processingSatellite: {
      headline: `${sat.n_observed_dekads} of 21 dekads observed`,
      items: [
        { label: 'Indices', value: indices.join(' · ') },
        { label: 'NDVI peak', value: peakI >= 0 ? `${fmt(ndvi[peakI], 2)} · ${dekadLabel(peakI, f.year)}` : '–' },
        { label: 'Gaps', value: 'kept as gaps, not interpolated' },
      ],
    },
    loadingWeather: {
      headline: `${fmtInt(prec)} mm rain · ${fmtInt(gdd)} GDD`,
      items: [
        { label: 'Rain vs normal', value: precN ? `${fmtSigned(((prec - precN) / precN) * 100, 0)} %` : '–' },
        { label: 'GDD vs normal', value: gddN ? `${fmtSigned(gdd - gddN, 0)} °C·d` : '–' },
        { label: 'Days > 32 °C', value: fmtInt(heat) },
        { label: 'ERA5-Land cell', value: w.era5_cell },
        { label: 'Normal period', value: w.climatology_years?.join('–') ?? '–' },
      ],
    },
    loadingEnvironment: {
      headline: f.soil ? `Clay ${fmt(f.soil.clay_pct, 0)} % · water capacity ${fmt(f.soil.awc, 2)}` : 'No soil record',
      items: f.soil
        ? [
            { label: 'Organic carbon', value: `${fmt(f.soil.soc, 1)} %` },
            { label: 'pH', value: fmt(f.soil.ph, 1) },
            { label: 'Elevation · slope', value: `${fmt(f.soil.elev_m, 0)} m · ${fmt(f.soil.slope_deg, 1)}°` },
            { label: 'Resolution', value: '250 m, not field-exact' },
          ]
        : [],
    },
    featureEngineering: {
      headline: s?.score != null ? `Stress score ${fmtSigned(s.score, 3)}` : 'Stress score unavailable',
      items: [
        { label: 'Reference', value: `${f.reference.ndvi.n_fieldyears} healthy field-years` },
        ...(s ? [{ label: 'Shortfall Jun · Jul · Aug', value: `${fmt(s.phases.Jun, 2)} · ${fmt(s.phases.Jul, 2)} · ${fmt(s.phases.Aug, 2)}` }] : []),
        ...(px ? [{ label: 'Within-field cells', value: `${fmtInt(px.n_cells)} × ${px.cell_m} m` }] : []),
      ],
    },
    runningModel: {
      headline: s ? (s.alarm ? 'Alarm · curve below reference' : 'No alarm') : 'Not scored',
      items: s
        ? [
            { label: 'Risk', value: `${fmt(s.risk_p, 2)} (alarm at ≥ ${fmt(s.threshold, 2)})` },
            { label: 'Main deviation', value: s.main_phase ?? '–' },
            { label: 'Model', value: f.simulated ? 'simulated (backend not connected)' : 'A0 · logistic on stress score' },
          ]
        : [],
    },
  }
}
