import type { ReactNode } from 'react'
import { Reveal } from './Reveal'

export function Container({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`mx-auto w-full max-w-[1240px] px-4 sm:px-8 ${className}`}>{children}</div>
}

/** Section heading: eyebrow names the kind of content, title states the claim. */
export function SectionHeader({
  eyebrow,
  title,
  lede,
  aside,
  className = '',
}: {
  eyebrow: string
  title: ReactNode
  lede?: ReactNode
  aside?: ReactNode
  className?: string
}) {
  return (
    <Reveal className={`flex flex-col gap-6 md:flex-row md:items-end md:justify-between ${className}`}>
      <div className="max-w-[780px]">
        <p className="eyebrow mb-4">{eyebrow}</p>
        <h2 className="text-balance text-[clamp(2rem,4vw,3.25rem)]">{title}</h2>
        {lede && <div className="mt-5 max-w-[640px] text-pretty text-[17px] leading-relaxed text-ink-2">{lede}</div>}
      </div>
      {aside}
    </Reveal>
  )
}

/** Pointer to the repository file a number comes from. */
export function Source({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <p className={`font-mono text-[10.5px] leading-relaxed tracking-wide text-ink-4 ${className}`}>Quelle · {children}</p>
}
