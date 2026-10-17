import { motion, useReducedMotion } from 'motion/react'
import type { FieldGeometry } from '../../api/types'
import { bbox, metresPerDegree, outerRings } from '../../lib/geo'

/** Field polygon drawn to scale as an SVG outline (draws itself on first view). */
export function FieldOutline({ geometry, className = '', stroke = '#e6b450' }: { geometry: FieldGeometry; className?: string; stroke?: string }) {
  const reduce = useReducedMotion()
  const [x0, y0, x1, y1] = bbox(geometry)
  const k = metresPerDegree((y0 + y1) / 2)
  const w = (x1 - x0) * k.x
  const h = (y1 - y0) * k.y
  const s = 100 / Math.max(w, h)
  const d = outerRings(geometry)
    .map((ring) => `M${ring.map(([x, y]) => `${((x - x0) * k.x * s).toFixed(2)},${((y1 - y) * k.y * s).toFixed(2)}`).join('L')}Z`)
    .join('')
  const vw = w * s
  const vh = h * s
  return (
    <svg viewBox={`-4 -4 ${vw + 8} ${vh + 8}`} className={className} role="img" aria-label="Field outline">
      <motion.path
        d={d}
        fill={stroke}
        fillOpacity={0.06}
        stroke={stroke}
        strokeWidth={1.2}
        vectorEffect="non-scaling-stroke"
        initial={reduce ? false : { pathLength: 0 }}
        whileInView={{ pathLength: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 1.6, ease: [0.22, 1, 0.36, 1] }}
      />
    </svg>
  )
}
