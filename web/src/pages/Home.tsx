import { motion, useReducedMotion } from 'motion/react'
import { ArrowRight, ArrowUpRight } from 'lucide-react'
import type { ReactNode } from 'react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router'
import type { Evidence, FieldAnalysis } from '../api/types'
import { SeasonChart } from '../components/charts/SeasonChart'
import { FieldOutline } from '../components/field/FieldOutline'
import { HeroField } from '../components/field/HeroField'
import { PixelField } from '../components/field/PixelField'
import { StrengthBadge, type Strength } from '../components/ui/Badge'
import { ButtonLink } from '../components/ui/Button'
import { Metric } from '../components/ui/Metric'
import { Reveal } from '../components/ui/Reveal'
import { Container, SectionHeader } from '../components/ui/Section'
import { ErrorNote, Skeleton } from '../components/ui/States'
import { useContent } from '../i18n'
import { NDVI_LEGEND, tokens } from '../lib/color'
import { lastCompleteDekad, phaseName } from '../lib/dekads'
import { fmt, fmtArea, fmtInt, fmtSigned } from '../lib/format'
import { useResource } from '../lib/useResource'
import { getEvidence } from '../services/evidenceService'
import { getPreparedFields } from '../services/fieldService'

const HERO_FIELD = 'barc-2018'

export default function Home() {
  const fields = useResource(getPreparedFields, 'fields')
  const evidence = useResource(getEvidence, 'evidence')
  const hero = fields.data?.fields.find((f) => f.id === HERO_FIELD)

  return (
    <>
      <Hero field={hero} error={fields.error} />
      <Params />
      {hero && <FieldToSignal field={hero} />}
      {evidence.data && <Claims ev={evidence.data} />}
      <AustriaBand />
      <ReadOn />
      <ClosingCta />
    </>
  )
}

/* ------------------------------------------------------------------ */

