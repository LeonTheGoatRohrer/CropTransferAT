import { motion, useReducedMotion } from 'motion/react'
import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router'
import type { Evidence, FieldAnalysis } from '../api/types'
import { HeroField } from '../components/field/HeroField'
import { Backdrop } from '../components/ui/Backdrop'
import { FieldJourney } from '../components/ui/FieldJourney'
import { ButtonLink } from '../components/ui/Button'
import { Reveal } from '../components/ui/Reveal'
import { Container, SectionHeader } from '../components/ui/Section'
import { ErrorNote, Skeleton } from '../components/ui/States'
import { useResource } from '../lib/useResource'
import { getEvidence } from '../services/evidenceService'
import { getHeroField } from '../services/fieldService'

export default function Home() {
  const hero = useResource(getHeroField, 'hero')
  const evidence = useResource(getEvidence, 'evidence')
  return (
    <>
      <Hero field={hero.data} error={hero.error} />
      <Journey ev={evidence.data} />
      <WhyAustria />
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
    <section className="relative isolate overflow-hidden pt-28 pb-20 sm:pt-36 lg:pb-28">
      <Backdrop name="hero-abendlicht" />
      <div aria-hidden className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute -top-40 right-[-10%] h-[620px] w-[620px] rounded-full bg-[radial-gradient(closest-side,rgba(230,180,80,0.10),transparent)]" />
        <div className="absolute bottom-[-30%] left-[-15%] h-[560px] w-[760px] rounded-full bg-[radial-gradient(closest-side,rgba(85,160,90,0.08),transparent)]" />
      </div>
      <Container className="grid items-center gap-14 lg:grid-cols-[1.02fr_1fr] lg:gap-16">
        <div>
          <motion.p {...rise(0)} className="eyebrow mb-6 flex items-center gap-3">
            <span className="inline-block h-px w-8 bg-maize" /> Für Maisbäuerinnen und -bauern in Österreich
          </motion.p>
          <motion.h1 {...rise(0.08)} className="text-balance text-[clamp(2.6rem,6vw,4.8rem)] font-semibold leading-[0.96] tracking-[-0.045em]">
            Ein Feld. Viele Unterschiede. <span className="whitespace-nowrap text-maize">Endlich sichtbar.</span>
          </motion.h1>
          <motion.p {...rise(0.18)} className="mt-7 max-w-[540px] text-pretty text-[18px] leading-relaxed text-ink-2">
            Der Regen bleibt aus. Wie steht es um Ihren Mais? Wir machen mit Satellitendaten sichtbar, welche Bereiche Ihres Felds
            zurückbleiben – damit Sie wissen, wo sich ein genauerer Blick lohnt.
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
                ['22 800', 'wolkenfreie Satellitenwerte', 'ungefähr, 5 Indizes je 10-Tage-Schritt (HLS und Sentinel-2)'],
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

function Journey({ ev }: { ev?: Evidence }) {
  return (
    <section className="py-16 sm:py-20">
      <Container>
        <SectionHeader eyebrow="So funktioniert es" title="Was mit einem Feld passiert." lede="Vom eingezeichneten Umriss bis zur Feldkarte – mit kostenlosen Satelliten-, Wetter- und Bodendaten." />
        <div className="mt-12">
          <FieldJourney ev={ev} />
        </div>
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
