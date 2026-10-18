import { animate, useInView, useReducedMotion } from 'motion/react'
import { useEffect, useRef } from 'react'
import { fmtNum } from '../../lib/format'

const text = (v: number, digits: number) =>
  Number.isFinite(v) ? (v < 0 ? `−${fmtNum(Math.abs(v), digits)}` : fmtNum(v, digits)) : '–'

/** Counts from 0 to value once the number scrolls into view. */
export function CountUp({ value, digits = 2 }: { value: number; digits?: number }) {
  const ref = useRef<HTMLSpanElement>(null)
  const inView = useInView(ref, { once: true, margin: '-10% 0px' })
  const reduce = useReducedMotion()

  useEffect(() => {
    const el = ref.current
    if (!el) return
    if (!Number.isFinite(value) || reduce) {
      el.textContent = text(value, digits)
      return
    }
    if (!inView) {
      el.textContent = text(0, digits)
      return
    }
    const c = animate(0, value, { duration: 1.1, ease: [0.22, 1, 0.36, 1], onUpdate: (v) => (el.textContent = text(v, digits)) })
    return () => c.stop()
  }, [value, inView, reduce, digits])

  return (
    <span ref={ref} className="tabular">
      {text(value, digits)}
    </span>
  )
}
