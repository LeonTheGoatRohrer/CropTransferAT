/** Season axis: 21 dekads (10-day steps) starting 1 April, as in the project (dekad 0 = 1–10 Apr). */

export const N_DEKADS = 21
const MONTHS = ['Jän', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']

export function dekadDate(i: number, year = 2021): Date {
  const d = new Date(Date.UTC(year, 3, 1))
  d.setUTCDate(d.getUTCDate() + 10 * i)
  return d
}

export const dekadLabel = (i: number, year?: number) => {
  const d = dekadDate(i, year)
  return `${d.getUTCDate()}. ${MONTHS[d.getUTCMonth()]}`
}

/** Fractional dekad position of the first day of each month in the season, for axis ticks. */
export const MONTH_TICKS: { pos: number; label: string }[] = [
  { pos: 0, label: 'Apr' },
  { pos: 3.0, label: 'Mai' },
  { pos: 6.1, label: 'Jun' },
  { pos: 9.1, label: 'Jul' },
  { pos: 12.2, label: 'Aug' },
  { pos: 15.3, label: 'Sep' },
  { pos: 18.3, label: 'Okt' },
]

/** Dekads that make up the phases used by the project's alarm explanation. */
export const PHASES = [
  { key: 'Jun', label: 'Juni', from: 6.1, to: 9.1 },
  { key: 'Jul', label: 'Juli', from: 9.1, to: 12.2 },
  { key: 'Aug', label: 'August', from: 12.2, to: 15.3 },
] as const

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
