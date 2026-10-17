import { color as d3color } from 'd3-color'
import { useEffect, useMemo, useRef, useState } from 'react'
import type { PixelGrid } from '../../api/types'
import { ndviColor, relYieldColor } from '../../lib/color'
import { fmt } from '../../lib/format'
import { filledSeries } from '../../lib/series'

export type PixelMode = 'season' | 'window' | 'yield' | 'weak'

type Props = {
  pixels: PixelGrid
  mode: PixelMode
  /** dekad index for mode "season" */
  dekad?: number
  className?: string
  /** max rendered height in px; width follows the grid aspect */
  maxHeight?: number
  interactive?: boolean
  ariaLabel?: string
}

type Rgb = [number, number, number, number]

const toRgb = (c: string, a = 1): Rgb => {
  const p = d3color(c)?.rgb()
  return p ? [p.r, p.g, p.b, a] : [128, 128, 128, a]
}

/**
 * The project's signature view: a real field drawn as its 10-m Sentinel-2 cells.
 * Colors ease between states so the season and the reveal read as one motion.
 */
export function PixelField({ pixels, mode, dekad = 12, className = '', maxHeight = 520, interactive = true, ariaLabel }: Props) {
  const wrap = useRef<HTMLDivElement>(null)
  const canvas = useRef<HTMLCanvasElement>(null)
  const current = useRef<Rgb[] | null>(null)
  const [box, setBox] = useState({ w: 600, h: 400 })
  const [hover, setHover] = useState<{ i: number; x: number; y: number; maxX: number } | null>(null)

  const { w: gw, h: gh } = pixels.grid
  const filled = useMemo(() => (pixels.ndvi_by_dekad ? filledSeries(pixels.ndvi_by_dekad) : null), [pixels])

  // Fit the grid into the container width and max height.
  useEffect(() => {
    const el = wrap.current
    if (!el) return
    const ro = new ResizeObserver(([e]) => {
      const cw = e.contentRect.width
      const cell = Math.min(cw / gw, maxHeight / gh)
      setBox({ w: Math.floor(cell * gw), h: Math.floor(cell * gh) })
    })
    ro.observe(el)
    return () => ro.disconnect()
  }, [gw, gh, maxHeight])

  const target = useMemo<Rgb[]>(() => {
    const thr = pixels.weak_threshold
    return pixels.cells.map((c, i) => {
      const ndvi = c[4]
      const rel = c[5]
      if (mode === 'season') {
        const v = filled?.[Math.max(0, Math.min(filled.length - 1, dekad))]?.[i]
        return Number.isFinite(v) ? toRgb(ndviColor(v as number)) : [40, 46, 40, 1]
      }
      if (mode === 'yield') return toRgb(relYieldColor(rel))
      if (mode === 'weak') {
        const weak = ndvi != null && ndvi <= thr
        return weak ? toRgb('#e4694a') : toRgb(ndvi != null ? ndviColor(ndvi) : '#2a302a', 0.28)
      }
      return ndvi != null ? toRgb(ndviColor(ndvi)) : [40, 46, 40, 1]
    })
  }, [pixels, mode, dekad, filled])

  // Animate current colors toward the target.
  useEffect(() => {
    const cv = canvas.current
    if (!cv) return
    const ctx = cv.getContext('2d')
    if (!ctx) return
    const dpr = Math.min(2, window.devicePixelRatio || 1)
    cv.width = box.w * dpr
    cv.height = box.h * dpr
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    const cell = box.w / gw
    const gap = cell > 6 ? Math.min(1.2, cell * 0.12) : 0
    const radius = cell > 8 ? 1.5 : 0
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    const from = current.current && current.current.length === target.length ? current.current : target.map((t) => [t[0], t[1], t[2], 0] as Rgb)
    const dur = reduce ? 0 : mode === 'season' ? 260 : 650
    const t0 = performance.now()
    let raf = 0
    const draw = (now: number) => {
      const k = dur === 0 ? 1 : Math.min(1, (now - t0) / dur)
      const e = 1 - Math.pow(1 - k, 3)
      ctx.clearRect(0, 0, box.w, box.h)
      const next: Rgb[] = new Array(target.length)
      for (let i = 0; i < target.length; i++) {
        const a = from[i]
        const b = target[i]
        const c: Rgb = [a[0] + (b[0] - a[0]) * e, a[1] + (b[1] - a[1]) * e, a[2] + (b[2] - a[2]) * e, a[3] + (b[3] - a[3]) * e]
        next[i] = c
        const px = pixels.cells[i]
        ctx.fillStyle = `rgba(${c[0] | 0},${c[1] | 0},${c[2] | 0},${c[3]})`
        const x = px[2] * cell + gap / 2
        const y = px[3] * cell + gap / 2
        const s = cell - gap
        if (radius) {
          ctx.beginPath()
          ctx.roundRect(x, y, s, s, radius)
          ctx.fill()
        } else ctx.fillRect(x, y, s, s)
      }
      current.current = next
      if (k < 1) raf = requestAnimationFrame(draw)
    }
    raf = requestAnimationFrame(draw)
    return () => cancelAnimationFrame(raf)
  }, [target, box, gw, mode, pixels.cells])

  const index = useMemo(() => {
    const m = new Map<string, number>()
    pixels.cells.forEach((c, i) => m.set(`${c[2]},${c[3]}`, i))
    return m
  }, [pixels])

  const hc = hover ? pixels.cells[hover.i] : null
  const seasonVal = hover && filled ? filled[dekad]?.[hover.i] : null

  return (
    <div ref={wrap} className={`relative flex w-full justify-center ${className}`}>
      <canvas
        ref={canvas}
        role="img"
        aria-label={ariaLabel ?? 'Field shown as 10-metre satellite cells'}
        style={{ width: box.w, height: box.h }}
        onMouseLeave={() => setHover(null)}
        onMouseMove={(e) => {
          if (!interactive) return
          const r = e.currentTarget.getBoundingClientRect()
          const cell = box.w / gw
          const gx = Math.floor((e.clientX - r.left) / cell)
          const gy = Math.floor((e.clientY - r.top) / cell)
          const i = index.get(`${gx},${gy}`)
          const cw = wrap.current?.clientWidth ?? box.w
          setHover(i == null ? null : { i, x: e.clientX - r.left + (cw - box.w) / 2, y: e.clientY - r.top, maxX: cw - 170 })
        }}
      />
      {hc && hover && (
        <div className="panel-glass pointer-events-none absolute z-10 px-3 py-2 font-mono text-[11px] leading-relaxed text-ink" style={{ left: Math.min(hover.x + 14, hover.maxX), top: hover.y + 14 }}>
          {mode === 'season' ? <p>NDVI {fmt(seasonVal, 2)}</p> : <p>NDVI (Jul–Aug) {fmt(hc[4], 2)}</p>}
          <p>Yield {fmt(hc[5] * 100, 0)} % of field mean</p>
          {mode === 'weak' && hc[4] != null && hc[4] <= pixels.weak_threshold && <p className="text-rust">Flagged: lowest NDVI quarter</p>}
        </div>
      )}
    </div>
  )
}
