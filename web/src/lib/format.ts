/** Number formatting used across the site (German UI: decimal comma, de-AT grouping, en dash for ranges). */

/** toFixed with a decimal comma (no minus replacement; for axis ticks and plain numbers). */
export const fmtNum = (v: number, digits = 0): string => v.toFixed(digits).replace('.', ',')

export const fmt = (v: number | null | undefined, digits = 2): string =>
  v == null || !Number.isFinite(v) ? '–' : fmtNum(v, digits).replace('-', '−')

export const fmtSigned = (v: number | null | undefined, digits = 2): string =>
  v == null || !Number.isFinite(v) ? '–' : `${v > 0 ? '+' : v < 0 ? '−' : ''}${fmtNum(Math.abs(v), digits)}`

export const fmtPct = (v: number | null | undefined, digits = 0): string =>
  v == null || !Number.isFinite(v) ? '–' : `${fmtNum(v * 100, digits)} %`

export const fmtInt = (v: number | null | undefined): string =>
  v == null || !Number.isFinite(v) ? '–' : Math.round(v).toLocaleString('de-AT')

/** CI bounds; semicolon separator because the comma is the decimal mark. */
export const fmtCi = (lo: number | null | undefined, hi: number | null | undefined, digits = 2): string =>
  lo == null || hi == null ? '' : `[${fmtSigned0(lo, digits)}; ${fmtSigned0(hi, digits)}]`

/** Minus sign for negatives only (CI bounds). */
const fmtSigned0 = (v: number, digits: number) => (v < 0 ? `−${fmtNum(Math.abs(v), digits)}` : fmtNum(v, digits))

export const fmtArea = (m2: number): string =>
  m2 >= 10000 ? `${fmtNum(m2 / 10000, 2)} ha` : `${fmtInt(m2)} m²`

export const minus = (s: string) => s.replace(/-/g, '−')
