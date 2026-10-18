import { Link } from 'react-router'
import { Logo } from './Nav'

const COLUMNS = [
  {
    title: 'Angebot',
    links: [
      { to: '/', label: 'Übersicht' },
      { to: '/contribute', label: 'Feld eintragen' },
      { to: '/analyse', label: 'Feld analysieren' },
      { to: '/evidence', label: 'Belege' },
    ],
  },
  {
    title: 'Wissenschaft',
    links: [
      { to: '/model', label: 'Die drei Modelle' },
      { to: '/method', label: 'Methode und Experimente' },
      { to: '/data', label: 'Datenquellen und Datenexplorer' },
    ],
  },
  {
    title: 'Projekt',
    links: [
      { to: '/about#limitations', label: 'Grenzen' },
      { to: '/about#roadmap', label: 'Ausblick' },
      { to: '/about#disclosure', label: 'Unterstützung und KI-Offenlegung' },
    ],
  },
]

export function Footer() {
  return (
    <footer className="mt-32 border-t border-[var(--line)]">
      <div className="mx-auto grid max-w-[1240px] gap-12 px-4 py-16 sm:px-8 md:grid-cols-[1.4fr_repeat(3,1fr)]">
        <div className="max-w-[340px]">
          <div className="flex items-center gap-2.5">
            <Logo className="size-5" />
            <span className="font-display text-[16px] font-semibold">CropTransfer AT</span>
          </div>
          <p className="mt-4 text-[13.5px] leading-relaxed text-ink-3">
            Früherkennung von Stress und Ertragsverlust bei Mais aus Sentinel-2-Zeitreihen, Wetter und Boden. Ein Einzelprojekt für den
            Bundeswettbewerb Künstliche Intelligenz (BWKI) Österreich.
          </p>
        </div>
        {COLUMNS.map((c) => (
          <div key={c.title}>
            <p className="eyebrow mb-4">{c.title}</p>
            <ul className="flex flex-col gap-2.5">
              {c.links.map((l) => (
                <li key={l.to}>
                  <Link to={l.to} className="link-underline text-[13.5px] text-ink-2 hover:text-ink">
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="mx-auto flex max-w-[1240px] flex-col gap-2 border-t border-[var(--line)] px-4 py-6 text-[12px] text-ink-4 sm:flex-row sm:justify-between sm:px-8">
        <p>Jede Modellzahl auf dieser Seite stammt aus den Ergebnisdateien des Projekts. Demowerte sind als solche gekennzeichnet.</p>
        <p className="font-mono">Private Vorschau · nicht veröffentlicht</p>
      </div>
    </footer>
  )
}
