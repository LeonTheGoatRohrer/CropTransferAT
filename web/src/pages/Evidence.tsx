import { useMemo, useState, type ReactNode } from 'react'
import { useTranslation } from 'react-i18next'
import type { Evidence as Ev } from '../api/types'
import { CiRows, Histogram, LineCi, PairedBars, Scatter, Strip, type CiRow } from '../components/charts/Stats'
import { Legend } from '../components/charts/core'
import { StrengthBadge, type Strength } from '../components/ui/Badge'
import { Metric } from '../components/ui/Metric'
import { Reveal } from '../components/ui/Reveal'
import { Container, SectionHeader, Source } from '../components/ui/Section'
import { ErrorNote, Skeleton } from '../components/ui/States'
import { Tabs } from '../components/ui/Tabs'
import { keepGreek } from '../components/ui/Text'
import { tokens } from '../lib/color'
import { fmt, fmtCi, fmtCutoff, fmtInt, fmtPct, fmtSigned } from '../lib/format'
import { useResource } from '../lib/useResource'
import { getEvidence } from '../services/evidenceService'

export default function Evidence() {
  const { t } = useTranslation()
  const ev = useResource(getEvidence, 'evidence')
  return (
    <>
      <section className="pt-36 pb-10">
        <Container>
          <Reveal>
            <p className="eyebrow mb-5">{t('evidence.eyebrow')}</p>
            <h1 className="max-w-[920px] text-balance text-[clamp(2.4rem,5.4vw,4.4rem)] leading-[1] tracking-[-0.04em] [hyphens:auto]">{t('evidence.title')}</h1>
            <p className="mt-6 max-w-[700px] text-pretty text-[17px] leading-relaxed text-ink-2">{t('evidence.lede')}</p>
          </Reveal>
        </Container>
      </section>
      {ev.status === 'loading' && <Container><Skeleton className="h-[480px]" /></Container>}
      {ev.error && <Container><ErrorNote error={ev.error} /></Container>}
      {ev.data && (
        <>
          <Scorecard ev={ev.data} />
          <WithinField ev={ev.data} />
          <FieldLevel ev={ev.data} />
          <YearModels ev={ev.data} />
          <Regional ev={ev.data} />
          {ev.data.austria && <Austria ev={ev.data} />}
        </>
      )}
    </>
  )
}

/* ------------------------------------------------------------------ */

