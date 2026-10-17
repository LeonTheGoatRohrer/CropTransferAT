import { scaleLinear } from 'd3-scale'
import { area, curveMonotoneX, line } from 'd3-shape'
import { motion, useReducedMotion } from 'motion/react'
import { useState } from 'react'
import type { Nullable, ReferenceBand } from '../../api/types'
import { tokens } from '../../lib/color'
import { MONTH_TICKS, N_DEKADS, PHASES, dekadLabel } from '../../lib/dekads'
import { fmt, fmtSigned } from '../../lib/format'
import { ChartTooltip, GridY, axisText, useWidth } from './core'

type Props = {
  values: Nullable<number>[]
  reference?: ReferenceBand
  year?: number
  height?: number
  yDomain?: [number, number]
  label?: string
  color?: string
  /** dekad index of a cutoff marker (e.g. 1 Sep) */
  cutoff?: number
  showPhases?: boolean
  showShortfall?: boolean
  /** highlight one dekad (season scrubber) */
  activeDekad?: number
  compact?: boolean
}

type Pt = { i: number; v: number }

/** Season curve of one field against the healthy reference band, on the shared 21-dekad axis. */
export function SeasonChart({
  values,
  reference,
  year,
  height = 300,
  yDomain = [0, 1],
  label = 'NDVI',
  color = tokens.maize,
  cutoff,
  showPhases = true,
  showShortfall = true,
  activeDekad,
  compact = false,
}: Props) {
  const [ref, width] = useWidth<HTMLDivElement>()
  const [hover, setHover] = useState<number | null>(null)
  const reduce = useReducedMotion()
  const m = compact ? { t: 10, r: 10, b: 24, l: 34 } : { t: 18, r: 16, b: 30, l: 42 }
  const x = scaleLinear().domain([0, N_DEKADS - 1]).range([m.l, width - m.r])
  const y = scaleLinear().domain(yDomain).range([height - m.b, m.t])

  const pts: Pt[] = values.flatMap((v, i) => (v == null ? [] : [{ i, v }]))
  const refPts = reference
    ? reference.median.flatMap((v, i) => (v == null ? [] : [{ i, v, lo: reference.p25[i] ?? v, hi: reference.p75[i] ?? v }]))
    : []

  const lineGen = line<Pt>().x((d) => x(d.i)).y((d) => y(d.v)).curve(curveMonotoneX)
  const bandGen = area<{ i: number; lo: number; hi: number }>().x((d) => x(d.i)).y0((d) => y(d.lo)).y1((d) => y(d.hi)).curve(curveMonotoneX)

  // Shortfall: observed dekads (from 1 June, dekad 6) where the field is below the reference median.
  const shortfall = showShortfall && reference
    ? pts.filter((p) => p.i >= 6 && reference.median[p.i] != null && p.v < (reference.median[p.i] as number))
    : []

  const ticks = y.ticks(compact ? 3 : 5)
  const hv = hover != null ? values[hover] : null
  const hr = hover != null && reference ? reference.median[hover] : null

  return (
    <div ref={ref} className="relative w-full select-none">
      <svg
        width={width}
        height={height}
        role="img"
        aria-label={`${label} season curve against the healthy reference`}
        onMouseLeave={() => setHover(null)}
        onMouseMove={(e) => {
          const r = (e.currentTarget as SVGSVGElement).getBoundingClientRect()
          const i = Math.round(x.invert(e.clientX - r.left))
          setHover(i >= 0 && i < N_DEKADS ? i : null)
        }}
      >
        {showPhases &&
          PHASES.map((p) => (
            <g key={p.key}>
              <rect x={x(p.from)} y={m.t} width={x(p.to) - x(p.from)} height={height - m.t - m.b} fill="white" opacity={p.key === 'Jul' ? 0.035 : 0.018} />
              {!compact && (
                <text x={(x(p.from) + x(p.to)) / 2} y={m.t + 12} textAnchor="middle" {...axisText} fill={tokens.ink4}>
                  {p.label}
                </text>
              )}
            </g>
          ))}
        <GridY ticks={ticks} y={y} x0={m.l} x1={width - m.r} fmt={(v) => (Math.abs(v) < 1e-9 ? '0' : v.toFixed(1))} />
        {MONTH_TICKS.filter((t) => t.pos <= N_DEKADS - 1).map((t) => (
          <text key={t.label} x={x(t.pos)} y={height - m.b + 18} textAnchor="start" {...axisText}>
            {t.label}
          </text>
        ))}

        {refPts.length > 1 && (
          <>
            <path d={bandGen(refPts) ?? ''} fill={tokens.sage} opacity={0.16} />
            <path d={lineGen(refPts) ?? ''} fill="none" stroke={tokens.sage} strokeWidth={1.4} strokeDasharray="4 4" opacity={0.85} />
          </>
        )}

        {shortfall.map((p) => (
          <line key={p.i} x1={x(p.i)} x2={x(p.i)} y1={y(p.v)} y2={y(reference!.median[p.i] as number)} stroke={tokens.rust} strokeWidth={compact ? 3 : 5} strokeLinecap="round" opacity={0.55} />
        ))}

        {cutoff != null && (
          <g>
            <line x1={x(cutoff)} x2={x(cutoff)} y1={m.t} y2={height - m.b} stroke={tokens.ink3} strokeDasharray="3 3" />
            {!compact && (
              <text x={x(cutoff) + 6} y={height - m.b - 8} {...axisText} fill={tokens.ink2}>
                1 Sep cutoff
              </text>
            )}
          </g>
        )}

        {pts.length > 1 && (
          <motion.path
            key={values.join(',')}
            d={lineGen(pts) ?? ''}
            fill="none"
            stroke={color}
            strokeWidth={2.2}
            initial={reduce ? false : { pathLength: 0, opacity: 0.4 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
          />
        )}
        {pts.map((p) => (
          <circle key={p.i} cx={x(p.i)} cy={y(p.v)} r={hover === p.i || activeDekad === p.i ? 5 : compact ? 2.4 : 3.2} fill={tokens.soil800} stroke={color} strokeWidth={1.8} />
        ))}

        {activeDekad != null && <line x1={x(activeDekad)} x2={x(activeDekad)} y1={m.t} y2={height - m.b} stroke={tokens.maize} opacity={0.5} />}
        {hover != null && <line x1={x(hover)} x2={x(hover)} y1={m.t} y2={height - m.b} stroke={tokens.ink3} opacity={0.6} />}
      </svg>
      {hover != null && !compact && (
        <ChartTooltip x={x(hover)} y={y(hv ?? hr ?? yDomain[1])} width={width}>
          <p className="eyebrow mb-1 !text-[10px]">{dekadLabel(hover, year)}</p>
          <p className="flex justify-between gap-4">
            <span className="text-ink-2">{label}</span>
            <span className="font-mono tabular">{hv == null ? 'no clear scene' : fmt(hv, 3)}</span>
          </p>
          {hr != null && (
            <p className="flex justify-between gap-4">
              <span className="text-ink-2">Healthy median</span>
              <span className="font-mono tabular">{fmt(hr, 3)}</span>
            </p>
          )}
          {hv != null && hr != null && (
            <p className="flex justify-between gap-4">
              <span className="text-ink-2">Deviation</span>
              <span className={`font-mono tabular ${hv < hr ? 'text-rust' : 'text-sage'}`}>{fmtSigned(hv - hr, 3)}</span>
            </p>
          )}
        </ChartTooltip>
      )}
    </div>
  )
}
