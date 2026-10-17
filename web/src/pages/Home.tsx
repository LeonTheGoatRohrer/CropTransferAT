import { motion, useReducedMotion } from 'motion/react'
import { ArrowRight, ArrowUpRight } from 'lucide-react'
import { Link } from 'react-router'
import type { Evidence, FieldAnalysis } from '../api/types'
import { LineCi, Strip } from '../components/charts/Stats'
import { SeasonChart } from '../components/charts/SeasonChart'
import { FieldOutline } from '../components/field/FieldOutline'
import { HeroField } from '../components/field/HeroField'
import { PixelField } from '../components/field/PixelField'
import { StrengthBadge, type Strength } from '../components/ui/Badge'
import { ButtonLink } from '../components/ui/Button'
import { Metric } from '../components/ui/Metric'
import { Reveal } from '../components/ui/Reveal'
import { Container, SectionHeader, Source } from '../components/ui/Section'
import { ErrorNote, Skeleton } from '../components/ui/States'
import { EXPERIMENTS } from '../data/content/project'
import { tokens } from '../lib/color'
import { lastCompleteDekad } from '../lib/dekads'
import { fmt, fmtArea, fmtSigned } from '../lib/format'
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
      {hero && <FieldToSignal field={hero} />}
      {evidence.data && <Claims ev={evidence.data} />}
      {evidence.data && <ProofPreview ev={evidence.data} />}
      <WhatFailed />
      <AustriaBand />
      <ClosingCta />
    </>
  )
}

/* ------------------------------------------------------------------ */

