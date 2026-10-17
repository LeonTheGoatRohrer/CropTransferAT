/**
 * Client for the local FastAPI backend (python -m croptransfer.webapi, http://127.0.0.1:8765).
 * The backend is local only; when it is not running, callers fall back to the browser (path A)
 * or to the labelled simulation (path B).
 */
import type { Polygon } from '../api/types'

const BACKEND: string = import.meta.env.VITE_BACKEND ?? 'http://127.0.0.1:8765'

export type AlertLevel = {
  level: 'warning' | 'hint'
  x_pct: number
  statement: 'ok' | 'no_statement'
  threshold: number | null
  triggered: boolean
  k_hit: number | null
  n_alert: number | null
  prevalence: number | null
  reasons: string[]
}

export type AlertResult = { state: 'warning' | 'hint' | 'none' | 'no_statement'; cutoff: string; score: number | null; levels: AlertLevel[] }

export type Baseline = {
  year: number
  n_other_years: number
  history: 'too_little' | 'with_hint' | 'ok'
  normal_t_ha: number | null
  yield_t_ha: number | null
  ry: number | null
  per_year: { year: number; t_ha: number; normal_others: number | null; ry: number | null; n_other: number }[]
  state: 'no_assessment' | 'pending' | 'normal' | 'hint' | 'warning' | 'ok'
  hint_below_t_ha?: number
  warning_below_t_ha?: number
}

export type FieldRecord = { id: string; label: string; crop: string; geometry: Polygon; area_m2: number; created_at: string; n_yields?: number }
export type YieldRow = { year: number; t_ha: number; unit: 't/ha' | 'dt/ha'; value: number }
export type AlertSetting = { cutoff: string; hint_pct: number; warn_pct: number; updated_at?: string }
export type FieldDetail = FieldRecord & { yields: YieldRow[]; alert: AlertSetting | null; baseline: Baseline }

export type CalibrationRow = {
  cutoff: string
  x_pct: number
  n_valid: number
  n_site_years: number
  n_event: number
  prevalence: number | null
  n_alert: number
  k_hit: number
  precision: number | null
  precision_ci: [number | null, number | null]
  recall: number | null
  fpr: number | null
  alert_site_years: number
  statement: 'ok' | 'no_statement'
  reasons: string[]
}
export type Calibration = { date: string; n_field_years: number; n_site_years: number; table: CalibrationRow[]; frozen_thresholds: Record<string, number | null> }

export type LiveResult = {
  year: number
  cutoff: string
  area_m2: number
  centroid: [number, number]
  satellite: {
    indices: Record<'ndvi' | 'evi' | 'ndmi', (number | null)[]>
    n_scenes: number
    n_clear_scenes: number
    n_observed_dekads: number
    first_scene: string | null
    last_scene: string | null
    dekad_dates: string[]
  }
  reference: Record<'ndvi' | 'evi' | 'ndmi', { p25: (number | null)[]; median: (number | null)[]; p75: (number | null)[]; n_fieldyears: number }>
  scores: Record<string, { score: number | null; n_obs: number }>
  phases: { Jun: number; Jul: number; Aug: number }
  alert: AlertResult
  weather: { era5_cell: string; climatology_years: [number, number]; n_climatology_years: number; dekads: Record<string, (number | null)[]>; normal: Record<string, (number | null)[]> }
  weather_hints: { key: 'drought' | 'heat_flowering' | 'wet_spring'; value_cwb_30d_mm?: number | null; days?: number; mm?: number; rule: string }[]
  soil: { clay_pct: number; sand_pct: number; soc: number; awc: number; ph: number; elev_m: number; slope_deg: number; twi: number; nccpi_corn: null } | null
  baseline?: Baseline
}

export type AnalysisJob = {
  id: string
  field_id: string
  year: number
  cutoff: string
  status: 'queued' | 'running' | 'completed' | 'error'
  stage: string | null
  facts: Record<string, Record<string, unknown>>
  result: LiveResult | null
  error: string | null
}

export type Notification = { id: string; field_id: string; label: string; analysis_id: string | null; level: 'hint' | 'warning'; payload: { year: number; cutoff: string }; created_at: string; read: boolean }

export class BackendError extends Error {}

async function call<T>(path: string, init?: RequestInit, timeoutMs = 15000): Promise<T> {
  const ctrl = new AbortController()
  const t = setTimeout(() => ctrl.abort(), timeoutMs)
  try {
    const res = await fetch(`${BACKEND}${path}`, { ...init, signal: init?.signal ?? ctrl.signal, headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) } })
    if (res.status === 204) return undefined as T
    const body = await res.json().catch(() => null)
    if (!res.ok) {
      const detail = body?.detail
      const msg = typeof detail === 'string' ? detail : Array.isArray(detail) ? detail.map((d: { msg: string }) => d.msg).join('; ') : `HTTP ${res.status}`
      throw new BackendError(msg)
    }
    return body as T
  } finally {
    clearTimeout(t)
  }
}

let healthCache: { at: number; ok: boolean } | null = null

/** True when the local backend answers within 1.5 s (cached for 10 s). */
export async function backendAvailable(force = false): Promise<boolean> {
  if (!force && healthCache && Date.now() - healthCache.at < 10_000) return healthCache.ok
  let ok = false
  try {
    ok = Boolean((await call<{ ok: boolean }>('/api/health', undefined, 1500))?.ok)
  } catch {
    ok = false
  }
  healthCache = { at: Date.now(), ok }
  return ok
}

export const api = {
  calibration: () => call<Calibration>('/api/calibration'),
  listFields: () => call<FieldRecord[]>('/api/fields'),
  createField: (label: string, geometry: Polygon) => call<FieldRecord>('/api/fields', { method: 'POST', body: JSON.stringify({ label, geometry }) }),
  getField: (id: string, year?: number) => call<FieldDetail>(`/api/fields/${id}${year ? `?year=${year}` : ''}`),
  deleteField: (id: string) => call<void>(`/api/fields/${id}`, { method: 'DELETE' }),
  putYields: (id: string, unit: 't/ha' | 'dt/ha', entries: { year: number; value: number }[]) =>
    call<YieldRow[]>(`/api/fields/${id}/yields`, { method: 'PUT', body: JSON.stringify({ unit, entries }) }),
  baseline: (id: string, year: number) => call<Baseline>(`/api/fields/${id}/baseline?year=${year}`),
  putAlert: (id: string, a: AlertSetting) => call<AlertSetting>(`/api/fields/${id}/alert`, { method: 'PUT', body: JSON.stringify(a) }),
  startAnalysis: (id: string, year: number, cutoff?: string) =>
    call<{ id: string }>(`/api/fields/${id}/analyses`, { method: 'POST', body: JSON.stringify({ year, cutoff }) }),
  getAnalysis: (id: string) => call<AnalysisJob>(`/api/analyses/${id}`),
  notifications: () => call<Notification[]>('/api/notifications'),
  markRead: (id: string) => call<void>(`/api/notifications/${id}/read`, { method: 'POST' }),
}
