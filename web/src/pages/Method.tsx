import { motion, useReducedMotion, useScroll, useTransform } from 'motion/react'
import { useRef } from 'react'
import { StrengthBadge } from '../components/ui/Badge'
import { Reveal } from '../components/ui/Reveal'
import { Container, SectionHeader, Source } from '../components/ui/Section'
import { EXPERIMENTS, FEATURE_GROUPS, PIPELINE_STEPS } from '../data/content/project'

export default function Method() {
  return (
    <>
      <section className="pt-36 pb-10">
        <Container>
          <Reveal>
            <p className="eyebrow mb-5">Method</p>
            <h1 className="max-w-[900px] text-balance text-[clamp(2.6rem,6vw,4.6rem)] leading-[0.98] tracking-[-0.04em]">Decide the test first. Then run it once.</h1>
            <p className="mt-6 max-w-[680px] text-[17px] leading-relaxed text-ink-2">
              Every model round was written down before it ran: features, splits, metrics and pass criteria. Results — good or bad — are
              reported as they came out.
            </p>
          </Reveal>
        </Container>
      </section>
      <Pipeline />
      <Validation />
      <Features />
      <Experiments />
    </>
  )
}

function Pipeline() {
  const ref = useRef<HTMLDivElement>(null)
  const reduce = useReducedMotion()
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start 70%', 'end 60%'] })
  const h = useTransform(scrollYProgress, [0, 1], ['0%', '100%'])
  return (
    <section className="py-20">
      <Container>
        <SectionHeader eyebrow="How it works" title="From satellite pixels to field-level insight." lede="Seven steps, each with a rule that keeps future information out." />
        <div ref={ref} className="relative mx-auto mt-16 max-w-[880px]">
          <div className="absolute bottom-0 left-[19px] top-0 w-px bg-[var(--line)] sm:left-1/2">
            <motion.div className="w-full bg-gradient-to-b from-maize to-rust" style={{ height: reduce ? '100%' : h }} />
          </div>
          <ol className="flex flex-col gap-10">
            {PIPELINE_STEPS.map((s, i) => (
              <li key={s.key} className={`relative grid gap-4 pl-14 sm:grid-cols-2 sm:gap-16 sm:pl-0 ${i % 2 ? 'sm:[&>div]:col-start-2' : ''}`}>
                <span className="absolute left-[13px] top-2 size-[13px] rounded-full border-2 border-maize bg-soil-950 sm:left-1/2 sm:-translate-x-1/2" />
                <Reveal className={`panel p-6 ${i % 2 ? '' : 'sm:text-right'}`}>
                  <p className="font-mono text-[10.5px] uppercase tracking-[0.14em] text-maize">Step {i + 1} · {s.meta}</p>
                  <h3 className="mt-3 text-[21px]">{s.title}</h3>
                  <p className="mt-2 text-[14px] leading-relaxed text-ink-2">{s.body}</p>
                </Reveal>
              </li>
            ))}
          </ol>
        </div>
      </Container>
    </section>
  )
}

/** Visual explanation of the hold-out schemes: a grid of fields × years, with held-out cells highlighted. */
function Validation() {
  const years = ['2014', '2017', '2018', '2019', '2020', '2021', '2023']
  const fields = ['Field group 1', 'Field group 2', 'Field group 3', 'Field group 4']
  const schemes = [
    {
      key: 'lofyo',
      name: 'Leave field group and year out',
      body: 'Test cell: one field group in one year. Training excludes that whole year and that whole field group — the model sees neither.',
      used: 'Field models, stress score',
      cell: (f: number, y: number) => (f === 1 && y === 3 ? 'test' : f === 1 || y === 3 ? 'gap' : 'train'),
    },
    {
      key: 'lofo',
      name: 'Leave one field out',
      body: 'Within-field models are trained on the other fields and scored on cells of a field they have never seen.',
      used: 'Within-field model M1',
      cell: (f: number) => (f === 2 ? 'test' : 'train'),
    },
    {
      key: 'loco',
      name: 'Leave one country out',
      body: 'Each EU country is predicted by a model trained on the other 15. Austria is never in any fold.',
      used: 'EU regional model',
      cell: (f: number) => (f === 0 ? 'test' : 'train'),
    },
  ]
  const color = { train: 'bg-sage/35', test: 'bg-maize', gap: 'bg-white/[0.04]' }
  return (
    <section className="py-20">
      <Container>
        <SectionHeader eyebrow="Validation" title="Held out means held out." lede="Three hold-out schemes, chosen so that a model can never recognise a field, a year or a country it was tested on." />
        <div className="mt-12 grid gap-5 lg:grid-cols-3">
          {schemes.map((s, si) => (
            <Reveal key={s.key} delay={si * 0.06} className="panel p-6">
              <p className="eyebrow">{s.used}</p>
              <h3 className="mt-3 text-[19px]">{s.name}</h3>
              <div className="mt-6 grid gap-1" style={{ gridTemplateColumns: `repeat(${years.length}, minmax(0, 1fr))` }} aria-hidden>
                {fields.map((_, f) => years.map((__, y) => <span key={`${f}-${y}`} className={`aspect-square rounded-[4px] ${color[s.cell(f, y) as keyof typeof color]}`} />))}
              </div>
              <div className="mt-2 flex justify-between font-mono text-[9.5px] text-ink-4">
                <span>{s.key === 'loco' ? 'years →' : years[0]}</span>
                <span>{s.key === 'loco' ? 'rows = countries' : years.at(-1)}</span>
              </div>
              <p className="mt-5 text-[13.5px] leading-relaxed text-ink-2">{s.body}</p>
            </Reveal>
          ))}
        </div>
        <div className="mt-5 flex flex-wrap gap-5 text-[12.5px] text-ink-3">
          <span className="flex items-center gap-2"><span className="size-3 rounded-[3px] bg-maize" />test</span>
          <span className="flex items-center gap-2"><span className="size-3 rounded-[3px] bg-sage/35" />training</span>
          <span className="flex items-center gap-2"><span className="size-3 rounded-[3px] bg-white/[0.06]" />excluded from both</span>
        </div>
        <Reveal className="mt-10 grid gap-5 md:grid-cols-3">
          {[
            ['Label shuffle', 'Yields are permuted at random. Every model must fall to baseline; one that does not would reveal leakage.'],
            ['Adversarial validation', 'Can a classifier tell training from test rows? It can tell Michigan from Maryland perfectly — so transfer between sites is reported separately.'],
            ['As-of rule', 'A feature for forecast date t only uses observations made before t. A dedicated test (test_no_leakage.py) enforces it.'],
          ].map(([t, b]) => (
            <div key={t} className="border-t border-[var(--line-strong)] pt-5">
              <h3 className="text-[17px]">{t}</h3>
              <p className="mt-2 text-[13.5px] leading-relaxed text-ink-2">{b}</p>
            </div>
          ))}
        </Reveal>
      </Container>
    </section>
  )
}