function Hero({ field, error }: { field?: FieldAnalysis; error?: Error }) {
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
            <span className="inline-block h-px w-8 bg-maize" /> Maize · Sentinel-2 · BWKI Austria
          </motion.p>
          <motion.h1 {...rise(0.08)} className="text-balance text-[clamp(2.9rem,6vw,5.1rem)] font-semibold leading-[0.96] tracking-[-0.045em]">
            Find the weak zones <span className="text-maize">before harvest.</span>
          </motion.h1>
          <motion.p {...rise(0.18)} className="mt-7 max-w-[540px] text-pretty text-[18px] leading-relaxed text-ink-2">
            CropTransfer AT turns Sentinel-2 time series, weather and soil into an early warning for maize fields — and checks every
            claim against yields measured by the combine.
          </motion.p>
          <motion.div {...rise(0.28)} className="mt-10 flex flex-wrap gap-3">
            <ButtonLink to="/analyse" size="lg" icon={<ArrowRight className="size-4" />}>
              Analyse a field
            </ButtonLink>
            <ButtonLink to="/evidence" size="lg" variant="secondary">
              See the evidence
            </ButtonLink>
          </motion.div>
          <motion.dl {...rise(0.38)} className="mt-14 grid max-w-[520px] grid-cols-3 gap-6 border-t border-[var(--line)] pt-6">
            {[
              ['365', 'measured maize field-years'],
              ['10 m', 'Sentinel-2 cells, 21 dekads'],
              ['0', 'Austrian values in the frozen models'],
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

function FieldToSignal({ field }: { field: FieldAnalysis }) {
  const px = field.pixels!
  const ndvi = field.satellite.indices.ndvi ?? []
  const cutoff = lastCompleteDekad(9, 1)
  const steps = [
    {
      k: 'Field',
      t: `${fmtArea(field.area_m2)} of maize`,
      d: 'A polygon and a season. This one is a real research field in Maryland, 2018.',
      v: <FieldOutline geometry={field.geometry} className="h-36 w-full" />,
    },
    {
      k: 'Pixels',
      t: `${px.n_cells} cells × 10 m`,
      d: `${field.satellite.n_scenes} Sentinel-2 scenes; ${field.satellite.n_clear_scenes} clear enough to use.`,
      v: <PixelField pixels={px} mode="season" dekad={12} maxHeight={144} interactive={false} />,
    },
    {
      k: 'Curve',
      t: `${field.satellite.n_observed_dekads} of 21 dekads`,
      d: 'Median NDVI per 10-day step, set against the healthy reference band.',
      v: <SeasonChart values={ndvi} reference={field.reference.ndvi} height={144} compact showPhases={false} showShortfall={false} />,
    },
    {
      k: 'Signal',
      t: `Stress score ${fmtSigned(field.stress?.score, 3)}`,
      d: `Shortfall below the reference by 1 September. Most of it in ${field.stress?.main_phase ?? 'July'}.`,
      v: <SeasonChart values={ndvi} reference={field.reference.ndvi} height={144} compact showPhases cutoff={cutoff} color={tokens.rust} />,
    },
    {
      k: 'Map',
      t: `Flagged quarter: ${Math.round(px.precision_weak * 100)} % hit`,
      d: 'The lowest NDVI quarter in July–August, checked against the combine yield map.',
      v: <PixelField pixels={px} mode="weak" maxHeight={144} interactive={false} />,
    },
  ]
  return (
    <section className="py-24 sm:py-32">
      <Container>
        <SectionHeader
          eyebrow="How a field becomes data"
          title="From a field to a signal, in five steps."
          lede="The same field from the top of this page, step by step. Nothing here is illustrative: every panel is computed from this field’s own observations."
        />
        <div className="mt-16 grid gap-px overflow-hidden rounded-[var(--radius-panel)] border border-[var(--line)] bg-[var(--line)] sm:grid-cols-2 lg:grid-cols-5">
          {steps.map((s, i) => (
            <Reveal key={s.k} delay={i * 0.08} className="flex flex-col bg-soil-900 p-5">
              <div className="flex items-center justify-between">
                <span className="eyebrow text-maize">{s.k}</span>
                {i < steps.length - 1 && <ArrowRight className="hidden size-3.5 text-ink-4 lg:block" />}
              </div>
              <div className="my-6 flex h-36 items-center justify-center">{s.v}</div>
              <p className="font-display text-[17px] font-semibold tracking-[-0.015em]">{s.t}</p>
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
  const barc = ev.innerfeld_main.untrained.BARC.B0
  const eu = ev.eu_cutoffs.find((c) => c.cutoff === '09-01')!
  const a0 = ev.stress_models.A0
  const noT4 = ev.stress_sensitivity['A0|ohne_T4']
  const claims: { strength: Strength; q: string; metric: React.ReactNode; body: string; to: string }[] = [
    {
      strength: 'robust',
      q: 'Which part of the field falls behind?',
      metric: <Metric label="Median ρ, NDVI vs pixel yield" value={barc.rho_median} ci={barc.rho_ci} n={`${barc.n_fy} field-years`} size="lg" tone="sage" />,
      body: `Within a field, mid-summer NDVI ranks the 10-m cells by yield. Positive in all ${barc.n_fy} BARC field-years; needs no training.`,
      to: '/evidence#within-field',
    },
    {
      strength: 'certain-small',
      q: 'Which years turn out worse for a region?',
      metric: <Metric label="Spearman ρ on 1 September" value={eu.spearman.value} ci={[eu.spearman.lo, eu.spearman.hi]} n={`${eu.n.toLocaleString('en-US')} region-years`} size="lg" tone="water" />,
      body: `EU regional model, 16 countries, Austria excluded and frozen. The signal is small (skill ${fmt(eu.skill_vs_normal.value, 2)} over a normal year) but certain.`,
      to: '/evidence#regional',
    },
    {
      strength: 'limited',
      q: 'Which whole field is at risk?',
      metric: <Metric label="PR-AUC, stress-score risk model" value={a0.pr_auc} ci={[a0.pr_auc_lo, a0.pr_auc_hi]} n={`${a0.n} field-years · chance ${fmt(a0.prevalence, 2)}`} size="lg" tone="maize" />,
      body: `Clearly above chance, but partly driven by late-sown organic plots. Without them: ${fmt(noT4?.pr_auc, 2)} against a chance level of ${fmt(noT4?.prevalence, 2)}.`,
      to: '/evidence#field-level',
    },
  ]
  return (
    <section className="py-24 sm:py-28">
      <Container>
        <SectionHeader
          eyebrow="What the system can say"
          title="Three questions, three levels of certainty."
          lede="Each answer comes with its confidence interval, its sample size and an honest label for how far it carries."
        />
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

function ProofPreview({ ev }: { ev: Evidence }) {
  const barc = ev.innerfeld_per_fy.filter((r) => r.model === 'B0' && r.scheme === 'untrained' && r.rho != null)
  const sites = [
    { key: 'BARC', label: 'BARC', sub: 'Maryland, USA', color: tokens.sage },
    { key: 'KAYAD', label: 'Kayad', sub: 'Po valley, Italy', color: tokens.maize },
    { key: 'COLORADO', label: 'Akron', sub: 'Colorado, USA', color: tokens.water },
  ]
  const groups = sites.map((s) => {
    const vals = barc.filter((r) => r.site === s.key)
    const summ = ev.innerfeld_main.untrained[s.key]?.B0
    return { label: s.label, sub: `${s.sub} · ${vals.length} field-years`, color: s.color, values: vals.map((v) => ({ v: v.rho as number, title: `${v.fy_key.split('|')[1].split(':')[1]} · ${v.year}` })), median: summ?.rho_median }
  })
  const cut = ev.eu_cutoffs
  return (
    <section className="py-24 sm:py-28">
      <Container>
        <SectionHeader
          eyebrow="Evidence preview"
          title="Tested on data the model never saw."
          lede="Left: each dot is one field-year, comparing the NDVI map with the measured yield map. Right: how early the EU model knows something, with 95 % bands."
          aside={
            <ButtonLink to="/evidence" variant="secondary" icon={<ArrowRight className="size-4" />}>
              All benchmarks
            </ButtonLink>
          }
        />
        <div className="mt-14 grid gap-5 lg:grid-cols-2">
          <Reveal className="panel p-6">
            <p className="eyebrow">Within-field rank correlation, per field-year</p>
            <div className="mt-6">
              <Strip groups={groups} domain={[-0.2, 1]} xLabel="Spearman ρ" reference={0} />
            </div>
            <Source className="mt-4">results/2026-10-17_innerfeld/per_fy.csv · rule B0, untrained</Source>
          </Reveal>
          <Reveal className="panel p-6" delay={0.1}>
            <p className="eyebrow">EU regional model by forecast date</p>
            <div className="mt-6">
              <LineCi
                categories={cut.map((c) => { const [m, d] = c.cutoff.split('-'); return `${Number(d)} ${['', '', '', '', '', '', 'Jun', 'Jul', 'Aug', 'Sep'][Number(m)]}` })}
                yDomain={[-0.1, 0.5]}
                series={[
                  { label: 'Spearman ρ', color: tokens.water, values: cut.map((c) => ({ v: c.spearman.value, lo: c.spearman.lo, hi: c.spearman.hi })) },
                  { label: 'Skill vs normal year', color: tokens.maize, values: cut.map((c) => ({ v: c.skill_vs_normal.value, lo: c.skill_vs_normal.lo, hi: c.skill_vs_normal.hi })) },
                ]}
              />
            </div>
            <Source className="mt-4">results/2026-10-16_cybench_eu/metrics.json · leave-one-country-out, n = 8 371</Source>
          </Reveal>
        </div>
      </Container>
    </section>
  )
}

/* ------------------------------------------------------------------ */

function WhatFailed() {
  const failed = EXPERIMENTS.filter((e) => e.status === 'failed')
  return (
    <section className="py-24 sm:py-28">
      <Container>
        <SectionHeader
          eyebrow="Negative results"
          title="What did not work — reported in full."
          lede="Every criterion was written down before the run and never changed afterwards. A failed approach rules out a direction; that is progress too."
        />
        <div className="mt-14 grid gap-px overflow-hidden rounded-[var(--radius-panel)] border border-[var(--line)] bg-[var(--line)] md:grid-cols-2 lg:grid-cols-4">
          {failed.slice(0, 4).map((e, i) => (
            <Reveal key={e.id} delay={i * 0.06} className="flex flex-col bg-soil-900 p-6">
              <StrengthBadge strength="failed" />
              <h3 className="mt-5 text-[18px] leading-snug">{e.title}</h3>
              <p className="mt-3 flex-1 text-[13.5px] leading-relaxed text-ink-3">{e.result}</p>
              <p className="mt-5 font-mono text-[12px] text-ink-2">{e.numbers[0].label}: {e.numbers[0].value}</p>
            </Reveal>
          ))}
        </div>
        <Link to="/method#experiments" className="link-underline mt-6 inline-flex items-center gap-1.5 text-[14px] text-ink-2 hover:text-ink">
          All {EXPERIMENTS.length} experiments in order <ArrowRight className="size-3.5" />
        </Link>
      </Container>
    </section>
  )
}

function AustriaBand() {
  return (
    <section className="py-16">
      <Container>
        <Reveal className="panel grain relative overflow-hidden p-8 sm:p-12">
          <div className="grid gap-10 lg:grid-cols-[1.2fr_1fr] lg:items-center">
            <div>
              <p className="eyebrow mb-4">The Austria rule</p>
              <h2 className="text-balance text-[clamp(1.8rem,3.4vw,2.6rem)]">Austria is the exam, not the textbook.</h2>
              <p className="mt-5 max-w-[560px] text-pretty text-[16px] leading-relaxed text-ink-2">
                Models learn only from fields abroad. Austrian yields, parcels and statistics stayed closed for training, features, thresholds
                and model choice. The first test ran once under rules frozen in advance: good and bad years rank correctly (ρ ≈ 0.5), single
                sites and fields do not yet.
              </p>
            </div>
            <ol className="relative flex flex-col gap-5 border-l border-[var(--line-strong)] pl-6">
              {[
                ['Done', 'Train on US and EU data only'],
                ['Done', 'Freeze models with checksums (freeze-cybench-1, freeze-at-1)'],
                ['Done', 'Run the frozen protocol once: years rank in Upper Austria and across states'],
                ['Next', 'Collect Austrian field yields for a field-level test'],
              ].map(([s, t]) => (
                <li key={t} className="relative">
                  <span className={`absolute -left-[29px] top-1.5 size-2.5 rounded-full ${s === 'Done' ? 'bg-sage' : s === 'Now' ? 'bg-maize ring-4 ring-maize/20' : 'bg-ink-4'}`} />
                  <p className="font-mono text-[10.5px] uppercase tracking-[0.12em] text-ink-3">{s}</p>
                  <p className="text-[15px] text-ink">{t}</p>
                </li>
              ))}
            </ol>
          </div>
        </Reveal>
      </Container>
    </section>
  )
}

function ClosingCta() {
  return (
    <section className="pt-20">
      <Container className="text-center">
        <Reveal>
          <h2 className="mx-auto max-w-[760px] text-balance text-[clamp(2.2rem,5vw,3.8rem)]">Open a real field and watch it turn into data.</h2>
          <p className="mx-auto mt-5 max-w-[520px] text-[16px] text-ink-2">Five prepared field-years from the training sites, with their measured outcome — or draw your own.</p>
          <div className="mt-9 flex justify-center gap-3">
            <ButtonLink to="/analyse" size="lg" icon={<ArrowRight className="size-4" />}>
              Analyse a field
            </ButtonLink>
            <ButtonLink to="/model" size="lg" variant="secondary">
              Read the model card
            </ButtonLink>
          </div>
        </Reveal>
      </Container>
    </section>
  )
}
