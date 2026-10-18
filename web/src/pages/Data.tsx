import { bin, extent } from 'd3-array'
import { scaleLinear } from 'd3-scale'
import { CloudSun, Layers, Lock, MapPinned, Mountain, Satellite } from 'lucide-react'
import { useMemo, useState, type ReactNode } from 'react'
import type { ExplorerRow } from '../api/types'
import { Scatter } from '../components/charts/Stats'
import { axisText, useWidth } from '../components/charts/core'
import { Badge } from '../components/ui/Badge'
import { Reveal } from '../components/ui/Reveal'
import { Container, SectionHeader, Source } from '../components/ui/Section'
import { ErrorNote, Skeleton } from '../components/ui/States'
import { Tabs } from '../components/ui/Tabs'
import { DATA_SOURCES, type DataSource } from '../data/content/project'
import { tokens } from '../lib/color'
import { fmt, fmtNum } from '../lib/format'
import { useResource } from '../lib/useResource'
import { getExplorer } from '../services/evidenceService'

const GROUP_META: Record<DataSource['group'], { label: string; icon: ReactNode }> = {
  yield: { label: 'Gemessener Ertrag', icon: <MapPinned className="size-4" /> },
  satellite: { label: 'Satellit', icon: <Satellite className="size-4" /> },
  weather: { label: 'Wetter', icon: <CloudSun className="size-4" /> },
  soil: { label: 'Boden und Gelände', icon: <Mountain className="size-4" /> },
  regional: { label: 'Regionalstatistik', icon: <Layers className="size-4" /> },
  austria: { label: 'Österreich – nur Test', icon: <Lock className="size-4" /> },
}

const SITE_COLOR: Record<string, string> = { KBS: tokens.sage, BARC: tokens.water, Colorado: tokens.maize }

type NumKey = 'Y_t_ha' | 'RY_descr' | 'ndvi_peak' | 'ndvi_jul_aug' | 'gdd' | 'prec' | 'heat32' | 'tmax_jun' | 'vpd_jun' | 'clay' | 'soc' | 'awc'
const NUM: { key: NumKey; label: string; digits: number }[] = [
  { key: 'Y_t_ha', label: 'Ertrag (t/ha)', digits: 1 },
  { key: 'RY_descr', label: 'Relativer Ertrag', digits: 2 },
  { key: 'ndvi_peak', label: 'NDVI-Maximum', digits: 2 },
  { key: 'ndvi_jul_aug', label: 'NDVI Jul–Aug', digits: 2 },
  { key: 'gdd', label: 'GDD bis 1. Sep', digits: 0 },
  { key: 'prec', label: 'Regen bis 1. Sep (mm)', digits: 0 },
  { key: 'heat32', label: 'Tage > 32 °C', digits: 0 },
  { key: 'tmax_jun', label: 'Höchsttemp. Juni (°C)', digits: 1 },
  { key: 'vpd_jun', label: 'VPD Juni (kPa)', digits: 2 },
  { key: 'clay', label: 'Ton (Anteil)', digits: 2 },
  { key: 'soc', label: 'Org. Kohlenstoff', digits: 1 },
  { key: 'awc', label: 'Nutzbare Feldkapazität', digits: 3 },
]

export default function Data() {
  return (
    <>
      <section className="pt-36 pb-10">
        <Container>
          <Reveal>
            <p className="eyebrow mb-5">Daten</p>
            <h1 className="max-w-[900px] text-balance text-[clamp(2.6rem,6vw,4.6rem)] leading-[0.98] tracking-[-0.04em]">Gemessen, wo es zählt: auf dem Feld.</h1>
            <p className="mt-6 max-w-[680px] text-[17px] leading-relaxed text-ink-2">
              Die Modelle lernen von Feldern, deren Ertrag gewogen oder vom Mähdrescher kartiert wurde – verknüpft mit offenen Satelliten-, Wetter- und Bodendaten.
              Österreichische Daten sind gesammelt, bleiben aber bis zum Test unter Verschluss.
            </p>
          </Reveal>
        </Container>
      </section>
      <SourceFlow />
      <Explorer />
    </>
  )
}

