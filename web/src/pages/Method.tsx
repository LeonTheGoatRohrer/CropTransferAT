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
            <p className="eyebrow mb-5">Methode</p>
            <h1 className="max-w-[900px] text-balance text-[clamp(2.6rem,6vw,4.6rem)] leading-[0.98] tracking-[-0.04em]">Erst den Test festlegen. Dann ein einziges Mal durchführen.</h1>
            <p className="mt-6 max-w-[680px] text-[17px] leading-relaxed text-ink-2">
              Jede Modellrunde wurde aufgeschrieben, bevor sie lief: Merkmale, Datenaufteilung, Metriken und Bestehenskriterien. Ergebnisse – gute
              wie schlechte – werden so berichtet, wie sie herauskamen.
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
        <SectionHeader eyebrow="So funktioniert es" title="Vom Satellitenpixel zur Aussage über das Feld." lede="Sieben Schritte, jeder mit einer Regel, die Zukunftswissen ausschließt." />
        <div ref={ref} className="relative mx-auto mt-16 max-w-[880px]">
          <div className="absolute bottom-0 left-[19px] top-0 w-px bg-[var(--line)] sm:left-1/2">
            <motion.div className="w-full bg-gradient-to-b from-maize to-rust" style={{ height: reduce ? '100%' : h }} />
          </div>
          <ol className="flex flex-col gap-10">
            {PIPELINE_STEPS.map((s, i) => (
              <li key={s.key} className={`relative grid gap-4 pl-14 sm:grid-cols-2 sm:gap-16 sm:pl-0 ${i % 2 ? 'sm:[&>div]:col-start-2' : ''}`}>
                <span className="absolute left-[13px] top-2 size-[13px] rounded-full border-2 border-maize bg-soil-950 sm:left-1/2 sm:-translate-x-1/2" />
                <Reveal className={`panel p-6 ${i % 2 ? '' : 'sm:text-right'}`}>
                  <p className="font-mono text-[10.5px] uppercase tracking-[0.14em] text-maize">Schritt {i + 1} · {s.meta}</p>
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
  const fields = ['Feldgruppe 1', 'Feldgruppe 2', 'Feldgruppe 3', 'Feldgruppe 4']
  const schemes = [
    {
      key: 'lofyo',
      name: 'Feldgruppe und Jahr auslassen',
      body: 'Testzelle: eine Feldgruppe in einem Jahr. Das Training schließt dieses ganze Jahr und diese ganze Feldgruppe aus – das Modell sieht keines von beiden.',
      used: 'Feldmodelle, Stress-Score',
      cell: (f: number, y: number) => (f === 1 && y === 3 ? 'test' : f === 1 || y === 3 ? 'gap' : 'train'),
    },
    {
      key: 'lofo',
      name: 'Ein Feld auslassen',
      body: 'Teilflächenmodelle werden auf den anderen Feldern trainiert und auf den Zellen eines Feldes bewertet, das sie nie gesehen haben.',
      used: 'Teilflächenmodell M1',
      cell: (f: number) => (f === 2 ? 'test' : 'train'),
    },
    {
      key: 'loco',
      name: 'Ein Land auslassen',
      body: 'Jedes EU-Land wird von einem Modell vorhergesagt, das auf den anderen 15 trainiert wurde. Österreich ist in keinem Durchgang enthalten.',
      used: 'EU-Regionalmodell',
      cell: (f: number) => (f === 0 ? 'test' : 'train'),
    },
  ]
  const color = { train: 'bg-sage/35', test: 'bg-maize', gap: 'bg-white/[0.04]' }
  return (
    <section className="py-20">
      <Container>
        <SectionHeader eyebrow="Validierung" title="Zurückgehalten heißt zurückgehalten." lede="Drei Schemata zum Zurückhalten von Testdaten – so gewählt, dass ein Modell nie ein Feld, ein Jahr oder ein Land wiedererkennen kann, an dem es getestet wird." />
        <div className="mt-12 grid gap-5 lg:grid-cols-3">
          {schemes.map((s, si) => (
            <Reveal key={s.key} delay={si * 0.06} className="panel p-6">
              <p className="eyebrow">{s.used}</p>
              <h3 className="mt-3 text-[19px]">{s.name}</h3>
              <div className="mt-6 grid gap-1" style={{ gridTemplateColumns: `repeat(${years.length}, minmax(0, 1fr))` }} aria-hidden>
                {fields.map((_, f) => years.map((__, y) => <span key={`${f}-${y}`} className={`aspect-square rounded-[4px] ${color[s.cell(f, y) as keyof typeof color]}`} />))}
              </div>
              <div className="mt-2 flex justify-between font-mono text-[9.5px] text-ink-4">
                <span>{s.key === 'loco' ? 'Jahre →' : years[0]}</span>
                <span>{s.key === 'loco' ? 'Zeilen = Länder' : years.at(-1)}</span>
              </div>
              <p className="mt-5 text-[13.5px] leading-relaxed text-ink-2">{s.body}</p>
            </Reveal>
          ))}
        </div>
        <div className="mt-5 flex flex-wrap gap-5 text-[12.5px] text-ink-3">
          <span className="flex items-center gap-2"><span className="size-3 rounded-[3px] bg-maize" />Test</span>
          <span className="flex items-center gap-2"><span className="size-3 rounded-[3px] bg-sage/35" />Training</span>
          <span className="flex items-center gap-2"><span className="size-3 rounded-[3px] bg-white/[0.06]" />von beidem ausgeschlossen</span>
        </div>
        <Reveal className="mt-10 grid gap-5 md:grid-cols-3">
          {[
            ['Label-Shuffle', 'Die Erträge werden zufällig vertauscht. Jedes Modell muss dann auf Baseline-Niveau fallen; eines, das das nicht tut, würde Leakage verraten.'],
            ['Adversarial Validation', 'Kann ein Klassifikator Trainings- von Testzeilen unterscheiden? Michigan und Maryland trennt er perfekt – deshalb wird die Übertragung zwischen Standorten getrennt berichtet.'],
            ['Stichtagsregel', 'Ein Merkmal für den Prognosestichtag t nutzt nur Beobachtungen, die vor t gemacht wurden. Ein eigener Test (test_no_leakage.py) erzwingt das.'],
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

/** The 'deliberately excluded' group, identified by its source path so it survives title translation. */
const isExcluded = (g: { source: string }) => g.source.includes('test_no_leakage')

function Features() {
  return (
    <section className="py-20">
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

function Experiments() {
  return (
    <section id="experiments" className="scroll-mt-20 py-20">
      <Container>
        <SectionHeader
          eyebrow="Experimente"
          title={`${EXPERIMENTS.length} Schritte, in der Reihenfolge, in der sie stattfanden.`}
          lede={`Jeder Schritt änderte genau eine Sache und wurde an vorab festgelegten Kriterien gemessen. ${EXPERIMENTS.filter((e) => e.status === 'failed').length} davon sind gescheitert; sie stehen mit derselben Sorgfalt hier wie die Erfolge.`}
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
                  <span className="text-ink-3">Geändert: </span>
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
