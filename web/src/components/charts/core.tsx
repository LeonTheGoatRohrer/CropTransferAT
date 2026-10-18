import { useEffect, useRef, useState, type ReactNode } from 'react'
import { tokens } from '../../lib/color'

/** Width of a container, tracked with ResizeObserver (charts are always fluid). */
export function useWidth<T extends HTMLElement>(initial = 640) {
  const ref = useRef<T>(null)
  const [w, setW] = useState(initial)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const ro = new ResizeObserver(([e]) => setW(Math.max(240, Math.round(e.contentRect.width))))
    ro.observe(el)
    return () => ro.disconnect()
  }, [])
  return [ref, w] as const
}

export type Margin = { t: number; r: number; b: number; l: number }

export const axisText = {
  fill: tokens.ink3,
  fontSize: 10.5,
  fontFamily: 'var(--font-mono)',
  letterSpacing: '0.02em',
} as const

export function GridY({ ticks, y, x0, x1, fmt = (v: number) => String(v).replace('.', ',').replace('-', '−'), zero }: { ticks: number[]; y: (v: number) => number; x0: number; x1: number; fmt?: (v: number) => string; zero?: number }) {
  return (
    <g>
      {ticks.map((t) => (
        <g key={t}>
          <line x1={x0} x2={x1} y1={y(t)} y2={y(t)} stroke={t === zero ? tokens.lineStrong : tokens.line} strokeDasharray={t === zero ? undefined : '2 4'} />
          <text x={x0 - 8} y={y(t)} dy="0.32em" textAnchor="end" {...axisText}>
            {fmt(t)}
          </text>
        </g>
      ))}
    </g>
  )
}

/** Floating tooltip positioned inside a relative chart container. */
export function ChartTooltip({ x, y, width, children }: { x: number; y: number; width: number; children: ReactNode }) {
  const left = Math.min(Math.max(x + 14, 8), width - 200)
  return (
    <div
      className="panel-glass pointer-events-none absolute z-10 min-w-[150px] max-w-[220px] px-3 py-2 text-[12px] leading-snug text-ink shadow-xl"
      style={{ left, top: Math.max(0, y - 10) }}
    >
      {children}
    </div>
  )
}

export function Legend({ items, className = '' }: { items: { label: string; color: string; kind?: 'line' | 'dash' | 'band' | 'dot' | 'bar' }[]; className?: string }) {
  return (
    <div className={`flex flex-wrap items-center gap-x-5 gap-y-2 text-[12px] text-ink-2 ${className}`}>
      {items.map((it) => (
        <span key={it.label} className="inline-flex items-center gap-2">
          {it.kind === 'band' ? (
            <span className="h-2.5 w-4 rounded-[3px]" style={{ background: it.color, opacity: 0.35 }} />
          ) : it.kind === 'dot' ? (
            <span className="size-2 rounded-full" style={{ background: it.color }} />
          ) : it.kind === 'bar' ? (
            <span className="h-2.5 w-2.5 rounded-[2px]" style={{ background: it.color }} />
          ) : (
            <span className="h-0 w-4 border-t-2" style={{ borderColor: it.color, borderStyle: it.kind === 'dash' ? 'dashed' : 'solid' }} />
          )}
          {it.label}
        </span>
      ))}
    </div>
  )
}

export const niceTicks = (lo: number, hi: number, n = 4) => {
  const step = (hi - lo) / n
  return Array.from({ length: n + 1 }, (_, i) => +(lo + i * step).toFixed(6))
}
