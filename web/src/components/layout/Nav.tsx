import { AnimatePresence, motion } from 'motion/react'
import { ArrowRight, ChevronDown, Menu, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, NavLink, useLocation, type Location } from 'react-router'
import { ButtonLink } from '../ui/Button'

export type NavSection = { hash: string; label: string }
export type NavItem = { to: string; label: string; sections?: NavSection[] }

/** Every page and every anchored section of the site, so all of it is reachable from the navbar. */
export const NAV_LINKS: NavItem[] = [
  { to: '/', label: 'Übersicht' },
  { to: '/analyse', label: 'Feld analysieren' },
  {
    to: '/model',
    label: 'Modelle',
    sections: [
      { hash: 'vorgehen', label: 'So sind wir vorgegangen' },
      { hash: 'drei-modelle', label: 'Die drei Modelle' },
    ],
  },
  {
    to: '/method',
    label: 'Methode',
    sections: [
      { hash: 'ablauf', label: 'So funktioniert es' },
      { hash: 'validierung', label: 'Validierung' },
      { hash: 'merkmale', label: 'Merkmalsbildung' },
      { hash: 'modelle', label: 'Modellübersicht' },
      { hash: 'experiments', label: 'Experimente' },
    ],
  },
  {
    to: '/evidence',
    label: 'Belege',
    sections: [
      { hash: 'within-field', label: 'Innerhalb des Feldes' },
      { hash: 'field-level', label: 'Ganze Felder' },
      { hash: 'year-models', label: 'Von Jahr zu Jahr' },
      { hash: 'regional', label: 'Regionen, EU' },
      { hash: 'austria', label: 'Österreich-Test' },
    ],
  },
  {
    to: '/data',
    label: 'Daten',
    sections: [
      { hash: 'quellen', label: 'Datenquellen' },
      { hash: 'explorer', label: 'Daten erkunden' },
    ],
  },
  {
    to: '/about',
    label: 'Über',
    sections: [
      { hash: 'limitations', label: 'Grenzen' },
      { hash: 'roadmap', label: 'Ausblick' },
      { hash: 'disclosure', label: 'Unterstützung und KI-Offenlegung' },
    ],
  },
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

/** Drops focus after a click so a hover menu does not stay open through :focus-within. */
const blurActive = () => (document.activeElement as HTMLElement | null)?.blur()

/** Section links: the router only scrolls on a hash change, so a repeated click on the same section scrolls here. */
function goToSection(el: HTMLElement, loc: Location, to: string, hash: string, after?: () => void) {
  el.blur()
  after?.()
  if (loc.pathname === to && loc.hash === `#${hash}`) document.getElementById(hash)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
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
  useEffect(() => setOpen(false), [loc.pathname, loc.hash])

  return (
    <header
      className={`fixed inset-x-0 top-0 z-50 transition-[background,border-color,backdrop-filter] duration-300 ${
        scrolled || open ? 'border-b border-[var(--line)] bg-soil-950/75 backdrop-blur-xl' : 'border-b border-transparent'
      }`}
    >
      <div className="mx-auto flex h-16 max-w-[1240px] items-center justify-between gap-6 px-4 sm:px-8">
        <Link to="/" className="flex items-center gap-2.5" aria-label="CropTransfer AT, Übersicht">
          <Logo className="size-[22px]" />
          <span className="whitespace-nowrap font-display text-[17px] font-semibold tracking-[-0.02em]">
            CropTransfer <span className="text-ink-3">AT</span>
          </span>
        </Link>
        <nav aria-label="Hauptnavigation" className="hidden items-center lg:flex">
          {NAV_LINKS.map((l) => (
            <div key={l.to} className="group relative">
              <NavLink
                to={l.to}
                end
                onClick={blurActive}
                className={({ isActive }) =>
                  `relative flex items-center gap-1 whitespace-nowrap rounded-lg px-2.5 py-2 text-[13.5px] transition-colors ${isActive ? 'text-ink' : 'text-ink-2 hover:text-ink'}`
                }
              >
                {({ isActive }) => (
                  <>
                    {l.label}
                    {l.sections && <ChevronDown aria-hidden className="size-3 opacity-60 transition-transform group-focus-within:rotate-180 group-hover:rotate-180" />}
                    {isActive && <motion.span layoutId="nav-active" className="absolute inset-x-2.5 -bottom-[1px] h-px bg-maize" />}
                  </>
                )}
              </NavLink>
              {l.sections && (
                <div className="invisible absolute left-0 top-full pt-2 opacity-0 transition-[opacity,visibility] duration-150 group-focus-within:visible group-focus-within:opacity-100 group-hover:visible group-hover:opacity-100">
                  <ul aria-label={`Abschnitte: ${l.label}`} className="min-w-[230px] rounded-xl border border-[var(--line)] bg-soil-950/95 p-1.5 shadow-[var(--shadow-panel)] backdrop-blur-xl">
                    {l.sections.map((sec) => (
                      <li key={sec.hash}>
                        <Link
                          to={`${l.to}#${sec.hash}`}
                          onClick={(e) => goToSection(e.currentTarget, loc, l.to, sec.hash)}
                          className="block whitespace-nowrap rounded-lg px-3 py-2 text-[13px] text-ink-2 transition-colors hover:bg-white/[0.05] hover:text-ink focus-visible:bg-white/[0.05] focus-visible:text-ink"
                        >
                          {sec.label}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </nav>
        <div className="flex items-center gap-2">
          <span className="hidden sm:block">
            <ButtonLink to="/contribute" size="sm" icon={<ArrowRight className="size-3.5" />}>
              Feld eintragen
            </ButtonLink>
          </span>
          <button
            type="button"
            className="inline-flex size-9 items-center justify-center rounded-lg text-ink-2 hover:bg-white/5 lg:hidden"
            aria-label={open ? 'Menü schließen' : 'Menü öffnen'}
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
            aria-label="Mobile Navigation"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden border-t border-[var(--line)] lg:hidden"
          >
            <div className="flex max-h-[calc(100dvh-4rem)] flex-col gap-1 overflow-y-auto px-4 py-4">
              {[...NAV_LINKS.slice(0, 1), { to: '/contribute', label: 'Feld eintragen' }, ...NAV_LINKS.slice(1)].map((l: NavItem) => (
                <div key={l.to}>
                  <NavLink to={l.to} end className={({ isActive }) => `block rounded-lg px-3 py-2.5 font-display text-xl ${isActive ? 'text-maize' : 'text-ink'}`}>
                    {l.label}
                  </NavLink>
                  {l.sections && (
                    <ul className="mb-2 ml-3 flex flex-col border-l border-[var(--line)] pl-3">
                      {l.sections.map((sec) => (
                        <li key={sec.hash}>
                          <Link
                            to={`${l.to}#${sec.hash}`}
                            onClick={(e) => goToSection(e.currentTarget, loc, l.to, sec.hash, () => setOpen(false))}
                            className="block rounded-lg px-2 py-1.5 text-[14.5px] text-ink-2 hover:text-ink"
                          >
                            {sec.label}
                          </Link>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          </motion.nav>
        )}
      </AnimatePresence>
    </header>
  )
}
