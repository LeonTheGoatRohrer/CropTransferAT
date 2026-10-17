import { useTranslation } from 'react-i18next'
import { Link } from 'react-router'
import { Logo } from './Nav'

const COLUMNS: { title: string; links: [string, string][] }[] = [
  { title: 'footer.product', links: [['/', 'footer.overview'], ['/analyse', 'footer.analyse'], ['/evidence', 'footer.evidence']] },
  { title: 'footer.science', links: [['/model', 'footer.model'], ['/method', 'footer.method'], ['/data', 'footer.data']] },
  {
    title: 'footer.project',
    links: [['/konzept', 'footer.concept'], ['/about#limitations', 'footer.limits'], ['/about#roadmap', 'footer.roadmap'], ['/about#disclosure', 'footer.disclosure']],
  },
]

export function Footer() {
  const { t } = useTranslation()
  return (
    <footer className="mt-32 border-t border-[var(--line)]">
      <div className="mx-auto grid max-w-[1240px] gap-12 px-4 py-16 sm:px-8 md:grid-cols-[1.4fr_repeat(3,1fr)]">
        <div className="max-w-[340px]">
          <div className="flex items-center gap-2.5">
            <Logo className="size-5" />
            <span className="font-display text-[16px] font-semibold">CropTransfer AT</span>
          </div>
          <p className="mt-4 text-[13.5px] leading-relaxed text-ink-3">{t('footer.blurb')}</p>
        </div>
        {COLUMNS.map((c) => (
          <div key={c.title}>
            <p className="eyebrow mb-4">{t(c.title)}</p>
            <ul className="flex flex-col gap-2.5">
              {c.links.map(([to, key]) => (
                <li key={to}>
                  <Link to={to} className="link-underline text-[13.5px] text-ink-2 hover:text-ink">
                    {t(key)}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="mx-auto flex max-w-[1240px] flex-col gap-2 border-t border-[var(--line)] px-4 py-6 text-[12px] text-ink-4 sm:flex-row sm:justify-between sm:px-8">
        <p>{t('footer.note')}</p>
        <p className="font-mono">{t('footer.private')}</p>
      </div>
    </footer>
  )
}
