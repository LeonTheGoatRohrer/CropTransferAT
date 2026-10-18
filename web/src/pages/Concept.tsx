import { scaleBand, scaleLinear } from 'd3-scale'
import { Bell, Check, Loader2, PenLine, Play, Plus, Save, Trash2, X } from 'lucide-react'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import type { FieldAnalysis, Polygon } from '../api/types'
import { axisText, useWidth } from '../components/charts/core'
import { AlertCard, SatellitePanel, WeatherPanel } from '../components/field/Results'
import { FieldMap } from '../components/map/FieldMap'
import { Badge, ConceptBadge, LiveBadge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Reveal } from '../components/ui/Reveal'
import { Container, SectionHeader, Source } from '../components/ui/Section'
import { tokens } from '../lib/color'
import { fmt, fmtArea, fmtCutoff, fmtDate } from '../lib/format'
import type { Unit } from '../lib/baseline'
import { areaM2 } from '../lib/geo'
import { useResource } from '../lib/useResource'
import { api, backendAvailable, type AlertSetting, type Baseline, type Calibration, type FieldDetail, type FieldRecord, type Notification } from '../services/backendService'
import { getEvidence, getExplorer } from '../services/evidenceService'
import { getPreparedFields, runAnalysis } from '../services/fieldService'
import { getFieldStore, type FieldStore } from '../services/fieldStore'

const CUTOFFS = ['06-01', '06-15', '07-01', '07-15', '08-01', '08-15', '09-01']
const X_OPTIONS = [10, 15, 20, 25, 30]
const THIS_YEAR = new Date().getFullYear()
const LAST_SEASON = new Date().getMonth() >= 9 ? THIS_YEAR : THIS_YEAR - 1
/** Example field for the tool: a real KBS trial plot whose yields were measured over many seasons. */
const DEMO_FIELD = 'kbs-2017'
/** Earliest season the tool (and the backend) accepts. */
const FIRST_YEAR = 1990

export default function Concept() {
  const { t } = useTranslation()
  const ev = useResource(getEvidence, 'evidence')
  const [live, setLive] = useState<boolean | null>(null)
  useEffect(() => {
    backendAvailable(true).then(setLive)
  }, [])
  const cal = ev.data?.alert_calibration
  return (
    <>
      <section className="pt-36 pb-10">
        <Container>
          <Reveal>
            <div className="mb-5 flex flex-wrap items-center gap-3">
              <ConceptBadge label={t('concept.badge')} />
              <p className="eyebrow">{t('concept.eyebrow')}</p>
            </div>
            <h1 className="max-w-[920px] text-balance text-[clamp(2.3rem,5vw,4.2rem)] leading-[1.02] tracking-[-0.04em] [hyphens:auto]">{t('concept.title')}</h1>
            <p className="mt-6 max-w-[700px] text-[17px] leading-relaxed text-ink-2">{t('concept.lede')}</p>
            <div className="mt-6 flex flex-wrap items-center gap-3 text-[13px]">
              {live === null ? null : live ? (
                <LiveBadge />
              ) : (
                <>
                  <Badge>{t('concept.backendOff')}</Badge>
                  <span className="font-mono text-[11.5px] text-ink-4">{t('concept.backendHow')}</span>
                </>
              )}
            </div>
          </Reveal>
        </Container>
      </section>

      <section className="py-10">
        <Container>
          <SectionHeader eyebrow={t('concept.eyebrow')} title={t('concept.pathsTitle')} />
          <div className="mt-10 grid gap-5 md:grid-cols-2">
            {[
              [t('concept.a'), t('concept.aBody')],
              [t('concept.b'), t('concept.bBody')],
            ].map(([h, b], i) => (
              <Reveal key={h} delay={i * 0.06} className="panel p-7">
                <p className="font-display text-[20px] font-semibold">{h}</p>
                <p className="mt-3 text-[14.5px] leading-relaxed text-ink-2">{b}</p>
              </Reveal>
            ))}
          </div>
        </Container>
      </section>

      {cal && <CalibrationSection cal={cal} />}

      <Tool cal={cal} />
    </>
  )
}

/* ------------------------------------------------------------------ */

