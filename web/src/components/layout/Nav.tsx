import { AnimatePresence, motion } from 'motion/react'
import { ArrowRight, Menu, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, NavLink, useLocation } from 'react-router'
import { ButtonLink } from '../ui/Button'

export const NAV_LINKS = [
  { to: '/evidence', label: 'Evidence' },
  { to: '/model', label: 'Model card' },
  { to: '/data', label: 'Data' },
  { to: '/method', label: 'Method' },
  { to: '/about', label: 'About' },
]

export function Logo({ className = '' }: { className?: string }) {
  const cells = [1, 0.7, 0.45, 0.7, 1, 2, 0.45, 0.7, 1]
  return (
    <svg viewBox="0 0 22 22" className={className} aria-hidden>
      {cells.map((o, i) => (
        <rect key={i} x={(i % 3) * 7.5} y={Math.floor(i / 3) * 7.5} width="6" height="6" rx="1.2" fill={o === 2 ? '#e4694a' : '#e6b450'} opacity={o === 2 ? 1 : o} />
      ))}
    </svg>
  )
}

export function Nav() {
  const [scrolled, setScrolled] = useState(false)
  const [open, setOpen] = useState(false)
  const loc = useLocation()

  useEffect(() => {
    const on = () => setScrolled(window.scrollY > 12)
    on()
    window.addEventListener('scroll', on, { passive: true })
    return () => window.removeEventListener('scroll', on)
  }, [])
  useEffect(() => setOpen(false), [loc.pathname])

  return (
    <header
      className={`fixed inset-x-0 top-0 z-50 transition-[background,border-color,backdrop-filter] duration-300 ${
        scrolled || open ? 'border-b border-[var(--line)] bg-soil-950/75 backdrop-blur-xl' : 'border-b border-transparent'
      }`}
    >
      <div className="mx-auto flex h-16 max-w-[1240px] items-center justify-between gap-6 px-4 sm:px-8">
        <Link to="/" className="flex items-center gap-2.5" aria-label="CropTransfer AT, overview">
          <Logo className="size-[22px]" />
          <span className="whitespace-nowrap font-display text-[17px] font-semibold tracking-[-0.02em]">
            CropTransfer <span className="text-ink-3">AT</span>
          </span>
        </Link>
        <nav aria-label="Main" className="hidden items-center gap-1 lg:flex">
          {NAV_LINKS.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) =>
                `relative rounded-lg px-3 py-2 text-[13.5px] transition-colors ${isActive ? 'text-ink' : 'text-ink-2 hover:text-ink'}`
              }
            >
              {({ isActive }) => (
                <>
                  {l.label}
                  {isActive && <motion.span layoutId="nav-active" className="absolute inset-x-3 -bottom-[1px] h-px bg-maize" />}
                </>
              )}
            </NavLink>
          ))}
        </nav>
        <div className="flex items-center gap-2">
          <span className="hidden sm:block">
            <ButtonLink to="/analyse" size="sm" icon={<ArrowRight className="size-3.5" />}>
              Analyse a field
            </ButtonLink>
          </span>
          <button
            type="button"
            className="inline-flex size-9 items-center justify-center rounded-lg text-ink-2 hover:bg-white/5 lg:hidden"
            aria-label={open ? 'Close menu' : 'Open menu'}
            aria-expanded={open}
            onClick={() => setOpen((v) => !v)}
          >
            {open ? <X className="size-5" /> : <Menu className="size-5" />}
          </button>
        </div>
      </div>
      <AnimatePresence>
        {open && (
          <motion.nav
            aria-label="Mobile"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden border-t border-[var(--line)] lg:hidden"
          >
            <div className="flex flex-col gap-1 px-4 py-4">
              {[{ to: '/', label: 'Overview' }, { to: '/analyse', label: 'Analyse a field' }, ...NAV_LINKS].map((l) => (
                <NavLink key={l.to} to={l.to} end className={({ isActive }) => `rounded-lg px-3 py-3 font-display text-xl ${isActive ? 'text-maize' : 'text-ink'}`}>
                  {l.label}
                </NavLink>
              ))}
            </div>
          </motion.nav>
        )}
      </AnimatePresence>
    </header>
  )
}
