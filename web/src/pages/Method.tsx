import { motion, useReducedMotion, useScroll, useTransform } from 'motion/react'
import { useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { StrengthBadge } from '../components/ui/Badge'
import { Reveal } from '../components/ui/Reveal'
import { Container, SectionHeader, Source } from '../components/ui/Section'
import { useContent } from '../i18n'

export default function Method() {
  const { t } = useTranslation()
  return (
    <>
      <section className="pt-36 pb-10">
        <Container>
          <Reveal>
            <p className="eyebrow mb-5">{t('method.eyebrow')}</p>
            <h1 className="max-w-[900px] text-balance text-[clamp(2.4rem,5.4vw,4.4rem)] leading-[1] tracking-[-0.04em] [hyphens:auto]">{t('method.title')}</h1>
            <p className="mt-6 max-w-[680px] text-[17px] leading-relaxed text-ink-2">{t('method.lede')}</p>
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
  const { t } = useTranslation()
  const { pipelineSteps } = useContent()
  const ref = useRef<HTMLDivElement>(null)
  const reduce = useReducedMotion()
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start 70%', 'end 60%'] })
  const h = useTransform(scrollYProgress, [0, 1], ['0%', '100%'])
  return (
    <section className="py-20">
      <Container>
        <SectionHeader eyebrow={t('method.pipeEyebrow')} title={t('method.pipeTitle')} lede={t('method.pipeLede')} />
        <div ref={ref} className="relative mx-auto mt-16 max-w-[880px]">
          <div className="absolute bottom-0 left-[19px] top-0 w-px bg-[var(--line)] sm:left-1/2">
            <motion.div className="w-full bg-gradient-to-b from-maize to-rust" style={{ height: reduce ? '100%' : h }} />
          </div>
          <ol className="flex flex-col gap-10">
            {pipelineSteps.map((s, i) => (
              <li key={s.key} className={`relative grid gap-4 pl-14 sm:grid-cols-2 sm:gap-16 sm:pl-0 ${i % 2 ? 'sm:[&>div]:col-start-2' : ''}`}>
                <span className="absolute left-[13px] top-2 size-[13px] rounded-full border-2 border-maize bg-soil-950 sm:left-1/2 sm:-translate-x-1/2" />
                <Reveal className={`panel p-6 ${i % 2 ? '' : 'sm:text-right'}`}>
                  <p className="font-mono text-[10.5px] uppercase tracking-[0.14em] text-maize">{t('method.step', { n: i + 1, meta: s.meta })}</p>
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
  const { t } = useTranslation()
  const years = ['2014', '2017', '2018', '2019', '2020', '2021', '2023']
  const rows = 4
  const texts = t('method.schemes', { returnObjects: true }) as { name: string; body: string; used: string }[]
  const controls = t('method.controls', { returnObjects: true }) as [string, string][]
  const cells: ((f: number, y: number) => string)[] = [
    (f, y) => (f === 1 && y === 3 ? 'test' : f === 1 || y === 3 ? 'gap' : 'train'),
    (f) => (f === 2 ? 'test' : 'train'),
    (f) => (f === 0 ? 'test' : 'train'),
  ]
  const color = { train: 'bg-sage/35', test: 'bg-maize', gap: 'bg-white/[0.04]' }
  return (
    <section className="py-20">
      <Container>
        <SectionHeader eyebrow={t('method.valEyebrow')} title={t('method.valTitle')} lede={t('method.valLede')} />
        <div className="mt-12 grid gap-5 lg:grid-cols-3">
          {texts.map((s, si) => (
            <Reveal key={s.name} delay={si * 0.06} className="panel p-6">
              <p className="eyebrow">{s.used}</p>
              <h3 className="mt-3 text-[19px]">{s.name}</h3>
              <div className="mt-6 grid gap-1" style={{ gridTemplateColumns: `repeat(${years.length}, minmax(0, 1fr))` }} aria-hidden>
                {Array.from({ length: rows }, (_, f) => years.map((__, y) => <span key={`${f}-${y}`} className={`aspect-square rounded-[4px] ${color[cells[si](f, y) as keyof typeof color]}`} />))}
              </div>
              <div className="mt-2 flex justify-between font-mono text-[9.5px] text-ink-4">
                <span>{si === 2 ? t('method.yearsAxis') : years[0]}</span>
                <span>{si === 2 ? t('method.rowsCountries') : years.at(-1)}</span>
              </div>
              <p className="mt-5 text-[13.5px] leading-relaxed text-ink-2">{s.body}</p>
            </Reveal>
          ))}
        </div>
        <div className="mt-5 flex flex-wrap gap-5 text-[12.5px] text-ink-3">
          <span className="flex items-center gap-2"><span className="size-3 rounded-[3px] bg-maize" />{t('method.test')}</span>
          <span className="flex items-center gap-2"><span className="size-3 rounded-[3px] bg-sage/35" />{t('method.train')}</span>
          <span className="flex items-center gap-2"><span className="size-3 rounded-[3px] bg-white/[0.06]" />{t('method.excluded')}</span>
        </div>
        <Reveal className="mt-10 grid gap-5 md:grid-cols-3">
          {controls.map(([title, body]) => (
            <div key={title} className="border-t border-[var(--line-strong)] pt-5">
              <h3 className="text-[17px]">{title}</h3>
              <p className="mt-2 text-[13.5px] leading-relaxed text-ink-2">{body}</p>
            </div>
          ))}
        </Reveal>
      </Container>
    </section>
  )
}

function Features() {
  const { t } = useTranslation()
  const { featureGroups } = useContent()
  return (
    <section className="py-20">
      <Container>
        <SectionHeader eyebrow={t('method.featEyebrow')} title={t('method.featTitle')} lede={t('method.featLede')} />
        <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {featureGroups.map((g, i) => (
            <Reveal key={g.title} delay={i * 0.05} className={`panel p-6 ${g.denied ? 'border-rust/25' : ''}`}>
              <h3 className="text-[18px]">{g.title}</h3>
              <ul className="mt-4 flex flex-col gap-2.5">
                {g.items.map((it) => (
                  <li key={it} className="flex gap-2.5 text-[13.5px] leading-relaxed text-ink-2">
                    <span className={`mt-[7px] size-1.5 shrink-0 rounded-full ${g.denied ? 'bg-rust' : 'bg-maize'}`} />
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
  const { t } = useTranslation()
  const { experiments } = useContent()
  const nFailed = experiments.filter((e) => e.status === 'failed').length
  const dot = (s: string) => (s === 'failed' ? 'bg-rust' : s === 'robust' ? 'bg-sage' : s === 'certain-small' ? 'bg-water' : s === 'frozen' ? 'bg-ink' : s === 'done' ? 'bg-ink-3' : 'bg-maize')
  return (
    <section id="experiments" className="scroll-mt-20 py-20">
      <Container>
        <SectionHeader eyebrow={t('method.expEyebrow')} title={t('method.expTitle', { n: experiments.length })} lede={t('method.expLede', { f: nFailed })} />
        <ol className="relative mt-14 border-l border-[var(--line-strong)] pl-6 sm:ml-[132px] sm:pl-10">
          {experiments.map((e, i) => (
            <li key={e.id} className="relative list-none pb-10 last:pb-0">
              <Reveal delay={Math.min(i, 4) * 0.03}>
                <span className={`absolute -left-[31px] top-1.5 size-2.5 rounded-full sm:-left-[45px] ${dot(e.status)}`} />
                <p className="font-mono text-[11px] text-ink-3 sm:absolute sm:-left-[172px] sm:top-0.5 sm:w-[110px] sm:text-right">
                  {e.date}
                  <span className="block text-ink-4">{e.phase}</span>
                </p>
                <div className="mt-1 flex flex-wrap items-center gap-3 sm:mt-0">
                  <h3 className="text-[20px]">{e.title}</h3>
                  <StrengthBadge strength={e.status} />
                </div>
                <p className="mt-2 max-w-[720px] text-[14px] leading-relaxed text-ink-2">
                  <span className="text-ink-3">{t('method.changed')}</span>
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
