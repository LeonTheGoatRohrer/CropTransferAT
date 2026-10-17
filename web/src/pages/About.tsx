import { ArrowRight } from 'lucide-react'
import { ButtonLink } from '../components/ui/Button'
import { Reveal } from '../components/ui/Reveal'
import { Container, SectionHeader, Source } from '../components/ui/Section'
import { LIMITATIONS, PROJECT, ROADMAP } from '../data/content/project'

const STAGE_STYLE: Record<string, string> = {
  Done: 'bg-sage',
  Now: 'bg-maize ring-4 ring-maize/20',
  Next: 'bg-ink-3',
  Later: 'bg-ink-4',
}

export default function About() {
  return (
    <>
      <section className="pt-36 pb-10">
        <Container className="grid gap-12 lg:grid-cols-[1.2fr_1fr] lg:items-end">
          <Reveal>
            <p className="eyebrow mb-5">About the project</p>
            <h1 className="text-balance text-[clamp(2.6rem,6vw,4.6rem)] leading-[0.98] tracking-[-0.04em]">A research question, not a sales pitch.</h1>
          </Reveal>
          <Reveal delay={0.1}>
            <p className="text-pretty text-[17px] leading-relaxed text-ink-2">{PROJECT.question}</p>
            <p className="mt-4 text-[14px] text-ink-3">{PROJECT.competition} · solo project · 2026</p>
          </Reveal>
        </Container>
      </section>

      <section id="limitations" className="scroll-mt-20 py-20">
        <Container>
          <SectionHeader
            eyebrow="Current limitations"
            title="What the evidence does not cover yet."
            lede="Each limit is named with the next step that would close it. They define the next stage of the research — not an excuse for this one."
          />
          <div className="mt-12 grid gap-px overflow-hidden rounded-[var(--radius-panel)] border border-[var(--line)] bg-[var(--line)] md:grid-cols-2 lg:grid-cols-3">
            {LIMITATIONS.map((l, i) => (
              <Reveal key={l.title} delay={(i % 3) * 0.06} className="flex flex-col bg-soil-900 p-7">
                <h3 className="text-[19px] leading-snug">{l.title}</h3>
                <p className="mt-3 flex-1 text-[14px] leading-relaxed text-ink-2">{l.body}</p>
                <p className="mt-6 border-t border-[var(--line)] pt-4 text-[13px] leading-relaxed text-ink-3">
                  <span className="font-mono text-[10.5px] uppercase tracking-[0.12em] text-maize">Next · </span>
                  {l.next}
                </p>
              </Reveal>
            ))}
          </div>
        </Container>
      </section>

      <section id="roadmap" className="scroll-mt-20 py-20">
        <Container>
          <SectionHeader eyebrow="Roadmap" title="Done, now, next." lede="Nothing under “Next” or “Later” is presented as working today." />
          <div className="mt-12 grid gap-5 md:grid-cols-3">
            {(['Done', 'Now', 'Next', 'Later'] as const).filter((st) => ROADMAP.some((r) => r.stage === st)).map((stage, si) => (
              <Reveal key={stage} delay={si * 0.06} className="panel p-6">
                <div className="flex items-center gap-2.5">
                  <span className={`size-2.5 rounded-full ${STAGE_STYLE[stage]}`} />
                  <p className="eyebrow">{stage}</p>
                </div>
                <ul className="mt-5 flex flex-col gap-5">
                  {ROADMAP.filter((r) => r.stage === stage).map((r) => (
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
          <SectionHeader eyebrow="Support and AI disclosure" title="Who and what helped." lede="BWKI requires every kind of support to be disclosed. The full, dated list is kept in SUPPORT.md." />
          <div className="mt-12 grid gap-5 lg:grid-cols-3">
            <Reveal className="panel p-7">
              <p className="eyebrow mb-4">AI tools</p>
              <p className="text-[14px] leading-relaxed text-ink-2">
                Claude Code (Anthropic) was used for code, data pipelines, analyses, documentation drafts and this website; Codex (OpenAI) for an
                independent second literature and data search. Plans, decisions and every research choice were made by the project owner and are
                logged in DECISIONS.md.
              </p>
            </Reveal>
            <Reveal className="panel p-7" delay={0.06}>
              <p className="eyebrow mb-4">Data providers</p>
              <p className="text-[14px] leading-relaxed text-ink-2">
                Kellogg Biological Station LTER, USDA-ARS Beltsville and Akron, Kayad et al., ESA/Copernicus, NASA, ECMWF, ISRIC, USDA NRCS,
                CY-Bench, One Acre Fund. KBS data may only be published with written permission — one reason this site is private.
              </p>
            </Reveal>
            <Reveal className="panel p-7" delay={0.12}>
              <p className="eyebrow mb-4">Software</p>
              <p className="text-[14px] leading-relaxed text-ink-2">
                Python: Earth Engine API, geopandas, pandas, scikit-learn, LightGBM, SHAP. Web: React, MapLibre GL, Terra Draw, D3, Motion. Base
                maps by Esri, EOX (Sentinel-2 cloudless) and OpenTopoMap; place search by OpenStreetMap Nominatim.
              </p>
            </Reveal>
          </div>
          <Source className="mt-6">SUPPORT.md · DATA_SOURCES.md · DECISIONS.md</Source>
          <Reveal className="mt-16 flex flex-col items-start justify-between gap-6 border-t border-[var(--line)] pt-10 sm:flex-row sm:items-center">
            <p className="max-w-[560px] font-display text-[24px] leading-snug tracking-[-0.02em]">See it on a real field: five held-out field-years with their measured outcome.</p>
            <ButtonLink to="/analyse" size="lg" icon={<ArrowRight className="size-4" />}>Analyse a field</ButtonLink>
          </Reveal>
        </Container>
      </section>
    </>
  )
}
