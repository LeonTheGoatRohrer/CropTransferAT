import { AnimatePresence, motion } from 'motion/react'
import { Check, Download, PenLine, X } from 'lucide-react'
import { useMemo, useState } from 'react'
import type { Polygon } from '../api/types'
import { FieldMap, type Basemap } from '../components/map/FieldMap'
import { PlaceSearch } from '../components/map/PlaceSearch'
import { Button } from '../components/ui/Button'
import { AT_SITES, AUSTRIA_BOUNDS } from '../data/content/atSites'
import { Tabs } from '../components/ui/Tabs'
import { fmt, fmtArea } from '../lib/format'
import { areaM2 } from '../lib/geo'
import { downloadContributions, judgeYield, listContributions, submitContribution, type Contribution } from '../services/contributionService'

const THIS_YEAR = 2026
const PAST_YEARS = [2025, 2024, 2023, 2022, 2021]
const MIN_AREA = 3000
const MAX_AREA = 2_000_000

const SITE_POINTS = AT_SITES.map((s) => ({
  id: s.id,
  title: `${s.name} (${s.region})`,
  text: `Trial site with ${s.years} yield years (${s.from}–${s.to}), average ${s.meanTHa.toFixed(1)} t/ha.`,
  lngLat: s.lngLat,
}))

type Unit = 't' | 'dt'

/** Parse "9,8" / "9.8" into t/ha; returns null when empty or out of range. */
function toT(raw: string, unit: Unit): number | null {
  const v = Number(raw.replace(',', '.'))
  if (!raw.trim() || !Number.isFinite(v) || v <= 0) return null
  const t = unit === 'dt' ? v / 10 : v
  return t > 0 && t <= 25 ? t : null
}