function SourceFlow() {
  const groups = Object.keys(GROUP_META) as DataSource['group'][]
  return (
    <section className="py-12">
      <Container>
        <div className="grid gap-5 lg:grid-cols-3">
          {groups.map((g, gi) => (
            <Reveal key={g} delay={gi * 0.05} className={`panel p-6 ${g === 'austria' ? 'border-dashed !bg-none' : ''}`}>
              <div className="flex items-center gap-2.5 text-maize">
                {GROUP_META[g].icon}
                <p className="eyebrow !text-maize">{GROUP_META[g].label}</p>
              </div>
              <ul className="mt-5 flex flex-col divide-y divide-[var(--line)]">
                {DATA_SOURCES.filter((d) => d.group === g).map((d) => (
                  <li key={d.name} className="py-4 first:pt-0 last:pb-0">
                    <div className="flex flex-wrap items-baseline justify-between gap-2">
                      <p className="text-[15px] font-medium text-ink">{d.name}</p>
                      <span className="font-mono text-[10.5px] text-ink-4">{d.scale}</span>
                    </div>
                    <p className="mt-0.5 text-[12.5px] text-ink-3">{d.provider}</p>
                    <p className="mt-2 text-[13.5px] leading-relaxed text-ink-2">{d.role} — {d.detail}</p>
                    <p className="mt-1.5 font-mono text-[10.5px] text-ink-4">{d.license}</p>
                  </li>
                ))}
              </ul>
            </Reveal>
          ))}
        </div>
        <Source className="mt-6">DATA_SOURCES.md · SUPPORT.md – Lizenzen, Abrufdaten und Schritte zur Neuerzeugung jeder Datei</Source>
      </Container>
    </section>
  )
}

/* ------------------------------------------------------------------ */

function Explorer() {
  const res = useResource(getExplorer, 'explorer')
  const [site, setSite] = useState<'all' | 'KBS' | 'BARC' | 'Colorado'>('all')
  const [era, setEra] = useState<'all' | 'HLS' | 'Landsat'>('all')
  const [yMin, setYMin] = useState(0)
  const [xKey, setXKey] = useState<NumKey>('ndvi_jul_aug')
  const [yKey, setYKey] = useState<NumKey>('RY_descr')

  const rows = useMemo(() => {
    const all = res.data?.rows ?? []
    return all.filter(
      (r) => (site === 'all' || r.dataset === site) && (era === 'all' || (era === 'HLS' ? r.sensor_era === 'HLS' : r.sensor_era !== 'HLS')) && (r.Y_t_ha ?? 0) >= yMin,
    )
  }, [res.data, site, era, yMin])

  if (res.error) return <Container><ErrorNote error={res.error} /></Container>
  if (!res.data) return <Container><Skeleton className="h-[600px]" /></Container>
  const c = res.data.counts
  const pts = rows
    .filter((r) => r[xKey] != null && r[yKey] != null)
    .map((r) => ({
      x: r[xKey] as number,
      y: r[yKey] as number,
      color: SITE_COLOR[r.dataset] ?? tokens.ink2,
      r: 3,
      label: (
        <>
          <p className="font-mono text-[11px] text-ink-3">{r.fy_key.split('|')[1]} · {r.year}</p>
          <p>{NUM.find((n) => n.key === xKey)!.label}: {fmt(r[xKey], NUM.find((n) => n.key === xKey)!.digits)}</p>
          <p>{NUM.find((n) => n.key === yKey)!.label}: {fmt(r[yKey], NUM.find((n) => n.key === yKey)!.digits)}</p>
        </>
      ),
    }))
  const xd = extent(pts, (p) => p.x) as [number, number]
  const yd = extent(pts, (p) => p.y) as [number, number]
  const pad = (d: [number, number]): [number, number] => (d[0] == null ? [0, 1] : [d[0] - (d[1] - d[0]) * 0.05, d[1] + (d[1] - d[0]) * 0.05])

  return (
    <section id="explorer" className="scroll-mt-20 py-20">
      <Container>
        <SectionHeader
          eyebrow="Daten erkunden"
          title={`${c.field_years} Mais-Feld-Jahre, 1989–2023.`}
          lede="Jedes Feld-Jahr mit gemessenem Ertrag im Projekt, mit seinen Satelliten-, Wetter- und Bodenkennwerten zum Stichtag 1. September. Filtern Sie, stellen Sie zwei beliebige Variablen gegenüber und sehen Sie selbst."
        />
        <Reveal className="mt-10 panel flex flex-wrap items-center gap-x-6 gap-y-4 p-4 sm:p-5">
          <label className="flex items-center gap-3 text-[13px] text-ink-3">
            Standort
            <Tabs size="sm" label="Standort" value={site} onChange={setSite} items={[{ value: 'all', label: 'Alle' }, { value: 'KBS', label: 'KBS' }, { value: 'BARC', label: 'BARC' }, { value: 'Colorado', label: 'Akron' }]} />
          </label>
          <label className="flex items-center gap-3 text-[13px] text-ink-3">
            Sensorzeitraum
            <Tabs size="sm" label="Sensorzeitraum" value={era} onChange={setEra} items={[{ value: 'all', label: 'Alle' }, { value: 'HLS', label: 'HLS / S2' }, { value: 'Landsat', label: 'Vor 2013' }]} />
          </label>
          <label className="flex items-center gap-3 text-[13px] text-ink-3">
            Ertrag ≥ <span className="w-12 font-mono text-ink">{fmtNum(yMin, Number.isInteger(yMin) ? 0 : 1)} t/ha</span>
            <input type="range" min={0} max={12} step={0.5} value={yMin} onChange={(e) => setYMin(Number(e.target.value))} className="h-1 w-36 cursor-pointer appearance-none rounded-full bg-white/10 accent-[var(--color-maize)]" aria-label="Mindestertrag" />
          </label>
          <span className="ml-auto font-mono text-[12px] text-ink-2">{rows.length} Feld-Jahre</span>
        </Reveal>

        <div className="mt-5 grid gap-5 lg:grid-cols-[1.25fr_1fr]">
          <Reveal className="panel p-6">
            <div className="mb-5 flex flex-wrap items-center gap-3 text-[13px] text-ink-3">
              <Select value={yKey} onChange={setYKey} label="Y-Achse" />
              <span>gegen</span>
              <Select value={xKey} onChange={setXKey} label="X-Achse" />
            </div>
            <Scatter points={pts} xLabel={NUM.find((n) => n.key === xKey)!.label} yLabel={NUM.find((n) => n.key === yKey)!.label} xDomain={pad(xd)} yDomain={pad(yd)} height={360} opacity={0.75} xFmt={(v) => fmt(v, NUM.find((n) => n.key === xKey)!.digits > 1 ? 2 : 0)} yFmt={(v) => fmt(v, NUM.find((n) => n.key === yKey)!.digits > 1 ? 2 : 0)} />
            <div className="mt-3 flex flex-wrap items-center gap-4 text-[12px] text-ink-2">
              {Object.entries(SITE_COLOR).map(([k, v]) => (
                <span key={k} className="flex items-center gap-1.5"><span className="size-2 rounded-full" style={{ background: v }} />{k === 'Colorado' ? 'Akron' : k} · {c.by_site[k]}</span>
              ))}
              <span className="ml-auto font-mono text-ink-3">Spearman ρ = {fmt(spearman(pts.map((p) => p.x), pts.map((p) => p.y)), 2)} · n = {pts.length}</span>
            </div>
          </Reveal>
          <Reveal className="panel p-6" delay={0.06}>
            <p className="eyebrow mb-5">Ertragsverteilung (t/ha)</p>
            <YieldHistogram rows={rows} />
            <p className="mt-4 text-[13px] leading-relaxed text-ink-3">
              Einen relativen Ertrag gibt es für {c.with_relative_yield} Feld-Jahre (ein Feld braucht mindestens zwei weitere Jahre, um seinen Normalertrag festzulegen). Nur{' '}
              8–11 davon sind unabhängige Standort-Jahre – die zentrale Grenze des Projekts.
            </p>
          </Reveal>
        </div>

        <Reveal className="mt-5 panel p-6">
          <p className="eyebrow mb-5">Rangkorrelationen zwischen den Variablen (gefilterte Zeilen)</p>
          <CorrMatrix rows={rows} />
        </Reveal>
        <Source className="mt-5">data/processed/gt_field_years.parquet · features_0901.parquet · gt_dekads.parquet (exportiert nach explorer.json)</Source>
      </Container>
    </section>
  )
}

