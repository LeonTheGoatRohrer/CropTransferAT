import { AnimatePresence, motion } from 'motion/react'
import { ArrowDown, Layers as LayersIcon, Loader2, MapPin, PenLine, Play, RotateCcw, X } from 'lucide-react'
import { useEffect, useMemo, useReducer, useRef, useState } from 'react'
import type { FieldAnalysis, Polygon } from '../api/types'
import { ModeSwitch } from '../components/field/ModeSwitch'
import { PipelinePanel } from '../components/field/PipelinePanel'
import { filledSeries } from '../lib/series'
import { Assessment, PhaseContributions, SatellitePanel, SoilPanel, WeatherPanel, WithinFieldPanel, YieldHistory } from '../components/field/Results'
import { FieldMap, type Basemap, type CellOverlay } from '../components/map/FieldMap'
import { Badge, SimulatedBadge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Container } from '../components/ui/Section'
import { ErrorNote } from '../components/ui/States'
import { Tabs } from '../components/ui/Tabs'
import { ndviColor, relYieldColor } from '../lib/color'
import { N_DEKADS, dekadLabel } from '../lib/dekads'
import { fmtArea } from '../lib/format'
import { areaM2, cellSquare } from '../lib/geo'
import { useResource } from '../lib/useResource'
import { getEvidence } from '../services/evidenceService'
import { getPreparedFields, runAnalysis } from '../services/fieldService'
import { PlaceSearch } from '../components/map/PlaceSearch'
import { analysisReducer, initialAnalysis, isRunning } from '../state/analysisMachine'

const MIN_AREA = 3000 // m²
const MAX_AREA = 2_000_000 // m² (200 ha)

type Layer = 'none' | 'season' | 'weak' | 'yield'

/** Neutral description of a prepared field-year: where, how big, how much satellite data – nothing about the outcome. */
function teaser(f: FieldAnalysis): string {
  const nd = f.satellite.indices.ndvi ?? []
  const summer = nd.slice(6, 15).filter((v) => v != null).length
  const years = f.history?.length ?? 0
  return [
    f.place,
    fmtArea(f.area_m2),
    `${f.satellite.n_observed_dekads} von 21 Dekaden beobachtet (Juni–August: ${summer} von 9)`,
    years > 1 ? `Erträge aus ${years} Jahren` : null,
  ]
    .filter(Boolean)
    .join(' · ')
}

