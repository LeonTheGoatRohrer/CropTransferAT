import { getJson } from '../api/client'
import type { FieldAnalysis, FieldsPayload } from '../api/types'
import { simulateAnalysis } from '../data/demo/simulatedAnalysis'
import { cumulative, dekadLabel } from '../lib/dekads'
import { fmt, fmtInt, fmtSigned } from '../lib/format'
import { PIPELINE, type FieldSelection, type PipelineStage, type StageFacts } from '../state/analysisMachine'

/** Display names for phase values that may arrive in English from the data export. */
const PHASE_DE: Record<string, string> = { June: 'Juni', July: 'Juli', August: 'August', Jun: 'Juni', Jul: 'Juli', Aug: 'August' }
export const phaseLabel = (p: string | null | undefined): string | null => (p == null ? null : (PHASE_DE[p] ?? p))

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
    if (!f) throw new Error(`Vorbereitetes Feld „${selection.id}“ nicht in fields.json gefunden.`)
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
      headline: `${sat.n_scenes} Szenen · ${sat.n_clear_scenes} wolkenfrei`,
      items: [
        { label: 'Sensor', value: 'Sentinel-2 L2A · 10 m' },
        { label: 'Zeitraum', value: `${sat.first_scene ?? '–'} → ${sat.last_scene ?? '–'}` },
        { label: 'Wolkenfrei-Regel', value: '≥ 70 % wolkenfreie Pixel' },
      ],
    },
    processingSatellite: {
      headline: `${sat.n_observed_dekads} von 21 Dekaden beobachtet`,
      items: [
        { label: 'Indizes', value: indices.join(' · ') },
        { label: 'NDVI-Maximum', value: peakI >= 0 ? `${fmt(ndvi[peakI], 2)} · ${dekadLabel(peakI, f.year)}` : '–' },
        { label: 'Lücken', value: 'bleiben Lücken, nicht interpoliert' },
      ],
    },
    loadingWeather: {
      headline: `${fmtInt(prec)} mm Niederschlag · ${fmtInt(gdd)} GDD`,
      items: [
        { label: 'Niederschlag ggü. Mittel', value: precN ? `${fmtSigned(((prec - precN) / precN) * 100, 0)} %` : '–' },
        { label: 'GDD ggü. Mittel', value: gddN ? `${fmtSigned(gdd - gddN, 0)} °C·d` : '–' },
        { label: 'Tage > 32 °C', value: fmtInt(heat) },
        { label: 'ERA5-Land-Zelle', value: w.era5_cell },
        { label: 'Vergleichszeitraum', value: w.climatology_years?.join('–') ?? '–' },
      ],
    },
    loadingEnvironment: {
      headline: f.soil ? `Ton ${fmt(f.soil.clay_pct, 0)} % · Wasserspeicherung ${fmt(f.soil.awc, 2)}` : 'Keine Bodendaten',
      items: f.soil
        ? [
            { label: 'Org. Kohlenstoff', value: `${fmt(f.soil.soc, 1)} %` },
            { label: 'pH', value: fmt(f.soil.ph, 1) },
            { label: 'Seehöhe · Neigung', value: `${fmt(f.soil.elev_m, 0)} m · ${fmt(f.soil.slope_deg, 1)}°` },
            { label: 'Auflösung', value: '250 m, nicht feldgenau' },
          ]
        : [],
    },
    featureEngineering: {
      headline: s?.score != null ? `Stress-Score ${fmtSigned(s.score, 3)}` : 'Stress-Score nicht verfügbar',
      items: [
        { label: 'Referenz', value: `${fmtInt(f.reference.ndvi.n_fieldyears)} gesunde Feld-Jahre` },
        ...(s ? [{ label: 'Rückstand Jun · Jul · Aug', value: `${fmt(s.phases.Jun, 2)} · ${fmt(s.phases.Jul, 2)} · ${fmt(s.phases.Aug, 2)}` }] : []),
        ...(px ? [{ label: 'Teilflächen-Zellen', value: `${fmtInt(px.n_cells)} × ${fmt(px.cell_m, 0)} m` }] : []),
      ],
    },
    runningModel: {
      headline: s ? (s.alarm ? 'Alarm · Kurve unter Referenz' : 'Kein Alarm') : 'Nicht bewertet',
      items: s
        ? [
            { label: 'Risiko', value: `${fmt(s.risk_p, 2)} (Alarm ab ${fmt(s.threshold, 2)})` },
            { label: 'Größte Abweichung', value: phaseLabel(s.main_phase) ?? '–' },
            { label: 'Modell', value: f.simulated ? 'simuliert (Backend nicht verbunden)' : 'A0 · logistisch auf Stress-Score' },
          ]
        : [],
    },
  }
}
