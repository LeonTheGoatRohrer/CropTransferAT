import type { Polygon } from '../api/types'

export type YearYield = { year: number; tPerHa: number }

export type Contribution = {
  id: string
  createdAt: string
  polygon: Polygon
  areaM2: number
  fieldName: string
  cropType: 'grain' | 'silage'
  irrigated: boolean
  /** Completed harvests of earlier years. */
  pastYields: YearYield[]
  /** The current season: harvested value, or the farmer's estimate so far. */
  thisYear: { year: number; tPerHa: number; status: 'harvested' | 'estimate' } | null
}

const KEY = 'croptransfer.contributions.v1'

export function listContributions(): Contribution[] {
  try {
    return JSON.parse(localStorage.getItem(KEY) ?? '[]') as Contribution[]
  } catch {
    return []
  }
}

/**
 * Store a contribution on the project server (python -m croptransfer.contrib_server).
 * If the server cannot be reached, the entry is kept in this browser and can be exported.
 */
export async function submitContribution(c: Omit<Contribution, 'id' | 'createdAt'>): Promise<{ contribution: Contribution; saved: 'server' | 'browser' }> {
  let res: Response | null = null
  try {
    res = await fetch('/api/contributions', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...c, consent: true }) })
  } catch {
    res = null // server not running: keep the entry in this browser
  }
  if (res?.ok) {
    const { id, createdAt } = (await res.json()) as { id: string; createdAt: string }
    return { contribution: { ...c, id, createdAt }, saved: 'server' }
  }
  if (res && res.status >= 400 && res.status < 500) {
    const { error } = (await res.json().catch(() => ({ error: '' }))) as { error?: string }
    throw new Error(error || 'The server rejected this entry.')
  }
  const full: Contribution = { ...c, id: crypto.randomUUID(), createdAt: new Date().toISOString() }
  try {
    localStorage.setItem(KEY, JSON.stringify([...listContributions(), full]))
  } catch {
    /* storage unavailable: the export still works for this session only */
  }
  return { contribution: full, saved: 'browser' }
}

export function downloadContributions(rows: Contribution[]) {
  const blob = new Blob([JSON.stringify(rows, null, 2)], { type: 'application/json' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = 'croptransfer-contributions.json'
  a.click()
  URL.revokeObjectURL(a.href)
}

export type YieldVerdict = { normal: number; n: number; ratio: number; label: 'below' | 'normal' | 'above' }

/** This season against the field's own average of earlier years — the same "relative yield" the models predict. */
export function judgeYield(past: YearYield[], current: number | null): YieldVerdict | null {
  if (past.length < 2 || current == null) return null
  const normal = past.reduce((s, y) => s + y.tPerHa, 0) / past.length
  const ratio = current / normal
  return { normal, n: past.length, ratio, label: ratio < 0.85 ? 'below' : ratio > 1.1 ? 'above' : 'normal' }
}
