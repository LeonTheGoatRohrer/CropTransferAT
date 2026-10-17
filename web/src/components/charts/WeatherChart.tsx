import { max, min } from 'd3-array'
import { scaleLinear } from 'd3-scale'
import { curveMonotoneX, line } from 'd3-shape'
import { useState } from 'react'
import type { WeatherSeries } from '../../api/types'
import { tokens } from '../../lib/color'
import { MONTH_TICKS, N_DEKADS, cumulative, dekadLabel } from '../../lib/dekads'
import { fmt } from '../../lib/format'
import { ChartTooltip, GridY, axisText, niceTicks, useWidth } from './core'

export type WeatherMode = 'rain' | 'temperature' | 'gdd' | 'moisture'

type P = { i: number; v: number }

/** Weather of the field-year (solid) against the long-term mean of the same ERA5-Land cell (dashed). */
export function WeatherChart({ actual, normal, mode, year, height = 260 }: { actual: WeatherSeries; normal: WeatherSeries; mode: WeatherMode; year?: number; height?: number }) {
  const [ref, width] = useWidth<HTMLDivElement>()
  const [hover, setHover] = useState<number | null>(null)
  const m = { t: 16, r: 16, b: 30, l: 46 }
  const x = scaleLinear().domain([-0.5, N_DEKADS - 0.5]).range([m.l, width - m.r])

  const series = (() => {
    switch (mode) {
      case 'rain':
        return { a: cumulative(actual.prec), n: cumulative(normal.prec), bars: actual.prec, barsN: normal.prec, unit: 'mm', label: 'Cumulative rain' }
      case 'temperature':
        return { a: actual.tmax, n: normal.tmax, unit: '°C', label: 'Mean daily max' }
      case 'gdd':
        return { a: cumulative(actual.gdd), n: cumulative(normal.gdd), unit: '°C·d', label: 'Growing degree days' }
      case 'moisture':
        return { a: actual.swvl, n: normal.swvl, unit: 'm³/m³', label: 'Soil moisture 7–28 cm' }
    }
  })()

  const vals = [...series.a, ...series.n].filter((v): v is number => v != null)
  let lo = mode === 'temperature' || mode === 'moisture' ? (min(vals) ?? 0) : 0
  let hi = max(vals) ?? 1
  const pad = (hi - lo) * 0.08
  lo = mode === 'temperature' || mode === 'moisture' ? lo - pad : 0
  hi = hi + pad
  const y = scaleLinear().domain([lo, hi]).range([height - m.b, m.t]).nice(4)
  const [d0, d1] = y.domain()

  const toPts = (xs: (number | null)[]): P[] => xs.flatMap((v, i) => (v == null ? [] : [{ i, v }]))
  const lg = line<P>().x((d) => x(d.i)).y((d) => y(d.v)).curve(curveMonotoneX)
  const barMax = series.bars ? Math.max(...[...series.bars, ...(series.barsN ?? [])].map((v) => v ?? 0), 1) : 1
  const barH = (v: number) => ((height - m.t - m.b) * 0.38 * v) / barMax
  const bw = Math.max(2, (x(1) - x(0)) * 0.34)
  const digits = mode === 'moisture' ? 2 : 0

  return (
    <div ref={ref} className="relative w-full select-none">
      <svg
        width={width}
        height={height}
        role="img"
        aria-label={`${series.label}: this season vs long-term mean`}
        onMouseLeave={() => setHover(null)}
        onMouseMove={(e) => {
          const r = (e.currentTarget as SVGSVGElement).getBoundingClientRect()
          const i = Math.round(x.invert(e.clientX - r.left))
          setHover(i >= 0 && i < N_DEKADS ? i : null)
        }}
      >
        <GridY ticks={niceTicks(d0, d1, 4)} y={y} x0={m.l} x1={width - m.r} fmt={(v) => v.toFixed(digits)} />
        {MONTH_TICKS.map((t) => (
          <text key={t.label} x={x(t.pos)} y={height - m.b + 18} {...axisText}>
            {t.label}
          </text>
        ))}
        {series.bars &&
          series.bars.map((v, i) => (
            <g key={i}>
              <rect x={x(i) - bw - 1} y={height - m.b - barH(series.barsN?.[i] ?? 0)} width={bw} height={barH(series.barsN?.[i] ?? 0)} rx={1.5} fill={tokens.ink4} opacity={0.5} />
              <rect x={x(i) + 1} y={height - m.b - barH(v ?? 0)} width={bw} height={barH(v ?? 0)} rx={1.5} fill={tokens.water} opacity={hover === i ? 1 : 0.75} />
            </g>
          ))}
        <path d={lg(toPts(series.n)) ?? ''} fill="none" stroke={tokens.ink3} strokeWidth={1.5} strokeDasharray="4 4" />
        <path d={lg(toPts(series.a)) ?? ''} fill="none" stroke={mode === 'temperature' ? tokens.rust : mode === 'gdd' ? tokens.maize : tokens.water} strokeWidth={2.2} />
        {mode === 'temperature' &&
          (actual.heat ?? []).map((h, i) =>
            h ? <circle key={i} cx={x(i)} cy={m.t + 4} r={2 + Math.min(4, h)} fill={tokens.rust} opacity={0.75} /> : null,
          )}
        {hover != null && <line x1={x(hover)} x2={x(hover)} y1={m.t} y2={height - m.b} stroke={tokens.ink3} opacity={0.5} />}
      </svg>
      {hover != null && (
        <ChartTooltip x={x(hover)} y={m.t + 20} width={width}>
          <p className="eyebrow mb-1 !text-[10px]">{dekadLabel(hover, year)}</p>
          <p className="flex justify-between gap-4"><span className="text-ink-2">This season</span><span className="font-mono tabular">{fmt(series.a[hover], digits)} {series.unit}</span></p>
          <p className="flex justify-between gap-4"><span className="text-ink-2">Long-term mean</span><span className="font-mono tabular">{fmt(series.n[hover], digits)} {series.unit}</span></p>
          {series.bars && <p className="flex justify-between gap-4"><span className="text-ink-2">Rain this dekad</span><span className="font-mono tabular">{fmt(series.bars[hover], 0)} mm</span></p>}
          {mode === 'temperature' && (actual.heat?.[hover] ?? 0) > 0 && <p className="text-rust">{actual.heat?.[hover]} day(s) above 32 °C</p>}
        </ChartTooltip>
      )}
    </div>
  )
}
