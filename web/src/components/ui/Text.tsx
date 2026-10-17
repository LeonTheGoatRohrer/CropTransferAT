import type { ReactNode } from 'react'

/** Keep Greek letters lower-case inside upper-cased labels (ρ would otherwise render like a Latin P). */
export function keepGreek(text: string): ReactNode {
  const parts = text.split(/([ρσα])/)
  return parts.map((p, i) => (/^[ρσα]$/.test(p) ? <span key={i} className="normal-case">{p}</span> : p))
}
