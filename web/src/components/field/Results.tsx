import { motion } from 'motion/react'
import { Eye, Info } from 'lucide-react'
import { useMemo, useState, type ReactNode } from 'react'
import type { FieldAnalysis, IndexName } from '../../api/types'
import { ndviColor, relYieldColor, tokens } from '../../lib/color'
import { cumulative, lastCompleteDekad } from '../../lib/dekads'
import { fmt, fmtArea, fmtInt, fmtPct, fmtSigned } from '../../lib/format'
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
  const verdict = outcome.at_risk == null ? null : alarm === outcome.at_risk ? 'correct' : alarm ? 'false-alarm' : 'missed'
  return (
    <div className="grid gap-5 lg:grid-cols-[1.35fr_1fr]">
      <Reveal className="panel relative overflow-hidden p-7 sm:p-9">
        <div className={`pointer-events-none absolute -right-24 -top-24 size-72 rounded-full blur-3xl ${alarm ? 'bg-rust/15' : 'bg-sage/10'}`} />
        <div className="flex flex-wrap items-center gap-2">
          <p className="eyebrow">Stress assessment · as of 1 September {f.year}</p>
          {f.simulated && <SimulatedBadge />}
        </div>
        <div className="mt-6 flex flex-wrap items-end gap-x-10 gap-y-6">
          <div>
            <p className={`font-display text-[clamp(3.2rem,6vw,4.6rem)] font-semibold leading-none tracking-[-0.04em] ${alarm ? 'text-rust' : 'text-sage'}`}>
              {alarm ? 'Alarm' : 'No alarm'}
            </p>
            <p className="mt-3 max-w-[420px] text-[14.5px] leading-relaxed text-ink-2">
              {alarm
                ? `The season curve sits clearly below the healthy reference, mostly in ${s.main_phase ?? 'mid-summer'}. An alarm means “unusual curve” — stress, or for example late sowing.`
                : 'The season curve stays close to the healthy reference. The field is not flagged.'}
            </p>
          </div>
          <dl className="grid grid-cols-2 gap-x-8 gap-y-4">
            <div>
              <dt className="eyebrow">Stress score</dt>
              <dd className="mt-1 font-mono text-[22px] tabular">{fmtSigned(s.score, 3)}</dd>
            </div>
            <div>
              <dt className="eyebrow">Main deviation</dt>
              <dd className="mt-1 font-mono text-[22px]">{s.main_phase ?? '–'}</dd>
            </div>
          </dl>
        </div>
        <div className="mt-9">
          <div className="flex justify-between font-mono text-[11px] text-ink-3">
            <span>Risk of ≥ 15 % yield loss</span>
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
              alarm threshold {fmt(s.threshold, 2)} · ≤ 20 % false alarms
            </span>
          </div>
        </div>
      </Reveal>

      <Reveal delay={0.08} className="panel flex flex-col p-7 sm:p-9">
        <p className="eyebrow">What actually happened</p>
        {f.simulated || outcome.relative_yield == null ? (
          <div className="mt-6 flex flex-1 flex-col justify-center gap-3 text-[14.5px] leading-relaxed text-ink-2">
            <p className="text-ink">No measured yield for this field.</p>
            <p>Prepared fields come with the combine’s measurement, so each result can be checked. A drawn field has no ground truth.</p>
          </div>
        ) : !revealed ? (
          <div className="mt-6 flex flex-1 flex-col items-start justify-center gap-4">
            <p className="text-[14.5px] leading-relaxed text-ink-2">
              This field-year was held out when the model was fitted. Its measured yield is known — compare it with the assessment.
            </p>
            <button
              type="button"
              onClick={() => setRevealed(true)}
              className="inline-flex items-center gap-2 rounded-[var(--radius-control)] border border-[var(--line-strong)] px-4 py-2.5 text-[14px] font-medium text-ink transition hover:border-maize hover:text-maize"
            >
              <Eye className="size-4" /> Reveal measured outcome
            </button>
          </div>
        ) : (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="mt-6 flex flex-1 flex-col">
            <p className="font-display text-[clamp(2.8rem,5vw,3.8rem)] font-semibold leading-none tracking-[-0.04em]">
              {fmt(outcome.yield_t_ha, 1)}
              <span className="ml-2 text-[0.38em] font-medium tracking-normal text-ink-3">t/ha</span>
            </p>
            <p className="mt-3 text-[14.5px] text-ink-2">
              {fmtPct(outcome.relative_yield)} of this field’s normal yield ·{' '}
              <span className={outcome.at_risk ? 'text-rust' : 'text-sage'}>{outcome.at_risk ? 'at risk (≥ 15 % loss)' : 'not at risk'}</span>
            </p>
            <div className="mt-auto pt-6">
              {verdict === 'correct' && <Badge tone="sage" dot>{alarm ? 'Correct alarm' : 'Correctly quiet'}</Badge>}
              {verdict === 'false-alarm' && <Badge tone="maize" dot>False alarm</Badge>}
              {verdict === 'missed' && <Badge tone="water" dot>Missed loss</Badge>}
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
  const rows = [
    { key: 'Jun' as const, label: 'June', t: 'Juni' },
    { key: 'Jul' as const, label: 'July', t: 'Juli' },
    { key: 'Aug' as const, label: 'August', t: 'August' },
  ]
  const lo = Math.min(-0.35, ...rows.map((r) => s.phases[r.key] ?? 0))
  const pos = (v: number) => `${(v / lo) * 100}%`
  return (
    <Block eyebrow="Where the deviation came from" title="Shortfall below the healthy curve, by month">
      <div className="flex flex-col gap-5">
        {rows.map((r) => {
          const v = s.phases[r.key] ?? 0
          const tr = typical?.at_risk[r.t]
          const tn = typical?.not_at_risk[r.t]
          return (
            <div key={r.key} className="grid grid-cols-[72px_1fr_64px] items-center gap-4">
              <span className="text-[14px] text-ink">{r.label}</span>
              <div className="relative h-7 rounded-md bg-white/[0.035]">
                <motion.div
                  className="absolute inset-y-1 left-0 rounded-[4px] bg-rust/80"
                  initial={{ width: 0 }}
                  whileInView={{ width: pos(v) }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
                />
                {tn != null && <span className="absolute inset-y-0 w-px bg-sage" style={{ left: pos(tn) }} title="Typical not-at-risk field" />}
                {tr != null && <span className="absolute inset-y-0 w-px bg-ink" style={{ left: pos(tr) }} title="Typical at-risk field" />}
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
            { label: 'This field', color: tokens.rust, kind: 'bar' },
            { label: 'Mean of at-risk US fields', color: tokens.ink },
            { label: 'Mean of not-at-risk US fields', color: tokens.sage },
          ]}
        />
      )}
      <p className="mt-5 flex gap-2 text-[13px] leading-relaxed text-ink-3">
        <Info className="mt-0.5 size-3.5 shrink-0" />
        Summed NDVI shortfall per month (observed dekads only). This explains the alarm; it is not a causal attribution. In the US
        data, 22 of 31 alarms came mainly from July.
      </p>
      <Source className="mt-4">results/2026-10-16_feinjust_ablation/ranking.csv · product.json</Source>
    </Block>
  )
}

/* ------------------------------------------------------------------ */
/* Satellite                                                           */
/* ------------------------------------------------------------------ */

const INDEX_INFO: Record<IndexName, { label: string; domain: [number, number]; about: string }> = {
  ndvi: { label: 'NDVI', domain: [0, 1], about: 'Green biomass. The main signal for the stress score and the field map.' },
  evi: { label: 'EVI', domain: [0, 0.9], about: 'Like NDVI, less saturated over dense canopy.' },
  ndmi: { label: 'NDMI', domain: [-0.3, 0.6], about: 'Canopy water content (near- vs short-wave infrared).' },
  ndre: { label: 'NDRE', domain: [0, 0.7], about: 'Red-edge index, sensitive to chlorophyll in dense maize.' },
  gndvi: { label: 'GNDVI', domain: [0, 0.9], about: 'Green NDVI.' },
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
      eyebrow="Satellite time series"
      title="The season, dekad by dekad"
      aside={<Tabs label="Vegetation index" value={idx} onChange={setIdx} items={available.map((k) => ({ value: k, label: INDEX_INFO[k].label }))} />}
    >
      <div className="grid gap-8 lg:grid-cols-[1fr_250px]">
        <div>
          <SeasonChart values={vals} reference={ref} year={f.year} label={INDEX_INFO[idx].label} yDomain={INDEX_INFO[idx].domain} cutoff={CUTOFF} showShortfall={idx === 'ndvi'} height={320} />
          <Legend
            className="mt-4"
            items={[
              { label: `${INDEX_INFO[idx].label}, this field`, color: tokens.maize, kind: 'line' },
              ...(ref ? [{ label: `Healthy reference (median, IQR of ${ref.n_fieldyears} field-years)`, color: tokens.sage, kind: 'band' as const }] : []),
              ...(idx === 'ndvi' ? [{ label: 'Shortfall from June', color: tokens.rust, kind: 'bar' as const }] : []),
            ]}
          />
        </div>
        <div className="flex flex-col gap-6 border-[var(--line)] lg:border-l lg:pl-8">
          {health && (
            <div>
              <p className="eyebrow">Vegetation health · Jul–Aug</p>
              <p className="mt-2 font-display text-[40px] font-semibold leading-none tracking-[-0.03em] tabular">{fmt(health.a, 2)}</p>
              <p className={`mt-2 font-mono text-[13px] ${health.diff < 0 ? 'text-rust' : 'text-sage'}`}>{fmtSigned(health.diff * 100, 1)} % vs healthy reference</p>
              <p className="mt-1 text-[12px] text-ink-4">mean NDVI over {health.n} observed dekads</p>
            </div>
          )}
          <dl className="grid grid-cols-2 gap-4 text-[13px]">
            <div><dt className="eyebrow">Scenes</dt><dd className="mt-1 font-mono tabular">{f.satellite.n_scenes}</dd></div>
            <div><dt className="eyebrow">Clear</dt><dd className="mt-1 font-mono tabular">{f.satellite.n_clear_scenes}</dd></div>
            <div><dt className="eyebrow">Dekads</dt><dd className="mt-1 font-mono tabular">{f.satellite.n_observed_dekads} / 21</dd></div>
            <div><dt className="eyebrow">Peak NDVI</dt><dd className="mt-1 font-mono tabular">{fmt(health?.peak, 2)}</dd></div>
          </dl>
          <p className="text-[12.5px] leading-relaxed text-ink-3">{INDEX_INFO[idx].about} Dots are observed dekads; gaps had no clear scene.</p>
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
      <Block eyebrow="Within-field map" title="Which part of the field falls behind">
        <p className="max-w-[640px] text-[14.5px] leading-relaxed text-ink-2">
          This field is a {fmtArea(f.area_m2)} research plot without a combine yield map, so the 10-m map cannot be checked here. The map
          was validated on the BARC fields (Field A, B and E).
        </p>
      </Block>
    )
  }
  const sim = Boolean(f.simulated)
  return (
    <Block
      id="within-field"
      eyebrow="Within-field map"
      title="Which part of the field falls behind"
      aside={
        <Tabs
          label="Map layer"
          value={mode}
          onChange={setMode}
          items={[
            { value: 'weak', label: 'Flagged zones' },
            { value: 'window', label: 'NDVI Jul–Aug' },
            { value: 'yield', label: sim ? 'Yield (simulated)' : 'Measured yield' },
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
                <span key={v} className="flex items-center gap-1.5"><span className="size-2.5 rounded-[2px]" style={{ background: relYieldColor(v) }} />{Math.round(v * 100)} % of field mean</span>
              ))
            ) : mode === 'weak' ? (
              <span className="flex items-center gap-1.5"><span className="size-2.5 rounded-[2px] bg-rust" />Lowest NDVI quarter (≤ {fmt(px.weak_threshold, 2)})</span>
            ) : (
              <span className="font-mono">{px.window}</span>
            )}
          </div>
        </div>
        <div className="flex flex-col gap-6">
          {!sim ? (
            <dl className="grid grid-cols-2 gap-x-6 gap-y-5">
              <div><dt className="eyebrow">Rank correlation <span className="normal-case">ρ</span></dt><dd className="mt-1 font-display text-[32px] font-semibold tabular text-sage">{fmt(px.rho, 2)}</dd></div>
              <div><dt className="eyebrow">Flagged cells truly low</dt><dd className="mt-1 font-display text-[32px] font-semibold tabular">{fmtPct(px.precision_weak)}</dd></div>
              <div><dt className="eyebrow">Low-yield share overall</dt><dd className="mt-1 font-mono text-[18px] tabular text-ink-2">{fmtPct(px.prevalence_problem)}</dd></div>
              <div><dt className="eyebrow">Lift vs random</dt><dd className="mt-1 font-mono text-[18px] tabular text-ink-2">× {fmt(px.lift, 1)}</dd></div>
            </dl>
          ) : (
            <p className="text-[14px] leading-relaxed text-ink-2">The pattern is simulated. For a drawn field the backend would extract real Sentinel-2 cells; there is no yield map to compare against.</p>
          )}
          <Scatter
            points={pts}
            xLabel="NDVI, 10 Jul – 18 Aug"
            yLabel="Yield / field mean"
            height={230}
            hLines={[{ v: 0.85, label: 'low-yield zone < 85 %', color: tokens.rust }]}
            vLines={[{ v: px.weak_threshold, color: tokens.ink3 }]}
            xFmt={(v) => fmt(v, 2)}
            yFmt={(v) => fmt(v, 1)}
            yDomain={[0.2, 1.6]}
            opacity={0.6}
          />
        </div>
      </div>
      <p className="mt-6 text-[13px] leading-relaxed text-ink-3">
        {fmtInt(px.n_cells)} cells of {px.cell_m} m. Rule B0 needs no training: it ranks cells by their own NDVI. Over 41 BARC field-years
        the median ρ is 0.67.
      </p>
      {!sim && <Source className="mt-3">data/processed/features_innerfeld.parquet · data/interim/pixels_dekad · rule B0 as in innerfeld_run.py</Source>}
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
      eyebrow="Weather · ERA5-Land"
      title="This season against the long-term mean"
      aside={
        <Tabs
          label="Weather variable"
          value={mode}
          onChange={setMode}
          items={[
            { value: 'rain', label: 'Rainfall' },
            { value: 'temperature', label: 'Temperature' },
            { value: 'gdd', label: 'Degree days' },
            { value: 'moisture', label: 'Soil moisture' },
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
              { label: `Mean ${w.climatology_years?.join('–')} (${w.n_climatology_years} years)`, color: tokens.ink3, kind: 'dash' },
              ...(mode === 'rain' ? [{ label: 'Rain per dekad (this season / mean)', color: tokens.water, kind: 'bar' as const }] : []),
              ...(mode === 'temperature' ? [{ label: 'Days above 32 °C', color: tokens.rust, kind: 'dot' as const }] : []),
            ]}
          />
        </div>
        <dl className="flex flex-col gap-5 border-[var(--line)] lg:border-l lg:pl-8">
          <div><dt className="eyebrow">Season rain</dt><dd className="mt-1 font-display text-[30px] font-semibold tabular">{fmtInt(rain)} <span className="text-[14px] text-ink-3">mm</span></dd><dd className={`font-mono text-[12px] ${rain < rainN ? 'text-rust' : 'text-water'}`}>{fmtSigned(((rain - rainN) / rainN) * 100, 0)} % vs mean</dd></div>
          <div><dt className="eyebrow">July–August rain</dt><dd className="mt-1 font-mono text-[18px] tabular">{fmtInt(jul(w.dekads.prec))} mm <span className="text-ink-4">/ {fmtInt(jul(w.normal.prec))}</span></dd></div>
          <div><dt className="eyebrow">Growing degree days</dt><dd className="mt-1 font-mono text-[18px] tabular">{fmtInt(gdd)} <span className="text-ink-4">/ {fmtInt(gddN)}</span></dd></div>
          <div><dt className="eyebrow">Days above 32 °C</dt><dd className="mt-1 font-mono text-[18px] tabular">{fmtInt(heat)}</dd></div>
        </dl>
      </div>
      <p className="mt-6 text-[13px] leading-relaxed text-ink-3">
        ERA5-Land cell {w.era5_cell} (≈ 9 km). Weather describes the surroundings, not the single field — and in this project it
        mostly identifies the year, not the field.
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
    { k: 'Clay', v: `${fmt(s.clay_pct, 0)} %` },
    { k: 'Sand', v: `${fmt(s.sand_pct, 0)} %` },
    { k: 'Organic carbon', v: `${fmt(s.soc, 1)} %` },
    { k: 'Water capacity', v: `${fmt(s.awc, 3)} m³/m³` },
    { k: 'pH', v: fmt(s.ph, 1) },
    { k: 'Elevation', v: `${fmt(s.elev_m, 0)} m` },
    { k: 'Slope', v: `${fmt(s.slope_deg, 1)}°` },
    { k: 'Wetness index', v: fmt(s.twi, 1) },
  ]
  return (
    <Block eyebrow="Soil and terrain" title="Environmental context">
      <dl className="grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-[var(--line)] bg-[var(--line)] sm:grid-cols-4">
        {items.map((it) => (
          <div key={it.k} className="bg-soil-900 p-4">
            <dt className="eyebrow">{it.k}</dt>
            <dd className="mt-2 font-mono text-[17px] tabular text-ink">{it.v}</dd>
          </div>
        ))}
      </dl>
      <p className="mt-5 text-[13px] leading-relaxed text-ink-3">
        SoilGrids 2.0 (250 m) and Copernicus DEM (30 m). Soil alone explains almost nothing of the yield differences here (ρ ≤ 0.16 for
        absolute yield), so it is context, not a driver of the score.
      </p>
    </Block>
  )
}
