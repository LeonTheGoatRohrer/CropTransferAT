import type { ReactNode } from 'react'
import { fmtCi } from '../../lib/format'
import { CountUp } from './CountUp'
import { keepGreek } from './Text'

type Props = {
  label: string
  value: number | null | undefined
  digits?: number
  prefix?: string
  suffix?: string
  ci?: [number | null | undefined, number | null | undefined]
  n?: string
  note?: ReactNode
  size?: 'md' | 'lg' | 'xl'
  tone?: 'ink' | 'maize' | 'rust' | 'sage' | 'water'
}

const sizes = { md: 'text-3xl', lg: 'text-5xl', xl: 'text-[clamp(3.5rem,7vw,5.5rem)]' }
const toneCls = { ink: 'text-ink', maize: 'text-maize', rust: 'text-rust', sage: 'text-sage', water: 'text-water' }

/** A number with its uncertainty and sample size — never a bare number. */
export function Metric({ label, value, digits = 2, prefix = '', suffix = '', ci, n, note, size = 'md', tone = 'ink' }: Props) {
  const hasCi = ci && ci[0] != null && ci[1] != null
  return (
    <div className="flex flex-col gap-2">
      <span className="eyebrow">{keepGreek(label)}</span>
      <span className={`font-display font-semibold leading-none tracking-[-0.035em] ${sizes[size]} ${toneCls[tone]}`}>
        {prefix}
        <CountUp value={value ?? NaN} digits={digits} />
        {suffix && <span className="ml-1 text-[0.42em] font-medium tracking-normal text-ink-3">{suffix}</span>}
      </span>
      {(hasCi || n) && (
        <span className="font-mono text-[11.5px] text-ink-3 tabular">
          {hasCi && <>95 % CI {fmtCi(ci[0], ci[1], digits)}</>}
          {hasCi && n && ' · '}
          {n && <>n = {n}</>}
        </span>
      )}
      {note && <div className="text-pretty text-[13.5px] leading-relaxed text-ink-2">{note}</div>}
    </div>
  )
}
