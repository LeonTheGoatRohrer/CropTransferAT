/** Season axis: 21 dekads (10-day steps) starting 1 April, as in the project (dekad 0 = 1–10 Apr). */

import { intlLocale } from '../i18n/lang'

export const N_DEKADS = 21

const monthShort = (m: number) =>
  new Intl.DateTimeFormat(intlLocale(), { month: 'short', timeZone: 'UTC' }).format(new Date(Date.UTC(2021, m, 1))).replace('.', '')

export function dekadDate(i: number, year = 2021): Date {
  const d = new Date(Date.UTC(year, 3, 1))
  d.setUTCDate(d.getUTCDate() + 10 * i)
  return d
}

export const dekadLabel = (i: number, year?: number) =>
  new Intl.DateTimeFormat(intlLocale(), { day: 'numeric', month: 'short', timeZone: 'UTC' }).format(dekadDate(i, year))

/** Fractional dekad position of the first day of each month in the season, for axis ticks. */
const TICK_POS = [0, 3.0, 6.1, 9.1, 12.2, 15.3, 18.3]
export const monthTicks = (): { pos: number; label: string }[] => TICK_POS.map((pos, i) => ({ pos, label: monthShort(3 + i) }))

/** Dekads that make up the phases used by the project's alarm explanation. */
export const PHASES = [
  { key: 'Jun', month: 5, from: 6.1, to: 9.1 },
  { key: 'Jul', month: 6, from: 9.1, to: 12.2 },
  { key: 'Aug', month: 7, from: 12.2, to: 15.3 },
] as const

export const monthLong = (m: number) =>
  new Intl.DateTimeFormat(intlLocale(), { month: 'long', timeZone: 'UTC' }).format(new Date(Date.UTC(2021, m, 1)))

/** Last complete dekad before a cutoff date (mirrors croptransfer.stress.last_complete_dekad). */
export function lastCompleteDekad(month: number, day: number): number {
  const c = Date.UTC(2001, month - 1, day)
  const s = Date.UTC(2001, 3, 1)
  return Math.floor((c - s) / 86400000 / 10) - 1
}

export const cumulative = (xs: (number | null)[]) => {
  let acc = 0
  return xs.map((x) => (x == null ? null : (acc += x)))
}

/** Localised month name for the English phase names stored in the data ("June", "July", "August"). */
export const phaseName = (p: string | null | undefined): string => {
  const idx = { June: 5, July: 6, August: 7, Jun: 5, Jul: 6, Aug: 7 }[p ?? ''] as number | undefined
  return idx == null ? (p ?? '–') : monthLong(idx)
}