function Features() {
  return (
    <section className="py-20">
      <Container>
        <SectionHeader eyebrow="Feature engineering" title="More than raw pixels." lede="What the models actually see, and what they are deliberately denied." />
        <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {FEATURE_GROUPS.map((g, i) => (
            <Reveal key={g.title} delay={i * 0.05} className={`panel p-6 ${g.title.startsWith('Deliberately') ? 'border-rust/25' : ''}`}>
              <h3 className="text-[18px]">{g.title}</h3>
              <ul className="mt-4 flex flex-col gap-2.5">
                {g.items.map((it) => (
                  <li key={it} className="flex gap-2.5 text-[13.5px] leading-relaxed text-ink-2">
                    <span className={`mt-[7px] size-1.5 shrink-0 rounded-full ${g.title.startsWith('Deliberately') ? 'bg-rust' : 'bg-maize'}`} />
                    {it}
                  </li>
                ))}
              </ul>
              <p className="mt-5 font-mono text-[10.5px] text-ink-4">{g.source}</p>
            </Reveal>
          ))}
        </div>
      </Container>
    </section>
  )
}

function Experiments() {
  return (
    <section id="experiments" className="scroll-mt-20 py-20">
      <Container>
        <SectionHeader
          eyebrow="Experiments"
          title={`${EXPERIMENTS.length} steps, in the order they happened.`}
          lede={`Each step changed one thing and was judged against criteria fixed beforehand. ${EXPERIMENTS.filter((e) => e.status === 'failed').length} of them failed; they are listed with the same care as the successes.`}
        />
        <ol className="relative mt-14 border-l border-[var(--line-strong)] pl-6 sm:ml-[132px] sm:pl-10">
          {EXPERIMENTS.map((e, i) => (
            <li key={e.id} className="relative list-none pb-10 last:pb-0">
              <Reveal delay={Math.min(i, 4) * 0.03}>
                <span className={`absolute -left-[31px] top-1.5 size-2.5 rounded-full sm:-left-[45px] ${e.status === 'failed' ? 'bg-rust' : e.status === 'robust' ? 'bg-sage' : e.status === 'certain-small' ? 'bg-water' : e.status === 'frozen' ? 'bg-ink' : 'bg-maize'}`} />
                <p className="font-mono text-[11px] text-ink-3 sm:absolute sm:-left-[172px] sm:top-0.5 sm:w-[110px] sm:text-right">
                  {e.date}
                  <span className="block text-ink-4">{e.phase}</span>
                </p>
                <div className="mt-1 flex flex-wrap items-center gap-3 sm:mt-0">
                  <h3 className="text-[20px]">{e.title}</h3>
                  <StrengthBadge strength={e.status} />
                </div>
                <p className="mt-2 max-w-[720px] text-[14px] leading-relaxed text-ink-2">
                  <span className="text-ink-3">Changed: </span>
                  {e.changed}
                </p>
                <p className="mt-1 max-w-[720px] text-[14px] leading-relaxed text-ink">{e.result}</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {e.numbers.map((n) => (
                    <span key={n.label} className="rounded-lg border border-[var(--line)] bg-white/[0.02] px-2.5 py-1 font-mono text-[11.5px] text-ink-2">
                      {n.label} <span className="text-ink">{n.value}</span>
                    </span>
                  ))}
                </div>
                <Source className="mt-2">{e.source}</Source>
              </Reveal>
            </li>
          ))}
        </ol>
      </Container>
    </section>
  )
}
