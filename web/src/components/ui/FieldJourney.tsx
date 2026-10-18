import { motion, useReducedMotion } from 'motion/react'
import { ArrowDown, ArrowRight, CloudRain, Layers, Map as MapIcon, Mountain, PenLine, RefreshCw, Satellite, Siren, TrendingUp, type LucideIcon } from 'lucide-react'
import type { ReactNode } from 'react'
import { Link } from 'react-router'
import type { Evidence } from '../../api/types'
import { fmt, fmtInt, fmtPct } from '../../lib/format'

/**
 * Landing-page overview: what happens to a field after it is entered – data, preparation, the three models
 * and the result. Model numbers come from evidence.json (same values as on the Belege page).
 */
export function FieldJourney({ ev }: { ev?: Evidence }) {
  const reduce = useReducedMotion()
  const appear = (i: number) => ({
    initial: reduce ? false : { opacity: 0, y: 16 },
    whileInView: { opacity: 1, y: 0 },
    viewport: { once: true, margin: '-60px' },
    transition: { duration: 0.6, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] as const },
  })
  const b0 = ev?.innerfeld_main.untrained.BARC.B0
  const map = ev?.within_field_map
  const al = ev?.alarm
  const eu = ev?.eu_cutoffs.find((c) => c.cutoff === '09-01')
  const models: { name: string; q: string; value: string; unit: string; note: string }[] = [
    { name: 'Teilflächenkarte', q: 'Wo im Feld wächst weniger?', value: map ? `× ${fmt(map.median_lift, 1)}` : '…', unit: 'besser als Zufall', note: b0 ? `Übereinstimmung mit der Ertragskarte ${fmt(b0.rho_median, 2)}` : '' },
    { name: 'Feld-Stress-Score', q: 'Ist die Saison dieses Felds auffällig?', value: al ? fmtPct(al.alarm_recall) : '…', unit: 'der schlechten Jahre erkannt', note: 'bei höchstens 20 % Fehlalarmen' },
    { name: 'EU-Regionalmodell', q: 'Wird es in der Region ein schlechtes Jahr?', value: eu ? String(eu.countries) : '…', unit: 'EU-Länder getestet', note: eu ? `${fmtInt(eu.n)} Region-Jahre · statistisch gesichert` : '' },
  ]
  return (
    <div>
      <div className="grid items-stretch gap-3 lg:grid-cols-[0.9fr_16px_1.05fr_16px_1fr_16px_1.6fr_16px_1.05fr] lg:gap-2">
        <Step i={0} appear={appear} n={1} icon={PenLine} title="Feld eintragen">
          <p>Umriss auf der Satellitenkarte einzeichnen, dazu die Erträge der letzten Jahre.</p>
          <FieldSketch />
        </Step>
        <Arrow />
        <Step i={1} appear={appear} n={2} icon={Satellite} title="Daten sammeln">
          <Source icon={Satellite} t="Satellit" d="Sentinel-2, etwa alle 5 Tage, 10 × 10 m" />
          <Source icon={CloudRain} t="Wetter" d="Regen, Hitze, Bodenfeuchte – jeden Tag" />
          <Source icon={Mountain} t="Boden" d="Bodenart, Wasserspeicher, Gelände" />
        </Step>
        <Arrow />
        <Step i={2} appear={appear} n={3} icon={Layers} title="Aufbereiten">
          <p>Wolken entfernen, die Saison in 10-Tage-Abschnitte teilen, die Grünkurve des Felds bilden.</p>
          <CurveSketch />
        </Step>
        <Arrow />
        <motion.div {...appear(3)} className="flex flex-col rounded-2xl border border-maize/30 bg-maize/[0.05] p-4">
          <Head n={4} icon={TrendingUp} title="Drei Modelle rechnen" />
          <div className="mt-3 flex flex-1 flex-col gap-2.5">
            {models.map((m) => (
              <Link key={m.name} to="/model" className="group rounded-xl border border-[var(--line)] bg-soil-900/80 p-3 transition hover:border-maize/40">
                <p className="text-[14.5px] font-medium leading-tight text-ink group-hover:text-maize">{m.name}</p>
                <p className="mt-0.5 text-[12.5px] leading-snug text-ink-3">{m.q}</p>
                <p className="mt-2 flex items-baseline gap-2">
                  <span className="whitespace-nowrap font-display text-[22px] font-semibold leading-none tracking-[-0.03em] text-maize tabular">{m.value}</span>
                  <span className="text-[12px] leading-tight text-ink-2">{m.unit}</span>
                </p>
                {m.note && <p className="mt-1 text-[11.5px] leading-snug text-ink-4">{m.note}</p>}
              </Link>
            ))}
          </div>
        </motion.div>
        <Arrow />
        <Step i={4} appear={appear} n={5} icon={MapIcon} title="Ergebnis">
          <Source icon={MapIcon} t="Feldkarte" d="Welche Zonen zurückbleiben" />
          <Source icon={Siren} t="Warnung" d="Wenn die Saison deutlich unter gesunden Feldern liegt" />
          <Source icon={TrendingUp} t="Vergleich" d="Dieses Jahr gegenüber dem eigenen Durchschnitt" />
        </Step>
      </div>
      <motion.div {...appear(5)} className="mt-3 flex items-center gap-3 rounded-2xl border border-dashed border-sage/40 bg-sage/[0.05] px-5 py-4">
        <RefreshCw className="size-5 shrink-0 text-sage" />
        <p className="text-[14px] leading-snug text-ink-2">
          <span className="font-medium text-ink">Der Kreislauf:</span> Jeder eingetragene Ertrag fließt ins nächste Training ein – so lernen die
          Modelle österreichische Felder kennen und werden mit jedem Feld genauer.
        </p>
      </motion.div>
    </div>
  )
}