function hitText(t: (k: string, o?: Record<string, unknown>) => string, cal: Calibration | undefined, cutoff: string, x: number) {
  const row = cal?.table.find((r) => r.cutoff === cutoff && r.x_pct === x)
  if (!row || row.statement !== 'ok') return { ok: false, text: t('concept.none') }
  return { ok: true, text: t('concept.inKofN', { k: row.k_hit, n: row.n_alert }) }
}

function CalibrationSection({ cal }: { cal: Calibration }) {
  const { t } = useTranslation()
  const facts = t('concept.alertFacts', { returnObjects: true }) as string[]
  const cuts = ['07-15', '08-01', '08-15', '09-01']
  return (
    <section className="py-16">
      <Container>
        <SectionHeader eyebrow={t('concept.eyebrow')} title={t('concept.alertTitle')} lede={t('concept.alertLede')} />
        <div className="mt-10 grid gap-5 lg:grid-cols-[1.3fr_1fr]">
          <Reveal className="panel overflow-x-auto p-6">
            <table className="w-full min-w-[520px] text-left text-[13.5px]">
              <thead>
                <tr className="text-ink-3">
                  <th className="pb-3 font-mono text-[10.5px] font-normal uppercase tracking-[0.12em]">{t('concept.alertTable.cutoff')}</th>
                  {X_OPTIONS.map((x) => (
                    <th key={x} className="pb-3 text-right font-mono text-[10.5px] font-normal uppercase tracking-[0.12em]">{x} %</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {['06-01', '06-15', '07-01', ...cuts].map((c) => (
                  <tr key={c} className="border-t border-[var(--line)]">
                    <td className="py-3 text-ink">{fmtCutoff(c)}</td>
                    {X_OPTIONS.map((x) => {
                      const r = cal.table.find((row) => row.cutoff === c && row.x_pct === x)
                      const ok = r?.statement === 'ok'
                      return (
                        <td key={x} className={`py-3 text-right font-mono tabular ${ok ? 'text-ink' : 'text-ink-4'}`} title={ok ? '' : r?.reasons.join('; ')}>
                          {ok ? `${r!.k_hit}/${r!.n_alert}` : '–'}
                        </td>
                      )
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="mt-4 text-[12.5px] text-ink-3">
              {t('concept.alertTable.hits')}: k/n · – = {t('concept.none')} · {cal.n_field_years} {t('common.fieldYears')}, {cal.n_site_years} {t('common.siteYears')}
            </p>
            <Source className="mt-3">{t('concept.alertSrc')}</Source>
          </Reveal>
          <Reveal className="panel p-6" delay={0.06}>
            <ul className="flex flex-col gap-4">
              {facts.map((f) => (
                <li key={f} className="flex gap-3 text-[14px] leading-relaxed text-ink-2">
                  <span className="mt-2 size-1.5 shrink-0 rounded-full bg-maize" />
                  {f}
                </li>
              ))}
            </ul>
          </Reveal>
        </div>
      </Container>
    </section>
  )
}

/* ------------------------------------------------------------------ */

function YieldChart({ b }: { b: Baseline }) {
  const { t } = useTranslation()
  const [ref, width] = useWidth<HTMLDivElement>()
  const h = 200
  const m = { t: 10, r: 10, b: 26, l: 36 }
  const vmax = Math.max(1, ...b.per_year.map((p) => p.t_ha), b.normal_t_ha ?? 0) * 1.15
  const x = scaleBand<number>().domain(b.per_year.map((p) => p.year)).range([m.l, width - m.r]).padding(0.3)
  const y = scaleLinear().domain([0, vmax]).range([h - m.b, m.t])
  const line = (v: number | undefined | null, color: string, dash?: string) =>
    v == null ? null : <line x1={m.l} x2={width - m.r} y1={y(v)} y2={y(v)} stroke={color} strokeDasharray={dash} strokeWidth={1.4} />
  return (
    <div ref={ref}>
      <svg width={width} height={h} role="img" aria-label={t('concept.chartAria')}>
        {y.ticks(4).map((tk) => (
          <g key={tk}>
            <line x1={m.l} x2={width - m.r} y1={y(tk)} y2={y(tk)} stroke={tokens.line} strokeDasharray="2 4" />
            <text x={m.l - 6} y={y(tk)} dy="0.32em" textAnchor="end" {...axisText}>{fmt(tk, 0)}</text>
          </g>
        ))}
        {b.per_year.map((p) => (
          <g key={p.year}>
            <rect x={x(p.year)} y={y(p.t_ha)} width={x.bandwidth()} height={h - m.b - y(p.t_ha)} rx={2} fill={p.year === b.year ? tokens.maize : tokens.sage} opacity={p.year === b.year ? 1 : 0.55} />
            <text x={(x(p.year) ?? 0) + x.bandwidth() / 2} y={h - 8} textAnchor="middle" {...axisText}>{String(p.year).slice(2)}</text>
          </g>
        ))}
        {line(b.normal_t_ha, tokens.ink)}
        {line(b.hint_below_t_ha, tokens.maize, '4 4')}
        {line(b.warning_below_t_ha, tokens.rust, '4 4')}
      </svg>
    </div>
  )
}

type Row = { year: number | ''; value: number | '' }

function Tool({ cal }: { cal: Calibration | undefined }) {
  const { t } = useTranslation()
  const [store, setStore] = useState<FieldStore | null>(null)
  const [fields, setFields] = useState<FieldRecord[]>([])
  const [sel, setSel] = useState<string | null>(null)
  const [detail, setDetail] = useState<FieldDetail | null>(null)
  const [drawing, setDrawing] = useState(false)
  const [draft, setDraft] = useState<Polygon | null>(null)
  const [name, setName] = useState('')
  const [unit, setUnit] = useState<Unit>('t/ha')
  const [rows, setRows] = useState<Row[]>([])
  const [targetYear, setTargetYear] = useState(LAST_SEASON)
  const [alert, setAlert] = useState<AlertSetting>({ cutoff: '09-01', hint_pct: 20, warn_pct: 30 })
  const [msg, setMsg] = useState<{ kind: 'ok' | 'err'; text: string } | null>(null)
  const [notes, setNotes] = useState<Notification[]>([])
  const [runState, setRunState] = useState<{ stage: string | null; result: FieldAnalysis | null; error: string | null; busy: boolean }>({ stage: null, result: null, error: null, busy: false })

  const refresh = useCallback(async (s: FieldStore) => {
    setFields(await s.list())
    if (s.mode === 'backend') setNotes(await api.notifications().catch(() => []))
  }, [])

  useEffect(() => {
    getFieldStore().then((s) => {
      setStore(s)
      refresh(s)
    })
  }, [refresh])

  const load = useCallback(
    async (id: string, year = targetYear) => {
      if (!store) return
      const d = await store.get(id, year)
      setDetail(d)
      setUnit((d.yields[0]?.unit as Unit) ?? 't/ha')
      setRows(d.yields.map((y) => ({ year: y.year, value: y.value })))
      if (d.alert) setAlert({ cutoff: d.alert.cutoff, hint_pct: d.alert.hint_pct, warn_pct: d.alert.warn_pct })
    },
    [store, targetYear],
  )

  useEffect(() => {
    if (sel) load(sel)
  }, [sel, load])

  const flash = (kind: 'ok' | 'err', text: string) => {
    setMsg({ kind, text })
    setTimeout(() => setMsg(null), 3500)
  }

  const loadDemo = async () => {
    if (!store) return
    try {
      const [prepared, explorer] = await Promise.all([getPreparedFields(), getExplorer()])
      const f = prepared.fields.find((x) => x.id === DEMO_FIELD)
      if (!f || f.geometry.type !== 'Polygon') throw new Error(DEMO_FIELD)
      const plot = f.fy_key.split('|')[1]
      const ys = explorer.rows.filter((r) => r.fy_key.split('|')[1] === plot && r.Y_t_ha != null && r.year >= FIRST_YEAR).map((r) => ({ year: r.year, value: r.Y_t_ha as number }))
      const rec = await store.create(t('concept.demoLabel', { id: f.field_id }), f.geometry)
      await store.setYields(rec.id, 't/ha', ys)
      const last = Math.max(...ys.map((y) => y.year))
      setTargetYear(last)
      await refresh(store)
      setSel(rec.id)
      flash('ok', t('concept.demoLoaded', { n: ys.length }))
    } catch (e) {
      flash('err', t('concept.error', { msg: (e as Error).message }))
    }
  }

  const createField = async () => {
    if (!store || !draft || !name.trim()) return
    try {
      const f = await store.create(name.trim(), draft)
      setDraft(null)
      setName('')
      await refresh(store)
      setSel(f.id)
      flash('ok', t('concept.saved'))
    } catch (e) {
      flash('err', t('concept.error', { msg: (e as Error).message }))
    }
  }

  const saveYields = async () => {
    if (!store || !sel) return
    try {
      const entries = rows.filter((r) => r.year !== '' && r.value !== '').map((r) => ({ year: Number(r.year), value: Number(r.value) }))
      await store.setYields(sel, unit, entries)
      await load(sel)
      flash('ok', t('concept.saved'))
    } catch (e) {
      flash('err', t('concept.error', { msg: (e as Error).message }))
    }
  }

  const saveAlert = async () => {
    if (!store || !sel) return
    if (alert.warn_pct <= alert.hint_pct) return flash('err', t('concept.warnGtHint'))
    try {
      await store.setAlert(sel, alert)
      await load(sel)
      flash('ok', t('concept.saved'))
    } catch (e) {
      flash('err', t('concept.error', { msg: (e as Error).message }))
    }
  }

  const runB = async () => {
    if (!detail || store?.mode !== 'backend') return
    setRunState({ stage: null, result: null, error: null, busy: true })
    try {
      const ctrl = new AbortController()
      const res = await runAnalysis(
        { kind: 'custom', polygon: detail.geometry, areaM2: detail.area_m2, label: detail.label, fieldId: detail.id },
        { onStage: (s) => setRunState((r) => ({ ...r, stage: s })), onStageDone: () => undefined },
        ctrl.signal,
        { year: targetYear, cutoff: alert.cutoff },
      )
      setRunState({ stage: null, result: res, error: null, busy: false })
      refresh(store)
    } catch (e) {
      setRunState({ stage: null, result: null, error: (e as Error).message, busy: false })
    }
  }

  const mapFields = useMemo(() => fields.map((f) => ({ id: f.id, label: f.label, geometry: f.geometry, role: 'custom' })), [fields])
  const b = detail?.baseline
  const hint = hitText(t, cal, alert.cutoff, alert.hint_pct)
  const warn = hitText(t, cal, alert.cutoff, alert.warn_pct)
  const years = Array.from({ length: THIS_YEAR - FIRST_YEAR + 1 }, (_, i) => THIS_YEAR - i)
  const input = 'h-9 rounded-[10px] border border-[var(--line-strong)] bg-soil-850 px-3 text-[13.5px] text-ink focus:border-maize focus:outline-none'

  return (
    <section id="tool" className="scroll-mt-20 py-16">
      <Container>
        <SectionHeader
          eyebrow={t('concept.badge')}
          title={t('concept.toolTitle')}
          lede={
            <>
              {t('concept.toolLede')}{' '}
              {store?.mode === 'local' && <span className="text-maize">{t('concept.localOnly')}</span>}
            </>
          }
        />
        <div className="mt-10 grid gap-5 lg:grid-cols-[1.1fr_1fr]">
          <Reveal className="panel relative h-[520px] overflow-hidden p-0">
            <FieldMap
              fields={mapFields}
              selectedId={sel}
              selectedGeometry={fields.find((f) => f.id === sel)?.geometry ?? null}
              overlay={null}
              basemap="satellite"
              drawing={drawing}
              onSelectField={(id) => setSel(id)}
              onPolygon={(p) => {
                setDrawing(false)
                setDraft(p)
              }}
              flyTo={null}
            />
            <div className="pointer-events-none absolute bottom-10 left-3 flex flex-col items-start gap-2">
              <Button size="sm" variant={drawing ? 'primary' : 'secondary'} className={drawing ? 'pointer-events-auto' : 'panel-glass pointer-events-auto !border-white/10'} icon={drawing ? <X className="size-3.5" /> : <PenLine className="size-3.5" />} onClick={() => setDrawing((d) => !d)}>
                {drawing ? t('analyse.cancelDraw') : t('analyse.draw')}
              </Button>
              {drawing && <p className="panel-glass pointer-events-auto px-3 py-2 text-[12px] text-ink-2">{t('analyse.drawHelp')}</p>}
            </div>
          </Reveal>

          <Reveal className="panel flex flex-col gap-6 p-6" delay={0.05}>
            <div>
              <p className="eyebrow mb-3">{t('concept.myFields')}</p>
              {fields.length === 0 && !draft && <p className="text-[13.5px] text-ink-3">{t('concept.noFields')}</p>}
              {!fields.some((f) => f.label === t('concept.demoLabel', { id: 'T2R3' })) && !draft && (
                <Button size="sm" variant="secondary" className="mb-3 mt-3" icon={<Plus className="size-3.5" />} onClick={loadDemo}>
                  {t('concept.loadDemo')}
                </Button>
              )}
              <ul className="flex flex-col gap-1.5">
                {fields.map((f) => (
                  <li key={f.id}>
                    <button type="button" onClick={() => setSel(f.id)} className={`flex w-full items-center justify-between rounded-lg border px-3 py-2 text-left text-[13.5px] transition ${sel === f.id ? 'border-maize bg-maize/5 text-ink' : 'border-[var(--line)] text-ink-2 hover:border-[var(--line-strong)]'}`}>
                      <span>{f.label}</span>
                      <span className="font-mono text-[11px] text-ink-4">{fmtArea(f.area_m2)} · {f.n_yields ?? 0} {t('common.years')}</span>
                    </button>
                  </li>
                ))}
              </ul>
              {draft && (
                <div className="mt-3 flex flex-wrap items-end gap-2 rounded-xl border border-dashed border-maize/40 p-3">
                  <label className="flex flex-1 flex-col gap-1 text-[12px] text-ink-3">
                    {t('concept.fieldName')} · {fmtArea(areaM2(draft))}
                    <input value={name} maxLength={40} onChange={(e) => setName(e.target.value)} placeholder={t('concept.fieldNamePh')} className={input} />
                  </label>
                  <Button size="sm" icon={<Save className="size-3.5" />} disabled={!name.trim()} onClick={createField}>{t('concept.save')}</Button>
                  <p className="w-full text-[11.5px] text-ink-4">{t('concept.onlyMaize')}</p>
                </div>
              )}
            </div>

            {!detail && fields.length > 0 && !draft && <p className="text-[13.5px] text-ink-3">{t('concept.selectField')}</p>}
            {detail && (
              <>
                <div className="border-t border-[var(--line)] pt-5">
                  <div className="flex items-center justify-between gap-3">
                    <p className="eyebrow">{t('concept.yields')} · {detail.label}</p>
                    <label className="flex items-center gap-2 text-[12px] text-ink-3">
                      {t('concept.unit')}
                      <select value={unit} onChange={(e) => setUnit(e.target.value as Unit)} className={input}>
                        <option value="t/ha">t/ha</option>
                        <option value="dt/ha">dt/ha</option>
                      </select>
                    </label>
                  </div>
                  <div className="mt-3 flex flex-col gap-1.5">
                    {rows.map((r, i) => (
                      <div key={i} className="grid grid-cols-[1fr_1fr_auto] gap-2">
                        <select aria-label={t('concept.year')} value={r.year} onChange={(e) => setRows(rows.map((x, j) => (j === i ? { ...x, year: e.target.value === '' ? '' : Number(e.target.value) } : x)))} className={input}>
                          <option value="">{t('concept.year')}</option>
                          {years.map((y) => <option key={y} value={y}>{y}</option>)}
                        </select>
                        <input aria-label={t('concept.value')} type="number" step="0.1" min="0" placeholder={`${t('concept.value')} (${unit})`} value={r.value} onChange={(e) => setRows(rows.map((x, j) => (j === i ? { ...x, value: e.target.value === '' ? '' : Number(e.target.value) } : x)))} className={input} />
                        <button type="button" aria-label={t('concept.remove')} onClick={() => setRows(rows.filter((_, j) => j !== i))} className="rounded-lg px-2 text-ink-4 hover:text-rust"><Trash2 className="size-4" /></button>
                      </div>
                    ))}
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Button size="sm" variant="secondary" icon={<Plus className="size-3.5" />} onClick={() => setRows([...rows, { year: '', value: '' }])}>{t('concept.addYear')}</Button>
                    <Button size="sm" icon={<Save className="size-3.5" />} onClick={saveYields}>{t('concept.saveYields')}</Button>
                  </div>
                  <p className="mt-2 text-[11.5px] text-ink-4">{t('concept.moistureNote')}</p>
                </div>

                {b && (
                  <div className="border-t border-[var(--line)] pt-5">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <p className="eyebrow">{t('concept.baseline')}</p>
                      <label className="flex items-center gap-2 text-[12px] text-ink-3">
                        {t('concept.targetYear')}
                        <select value={targetYear} onChange={(e) => { setTargetYear(Number(e.target.value)); if (sel) load(sel, Number(e.target.value)) }} className={input}>
                          {years.slice(0, 15).map((y) => <option key={y} value={y}>{y}</option>)}
                        </select>
                      </label>
                    </div>
                    <p className={`mt-3 rounded-lg px-3 py-2 text-[13px] ${b.history === 'too_little' ? 'bg-rust/10 text-rust' : b.history === 'with_hint' ? 'bg-maize/10 text-maize' : 'bg-sage/10 text-sage'}`}>{t(`concept.history.${b.history}`)}</p>
                    {b.per_year.length > 0 && <div className="mt-3"><YieldChart b={b} /></div>}
                    <dl className="mt-3 grid grid-cols-2 gap-3 text-[13px]">
                      <div><dt className="eyebrow">{t('concept.normal')}</dt><dd className="mt-1 font-mono tabular text-ink">{b.normal_t_ha == null ? t('concept.normalNone') : `${fmt(b.normal_t_ha, 2)} t/ha`}</dd></div>
                      <div><dt className="eyebrow">{t('concept.thisYear')}</dt><dd className="mt-1 font-mono tabular text-ink">{b.yield_t_ha == null ? '–' : `${fmt(b.yield_t_ha, 2)} t/ha`}</dd></div>
                      <div><dt className="eyebrow">{t('concept.ry')}</dt><dd className="mt-1 font-mono tabular text-ink">{fmt(b.ry, 2)}</dd></div>
                      <div><dt className="eyebrow">{t('concept.hintBelow')} · {t('concept.warnBelow')}</dt><dd className="mt-1 font-mono tabular text-ink">{b.hint_below_t_ha == null ? '–' : `${fmt(b.hint_below_t_ha, 1)} · ${fmt(b.warning_below_t_ha, 1)} t/ha`}</dd></div>
                    </dl>
                    <p className="mt-3 text-[14px] font-medium text-ink">
                      {b.state === 'hint' || b.state === 'warning' ? t(`concept.states.${b.state}`, { x: b.state === 'hint' ? alert.hint_pct : alert.warn_pct }) : t(`concept.states.${b.state === 'ok' ? 'normal' : b.state}`)}
                    </p>
                  </div>
                )}

                <div className="border-t border-[var(--line)] pt-5">
                  <p className="eyebrow mb-3">{t('concept.alerts')}</p>
                  <div className="grid grid-cols-3 gap-2">
                    <label className="flex flex-col gap-1 text-[12px] text-ink-3">
                      {t('concept.cutoff')}
                      <select value={alert.cutoff} onChange={(e) => setAlert({ ...alert, cutoff: e.target.value })} className={input}>
                        {CUTOFFS.map((c) => <option key={c} value={c}>{fmtCutoff(c)}</option>)}
                      </select>
                    </label>
                    <label className="flex flex-col gap-1 text-[12px] text-ink-3">
                      {t('concept.hintPct')}
                      <select value={alert.hint_pct} onChange={(e) => setAlert({ ...alert, hint_pct: Number(e.target.value) })} className={input}>
                        {X_OPTIONS.map((x) => <option key={x} value={x}>{x} {t('concept.pctUnder')}</option>)}
                      </select>
                    </label>
                    <label className="flex flex-col gap-1 text-[12px] text-ink-3">
                      {t('concept.warnPct')}
                      <select value={alert.warn_pct} onChange={(e) => setAlert({ ...alert, warn_pct: Number(e.target.value) })} className={input}>
                        {X_OPTIONS.map((x) => <option key={x} value={x}>{x} {t('concept.pctUnder')}</option>)}
                      </select>
                    </label>
                  </div>
                  <ul className="mt-3 flex flex-col gap-1.5 text-[13px]">
                    <li className="flex items-center gap-2"><span className="size-2.5 rounded-full bg-maize" /><span className="text-ink-2">{t('results.alertHint')}:</span> <span className={hint.ok ? 'text-ink' : 'text-ink-4'}>{hint.text}</span></li>
                    <li className="flex items-center gap-2"><span className="size-2.5 rounded-full bg-rust" /><span className="text-ink-2">{t('results.alertWarning')}:</span> <span className={warn.ok ? 'text-ink' : 'text-ink-4'}>{warn.text}</span></li>
                  </ul>
                  <p className="mt-2 text-[11.5px] text-ink-4">{t('concept.proposal')}</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Button size="sm" variant="secondary" icon={<Save className="size-3.5" />} onClick={saveAlert}>{t('concept.saveAlert')}</Button>
                    <Button size="sm" icon={runState.busy ? <Loader2 className="size-3.5 animate-spin" /> : <Play className="size-3.5" />} disabled={store?.mode !== 'backend' || runState.busy} onClick={runB}>
                      {t('concept.runB')} · {targetYear}
                    </Button>
                  </div>
                  {store?.mode !== 'backend' && <p className="mt-2 text-[11.5px] text-ink-4">{t('concept.runBNeeds')}</p>}
                  {runState.busy && runState.stage && <p className="mt-2 text-[12px] text-ink-3">{t(`pipeline.${runState.stage}.running`)}</p>}
                  {runState.error && <p className="mt-2 text-[12.5px] text-rust">{t('concept.error', { msg: runState.error })}</p>}
                </div>
                <Button size="sm" variant="ghost" icon={<Trash2 className="size-3.5" />} onClick={async () => { if (store && sel) { await store.remove(sel); setSel(null); setDetail(null); refresh(store) } }}>{t('concept.delete')}</Button>
              </>
            )}
            {msg && <p className={`flex items-center gap-2 text-[13px] ${msg.kind === 'ok' ? 'text-sage' : 'text-rust'}`}>{msg.kind === 'ok' && <Check className="size-3.5" />}{msg.text}</p>}
          </Reveal>
        </div>

        {store?.mode === 'backend' && (
          <Reveal className="mt-5 panel p-6">
            <p className="eyebrow mb-3 flex items-center gap-2"><Bell className="size-3.5" /> {t('concept.notifications')}</p>
            {notes.length === 0 ? (
              <p className="text-[13.5px] text-ink-3">{t('concept.noNotifications')}</p>
            ) : (
              <ul className="flex flex-col gap-2">
                {notes.map((n) => (
                  <li key={n.id} className={`flex flex-wrap items-center justify-between gap-2 rounded-lg border px-3 py-2 text-[13.5px] ${n.read ? 'border-[var(--line)] text-ink-3' : n.level === 'warning' ? 'border-rust/40 text-ink' : 'border-maize/40 text-ink'}`}>
                    <span>
                      {t('concept.notifText', { level: n.level === 'warning' ? t('results.alertWarning') : t('results.alertHint'), field: n.label, year: n.payload.year, cutoff: fmtCutoff(n.payload.cutoff) })}
                      <span className="ml-2 font-mono text-[11px] text-ink-4">{fmtDate(n.created_at)}</span>
                    </span>
                    {!n.read && <button type="button" className="text-[12px] text-ink-3 hover:text-ink" onClick={async () => { await api.markRead(n.id); setNotes(await api.notifications()) }}>{t('concept.markRead')}</button>}
                  </li>
                ))}
              </ul>
            )}
          </Reveal>
        )}

        {runState.result && (
          <div className="mt-5 flex flex-col gap-5">
            <AlertCard f={runState.result} />
            <SatellitePanel f={runState.result} />
            <WeatherPanel f={runState.result} />
          </div>
        )}
        <p className="mt-6 text-[12.5px] text-ink-4">{t('concept.demoNote')}</p>
      </Container>
    </section>
  )
}
