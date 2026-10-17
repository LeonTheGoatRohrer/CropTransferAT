/** Number formatting used across the site (English UI, en dash for ranges). */

export const fmt = (v: number | null | undefined, digits = 2): string =>
  v == null || !Number.isFinite(v) ? '–' : v.toFixed(digits).replace('-', '−')

export const fmtSigned = (v: number | null | undefined, digits = 2): string =>
  v == null || !Number.isFinite(v) ? '–' : `${v > 0 ? '+' : v < 0 ? '−' : ''}${Math.abs(v).toFixed(digits)}`

export const fmtPct = (v: number | null | undefined, digits = 0): string =>
  v == null || !Number.isFinite(v) ? '–' : `${(v * 100).toFixed(digits)} %`

export const fmtInt = (v: number | null | undefined): string =>
  v == null || !Number.isFinite(v) ? '–' : Math.round(v).toLocaleString('en-US')

export const fmtCi = (lo: number | null | undefined, hi: number | null | undefined, digits = 2): string =>
  lo == null || hi == null ? '' : `[${fmtSigned0(lo, digits)}, ${fmtSigned0(hi, digits)}]`

/** Minus sign for negatives only (CI bounds). */
const fmtSigned0 = (v: number, digits: number) => (v < 0 ? `−${Math.abs(v).toFixed(digits)}` : v.toFixed(digits))

export const fmtArea = (m2: number): string =>
  m2 >= 10000 ? `${(m2 / 10000).toFixed(2)} ha` : `${fmtInt(m2)} m²`

export const minus = (s: string) => s.replace(/-/g, '−')