function Hero({ field, error }: { field?: FieldAnalysis; error?: Error }) {
  const { t } = useTranslation()
  const reduce = useReducedMotion()
  const rise = (d: number) => ({
    initial: reduce ? false : { opacity: 0, y: 22 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.9, delay: d, ease: [0.22, 1, 0.36, 1] as const },
  })
  return (
    <section className="relative overflow-hidden pt-28 pb-20 sm:pt-36 lg:pb-28">
      <div aria-hidden className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute -top-40 right-[-10%] h-[620px] w-[620px] rounded-full bg-[radial-gradient(closest-side,rgba(230,180,80,0.10),transparent)]" />
        <div className="absolute bottom-[-30%] left-[-15%] h-[560px] w-[760px] rounded-full bg-[radial-gradient(closest-side,rgba(85,160,90,0.08),transparent)]" />
      </div>
      <Container className="grid items-center gap-14 lg:grid-cols-[1.02fr_1fr] lg:gap-16">
        <div>
          <motion.p {...rise(0)} className="eyebrow mb-6 flex items-center gap-3">
            <span className="inline-block h-px w-8 bg-maize" /> {t('home.eyebrow')}
          </motion.p>
          <motion.h1 {...rise(0.08)} className="text-balance text-[clamp(2.5rem,4.9vw,4.1rem)] font-semibold leading-[1] tracking-[-0.045em] [hyphens:auto]">
            {t('home.h1a')} <span className="text-maize">{t('home.h1b')}</span>
          </motion.h1>
          <motion.p {...rise(0.18)} className="mt-6 max-w-[540px] text-pretty text-[clamp(1.05rem,1.6vw,1.25rem)] leading-snug text-ink-2">
            {t('home.lede')}
          </motion.p>
          <motion.div {...rise(0.28)} className="mt-10 flex flex-wrap gap-3">
            <ButtonLink to="/analyse" size="lg" icon={<ArrowRight className="size-4" />}>
              {t('home.ctaAnalyse')}
            </ButtonLink>
            <ButtonLink to="/evidence" size="lg" variant="secondary">
              {t('home.ctaEvidence')}
            </ButtonLink>
          </motion.div>
          <motion.dl {...rise(0.38)} className="mt-14 grid max-w-[540px] grid-cols-3 gap-6 border-t border-[var(--line)] pt-6">
            {[
              [fmtInt(365), t('home.stat1')],
              ['10 m', t('home.stat2')],
              ['0', t('home.stat3')],
            ].map(([v, l]) => (
              <div key={l}>
                <dt className="sr-only">{l}</dt>
                <dd className="font-display text-[28px] font-semibold tracking-[-0.03em]">{v}</dd>
                <dd className="mt-1 text-[12.5px] leading-snug text-ink-3">{l}</dd>
              </div>
            ))}
          </motion.dl>
        </div>
        <motion.div initial={reduce ? false : { opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 1.1, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}>
          {field ? <HeroField field={field} /> : error ? <ErrorNote error={error} /> : <Skeleton className="h-[520px]" />}
        </motion.div>
      </Container>
    </section>
  )
}

/* ------------------------------------------------------------------ */

type Param = { name: string; q: string; body: string; formula: string }

/** Plain-language explainer of the measures the whole site builds on. */
function Params() {
  const { t } = useTranslation()
  const items = t('home.params.items', { returnObjects: true }) as Param[]
  const [ndvi, ...rest] = items
  const gradient = `linear-gradient(90deg, ${NDVI_LEGEND.map((s) => `${s.c} ${s.v * 100}%`).join(', ')})`
  return (
    <section className="py-20 sm:py-24">
      <Container>
        <SectionHeader eyebrow={t('home.params.eyebrow')} title={t('home.params.title')} lede={t('home.params.lede')} />
        <div className="mt-14 grid gap-5 lg:grid-cols-3">
          <Reveal className="panel flex flex-col p-7 lg:row-span-2">
            <p className="eyebrow text-maize">{t('home.params.main')}</p>
            <h3 className="mt-4 font-display text-[34px] font-semibold tracking-[-0.03em]">{ndvi.name}</h3>
            <p className="mt-1 text-[17px] text-ink">{ndvi.q}</p>
            <p className="mt-4 text-pretty text-[14.5px] leading-relaxed text-ink-2">{ndvi.body}</p>
            {ndvi.formula && <p className="mt-6 rounded-lg border border-[var(--line)] bg-white/[0.02] px-4 py-3 font-mono text-[13px] text-ink">{ndvi.formula}</p>}
            <div className="mt-auto pt-8">
              <div aria-hidden className="h-3 rounded-full" style={{ background: gradient }} />
              <div className="mt-2 flex justify-between font-mono text-[11.5px] text-ink-3">
                <span>{fmt(0, 1)} · {t('home.params.legendLow')}</span>
                <span>{fmt(1, 1)}</span>
              </div>
              <p className="mt-1 text-right font-mono text-[11.5px] text-ink-3">{t('home.params.legendHigh')} ≈ {fmt(0.7, 1)}–{fmt(0.9, 1)}</p>
            </div>
          </Reveal>
          {rest.map((p, i) => (
            <Reveal key={p.name} delay={(i + 1) * 0.06} className="panel flex flex-col p-6">
              <p className="font-mono text-[12px] uppercase tracking-[0.1em] text-maize">{p.name}</p>
              <h3 className="mt-3 text-[18px] leading-snug">{p.q}</h3>
              <p className="mt-3 text-pretty text-[13.5px] leading-relaxed text-ink-3">{p.body}</p>
            </Reveal>
          ))}
        </div>
      </Container>
    </section>
  )
}

/* ------------------------------------------------------------------ */

function FieldToSignal({ field }: { field: FieldAnalysis }) {
  const { t } = useTranslation()
  const px = field.pixels!
  const ndvi = field.satellite.indices.ndvi ?? []
  const cutoff = lastCompleteDekad(9, 1)
  const steps: { k: string; title: string; d: string; v: ReactNode }[] = [
    { k: t('home.steps.field'), title: t('home.steps.fieldT', { area: fmtArea(field.area_m2) }), d: t('home.steps.fieldD'), v: <FieldOutline geometry={field.geometry} className="h-36 w-full" /> },
    {
      k: t('home.steps.pixels'),
      title: t('home.steps.pixelsT', { n: px.n_cells }),
      d: t('home.steps.pixelsD', { n: field.satellite.n_scenes, c: field.satellite.n_clear_scenes }),
      v: <PixelField pixels={px} mode="season" dekad={12} maxHeight={144} interactive={false} />,
    },
    {
      k: t('home.steps.curve'),
      title: t('home.steps.curveT', { n: field.satellite.n_observed_dekads }),
      d: t('home.steps.curveD'),
      v: <SeasonChart values={ndvi} reference={field.reference.ndvi} height={144} compact showPhases={false} showShortfall={false} />,
    },
    {
      k: t('home.steps.signal'),
      title: t('home.steps.signalT', { v: fmtSigned(field.stress?.score, 3) }),
      d: t('home.steps.signalD', { phase: phaseName(field.stress?.main_phase ?? 'July') }),
      v: <SeasonChart values={ndvi} reference={field.reference.ndvi} height={144} compact showPhases cutoff={cutoff} color={tokens.rust} />,
    },
    {
      k: t('home.steps.map'),
      title: t('home.steps.mapT', { v: `${fmt(px.precision_weak * 100, 0)} %` }),
      d: t('home.steps.mapD'),
      v: <PixelField pixels={px} mode="weak" maxHeight={144} interactive={false} />,
    },
  ]
  return (
    <section className="py-24 sm:py-32">
      <Container>
        <SectionHeader eyebrow={t('home.steps.eyebrow')} title={t('home.steps.title')} lede={t('home.steps.lede')} />
        <div className="mt-16 grid gap-px overflow-hidden rounded-[var(--radius-panel)] border border-[var(--line)] bg-[var(--line)] sm:grid-cols-2 lg:grid-cols-5">
          {steps.map((s, i) => (
            <Reveal key={s.k} delay={i * 0.08} className="flex flex-col bg-soil-900 p-5">
              <div className="flex items-center justify-between">
                <span className="eyebrow text-maize">{s.k}</span>
                {i < steps.length - 1 && <ArrowRight className="hidden size-3.5 text-ink-4 lg:block" />}
              </div>
              <div className="my-6 flex h-36 items-center justify-center">{s.v}</div>
              <p className="font-display text-[17px] font-semibold tracking-[-0.015em]">{s.title}</p>
              <p className="mt-2 text-[13.5px] leading-relaxed text-ink-3">{s.d}</p>
            </Reveal>
          ))}
        </div>
      </Container>
    </section>
  )
}

/* ------------------------------------------------------------------ */

function Claims({ ev }: { ev: Evidence }) {
  const { t } = useTranslation()
  const barc = ev.innerfeld_main.untrained.BARC.B0
  const eu = ev.eu_cutoffs.find((c) => c.cutoff === '09-01')!
  const a0 = ev.stress_models.A0
  const noT4 = ev.stress_sensitivity['A0|ohne_T4']
  const claims: { strength: Strength; q: string; metric: ReactNode; body: string; to: string }[] = [
    {
      strength: 'robust',
      q: t('home.claims.q1'),
      metric: <Metric label={t('home.claims.m1')} value={barc.rho_median} ci={barc.rho_ci} n={t('home.claims.nFy', { n: barc.n_fy })} size="lg" tone="sage" />,
      body: t('home.claims.b1', { n: barc.n_fy }),
      to: '/evidence#within-field',
    },
    {
      strength: 'certain-small',
      q: t('home.claims.q2'),
      metric: <Metric label={t('home.claims.m2')} value={eu.spearman.value} ci={[eu.spearman.lo, eu.spearman.hi]} n={t('home.claims.nRy', { n: fmtInt(eu.n) })} size="lg" tone="water" />,
      body: t('home.claims.b2', { skill: fmt(eu.skill_vs_normal.value, 2) }),
      to: '/evidence#regional',
    },
    {
      strength: 'limited',
      q: t('home.claims.q3'),
      metric: <Metric label={t('home.claims.m3')} value={a0.pr_auc} ci={[a0.pr_auc_lo, a0.pr_auc_hi]} n={t('home.claims.nFyChance', { n: a0.n, c: fmt(a0.prevalence, 2) })} size="lg" tone="maize" />,
      body: t('home.claims.b3', { v: fmt(noT4?.pr_auc, 2), c: fmt(noT4?.prevalence, 2) }),
      to: '/evidence#field-level',
    },
  ]
  return (
    <section className="py-24 sm:py-28">
      <Container>
        <SectionHeader eyebrow={t('home.claims.eyebrow')} title={t('home.claims.title')} lede={t('home.claims.lede')} />
        <div className="mt-14 grid gap-5 lg:grid-cols-3">
          {claims.map((c, i) => (
            <Reveal key={c.q} delay={i * 0.08}>
              <Link to={c.to} className="panel group flex h-full flex-col p-7 transition-[transform,box-shadow,border-color] duration-300 hover:-translate-y-1 hover:border-[var(--line-strong)] hover:shadow-[var(--shadow-lift)]">
                <div className="flex items-center justify-between">
                  <StrengthBadge strength={c.strength} />
                  <ArrowUpRight className="size-4 text-ink-4 transition group-hover:text-ink" />
                </div>
                <h3 className="mt-6 text-[22px] leading-tight">{c.q}</h3>
                <div className="mt-8">{c.metric}</div>
                <p className="mt-6 text-pretty text-[14px] leading-relaxed text-ink-2">{c.body}</p>
              </Link>
            </Reveal>
          ))}
        </div>
      </Container>
    </section>
  )
}

/* ------------------------------------------------------------------ */

function AustriaBand() {
  const { t } = useTranslation()
  const steps: ['done' | 'now' | 'next', string][] = [
    ['done', t('home.austria.s1')],
    ['done', t('home.austria.s2')],
    ['done', t('home.austria.s3')],
    ['next', t('home.austria.s4')],
  ]
  return (
    <section className="py-16">
      <Container>
        <Reveal className="panel grain relative overflow-hidden p-8 sm:p-12">
          <div className="grid gap-10 lg:grid-cols-[1.2fr_1fr] lg:items-center">
            <div>
              <p className="eyebrow mb-4">{t('home.austria.eyebrow')}</p>
              <h2 className="text-balance text-[clamp(1.8rem,3.4vw,2.6rem)]">{t('home.austria.title')}</h2>
              <p className="mt-5 max-w-[560px] text-pretty text-[16px] leading-relaxed text-ink-2">{t('home.austria.body')}</p>
            </div>
            <ol className="relative flex flex-col gap-5 border-l border-[var(--line-strong)] pl-6">
              {steps.map(([s, txt]) => (
                <li key={txt} className="relative">
                  <span className={`absolute -left-[29px] top-1.5 size-2.5 rounded-full ${s === 'done' ? 'bg-sage' : s === 'now' ? 'bg-maize ring-4 ring-maize/20' : 'bg-ink-4'}`} />
                  <p className="font-mono text-[10.5px] uppercase tracking-[0.12em] text-ink-3">{t(`home.austria.${s}`)}</p>
                  <p className="text-[15px] text-ink">{txt}</p>
                </li>
              ))}
            </ol>
          </div>
        </Reveal>
      </Container>
    </section>
  )
}

function ReadOn() {
  const { t } = useTranslation()
  const { experiments } = useContent()
  const nFailed = experiments.filter((e) => e.status === 'failed').length
  const links = [
    { to: '/evidence', h: t('home.more.evidence'), d: t('home.more.evidenceD') },
    { to: '/method#experiments', h: t('home.more.failed'), d: t('home.more.failedD', { n: nFailed }) },
    { to: '/konzept', h: t('home.more.concept'), d: t('home.more.conceptD') },
  ]
  return (
    <section className="py-16">
      <Container>
        <p className="eyebrow mb-5">{t('home.more.eyebrow')}</p>
        <div className="grid gap-px overflow-hidden rounded-[var(--radius-panel)] border border-[var(--line)] bg-[var(--line)] md:grid-cols-3">
          {links.map((l) => (
            <Link key={l.to} to={l.to} className="group flex flex-col bg-soil-900 p-6 transition-colors hover:bg-white/[0.03]">
              <span className="flex items-center justify-between font-display text-[17px] font-semibold">
                {l.h} <ArrowUpRight className="size-4 text-ink-4 transition group-hover:text-ink" />
              </span>
              <span className="mt-2 text-[13.5px] leading-relaxed text-ink-3">{l.d}</span>
            </Link>
          ))}
        </div>
      </Container>
    </section>
  )
}

function ClosingCta() {
  const { t } = useTranslation()
  return (
    <section className="pt-20">
      <Container className="text-center">
        <Reveal>
          <h2 className="mx-auto max-w-[760px] text-balance text-[clamp(2.2rem,5vw,3.8rem)]">{t('home.closing.title')}</h2>
          <p className="mx-auto mt-5 max-w-[520px] text-[16px] text-ink-2">{t('home.closing.body')}</p>
          <div className="mt-9 flex flex-wrap justify-center gap-3">
            <ButtonLink to="/analyse" size="lg" icon={<ArrowRight className="size-4" />}>
              {t('home.ctaAnalyse')}
            </ButtonLink>
            <ButtonLink to="/model" size="lg" variant="secondary">
              {t('home.closing.model')}
            </ButtonLink>
          </div>
        </Reveal>
      </Container>
    </section>
  )
}
