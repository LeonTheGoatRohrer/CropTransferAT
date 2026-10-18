import { motion } from 'motion/react'
import { Eye, Info } from 'lucide-react'
import { useMemo, useState, type ReactNode } from 'react'
import type { FieldAnalysis, IndexName } from '../../api/types'
import { ndviColor, relYieldColor, tokens } from '../../lib/color'
import { cumulative, lastCompleteDekad } from '../../lib/dekads'
import { fmt, fmtArea, fmtInt, fmtPct, fmtSigned } from '../../lib/format'
import { phaseLabel } from '../../services/fieldService'
import { SeasonChart } from '../charts/SeasonChart'
import { Scatter } from '../charts/Stats'
import { WeatherChart, type WeatherMode } from '../charts/WeatherChart'
import { Legend } from '../charts/core'
import { Badge, SimulatedBadge } from '../ui/Badge'
import { Reveal } from '../ui/Reveal'
import { Source } from '../ui/Section'
import { Tabs } from '../ui/Tabs'
import { PixelField, type PixelMode } from './PixelField'

const CUTOFF = lastCompleteDekad(9, 1)

function Block({ eyebrow, title, aside, children, id }: { eyebrow: string; title: string; aside?: ReactNode; children: ReactNode; id?: string }) {
  return (
    <Reveal>
      <section id={id} className="panel p-6 sm:p-8">
        <div className="mb-7 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="eyebrow mb-2">{eyebrow}</p>
            <h3 className="text-[24px] leading-tight">{title}</h3>
          </div>
          {aside}
        </div>
        {children}
      </section>
    </Reveal>
  )
}

/* ------------------------------------------------------------------ */
/* Assessment                                                          */
/* ------------------------------------------------------------------ */