function Select({ value, onChange, label }: { value: NumKey; onChange: (v: NumKey) => void; label: string }) {
  return (
    <select
      aria-label={label}
      value={value}
      onChange={(e) => onChange(e.target.value as NumKey)}
      className="h-9 rounded-[10px] border border-[var(--line-strong)] bg-soil-850 px-3 text-[13px] text-ink focus:border-maize focus:outline-none"
    >
      {NUM.map((n) => (
        <option key={n.key} value={n.key}>{n.label}</option>
      ))}
    </select>
  )
}

function rank(xs: number[]) {
  const idx = xs.map((v, i) => [v, i] as const).sort((a, b) => a[0] - b[0])
  const r = new Array<number>(xs.length)
  for (let i = 0; i < idx.length; ) {
    let j = i
    while (j + 1 < idx.length && idx[j + 1][0] === idx[i][0]) j++
    for (let k = i; k <= j; k++) r[idx[k][1]] = (i + j) / 2
    i = j + 1
  }
  return r
}

function spearman(a: number[], b: number[]): number {
  if (a.length < 5) return NaN
  const ra = rank(a)
  const rb = rank(b)
  const n = a.length
  const ma = ra.reduce((s, v) => s + v, 0) / n
  const mb = rb.reduce((s, v) => s + v, 0) / n
  let num = 0
  let da = 0
  let db = 0
  for (let i = 0; i < n; i++) {
    num += (ra[i] - ma) * (rb[i] - mb)
    da += (ra[i] - ma) ** 2
    db += (rb[i] - mb) ** 2
  }
  return num / Math.sqrt(da * db)
}

