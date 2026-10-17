import { motion } from 'motion/react'
import { CloudRain, Eye, Info } from 'lucide-react'
import { useMemo, useState, type ReactNode } from 'react'
import { useTranslation } from 'react-i18next'
import type { FieldAnalysis, IndexName } from '../../api/types'
import { ndviColor, relYieldColor, tokens } from '../../lib/color'
import { cumulative, lastCompleteDekad, monthLong, phaseName } from '../../lib/dekads'
import { fmt, fmtArea, fmtCutoff, fmtInt, fmtPct, fmtSigned } from '../../lib/format'
import { SeasonChart } from '../charts/SeasonChart'
import { Scatter } from '../charts/Stats'
import { WeatherChart, type WeatherMode } from '../charts/WeatherChart'
import { Legend } from '../charts/core'
import { Badge, LiveBadge, SimulatedBadge } from '../ui/Badge'
import { Reveal } from '../ui/Reveal'
import { Source } from '../ui/Section'
import { Tabs } from '../ui/Tabs'
import { keepGreek } from '../ui/Text'
import { PixelField, type PixelMode } from './PixelField'

const cutoffDekad = (f: FieldAnalysis) => {
  const [m, d] = (f.cutoff ?? '09-01').split('-').map(Number)
  return lastCompleteDekad(m, d) + 1
}

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
  const { t } = useTranslation()
  const s = f.stress
  const [revealed, setRevealed] = useState(false)
  if (!s) return null
  const outcome = f.measured
  return (
    <div className="grid gap-5 lg:grid-cols-[1.35fr_1fr]">
      {f.alert ? <AlertCard f={f} /> : <RiskCard f={f} />}
      <Reveal delay={0.08} className="panel flex flex-col p-7 sm:p-9">
        <p className="eyebrow">{t('results.happened')}</p>
        {f.simulated || outcome.relative_yield == null ? (
          <div className="mt-6 flex flex-1 flex-col justify-center gap-3 text-[14.5px] leading-relaxed text-ink-2">
            <p className="text-ink">{t('results.noTruth')}</p>
            <p>{t('results.noTruthBody')}</p>
          </div>
        ) : !revealed && !f.live ? (
          <div className="mt-6 flex flex-1 flex-col items-start justify-center gap-4">
            <p className="text-[14.5px] leading-relaxed text-ink-2">{t('results.heldOut')}</p>
            <button
              type="button"
              onClick={() => setRevealed(true)}
              className="inline-flex items-center gap-2 rounded-[var(--radius-control)] border border-[var(--line-strong)] px-4 py-2.5 text-[14px] font-medium text-ink transition hover:border-maize hover:text-maize"
            >
              <Eye className="size-4" /> {t('results.reveal')}
            </button>
          </div>
        ) : (
          <Outcome f={f} />
        )}
      </Reveal>
    </div>
  )
}

function Outcome({ f }: { f: FieldAnalysis }) {
  const { t } = useTranslation()
  const s = f.stress!
  const outcome = f.measured
  const alarm = s.alarm
  const verdict = outcome.at_risk == null ? null : alarm === outcome.at_risk ? 'correct' : alarm ? 'false-alarm' : 'missed'
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="mt-6 flex flex-1 flex-col">
      <p className="font-display text-[clamp(2.8rem,5vw,3.8rem)] font-semibold leading-none tracking-[-0.04em]">
        {fmt(outcome.yield_t_ha, 1)}
        <span className="ml-2 text-[0.38em] font-medium tracking-normal text-ink-3">t/ha</span>
      </p>
      <p className="mt-3 text-[14.5px] text-ink-2">
        {t('results.ofNormal', { v: fmtPct(outcome.relative_yield) })} ·{' '}
        <span className={outcome.at_risk ? 'text-rust' : 'text-sage'}>{outcome.at_risk ? t('results.atRisk') : t('results.notAtRisk')}</span>
      </p>
      {!f.live && (
        <div className="mt-auto pt-6">
          {verdict === 'correct' && <Badge tone="sage" dot>{alarm ? t('results.correctAlarm') : t('results.correctQuiet')}</Badge>}
          {verdict === 'false-alarm' && <Badge tone="maize" dot>{t('results.falseAlarm')}</Badge>}
          {verdict === 'missed' && <Badge tone="water" dot>{t('results.missed')}</Badge>}
        </div>
      )}
    </motion.div>
  )
}