function Scorecard({ ev }: { ev: Ev }) {
  const { t } = useTranslation()
  const b0 = ev.innerfeld_main.untrained.BARC.B0
  const a0 = ev.stress_models.A0
  const eu = ev.eu_cutoffs.find((c) => c.cutoff === '09-01')!
  const st = ev.phase4_stages.at(-1)!
  const rows: { q: string; metric: string; value: string; ci: string; n: string; baseline: string; strength: Strength; href: string }[] = [
    { q: t('evidence.rows.q1'), metric: t('evidence.rows.m1'), value: fmt(b0.rho_median, 2), ci: fmtCi(b0.rho_ci?.[0], b0.rho_ci?.[1]), n: t('evidence.rows.n1', { n: b0.n_fy, c: b0.n_clusters }), baseline: t('evidence.rows.b1'), strength: 'robust', href: '#within-field' },
    { q: t('evidence.rows.q2'), metric: t('evidence.rows.m2'), value: fmt(a0.pr_auc, 2), ci: fmtCi(a0.pr_auc_lo, a0.pr_auc_hi), n: t('evidence.rows.n2', { n: a0.n }), baseline: t('evidence.rows.b2', { c: fmt(a0.prevalence, 2) }), strength: 'limited', href: '#field-level' },
    { q: t('evidence.rows.q3'), metric: t('evidence.rows.m3'), value: fmt(st.rho, 2), ci: fmtCi(st.rho_lo, st.rho_hi), n: t('evidence.rows.n3', { n: st.n, c: st.clusters }), baseline: t('evidence.rows.b3'), strength: 'failed', href: '#year-models' },
    { q: t('evidence.rows.q4'), metric: t('evidence.rows.m4'), value: fmt(eu.spearman.value, 2), ci: fmtCi(eu.spearman.lo, eu.spearman.hi), n: t('evidence.rows.n4', { n: fmtInt(eu.n), c: eu.countries }), baseline: t('evidence.rows.b4', { s: fmt(eu.skill_vs_normal.value, 2) }), strength: 'certain-small', href: '#regional' },
  ]
  const at = ev.austria?.cutoffs['09-01']?.['V2-A_stress_score']
  if (at)
    rows.push({
      q: t('evidence.rows.q5'), metric: t('evidence.rows.m5'), value: fmt(at.rho, 2), ci: fmtCi(at.lo, at.hi), n: t('evidence.rows.n5', { n: at.n, c: at.clusters }),
      baseline: t('evidence.rows.b5', { v: fmt(ev.austria?.cutoffs['09-01']['V2-baseline_NDVI']?.rho, 2) }), strength: 'limited', href: '#austria',
    })
  const head = t('evidence.table', { returnObjects: true }) as Record<string, string>
  return (
    <section className="pb-12">
      <Container>
        <Reveal className="panel overflow-x-auto">
          <table className="w-full min-w-[880px] text-left text-[13.5px]">
            <thead>
              <tr className="border-b border-[var(--line)] text-ink-3">
                {['q', 'metric', 'value', 'ci', 'units', 'vs', 'verdict'].map((h) => (
                  <th key={h} className="px-5 py-4 font-mono text-[10.5px] font-normal uppercase tracking-[0.12em]">{head[h]}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.q} className="group border-b border-[var(--line)] last:border-0 transition-colors hover:bg-white/[0.025]">
                  <td className="px-5 py-4"><a href={r.href} className="font-medium text-ink group-hover:text-maize">{r.q}</a></td>
                  <td className="px-5 py-4 text-ink-2">{r.metric}</td>
                  <td className="px-5 py-4 font-display text-[22px] font-semibold tabular">{r.value}</td>
                  <td className="px-5 py-4 font-mono text-[12px] text-ink-3 tabular">{r.ci}</td>
                  <td className="px-5 py-4 text-ink-3">{r.n}</td>
                  <td className="px-5 py-4 text-ink-3">{r.baseline}</td>
                  <td className="px-5 py-4"><StrengthBadge strength={r.strength} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </Reveal>
      </Container>
    </section>
  )
}

/* ------------------------------------------------------------------ */

function Panel({ title, children, source, className = '' }: { title: string; children: ReactNode; source?: string; className?: string }) {
  return (
    <Reveal className={`panel flex flex-col p-6 sm:p-7 ${className}`}>
      <p className="eyebrow mb-6">{keepGreek(title)}</p>
      <div className="flex-1">{children}</div>
      {source && <Source className="mt-5">{source}</Source>}
    </Reveal>
  )
}

function WithinField({ ev }: { ev: Ev }) {
  const { t } = useTranslation()
  const u = ev.innerfeld_main.untrained
  const e = ev.innerfeld_main.E
  const l = ev.innerfeld_main.L
  const rows: CiRow[] = [
    { label: t('evidence.wf.m1'), sub: t('evidence.wf.m1s'), value: e.BARC.M1.rho_median, lo: e.BARC.M1.rho_ci?.[0], hi: e.BARC.M1.rho_ci?.[1], emphasis: true, color: tokens.sage },
    { label: t('evidence.wf.b0'), sub: t('evidence.wf.b0s'), value: u.BARC.B0.rho_median, lo: u.BARC.B0.rho_ci?.[0], hi: u.BARC.B0.rho_ci?.[1], color: tokens.sage },
    { label: t('evidence.wf.b1'), sub: t('evidence.wf.b1s'), value: u.BARC.B1.rho_median, lo: u.BARC.B1.rho_ci?.[0], hi: u.BARC.B1.rho_ci?.[1] },
    { label: t('evidence.wf.lso'), sub: t('evidence.wf.lsos'), value: l.BARC.M1.rho_median, lo: l.BARC.M1.rho_ci?.[0], hi: l.BARC.M1.rho_ci?.[1] },
    { label: t('evidence.wf.pos'), sub: t('evidence.wf.poss'), value: e.BARC.KRAUM.rho_median, lo: e.BARC.KRAUM.rho_ci?.[0], hi: e.BARC.KRAUM.rho_ci?.[1], color: tokens.ink3 },
  ]
  const groups = [
    { key: 'BARC', label: 'BARC', sub: t('evidence.wf.siteBarc'), color: tokens.sage },
    { key: 'KAYAD', label: 'Kayad', sub: t('evidence.wf.siteKayad'), color: tokens.maize },
    { key: 'COLORADO', label: 'Akron', sub: t('evidence.wf.siteAkron'), color: tokens.water },
  ].map((s) => {
    const vals = ev.innerfeld_per_fy.filter((r) => r.model === 'B0' && r.scheme === 'untrained' && r.site === s.key && r.rho != null)
    const sorted = vals.map((v) => v.rho as number).sort((a, b) => a - b)
    return { label: s.label, sub: s.sub, color: s.color, values: vals.map((v) => ({ v: v.rho as number, title: `${v.fy_key.split(':')[1]?.split('|')[0] ?? ''} ${v.year}` })), median: sorted.length ? sorted[Math.floor(sorted.length / 2)] : undefined }
  })
  const b0All = ev.innerfeld_per_fy.filter((r) => r.model === 'B0' && r.scheme === 'untrained' && r.rho != null)
  const nPos = b0All.filter((r) => (r.rho as number) > 0).length
  const map = ev.within_field_map
  const shuffle = ev.innerfeld_label_shuffle.E_BARC_median_rho
  return (
    <section id="within-field" className="scroll-mt-20 py-20">
      <Container>
        <SectionHeader eyebrow={t('evidence.wf.eyebrow')} title={t('evidence.wf.title')} lede={t('evidence.wf.lede')} aside={<StrengthBadge strength="robust" />} />
        <div className="mt-12 grid gap-5 lg:grid-cols-[1.15fr_1fr]">
          <Panel title={t('evidence.wf.ciTitle')} source={t('evidence.wf.srcCi')}>
            <CiRows rows={rows} domain={[-0.4, 1]} reference={0} />
          </Panel>
          <Panel title={t('evidence.wf.stripTitle')} source="results/2026-10-17_innerfeld/per_fy.csv">
            <Strip groups={groups} domain={[-0.2, 1]} xLabel="Spearman ρ" reference={0} />
            <p className="mt-4 text-[13px] leading-relaxed text-ink-3">{t('evidence.wf.positive', { p: nPos, n: b0All.length })}</p>
          </Panel>
        </div>
        <div className="mt-5 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          <Panel title={t('evidence.wf.p1')}>
            <Metric label={t('evidence.wf.p1m')} value={map.median_precision} digits={2} n={`${map.n_fy} ${t('common.fieldYears')}`} note={t('evidence.wf.p1n', { v: fmtPct(map.median_prevalence) })} />
          </Panel>
          <Panel title={t('evidence.wf.p2')}>
            <Metric label={t('evidence.wf.p2m')} value={map.median_lift} digits={1} prefix="× " note={t('evidence.wf.p2n', { v: fmtPct(map.median_recall) })} />
          </Panel>
          <Panel title={t('evidence.wf.p3')}>
            <Metric label={t('evidence.wf.p3m')} value={shuffle.mean} digits={2} note={t('evidence.wf.p3n')} />
          </Panel>
          <Panel title={t('evidence.wf.p4')}>
            <Metric label={t('evidence.wf.p4m')} value={u.KAYAD.B0.rho_median} digits={2} note={t('evidence.wf.p4n')} />
          </Panel>
        </div>
      </Container>
    </section>
  )
}

/* ------------------------------------------------------------------ */

function FieldLevel({ ev }: { ev: Ev }) {
  const { t } = useTranslation()
  const sm = ev.stress_models
  const p3 = ev.early_warning_field
  const fy = ev.field_years
  const noT4 = ev.stress_sensitivity['A0|ohne_T4']
  const withinTr = ev.stress_sensitivity['A_roh|KBS_rho_innerhalb_Behandlung_Jahr']
  const last = p3.find((r) => r.cutoff === '09-01')!
  const la = last.a_threshold_on_pred_RY as { pr_auc: number; pr_auc_lo: number; pr_auc_hi: number }
  const lb = last.b_direct_classifier as { pr_auc: number; pr_auc_lo: number; pr_auc_hi: number }
  const rows: CiRow[] = [
    { label: t('evidence.fl.raw'), sub: t('evidence.fl.raws'), value: sm.A_roh.pr_auc, lo: sm.A_roh.pr_auc_lo, hi: sm.A_roh.pr_auc_hi, emphasis: true, color: tokens.maize },
    { label: t('evidence.fl.a0'), sub: t('evidence.fl.a0s'), value: sm.A0.pr_auc, lo: sm.A0.pr_auc_lo, hi: sm.A0.pr_auc_hi, color: tokens.maize },
    ...(['M1', 'M2', 'M3', 'M4'] as const).map((k) => {
      const a = ev.ablation.find((r) => r.feature_set === k)!
      return { label: `A0 ${t(`evidence.fl.${k}`)}`, sub: t('evidence.fl.abl'), value: a.pr_auc, lo: a.pr_auc_lo, hi: a.pr_auc_hi, color: tokens.ink3 }
    }),
    { label: t('evidence.fl.learned'), sub: t('evidence.fl.learneds'), value: la.pr_auc, lo: la.pr_auc_lo, hi: la.pr_auc_hi, color: tokens.ink3 },
    { label: t('evidence.fl.direct'), sub: t('evidence.fl.directs'), value: lb.pr_auc, lo: lb.pr_auc_lo, hi: lb.pr_auc_hi, color: tokens.ink3 },
  ]
  const pts = fy
    .filter((r) => r.score != null)
    .map((r) => ({
      x: r.score as number,
      y: r.ry,
      color: r.treatment === 'T4' ? tokens.maize : r.site === 'BARC' ? tokens.water : tokens.sage,
      ring: !r.alarm,
      r: 4,
      label: (
        <>
          <p className="font-mono text-[11px] text-ink-3">{r.fy_key.split('|')[1]} · {r.year}</p>
          <p>{t('evidence.fl.tip', { s: fmtSigned(r.score, 3), r: fmt(r.ry, 2) })}</p>
          <p className={r.alarm ? 'text-rust' : 'text-ink-3'}>{r.alarm ? t('evidence.fl.alarm') : t('evidence.fl.noAlarm')}{r.risk ? ` · ${t('evidence.fl.atRisk')}` : ''}</p>
        </>
      ),
    }))
  const series = [
    { key: 'reference_stress_score', label: t('evidence.fl.earlyScore'), color: tokens.maize, dashed: false },
    { key: 'a_threshold_on_pred_RY', label: t('evidence.fl.earlyLearned'), color: tokens.water, dashed: false },
    { key: 'b_direct_classifier', label: t('evidence.fl.earlyDirect'), color: tokens.ink3, dashed: true },
  ].map((s) => ({
    label: s.label,
    color: s.color,
    dashed: s.dashed,
    values: p3.map((r) => {
      const m = r[s.key] as { pr_auc: number | null; pr_auc_lo: number | null; pr_auc_hi: number | null }
      return { v: m?.pr_auc ?? null, lo: m?.pr_auc_lo, hi: m?.pr_auc_hi }
    }),
  }))
  const a = ev.alarm
  return (
    <section id="field-level" className="scroll-mt-20 py-20">
      <Container>
        <SectionHeader eyebrow={t('evidence.fl.eyebrow')} title={t('evidence.fl.title')} lede={t('evidence.fl.lede')} aside={<StrengthBadge strength="limited" />} />
        <div className="mt-12 grid gap-5 lg:grid-cols-2">
          <Panel title={t('evidence.fl.ciTitle', { c: fmt(sm.A0.prevalence, 2) })} source={t('evidence.fl.srcCi')}>
            <CiRows rows={rows} domain={[0, 1]} reference={sm.A0.prevalence} referenceLabel={t('common.chance')} />
          </Panel>
          <Panel title={t('evidence.fl.scatterTitle')} source={t('evidence.fl.srcScatter')}>
            <Scatter points={pts} xLabel={t('evidence.fl.scatterX')} yLabel={t('evidence.fl.scatterY')} height={330} yDomain={[0.2, 1.6]} hLines={[{ v: 0.85, label: t('evidence.fl.atRiskLine'), color: tokens.rust }]} xFmt={(v) => fmt(v, 2)} yFmt={(v) => fmt(v, 1)} />
            <Legend
              className="mt-3"
              items={[
                { label: 'BARC', color: tokens.water, kind: 'dot' },
                { label: 'KBS', color: tokens.sage, kind: 'dot' },
                { label: t('evidence.fl.t4'), color: tokens.maize, kind: 'dot' },
                { label: t('evidence.fl.hollow'), color: tokens.ink3, kind: 'line' },
              ]}
            />
          </Panel>
        </div>
        <div className="mt-5 grid gap-5 lg:grid-cols-[1.3fr_1fr]">
          <Panel title={t('evidence.fl.earlyTitle')} source={t('evidence.fl.srcEarly')}>
            <LineCi categories={p3.map((r) => fmtCutoff(r.cutoff))} series={series} yDomain={[0, 1]} yFmt={(v) => fmt(v, 2)} hLines={[{ v: sm.A0.prevalence, label: t('common.chance'), color: tokens.ink4 }]} />
            <Legend className="mt-3" items={series.map((s) => ({ label: s.label, color: s.color, kind: s.dashed ? 'dash' : 'line' }))} />
          </Panel>
          <Panel title={t('evidence.fl.catchTitle')}>
            <div className="flex flex-col gap-6">
              <Metric label={t('evidence.fl.noT4')} value={noT4?.pr_auc} ci={[noT4?.pr_auc_lo, noT4?.pr_auc_hi]} n={t('evidence.fl.noT4n', { n: noT4?.n, c: fmt(noT4?.prevalence, 2) })} tone="maize" />
              <Metric label={t('evidence.fl.within')} value={withinTr?.median} digits={2} n={t('evidence.fl.withinN', { n: withinTr?.n_groups })} tone="rust" />
              <p className="text-[13.5px] leading-relaxed text-ink-2">{t('evidence.fl.catchBody')}</p>
            </div>
          </Panel>
        </div>
        <div className="mt-5 grid gap-5 md:grid-cols-3">
          <Panel title={t('evidence.fl.thrTitle')}>
            <Metric label={t('evidence.fl.thrM')} value={a.alarm_fpr} digits={2} note={t('evidence.fl.thrN')} />
          </Panel>
          <Panel title={t('evidence.fl.precTitle')}>
            <Metric label={t('evidence.fl.precM')} value={a.alarm_precision} digits={2} note={t('evidence.fl.precN', { k: Math.round(a.alarm_precision * a.n_alarm), n: a.n_alarm })} />
          </Panel>
          <Panel title={t('evidence.fl.recTitle')}>
            <Metric label={t('evidence.fl.recM')} value={a.alarm_recall} digits={2} note={t('evidence.fl.recN', { k: a.main_phase_alarms.Juli, n: a.n_alarm })} />
          </Panel>
        </div>
      </Container>
    </section>
  )
}

/* ------------------------------------------------------------------ */

function YearModels({ ev }: { ev: Ev }) {
  const { t } = useTranslation()
  const [kind, setKind] = useState<'ridge' | 'lgbm'>('ridge')
  const names = t('evidence.ym.models', { returnObjects: true }) as Record<string, string>
  const stages = t('evidence.ym.stages', { returnObjects: true }) as Record<string, string>
  const crit = t('evidence.ym.crit', { returnObjects: true }) as string[]
  const fam = ev.phase2_models.filter((r) => r.cutoff === '09-01' && r.basis === 'S2' && (r.kind === kind || r.model === 'B1'))
  const famRows: CiRow[] = fam
    .sort((a, b) => b.rho - a.rho)
    .map((r) => ({ label: names[r.model] ?? r.model, sub: t('evidence.ym.skill', { v: fmtSigned(r.skill_b0, 2) }), value: r.rho, lo: r.rho_lo, hi: r.rho_hi, color: r.model === 'B1' ? tokens.ink3 : r.skill_b0 > 0 ? tokens.sage : tokens.water }))
  const stageRows: CiRow[] = ev.phase4_stages.map((s) => ({
    label: stages[s.stage.replace(/�/g, '·')] ?? s.stage,
    sub: `${s.model} · ${s.kind} · ${t('evidence.ym.criteriaN', { n: Object.values(s.criteria).filter(Boolean).length })}`,
    value: s.rho,
    lo: s.rho_lo,
    hi: s.rho_hi,
    color: tokens.water,
  }))
  return (
    <section id="year-models" className="scroll-mt-20 py-20">
      <Container>
        <SectionHeader eyebrow={t('evidence.ym.eyebrow')} title={t('evidence.ym.title')} lede={t('evidence.ym.lede')} aside={<StrengthBadge strength="failed" />} />
        <div className="mt-12 grid gap-5 lg:grid-cols-2">
          <Panel title={t('evidence.ym.famTitle')} source={t('evidence.ym.srcFam')}>
            <div className="mb-5">
              <Tabs size="sm" label={t('evidence.ym.kind')} value={kind} onChange={setKind} items={[{ value: 'ridge', label: 'Ridge' }, { value: 'lgbm', label: 'LightGBM' }]} />
            </div>
            <CiRows rows={famRows} domain={[-0.6, 0.8]} reference={0} />
          </Panel>
          <Panel title={t('evidence.ym.roundsTitle')} source={t('evidence.ym.srcRounds')}>
            <CiRows rows={stageRows} domain={[-0.6, 0.8]} reference={0.4} referenceLabel={t('evidence.ym.criterion')} />
            <ul className="mt-5 grid gap-2 text-[13px] text-ink-2">
              {crit.map((c, i) => {
                const passed = ev.phase4_stages.map((s) => Object.values(s.criteria)[i])
                return (
                  <li key={c} className="flex items-center justify-between gap-3 border-b border-[var(--line)] pb-2 last:border-0">
                    <span>{c}</span>
                    <span className="flex gap-1.5">
                      {passed.map((p, j) => <span key={j} className={`size-2.5 rounded-full ${p ? 'bg-sage' : 'bg-rust/70'}`} title={ev.phase4_stages[j].stage} />)}
                    </span>
                  </li>
                )
              })}
            </ul>
          </Panel>
        </div>
        <p className="mt-6 max-w-[780px] text-[14px] leading-relaxed text-ink-3">{t('evidence.ym.why')}</p>
      </Container>
    </section>
  )
}

/* ------------------------------------------------------------------ */

function Regional({ ev }: { ev: Ev }) {
  const { t } = useTranslation()
  const cut = ev.eu_cutoffs
  const last = cut.find((c) => c.cutoff === '09-01')!
  const pts = useMemo(() => ev.eu_scatter.map(([y, p]) => ({ x: y, y: p, color: tokens.water, r: 2.2 })), [ev])
  const countries = Object.entries(ev.eu_per_country).filter(([, v]) => v.n >= 50).sort((a, b) => b[1].n - a[1].n)
  const baseRows = [
    { label: 'RMSE', a: last.rmse.value!, b: last.baselines.normal_year.rmse.value! },
    { label: 'MAE', a: last.mae.value!, b: last.baselines.normal_year.mae.value! },
  ]
  const noDe = (ev.eu_controls.without_DE_eval as { metrics: { model_spearman: { value: number } } }).metrics.model_spearman.value
  return (
    <section id="regional" className="scroll-mt-20 py-20">
      <Container>
        <SectionHeader eyebrow={t('evidence.eu.eyebrow')} title={t('evidence.eu.title')} lede={t('evidence.eu.lede')} aside={<StrengthBadge strength="certain-small" />} />
        <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <Panel title={t('evidence.eu.rank')}><Metric label={t('evidence.eu.rho')} value={last.spearman.value} ci={[last.spearman.lo, last.spearman.hi]} n={fmtInt(last.n)} tone="water" size="lg" /></Panel>
          <Panel title={t('evidence.eu.better')}><Metric label={t('evidence.eu.skill')} value={last.skill_vs_normal.value} ci={[last.skill_vs_normal.lo, last.skill_vs_normal.hi]} size="lg" /></Panel>
          <Panel title={t('evidence.eu.r2t')}><Metric label="R²" value={last.r2.value} ci={[last.r2.lo, last.r2.hi]} size="lg" /></Panel>
          <Panel title={t('evidence.eu.within')}><Metric label={t('evidence.eu.withinM')} value={last.within_year.value} ci={[last.within_year.lo, last.within_year.hi]} size="lg" note={t('evidence.eu.withinN', { v: fmt(last.yearly_mean_spearman, 2) })} /></Panel>
        </div>
        <div className="mt-5 grid gap-5 lg:grid-cols-2">
          <Panel title={t('evidence.eu.baseTitle')} source={t('evidence.eu.srcPooled')}>
            <PairedBars rows={baseRows} a={{ label: t('evidence.eu.model'), color: tokens.water }} b={{ label: t('evidence.eu.normal'), color: tokens.ink4 }} format={(v) => fmt(v, 3)} />
            <p className="mt-3 text-[13px] text-ink-3">{t('evidence.eu.trend', { r: fmt(last.baselines.trend.rmse.value, 3), m: fmt(last.baselines.trend.mae.value, 3) })}</p>
            <Legend className="mt-4" items={[{ label: t('evidence.eu.model'), color: tokens.water, kind: 'bar' }, { label: t('evidence.eu.normalLong'), color: tokens.ink4, kind: 'bar' }]} />
          </Panel>
          <Panel title={t('evidence.eu.early')} source={t('evidence.eu.srcMetrics')}>
            <LineCi
              categories={cut.map((c) => fmtCutoff(c.cutoff))}
              yDomain={[-0.1, 0.5]}
              yFmt={(v) => fmt(v, 2)}
              series={[
                { label: 'Spearman ρ', color: tokens.water, values: cut.map((c) => ({ v: c.spearman.value, lo: c.spearman.lo, hi: c.spearman.hi })) },
                { label: t('evidence.eu.rhoWithin'), color: tokens.sage, values: cut.map((c) => ({ v: c.within_year.value, lo: c.within_year.lo, hi: c.within_year.hi })) },
                { label: t('evidence.eu.skillNormal'), color: tokens.maize, values: cut.map((c) => ({ v: c.skill_vs_normal.value, lo: c.skill_vs_normal.lo, hi: c.skill_vs_normal.hi })) },
              ]}
            />
            <Legend className="mt-3" items={[{ label: 'Spearman ρ', color: tokens.water }, { label: t('evidence.eu.rhoWithin'), color: tokens.sage }, { label: t('evidence.eu.skillNormal'), color: tokens.maize }]} />
          </Panel>
          <Panel title={t('evidence.eu.scatter')} source={t('evidence.eu.srcPred')}>
            <Scatter points={pts} xLabel={t('evidence.eu.scatterX')} yLabel={t('evidence.eu.scatterY')} xDomain={[0.2, 1.8]} yDomain={[0.6, 1.4]} diagonal height={320} opacity={0.35} xFmt={(v) => fmt(v, 1)} yFmt={(v) => fmt(v, 1)} />
            <p className="mt-3 text-[13px] text-ink-3">{t('evidence.eu.scatterNote')}</p>
          </Panel>
          <Panel title={t('evidence.eu.resid')} source={t('evidence.eu.srcAll')}>
            <Histogram edges={ev.eu_residuals.edges} series={[{ label: t('evidence.eu.model'), counts: ev.eu_residuals.model, color: tokens.water }, { label: t('evidence.eu.normal'), counts: ev.eu_residuals.normal_year, color: tokens.ink3 }]} xLabel={t('evidence.eu.residX')} height={230} />
            <Legend className="mt-3" items={[{ label: t('evidence.eu.model'), color: tokens.water }, { label: t('evidence.eu.normal'), color: tokens.ink3 }]} />
          </Panel>
          <Panel title={t('evidence.eu.range')} source={t('evidence.eu.srcAll')}>
            <PairedBars rows={ev.eu_by_range.map((r) => ({ label: r.bin, sub: `n = ${fmtInt(r.n)}`, a: r.mae_model, b: r.mae_normal }))} a={{ label: t('evidence.eu.model'), color: tokens.water }} b={{ label: t('evidence.eu.normal'), color: tokens.ink4 }} format={(v) => fmt(v, 2)} />
            <p className="mt-3 text-[13px] text-ink-3">{t('evidence.eu.rangeNote')}</p>
          </Panel>
          <Panel title={t('evidence.eu.country')} source={t('evidence.eu.srcCountry')}>
            <PairedBars rows={countries.map(([c, v]) => ({ label: c, sub: `n = ${fmtInt(v.n)}`, a: Math.max(0, v.spearman), b: Math.max(0, v.skill_vs_yas1) }))} a={{ label: 'ρ', color: tokens.water }} b={{ label: 'Skill', color: tokens.maize }} format={(v) => fmt(v, 2)} />
            <p className="mt-3 text-[13px] text-ink-3">{t('evidence.eu.countryNote', { v: fmt(noDe, 2) })}</p>
          </Panel>
        </div>
        <Reveal className="mt-5 panel p-6 text-[13.5px] leading-relaxed text-ink-2">
          <p className="eyebrow mb-3">{t('evidence.eu.disclosed')}</p>
          {t('evidence.eu.disclosedBody', { tag: ev.eu_meta.freeze, commit: ev.eu_meta.commit })}
        </Reveal>
      </Container>
    </section>
  )
}

/* ------------------------------------------------------------------ */

function Austria({ ev }: { ev: Ev }) {
  const { t } = useTranslation()
  const at = ev.austria!
  const cuts = Object.keys(at.cutoffs)
  const last = at.cutoffs['09-01']
  const ndvi = last['V2-baseline_NDVI']
  const rows: CiRow[] = [
    { label: t('evidence.at.score'), sub: t('evidence.at.scoreS', { n: last['V2-A_stress_score'].n }), value: last['V2-A_stress_score'].rho, lo: last['V2-A_stress_score'].lo, hi: last['V2-A_stress_score'].hi, emphasis: true, color: tokens.maize },
    ...(ndvi ? [{ label: t('evidence.at.ndvi'), sub: t('evidence.at.ndviS'), value: ndvi.rho, lo: ndvi.lo, hi: ndvi.hi, color: tokens.ink3 }] : []),
    { label: t('evidence.at.states'), sub: t('evidence.at.statesS', { n: last.V1_regional_model.n }), value: last.V1_regional_model.rho, lo: last.V1_regional_model.lo, hi: last.V1_regional_model.hi, color: tokens.water },
    { label: t('evidence.at.trial'), sub: t('evidence.at.trialS', { n: last['V2-B_regional_model'].n }), value: last['V2-B_regional_model'].rho, lo: last['V2-B_regional_model'].lo, hi: last['V2-B_regional_model'].hi, color: tokens.ink3 },
  ]
  const r = at.retrain?.['09-01']
  return (
    <section id="austria" className="scroll-mt-20 py-20">
      <Container>
        <SectionHeader eyebrow={t('evidence.at.eyebrow')} title={t('evidence.at.title')} lede={t('evidence.at.lede')} aside={<StrengthBadge strength="limited" />} />
        <div className="mt-12 grid gap-5 lg:grid-cols-[1.2fr_1fr]">
          <Panel title={t('evidence.at.ciTitle')} source={t('evidence.at.src')}>
            <CiRows rows={rows} domain={[-1, 1]} reference={0} />
          </Panel>
          <Panel title={t('evidence.at.byCutoff')}>
            <LineCi
              categories={cuts.map(fmtCutoff)}
              yDomain={[-0.5, 1]}
              yFmt={(v) => fmt(v, 2)}
              series={[
                { label: t('evidence.at.scoreSites'), color: tokens.maize, values: cuts.map((c) => ({ v: at.cutoffs[c]['V2-A_stress_score'].rho, lo: at.cutoffs[c]['V2-A_stress_score'].lo, hi: at.cutoffs[c]['V2-A_stress_score'].hi })) },
                { label: t('evidence.at.euStates'), color: tokens.water, values: cuts.map((c) => ({ v: at.cutoffs[c].V1_regional_model.rho, lo: at.cutoffs[c].V1_regional_model.lo, hi: at.cutoffs[c].V1_regional_model.hi })) },
              ]}
            />
            <Legend className="mt-3" items={[{ label: t('evidence.at.scoreSites'), color: tokens.maize }, { label: t('evidence.at.euStates'), color: tokens.water }]} />
          </Panel>
        </div>
        <div className="mt-5 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          <Panel title={t('evidence.at.withinYear')}>
            <Metric label={t('evidence.at.withinYearM')} value={last['V2-A_within_year'].median} digits={2} tone="rust" note={t('evidence.at.withinYearN', { n: last['V2-A_within_year'].n_groups })} />
          </Panel>
          <Panel title={t('evidence.at.withinSite')}>
            <Metric label={t('evidence.at.withinSiteM')} value={last['V2-A_within_site'].median} digits={2} note={t('evidence.at.withinSiteN', { n: last['V2-A_within_site'].n_groups })} />
          </Panel>
          <Panel title={t('evidence.at.rmse')}>
            <Metric label={t('evidence.at.rmseM')} value={last.V1_regional_model.rmse_diff} digits={3} ci={[last.V1_regional_model.rmse_diff_lo, last.V1_regional_model.rmse_diff_hi]} note={t('evidence.at.rmseN')} />
          </Panel>
          {r && (
            <Panel title={t('evidence.at.recal')}>
              <Metric label={t('evidence.at.recalM')} value={r.pred_r1.rmse} digits={3} prefix={`${fmt(r.pred_r0.rmse, 3)} → `} note={t('evidence.at.recalN', { n: r.pred_r1.n })} />
            </Panel>
          )}
        </div>
        <Reveal className="mt-5 panel p-6 text-[13.5px] leading-relaxed text-ink-2">
          <p className="eyebrow mb-3">{t('evidence.at.notClaim')}</p>
          {t('evidence.at.notClaimBody')}
        </Reveal>
        {ev.at_feasibility && (
          <Reveal className="mt-5 panel border-dashed p-6">
            <div className="flex flex-wrap items-center gap-3">
              <p className="eyebrow">{t('concept.atTitle')}</p>
              <StrengthBadge strength="failed" />
            </div>
            <p className="mt-3 text-[14px] text-ink-2">{t('concept.atBody')}</p>
            <div className="mt-3 flex flex-col gap-2 text-[13.5px] text-ink">
              <p>
                {t('concept.atCounts', {
                  sy: ev.at_feasibility.counts.site_years_with_yield_and_score,
                  s: ev.at_feasibility.counts.sites,
                  y: ev.at_feasibility.counts.years,
                  c: ev.at_feasibility.counts.trial_rows_with_coordinates ?? 0,
                  t: ev.at_feasibility.counts.trial_rows ?? 0,
                })}
              </p>
              {ev.at_feasibility.metrics && (
                <p>
                  {keepGreek(
                    t('concept.atResult', {
                      rho: fmt(ev.at_feasibility.metrics.rho, 2),
                      ci: fmtCi(ev.at_feasibility.metrics.rho_ci[0], ev.at_feasibility.metrics.rho_ci[1]),
                      rm: fmt(ev.at_feasibility.metrics.rmse_model, 3),
                      rn: fmt(ev.at_feasibility.metrics.rmse_normal, 3),
                    }),
                  )}
                </p>
              )}
              <p className="text-ink-2">{t('concept.atVerdict')}</p>
            </div>
            <Source className="mt-4">results/2026-10-17_at_feasibility/metrics.json · DECISIONS.md</Source>
          </Reveal>
        )}
      </Container>
    </section>
  )
}