export function Assessment({ f }: { f: FieldAnalysis }) {
  const s = f.stress
  const [revealed, setRevealed] = useState(false)
  if (!s) return null
  const alarm = s.alarm
  const pct = Math.max(0, Math.min(1, s.risk_p))
  const outcome = f.measured
  const mainPhase = phaseLabel(s.main_phase)
  const verdict = outcome.at_risk == null ? null : alarm === outcome.at_risk ? 'correct' : alarm ? 'false-alarm' : 'missed'
  return (
    <div className="grid gap-5 lg:grid-cols-[1.35fr_1fr]">
      <Reveal className="panel relative overflow-hidden p-7 sm:p-9">
        <div className={`pointer-events-none absolute -right-24 -top-24 size-72 rounded-full blur-3xl ${alarm ? 'bg-rust/15' : 'bg-sage/10'}`} />
        <div className="flex flex-wrap items-center gap-2">
          <p className="eyebrow">Stress-Bewertung · Stand 1. September {f.year}</p>
          {f.simulated && <SimulatedBadge />}
        </div>
        <div className="mt-6 flex flex-wrap items-end gap-x-10 gap-y-6">
          <div>
            <p className={`font-display text-[clamp(3.2rem,6vw,4.6rem)] font-semibold leading-none tracking-[-0.04em] ${alarm ? 'text-rust' : 'text-sage'}`}>
              {alarm ? 'Alarm' : 'Kein Alarm'}
            </p>
            <p className="mt-3 max-w-[420px] text-[14.5px] leading-relaxed text-ink-2">
              {alarm
                ? `Die Saisonkurve liegt deutlich unter der gesunden Referenz, vor allem im ${mainPhase ?? 'Hochsommer'}. Ein Alarm bedeutet „ungewöhnliche Kurve“ – Stress oder zum Beispiel eine späte Aussaat.`
                : 'Die Saisonkurve bleibt nahe an der gesunden Referenz. Das Feld wird nicht markiert.'}
            </p>
          </div>
          <dl className="grid grid-cols-2 gap-x-8 gap-y-4">
            <div>
              <dt className="eyebrow">Stress-Score</dt>
              <dd className="mt-1 font-mono text-[22px] tabular">{fmtSigned(s.score, 3)}</dd>
            </div>
            <div>
              <dt className="eyebrow">Größte Abweichung</dt>
              <dd className="mt-1 font-mono text-[22px]">{mainPhase ?? '–'}</dd>
            </div>
          </dl>
        </div>
        <div className="mt-9">
          <div className="flex justify-between font-mono text-[11px] text-ink-3">
            <span>Risiko für ≥ 15 % Ertragsausfall</span>
            <span className="tabular text-ink">{fmt(s.risk_p, 2)}</span>
          </div>
          <div className="relative mt-2 h-2.5 rounded-full bg-white/[0.06]">
            <motion.div
              className={`absolute inset-y-0 left-0 rounded-full ${alarm ? 'bg-rust' : 'bg-sage'}`}
              initial={{ width: 0 }}
              whileInView={{ width: `${pct * 100}%` }}
              viewport={{ once: true }}
              transition={{ duration: 1.1, ease: [0.22, 1, 0.36, 1] }}
            />
            <div className="absolute -top-1.5 bottom-[-6px] w-px bg-ink" style={{ left: `${s.threshold * 100}%` }} />
          </div>
          <div className="relative mt-2 h-4 font-mono text-[10.5px] text-ink-3">
            <span className="absolute -translate-x-1/2 whitespace-nowrap" style={{ left: `${s.threshold * 100}%` }}>
              Alarmschwelle {fmt(s.threshold, 2)} · ≤ 20 % Fehlalarme
            </span>
          </div>
        </div>
      </Reveal>

      <Reveal delay={0.08} className="panel flex flex-col p-7 sm:p-9">
        <p className="eyebrow">Was tatsächlich geschah</p>
        {f.simulated || outcome.relative_yield == null ? (
          <div className="mt-6 flex flex-1 flex-col justify-center gap-3 text-[14.5px] leading-relaxed text-ink-2">
            <p className="text-ink">Für dieses Feld gibt es keinen gemessenen Ertrag.</p>
            <p>Vorbereitete Felder haben die Messung des Mähdreschers, daher lässt sich jedes Ergebnis prüfen. Für ein gezeichnetes Feld gibt es keine Vergleichsmessung.</p>
          </div>
        ) : !revealed ? (
          <div className="mt-6 flex flex-1 flex-col items-start justify-center gap-4">
            <p className="text-[14.5px] leading-relaxed text-ink-2">
              Dieses Feld-Jahr blieb beim Anpassen des Modells außen vor. Sein gemessener Ertrag ist bekannt – vergleichen Sie ihn mit der Bewertung.
            </p>
            <button
              type="button"
              onClick={() => setRevealed(true)}
              className="inline-flex items-center gap-2 rounded-[var(--radius-control)] border border-[var(--line-strong)] px-4 py-2.5 text-[14px] font-medium text-ink transition hover:border-maize hover:text-maize"
            >
              <Eye className="size-4" /> Ergebnis aufdecken
            </button>
          </div>
        ) : (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="mt-6 flex flex-1 flex-col">
            <p className="font-display text-[clamp(2.8rem,5vw,3.8rem)] font-semibold leading-none tracking-[-0.04em]">
              {fmt(outcome.yield_t_ha, 1)}
              <span className="ml-2 text-[0.38em] font-medium tracking-normal text-ink-3">t/ha</span>
            </p>
            <p className="mt-3 text-[14.5px] text-ink-2">
              {fmtPct(outcome.relative_yield)} des üblichen Ertrags dieses Feldes ·{' '}
              <span className={outcome.at_risk ? 'text-rust' : 'text-sage'}>{outcome.at_risk ? 'gefährdet (≥ 15 % Ausfall)' : 'nicht gefährdet'}</span>
            </p>
            {f.title && (
              <div className="mt-5 border-t border-[var(--line)] pt-4">
                <p className="text-[15px] font-medium text-ink">{f.title}</p>
                <p className="mt-1 text-[13.5px] leading-relaxed text-ink-3">{f.blurb}</p>
              </div>
            )}
            <div className="mt-auto pt-6">
              {verdict === 'correct' && <Badge tone="sage" dot>{alarm ? 'Richtiger Alarm' : 'Zu Recht kein Alarm'}</Badge>}
              {verdict === 'false-alarm' && <Badge tone="maize" dot>Fehlalarm</Badge>}
              {verdict === 'missed' && <Badge tone="water" dot>Übersehener Ausfall</Badge>}
            </div>
          </motion.div>
        )}
      </Reveal>
    </div>
  )
}

