import { Link } from 'react-router'
import type { ComponentProps, ReactNode } from 'react'

type Variant = 'primary' | 'secondary' | 'ghost'

const base =
  'group relative inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-[var(--radius-control)] font-medium transition-[background,color,box-shadow,transform,border-color] duration-200 ease-[var(--ease-out-soft)] active:translate-y-px disabled:pointer-events-none disabled:opacity-40'

const variants: Record<Variant, string> = {
  primary:
    'bg-maize text-soil-950 shadow-[0_1px_0_rgba(255,255,255,0.35)_inset,0_10px_30px_-12px_rgba(230,180,80,0.6)] hover:bg-maize-soft',
  secondary: 'border border-[var(--line-strong)] bg-white/[0.03] text-ink hover:border-ink-3 hover:bg-white/[0.06]',
  ghost: 'text-ink-2 hover:bg-white/[0.05] hover:text-ink',
}

const sizes = { sm: 'h-8 px-3 text-[13px]', md: 'h-10 px-4 text-sm', lg: 'h-12 px-5 text-[15px]' }

type Common = { variant?: Variant; size?: keyof typeof sizes; icon?: ReactNode; children: ReactNode; className?: string }

export function Button({ variant = 'primary', size = 'md', icon, children, className = '', ...rest }: Common & ComponentProps<'button'>) {
  return (
    <button className={`${base} ${variants[variant]} ${sizes[size]} ${className}`} {...rest}>
      {children}
      {icon}
    </button>
  )
}

export function ButtonLink({ variant = 'primary', size = 'md', icon, children, className = '', to }: Common & { to: string }) {
  return (
    <Link to={to} className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}>
      {children}
      {icon && <span className="transition-transform duration-300 group-hover:translate-x-0.5">{icon}</span>}
    </Link>
  )
}
