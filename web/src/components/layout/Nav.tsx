import { AnimatePresence, motion } from 'motion/react'
import { ArrowRight, Menu, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, NavLink, useLocation } from 'react-router'
import { ButtonLink } from '../ui/Button'
import { LanguageSwitch } from './LanguageSwitch'

const NAV_LINKS = [
  { to: '/evidence', key: 'nav.evidence' },
  { to: '/model', key: 'nav.model' },
  { to: '/data', key: 'nav.data' },
  { to: '/method', key: 'nav.method' },
  { to: '/konzept', key: 'nav.concept' },
  { to: '/about', key: 'nav.about' },
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
  const { t } = useTranslation()
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
      <div className="mx-auto flex h-16 max-w-[1240px] items-center justify-between gap-4 px-4 sm:px-8">
        <Link to="/" className="flex items-center gap-2.5" aria-label={t('nav.homeAria')}>
          <Logo className="size-[22px]" />
          <span className="whitespace-nowrap font-display text-[17px] font-semibold tracking-[-0.02em]">
            CropTransfer <span className="text-ink-3">AT</span>
          </span>
        </Link>
        <nav aria-label={t('nav.main')} className="hidden items-center gap-0.5 lg:flex">
          {NAV_LINKS.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) =>
                `relative rounded-lg px-2.5 py-2 text-[13.5px] transition-colors ${isActive ? 'text-ink' : 'text-ink-2 hover:text-ink'}`
              }
            >
              {({ isActive }) => (
                <>
                  {t(l.key)}
                  {isActive && <motion.span layoutId="nav-active" className="absolute inset-x-2.5 -bottom-[1px] h-px bg-maize" />}
                </>
              )}
            </NavLink>
          ))}
        </nav>
        <div className="flex items-center gap-1.5">
          <span className="hidden lg:block">
            <LanguageSwitch />
          </span>
          <span className="hidden sm:block">
            <ButtonLink to="/analyse" size="sm" icon={<ArrowRight className="size-3.5" />}>
              {t('nav.cta')}
            </ButtonLink>
          </span>
          <button
            type="button"
            className="inline-flex size-9 items-center justify-center rounded-lg text-ink-2 hover:bg-white/5 lg:hidden"
            aria-label={open ? t('nav.closeMenu') : t('nav.openMenu')}
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
            aria-label={t('nav.mobile')}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden border-t border-[var(--line)] lg:hidden"
          >
            <div className="flex flex-col gap-1 px-4 py-4">
              {[{ to: '/', key: 'nav.home' }, { to: '/analyse', key: 'nav.cta' }, ...NAV_LINKS].map((l) => (
                <NavLink key={l.to} to={l.to} end className={({ isActive }) => `rounded-lg px-3 py-3 font-display text-xl ${isActive ? 'text-maize' : 'text-ink'}`}>
                  {t(l.key)}
                </NavLink>
              ))}
              <div className="px-3 pt-3">
                <LanguageSwitch inline />
              </div>
            </div>
          </motion.nav>
        )}
      </AnimatePresence>
    </header>
  )
}
