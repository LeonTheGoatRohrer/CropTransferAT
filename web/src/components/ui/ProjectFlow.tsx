import { motion, useReducedMotion } from 'motion/react'
import { ArrowDown, ArrowRight, Cpu, Database, Flag, Layers, Lock, ShieldCheck, Sprout, type LucideIcon } from 'lucide-react'

type Step = { n: number; icon: LucideIcon; title: string; text: string; facts: string[] }

/** Numbers below come from src/data/content/project.ts (data sources) and evidence.json (results). */
const TRAIN: Step[] = [
  {
    n: 1,
    icon: Database,
    title: 'Daten sammeln',
    text: 'Nur öffentliche Daten aus den USA und der EU.',
    facts: ['Gemessene Erträge: 294 Parzellen-Jahre (Michigan), 61 Felder mit Ertragskarte (Maryland)', 'Satellit, Wetter, Boden', '8 371 Region-Jahre aus 16 EU-Ländern'],
  },
  {
    n: 2,
    icon: Layers,
    title: 'Aufbereiten',
    text: 'Wolken entfernen, die Saison in 10-Tage-Abschnitte teilen.',
    facts: ['Grünwert (NDVI) je Feld und je 10 × 10 m', 'Gesunde Referenzkurve aus Feldern mit normaler Ernte'],
  },
  {
    n: 3,
    icon: Cpu,
    title: 'Modelle bauen',
    text: 'Drei Modelle für drei Fragen.',
    facts: ['Teilflächenkarte: wo im Feld?', 'Stress-Score: welches Feld?', 'EU-Regionalmodell: welches Jahr?'],
  },
  {
    n: 4,
    icon: ShieldCheck,
    title: 'Ehrlich prüfen',
    text: 'Getestet nur an Feldern, Jahren und Ländern, die das Modell nie gesehen hat.',
    facts: ['Erfolgskriterien vorher schriftlich festgelegt', 'Gegenprobe mit vertauschten Erträgen'],
  },
  {
    n: 5,
    icon: Lock,
    title: 'Einfrieren',
    text: 'Modelle mit Prüfsummen festgeschrieben.',
    facts: ['Danach wird nichts mehr verändert'],
  },
]

/** Visual overview of the whole project: data → preparation → models → testing → freeze → Austria. */
export function ProjectFlow() {
  const reduce = useReducedMotion()
  const appear = (i: number) => ({
    initial: reduce ? false : { opacity: 0, y: 14 },
    whileInView: { opacity: 1, y: 0 },
    viewport: { once: true, margin: '-60px' },
    transition: { duration: 0.6, delay: i * 0.09, ease: [0.22, 1, 0.36, 1] as const },
  })
  return (
    <div className="grid gap-4 xl:grid-cols-[1fr_auto_250px] xl:items-stretch">
      {/* Training zone: USA + EU only */}
      <div className="rounded-2xl border border-water/25 bg-water/[0.04] p-4 sm:p-5">
        <p className="eyebrow mb-4 flex items-center gap-2 !text-water">
          <span className="inline-block size-1.5 rounded-full bg-water" /> Trainiert nur mit Daten aus den USA und der EU
        </p>
        <ol className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {TRAIN.map((s, i) => (
            <motion.li key={s.n} {...appear(i)} className="relative flex flex-col rounded-xl border border-[var(--line)] bg-soil-900/80 p-4">
              <div className="flex items-center gap-2.5">
                <span className="grid size-8 shrink-0 place-items-center rounded-full bg-water/15 font-mono text-[13px] font-semibold text-water">{s.n}</span>
                <s.icon className="size-4 text-ink-3" />
              </div>
              <h3 className="mt-3 text-[17px] leading-tight">{s.title}</h3>
              <p className="mt-1.5 text-[13px] leading-snug text-ink-2">{s.text}</p>
              <ul className="mt-3 flex flex-col gap-1.5 border-t border-[var(--line)] pt-3">
                {s.facts.map((f) => (
                  <li key={f} className="flex gap-2 text-[12px] leading-snug text-ink-3">
                    <span className="mt-[6px] size-1 shrink-0 rounded-full bg-ink-4" />
                    {f}
                  </li>
                ))}
              </ul>
              {i < TRAIN.length - 1 && (
                <ArrowRight className="absolute -right-[13px] top-7 z-10 hidden size-4 rounded-full bg-soil-950 text-ink-3 lg:block" />
              )}
            </motion.li>
          ))}
        </ol>
      </div>

      <div className="flex items-center justify-center text-maize">
        <ArrowRight className="hidden size-6 xl:block" />
        <ArrowDown className="size-6 xl:hidden" />
      </div>

      {/* Austria zone: one test, then the next step */}
      <div className="flex flex-col gap-3 rounded-2xl border border-maize/30 bg-maize/[0.05] p-4 sm:p-5">
        <p className="eyebrow flex items-center gap-2 !text-maize">
          <span className="inline-block size-1.5 rounded-full bg-maize" /> Österreich
        </p>
        <motion.div {...appear(5)} className="flex flex-1 flex-col rounded-xl border border-[var(--line)] bg-soil-900/80 p-4">
          <div className="flex items-center gap-2.5">
            <span className="grid size-8 place-items-center rounded-full bg-maize/15 font-mono text-[13px] font-semibold text-maize">6</span>
            <Flag className="size-4 text-ink-3" />
          </div>
          <h3 className="mt-3 text-[17px] leading-tight">Einmal testen</h3>
          <p className="mt-1.5 text-[13px] leading-snug text-ink-2">Die eingefrorenen Modelle an österreichischen Erträgen: 34 Versuchs-Jahre in Oberösterreich und 30 Bundesland-Jahre.</p>
          <p className="mt-3 border-t border-[var(--line)] pt-3 text-[12px] leading-snug text-ink-3">
            Gute und schlechte Jahre: <span className="text-sage">ja</span> · einzelne Standorte: <span className="text-maize">noch nicht</span>
          </p>
        </motion.div>
        <motion.div {...appear(6)} className="rounded-xl border border-dashed border-maize/40 p-4">
          <div className="flex items-center gap-2 text-maize">
            <Sprout className="size-4" />
            <p className="text-[14px] font-medium">Nächster Schritt</p>
          </div>
          <p className="mt-1.5 text-[12.5px] leading-snug text-ink-2">Mit Feld-Erträgen aus Österreich – von Landwirten über die Website oder von Hagelversicherungen – nachtrainieren.</p>
        </motion.div>
      </div>
    </div>
  )
}
