import type { ReactNode } from 'react'

export type Tone = 'neutral' | 'maize' | 'rust' | 'sage' | 'water'

const tones: Record<Tone, string> = {
  neutral: 'border-[var(--line-strong)] text-ink-2 bg-white/[0.03]',
  maize: 'border-maize/30 text-maize bg-maize/[0.08]',
  rust: 'border-rust/30 text-rust bg-rust/[0.08]',
  sage: 'border-sage/30 text-sage bg-sage/[0.08]',
  water: 'border-water/30 text-water bg-water/[0.08]',
}

export function Badge({ tone = 'neutral', children, dot = false, className = '' }: { tone?: Tone; children: ReactNode; dot?: boolean; className?: string }) {
  return (
    <span className={`inline-flex items-center gap-1.5 whitespace-nowrap rounded-full border px-2.5 py-0.5 font-mono text-[10.5px] uppercase tracking-[0.1em] ${tones[tone]} ${className}`}>
      {dot && <span className="size-1.5 rounded-full bg-current" />}
      {children}
    </span>
  )
}

/** How strong the evidence behind a claim is — mirrors the project's status vocabulary. */
export type Strength = 'robust' | 'certain-small' | 'limited' | 'failed' | 'frozen' | 'pending' | 'done'

const strengthMap: Record<Strength, { tone: Tone; label: string }> = {
  robust: { tone: 'sage', label: 'Robust' },
  'certain-small': { tone: 'water', label: 'Small but certain' },
  limited: { tone: 'maize', label: 'Limited' },
  failed: { tone: 'rust', label: 'Did not pass' },
  frozen: { tone: 'neutral', label: 'Frozen' },
  pending: { tone: 'neutral', label: 'Pending' },
  done: { tone: 'neutral', label: 'Done' },
}

export function StrengthBadge({ strength }: { strength: Strength }) {
  const s = strengthMap[strength]
  return (
    <Badge tone={s.tone} dot>
      {s.label}
    </Badge>
  )
}

export function SimulatedBadge() {
  return (
    <Badge tone="maize" className="border-dashed">
      Simulated · backend not connected
    </Badge>
  )
}