export default function Contribute() {
  const [polygon, setPolygon] = useState<Polygon | null>(null)
  const [drawing, setDrawing] = useState(false)
  const [basemap, setBasemap] = useState<Basemap>('satellite')
  const [flyTo, setFlyTo] = useState<{ center: [number, number]; bbox?: [number, number, number, number]; key: number } | null>(null)
  const [unit, setUnit] = useState<Unit>('dt')
  const [past, setPast] = useState<Record<number, string>>({})
  const [now, setNow] = useState('')
  const [nowStatus, setNowStatus] = useState<'harvested' | 'estimate'>('harvested')
  const [name, setName] = useState('')
  const [cropType, setCropType] = useState<'grain' | 'silage'>('grain')
  const [irrigated, setIrrigated] = useState(false)
  const [consent, setConsent] = useState(false)
  const [sent, setSent] = useState<{ contribution: Contribution; saved: 'server' | 'browser' } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [stored, setStored] = useState(() => listContributions().length)

  const area = polygon ? areaM2(polygon) : 0
  const outside = polygon ? !polygon.coordinates[0].every(([x, y]) => x >= AUSTRIA_BOUNDS[0] && x <= AUSTRIA_BOUNDS[2] && y >= AUSTRIA_BOUNDS[1] && y <= AUSTRIA_BOUNDS[3]) : false
  const areaProblem = outside ? 'Please draw a field in Austria.' : polygon ? (area < MIN_AREA ? 'Too small, draw at least 0.3 ha.' : area > MAX_AREA ? 'Too large, draw a single field (max. 200 ha).' : null) : null

  const pastYields = useMemo(
    () => PAST_YEARS.flatMap((y) => { const t = toT(past[y] ?? '', unit); return t == null ? [] : [{ year: y, tPerHa: t }] }),
    [past, unit],
  )
  const nowT = toT(now, unit)
  const verdict = judgeYield(pastYields, nowT)
  const canSend = Boolean(polygon) && !areaProblem && (pastYields.length >= 1 || nowT != null) && consent

  const send = async () => {
    if (!polygon || !canSend) return
    setBusy(true)
    setError(null)
    try {
      setSent(await submitContribution({
      polygon,
      areaM2: area,
      fieldName: name.trim(),
      cropType,
      irrigated,
      pastYields,
      thisYear: nowT == null ? null : { year: THIS_YEAR, tPerHa: nowT, status: nowStatus },
      }))
      setStored(listContributions().length)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setBusy(false)
    }
  }

  const reset = () => {
    setSent(null)
    setPolygon(null)
    setPast({})
    setNow('')
    setName('')
    setConsent(false)
  }

  return (
    <section className="relative flex flex-col pt-16 lg:h-dvh lg:min-h-[680px] lg:flex-row">
      <div className="relative h-[46vh] min-h-[320px] lg:h-auto lg:flex-1">
        <FieldMap
          fields={[]}
          selectedId={null}
          selectedGeometry={null}
          overlay={null}
          basemap={basemap}
          drawing={drawing}
          onSelectField={() => {}}
          onPolygon={(p) => {
            setDrawing(false)
            setPolygon(p)
          }}
          flyTo={flyTo}
          bounds={AUSTRIA_BOUNDS}
          points={SITE_POINTS}
        />
        <div className="pointer-events-none absolute inset-x-3 top-3 flex flex-wrap items-start justify-between gap-2 sm:inset-x-4 sm:top-4">
          <PlaceSearch countryCode="at" onPick={(p) => setFlyTo({ center: p.center, bbox: p.bbox, key: Date.now() })} />
          <Tabs
            size="sm"
            label="Base map"
            value={basemap}
            onChange={setBasemap}
            className="panel-glass pointer-events-auto !rounded-[12px] !border-white/10"
            items={[{ value: 'satellite', label: 'Satellite' }, { value: 'terrain', label: 'Terrain' }]}
          />
        </div>
        <div className="pointer-events-none absolute bottom-10 left-3 flex flex-col items-start gap-2 sm:left-4">
          <Button
            size="sm"
            variant={drawing ? 'primary' : 'secondary'}
            className={`pointer-events-auto ${drawing ? '' : 'panel-glass !border-white/10'}`}
            icon={drawing ? <X className="size-3.5" /> : <PenLine className="size-3.5" />}
            onClick={() => setDrawing((d) => !d)}
          >
            {drawing ? 'Cancel' : polygon ? 'Redraw field' : 'Draw your field'}
          </Button>
          {drawing && <p className="panel-glass px-3 py-2 text-[12.5px] text-ink-2">Click the corners of your field. Click the first corner to close it.</p>}
        </div>
      </div>

      <aside className="relative flex w-full flex-col border-t border-[var(--line)] bg-soil-900/95 lg:w-[460px] lg:border-l lg:border-t-0">
        <div className="flex-1 p-5 sm:p-6 lg:overflow-y-auto">
          <AnimatePresence mode="wait">
            {sent ? (
              <motion.div key="done" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col gap-5">
                <span className="grid size-10 place-items-center rounded-full bg-sage/15 text-sage"><Check className="size-5" /></span>
                <h1 className="text-[28px] leading-tight">Thank you. Your field is in.</h1>
                <p className="text-[14.5px] leading-relaxed text-ink-2">
                  Every field with a known yield makes the forecast for the next farmer better. Come back next year to add the new harvest.
                </p>
                {verdict && <Result verdict={verdict} now={nowT} />}
                <p className="rounded-xl border border-[var(--line)] bg-white/[0.02] p-4 text-[12.5px] leading-relaxed text-ink-3">
                  {sent.saved === 'server'
                    ? 'Saved on the project server.'
                    : `The project server could not be reached, so your entry is kept in this browser for now (${stored} so far). You can download it.`}
                </p>
                <div className="flex flex-wrap gap-2">
                  <Button variant="secondary" size="sm" icon={<Download className="size-3.5" />} onClick={() => downloadContributions(listContributions())}>Download entries</Button>
                  <Button variant="ghost" size="sm" onClick={reset}>Add another field</Button>
                </div>
              </motion.div>
            ) : (
              <motion.div key="form" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col gap-7">
                <div>
                  <p className="eyebrow">Add your field</p>
                  <h1 className="mt-3 text-[28px] leading-tight">Share your yields. Get a forecast for your field.</h1>
                  <p className="mt-3 text-[14px] leading-relaxed text-ink-2">
                    The dots on the map are trial sites that already have yield data. Takes two minutes. You tell us what your field yielded; we tell you how this year compares, and the data helps the models learn Austria.
                  </p>
                </div>

                <Step n={1} title="Where is your field?" done={Boolean(polygon) && !areaProblem}>
                  {polygon ? (
                    <p className="text-[14px] text-ink">{fmtArea(area)} drawn. {areaProblem && <span className="text-rust">{areaProblem}</span>}</p>
                  ) : (
                    <p className="text-[14px] text-ink-3">Zoom to your village (search works for Austria), then press “Draw your field”. Just the outline; no address needed.</p>
                  )}
                </Step>

                <Step n={2} title="What did it yield?" done={pastYields.length > 0 || nowT != null}>
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <p className="text-[12.5px] text-ink-3">Leave out years you don’t know. Two or more earlier years give you a comparison.</p>
                    <Tabs size="sm" label="Unit" value={unit} onChange={setUnit} items={[{ value: 'dt', label: 'dt/ha' }, { value: 't', label: 't/ha' }]} />
                  </div>
                  <div className="grid grid-cols-[1fr_120px] items-center gap-x-4 gap-y-2">
                    <span className="text-[14px] font-medium text-maize">{THIS_YEAR} (this year)</span>
                    <YieldInput value={now} onChange={setNow} unit={unit} label={`Yield ${THIS_YEAR}`} />
                    <div className="col-span-2 -mt-1">
                      <Tabs size="sm" label="This year status" value={nowStatus} onChange={setNowStatus} items={[{ value: 'harvested', label: 'Harvested' }, { value: 'estimate', label: 'My estimate so far' }]} />
                    </div>
                    {PAST_YEARS.map((y) => (
                      <label key={y} className="contents">
                        <span className="text-[14px] text-ink-2">{y}</span>
                        <YieldInput value={past[y] ?? ''} onChange={(v) => setPast((p) => ({ ...p, [y]: v }))} unit={unit} label={`Yield ${y}`} />
                      </label>
                    ))}
                  </div>
                </Step>

                {verdict && (
                  <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}>
                    <Result verdict={verdict} now={nowT} />
                  </motion.div>
                )}

                <Step n={3} title="A few details (optional)" done={false}>
                  <div className="flex flex-col gap-3">
                    <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Field name, e.g. Acker hinter dem Hof" aria-label="Field name" className="h-10 rounded-[10px] border border-[var(--line-strong)] bg-soil-850 px-3 text-[14px] text-ink placeholder:text-ink-4 focus:border-maize focus:outline-none" />
                    <div className="flex flex-wrap items-center gap-4">
                      <Tabs size="sm" label="Maize type" value={cropType} onChange={setCropType} items={[{ value: 'grain', label: 'Grain maize' }, { value: 'silage', label: 'Silage maize' }]} />
                      <label className="flex items-center gap-2 text-[13.5px] text-ink-2">
                        <input type="checkbox" checked={irrigated} onChange={(e) => setIrrigated(e.target.checked)} className="size-4 accent-[var(--color-maize)]" /> Irrigated
                      </label>
                    </div>
                  </div>
                </Step>

                <div className="flex flex-col gap-4 border-t border-[var(--line)] pt-5">
                  <label className="flex items-start gap-3 text-[13px] leading-relaxed text-ink-2">
                    <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} className="mt-0.5 size-4 shrink-0 accent-[var(--color-maize)]" />
                    <span>I agree that the outline and yields of this field are used to train and test the models of this research project. No name, address or contact details are stored.</span>
                  </label>
                  <Button size="lg" disabled={!canSend || busy} onClick={send}>{busy ? 'Sending…' : 'Send and get my result'}</Button>
                  {error && <p role="alert" className="text-[13px] text-rust">{error}</p>}
                  {!canSend && <p className="text-[12px] text-ink-4">Needs: a drawn field, at least one yield and your agreement.</p>}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </aside>
    </section>
  )
}

