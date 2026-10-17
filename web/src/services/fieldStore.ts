/**
 * Field store for the concept tool: the local backend when it runs, otherwise the browser (localStorage).
 * Fields are pseudonymous in both cases. Path B (frozen model) is only available with the backend.
 */
import type { Polygon } from '../api/types'
import { baseline, toTHa, type Unit } from '../lib/baseline'
import { areaM2 } from '../lib/geo'
import { api, backendAvailable, type AlertSetting, type FieldDetail, type FieldRecord, type YieldRow } from './backendService'

const KEY = 'ct-concept-fields-v1'

type LocalField = FieldRecord & { yields: YieldRow[]; alert: AlertSetting | null }

function readLocal(): LocalField[] {
  try {
    return JSON.parse(localStorage.getItem(KEY) ?? '[]') as LocalField[]
  } catch {
    return []
  }
}

function writeLocal(f: LocalField[]) {
  try {
    localStorage.setItem(KEY, JSON.stringify(f))
  } catch {
    /* storage unavailable: data stays in memory for this session */
  }
}

export type FieldStore = {
  mode: 'backend' | 'local'
  list(): Promise<FieldRecord[]>
  create(label: string, geometry: Polygon): Promise<FieldRecord>
  get(id: string, year: number): Promise<FieldDetail>
  remove(id: string): Promise<void>
  setYields(id: string, unit: Unit, entries: { year: number; value: number }[]): Promise<void>
  setAlert(id: string, a: AlertSetting): Promise<void>
}

const backendStore: FieldStore = {
  mode: 'backend',
  list: () => api.listFields(),
  create: (label, geometry) => api.createField(label, geometry),
  get: (id, year) => api.getField(id, year),
  remove: (id) => api.deleteField(id),
  setYields: async (id, unit, entries) => {
    await api.putYields(id, unit, entries)
  },
  setAlert: async (id, a) => {
    await api.putAlert(id, a)
  },
}

const localStore: FieldStore = {
  mode: 'local',
  list: async () => readLocal().map(({ yields, alert: _a, ...f }) => ({ ...f, n_yields: yields.length })),
  create: async (label, geometry) => {
    const f: LocalField = { id: Math.random().toString(16).slice(2, 12), label, crop: 'maize', geometry, area_m2: areaM2(geometry), created_at: new Date().toISOString(), yields: [], alert: null }
    writeLocal([...readLocal(), f])
    return f
  },
  get: async (id, year) => {
    const f = readLocal().find((x) => x.id === id)
    if (!f) throw new Error('not found')
    const ys = Object.fromEntries(f.yields.map((y) => [y.year, y.t_ha]))
    return { ...f, baseline: baseline(ys, year, f.alert?.hint_pct, f.alert?.warn_pct) }
  },
  remove: async (id) => writeLocal(readLocal().filter((x) => x.id !== id)),
  setYields: async (id, unit, entries) => {
    const seen = new Set<number>()
    const rows = entries.map((e) => {
      if (seen.has(e.year)) throw new Error(`${e.year} ×2`)
      seen.add(e.year)
      return { year: e.year, t_ha: toTHa(e.value, unit), unit, value: e.value }
    })
    writeLocal(readLocal().map((f) => (f.id === id ? { ...f, yields: rows.sort((a, b) => a.year - b.year) } : f)))
  },
  setAlert: async (id, a) => writeLocal(readLocal().map((f) => (f.id === id ? { ...f, alert: a } : f))),
}

export async function getFieldStore(): Promise<FieldStore> {
  return (await backendAvailable(true)) ? backendStore : localStore
}