type Appear = (i: number) => object

function Head({ n, icon: Icon, title }: { n: number; icon: LucideIcon; title: string }) {
  return (
    <div className="flex items-center gap-2.5">
      <span className="grid size-7 shrink-0 place-items-center rounded-full bg-maize/15 font-mono text-[12px] font-semibold text-maize">{n}</span>
      <h3 className="text-[17px] leading-tight">{title}</h3>
      <Icon className="ml-auto size-4 text-ink-4" />
    </div>
  )
}

function Step({ i, appear, n, icon, title, children }: { i: number; appear: Appear; n: number; icon: LucideIcon; title: string; children: ReactNode }) {
  return (
    <motion.div {...appear(i)} className="flex flex-col rounded-2xl border border-[var(--line)] bg-soil-900/80 p-4">
      <Head n={n} icon={icon} title={title} />
      <div className="mt-3 flex flex-1 flex-col gap-2.5 text-[13.5px] leading-snug text-ink-2">{children}</div>
    </motion.div>
  )
}

function Source({ icon: Icon, t, d }: { icon: LucideIcon; t: string; d: string }) {
  return (
    <div className="flex gap-2.5">
      <Icon className="mt-0.5 size-4 shrink-0 text-sage" />
      <p>
        <span className="font-medium text-ink">{t}</span>
        <span className="block text-[12.5px] text-ink-3">{d}</span>
      </p>
    </div>
  )
}

function Arrow() {
  return (
    <div className="flex items-center justify-center text-ink-4">
      <ArrowRight className="hidden size-5 lg:block" />
      <ArrowDown className="size-5 lg:hidden" />
    </div>
  )
}

/** Schematic field outline on a 10-m grid (illustration only). */
function FieldSketch() {
  return (
    <svg viewBox="0 0 160 70" className="mt-auto w-full" aria-hidden>
      {Array.from({ length: 16 }, (_, x) => Array.from({ length: 7 }, (_, y) => <rect key={`${x}-${y}`} x={x * 10 + 0.5} y={y * 10 + 0.5} width={9} height={9} rx={1} fill="var(--color-soil-700)" />))}
      <path d="M22 10 L128 6 L142 52 L34 62 Z" fill="rgba(230,180,80,0.14)" stroke="var(--color-maize)" strokeWidth={1.6} strokeLinejoin="round" />
      {[[22, 10], [128, 6], [142, 52], [34, 62]].map(([x, y]) => <circle key={`${x}`} cx={x} cy={y} r={2.6} fill="var(--color-maize-soft)" />)}
    </svg>
  )
}

/** Schematic season curve: field (maize) vs healthy reference (sage), illustration only. */
function CurveSketch() {
  return (
    <svg viewBox="0 0 160 70" className="mt-auto w-full" aria-hidden>
      <path d="M4 60 C40 60 52 58 66 40 C78 22 92 12 110 12 C128 12 140 30 156 52" fill="none" stroke="var(--color-sage)" strokeWidth={1.6} strokeDasharray="3 3" />
      <path d="M4 61 C42 61 56 60 70 46 C82 33 94 24 110 24 C126 24 140 36 156 54" fill="none" stroke="var(--color-maize)" strokeWidth={2} />
      {[16, 36, 56, 76, 96, 116, 136].map((x, i) => <circle key={x} cx={x} cy={[61, 61, 58, 42, 27, 24, 37][i]} r={2.2} fill="var(--color-maize)" />)}
      <text x={4} y={8} fontSize={8} fill="var(--color-ink-4)">Grünwert</text>
      <text x={156} y={68} fontSize={8} textAnchor="end" fill="var(--color-ink-4)">Apr → Okt</text>
    </svg>
  )
}
