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
            <span className="inline-block h-px w-8 bg-maize" /> Maize farmers in Austria
          </motion.p>
          <motion.h1 {...rise(0.08)} className="text-balance text-[clamp(2.9rem,6vw,5.1rem)] font-semibold leading-[0.96] tracking-[-0.045em]">
            Share your yields. <span className="text-maize">Get a better forecast.</span>
          </motion.h1>
          <motion.p {...rise(0.18)} className="mt-7 max-w-[540px] text-pretty text-[18px] leading-relaxed text-ink-2">
            Draw your maize field and tell us what it yielded in past years. You see at once how this year compares with your usual
            harvest. We get the Austrian field data that early warning from satellites needs to work here.
          </motion.p>
          <motion.div {...rise(0.28)} className="mt-10 flex flex-wrap gap-3">
            <ButtonLink to="/contribute" size="lg" icon={<ArrowRight className="size-4" />}>
              Add your field
            </ButtonLink>
            <ButtonLink to="/model" size="lg" variant="secondary">
              What the models do
            </ButtonLink>
          </motion.div>
          <motion.div {...rise(0.38)} className="mt-12 flex max-w-[560px] flex-col gap-6 border-t border-[var(--line)] pt-6">
            <dl className="grid grid-cols-3 gap-4">
              {[
                ['365', 'field-years with measured yield', '19 seasons, 1989–2023 · about 19 per season'],
                ['28,000', 'yield cells (10 × 10 m)', 'about, inside 54 field-years (maps and points)'],
                ['7,700', 'satellite curves', 'about, 365 field-years × 21 ten-day steps'],
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
              <p className="text-[14px] font-medium leading-snug text-ink">Austrian values in training</p>
              <p className="mt-1 text-[12px] leading-snug text-ink-3">Austria is only the final test, because there is no field-level yield data yet. Your harvest data can change that.</p>
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
      title: 'You give',
      items: ['The outline of one maize field', 'Its yield in past years, as far as you know it', 'This year’s harvest, or your estimate so far'],
    },
    {
      icon: <TrendingUp className="size-5" />,
      title: 'You get',
      items: ['How this year compares with your own usual yield', 'A forecast that improves as more fields join', 'Satellite and weather analysis of your field, as it becomes available'],
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
    { icon: <PenLine className="size-5" />, t: 'Draw your field', d: 'Find your village on the satellite map and click the corners of the field.' },
    { icon: <Sprout className="size-5" />, t: 'Enter your yields', d: 'Past years and this year, in dt/ha or t/ha. Unknown years can stay empty.' },
    { icon: <TrendingUp className="size-5" />, t: 'See your result', d: 'Your field against its own average, right away. The models learn from it for the next season.' },
  ]
  return (
    <section className="py-16 sm:py-20">
      <Container>
        <SectionHeader eyebrow="How it works" title="Three steps, no account." />
        <ol className="mt-12 grid gap-5 md:grid-cols-3">
          {steps.map((s, i) => (
            <Reveal key={s.t} delay={i * 0.08}>
              <li className="panel h-full p-7">
                <span className="grid size-10 place-items-center rounded-xl bg-maize/10 text-maize">{s.icon}</span>
                <p className="mt-6 font-mono text-[11px] text-ink-4">Step {i + 1}</p>
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
              <p className="eyebrow mb-4">Why Austrian fields matter</p>
              <h2 className="text-balance text-[clamp(1.8rem,3.4vw,2.6rem)]">The models learned abroad. Austria still has to prove it.</h2>
              <p className="mt-5 max-w-[580px] text-pretty text-[16px] leading-relaxed text-ink-2">
                So far the models only saw fields in the USA and Europe. Tested on Austria, they already tell good years from bad ones. What
                is missing is the next step: telling single fields and regions apart. For that we need measured yields from Austrian fields,
                and you have them.
              </p>
            </div>
            <div className="flex flex-col gap-3">
              <ButtonLink to="/contribute" size="lg" icon={<ArrowRight className="size-4" />}>Add your field</ButtonLink>
              <Link to="/evidence" className="link-underline inline-flex items-center gap-1.5 text-[14px] text-ink-2 hover:text-ink">
                See the test results <ArrowRight className="size-3.5" />
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
    { t: 'Within-field map', d: 'Shows which part of one field is likely to be weak.' },
    { t: 'Field stress score', d: 'Flags fields whose season looks unusual compared with healthy ones.' },
    { t: 'EU regional model', d: 'Estimates whether a region’s maize year will be better or worse than usual.' },
  ]
  return (
    <section className="py-16 sm:py-20">
      <Container>
        <SectionHeader eyebrow="What we build" title="Three models, explained simply." />
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
          <h2 className="mx-auto max-w-[760px] text-balance text-[clamp(2.2rem,5vw,3.8rem)]">One field. Two minutes. A better forecast for everyone.</h2>
          <div className="mt-9 flex justify-center gap-3">
            <ButtonLink to="/contribute" size="lg" icon={<ArrowRight className="size-4" />}>Add your field</ButtonLink>
            <ButtonLink to="/analyse" size="lg" variant="secondary">Try an example field</ButtonLink>
          </div>
        </Reveal>
      </Container>
    </section>
  )
}
