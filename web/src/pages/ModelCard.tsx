import { AnimatePresence, motion } from 'motion/react'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import type { Evidence } from '../api/types'
import { StrengthBadge, type Strength } from '../components/ui/Badge'
import { Reveal } from '../components/ui/Reveal'
import { Container } from '../components/ui/Section'
import { ErrorNote, Skeleton } from '../components/ui/States'
import { Tabs } from '../components/ui/Tabs'
import { keepGreek } from '../components/ui/Text'
import { useContent } from '../i18n'
import { fmt, fmtCi, fmtInt, fmtPct } from '../lib/format'
import { useResource } from '../lib/useResource'
import { getEvidence } from '../services/evidenceService'

type Key = 'map' | 'score' | 'eu'
const STRENGTH: Record<Key, Strength> = { map: 'robust', score: 'limited', eu: 'certain-small' }
const ROWS = ['architecture', 'inputs', 'target', 'training', 'validation', 'metrics', 'version', 'use', 'notFor'] as const

/** Fills the {{placeholders}} of the card texts with numbers from evidence.json. */
function interpolate(text: string, vars: Record<string, string | number>) {
  return text.replace(/\{\{(\w+)\}\}/g, (_, k) => String(vars[k] ?? `{{${k}}}`))
}

function cardVars(ev: Evidence, key: Key): Record<string, string | number> {
  if (key === 'map') {
    const b0 = ev.innerfeld_main.untrained.BARC.B0
    const m1 = ev.innerfeld_main.E.BARC.M1
    const map = ev.within_field_map
    return {
      b0: fmt(b0.rho_median, 2), b0ci: fmtCi(b0.rho_ci?.[0], b0.rho_ci?.[1]), m1: fmt(m1.rho_median, 2), m1ci: fmtCi(m1.rho_ci?.[0], m1.rho_ci?.[1]),
      prec: fmtPct(map.median_precision), prev: fmtPct(map.median_prevalence), lift: fmt(map.median_lift, 1),
    }
  }
  if (key === 'score') {
    const a0 = ev.stress_models.A0
    const al = ev.alarm
    return {
      n: a0.n ?? '–', a0: fmt(a0.pr_auc, 2), a0ci: fmtCi(a0.pr_auc_lo, a0.pr_auc_hi), raw: fmt(ev.stress_models.A_roh.pr_auc, 2), prev: fmt(a0.prevalence, 2),
      rec: fmt(al.alarm_recall, 2), prec: fmt(al.alarm_precision, 2), fpr: fmt(al.alarm_fpr, 2),
    }
  }
  const eu = ev.eu_cutoffs.find((c) => c.cutoff === '09-01')!
  return {
    n: fmtInt(eu.n), c: eu.countries, tag: ev.eu_meta.freeze, commit: ev.eu_meta.commit, v: fmt(eu.yearly_mean_spearman, 2),
    rho: fmt(eu.spearman.value, 2), rhoci: fmtCi(eu.spearman.lo, eu.spearman.hi), r2: fmt(eu.r2.value, 2), skill: fmt(eu.skill_vs_normal.value, 2),
    skillci: fmtCi(eu.skill_vs_normal.lo, eu.skill_vs_normal.hi), within: fmt(eu.within_year.value, 2), features: eu.n_features,
  }
}

export default function ModelCard() {
  const { t } = useTranslation()
  const content = useContent()
  const ev = useResource(getEvidence, 'evidence')
  const [tab, setTab] = useState<Key>('map')
  const cards = content.modelCards
  const card = cards[tab]
  const rowLabels = t('model.rows', { returnObjects: true }) as Record<string, string>
  const shared = t('model.sharedRules', { returnObjects: true }) as string[]

  const vars: Record<string, string | number> = ev.data ? cardVars(ev.data, tab) : {}
  const text = (s: string) => keepGreek(interpolate(s, vars))
  const metrics = ev.data ? interpolate(cards.metrics[tab], vars) : ''

  return (
    <>
      <section className="pt-36 pb-12">
        <Container>
          <Reveal>
            <p className="eyebrow mb-5">{t('model.eyebrow')}</p>
            <h1 className="max-w-[900px] text-balance text-[clamp(2.4rem,5.4vw,4.4rem)] leading-[1] tracking-[-0.04em] [hyphens:auto]">{t('model.title')}</h1>
            <p className="mt-6 max-w-[680px] text-[17px] leading-relaxed text-ink-2">{t('model.lede')}</p>
          </Reveal>
        </Container>
      </section>
      <section>
        <Container>
          {ev.status === 'loading' && <Skeleton className="h-[600px]" />}
          {ev.error && <ErrorNote error={ev.error} />}
          {ev.data && (
            <>
              <Tabs label={t('model.tabs')} value={tab} onChange={setTab} items={(['map', 'score', 'eu'] as Key[]).map((k) => ({ value: k, label: cards[k].name }))} />
              <AnimatePresence mode="wait">
                <motion.div key={tab} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} transition={{ duration: 0.3 }} className="mt-8 grid gap-5 lg:grid-cols-[1fr_340px]">
                  <article className="panel overflow-hidden">
                    <header className="flex flex-col gap-4 border-b border-[var(--line)] p-7 sm:flex-row sm:items-start sm:justify-between sm:p-9">
                      <div className="min-w-0 flex-1">
                        <h2 className="text-[clamp(1.8rem,3vw,2.4rem)]">{card.name}</h2>
                        <p className="mt-3 max-w-[560px] text-[15.5px] leading-relaxed text-ink-2">{card.oneLine}</p>
                      </div>
                      <div className="flex shrink-0 flex-col items-start gap-2 sm:items-end">
                        <StrengthBadge strength={STRENGTH[tab]} />
                        <span className="max-w-[280px] font-mono text-[11px] text-ink-3 sm:text-right">{keepGreek(card.status)}</span>
                      </div>
                    </header>
                    <dl>
                      {ROWS.map((k) => (
                        <div key={k} className="grid gap-2 border-b border-[var(--line)] px-7 py-5 last:border-0 sm:grid-cols-[180px_1fr] sm:px-9">
                          <dt className="eyebrow pt-0.5">{rowLabels[k]}</dt>
                          <dd className="text-pretty text-[14.5px] leading-relaxed text-ink">{k === 'metrics' ? keepGreek(metrics) : text(card[k])}</dd>
                        </div>
                      ))}
                    </dl>
                  </article>
                  <aside className="flex flex-col gap-5">
                    <div className="panel p-7">
                      <p className="eyebrow mb-5">{t('model.failures')}</p>
                      <ul className="flex flex-col gap-4">
                        {card.failures.map((f) => (
                          <li key={f} className="flex gap-3 text-[14px] leading-relaxed text-ink-2">
                            <span className="mt-2 size-1.5 shrink-0 rounded-full bg-rust" />
                            {text(f)}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div className="panel p-7">
                      <p className="eyebrow mb-4">{t('model.shared')}</p>
                      <ul className="flex flex-col gap-3 text-[13.5px] leading-relaxed text-ink-2">
                        {shared.map((s) => <li key={s}>{s}</li>)}
                      </ul>
                    </div>
                  </aside>
                </motion.div>
              </AnimatePresence>
            </>
          )}
        </Container>
      </section>
    </>
  )
}
