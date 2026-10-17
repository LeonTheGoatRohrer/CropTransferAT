import { Link } from 'react-router'
import { Logo } from './Nav'

const COLUMNS = [
  {
    title: 'Product',
    links: [
      { to: '/', label: 'Overview' },
      { to: '/contribute', label: 'Add your field' },
      { to: '/analyse', label: 'Analyse a field' },
      { to: '/evidence', label: 'Evidence' },
    ],
  },
  {
    title: 'Science',
    links: [
      { to: '/model', label: 'The three models' },
      { to: '/method', label: 'Method and experiments' },
      { to: '/data', label: 'Data sources and explorer' },
    ],
  },
  {
    title: 'Project',
    links: [
      { to: '/about#limitations', label: 'Limitations' },
      { to: '/about#roadmap', label: 'Roadmap' },
      { to: '/about#disclosure', label: 'Support and AI disclosure' },
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
            Early detection of stress and yield loss in maize from Sentinel-2 time series, weather and soil. A solo project for the
            Bundeswettbewerb Künstliche Intelligenz (BWKI) Austria.
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
        <p>Every model number on this site is read from the project's result files. Demo values are labelled as such.</p>
        <p className="font-mono">Private preview · not published</p>
      </div>
    </footer>
  )
}
