import { Backdrop } from '../components/ui/Backdrop'
import { ProjectFlow } from '../components/ui/ProjectFlow'
import { Reveal } from '../components/ui/Reveal'
import { Container, SectionHeader } from '../components/ui/Section'
import { FEATURE_GROUPS } from '../data/content/project'

export default function Method() {
  return (
    <>
      <section className="relative isolate overflow-hidden pt-36 pb-16">
        <Backdrop name="methode-drohne" />
        <Container>
          <Reveal>
            <p className="eyebrow mb-5">Methode</p>
            <h1 className="max-w-[900px] text-balance text-[clamp(2.6rem,6vw,4.6rem)] leading-[0.98] tracking-[-0.04em]">Erst den Test festlegen. Dann ein einziges Mal durchführen.</h1>
            <p className="mt-6 max-w-[680px] text-[17px] leading-relaxed text-ink-2">
              Jede Modellrunde wurde aufgeschrieben, bevor sie lief: Merkmale, Datenaufteilung, Metriken und Bestehenskriterien. Ergebnisse – gute
              wie schlechte – werden so berichtet, wie sie herauskamen.
            </p>
          </Reveal>
        </Container>
      </section>
      <section id="vorgehen" className="scroll-mt-20 py-20">
        <Container>
          <SectionHeader eyebrow="So sind wir vorgegangen" title="Vom Satellitenbild zur Warnung – in fünf Schritten." lede="Daten sammeln, aufbereiten, Modelle trainieren, ehrlich prüfen, einfrieren. Österreich kommt erst danach, als einmaliger Test." />
          <div className="mt-12">
            <ProjectFlow />
          </div>
        </Container>
      </section>
      <Features />
    </>
  )
}

/** The 'deliberately excluded' group, identified by its source path so it survives title translation. */
const isExcluded = (g: { source: string }) => g.source.includes('test_no_leakage')

function Features() {
  return (
    <section id="merkmale" className="scroll-mt-20 py-20">
      <Container>
        <SectionHeader eyebrow="Merkmalsbildung" title="Mehr als rohe Pixel." lede="Was die Modelle tatsächlich sehen – und was ihnen bewusst vorenthalten wird." />
        <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {FEATURE_GROUPS.map((g, i) => (
            <Reveal key={g.title} delay={i * 0.05} className={`panel p-6 ${isExcluded(g) ? 'border-rust/25' : ''}`}>
              <h3 className="text-[18px]">{g.title}</h3>
              <ul className="mt-4 flex flex-col gap-2.5">
                {g.items.map((it) => (
                  <li key={it} className="flex gap-2.5 text-[13.5px] leading-relaxed text-ink-2">
                    <span className={`mt-[7px] size-1.5 shrink-0 rounded-full ${isExcluded(g) ? 'bg-rust' : 'bg-maize'}`} />
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