function YieldHistogram({ rows }: { rows: ExplorerRow[] }) {
  const [ref, width] = useWidth<HTMLDivElement>()
  const h = 250
  const m = { t: 10, r: 8, b: 30, l: 8 }
  const sites = ['KBS', 'BARC', 'Colorado']
  const bins = bin().domain([0, 16]).thresholds(16)
  const per = sites.map((s) => bins(rows.filter((r) => r.dataset === s && r.Y_t_ha != null).map((r) => r.Y_t_ha as number)))
  const totals = per[0].map((_, i) => per.reduce((a, p) => a + (p[i]?.length ?? 0), 0))
  const x = scaleLinear().domain([0, 16]).range([m.l, width - m.r])
  const y = scaleLinear().domain([0, Math.max(1, ...totals)]).range([h - m.b, m.t])
  return (
    <div ref={ref}>
      <svg width={width} height={h} role="img" aria-label="Ertragsverteilung nach Standort">
        {per[0].map((b, i) => {
          let acc = 0
          return (
            <g key={i}>
              {per.map((p, si) => {
                const n = p[i]?.length ?? 0
                const y0 = y(acc)
                acc += n
                const y1 = y(acc)
                return n ? <rect key={si} x={x(b.x0!) + 1} width={Math.max(1, x(b.x1!) - x(b.x0!) - 2)} y={y1} height={y0 - y1} rx={1.5} fill={SITE_COLOR[sites[si]]} opacity={0.85} /> : null
              })}
            </g>
          )
        })}
        {[0, 4, 8, 12, 16].map((t) => (
          <text key={t} x={x(t)} y={h - 10} textAnchor="middle" {...axisText}>{t}</text>
        ))}
      </svg>
    </div>
  )
}

function CorrMatrix({ rows }: { rows: ExplorerRow[] }) {
  const keys = NUM.map((n) => n.key)
  const [hover, setHover] = useState<[number, number] | null>(null)
  const mat = useMemo(
    () =>
      keys.map((a) =>
        keys.map((b) => {
          const pairs = rows.filter((r) => r[a] != null && r[b] != null)
          return spearman(pairs.map((r) => r[a] as number), pairs.map((r) => r[b] as number))
        }),
      ),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [rows],
  )
  const color = (v: number) => {
    if (!Number.isFinite(v)) return 'transparent'
    const a = Math.min(1, Math.abs(v))
    return v >= 0 ? `rgba(143,181,154,${a * 0.85})` : `rgba(228,105,74,${a * 0.85})`
  }
  return (
    <div className="overflow-x-auto">
      <table className="table-fixed border-separate border-spacing-[3px] text-[11.5px]">
        <colgroup>
          <col style={{ width: 150 }} />
          {NUM.map((n) => <col key={n.key} style={{ width: 58 }} />)}
        </colgroup>
        <thead>
          <tr>
            <th />
            {NUM.map((n, j) => (
              <th key={n.key} className={`relative h-28 font-normal ${hover?.[1] === j ? 'text-ink' : 'text-ink-3'}`}>
                <span className="absolute bottom-2 left-1/2 origin-bottom-left -rotate-45 whitespace-nowrap">{n.label}</span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {NUM.map((n, i) => (
            <tr key={n.key}>
              <th className={`pr-3 text-right font-normal whitespace-nowrap ${hover?.[0] === i ? 'text-ink' : 'text-ink-3'}`}>{n.label}</th>
              {mat[i].map((v, j) => (
                <td
                  key={j}
                  onMouseEnter={() => setHover([i, j])}
                  onMouseLeave={() => setHover(null)}
                  className="h-9 rounded-[5px] text-center font-mono tabular text-ink"
                  style={{ background: color(v), outline: hover?.[0] === i && hover?.[1] === j ? '1px solid #eceee6' : undefined }}
                  title={`${n.label} × ${NUM[j].label}: ρ ${fmt(v, 2)}`}
                >
                  {i === j ? '' : fmt(v, 2)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="mt-4 flex items-center gap-3 text-[12px] text-ink-3">
        <Badge tone="sage">positiv</Badge>
        <Badge tone="rust">negativ</Badge>
        <span>Über Standorte und Jahre zusammengefasst: Starke Werte spiegeln oft Unterschiede zwischen Standorten oder Jahren wider, nicht Feldeffekte.</span>
      </div>
    </div>
  )
}