/* ------------------------------------------------------------------ */
/* Phase contributions                                                  */
/* ------------------------------------------------------------------ */

export function PhaseContributions({ f, typical }: { f: FieldAnalysis; typical?: { at_risk: Record<string, number>; not_at_risk: Record<string, number> } }) {
  const s = f.stress
  if (!s) return null
  // Same month windows as the stress model: dekads 6-8 (31.5.-29.6.), 9-11, 12-14 (fj_product.PHASES).
  const rows = [
    { key: 'Jun' as const, label: 'Juni', t: 'Juni', dekads: [6, 7, 8] },
    { key: 'Jul' as const, label: 'Juli', t: 'Juli', dekads: [9, 10, 11] },
    { key: 'Aug' as const, label: 'August', t: 'August', dekads: [12, 13, 14] },
  ]
  const ndvi = f.satellite.indices.ndvi ?? []
  // below (<= 0, counts for the score) and above (>= 0, ignored by the score) the healthy reference
  const part = (k: 'Jun' | 'Jul' | 'Aug') => s.phase_parts?.[k] ?? { below: s.phases[k] ?? 0, above: 0 }
  const span = Math.max(0.35, ...rows.flatMap((r) => [-(part(r.key).below ?? 0), part(r.key).above ?? 0]))
  const w = (v: number) => `${(Math.abs(v) / span) * 50}%` // each side is half the track
  const at = (v: number) => `${50 + (v / span) * 50}%`
  const MIN = 0.005
  return (
    <Block eyebrow="Woher die Abweichung kommt" title="Abstand zur gesunden Kurve, je Monat">
      <div className="mb-2 grid grid-cols-[120px_1fr_96px] gap-4 font-mono text-[10.5px] text-ink-4">
        <span />
        <div className="flex justify-between">
          <span>← unter der Referenz (Rückstand)</span>
          <span>über der Referenz →</span>
        </div>
        <span />
      </div>
      <div className="flex flex-col gap-5">
        {rows.map((r) => {
          const below = part(r.key).below ?? 0
          const above = part(r.key).above ?? 0
          const seen = r.dekads.filter((i) => ndvi[i] != null).length
          const tr = typical?.at_risk[r.t]
          const tn = typical?.not_at_risk[r.t]
          return (
            <div key={r.key} className="grid grid-cols-[120px_1fr_96px] items-center gap-4">
              <span className="text-[14px] leading-tight text-ink">
                {r.label}
                <span className="mt-0.5 block font-mono text-[10.5px] text-ink-4" title="Ein Monat hat drei Dekaden (je 10 Tage). Gezählt sind die mit wolkenfreiem Satellitenbild.">
                  Bild in {seen} von 3 Dekaden
                </span>
              </span>
              <div className="relative h-7 rounded-md bg-white/[0.035]">
                <span className="absolute inset-y-0 left-1/2 w-px bg-ink-3/50" />
                <motion.div
                  className="absolute inset-y-1 right-1/2 rounded-l-[4px] bg-rust/80"
                  initial={{ width: 0 }}
                  whileInView={{ width: w(below) }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
                />
                <motion.div
                  className="absolute inset-y-1 left-1/2 rounded-r-[4px] bg-sage/80"
                  initial={{ width: 0 }}
                  whileInView={{ width: w(above) }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
                />
                {tn != null && <span className="absolute inset-y-0 w-px bg-ink-3" style={{ left: at(tn) }} title="Mittel nicht gefährdeter US-Felder" />}
                {tr != null && <span className="absolute inset-y-0 w-px bg-ink" style={{ left: at(tr) }} title="Mittel gefährdeter US-Felder" />}
              </div>
              <span className="flex flex-col items-end font-mono text-[13px] leading-tight tabular">
                {below < -MIN && <span className="text-rust">{fmtSigned(below, 2)}</span>}
                {above > MIN && <span className="text-sage">{fmtSigned(above, 2)}</span>}
                {below >= -MIN && above <= MIN && <span className="text-ink-3">0</span>}
              </span>
            </div>
          )
        })}
      </div>
      <Legend
        className="mt-6"
        items={[
          { label: 'Unter der Referenz', color: tokens.rust, kind: 'bar' },
          { label: 'Über der Referenz', color: tokens.sage, kind: 'bar' },
          ...(typical
            ? [
                { label: 'Rückstand im Mittel gefährdeter US-Felder', color: tokens.ink },
                { label: '… nicht gefährdeter US-Felder', color: tokens.ink3 },
              ]
            : []),
        ]}
      />
      <p className="mt-5 flex gap-2 text-[13px] leading-relaxed text-ink-3">
        <Info className="mt-0.5 size-3.5 shrink-0" />
        Summierter NDVI-Abstand zur gesunden Referenz je Monat. Eine Dekade sind 10 Tage, ein Monat hat drei; gezählt werden nur Dekaden mit
        wolkenfreiem Satellitenbild („Bild in 2 von 3 Dekaden“ heißt: In einem der drei 10-Tage-Abschnitte gab es keine wolkenfreie Aufnahme). Für
        Stress-Score und Alarm zählt nur der rote Teil; ein Vorsprung (grün) gleicht keinen Rückstand aus. Das erklärt den Alarm, ist aber
        keine Ursachenzuordnung. In den US-Daten kamen 22 von 31 Alarmen hauptsächlich aus dem Juli.
      </p>
      <Source className="mt-4">results/2026-10-16_feinjust_ablation/ranking.csv · product.json</Source>
    </Block>
  )
}

/* ------------------------------------------------------------------ */
/* Yield history                                                       */
/* ------------------------------------------------------------------ */

export function YieldHistory({ f }: { f: FieldAnalysis }) {
  const h = (f.history ?? []).filter((x) => x.yield_t_ha != null) as { year: number; yield_t_ha: number }[]
  if (h.length < 2) return null
  const max = Math.max(...h.map((x) => x.yield_t_ha))
  const others = h.filter((x) => x.year !== f.year)
  const mean = others.reduce((a, x) => a + x.yield_t_ha, 0) / Math.max(others.length, 1)
  const BAR = 120 // px for the highest year; the year label below takes 22 px
  const px = (v: number) => (v / max) * BAR
  return (
    <Block eyebrow="Ertragshistorie" title={`Gemessene Maiserträge dieses Feldes, ${h[0].year}–${h.at(-1)!.year}`}>
      <div className="relative flex h-44 items-end gap-1.5">
        <div className="pointer-events-none absolute inset-x-0 z-10 border-t border-dashed border-ink-3/70" style={{ bottom: 22 + px(mean) }} />
        {h.map((x) => {
          const cur = x.year === f.year
          return (
            <div key={x.year} className="flex h-full min-w-0 flex-1 flex-col items-center justify-end gap-1.5">
              <span className={`font-mono text-[10px] tabular ${cur ? 'text-maize' : 'text-ink-4'}`}>{fmt(x.yield_t_ha, 1)}</span>
              <motion.div
                className={`w-full max-w-[38px] shrink-0 rounded-t-[3px] ${cur ? 'bg-maize' : 'bg-white/15'}`}
                initial={{ height: 0 }}
                whileInView={{ height: px(x.yield_t_ha) }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
              />
              <span className={`h-4 font-mono text-[10.5px] leading-4 tabular ${cur ? 'text-maize' : 'text-ink-3'}`}>{h.length > 8 ? `’${String(x.year).slice(2)}` : x.year}</span>
            </div>
          )
        })}
      </div>
      <p className="mt-5 flex gap-2 text-[13px] leading-relaxed text-ink-3">
        <Info className="mt-0.5 size-3.5 shrink-0" />
        Gestrichelt: Mittel der anderen Jahre ({fmt(mean, 1)} t/ha). Nur Jahre mit Mais (Fruchtfolge). Der „übliche Ertrag“ für die Bewertung ist der Ertrag dieses Feldes in seinen anderen Jahren,
        bereinigt um den Ertragstrend über die Jahre – deshalb weicht er etwas vom einfachen Mittel ab.
      </p>
      <Source className="mt-4">data/processed/gt_field_years.parquet</Source>
    </Block>
  )
}

/* ------------------------------------------------------------------ */
/* Satellite                                                           */
/* ------------------------------------------------------------------ */

const INDEX_INFO: Record<IndexName, { label: string; domain: [number, number]; about: string }> = {
  ndvi: { label: 'NDVI', domain: [0, 1], about: 'Grüne Biomasse. Das Hauptsignal für den Stress-Score und die Feldkarte.' },
  evi: { label: 'EVI', domain: [0, 0.9], about: 'Wie NDVI, sättigt bei dichtem Bestand weniger.' },
  ndmi: { label: 'NDMI', domain: [-0.3, 0.6], about: 'Wassergehalt des Bestands (nahes vs. kurzwelliges Infrarot).' },
  ndre: { label: 'NDRE', domain: [0, 0.7], about: 'Red-Edge-Index, empfindlich für Chlorophyll in dichtem Mais.' },
  gndvi: { label: 'GNDVI', domain: [0, 0.9], about: 'Grün-NDVI.' },
}

export function SatellitePanel({ f }: { f: FieldAnalysis }) {
  const available = (['ndvi', 'evi', 'ndmi', 'ndre'] as IndexName[]).filter((k) => f.satellite.indices[k])
  const [idx, setIdx] = useState<IndexName>('ndvi')
  const vals = f.satellite.indices[idx] ?? []
  const ref = idx === 'ndvi' || idx === 'evi' || idx === 'ndmi' ? f.reference[idx] : undefined
  const health = useMemo(() => {
    const nd = f.satellite.indices.ndvi ?? []
    const r = f.reference.ndvi.median
    const win = [9, 10, 11, 12, 13, 14].filter((i) => nd[i] != null && r[i] != null)
    if (!win.length) return null
    const a = win.reduce((s, i) => s + (nd[i] as number), 0) / win.length
    const b = win.reduce((s, i) => s + (r[i] as number), 0) / win.length
    let peak = -1
    nd.forEach((v, i) => {
      if (v != null && (peak < 0 || v > (nd[peak] as number))) peak = i
    })
    return { a, b, diff: (a - b) / b, n: win.length, peak: peak >= 0 ? (nd[peak] as number) : null }
  }, [f])
  return (
    <Block
      eyebrow="Satelliten-Zeitreihe"
      title="Die Saison, Dekade für Dekade"
      aside={<Tabs label="Vegetationsindex" value={idx} onChange={setIdx} items={available.map((k) => ({ value: k, label: INDEX_INFO[k].label }))} />}
    >
      <div className="grid gap-8 lg:grid-cols-[1fr_250px]">
        <div>
          <SeasonChart values={vals} reference={ref} year={f.year} label={INDEX_INFO[idx].label} yDomain={INDEX_INFO[idx].domain} cutoff={CUTOFF} showShortfall={idx === 'ndvi'} height={320} />
          <Legend
            className="mt-4"
            items={[
              { label: `${INDEX_INFO[idx].label}, dieses Feld`, color: tokens.maize, kind: 'line' },
              ...(ref ? [{ label: `Gesunde Referenz (Median, IQR aus ${fmtInt(ref.n_fieldyears)} Feld-Jahren)`, color: tokens.sage, kind: 'band' as const }] : []),
              ...(idx === 'ndvi' ? [{ label: 'Rückstand ab Juni', color: tokens.rust, kind: 'bar' as const }] : []),
            ]}
          />
        </div>
        <div className="flex flex-col gap-6 border-[var(--line)] lg:border-l lg:pl-8">
          {health && (
            <div>
              <p className="eyebrow">Vegetationszustand · Jul–Aug</p>
              <p className="mt-2 font-display text-[40px] font-semibold leading-none tracking-[-0.03em] tabular">{fmt(health.a, 2)}</p>
              <p className={`mt-2 font-mono text-[13px] ${health.diff < 0 ? 'text-rust' : 'text-sage'}`}>{fmtSigned(health.diff * 100, 1)} % ggü. gesunder Referenz</p>
              <p className="mt-1 text-[12px] text-ink-4">mittlerer NDVI über {health.n} beobachtete Dekaden</p>
            </div>
          )}
          <dl className="grid grid-cols-2 gap-4 text-[13px]">
            <div><dt className="eyebrow">Szenen</dt><dd className="mt-1 font-mono tabular">{f.satellite.n_scenes}</dd></div>
            <div><dt className="eyebrow">Wolkenfrei</dt><dd className="mt-1 font-mono tabular">{f.satellite.n_clear_scenes}</dd></div>
            <div><dt className="eyebrow">Dekaden</dt><dd className="mt-1 font-mono tabular">{f.satellite.n_observed_dekads} / 21</dd></div>
            <div><dt className="eyebrow">NDVI-Maximum</dt><dd className="mt-1 font-mono tabular">{fmt(health?.peak, 2)}</dd></div>
          </dl>
          <p className="text-[12.5px] leading-relaxed text-ink-3">{INDEX_INFO[idx].about} Punkte sind beobachtete Dekaden; in Lücken gab es keine wolkenfreie Szene.</p>
        </div>
      </div>
    </Block>
  )
}

/* ------------------------------------------------------------------ */
/* Within-field map                                                    */
/* ------------------------------------------------------------------ */

export function WithinFieldPanel({ f }: { f: FieldAnalysis }) {
  const px = f.pixels
  const [mode, setMode] = useState<PixelMode>('weak')
  const pts = useMemo(
    () =>
      px
        ? px.cells
            .filter((c) => c[4] != null)
            .map((c) => ({ x: c[4] as number, y: c[5], color: (c[4] as number) <= px.weak_threshold ? tokens.rust : ndviColor(c[4] as number), r: 2.4 }))
        : [],
    [px],
  )
  if (!px) {
    return (
      <Block eyebrow="Teilflächenkarte" title="Welcher Teil des Feldes zurückbleibt">
        <p className="max-w-[640px] text-[14.5px] leading-relaxed text-ink-2">
          Dieses Feld ist eine {fmtArea(f.area_m2)} große Versuchsparzelle ohne Mähdrescher-Ertragskarte, daher lässt sich die 10-m-Karte
          hier nicht prüfen. Die Karte wurde an den BARC-Feldern (Feld A, B und E) geprüft.
        </p>
      </Block>
    )
  }
  const sim = Boolean(f.simulated)
  return (
    <Block
      id="within-field"
      eyebrow="Teilflächenkarte"
      title="Welcher Teil des Feldes zurückbleibt"
      aside={
        <Tabs
          label="Kartenebene"
          value={mode}
          onChange={setMode}
          items={[
            { value: 'weak', label: 'Schwache Zonen' },
            { value: 'window', label: 'NDVI Jul–Aug' },
            { value: 'yield', label: sim ? 'Ertrag (simuliert)' : 'Gemessener Ertrag' },
          ]}
        />
      }
    >
      <div className="grid gap-8 lg:grid-cols-[1.25fr_1fr]">
        <div className="rounded-xl bg-black/25 p-4">
          <PixelField pixels={px} mode={mode} maxHeight={380} />
          <div className="mt-4 flex flex-wrap items-center gap-4 text-[11.5px] text-ink-3">
            {mode === 'yield' ? (
              [0.5, 0.85, 1, 1.2].map((v) => (
                <span key={v} className="flex items-center gap-1.5"><span className="size-2.5 rounded-[2px]" style={{ background: relYieldColor(v) }} />{Math.round(v * 100)} % des Feldmittels</span>
              ))
            ) : mode === 'weak' ? (
              <span className="flex items-center gap-1.5"><span className="size-2.5 rounded-[2px] bg-rust" />Unterstes NDVI-Viertel (≤ {fmt(px.weak_threshold, 2)})</span>
            ) : (
              <span className="font-mono">{px.window}</span>
            )}
          </div>
        </div>
        <div className="flex flex-col gap-6">
          {!sim ? (
            <dl className="grid grid-cols-2 gap-x-6 gap-y-5">
              <div><dt className="eyebrow">Rangkorrelation <span className="normal-case">ρ</span></dt><dd className="mt-1 font-display text-[32px] font-semibold tabular text-sage">{fmt(px.rho, 2)}</dd></div>
              <div><dt className="eyebrow">Markierte Zellen wirklich schwach</dt><dd className="mt-1 font-display text-[32px] font-semibold tabular">{fmtPct(px.precision_weak)}</dd></div>
              <div><dt className="eyebrow">Anteil schwach insgesamt</dt><dd className="mt-1 font-mono text-[18px] tabular text-ink-2">{fmtPct(px.prevalence_problem)}</dd></div>
              <div><dt className="eyebrow">Lift ggü. Zufall</dt><dd className="mt-1 font-mono text-[18px] tabular text-ink-2">× {fmt(px.lift, 1)}</dd></div>
            </dl>
          ) : (
            <p className="text-[14px] leading-relaxed text-ink-2">Das Muster ist simuliert. Für ein gezeichnetes Feld würde das Backend echte Sentinel-2-Zellen auslesen; eine Ertragskarte zum Vergleich gibt es nicht.</p>
          )}
          <Scatter
            points={pts}
            xLabel="NDVI, 10. Jul – 18. Aug"
            yLabel="Ertrag / Feldmittel"
            height={230}
            hLines={[{ v: 0.85, label: 'ertragsschwache Zone < 85 %', color: tokens.rust }]}
            vLines={[{ v: px.weak_threshold, color: tokens.ink3 }]}
            xFmt={(v) => fmt(v, 2)}
            yFmt={(v) => fmt(v, 1)}
            yDomain={[0.2, 1.6]}
            opacity={0.6}
          />
        </div>
      </div>
      <p className="mt-6 text-[13px] leading-relaxed text-ink-3">
        {fmtInt(px.n_cells)} Zellen zu {fmt(px.cell_m, 0)} m. Regel B0 braucht kein Training: Sie reiht die Zellen nach ihrem eigenen NDVI.
        Über 41 BARC-Feld-Jahre liegt der Median von ρ bei 0,67.
      </p>
      {!sim && <Source className="mt-3">data/processed/features_innerfeld.parquet · data/interim/pixels_dekad · Regel B0 wie in innerfeld_run.py</Source>}
    </Block>
  )
}

/* ------------------------------------------------------------------ */
/* Weather                                                             */
/* ------------------------------------------------------------------ */

export function WeatherPanel({ f }: { f: FieldAnalysis }) {
  const [mode, setMode] = useState<WeatherMode>('rain')
  const w = f.weather
  const sum = (xs: (number | null)[]) => xs.reduce<number>((a, b) => a + (b ?? 0), 0)
  const rain = sum(w.dekads.prec)
  const rainN = sum(w.normal.prec)
  const jul = (xs: (number | null)[]) => sum(xs.slice(9, 15))
  const gdd = cumulative(w.dekads.gdd).at(-1) ?? 0
  const gddN = cumulative(w.normal.gdd).at(-1) ?? 0
  const heat = sum(w.dekads.heat ?? [])
  return (
    <Block
      eyebrow="Wetter · ERA5-Land"
      title="Diese Saison im Vergleich zum langjährigen Mittel"
      aside={
        <Tabs
          label="Wettergröße"
          value={mode}
          onChange={setMode}
          items={[
            { value: 'rain', label: 'Niederschlag' },
            { value: 'temperature', label: 'Temperatur' },
            { value: 'gdd', label: 'Gradtage' },
            { value: 'moisture', label: 'Bodenfeuchte' },
          ]}
        />
      }
    >
      <div className="grid gap-8 lg:grid-cols-[1fr_250px]">
        <div>
          <WeatherChart actual={w.dekads} normal={w.normal} mode={mode} year={f.year} height={290} />
          <Legend
            className="mt-4"
            items={[
              { label: `${f.year}`, color: mode === 'temperature' ? tokens.rust : mode === 'gdd' ? tokens.maize : tokens.water, kind: 'line' },
              { label: `Mittel ${w.climatology_years?.join('–')} (${w.n_climatology_years} Jahre)`, color: tokens.ink3, kind: 'dash' },
              ...(mode === 'rain' ? [{ label: 'Niederschlag je Dekade (diese Saison / Mittel)', color: tokens.water, kind: 'bar' as const }] : []),
              ...(mode === 'temperature' ? [{ label: 'Tage über 32 °C', color: tokens.rust, kind: 'dot' as const }] : []),
            ]}
          />
        </div>
        <dl className="flex flex-col gap-5 border-[var(--line)] lg:border-l lg:pl-8">
          <div><dt className="eyebrow">Niederschlag Saison</dt><dd className="mt-1 font-display text-[30px] font-semibold tabular">{fmtInt(rain)} <span className="text-[14px] text-ink-3">mm</span></dd><dd className={`font-mono text-[12px] ${rain < rainN ? 'text-rust' : 'text-water'}`}>{fmtSigned(((rain - rainN) / rainN) * 100, 0)} % ggü. Mittel</dd></div>
          <div><dt className="eyebrow">Niederschlag Juli–August</dt><dd className="mt-1 font-mono text-[18px] tabular">{fmtInt(jul(w.dekads.prec))} mm <span className="text-ink-4">/ {fmtInt(jul(w.normal.prec))}</span></dd></div>
          <div><dt className="eyebrow">Wachstumsgradtage</dt><dd className="mt-1 font-mono text-[18px] tabular">{fmtInt(gdd)} <span className="text-ink-4">/ {fmtInt(gddN)}</span></dd></div>
          <div><dt className="eyebrow">Tage über 32 °C</dt><dd className="mt-1 font-mono text-[18px] tabular">{fmtInt(heat)}</dd></div>
        </dl>
      </div>
      <p className="mt-6 text-[13px] leading-relaxed text-ink-3">
        ERA5-Land-Zelle {w.era5_cell} (≈ 9 km). Das Wetter beschreibt die Umgebung, nicht das einzelne Feld – und in diesem Projekt
        kennzeichnet es vor allem das Jahr, nicht das Feld.
      </p>
    </Block>
  )
}

/* ------------------------------------------------------------------ */
/* Soil                                                                */
/* ------------------------------------------------------------------ */

export function SoilPanel({ f }: { f: FieldAnalysis }) {
  if (!f.soil) return null
  const s = f.soil
  const items = [
    { k: 'Ton', v: `${fmt(s.clay_pct, 0)} %` },
    { k: 'Sand', v: `${fmt(s.sand_pct, 0)} %` },
    { k: 'Org. Kohlenstoff', v: `${fmt(s.soc, 1)} %` },
    { k: 'Wasserspeicherung', v: `${fmt(s.awc, 3)} m³/m³` },
    { k: 'pH', v: fmt(s.ph, 1) },
    { k: 'Seehöhe', v: `${fmt(s.elev_m, 0)} m` },
    { k: 'Hangneigung', v: `${fmt(s.slope_deg, 1)}°` },
    { k: 'Feuchteindex', v: fmt(s.twi, 1) },
  ]
  return (
    <Block eyebrow="Boden und Gelände" title="Standortbedingungen">
      <dl className="grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-[var(--line)] bg-[var(--line)] sm:grid-cols-4">
        {items.map((it) => (
          <div key={it.k} className="bg-soil-900 p-4">
            <dt className="eyebrow">{it.k}</dt>
            <dd className="mt-2 font-mono text-[17px] tabular text-ink">{it.v}</dd>
          </div>
        ))}
      </dl>
      <p className="mt-5 text-[13px] leading-relaxed text-ink-3">
        SoilGrids 2.0 (250 m) und Copernicus DEM (30 m). Der Boden allein erklärt hier fast nichts von den Ertragsunterschieden (ρ ≤ 0,16
        für den absoluten Ertrag) – er ist Kontext, kein Treiber des Scores.
      </p>
    </Block>
  )
}
