import { motion } from 'motion/react'
import { useId } from 'react'

type Item<T extends string> = { value: T; label: string; disabled?: boolean }

/** Segmented control with a sliding indicator. */
export function Tabs<T extends string>({
  items,
  value,
  onChange,
  size = 'md',
  className = '',
  label,
}: {
  items: Item<T>[]
  value: T
  onChange: (v: T) => void
  size?: 'sm' | 'md'
  className?: string
  label?: string
}) {
  const id = useId()
  return (
    <div role="tablist" aria-label={label} className={`inline-flex max-w-full overflow-x-auto rounded-[11px] border border-[var(--line)] bg-black/25 p-1 ${className}`}>
      {items.map((it) => {
        const active = it.value === value
        return (
          <button
            key={it.value}
            role="tab"
            type="button"
            aria-selected={active}
            disabled={it.disabled}
            onClick={() => onChange(it.value)}
            className={`relative shrink-0 rounded-[8px] font-medium transition-colors duration-200 disabled:opacity-30 ${size === 'sm' ? 'h-7 px-2.5 text-[12px]' : 'h-8 px-3.5 text-[13px]'} ${active ? 'text-soil-950' : 'text-ink-2 hover:text-ink'}`}
          >
            {active && (
              <motion.span layoutId={`tab-${id}`} className="absolute inset-0 rounded-[8px] bg-ink" transition={{ type: 'spring', stiffness: 500, damping: 40 }} />
            )}
            <span className="relative">{it.label}</span>
          </button>
        )
      })}
    </div>
  )
}
