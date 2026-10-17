import { ArrowRight } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { ButtonLink } from '../components/ui/Button'
import { Reveal } from '../components/ui/Reveal'
import { Container, SectionHeader, Source } from '../components/ui/Section'
import { useContent } from '../i18n'

const STAGE_STYLE: Record<string, string> = {
  Done: 'bg-sage',
  Now: 'bg-maize ring-4 ring-maize/20',
  Next: 'bg-ink-3',
  Later: 'bg-ink-4',
}

export default function About() {
  const { t } = useTranslation()
  const { limitations, roadmap, project } = useContent()
  const stages = (['Done', 'Now', 'Next', 'Later'] as const).filter((st) => roadmap.some((r) => r.stage === st))
  return (
    <>
      <section className="pt-36 pb-10">
        <Container className="grid gap-12 lg:grid-cols-[1.2fr_1fr] lg:items-end">
          <Reveal>
            <p className="eyebrow mb-5">{t('about.eyebrow')}</p>
            <h1 className="text-balance text-[clamp(2.4rem,5.4vw,4.4rem)] leading-[1] tracking-[-0.04em] [hyphens:auto]">{t('about.title')}</h1>
          </Reveal>
          <Reveal delay={0.1}>
            <p className="text-pretty text-[17px] leading-relaxed text-ink-2">{project.question}</p>
            <p className="mt-4 text-[14px] text-ink-3">{t('about.meta', { c: project.competition })}</p>
          </Reveal>
        </Container>
      </section>

      <section id="limitations" className="scroll-mt-20 py-20">
        <Container>
          <SectionHeader eyebrow={t('about.limEyebrow')} title={t('about.limTitle')} lede={t('about.limLede')} />
          <div className="mt-12 grid gap-px overflow-hidden rounded-[var(--radius-panel)] border border-[var(--line)] bg-[var(--line)] md:grid-cols-2 lg:grid-cols-3">
            {limitations.map((l, i) => (
              <Reveal key={l.title} delay={(i % 3) * 0.06} className="flex flex-col bg-soil-900 p-7">
                <h3 className="text-[19px] leading-snug">{l.title}</h3>
                <p className="mt-3 flex-1 text-[14px] leading-relaxed text-ink-2">{l.body}</p>
                <p className="mt-6 border-t border-[var(--line)] pt-4 text-[13px] leading-relaxed text-ink-3">
                  <span className="font-mono text-[10.5px] uppercase tracking-[0.12em] text-maize">{t('about.next')}</span>
                  {l.next}
                </p>
              </Reveal>
            ))}
          </div>
        </Container>
      </section>

      <section id="roadmap" className="scroll-mt-20 py-20">
        <Container>
          <SectionHeader eyebrow={t('about.roadEyebrow')} title={t('about.roadTitle')} lede={t('about.roadLede')} />
          <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
            {stages.map((stage, si) => (
              <Reveal key={stage} delay={si * 0.06} className="panel p-6">
                <div className="flex items-center gap-2.5">
                  <span className={`size-2.5 rounded-full ${STAGE_STYLE[stage]}`} />
                  <p className="eyebrow">{t(`about.stages.${stage}`)}</p>
                </div>
                <ul className="mt-5 flex flex-col gap-5">
                  {roadmap.filter((r) => r.stage === stage).map((r) => (
                    <li key={r.title}>
                      <p className="text-[15px] font-medium text-ink">{r.title}</p>
                      <p className="mt-1 text-[13.5px] leading-relaxed text-ink-3">{r.body}</p>
                    </li>
                  ))}
                </ul>
              </Reveal>
            ))}
          </div>
        </Container>
      </section>

      <section id="disclosure" className="scroll-mt-20 py-20">
        <Container>
          <SectionHeader eyebrow={t('about.discEyebrow')} title={t('about.discTitle')} lede={t('about.discLede')} />
          <div className="mt-12 grid gap-5 md:grid-cols-2">
            {[
              [t('about.ai'), t('about.aiBody')],
              [t('about.providers'), t('about.providersBody')],
              [t('about.software'), t('about.softwareBody')],
              [t('about.translation'), t('about.translationBody')],
            ].map(([h, b], i) => (
              <Reveal key={h} className="panel p-7" delay={i * 0.05}>
                <p className="eyebrow mb-4">{h}</p>
                <p className="text-[14px] leading-relaxed text-ink-2">{b}</p>
              </Reveal>
            ))}
          </div>
          <Source className="mt-6">{t('about.src')}</Source>
          <Reveal className="mt-16 flex flex-col items-start justify-between gap-6 border-t border-[var(--line)] pt-10 sm:flex-row sm:items-center">
            <p className="max-w-[560px] font-display text-[24px] leading-snug tracking-[-0.02em]">{t('about.closing')}</p>
            <ButtonLink to="/analyse" size="lg" icon={<ArrowRight className="size-4" />}>{t('nav.cta')}</ButtonLink>
          </Reveal>
        </Container>
      </section>
    </>
  )
}