function RiskCard({ f }: { f: FieldAnalysis }) {
  const { t } = useTranslation()
  const s = f.stress!
  const alarm = s.alarm
  const pct = Math.max(0, Math.min(1, s.risk_p ?? 0))
  return (
    <Reveal className="panel relative overflow-hidden p-7 sm:p-9">
      <div className={`pointer-events-none absolute -right-24 -top-24 size-72 rounded-full blur-3xl ${alarm ? 'bg-rust/15' : 'bg-sage/10'}`} />
      <div className="flex flex-wrap items-center gap-2">
        <p className="eyebrow">{t('results.assessment', { y: f.year })}</p>
        {f.simulated && <SimulatedBadge />}
      </div>
      <div className="mt-6 flex flex-wrap items-end gap-x-10 gap-y-6">
        <div>
          <p className={`font-display text-[clamp(3.2rem,6vw,4.6rem)] font-semibold leading-none tracking-[-0.04em] ${alarm ? 'text-rust' : 'text-sage'}`}>
            {alarm ? t('results.alarm') : t('results.noAlarm')}
          </p>
          <p className="mt-3 max-w-[420px] text-[14.5px] leading-relaxed text-ink-2">
            {alarm ? t('results.alarmBody', { phase: phaseName(s.main_phase ?? 'July') }) : t('results.noAlarmBody')}
          </p>
        </div>
        <dl className="grid grid-cols-2 gap-x-8 gap-y-4">
          <div>
            <dt className="eyebrow">{t('results.score')}</dt>
            <dd className="mt-1 font-mono text-[22px] tabular">{fmtSigned(s.score, 3)}</dd>
          </div>
          <div>
            <dt className="eyebrow">{t('results.mainDev')}</dt>
            <dd className="mt-1 font-mono text-[22px]">{phaseName(s.main_phase)}</dd>
          </div>
        </dl>
      </div>
      {s.risk_p != null && s.threshold != null && (
        <div className="mt-9">
          <div className="flex justify-between font-mono text-[11px] text-ink-3">
            <span>{t('results.risk')}</span>
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
              {t('results.threshold', { t: fmt(s.threshold, 2) })}
            </span>
          </div>
        </div>
      )}
    </Reveal>
  )
}

/** Live result: frozen alert level with the historical hit rate of the US calibration. */
export function AlertCard({ f }: { f: FieldAnalysis }) {
  const { t } = useTranslation()
  const a = f.alert!
  const tone = { warning: 'text-rust', hint: 'text-maize', none: 'text-sage', no_statement: 'text-ink-2' }[a.state]
  const label = { warning: t('results.alertWarning'), hint: t('results.alertHint'), none: t('results.alertNone'), no_statement: t('results.alertNoStatement') }[a.state]
  return (
    <Reveal className="panel relative overflow-hidden p-7 sm:p-9">
      <div className={`pointer-events-none absolute -right-24 -top-24 size-72 rounded-full blur-3xl ${a.state === 'warning' ? 'bg-rust/15' : a.state === 'hint' ? 'bg-maize/15' : 'bg-sage/10'}`} />
      <div className="flex flex-wrap items-center gap-2">
        <p className="eyebrow">{t('results.assessmentCutoff', { d: `${fmtCutoff(a.cutoff)} ${f.year}` })}</p>
        <LiveBadge />
      </div>
      <p className={`mt-6 font-display text-[clamp(2.6rem,5vw,4rem)] font-semibold leading-none tracking-[-0.04em] ${tone}`}>{label}</p>
      <p className="mt-3 text-[14px] text-ink-2">{t('results.alertBody', { s: fmtSigned(a.score, 3), d: fmtCutoff(a.cutoff) })}</p>
      <ul className="mt-6 flex flex-col gap-3">
        {a.levels.map((lv) => (
          <li key={lv.level} className="flex gap-3 text-[14px] leading-relaxed">
            <span className={`mt-1.5 size-2.5 shrink-0 rounded-full ${lv.level === 'warning' ? 'bg-rust' : 'bg-maize'} ${lv.triggered ? '' : 'opacity-30'}`} />
            <span className="text-ink-2">
              <span className="text-ink">{t('results.alertLevel', { level: lv.level === 'warning' ? t('results.alertWarning') : t('results.alertHint'), x: lv.x_pct })}</span>
              {lv.statement === 'ok' && lv.k_hit != null && lv.n_alert != null ? t('results.alertHit', { k: lv.k_hit, n: lv.n_alert }) : t('results.alertNoData')}
            </span>
          </li>
        ))}
      </ul>
    </Reveal>
  )
}

