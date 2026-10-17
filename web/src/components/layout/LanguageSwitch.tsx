import { Check, Globe } from 'lucide-react'
import { AnimatePresence, motion } from 'motion/react'
import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { LANGS } from '../../i18n/lang'

/** Language menu in the navigation (German is the default). */
export function LanguageSwitch({ inline = false }: { inline?: boolean }) {
  const { t, i18n } = useTranslation()
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  const cur = LANGS.find((l) => l.code === i18n.language) ?? LANGS[0]

  useEffect(() => {
    if (!open) return
    const close = (e: MouseEvent) => {
      if (!ref.current?.contains(e.target as Node)) setOpen(false)
    }
    const esc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', close)
    document.addEventListener('keydown', esc)
    return () => {
      document.removeEventListener('mousedown', close)
      document.removeEventListener('keydown', esc)
    }
  }, [open])

  if (inline) {
    return (
      <div className="flex flex-wrap gap-2" role="group" aria-label={t('nav.language')}>
        {LANGS.map((l) => (
          <button
            key={l.code}
            type="button"
            onClick={() => i18n.changeLanguage(l.code)}
            className={`rounded-lg border px-3 py-1.5 text-[13px] ${l.code === cur.code ? 'border-maize text-maize' : 'border-[var(--line-strong)] text-ink-2'}`}
          >
            {l.label}
          </button>
        ))}
      </div>
    )
  }

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label={`${t('nav.language')}: ${cur.label}`}
        onClick={() => setOpen((o) => !o)}
        className="inline-flex h-8 items-center gap-1.5 rounded-lg px-2 font-mono text-[11.5px] tracking-[0.08em] text-ink-2 transition hover:bg-white/5 hover:text-ink"
      >
        <Globe className="size-3.5" />
        {cur.short}
      </button>
      <AnimatePresence>
        {open && (
          <motion.ul
            role="listbox"
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.15 }}
            className="panel-glass absolute right-0 top-10 z-50 min-w-[160px] p-1"
          >
            {LANGS.map((l) => (
              <li key={l.code}>
                <button
                  type="button"
                  role="option"
                  aria-selected={l.code === cur.code}
                  onClick={() => {
                    i18n.changeLanguage(l.code)
                    setOpen(false)
                  }}
                  className="flex w-full items-center justify-between gap-3 rounded-lg px-3 py-2 text-left text-[13.5px] text-ink hover:bg-white/[0.06]"
                >
                  <span>{l.label}</span>
                  {l.code === cur.code && <Check className="size-3.5 text-maize" />}
                </button>
              </li>
            ))}
          </motion.ul>
        )}
      </AnimatePresence>
    </div>
  )
}