function Step({ n, title, done, children }: { n: number; title: string; done: boolean; children: React.ReactNode }) {
  return (
    <div className="flex gap-4">
      <span className={`mt-0.5 grid size-7 shrink-0 place-items-center rounded-full border font-mono text-[12px] ${done ? 'border-sage/40 bg-sage/15 text-sage' : 'border-[var(--line-strong)] text-ink-3'}`}>
        {done ? <Check className="size-3.5" /> : n}
      </span>
      <div className="min-w-0 flex-1">
        <h2 className="mb-3 text-[17px] font-semibold tracking-[-0.01em]">{title}</h2>
        {children}
      </div>
    </div>
  )
}

function YieldInput({ value, onChange, unit, label }: { value: string; onChange: (v: string) => void; unit: Unit; label: string }) {
  const bad = value.trim() !== '' && toT(value, unit) == null
  return (
    <div className="relative">
      <input
        inputMode="decimal"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        aria-label={label}
        aria-invalid={bad}
        placeholder={unit === 'dt' ? '100' : '10'}
        className={`h-10 w-full rounded-[10px] border bg-soil-850 pl-3 pr-14 text-right font-mono text-[14px] text-ink placeholder:text-ink-4 focus:outline-none ${bad ? 'border-rust' : 'border-[var(--line-strong)] focus:border-maize'}`}
      />
      <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 font-mono text-[11px] text-ink-4">{unit}/ha</span>
    </div>
  )
}

function Result({ verdict, now }: { verdict: NonNullable<ReturnType<typeof judgeYield>>; now: number | null }) {
  const pct = Math.round(verdict.ratio * 100)
  const tone = verdict.label === 'below' ? 'text-rust' : verdict.label === 'above' ? 'text-sage' : 'text-maize'
  const text = { below: 'Below your usual yield', normal: 'About your usual yield', above: 'Above your usual yield' }[verdict.label]
  return (
    <div className="rounded-2xl border border-[var(--line-strong)] bg-white/[0.03] p-5">
      <p className="eyebrow">Your result</p>
      <p className={`mt-2 font-display text-[34px] font-semibold tracking-[-0.03em] ${tone}`}>{pct} %</p>
      <p className="text-[15px] text-ink">{text}</p>
      <p className="mt-2 text-[13px] leading-relaxed text-ink-3">
        {fmt(now, 1)} t/ha this year against {fmt(verdict.normal, 1)} t/ha on average over your last {verdict.n} years. Satellite and weather analysis of your field follows once the project server is connected.
      </p>
    </div>
  )
}
