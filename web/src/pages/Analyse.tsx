import { AnimatePresence, motion } from 'motion/react'
import { ArrowDown, Layers as LayersIcon, Loader2, MapPin, PenLine, Play, RotateCcw, Search, X } from 'lucide-react'
import { useEffect, useMemo, useReducer, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import type { FieldAnalysis, Polygon } from '../api/types'
import { PipelinePanel } from '../components/field/PipelinePanel'
import { Assessment, PhaseContributions, SatellitePanel, SoilPanel, WeatherPanel, WithinFieldPanel } from '../components/field/Results'
import { FieldMap, type Basemap, type CellOverlay } from '../components/map/FieldMap'
import { Badge, LiveBadge, SimulatedBadge, type Tone } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Container } from '../components/ui/Section'
import { ErrorNote } from '../components/ui/States'
import { Tabs } from '../components/ui/Tabs'
import { ndviColor, relYieldColor } from '../lib/color'
import { N_DEKADS, dekadLabel } from '../lib/dekads'
import { fmtArea, fmtCutoff } from '../lib/format'
import { areaM2, cellSquare } from '../lib/geo'
import { filledSeries } from '../lib/series'
import { useResource } from '../lib/useResource'
import { backendAvailable } from '../services/backendService'
import { getEvidence } from '../services/evidenceService'
import { getPreparedFields, runAnalysis } from '../services/fieldService'
import { searchPlaces, type Place } from '../services/geocodeService'
import { analysisReducer, initialAnalysis, isRunning } from '../state/analysisMachine'

const ROLE_TONE: Record<string, Tone> = { healthy: 'sage', stressed: 'rust', average: 'neutral', edge: 'maize', missed: 'water' }
const MIN_AREA = 3000 // m²
const MAX_AREA = 2_000_000 // m² (200 ha)
const CUTOFFS = ['06-01', '06-15', '07-01', '07-15', '08-01', '08-15', '09-01']
const LAST_SEASON = new Date().getMonth() >= 9 ? new Date().getFullYear() : new Date().getFullYear() - 1

type Layer = 'none' | 'season' | 'weak' | 'yield'