/* ------------------------------------------------------------------ */
/* Phase contributions                                                  */
/* ------------------------------------------------------------------ */

export function PhaseContributions({ f, typical }: { f: FieldAnalysis; typical?: { at_risk: Record<string, number>; not_at_risk: Record<string, number> } }) {
  const { t } = useTranslation()
  const s = f.stress
  if (!s) return null
  const rows = [
    { key: 'Jun' as const, m: 5, typ: 'Juni' },
    { key: 'Jul' as const, m: 6, typ: 'Juli' },
    { key: 'Aug' as const, m: 7, typ: 'August' },
  ]
  const lo = Math.min(-0.35, ...rows.map((r) => s.phases[r.key] ?? 0))
  const pos = (v: number) => `${(v / lo) * 100}%`
  return (
    <Block eyebrow={t('results.phasesEyebrow')} title={t('results.phasesTitle')}>
      <div className="flex flex-col gap-5">
        {rows.map((r) => {
          const v = s.phases[r.key] ?? 0
          const tr = typical?.at_risk[r.typ]
          const tn = typical?.not_at_risk[r.typ]
          return (
            <div key={r.key} className="grid grid-cols-[84px_1fr_64px] items-center gap-4">
              <span className="text-[14px] text-ink">{monthLong(r.m)}</span>
              <div className="relative h-7 rounded-md bg-white/[0.035]">
                <motion.div
                  className="absolute inset-y-1 left-0 rounded-[4px] bg-rust/80"
                  initial={{ width: 0 }}
                  whileInView={{ width: pos(v) }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
                />
                {tn != null && <span className="absolute inset-y-0 w-px bg-sage" style={{ left: pos(tn) }} />}
                {tr != null && <span className="absolute inset-y-0 w-px bg-ink" style={{ left: pos(tr) }} />}
              </div>
              <span className="text-right font-mono text-[13px] tabular text-ink-2">{fmtSigned(v, 2)}</span>
            </div>
          )
        })}
      </div>
      {typical && (
        <Legend
          className="mt-6"
          items={[
            { label: t('results.thisField'), color: tokens.rust, kind: 'bar' },
            { label: t('results.meanRisk'), color: tokens.ink },
            { label: t('results.meanOk'), color: tokens.sage },
          ]}
        />
      )}
      <p className="mt-5 flex gap-2 text-[13px] leading-relaxed text-ink-3">
        <Info className="mt-0.5 size-3.5 shrink-0" />
        {t('results.phasesNote')}
      </p>
      <Source className="mt-4">{t('results.srcPhases')}</Source>
    </Block>
  )
}

/* ------------------------------------------------------------------ */
/* Satellite                                                           */
/* ------------------------------------------------------------------ */

const INDEX_DOMAIN: Record<IndexName, [number, number]> = { ndvi: [0, 1], evi: [0, 0.9], ndmi: [-0.3, 0.6], ndre: [0, 0.7], gndvi: [0, 0.9] }

export function SatellitePanel({ f }: { f: FieldAnalysis }) {
  const { t } = useTranslation()
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
    return { a, diff: (a - b) / b, n: win.length, peak: peak >= 0 ? (nd[peak] as number) : null }
  }, [f])
  const label = idx.toUpperCase()
  const hasBand = Boolean(ref?.p25?.some((v) => v != null))
  return (
    <Block
      eyebrow={t('results.satEyebrow')}
      title={t('results.satTitle')}
      aside={<Tabs label={t('results.index')} value={idx} onChange={setIdx} items={available.map((k) => ({ value: k, label: k.toUpperCase() }))} />}
    >
      <div className="grid gap-8 lg:grid-cols-[1fr_250px]">
        <div>
          <SeasonChart values={vals} reference={ref} year={f.year} label={label} yDomain={INDEX_DOMAIN[idx]} cutoff={cutoffDekad(f) - 1} cutoffLabel={f.cutoff ? `${t('analyse.cutoff')} ${fmtCutoff(f.cutoff)}` : undefined} showShortfall={idx === 'ndvi'} height={320} />
          <Legend
            className="mt-4"
            items={[
              { label: t('results.thisFieldIdx', { idx: label }), color: tokens.maize, kind: 'line' },
              ...(ref ? [{ label: t('results.healthyBand', { n: ref.n_fieldyears }), color: tokens.sage, kind: hasBand ? ('band' as const) : ('dash' as const) }] : []),
              ...(idx === 'ndvi' ? [{ label: t('results.shortfallJune'), color: tokens.rust, kind: 'bar' as const }] : []),
            ]}
          />
        </div>
        <div className="flex flex-col gap-6 border-[var(--line)] lg:border-l lg:pl-8">
          {health && (
            <div>
              <p className="eyebrow">{t('results.health')}</p>
              <p className="mt-2 font-display text-[40px] font-semibold leading-none tracking-[-0.03em] tabular">{fmt(health.a, 2)}</p>
              <p className={`mt-2 font-mono text-[13px] ${health.diff < 0 ? 'text-rust' : 'text-sage'}`}>{t('results.vsHealthy', { v: fmtSigned(health.diff * 100, 1) })}</p>
              <p className="mt-1 text-[12px] text-ink-4">{t('results.meanOver', { n: health.n })}</p>
            </div>
          )}
          <dl className="grid grid-cols-2 gap-4 text-[13px]">
            <div><dt className="eyebrow">{t('results.scenes')}</dt><dd className="mt-1 font-mono tabular">{f.satellite.n_scenes}</dd></div>
            <div><dt className="eyebrow">{t('results.clear')}</dt><dd className="mt-1 font-mono tabular">{f.satellite.n_clear_scenes}</dd></div>
            <div><dt className="eyebrow">{t('results.dekads')}</dt><dd className="mt-1 font-mono tabular">{f.satellite.n_observed_dekads} / 21</dd></div>
            <div><dt className="eyebrow">{t('results.peak')}</dt><dd className="mt-1 font-mono tabular">{fmt(health?.peak, 2)}</dd></div>
          </dl>
          <p className="text-[12.5px] leading-relaxed text-ink-3">
            {t(`results.indexAbout.${idx}`)} {t('results.dotsNote')}
          </p>
        </div>
      </div>
    </Block>
  )
}