export default function Analyse() {
  const fields = useResource(getPreparedFields, 'fields')
  const evidence = useResource(getEvidence, 'evidence')
  const [state, dispatch] = useReducer(analysisReducer, initialAnalysis)
  const [basemap, setBasemap] = useState<Basemap>('satellite')
  const [drawing, setDrawing] = useState(false)
  const [layer, setLayer] = useState<Layer>('weak')
  const [dekad, setDekad] = useState(12)
  const [flyTo, setFlyTo] = useState<{ center: [number, number]; zoom?: number; bbox?: [number, number, number, number]; key: number } | null>(null)
  const resultsRef = useRef<HTMLDivElement>(null)

  const prepared = useMemo(() => fields.data?.fields ?? [], [fields.data])
  const mapFields = useMemo(() => prepared.map((f) => ({ id: f.id, label: f.label, geometry: f.geometry, role: f.role })), [prepared])
  const selectedPrepared = state.selection?.kind === 'prepared' ? prepared.find((f) => f.id === (state.selection as { id: string }).id) : undefined
  const result = state.result

  // Run the pipeline when a new run starts.
  useEffect(() => {
    if (state.status !== 'loadingSatellite' || !state.selection) return
    const ctrl = new AbortController()
    runAnalysis(
      state.selection,
      { onStage: (stage) => dispatch({ type: 'stage', stage }), onStageDone: (stage, facts) => dispatch({ type: 'stageDone', stage, facts }) },
      ctrl.signal,
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
    dispatch({ type: 'select', selection: { kind: 'prepared', id: f.id, polygon: f.geometry, areaM2: f.area_m2, label: `${f.label} · ${f.site} ${f.year}` } })
  }

  const onPolygon = (p: Polygon | null) => {
    setDrawing(false)
    if (!p) return dispatch({ type: 'clear' })
    dispatch({ type: 'select', selection: { kind: 'custom', polygon: p, areaM2: areaM2(p), label: 'Ihr Feld' } })
  }

  // Cell grid: shown only with the result, so the coloured zones do not give the answer away before the run.
  const pixels = state.status === 'completed' ? result?.pixels : null
  const pixelYear = result?.year ?? selectedPrepared?.year ?? 2020
  const pixelsSimulated = state.status === 'completed' ? Boolean(result?.simulated) : false

  // Cell overlay on the map.
  const overlay = useMemo<CellOverlay | null>(() => {
    const px = pixels
    if (!px || layer === 'none') return null
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
  }, [pixels, layer, dekad])

  const sel = state.selection
  const areaWarning = sel?.kind === 'custom' ? (sel.areaM2 < MIN_AREA ? 'Zu klein – zeichnen Sie mindestens 0,3 ha.' : sel.areaM2 > MAX_AREA ? 'Zu groß – zeichnen Sie ein einzelnes Feld (max. 200 ha).' : null) : null
  const running = isRunning(state.status)

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
                label="Grundkarte"
                value={basemap}
                onChange={setBasemap}
                className="panel-glass !rounded-[12px] !border-white/10"
                items={[
                  { value: 'satellite', label: 'Satellit' },
                  { value: 'sentinel', label: 'Sentinel-2' },
                  { value: 'terrain', label: 'Gelände' },
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
                {drawing ? 'Abbrechen' : 'Feld zeichnen'}
              </Button>
            </div>
            <AnimatePresence>
              {drawing && (
                <motion.p initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="panel-glass px-3 py-2 text-[12.5px] text-ink-2">
                  Klicken Sie, um Ecken zu setzen. Klicken Sie zum Schließen auf die erste Ecke. Danach können Sie Ecken verschieben.
                </motion.p>
              )}
              {pixels && (
                <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="panel-glass pointer-events-auto flex flex-col gap-2 p-2.5">
                  <div className="flex items-center gap-2">
                    <LayersIcon className="ml-1 size-3.5 text-ink-3" />
                    <Tabs
                      size="sm"
                      label="Kartenebene"
                      value={layer}
                      onChange={setLayer}
                      items={[
                        { value: 'weak', label: 'Schwache Zonen' },
                        { value: 'season', label: 'NDVI-Saison' },
                        { value: 'yield', label: pixelsSimulated ? 'Ertrag (sim.)' : 'Gemessener Ertrag' },
                        { value: 'none', label: 'Aus' },
                      ]}
                    />
                  </div>
                  {layer === 'season' && (
                    <div className="flex items-center gap-3 px-1">
                      <input type="range" min={0} max={N_DEKADS - 1} value={dekad} onChange={(e) => setDekad(Number(e.target.value))} aria-label="Dekade" className="h-1 w-48 cursor-pointer appearance-none rounded-full bg-white/15 accent-[var(--color-maize)]" />
                      <span className="w-14 font-mono text-[11px] text-ink-2">{dekadLabel(dekad, pixelYear)}</span>
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
            <ModeSwitch active="analyse" />
            <AnimatePresence mode="wait">
              {state.status === 'idle' && (
                <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <p className="eyebrow">Feld analysieren</p>
                  <h1 className="mt-3 text-[30px] leading-tight">Wählen Sie ein Feld-Jahr oder zeichnen Sie Ihr eigenes Feld.</h1>
                  <p className="mt-3 text-[14px] leading-relaxed text-ink-2">
                    Vorbereitete Felder sind echte, beim Training zurückgehaltene Feld-Jahre von den US-Trainingsstandorten, mit gemessenem
                    Ertrag. Was das Modell sagt und ob es stimmt, sehen Sie erst nach der Analyse. Für gezeichnete Felder läuft eine Simulation, bis das Backend für die Datenabfrage verbunden ist.
                  </p>
                  {fields.error && <div className="mt-6"><ErrorNote error={fields.error} /></div>}
                  <ul className="mt-6 flex flex-col gap-2">
                    {prepared.map((f) => (
                      <li key={f.id}>
                        <button
                          type="button"
                          onClick={() => selectPrepared(f)}
                          className="group flex w-full items-start gap-4 rounded-xl border border-[var(--line)] bg-white/[0.02] p-4 text-left transition hover:border-[var(--line-strong)] hover:bg-white/[0.045]"
                        >
                          <span className="mt-0.5 font-display text-[15px] font-semibold text-maize">{f.label.replace(/^(Field|Feld) /, '')}</span>
                          <span className="min-w-0 flex-1">
                            <span className="flex flex-wrap items-center gap-2">
                              <span className="text-[14.5px] font-medium text-ink">{f.site} {f.year}</span>
                              {f.treatment && <Badge tone="neutral">Variante {f.treatment}</Badge>}
                            </span>
                            <span className="mt-1 block text-[13px] leading-snug text-ink-3">{teaser(f)}</span>
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
                      <p className="eyebrow">{sel.kind === 'prepared' ? `${selectedPrepared?.site} · ${selectedPrepared?.year}` : 'Gezeichnetes Feld'}</p>
                      <h2 className="mt-2 text-[24px] leading-tight">{sel.label}</h2>
                      <p className="mt-1 font-mono text-[12.5px] text-ink-3">
                        {fmtArea(sel.areaM2)}
                        {sel.kind === 'prepared' && selectedPrepared?.treatment ? ` · Variante ${selectedPrepared.treatment}` : ''}
                      </p>
                    </div>
                    <button type="button" aria-label="Auswahl aufheben" onClick={() => dispatch({ type: 'clear' })} className="rounded-lg p-1.5 text-ink-3 hover:bg-white/5 hover:text-ink">
                      <X className="size-4" />
                    </button>
                  </div>
                  {sel.kind === 'custom' && <SimulatedBadge />}
                  {state.status === 'fieldSelected' && (
                    <>
                      {selectedPrepared && <p className="text-[14px] leading-relaxed text-ink-2">{teaser(selectedPrepared)}</p>}
                      {areaWarning && <p className="text-[13px] text-rust">{areaWarning}</p>}
                      <Button size="lg" icon={<Play className="size-4" />} disabled={Boolean(areaWarning)} onClick={() => dispatch({ type: 'start' })}>
                        Feld analysieren
                      </Button>
                    </>
                  )}
                  {(running || state.status === 'completed' || state.status === 'error') && <PipelinePanel state={state} />}
                  {state.status === 'error' && (
                    <div className="rounded-xl border border-rust/30 bg-rust/5 p-4 text-[13.5px] text-ink-2">
                      <p className="font-medium text-rust">Die Analyse wurde abgebrochen.</p>
                      <p className="mt-1">{state.error}</p>
                      <Button className="mt-3" size="sm" variant="secondary" icon={<RotateCcw className="size-3.5" />} onClick={() => dispatch({ type: 'start' })}>
                        Erneut starten
                      </Button>
                    </div>
                  )}
                  {state.status === 'completed' && (
                    <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col gap-2">
                      <Button size="lg" icon={<ArrowDown className="size-4" />} onClick={() => resultsRef.current?.scrollIntoView({ behavior: 'smooth' })}>
                        Ganzes Ergebnis
                      </Button>
                      <Button variant="ghost" size="sm" icon={<RotateCcw className="size-3.5" />} onClick={() => dispatch({ type: 'clear' })}>
                        Anderes Feld wählen
                      </Button>
                    </motion.div>
                  )}
                  {running && (
                    <p className="flex items-center gap-2 text-[12px] text-ink-4">
                      <Loader2 className="size-3.5 animate-spin" />
                      {sel.kind === 'prepared' ? 'Gespeicherte Projektergebnisse für dieses Feld-Jahr werden abgespielt.' : 'Simulation – kein Backend verbunden.'}
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
                <p className="eyebrow">Ergebnis · {result.label}</p>
                {/* The outcome headline (title/blurb) appears only once the measured yield is revealed (Assessment). */}
                <h2 className="mt-3 text-[clamp(2rem,4vw,3rem)]">{result.simulated ? result.title : `${result.site} ${result.year}`}</h2>
                {result.place && <p className="mt-2 text-[15px] text-ink-2">{result.place}</p>}
                <p className="mt-2 font-mono text-[12.5px] text-ink-3">
                  {result.site} · {result.field_id.replace(/_/g, '-')} · {result.year} · {fmtArea(result.area_m2)}
                </p>
              </div>
              {result.simulated && <SimulatedBadge />}
            </div>
            <Assessment f={result} />
            <PhaseContributions f={result} typical={evidence.data?.alarm.phase_sum_mean} />
            <SatellitePanel f={result} />
            <YieldHistory f={result} />
            <WithinFieldPanel f={result} />
            <WeatherPanel f={result} />
            <SoilPanel f={result} />
            <p className="mt-4 text-[12.5px] leading-relaxed text-ink-4">
              {result.simulated
                ? 'Simuliertes Ergebnis: Echt sind nur die gesunde Referenzkurve und die Formel des Stress-Scores. Um gezeichnete Felder mit Sentinel-2, ERA5-Land und SoilGrids zu analysieren, muss das Backend für die Datenabfrage verbunden sein.'
                : 'Alle Werte für dieses Feld-Jahr stammen aus web/public/data/fields.json, erzeugt von web/scripts/export_web_data.py aus den Daten und Ergebnissen des Projekts. Die Risikowahrscheinlichkeit ist out-of-fold: Dieses Feld-Jahr wurde nicht zum Anpassen des Modells verwendet, das es bewertet hat.'}
            </p>
          </Container>
        )}
      </div>
    </>
  )
}
