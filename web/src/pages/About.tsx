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

/** Display labels for the roadmap stage values (the values themselves stay English for logic). */
const STAGE_LABEL: Record<string, string> = {
  Done: 'Erledigt',
  Now: 'Jetzt',
  Next: 'Als Nächstes',
  Later: 'Später',
}

export default function About() {
  return (
    <>
      <section className="pt-36 pb-10">
        <Container className="grid gap-12 lg:grid-cols-[1.2fr_1fr] lg:items-end">
          <Reveal>
            <p className="eyebrow mb-5">Über das Projekt</p>
            <h1 className="text-balance text-[clamp(2.6rem,6vw,4.6rem)] leading-[0.98] tracking-[-0.04em]">Eine Forschungsfrage, kein Verkaufsgespräch.</h1>
          </Reveal>
          <Reveal delay={0.1}>
            <p className="text-pretty text-[17px] leading-relaxed text-ink-2">{PROJECT.question}</p>
            <p className="mt-4 text-[14px] text-ink-3">{PROJECT.competition} · Einzelprojekt · 2026</p>
          </Reveal>
        </Container>
      </section>

      <section id="limitations" className="scroll-mt-20 py-20">
        <Container>
          <SectionHeader
            eyebrow="Aktuelle Grenzen"
            title="Was die Belege noch nicht abdecken."
            lede="Jede Grenze steht hier mit dem nächsten Schritt, der sie schließen würde. Die Grenzen bestimmen die nächste Stufe der Forschung – sie sind keine Ausrede für diese."
          />
          <div className="mt-12 grid gap-px overflow-hidden rounded-[var(--radius-panel)] border border-[var(--line)] bg-[var(--line)] md:grid-cols-2 lg:grid-cols-3">
            {LIMITATIONS.map((l, i) => (
              <Reveal key={l.title} delay={(i % 3) * 0.06} className="flex flex-col bg-soil-900 p-7">
                <h3 className="text-[19px] leading-snug">{l.title}</h3>
                <p className="mt-3 flex-1 text-[14px] leading-relaxed text-ink-2">{l.body}</p>
                <p className="mt-6 border-t border-[var(--line)] pt-4 text-[13px] leading-relaxed text-ink-3">
                  <span className="font-mono text-[10.5px] uppercase tracking-[0.12em] text-maize">Als Nächstes · </span>
                  {l.next}
                </p>
              </Reveal>
            ))}
          </div>
        </Container>
      </section>

      <section id="roadmap" className="scroll-mt-20 py-20">
        <Container>
          <SectionHeader eyebrow="Ausblick" title="Erledigt, jetzt, als Nächstes." lede="Nichts unter „Als Nächstes“ oder „Später“ wird als heute schon funktionierend dargestellt." />
          <div className="mt-12 grid gap-5 md:grid-cols-3">
            {(['Done', 'Now', 'Next', 'Later'] as const).filter((st) => ROADMAP.some((r) => r.stage === st)).map((stage, si) => (
              <Reveal key={stage} delay={si * 0.06} className="panel p-6">
                <div className="flex items-center gap-2.5">
                  <span className={`size-2.5 rounded-full ${STAGE_STYLE[stage]}`} />
                  <p className="eyebrow">{STAGE_LABEL[stage]}</p>
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
          <SectionHeader eyebrow="Unterstützung und KI-Offenlegung" title="Wer und was geholfen hat." lede="Der BWKI verlangt, dass jede Art von Unterstützung offengelegt wird. Die vollständige, datierte Liste steht in SUPPORT.md." />
          <div className="mt-12 grid gap-5 lg:grid-cols-3">
            <Reveal className="panel p-7">
              <p className="eyebrow mb-4">KI-Werkzeuge</p>
              <p className="text-[14px] leading-relaxed text-ink-2">
                Claude Code (Anthropic) wurde für Code, Datenpipelines, Analysen, Dokumentationsentwürfe und diese Website eingesetzt, Codex (OpenAI)
                für eine unabhängige zweite Literatur- und Datenrecherche. Pläne, Entscheidungen und jede Forschungsentscheidung stammen vom
                Projektinhaber und sind in DECISIONS.md protokolliert.
              </p>
            </Reveal>
            <Reveal className="panel p-7" delay={0.06}>
              <p className="eyebrow mb-4">Datenanbieter</p>
              <p className="text-[14px] leading-relaxed text-ink-2">
                Kellogg Biological Station LTER, USDA-ARS Beltsville und Akron, Kayad et al., ESA/Copernicus, NASA, ECMWF, ISRIC, USDA NRCS,
                CY-Bench, One Acre Fund. KBS-Daten dürfen nur mit schriftlicher Genehmigung veröffentlicht werden – ein Grund, warum diese Website privat ist.
              </p>
            </Reveal>
            <Reveal className="panel p-7" delay={0.12}>
              <p className="eyebrow mb-4">Software</p>
              <p className="text-[14px] leading-relaxed text-ink-2">
                Python: Earth Engine API, geopandas, pandas, scikit-learn, LightGBM, SHAP. Web: React, MapLibre GL, Terra Draw, D3, Motion.
                Grundkarten von Esri, EOX (Sentinel-2 cloudless) und OpenTopoMap; Ortssuche über OpenStreetMap Nominatim.
              </p>
            </Reveal>
          </div>
          <Source className="mt-6">SUPPORT.md · DATA_SOURCES.md · DECISIONS.md</Source>
          <Reveal className="mt-16 flex flex-col items-start justify-between gap-6 border-t border-[var(--line)] pt-10 sm:flex-row sm:items-center">
            <p className="max-w-[560px] font-display text-[24px] leading-snug tracking-[-0.02em]">Sehen Sie es an einem echten Feld: sechs zurückgehaltene Feld-Jahre mit ihrem gemessenen Ergebnis.</p>
            <ButtonLink to="/analyse" size="lg" icon={<ArrowRight className="size-4" />}>Feld analysieren</ButtonLink>
          </Reveal>
        </Container>
      </section>
    </>
  )
}