/* ------------------------------------------------------------------ */
/* Within-field map                                                    */
/* ------------------------------------------------------------------ */

export function WithinFieldPanel({ f }: { f: FieldAnalysis }) {
  const { t } = useTranslation()
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
      <Block eyebrow={t('results.mapEyebrow')} title={t('results.mapTitle')}>
        <p className="max-w-[640px] text-[14.5px] leading-relaxed text-ink-2">{f.live ? t('results.mapNoneLive') : t('results.mapNone', { area: fmtArea(f.area_m2) })}</p>
      </Block>
    )
  }
  const sim = Boolean(f.simulated)
  return (
    <Block
      id="within-field"
      eyebrow={t('results.mapEyebrow')}
      title={t('results.mapTitle')}
      aside={
        <Tabs
          label={t('analyse.layer')}
          value={mode}
          onChange={setMode}
          items={[
            { value: 'weak', label: t('results.layerFlagged') },
            { value: 'window', label: t('results.layerNdvi') },
            { value: 'yield', label: sim ? t('results.layerYieldSim') : t('results.layerYield') },
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
                <span key={v} className="flex items-center gap-1.5">
                  <span className="size-2.5 rounded-[2px]" style={{ background: relYieldColor(v) }} />
                  {t('results.ofMean', { v: fmt(v * 100, 0) })}
                </span>
              ))
            ) : mode === 'weak' ? (
              <span className="flex items-center gap-1.5">
                <span className="size-2.5 rounded-[2px] bg-rust" />
                {t('results.lowestQuarter', { t: fmt(px.weak_threshold, 2) })}
              </span>
            ) : (
              <span className="font-mono">{px.window}</span>
            )}
          </div>
        </div>
        <div className="flex flex-col gap-6">
          {!sim ? (
            <dl className="grid grid-cols-2 gap-x-6 gap-y-5">
              <div><dt className="eyebrow">{t('results.rho')} <span className="normal-case">ρ</span></dt><dd className="mt-1 font-display text-[32px] font-semibold tabular text-sage">{fmt(px.rho, 2)}</dd></div>
              <div><dt className="eyebrow">{t('results.trulyLow')}</dt><dd className="mt-1 font-display text-[32px] font-semibold tabular">{fmtPct(px.precision_weak)}</dd></div>
              <div><dt className="eyebrow">{t('results.lowShare')}</dt><dd className="mt-1 font-mono text-[18px] tabular text-ink-2">{fmtPct(px.prevalence_problem)}</dd></div>
              <div><dt className="eyebrow">{t('results.lift')}</dt><dd className="mt-1 font-mono text-[18px] tabular text-ink-2">× {fmt(px.lift, 1)}</dd></div>
            </dl>
          ) : (
            <p className="text-[14px] leading-relaxed text-ink-2">{t('results.simPattern')}</p>
          )}
          <Scatter
            points={pts}
            xLabel={t('results.scatterX')}
            yLabel={t('results.scatterY')}
            height={230}
            hLines={[{ v: 0.85, label: t('results.lowZone'), color: tokens.rust }]}
            vLines={[{ v: px.weak_threshold, color: tokens.ink3 }]}
            xFmt={(v) => fmt(v, 2)}
            yFmt={(v) => fmt(v, 1)}
            yDomain={[0.2, 1.6]}
            opacity={0.6}
          />
        </div>
      </div>
      <p className="mt-6 text-[13px] leading-relaxed text-ink-3">{keepGreek(t('results.mapNote', { n: fmtInt(px.n_cells), m: px.cell_m }))}</p>
      {!sim && <Source className="mt-3">{t('results.srcMap')}</Source>}
    </Block>
  )
}