export default function Analyse() {
  const { t } = useTranslation()
  const fields = useResource(getPreparedFields, 'fields')
  const evidence = useResource(getEvidence, 'evidence')
  const [state, dispatch] = useReducer(analysisReducer, initialAnalysis)
  const [basemap, setBasemap] = useState<Basemap>('satellite')
  const [drawing, setDrawing] = useState(false)
  const [layer, setLayer] = useState<Layer>('weak')
  const [dekad, setDekad] = useState(12)
  const [year, setYear] = useState(LAST_SEASON)
  const [cutoff, setCutoff] = useState('09-01')
  const [live, setLive] = useState<boolean | null>(null)
  const [flyTo, setFlyTo] = useState<{ center: [number, number]; zoom?: number; bbox?: [number, number, number, number]; key: number } | null>(null)
  const resultsRef = useRef<HTMLDivElement>(null)

  const prepared = useMemo(() => fields.data?.fields ?? [], [fields.data])
  const label = (f: FieldAnalysis) => t(`analyse.fields.${f.id}.label`, { defaultValue: f.label })
  const title = (f: FieldAnalysis) => t(`analyse.fields.${f.id}.title`, { defaultValue: f.title })
  const blurb = (f: FieldAnalysis) => t(`analyse.fields.${f.id}.blurb`, { defaultValue: f.blurb })
  const mapFields = useMemo(() => prepared.map((f) => ({ id: f.id, label: f.label, geometry: f.geometry, role: f.role })), [prepared])
  const selectedPrepared = state.selection?.kind === 'prepared' ? prepared.find((f) => f.id === (state.selection as { id: string }).id) : undefined
  const result = state.result

  useEffect(() => {
    backendAvailable().then(setLive)
  }, [])

  // Run the pipeline when a new run starts.
  useEffect(() => {
    if (state.status !== 'loadingSatellite' || !state.selection) return
    const ctrl = new AbortController()
    runAnalysis(
      state.selection,
      { onStage: (stage) => dispatch({ type: 'stage', stage }), onStageDone: (stage, facts) => dispatch({ type: 'stageDone', stage, facts }) },
      ctrl.signal,
      { year, cutoff },
    ).then(
      (r) => dispatch({ type: 'complete', result: r }),
      (e: Error) => e.name !== 'AbortError' && dispatch({ type: 'fail', message: e.message }),
    )
    return () => ctrl.abort()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.runId])

  useEffect(() => {
    if (state.status === 'completed') setLayer(result?.pixels ? 'weak' : 'none')
  }, [state.status, result])

  const selectPrepared = (f: FieldAnalysis) => {
    setDrawing(false)
    dispatch({ type: 'select', selection: { kind: 'prepared', id: f.id, polygon: f.geometry, areaM2: f.area_m2, label: `${label(f)} · ${title(f)}` } })
  }

  const onPolygon = (p: Polygon | null) => {
    setDrawing(false)
    if (!p) return dispatch({ type: 'clear' })
    dispatch({ type: 'select', selection: { kind: 'custom', polygon: p, areaM2: areaM2(p), label: t('analyse.yourField') } })
  }

  // Cell overlay on the map (after the analysis).
  const overlay = useMemo<CellOverlay | null>(() => {
    const px = result?.pixels
    if (!px || layer === 'none' || state.status !== 'completed') return null
    const filled = layer === 'season' && px.ndvi_by_dekad ? filledSeries(px.ndvi_by_dekad) : null
    return {
      type: 'FeatureCollection',
      features: px.cells.map((c, i) => {
        let color = '#555'
        let opacity = 0.85
        if (layer === 'season') {
          const v = filled?.[dekad]?.[i]
          color = Number.isFinite(v) ? ndviColor(v as number) : '#333'
        } else if (layer === 'yield') color = relYieldColor(c[5])
        else {
          const weak = c[4] != null && c[4] <= px.weak_threshold
          color = weak ? '#e4694a' : '#eceee6'
          opacity = weak ? 0.88 : 0.08
        }
        return { type: 'Feature', geometry: { type: 'Polygon', coordinates: [cellSquare(c[0], c[1], px.cell_m * 0.92)] }, properties: { color, opacity } }
      }),
    }
  }, [result, layer, dekad, state.status])

  const sel = state.selection
  const areaWarning = sel?.kind === 'custom' ? (sel.areaM2 < MIN_AREA ? t('analyse.tooSmall') : sel.areaM2 > MAX_AREA ? t('analyse.tooLarge') : null) : null
  const running = isRunning(state.status)
  const years = Array.from({ length: LAST_SEASON - 2016 + 1 }, (_, i) => LAST_SEASON - i)

  return (
    <>
      <section className="relative flex flex-col pt-16 lg:h-dvh lg:min-h-[640px] lg:flex-row">
        {/* Map */}
        <div className="relative h-[56vh] min-h-[360px] lg:h-auto lg:flex-1">
          <FieldMap
            fields={mapFields}
            selectedId={sel?.kind === 'prepared' ? sel.id : null}
            selectedGeometry={selectedPrepared?.geometry ?? null}
            overlay={overlay}
            basemap={basemap}
            drawing={drawing}
            onSelectField={(id) => {
              const f = prepared.find((x) => x.id === id)
              if (f && !running) selectPrepared(f)
            }}
            onPolygon={onPolygon}
            flyTo={flyTo}
          />
          <div className="pointer-events-none absolute inset-x-3 top-3 flex flex-wrap items-start justify-between gap-2 sm:inset-x-4 sm:top-4">
            <PlaceSearch onPick={(p) => setFlyTo({ center: p.center, bbox: p.bbox, key: Date.now() })} />
            <div className="pointer-events-auto flex items-center gap-2">
              <Tabs
                size="sm"
                label={t('analyse.basemap')}
                value={basemap}
                onChange={setBasemap}
                className="panel-glass !rounded-[12px] !border-white/10"
                items={[
                  { value: 'satellite', label: t('analyse.satellite') },
                  { value: 'sentinel', label: t('analyse.sentinel') },
                  { value: 'terrain', label: t('analyse.terrain') },
                ]}
              />
            </div>
          </div>
          <div className="pointer-events-none absolute bottom-10 left-3 right-3 flex flex-col items-start gap-2 sm:left-4">
            <div className="pointer-events-auto flex gap-2">
              <Button
                size="sm"
                variant={drawing ? 'primary' : 'secondary'}
                className={drawing ? '' : 'panel-glass !border-white/10'}
                icon={drawing ? <X className="size-3.5" /> : <PenLine className="size-3.5" />}
                disabled={running}
                onClick={() => setDrawing((d) => !d)}
              >
                {drawing ? t('analyse.cancelDraw') : t('analyse.draw')}
              </Button>
            </div>
            <AnimatePresence>
              {drawing && (
                <motion.p initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="panel-glass px-3 py-2 text-[12.5px] text-ink-2">
                  {t('analyse.drawHelp')}
                </motion.p>
              )}
              {state.status === 'completed' && result?.pixels && (
                <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="panel-glass pointer-events-auto flex flex-col gap-2 p-2.5">
                  <div className="flex items-center gap-2">
                    <LayersIcon className="ml-1 size-3.5 text-ink-3" />
                    <Tabs
                      size="sm"
                      label={t('analyse.layer')}
                      value={layer}
                      onChange={setLayer}
                      items={[
                        { value: 'weak', label: t('analyse.layerFlagged') },
                        { value: 'season', label: t('analyse.layerSeason') },
                        { value: 'yield', label: result.simulated ? t('analyse.layerYieldSim') : t('analyse.layerYield') },
                        { value: 'none', label: t('analyse.layerOff') },
                      ]}
                    />
                  </div>
                  {layer === 'season' && (
                    <div className="flex items-center gap-3 px-1">
                      <input type="range" min={0} max={N_DEKADS - 1} value={dekad} onChange={(e) => setDekad(Number(e.target.value))} aria-label={t('analyse.dekad')} className="h-1 w-48 cursor-pointer appearance-none rounded-full bg-white/15 accent-[var(--color-maize)]" />
                      <span className="w-16 font-mono text-[11px] text-ink-2">{dekadLabel(dekad, result.year)}</span>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Side panel */}
        <aside className="relative flex w-full flex-col border-t border-[var(--line)] bg-soil-900/95 lg:w-[420px] lg:border-l lg:border-t-0">
          <div className="flex-1 p-5 sm:p-6 lg:overflow-y-auto">
            <AnimatePresence mode="wait">
              {state.status === 'idle' && (
                <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <div className="flex items-center justify-between gap-3">
                    <p className="eyebrow">{t('analyse.eyebrow')}</p>
                    {live === true && <LiveBadge />}
                  </div>
                  <h1 className="mt-3 text-[30px] leading-tight">{t('analyse.title')}</h1>
                  <p className="mt-3 text-[14px] leading-relaxed text-ink-2">{t('analyse.lede')}</p>
                  {fields.error && <div className="mt-6"><ErrorNote error={fields.error} /></div>}
                  <ul className="mt-6 flex flex-col gap-2">
                    {prepared.map((f) => (
                      <li key={f.id}>
                        <button
                          type="button"
                          onClick={() => selectPrepared(f)}
                          className="group flex w-full items-start gap-4 rounded-xl border border-[var(--line)] bg-white/[0.02] p-4 text-left transition hover:border-[var(--line-strong)] hover:bg-white/[0.045]"
                        >
                          <span className="mt-0.5 font-display text-[15px] font-semibold text-maize">{label(f).split(' ').at(-1)}</span>
                          <span className="min-w-0 flex-1">
                            <span className="flex flex-wrap items-center gap-2">
                              <span className="text-[14.5px] font-medium text-ink">{title(f)}</span>
                              <Badge tone={ROLE_TONE[f.role]}>{f.site} {f.field_id.replace(/_/g, '-')} · {f.year}</Badge>
                            </span>
                            <span className="mt-1 block text-[13px] leading-snug text-ink-3">{blurb(f)}</span>
                          </span>
                          <MapPin className="mt-1 size-4 text-ink-4 transition group-hover:text-ink-2" />
                        </button>
                      </li>
                    ))}
                  </ul>
                </motion.div>
              )}

              {sel && state.status !== 'idle' && (
                <motion.div key="sel" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex flex-col gap-6">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="eyebrow">{sel.kind === 'prepared' ? `${selectedPrepared?.site} · ${selectedPrepared?.field_id.replace(/_/g, '-')} · ${selectedPrepared?.year}` : t('analyse.drawnField')}</p>
                      <h2 className="mt-2 text-[24px] leading-tight">{sel.label}</h2>
                      <p className="mt-1 font-mono text-[12.5px] text-ink-3">
                        {fmtArea(sel.areaM2)}
                        {sel.kind === 'prepared' && selectedPrepared?.treatment ? ` · ${t('analyse.treatment', { t: selectedPrepared.treatment })}` : ''}
                      </p>
                    </div>
                    <button type="button" aria-label={t('analyse.clear')} onClick={() => dispatch({ type: 'clear' })} className="rounded-lg p-1.5 text-ink-3 hover:bg-white/5 hover:text-ink">
                      <X className="size-4" />
                    </button>
                  </div>
                  {sel.kind === 'custom' && (live ? <LiveBadge /> : <SimulatedBadge />)}
                  {state.status === 'fieldSelected' && (
                    <>
                      {selectedPrepared && <p className="text-[14px] leading-relaxed text-ink-2">{blurb(selectedPrepared)}</p>}
                      {sel.kind === 'custom' && live && (
                        <div className="grid grid-cols-2 gap-3">
                          <label className="flex flex-col gap-1.5 text-[12px] text-ink-3">
                            {t('analyse.year')}
                            <select value={year} onChange={(e) => setYear(Number(e.target.value))} className="h-10 rounded-[10px] border border-[var(--line-strong)] bg-soil-850 px-3 text-[14px] text-ink focus:border-maize focus:outline-none">
                              {years.map((y) => <option key={y} value={y}>{y}</option>)}
                            </select>
                          </label>
                          <label className="flex flex-col gap-1.5 text-[12px] text-ink-3">
                            {t('analyse.cutoff')}
                            <select value={cutoff} onChange={(e) => setCutoff(e.target.value)} className="h-10 rounded-[10px] border border-[var(--line-strong)] bg-soil-850 px-3 text-[14px] text-ink focus:border-maize focus:outline-none">
                              {CUTOFFS.map((c) => <option key={c} value={c}>{fmtCutoff(c)}</option>)}
                            </select>
                          </label>
                        </div>
                      )}
                      {areaWarning && <p className="text-[13px] text-rust">{areaWarning}</p>}
                      <Button size="lg" icon={<Play className="size-4" />} disabled={Boolean(areaWarning)} onClick={() => dispatch({ type: 'start' })}>
                        {t('analyse.run')}
                      </Button>
                    </>
                  )}
                  {(running || state.status === 'completed' || state.status === 'error') && <PipelinePanel state={state} />}
                  {state.status === 'error' && (
                    <div className="rounded-xl border border-rust/30 bg-rust/5 p-4 text-[13.5px] text-ink-2">
                      <p className="font-medium text-rust">{t('analyse.stopped')}</p>
                      <p className="mt-1">{state.error}</p>
                      <Button className="mt-3" size="sm" variant="secondary" icon={<RotateCcw className="size-3.5" />} onClick={() => dispatch({ type: 'start' })}>
                        {t('analyse.again')}
                      </Button>
                    </div>
                  )}
                  {state.status === 'completed' && (
                    <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col gap-2">
                      <Button size="lg" icon={<ArrowDown className="size-4" />} onClick={() => resultsRef.current?.scrollIntoView({ behavior: 'smooth' })}>
                        {t('analyse.viewResult')}
                      </Button>
                      <Button variant="ghost" size="sm" icon={<RotateCcw className="size-3.5" />} onClick={() => dispatch({ type: 'clear' })}>
                        {t('analyse.another')}
                      </Button>
                    </motion.div>
                  )}
                  {running && (
                    <p className="flex items-center gap-2 text-[12px] text-ink-4">
                      <Loader2 className="size-3.5 animate-spin" />
                      {sel.kind === 'prepared' ? t('analyse.replaying') : live ? t('analyse.computing') : t('analyse.simulating')}
                    </p>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </aside>
      </section>

      {/* Results */}
      <div ref={resultsRef} className="scroll-mt-16">
        {state.status === 'completed' && result && (
          <Container className="flex flex-col gap-5 py-16">
            <div className="mb-4 flex flex-wrap items-end justify-between gap-4">
              <div>
                <p className="eyebrow">{t('analyse.resultEyebrow', { label: label(result) })}</p>
                <h2 className="mt-3 text-[clamp(2rem,4vw,3rem)]">{title(result)}</h2>
                <p className="mt-2 font-mono text-[12.5px] text-ink-3">
                  {result.site} · {result.field_id.replace(/_/g, '-')} · {result.year} · {fmtArea(result.area_m2)}
                </p>
              </div>
              {result.simulated ? <SimulatedBadge /> : result.live ? <LiveBadge /> : null}
            </div>
            <Assessment f={result} />
            <PhaseContributions f={result} typical={evidence.data?.alarm.phase_sum_mean} />
            <SatellitePanel f={result} />
            <WithinFieldPanel f={result} />
            <WeatherPanel f={result} />
            <SoilPanel f={result} />
            <p className="mt-4 text-[12.5px] leading-relaxed text-ink-4">
              {result.simulated ? t('analyse.footSim') : result.live ? t('analyse.footLive') : t('analyse.footPrepared')}
            </p>
          </Container>
        )}
      </div>
    </>
  )
}

/* ------------------------------------------------------------------ */

function PlaceSearch({ onPick }: { onPick: (p: Place) => void }) {
  const { t } = useTranslation()
  const [q, setQ] = useState('')
  const [hits, setHits] = useState<Place[]>([])
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    if (q.trim().length < 3) {
      setHits([])
      return
    }
    const ctrl = new AbortController()
    const timer = setTimeout(() => {
      setBusy(true)
      searchPlaces(q, ctrl.signal)
        .then((h) => {
          setHits(h)
          setErr(null)
          setOpen(true)
        })
        .catch((e: Error) => e.name !== 'AbortError' && setErr(t('analyse.searchOffline')))
        .finally(() => setBusy(false))
    }, 450)
    return () => {
      clearTimeout(timer)
      ctrl.abort()
    }
  }, [q, t])

  return (
    <div className="pointer-events-auto relative w-full max-w-[340px]">
      <div className="panel-glass flex h-10 items-center gap-2 px-3">
        {busy ? <Loader2 className="size-4 animate-spin text-ink-3" /> : <Search className="size-4 text-ink-3" />}
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onFocus={() => hits.length && setOpen(true)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && hits[0]) {
              onPick(hits[0])
              setOpen(false)
            }
            if (e.key === 'Escape') setOpen(false)
          }}
          placeholder={t('analyse.search')}
          aria-label={t('analyse.searchAria')}
          className="h-full w-full bg-transparent text-[13.5px] text-ink placeholder:text-ink-4 focus:outline-none"
        />
      </div>
      {(open && hits.length > 0) || err ? (
        <div className="panel-glass absolute inset-x-0 top-12 z-20 overflow-hidden p-1">
          {err ? (
            <p className="px-3 py-2 text-[12.5px] text-ink-3">{err}</p>
          ) : (
            hits.map((h) => (
              <button
                key={h.id}
                type="button"
                onClick={() => {
                  onPick(h)
                  setOpen(false)
                  setQ(h.name)
                }}
                className="block w-full rounded-lg px-3 py-2 text-left hover:bg-white/[0.06]"
              >
                <span className="block text-[13.5px] text-ink">{h.name}</span>
                <span className="block truncate text-[11.5px] text-ink-3">{h.detail}</span>
              </button>
            ))
          )}
          <p className="px-3 pb-1 pt-1.5 text-[10px] text-ink-4">{t('analyse.searchCredit')}</p>
        </div>
      ) : null}
    </div>
  )
}
