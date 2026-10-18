import { motion, useReducedMotion } from 'motion/react'
import { ArrowRight, ArrowUpRight, Gift, PenLine, Sprout, TrendingUp } from 'lucide-react'
import { Link } from 'react-router'
import type { FieldAnalysis } from '../api/types'
import { HeroField } from '../components/field/HeroField'
import { ButtonLink } from '../components/ui/Button'
import { Reveal } from '../components/ui/Reveal'
import { Container, SectionHeader } from '../components/ui/Section'
import { ErrorNote, Skeleton } from '../components/ui/States'
import { useResource } from '../lib/useResource'
import { getPreparedFields } from '../services/fieldService'

const HERO_FIELD = 'barc-2018'

export default function Home() {
  const fields = useResource(getPreparedFields, 'fields')
  const hero = fields.data?.fields.find((f) => f.id === HERO_FIELD)
  return (
    <>
      <Hero field={hero} error={fields.error} />
      <GiveGet />
      <HowItWorks />
      <WhyAustria />
      <Models />
      <ClosingCta />
    </>
  )
}

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
            <span className="inline-block h-px w-8 bg-maize" /> Für Maisbäuerinnen und -bauern in Österreich
          </motion.p>
          <motion.h1 {...rise(0.08)} className="text-balance text-[clamp(2.9rem,6vw,5.1rem)] font-semibold leading-[0.96] tracking-[-0.045em]">
            Erträge teilen. <span className="text-maize">Bessere Prognose erhalten.</span>
          </motion.h1>
          <motion.p {...rise(0.18)} className="mt-7 max-w-[540px] text-pretty text-[18px] leading-relaxed text-ink-2">
            Zeichnen Sie Ihr Maisfeld ein und sagen Sie uns, was es in den letzten Jahren gebracht hat. Sie sehen sofort, wie dieses
            Jahr im Vergleich zu Ihrer üblichen Ernte liegt. Wir bekommen die österreichischen Felddaten, die eine Frühwarnung per
            Satellit hier braucht.
          </motion.p>
          <motion.div {...rise(0.28)} className="mt-10 flex flex-wrap gap-3">
            <ButtonLink to="/contribute" size="lg" icon={<ArrowRight className="size-4" />}>
              Feld eintragen
            </ButtonLink>
            <ButtonLink to="/model" size="lg" variant="secondary">
              Was die Modelle tun
            </ButtonLink>
          </motion.div>
          <motion.div {...rise(0.38)} className="mt-12 flex max-w-[560px] flex-col gap-6 border-t border-[var(--line)] pt-6">
            <dl className="grid grid-cols-3 gap-4">
              {[
                ['365', 'Feld-Jahre mit gemessenem Ertrag', '19 Saisonen, 1989–2023 · im Schnitt 19 pro Saison'],
                ['28 000', 'Ertragszellen (10 × 10 m)', 'ungefähr, in 54 Feld-Jahren (Karten und Punkte)'],
                ['7 700', 'Satellitenkurven', 'ungefähr, 365 Feld-Jahre × 21 Zehn-Tage-Schritte'],
              ].map(([v, l, d]) => (
                <div key={l}>
                  <dd className="whitespace-nowrap font-display text-[24px] font-semibold tracking-[-0.03em]">{v}</dd>
                  <dt className="mt-1 text-[12.5px] leading-snug text-ink-2">{l}</dt>
                  <dd className="mt-1 text-[11px] leading-snug text-ink-4">{d}</dd>
                </div>
              ))}
            </dl>
                        <div className="flex items-start gap-4 rounded-xl border border-maize/25 bg-maize/[0.05] p-4">
              <p className="font-display text-[34px] font-semibold leading-none tracking-[-0.03em] text-maize">0</p>
              <div>
              <p className="text-[14px] font-medium leading-snug text-ink">österreichische Werte im Training</p>
              <p className="mt-1 text-[12px] leading-snug text-ink-3">Österreich ist nur der Schlusstest, weil es noch keine Ertragsdaten auf Feldebene gibt. Ihre Erntedaten können das ändern.</p>
              </div>
            </div>
          </motion.div>
        </div>
        <motion.div initial={reduce ? false : { opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 1.1, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}>
          {field ? <HeroField field={field} /> : error ? <ErrorNote error={error} /> : <Skeleton className="h-[520px]" />}
        </motion.div>
      </Container>
    </section>
  )
}

function GiveGet() {
  const cols = [
    {
      icon: <Gift className="size-5" />,
      title: 'Sie geben',
      items: ['Den Umriss eines Maisfelds', 'Seinen Ertrag in den letzten Jahren, soweit Sie ihn kennen', 'Die Ernte dieses Jahres oder Ihre bisherige Schätzung'],
    },
    {
      icon: <TrendingUp className="size-5" />,
      title: 'Sie bekommen',
      items: ['Wie dieses Jahr im Vergleich zu Ihrem üblichen Ertrag liegt', 'Eine Prognose, die mit jedem weiteren Feld besser wird', 'Satelliten- und Wetteranalyse Ihres Felds, sobald verfügbar'],
    },
  ]
  return (
    <section className="py-16 sm:py-20">
      <Container className="grid gap-5 md:grid-cols-2">
        {cols.map((c, i) => (
          <Reveal key={c.title} delay={i * 0.08} className="panel p-8">
            <div className="flex items-center gap-3 text-maize">
              {c.icon}
              <h2 className="text-[24px]">{c.title}</h2>
            </div>
            <ul className="mt-6 flex flex-col gap-3.5">
              {c.items.map((t) => (
                <li key={t} className="flex gap-3 text-[15.5px] leading-snug text-ink-2">
                  <span className="mt-2 size-1.5 shrink-0 rounded-full bg-maize" />
                  {t}
                </li>
              ))}
            </ul>
          </Reveal>
        ))}
      </Container>
    </section>
  )
}

