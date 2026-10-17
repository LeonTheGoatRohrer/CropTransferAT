import type { Nullable } from '../api/types'

/** Carry the last observed value forward per cell (display only; flagged in the UI). */
export function filledSeries(series: Nullable<number>[][]): number[][] {
  const nCells = series[0]?.length ?? 0
  const out: number[][] = []
  const last = new Array<number>(nCells).fill(NaN)
  for (const row of series) {
    const r = new Array<number>(nCells)
    for (let c = 0; c < nCells; c++) {
      const v = row[c]
      if (v != null) last[c] = v
      r[c] = last[c]
    }
    out.push(r)
  }
  // back-fill leading gaps with the first observation
  for (let c = 0; c < nCells; c++) {
    const first = out.find((r) => Number.isFinite(r[c]))?.[c] ?? NaN
    for (const r of out) {
      if (!Number.isFinite(r[c])) r[c] = first
      else break
    }
  }
  return out
}

