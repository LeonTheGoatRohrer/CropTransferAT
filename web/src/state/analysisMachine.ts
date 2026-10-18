import type { FieldAnalysis, FieldGeometry, Polygon } from '../api/types'

/**
 * Field-analysis state machine. Each pipeline stage is an explicit state so a
 * real backend (job + progress events) can drive the same UI later.
 */
export const PIPELINE = [
  'loadingSatellite',
  'processingSatellite',
  'loadingWeather',
  'loadingEnvironment',
  'featureEngineering',
  'runningModel',
] as const

export type PipelineStage = (typeof PIPELINE)[number]

export type AnalysisStatus = 'idle' | 'fieldSelected' | PipelineStage | 'completed' | 'error'

export type FieldSelection =
  | { kind: 'prepared'; id: string; polygon: FieldGeometry; areaM2: number; label: string }
  | { kind: 'custom'; polygon: Polygon; areaM2: number; label: string }

/** Facts revealed by a finished stage, shown in the pipeline panel. */
export type StageFacts = { headline: string; items: { label: string; value: string }[] }

export type AnalysisState = {
  status: AnalysisStatus
  selection: FieldSelection | null
  facts: Partial<Record<PipelineStage, StageFacts>>
  result: FieldAnalysis | null
  error: string | null
  runId: number
}

export type AnalysisEvent =
  | { type: 'select'; selection: FieldSelection }
  | { type: 'clear' }
  | { type: 'start' }
  | { type: 'stage'; stage: PipelineStage }
  | { type: 'stageDone'; stage: PipelineStage; facts: StageFacts }
  | { type: 'complete'; result: FieldAnalysis }
  | { type: 'fail'; message: string }

export const initialAnalysis: AnalysisState = {
  status: 'idle',
  selection: null,
  facts: {},
  result: null,
  error: null,
  runId: 0,
}

export const isRunning = (s: AnalysisStatus) => (PIPELINE as readonly string[]).includes(s)

export function analysisReducer(state: AnalysisState, event: AnalysisEvent): AnalysisState {
  switch (event.type) {
    case 'select':
      return { ...initialAnalysis, status: 'fieldSelected', selection: event.selection, runId: state.runId }
    case 'clear':
      return { ...initialAnalysis, runId: state.runId + 1 }
    case 'start':
      if (!state.selection) return state
      return { ...state, status: PIPELINE[0], facts: {}, result: null, error: null, runId: state.runId + 1 }
    case 'stage':
      return isRunning(state.status) ? { ...state, status: event.stage } : state
    case 'stageDone':
      return isRunning(state.status) ? { ...state, facts: { ...state.facts, [event.stage]: event.facts } } : state
    case 'complete':
      return { ...state, status: 'completed', result: event.result }
    case 'fail':
      return { ...state, status: 'error', error: event.message }
  }
}

export const STAGE_TITLES: Record<PipelineStage, { title: string; running: string }> = {
  loadingSatellite: { title: 'Satellitenbeobachtungen', running: 'Sentinel-2-Szenen werden geladen …' },
  processingSatellite: { title: 'Vegetationsindizes', running: '10-Tage-Komposite werden erstellt …' },
  loadingWeather: { title: 'Wetterverlauf', running: 'ERA5-Land-Tageswetter wird geladen …' },
  loadingEnvironment: { title: 'Boden und Gelände', running: 'Boden- und Geländedaten werden geladen …' },
  featureEngineering: { title: 'Merkmale', running: 'Vergleich mit der gesunden Referenz …' },
  runningModel: { title: 'Stress-Bewertung', running: 'Saison wird bewertet …' },
}
