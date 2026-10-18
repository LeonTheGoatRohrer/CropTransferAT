import { extent, max } from 'd3-array'
import { scaleBand, scaleLinear } from 'd3-scale'
import { area, curveMonotoneX, line } from 'd3-shape'
import { motion, useReducedMotion } from 'motion/react'
import { useState, type ReactNode } from 'react'
import { tokens } from '../../lib/color'
import { fmt, fmtSigned } from '../../lib/format'
import { ChartTooltip, GridY, axisText, niceTicks, useWidth } from './core'

/* ------------------------------------------------------------------ */
/* Dot + confidence interval rows (forest plot)                        */
/* ------------------------------------------------------------------ */

export type CiRow = { label: string; sub?: string; value: number; lo?: number | null; hi?: number | null; color?: string; emphasis?: boolean; note?: string }

export function CiRows({ rows, domain, reference, referenceLabel, format = (v: number) => fmt(v, 2), signed = false, height }: { rows: CiRow[]; domain: [number, number]; reference?: number; referenceLabel?: string; format?: (v: number) => string; signed?: boolean; height?: number }) {
  const [ref, width] = useWidth<HTMLDivElement>()
  const reduce = useReducedMotion()
  const labelW = Math.min(230, width * 0.42)
  const rowH = 46
  const h = height ?? rows.length * rowH + 34
  const x = scaleLinear().domain(domain).range([labelW + 8, width - 64])
  const ticks = x.ticks(width < 520 ? 4 : 6)
  const f = signed ? (v: number) => fmtSigned(v, 2) : format
  return (
    <div ref={ref} className="w-full">
      <svg width={width} height={h} role="img" aria-label="Schätzwerte mit 95-%-Konfidenzintervallen">
        {ticks.map((t) => (
          <g key={t}>
            <line x1={x(t)} x2={x(t)} y1={6} y2={h - 24} stroke={tokens.line} strokeDasharray="2 4" />
            <text x={x(t)} y={h - 8} textAnchor="middle" {...axisText}>{f(t)}</text>
          </g>
        ))}
        {reference != null && (
          <g>
            <line x1={x(reference)} x2={x(reference)} y1={0} y2={h - 24} stroke={tokens.ink3} strokeWidth={1.2} />
            {referenceLabel && <text x={x(reference) + 5} y={10} {...axisText} fill={tokens.ink2}>{referenceLabel}</text>}
          </g>
        )}
        {rows.map((r, i) => {
          const cy = 18 + i * rowH + rowH / 2 - 6
          const c = r.color ?? (r.emphasis ? tokens.maize : tokens.ink2)
          return (
            <g key={r.label + i}>
              <text x={0} y={cy - (r.sub ? 5 : 0)} dy="0.32em" fill={r.emphasis ? tokens.ink : tokens.ink2} fontSize={13} fontWeight={r.emphasis ? 600 : 450}>{r.label}</text>
              {r.sub && <text x={0} y={cy + 11} dy="0.32em" {...axisText} fill={tokens.ink4}>{r.sub}</text>}
              {r.lo != null && r.hi != null && (
                <motion.line
                  x1={x(r.lo)} x2={x(r.hi)} y1={cy} y2={cy} stroke={c} strokeWidth={2} strokeLinecap="round" opacity={0.55}
                  initial={reduce ? false : { pathLength: 0 }} whileInView={{ pathLength: 1 }} viewport={{ once: true }} transition={{ duration: 0.8, delay: i * 0.06 }}
                />
              )}
              <motion.circle
                cx={x(r.value)} cy={cy} r={r.emphasis ? 6.5 : 5} fill={r.emphasis ? c : tokens.soil800} stroke={c} strokeWidth={2}
                initial={reduce ? false : { scale: 0 }} whileInView={{ scale: 1 }} viewport={{ once: true }} transition={{ duration: 0.4, delay: 0.2 + i * 0.06 }}
              />
              <text x={width - 58} y={cy} dy="0.32em" fontFamily="var(--font-mono)" fontSize={12} fill={r.emphasis ? tokens.ink : tokens.ink2}>{f(r.value)}</text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}

/* ------------------------------------------------------------------ */
/* Scatter                                                             */
/* ------------------------------------------------------------------ */

export type ScatterPoint = { x: number; y: number; color?: string; r?: number; label?: ReactNode; ring?: boolean }

export function Scatter({ points, xLabel, yLabel, xDomain, yDomain, diagonal = false, height = 340, hLines = [], vLines = [], xFmt = (v: number) => fmt(v, 1), yFmt = (v: number) => fmt(v, 1), opacity = 0.8 }: { points: ScatterPoint[]; xLabel: string; yLabel: string; xDomain?: [number, number]; yDomain?: [number, number]; diagonal?: boolean; height?: number; hLines?: { v: number; label?: string; color?: string }[]; vLines?: { v: number; label?: string; color?: string }[]; xFmt?: (v: number) => string; yFmt?: (v: number) => string; opacity?: number }) {
  const [ref, width] = useWidth<HTMLDivElement>()
  const [hover, setHover] = useState<number | null>(null)
  const m = { t: 14, r: 14, b: 42, l: 50 }
  const xd = xDomain ?? (extent(points, (p) => p.x) as [number, number])
  const yd = yDomain ?? (extent(points, (p) => p.y) as [number, number])
  const x = scaleLinear().domain(xd).range([m.l, width - m.r])
  const y = scaleLinear().domain(yd).range([height - m.b, m.t])
  const hp = hover != null ? points[hover] : null
  return (
    <div ref={ref} className="relative w-full select-none">
      <svg width={width} height={height} role="img" aria-label={`${yLabel} gegen ${xLabel}`} onMouseLeave={() => setHover(null)}>
        <GridY ticks={y.ticks(5)} y={y} x0={m.l} x1={width - m.r} fmt={yFmt} />
        {x.ticks(width < 420 ? 4 : 6).map((t) => (
          <text key={t} x={x(t)} y={height - m.b + 16} textAnchor="middle" {...axisText}>{xFmt(t)}</text>
        ))}
        <text x={(m.l + width - m.r) / 2} y={height - 6} textAnchor="middle" {...axisText} fill={tokens.ink2}>{xLabel}</text>
        <text transform={`translate(12 ${(m.t + height - m.b) / 2}) rotate(-90)`} textAnchor="middle" {...axisText} fill={tokens.ink2}>{yLabel}</text>
        {diagonal && <line x1={x(Math.max(xd[0], yd[0]))} y1={y(Math.max(xd[0], yd[0]))} x2={x(Math.min(xd[1], yd[1]))} y2={y(Math.min(xd[1], yd[1]))} stroke={tokens.ink3} strokeDasharray="4 4" />}
        {hLines.map((l) => (
          <g key={`h${l.v}`}>
            <line x1={m.l} x2={width - m.r} y1={y(l.v)} y2={y(l.v)} stroke={l.color ?? tokens.ink3} strokeDasharray="3 3" />
            {l.label && <text x={m.l + 6} y={y(l.v) - 6} {...axisText} fill={l.color ?? tokens.ink2}>{l.label}</text>}
          </g>
        ))}
        {vLines.map((l) => (
          <g key={`v${l.v}`}>
            <line x1={x(l.v)} x2={x(l.v)} y1={m.t} y2={height - m.b} stroke={l.color ?? tokens.ink3} strokeDasharray="3 3" />
            {l.label && <text x={x(l.v) + 5} y={m.t + 10} {...axisText} fill={l.color ?? tokens.ink2}>{l.label}</text>}
          </g>
        ))}
        {points.map((p, i) => (
          <circle
            key={i}
            cx={x(Math.min(Math.max(p.x, xd[0]), xd[1]))}
            cy={y(Math.min(Math.max(p.y, yd[0]), yd[1]))}
            r={(p.r ?? 3.2) + (hover === i ? 2 : 0)}
            fill={p.ring ? 'transparent' : (p.color ?? tokens.maize)}
            stroke={p.ring ? (p.color ?? tokens.maize) : 'none'}
            strokeWidth={1.6}
            opacity={hover == null || hover === i ? opacity : opacity * 0.5}
            onMouseEnter={() => p.label && setHover(i)}
          />
        ))}
      </svg>
      {hp && hover != null && (
        <ChartTooltip x={x(hp.x)} y={y(hp.y)} width={width}>{hp.label}</ChartTooltip>
      )}
    </div>
  )
}

/* ------------------------------------------------------------------ */
/* Overlaid histograms                                                 */
/* ------------------------------------------------------------------ */

export function Histogram({ edges, series, height = 220, xLabel }: { edges: number[]; series: { label: string; counts: number[]; color: string }[]; height?: number; xLabel: string }) {
  const [ref, width] = useWidth<HTMLDivElement>()
  const m = { t: 10, r: 12, b: 40, l: 12 }
  const x = scaleLinear().domain([edges[0], edges[edges.length - 1]]).range([m.l, width - m.r])
  const ymax = max(series.flatMap((s) => s.counts)) ?? 1
  const y = scaleLinear().domain([0, ymax]).range([height - m.b, m.t])
  const pts = (c: number[]) => c.map((v, i) => ({ x: (edges[i] + edges[i + 1]) / 2, v }))
  const ag = area<{ x: number; v: number }>().x((d) => x(d.x)).y0(height - m.b).y1((d) => y(d.v)).curve(curveMonotoneX)
  const lg = line<{ x: number; v: number }>().x((d) => x(d.x)).y((d) => y(d.v)).curve(curveMonotoneX)
  return (
    <div ref={ref} className="w-full">
      <svg width={width} height={height} role="img" aria-label={`Verteilung: ${xLabel}`}>
        <line x1={x(0)} x2={x(0)} y1={m.t} y2={height - m.b} stroke={tokens.ink3} />
        {series.map((s) => (
          <g key={s.label}>
            <path d={ag(pts(s.counts)) ?? ''} fill={s.color} opacity={0.14} />
            <path d={lg(pts(s.counts)) ?? ''} fill="none" stroke={s.color} strokeWidth={1.8} />
          </g>
        ))}
        {niceTicks(edges[0], edges[edges.length - 1], 4).map((t) => (
          <text key={t} x={x(t)} y={height - m.b + 16} textAnchor="middle" {...axisText}>{fmtSigned(t, 1)}</text>
        ))}
        <text x={width / 2} y={height - 6} textAnchor="middle" {...axisText} fill={tokens.ink2}>{xLabel}</text>
      </svg>
    </div>
  )
}

/* ------------------------------------------------------------------ */
/* Lines with CI bands over an ordinal x axis (e.g. forecast cutoffs)  */
/* ------------------------------------------------------------------ */

export type LineSeries = { label: string; color: string; values: { v: number | null; lo?: number | null; hi?: number | null }[]; dashed?: boolean }

export function LineCi({ categories, series, yDomain, height = 280, yFmt = (v: number) => fmt(v, 2), hLines = [] }: { categories: string[]; series: LineSeries[]; yDomain: [number, number]; height?: number; yFmt?: (v: number) => string; hLines?: { v: number; label: string; color?: string }[] }) {
  const [ref, width] = useWidth<HTMLDivElement>()
  const [hover, setHover] = useState<number | null>(null)
  const reduce = useReducedMotion()
  const m = { t: 16, r: 18, b: 30, l: 46 }
  const x = scaleLinear().domain([0, categories.length - 1]).range([m.l + 8, width - m.r - 8])
  const y = scaleLinear().domain(yDomain).range([height - m.b, m.t])
  type Pt = { i: number; v: number; lo: number; hi: number }
  const toPts = (s: LineSeries): Pt[] => s.values.flatMap((d, i) => (d.v == null ? [] : [{ i, v: d.v, lo: d.lo ?? d.v, hi: d.hi ?? d.v }]))
  const lg = line<Pt>().x((d) => x(d.i)).y((d) => y(d.v)).curve(curveMonotoneX)
  const ag = area<Pt>().x((d) => x(d.i)).y0((d) => y(d.lo)).y1((d) => y(d.hi)).curve(curveMonotoneX)
  return (
    <div ref={ref} className="relative w-full select-none">
      <svg
        width={width}
        height={height}
        role="img"
        aria-label="Metrik nach Prognosestichtag mit Konfidenzbändern"
        onMouseLeave={() => setHover(null)}
        onMouseMove={(e) => {
          const r = (e.currentTarget as SVGSVGElement).getBoundingClientRect()
          const i = Math.round(x.invert(e.clientX - r.left))
          setHover(i >= 0 && i < categories.length ? i : null)
        }}
      >
        <GridY ticks={y.ticks(5)} y={y} x0={m.l} x1={width - m.r} fmt={yFmt} zero={0} />
        {categories.map((c, i) => (
          <text key={c} x={x(i)} y={height - m.b + 18} textAnchor="middle" {...axisText} fill={hover === i ? tokens.ink : tokens.ink3}>{c}</text>
        ))}
        {hLines.map((l) => (
          <g key={l.label}>
            <line x1={m.l} x2={width - m.r} y1={y(l.v)} y2={y(l.v)} stroke={l.color ?? tokens.ink3} strokeDasharray="4 4" />
            <text x={width - m.r} y={y(l.v) - 6} textAnchor="end" {...axisText} fill={l.color ?? tokens.ink2}>{l.label}</text>
          </g>
        ))}
        {series.map((s) => {
          const p = toPts(s)
          return (
            <g key={s.label}>
              <path d={ag(p) ?? ''} fill={s.color} opacity={0.13} />
              <motion.path
                d={lg(p) ?? ''} fill="none" stroke={s.color} strokeWidth={2.2} strokeDasharray={s.dashed ? '5 4' : undefined}
                initial={reduce ? false : { pathLength: 0 }} whileInView={{ pathLength: 1 }} viewport={{ once: true }} transition={{ duration: 1.1, ease: [0.22, 1, 0.36, 1] }}
              />
              {p.map((d) => <circle key={d.i} cx={x(d.i)} cy={y(d.v)} r={hover === d.i ? 4.5 : 3} fill={tokens.soil800} stroke={s.color} strokeWidth={1.8} />)}
            </g>
          )
        })}
        {hover != null && <line x1={x(hover)} x2={x(hover)} y1={m.t} y2={height - m.b} stroke={tokens.ink3} opacity={0.5} />}
      </svg>
      {hover != null && (
        <ChartTooltip x={x(hover)} y={m.t + 10} width={width}>
          <p className="eyebrow mb-1 !text-[10px]">{categories[hover]}</p>
          {series.map((s) => {
            const d = s.values[hover]
            return (
              <p key={s.label} className="flex justify-between gap-3">
                <span className="text-ink-2" style={{ color: s.color }}>{s.label}</span>
                <span className="font-mono tabular">{d?.v == null ? '–' : yFmt(d.v)}</span>
              </p>
            )
          })}
        </ChartTooltip>
      )}
    </div>
  )
}

/* ------------------------------------------------------------------ */
/* Strip plot: one dot per unit, grouped                               */
/* ------------------------------------------------------------------ */

export function Strip({ groups, domain, height, xLabel, reference }: { groups: { label: string; sub?: string; color: string; values: { v: number; title?: string }[]; median?: number }[]; domain: [number, number]; height?: number; xLabel: string; reference?: number }) {
  const [ref, width] = useWidth<HTMLDivElement>()
  const [hover, setHover] = useState<{ g: number; i: number } | null>(null)
  const labelW = Math.min(150, width * 0.3)
  const rowH = 62
  const h = height ?? groups.length * rowH + 40
  const x = scaleLinear().domain(domain).range([labelW, width - 16])
  const yb = scaleBand<number>().domain(groups.map((_, i) => i)).range([8, h - 36]).padding(0.25)
  const jitter = (i: number) => (((i * 9301 + 49297) % 233280) / 233280 - 0.5) * (yb.bandwidth() * 0.7)
  const hv = hover ? groups[hover.g].values[hover.i] : null
  return (
    <div ref={ref} className="relative w-full">
      <svg width={width} height={h} role="img" aria-label={`Verteilung: ${xLabel}, nach Gruppe`}>
        {niceTicks(domain[0], domain[1], 4).map((t) => (
          <g key={t}>
            <line x1={x(t)} x2={x(t)} y1={4} y2={h - 30} stroke={t === 0 ? tokens.lineStrong : tokens.line} strokeDasharray={t === 0 ? undefined : '2 4'} />
            <text x={x(t)} y={h - 14} textAnchor="middle" {...axisText}>{fmt(t, 1)}</text>
          </g>
        ))}
        {reference != null && <line x1={x(reference)} x2={x(reference)} y1={4} y2={h - 30} stroke={tokens.ink3} />}
        {groups.map((g, gi) => {
          const cy = (yb(gi) ?? 0) + yb.bandwidth() / 2
          return (
            <g key={g.label}>
              <text x={0} y={cy - 6} dy="0.32em" fill={tokens.ink} fontSize={13} fontWeight={550}>{g.label}</text>
              {g.sub && <text x={0} y={cy + 10} dy="0.32em" {...axisText}>{g.sub}</text>}
              {g.values.map((d, i) => (
                <circle key={i} cx={x(d.v)} cy={cy + jitter(i)} r={hover?.g === gi && hover.i === i ? 5.5 : 3.8} fill={g.color} opacity={0.78} onMouseEnter={() => setHover({ g: gi, i })} onMouseLeave={() => setHover(null)} />
              ))}
              {g.median != null && <line x1={x(g.median)} x2={x(g.median)} y1={cy - yb.bandwidth() / 2} y2={cy + yb.bandwidth() / 2} stroke={tokens.ink} strokeWidth={2.5} />}
            </g>
          )
        })}
      </svg>
      {hv && hover && (
        <ChartTooltip x={x(hv.v)} y={(yb(hover.g) ?? 0) - 20} width={width}>
          <p className="font-mono tabular">ρ {fmt(hv.v, 2)}</p>
          {hv.title && <p className="text-ink-2">{hv.title}</p>}
        </ChartTooltip>
      )}
    </div>
  )
}

/* ------------------------------------------------------------------ */
/* Paired horizontal bars (model vs baseline)                          */
/* ------------------------------------------------------------------ */

export function PairedBars({ rows, a, b, format = (v: number) => fmt(v, 2), height }: { rows: { label: string; sub?: string; a: number; b: number }[]; a: { label: string; color: string }; b: { label: string; color: string }; format?: (v: number) => string; height?: number }) {
  const [ref, width] = useWidth<HTMLDivElement>()
  const labelW = Math.min(120, width * 0.28)
  const rowH = 40
  const h = height ?? rows.length * rowH + 10
  const vmax = max(rows.flatMap((r) => [r.a, r.b])) ?? 1
  const x = scaleLinear().domain([0, vmax * 1.05]).range([labelW, width - 56])
  return (
    <div ref={ref} className="w-full">
      <svg width={width} height={h} role="img" aria-label={`${a.label} ggü. ${b.label}`}>
        {rows.map((r, i) => {
          const y0 = 6 + i * rowH
          return (
            <g key={r.label}>
              <text x={0} y={y0 + 10} dy="0.32em" fill={tokens.ink} fontSize={12.5}>{r.label}</text>
              {r.sub && <text x={0} y={y0 + 25} dy="0.32em" {...axisText}>{r.sub}</text>}
              <rect x={labelW} y={y0 + 2} width={Math.max(1, x(r.a) - labelW)} height={11} rx={2} fill={a.color} />
              <rect x={labelW} y={y0 + 16} width={Math.max(1, x(r.b) - labelW)} height={11} rx={2} fill={b.color} />
              <text x={x(r.a) + 6} y={y0 + 8} dy="0.32em" fontFamily="var(--font-mono)" fontSize={11} fill={tokens.ink2}>{format(r.a)}</text>
              <text x={x(r.b) + 6} y={y0 + 22} dy="0.32em" fontFamily="var(--font-mono)" fontSize={11} fill={tokens.ink3}>{format(r.b)}</text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}