/* ------------------------------------------------------------------ */
/* Weather                                                             */
/* ------------------------------------------------------------------ */

export function WeatherPanel({ f }: { f: FieldAnalysis }) {
  const { t } = useTranslation()
  const [mode, setMode] = useState<WeatherMode>('rain')
  const w = f.weather
  const sum = (xs: (number | null)[] | undefined) => (xs ?? []).reduce<number>((a, b) => a + (b ?? 0), 0)
  const rain = sum(w.dekads.prec)
  const rainN = sum(w.normal.prec)
  const jul = (xs: (number | null)[] | undefined) => sum((xs ?? []).slice(9, 15))
  const gdd = cumulative(w.dekads.gdd ?? []).at(-1) ?? 0
  const gddN = cumulative(w.normal.gdd ?? []).at(-1) ?? 0
  const heat = sum(w.dekads.heat)
  const hints = f.weatherHints
  return (
    <Block
      eyebrow={t('results.weatherEyebrow')}
      title={t('results.weatherTitle')}
      aside={
        <Tabs
          label={t('results.weatherVar')}
          value={mode}
          onChange={setMode}
          items={[
            { value: 'rain', label: t('results.rain') },
            { value: 'temperature', label: t('results.temp') },
            { value: 'gdd', label: t('results.gdd') },
            { value: 'moisture', label: t('results.moisture') },
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
              { label: t('results.meanYears', { from: w.climatology_years?.[0] ?? '–', to: w.climatology_years?.[1] ?? '–', n: w.n_climatology_years }), color: tokens.ink3, kind: 'dash' },
              ...(mode === 'rain' ? [{ label: t('results.rainBars'), color: tokens.water, kind: 'bar' as const }] : []),
              ...(mode === 'temperature' ? [{ label: t('results.hot'), color: tokens.rust, kind: 'dot' as const }] : []),
            ]}
          />
        </div>
        <dl className="flex flex-col gap-5 border-[var(--line)] lg:border-l lg:pl-8">
          <div>
            <dt className="eyebrow">{t('results.seasonRain')}</dt>
            <dd className="mt-1 font-display text-[30px] font-semibold tabular">{fmtInt(rain)} <span className="text-[14px] text-ink-3">mm</span></dd>
            <dd className={`font-mono text-[12px] ${rain < rainN ? 'text-rust' : 'text-water'}`}>{rainN ? t('results.vsMean', { v: fmtSigned(((rain - rainN) / rainN) * 100, 0) }) : '–'}</dd>
          </div>
          <div><dt className="eyebrow">{t('results.julAugRain')}</dt><dd className="mt-1 font-mono text-[18px] tabular">{fmtInt(jul(w.dekads.prec))} mm <span className="text-ink-4">/ {fmtInt(jul(w.normal.prec))}</span></dd></div>
          <div><dt className="eyebrow">{t('results.gddLabel')}</dt><dd className="mt-1 font-mono text-[18px] tabular">{fmtInt(gdd)} <span className="text-ink-4">/ {fmtInt(gddN)}</span></dd></div>
          <div><dt className="eyebrow">{t('results.hotDays')}</dt><dd className="mt-1 font-mono text-[18px] tabular">{fmtInt(heat)}</dd></div>
        </dl>
      </div>
      {hints && (
        <div className="mt-7 rounded-xl border border-[var(--line)] bg-white/[0.02] p-5">
          <p className="eyebrow mb-3 flex items-center gap-2"><CloudRain className="size-3.5" /> {t('results.hintsTitle')}</p>
          {hints.length ? (
            <ul className="flex flex-col gap-1.5 text-[14px] text-ink">
              {hints.map((h) => (
                <li key={h.key}>
                  {t(`results.hint.${h.key}`, { v: h.key === 'drought' ? fmtInt(h.value_cwb_30d_mm) : h.key === 'heat_flowering' ? h.days : fmtInt(h.mm) })}
                  <span className="ml-2 font-mono text-[11px] text-ink-4">({h.rule})</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-[14px] text-ink-2">{t('results.hintsNone')}</p>
          )}
          <p className="mt-3 text-[12.5px] text-ink-3">{t('results.hintsNote')}</p>
        </div>
      )}
      <p className="mt-6 text-[13px] leading-relaxed text-ink-3">{t('results.weatherNote', { cell: w.era5_cell })}</p>
    </Block>
  )
}

/* ------------------------------------------------------------------ */
/* Soil                                                                */
/* ------------------------------------------------------------------ */

export function SoilPanel({ f }: { f: FieldAnalysis }) {
  const { t } = useTranslation()
  if (!f.soil) return null
  const s = f.soil
  const items = [
    { k: t('results.clay'), v: `${fmt(s.clay_pct, 0)} %` },
    { k: t('results.sand'), v: `${fmt(s.sand_pct, 0)} %` },
    { k: t('results.soc'), v: `${fmt(s.soc, 1)} %` },
    { k: t('results.awc'), v: `${fmt(s.awc, 3)} m³/m³` },
    { k: t('results.ph'), v: fmt(s.ph, 1) },
    { k: t('results.elev'), v: `${fmt(s.elev_m, 0)} m` },
    { k: t('results.slope'), v: `${fmt(s.slope_deg, 1)}°` },
    { k: t('results.twi'), v: fmt(s.twi, 1) },
  ]
  return (
    <Block eyebrow={t('results.soilEyebrow')} title={t('results.soilTitle')}>
      <dl className="grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-[var(--line)] bg-[var(--line)] sm:grid-cols-4">
        {items.map((it) => (
          <div key={it.k} className="bg-soil-900 p-4">
            <dt className="eyebrow">{it.k}</dt>
            <dd className="mt-2 font-mono text-[17px] tabular text-ink">{it.v}</dd>
          </div>
        ))}
      </dl>
      <p className="mt-5 text-[13px] leading-relaxed text-ink-3">{keepGreek(t('results.soilNote'))}</p>
    </Block>
  )
}
