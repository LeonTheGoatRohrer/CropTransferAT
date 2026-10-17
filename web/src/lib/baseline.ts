/**
 * Path A in the browser — mirrors src/croptransfer/fielddb.py (baseline, history_level, to_t_ha) so the tool
 * also works without the local backend. Keep both in sync; tests live in tests/test_fielddb.py.
 */
import type { Baseline } from '../services/backendService'

export const MAX_T_HA = 25
export const UNIT_FACTOR = { 't/ha': 1, 'dt/ha': 0.1 } as const
export type Unit = keyof typeof UNIT_FACTOR

export const historyLevel = (nOther: number): Baseline['history'] => (nOther < 3 ? 'too_little' : nOther < 5 ? 'with_hint' : 'ok')

export function toTHa(value: number, unit: Unit): number {
  const v = value * UNIT_FACTOR[unit]
  if (!(v > 0 && v <= MAX_T_HA)) throw new Error(`0 < Y ≤ ${MAX_T_HA} t/ha (${value} ${unit})`)
  return v
}

const r3 = (v: number) => Math.round(v * 1000) / 1000

export function baseline(yields: Record<number, number>, year: number, hintPct?: number, warnPct?: number): Baseline {
  const entries = Object.entries(yields).map(([y, v]) => [Number(y), v] as const)
  const others = entries.filter(([y]) => y !== year)
  const nOther = others.length
  const level = historyLevel(nOther)
  const normal = nOther ? others.reduce((a, [, v]) => a + v, 0) / nOther : null
  const yNow = yields[year] ?? null
  const ry = yNow != null && normal ? yNow / normal : null
  const perYear = entries
    .sort((a, b) => a[0] - b[0])
    .map(([y, v]) => {
      const o = entries.filter(([z]) => z !== y).map(([, w]) => w)
      const n = o.length ? o.reduce((a, b) => a + b, 0) / o.length : null
      return { year: y, t_ha: r3(v), normal_others: n == null ? null : r3(n), ry: n ? r3(v / n) : null, n_other: o.length }
    })
  const out: Baseline = {
    year,
    n_other_years: nOther,
    history: level,
    normal_t_ha: normal == null ? null : r3(normal),
    yield_t_ha: yNow == null ? null : r3(yNow),
    ry: ry == null || level === 'too_little' ? null : r3(ry),
    per_year: perYear,
    state: level === 'too_little' ? 'no_assessment' : ry == null ? 'pending' : 'ok',
  }
  if (normal != null && level !== 'too_little') {
    if (hintPct != null) out.hint_below_t_ha = r3(normal * (1 - hintPct / 100))
    if (warnPct != null) out.warning_below_t_ha = r3(normal * (1 - warnPct / 100))
    if (ry != null) out.state = warnPct != null && ry < 1 - warnPct / 100 ? 'warning' : hintPct != null && ry < 1 - hintPct / 100 ? 'hint' : 'normal'
  }
  return out
}
