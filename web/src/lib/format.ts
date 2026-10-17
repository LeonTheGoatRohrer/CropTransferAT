/** Locale-aware number formatting (Intl). Ranges use an en dash, negatives a true minus sign. */
import { currentLang, intlLocale } from '../i18n/lang'

const cache = new Map<string, Intl.NumberFormat>()
function nf(digits: number): Intl.NumberFormat {
  const key = `${intlLocale()}|${digits}`
  let f = cache.get(key)
  if (!f) {
    f = new Intl.NumberFormat(intlLocale(), { minimumFractionDigits: digits, maximumFractionDigits: digits, useGrouping: true })
    cache.set(key, f)
  }
  return f
}

const num = (v: number, digits: number) => nf(digits).format(Math.abs(v) < 0.5 * 10 ** -digits ? 0 : v).replace('-', '−')

export const fmt = (v: number | null | undefined, digits = 2): string => (v == null || !Number.isFinite(v) ? '–' : num(v, digits))

export const fmtSigned = (v: number | null | undefined, digits = 2): string =>
  v == null || !Number.isFinite(v) ? '–' : `${v > 0 && Math.abs(v) >= 0.5 * 10 ** -digits ? '+' : ''}${num(v, digits)}`

export const fmtPct = (v: number | null | undefined, digits = 0): string =>
  v == null || !Number.isFinite(v) ? '–' : `${num(v * 100, digits)} %`

export const fmtInt = (v: number | null | undefined): string => (v == null || !Number.isFinite(v) ? '–' : num(Math.round(v), 0))

/** Confidence interval: [lo; hi] in German (decimal comma), [lo, hi] otherwise. */
export const fmtCi = (lo: number | null | undefined, hi: number | null | undefined, digits = 2): string => {
  if (lo == null || hi == null) return ''
  const sep = currentLang() === 'en' ? ', ' : '; '
  return `[${num(lo, digits)}${sep}${num(hi, digits)}]`
}

export const fmtArea = (m2: number): string => (m2 >= 10000 ? `${num(m2 / 10000, 2)} ha` : `${fmtInt(m2)} m²`)

export const fmtDate = (iso: string | null | undefined): string => {
  if (!iso) return '–'
  const d = new Date(iso.length <= 10 ? `${iso}T00:00:00Z` : iso)
  return new Intl.DateTimeFormat(intlLocale(), { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' }).format(d)
}

/** "15.8." style cutoff label from "08-15", localised. */
export const fmtCutoff = (mmdd: string): string => {
  const [m, d] = mmdd.split('-').map(Number)
  return new Intl.DateTimeFormat(intlLocale(), { day: 'numeric', month: 'short', timeZone: 'UTC' }).format(new Date(Date.UTC(2021, m - 1, d)))
}