function HowItWorks() {
  const steps = [
    { icon: <PenLine className="size-5" />, t: 'Feld einzeichnen', d: 'Suchen Sie Ihren Ort auf der Satellitenkarte und klicken Sie die Ecken des Felds an.' },
    { icon: <Sprout className="size-5" />, t: 'Erträge eingeben', d: 'Vergangene Jahre und dieses Jahr, in dt/ha oder t/ha. Unbekannte Jahre bleiben einfach leer.' },
    { icon: <TrendingUp className="size-5" />, t: 'Ergebnis ansehen', d: 'Ihr Feld im Vergleich zu seinem eigenen Durchschnitt, sofort. Die Modelle lernen daraus für die nächste Saison.' },
  ]
  return (
    <section className="py-16 sm:py-20">
      <Container>
        <SectionHeader eyebrow="So funktioniert es" title="Drei Schritte, kein Konto." />
        <ol className="mt-12 grid gap-5 md:grid-cols-3">
          {steps.map((s, i) => (
            <Reveal key={s.t} delay={i * 0.08}>
              <li className="panel h-full p-7">
                <span className="grid size-10 place-items-center rounded-xl bg-maize/10 text-maize">{s.icon}</span>
                <p className="mt-6 font-mono text-[11px] text-ink-4">Schritt {i + 1}</p>
                <h3 className="mt-1 text-[20px]">{s.t}</h3>
                <p className="mt-3 text-[14.5px] leading-relaxed text-ink-3">{s.d}</p>
              </li>
            </Reveal>
          ))}
        </ol>
      </Container>
    </section>
  )
}

function WhyAustria() {
  return (
    <section className="py-16 sm:py-20">
      <Container>
        <Reveal className="panel grain relative overflow-hidden p-8 sm:p-12">
          <div className="grid gap-10 lg:grid-cols-[1.3fr_1fr] lg:items-center">
            <div>
              <p className="eyebrow mb-4">Warum österreichische Felder zählen</p>
              <h2 className="text-balance text-[clamp(1.8rem,3.4vw,2.6rem)]">Die Modelle haben im Ausland gelernt. In Österreich müssen sie sich erst beweisen.</h2>
              <p className="mt-5 max-w-[580px] text-pretty text-[16px] leading-relaxed text-ink-2">
                Bisher kennen die Modelle nur Felder in den USA und in Europa. Im Test mit Österreich unterscheiden sie schon gute von
                schlechten Jahren. Was fehlt, ist der nächste Schritt: einzelne Felder und Regionen auseinanderzuhalten. Dafür brauchen
                wir gemessene Erträge von österreichischen Feldern – und die haben Sie.
              </p>
            </div>
            <div className="flex flex-col gap-3">
              <ButtonLink to="/contribute" size="lg" icon={<ArrowRight className="size-4" />}>Feld eintragen</ButtonLink>
              <Link to="/evidence" className="link-underline inline-flex items-center gap-1.5 text-[14px] text-ink-2 hover:text-ink">
                Testergebnisse ansehen <ArrowRight className="size-3.5" />
              </Link>
            </div>
          </div>
        </Reveal>
      </Container>
    </section>
  )
}

function Models() {
  const items = [
    { t: 'Teilflächenkarte', d: 'Zeigt, welcher Teil eines Felds wahrscheinlich schwächer ist.' },
    { t: 'Feld-Stress-Score', d: 'Markiert Felder, deren Saison im Vergleich zu gesunden Feldern ungewöhnlich aussieht.' },
    { t: 'EU-Regionalmodell', d: 'Schätzt, ob das Maisjahr einer Region besser oder schlechter als üblich ausfällt.' },
  ]
  return (
    <section className="py-16 sm:py-20">
      <Container>
        <SectionHeader eyebrow="Was wir bauen" title="Drei Modelle, einfach erklärt." />
        <div className="mt-12 grid gap-5 md:grid-cols-3">
          {items.map((m, i) => (
            <Reveal key={m.t} delay={i * 0.08}>
              <Link to="/model" className="panel group flex h-full flex-col p-7 transition-[transform,border-color] duration-300 hover:-translate-y-1 hover:border-[var(--line-strong)]">
                <div className="flex items-start justify-between">
                  <h3 className="text-[20px]">{m.t}</h3>
                  <ArrowUpRight className="size-4 text-ink-4 transition group-hover:text-ink" />
                </div>
                <p className="mt-3 text-[14.5px] leading-relaxed text-ink-3">{m.d}</p>
              </Link>
            </Reveal>
          ))}
        </div>
      </Container>
    </section>
  )
}

function ClosingCta() {
  return (
    <section className="pt-16 sm:pt-20">
      <Container className="text-center">
        <Reveal>
          <h2 className="mx-auto max-w-[760px] text-balance text-[clamp(2.2rem,5vw,3.8rem)]">Ein Feld. Zwei Minuten. Eine bessere Prognose für alle.</h2>
          <div className="mt-9 flex flex-wrap justify-center gap-3">
            <ButtonLink to="/contribute" size="lg" icon={<ArrowRight className="size-4" />}>Feld eintragen</ButtonLink>
            <ButtonLink to="/analyse" size="lg" variant="secondary">Beispielfeld ansehen</ButtonLink>
          </div>
        </Reveal>
      </Container>
    </section>
  )
}
