import { useMemo, useState } from 'react'
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
import { fmt, fmtCi, fmtPct, fmtSigned } from '../lib/format'
import { useResource } from '../lib/useResource'
import { getEvidence } from '../services/evidenceService'

const CUT_LABEL = (c: string) => {
  const [m, d] = c.split('-').map(Number)
  return `${d} ${['', '', '', '', '', '', 'Jun', 'Jul', 'Aug', 'Sep'][m]}`
}

const MODEL_NAMES: Record<string, string> = {
  B1: 'Baseline B1 · NDVI peak only',
  'M-S': 'Satellite',
  'M-W': 'Weather',
  'M-B': 'Soil and terrain',
  'M-B+': 'Soil + SSURGO',
  'M-WB': 'Weather + soil',
  'M-SW': 'Satellite + weather',
  'M-SB': 'Satellite + soil',
  'M-alle': 'Satellite + weather + soil',
}

export default function Evidence() {
  const ev = useResource(getEvidence, 'evidence')
  return (
    <>
      <section className="pt-36 pb-10">
        <Container>
          <Reveal>
            <p className="eyebrow mb-5">Evidence · benchmarks</p>
            <h1 className="max-w-[900px] text-balance text-[clamp(2.6rem,6vw,4.6rem)] leading-[0.98] tracking-[-0.04em]">Every claim, with the test it had to pass.</h1>
            <p className="mt-6 max-w-[680px] text-pretty text-[17px] leading-relaxed text-ink-2">
              All numbers below are read from the project’s result files. Each comes with a 95 % confidence interval from a cluster
              bootstrap and the number of independent units behind it. Validation always holds out whole fields, years or countries.
            </p>
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
  const b0 = ev.innerfeld_main.untrained.BARC.B0
  const a0 = ev.stress_models.A0
  const eu = ev.eu_cutoffs.find((c) => c.cutoff === '09-01')!
  const st = ev.phase4_stages.at(-1)!
  const rows: { q: string; metric: string; value: string; ci: string; n: string; baseline: string; strength: Strength; href: string }[] = [
    { q: 'Where in the field is yield missing?', metric: 'Median Spearman ρ (NDVI vs pixel yield)', value: fmt(b0.rho_median, 2), ci: fmtCi(b0.rho_ci?.[0], b0.rho_ci?.[1]), n: `${b0.n_fy} field-years · ${b0.n_clusters} fields`, baseline: 'position only: ρ 0.03', strength: 'robust', href: '#within-field' },
    { q: 'Which field-years are at risk?', metric: 'PR-AUC on 1 Sep', value: fmt(a0.pr_auc, 2), ci: fmtCi(a0.pr_auc_lo, a0.pr_auc_hi), n: `${a0.n} field-years · 8 site-years`, baseline: `chance ${fmt(a0.prevalence, 2)}`, strength: 'limited', href: '#field-level' },
    { q: 'How much worse is this field’s year?', metric: 'Spearman ρ, best pre-registered round', value: fmt(st.rho, 2), ci: fmtCi(st.rho_lo, st.rho_hi), n: `${st.n} field-years · ${st.clusters} site-years`, baseline: 'does not beat “normal year”', strength: 'failed', href: '#year-models' },
    { q: 'Which years are worse for a region?', metric: 'Spearman ρ on 1 Sep (EU, LOCO)', value: fmt(eu.spearman.value, 2), ci: fmtCi(eu.spearman.lo, eu.spearman.hi), n: `${eu.n.toLocaleString('en-US')} region-years · ${eu.countries} countries`, baseline: `skill ${fmt(eu.skill_vs_normal.value, 2)} vs normal year`, strength: 'certain-small', href: '#regional' },
  ]
  const at = ev.austria?.cutoffs['09-01']?.['V2-A_stress_score']
  if (at) rows.push({ q: 'Does it carry over to Austria?', metric: 'Spearman ρ, frozen stress score, 1 Sep', value: fmt(at.rho, 2), ci: fmtCi(at.lo, at.hi), n: `${at.n} site-years · ${at.clusters} years`, baseline: `plain NDVI ρ ${fmt(ev.austria?.cutoffs['09-01']['V2-baseline_NDVI']?.rho, 2)}`, strength: 'limited', href: '#austria' })
  return (
    <section className="pb-12">
      <Container>
        <Reveal className="panel overflow-x-auto">
          <table className="w-full min-w-[860px] text-left text-[13.5px]">
            <thead>
              <tr className="border-b border-[var(--line)] text-ink-3">
                {['Question', 'Metric', 'Value', '95 % CI', 'Units', 'Compared with', 'Verdict'].map((h) => (
                  <th key={h} className="px-5 py-4 font-mono text-[10.5px] font-normal uppercase tracking-[0.12em]">{h}</th>
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

function Panel({ title, children, source, className = '' }: { title: string; children: React.ReactNode; source?: string; className?: string }) {
  return (
    <Reveal className={`panel flex flex-col p-6 sm:p-7 ${className}`}>
      <p className="eyebrow mb-6">{keepGreek(title)}</p>
      <div className="flex-1">{children}</div>
      {source && <Source className="mt-5">{source}</Source>}
    </Reveal>
  )
}

function WithinField({ ev }: { ev: Ev }) {
  const u = ev.innerfeld_main.untrained
  const e = ev.innerfeld_main.E
  const l = ev.innerfeld_main.L
  const rows: CiRow[] = [
    { label: 'Model M1 · trained ridge', sub: 'NDVI/NDRE windows, leave-one-field-out', value: e.BARC.M1.rho_median, lo: e.BARC.M1.rho_ci?.[0], hi: e.BARC.M1.rho_ci?.[1], emphasis: true, color: tokens.sage },
    { label: 'Rule B0 · raw NDVI', sub: '10 Jul – 18 Aug, no training', value: u.BARC.B0.rho_median, lo: u.BARC.B0.rho_ci?.[0], hi: u.BARC.B0.rho_ci?.[1], color: tokens.sage },
    { label: 'Rule B1 · NDVI at peak', sub: 'window around the curve maximum', value: u.BARC.B1.rho_median, lo: u.BARC.B1.rho_ci?.[0], hi: u.BARC.B1.rho_ci?.[1] },
    { label: 'M1 trained at other sites', sub: 'leave-one-site-out', value: l.BARC.M1.rho_median, lo: l.BARC.M1.rho_ci?.[0], hi: l.BARC.M1.rho_ci?.[1] },
    { label: 'Position only (control)', sub: 'cell coordinates, no satellite', value: e.BARC.KRAUM.rho_median, lo: e.BARC.KRAUM.rho_ci?.[0], hi: e.BARC.KRAUM.rho_ci?.[1], color: tokens.ink3 },
  ]
  const groups = (model: string, scheme: string) =>
    [
      { key: 'BARC', label: 'BARC', sub: 'Maryland · 41', color: tokens.sage },
      { key: 'KAYAD', label: 'Kayad', sub: 'Italy · 3', color: tokens.maize },
      { key: 'COLORADO', label: 'Akron', sub: 'Colorado · 6', color: tokens.water },
    ].map((s) => {
      const vals = ev.innerfeld_per_fy.filter((r) => r.model === model && r.scheme === scheme && r.site === s.key && r.rho != null)
      return { label: s.label, sub: s.sub, color: s.color, values: vals.map((v) => ({ v: v.rho as number, title: `${v.fy_key.split(':')[1]?.split('|')[0] ?? ''} ${v.year}` })), median: vals.length ? vals.map((v) => v.rho as number).sort((a, b) => a - b)[Math.floor(vals.length / 2)] : undefined }
    })
  const b0All = ev.innerfeld_per_fy.filter((r) => r.model === 'B0' && r.scheme === 'untrained' && r.rho != null)
  const nPos = b0All.filter((r) => (r.rho as number) > 0).length
  const map = ev.within_field_map
  const shuffle = ev.innerfeld_label_shuffle.E_BARC_median_rho
  return (
    <section id="within-field" className="scroll-mt-20 py-20">
      <Container>
        <SectionHeader
          eyebrow="1 · Within the field"
          title="Mid-summer NDVI ranks the weak zones."
          lede="Per field-year, the 10-m cells are ranked by NDVI and compared with the combine’s yield map. A trained model adds a little; the raw rule already carries most of the signal."
          aside={<StrengthBadge strength="robust" />}
        />
        <div className="mt-12 grid gap-5 lg:grid-cols-[1.15fr_1fr]">
          <Panel title="Median ρ across 41 BARC field-years, 95 % CI" source="results/2026-10-17_innerfeld/metrics.json · schemes E (per site) and L (leave-one-site-out)">
            <CiRows rows={rows} domain={[-0.4, 1]} reference={0} />
          </Panel>
          <Panel title="Each dot is one field-year · rule B0" source="results/2026-10-17_innerfeld/per_fy.csv">
            <Strip groups={groups('B0', 'untrained')} domain={[-0.2, 1]} xLabel="Spearman ρ" reference={0} />
            <p className="mt-4 text-[13px] leading-relaxed text-ink-3">{nPos} of {b0All.length} field-years are positive. Only BARC has enough field-years to judge; Italy and Colorado point the same way.</p>
          </Panel>
        </div>
        <div className="mt-5 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          <Panel title="Flagged quarter is truly low">
            <Metric label="Median precision" value={map.median_precision} digits={2} n={`${map.n_fy} field-years`} note={`against ${fmtPct(map.median_prevalence)} low-yield cells overall`} />
          </Panel>
          <Panel title="Better than random">
            <Metric label="Median lift" value={map.median_lift} digits={1} prefix="× " note={`${fmtPct(map.median_recall)} of low-yield cells are found`} />
          </Panel>
          <Panel title="Label-shuffle control">
            <Metric label="Mean ρ, shuffled yields" value={shuffle.mean} digits={2} note="20 repetitions. Falls to zero as it should; single runs reach ±0.45, which the report discloses." />
          </Panel>
          <Panel title="How much is left (Kayad)">
            <Metric label="Map vs ceiling" value={u.KAYAD.B0.rho_median} digits={2} note="Combine noise caps the achievable ρ at 0.72–0.94 on this field." />
          </Panel>
        </div>
      </Container>
    </section>
  )
}

/* ------------------------------------------------------------------ */

function FieldLevel({ ev }: { ev: Ev }) {
  const sm = ev.stress_models
  const p3 = ev.early_warning_field
  const fy = ev.field_years
  const noT4 = ev.stress_sensitivity['A0|ohne_T4']
  const withinTr = ev.stress_sensitivity['A_roh|KBS_rho_innerhalb_Behandlung_Jahr']
  const rows: CiRow[] = [
    { label: 'Stress score (raw)', sub: 'shortfall below healthy reference', value: sm.A_roh.pr_auc, lo: sm.A_roh.pr_auc_lo, hi: sm.A_roh.pr_auc_hi, emphasis: true, color: tokens.maize },
    { label: 'Risk model A0', sub: 'logistic regression on the score', value: sm.A0.pr_auc, lo: sm.A0.pr_auc_lo, hi: sm.A0.pr_auc_hi, color: tokens.maize },
    ...(['M1', 'M2', 'M3', 'M4'] as const).map((k) => {
      const a = ev.ablation.find((r) => r.feature_set === k)!
      const names = { M1: '+ radar (Sentinel-1)', M2: '+ surface temperature, ET', M3: '+ degree-day time axis', M4: '+ green-up date' }
      return { label: `A0 ${names[k]}`, sub: 'pre-registered ablation', value: a.pr_auc, lo: a.pr_auc_lo, hi: a.pr_auc_hi, color: tokens.ink3 }
    }),
    ...(() => {
      const last = p3.find((r) => r.cutoff === '09-01')!
      const a = last.a_threshold_on_pred_RY as { pr_auc: number; pr_auc_lo: number; pr_auc_hi: number }
      const b = last.b_direct_classifier as { pr_auc: number; pr_auc_lo: number; pr_auc_hi: number }
      return [
        { label: 'Learned yield model + threshold', sub: 'round 3 ridge', value: a.pr_auc, lo: a.pr_auc_lo, hi: a.pr_auc_hi, color: tokens.ink3 },
        { label: 'Direct classifier', sub: 'trained on “at risk”', value: b.pr_auc, lo: b.pr_auc_lo, hi: b.pr_auc_hi, color: tokens.ink3 },
      ]
    })(),
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
          <p>Score {fmtSigned(r.score, 3)} · relative yield {fmt(r.ry, 2)}</p>
          <p className={r.alarm ? 'text-rust' : 'text-ink-3'}>{r.alarm ? 'Alarm' : 'No alarm'}{r.risk ? ' · at risk' : ''}</p>
        </>
      ),
    }))
  const cats = p3.map((r) => CUT_LABEL(r.cutoff))
  const series = [
    { key: 'reference_stress_score', label: 'Stress score', color: tokens.maize },
    { key: 'a_threshold_on_pred_RY', label: 'Learned model + threshold', color: tokens.water },
    { key: 'b_direct_classifier', label: 'Direct classifier', color: tokens.ink3, dashed: true },
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
        <SectionHeader
          eyebrow="2 · Whole fields"
          title="The simplest score beats every learned model — with a catch."
          lede="A field-year counts as at risk when it yields at least 15 % below its own normal. Evaluated only on unseen field groups and years (LOFYO), 89 field-years from 8 site-years."
          aside={<StrengthBadge strength="limited" />}
        />
        <div className="mt-12 grid gap-5 lg:grid-cols-2">
          <Panel title={`PR-AUC on 1 September · chance = ${fmt(sm.A0.prevalence, 2)}`} source="results/2026-10-16_feinjust_ablation/metrics.json, metrics.csv · results/2026-10-16_round3/phase3.json">
            <CiRows rows={rows} domain={[0, 1]} reference={sm.A0.prevalence} referenceLabel="chance" />
          </Panel>
          <Panel title="Stress score vs measured relative yield, 89 field-years" source="results/2026-10-16_feinjust_ablation/oof.parquet (A_roh) · ranking.csv">
            <Scatter points={pts} xLabel="Stress score (more negative = further below reference)" yLabel="Relative yield" height={330} yDomain={[0.2, 1.6]} hLines={[{ v: 0.85, label: 'at risk below 0.85', color: tokens.rust }]} xFmt={(v) => fmt(v, 2)} />
            <Legend
              className="mt-3"
              items={[
                { label: 'BARC', color: tokens.water, kind: 'dot' },
                { label: 'KBS', color: tokens.sage, kind: 'dot' },
                { label: 'KBS organic T4', color: tokens.maize, kind: 'dot' },
                { label: 'Hollow = no alarm', color: tokens.ink3, kind: 'line' },
              ]}
            />
          </Panel>
        </div>
        <div className="mt-5 grid gap-5 lg:grid-cols-[1.3fr_1fr]">
          <Panel title="How early? PR-AUC by forecast date" source="results/2026-10-16_round3/phase3.json · score needs observed dekads from June">
            <LineCi categories={cats} series={series} yDomain={[0, 1]} hLines={[{ v: sm.A0.prevalence, label: 'chance', color: tokens.ink4 }]} />
            <Legend className="mt-3" items={series.map((s) => ({ label: s.label, color: s.color, kind: s.dashed ? 'dash' : 'line' }))} />
          </Panel>
          <Panel title="The catch: management, not only stress">
            <div className="flex flex-col gap-6">
              <Metric label="PR-AUC without organic plots (T4)" value={noT4?.pr_auc} ci={[noT4?.pr_auc_lo, noT4?.pr_auc_hi]} n={`${noT4?.n} · chance ${fmt(noT4?.prevalence, 2)}`} tone="maize" />
              <Metric label="ρ between plots with equal management" value={withinTr?.median} digits={2} n={`${withinTr?.n_groups} treatment-years`} tone="rust" />
              <p className="text-[13.5px] leading-relaxed text-ink-2">
                The score flags the late-sown organic plots every year — also in 2020, when they yielded normally. Without them, the interval
                includes chance. An alarm therefore means “curve below reference”, not a diagnosis.
              </p>
            </div>
          </Panel>
        </div>
        <div className="mt-5 grid gap-5 md:grid-cols-3">
          <Panel title="Alarm threshold">
            <Metric label="False-alarm rate" value={a.alarm_fpr} digits={2} note="Conformal threshold, set for at most 20 % false alarms among not-at-risk fields." />
          </Panel>
          <Panel title="Alarms that were right">
            <Metric label="Precision" value={a.alarm_precision} digits={2} note={`${Math.round(a.alarm_precision * a.n_alarm)} of ${a.n_alarm} alarms were at-risk field-years.`} />
          </Panel>
          <Panel title="At-risk fields found">
            <Metric label="Recall" value={a.alarm_recall} digits={2} note={`${a.main_phase_alarms.Juli} of ${a.n_alarm} alarms came mainly from July.`} />
          </Panel>
        </div>
      </Container>
    </section>
  )
}

/* ------------------------------------------------------------------ */

function YearModels({ ev }: { ev: Ev }) {
  const [kind, setKind] = useState<'ridge' | 'lgbm'>('ridge')
  const fam = ev.phase2_models.filter((r) => r.cutoff === '09-01' && r.basis === 'S2' && (r.kind === kind || r.model === 'B1'))
  const famRows: CiRow[] = fam
    .sort((a, b) => b.rho - a.rho)
    .map((r) => ({ label: MODEL_NAMES[r.model] ?? r.model, sub: `skill vs normal year ${fmtSigned(r.skill_b0, 2)}`, value: r.rho, lo: r.rho_lo, hi: r.rho_hi, color: r.model === 'B1' ? tokens.ink3 : r.skill_b0 > 0 ? tokens.sage : tokens.water }))
  const stageRows: CiRow[] = ev.phase4_stages.map((s) => ({ label: s.stage, sub: `${s.model} · ${s.kind} · ${Object.values(s.criteria).filter(Boolean).length}/4 criteria`, value: s.rho, lo: s.rho_lo, hi: s.rho_hi, color: tokens.water }))
  return (
    <section id="year-models" className="scroll-mt-20 py-20">
      <Container>
        <SectionHeader
          eyebrow="3 · Year-to-year at field level"
          title="Predicting how much worse a year gets: not strong enough."
          lede="Models tried to estimate the relative yield of an unseen field in an unseen year. With only 8–11 independent site-years, none beat the simple assumption of a normal year on error. The pre-registered verdict was “not strong enough”, so this model was never frozen."
          aside={<StrengthBadge strength="failed" />}
        />
        <div className="mt-12 grid gap-5 lg:grid-cols-2">
          <Panel title="Spearman ρ on 1 Sep, Sentinel-2 features, LOFYO" source="results/2026-10-16_phase2/metrics.csv · 89 field-years / 8 site-years">
            <div className="mb-5"><Tabs size="sm" label="Model kind" value={kind} onChange={setKind} items={[{ value: 'ridge', label: 'Ridge' }, { value: 'lgbm', label: 'LightGBM' }]} /></div>
            <CiRows rows={famRows} domain={[-0.6, 0.8]} reference={0} />
          </Panel>
          <Panel title="Pre-registered rounds against the four criteria" source="results/2026-10-16_{phase2,round1,round2,round3}/criteria*.json">
            <CiRows rows={stageRows} domain={[-0.6, 0.8]} reference={0.4} referenceLabel="criterion ρ ≥ 0.4" />
            <ul className="mt-5 grid gap-2 text-[13px] text-ink-2">
              {['Beats both baselines from 1 Aug', 'ρ ≥ 0.4 on 1 Sep', 'Transfers between both US sites', 'Label shuffle falls to baseline'].map((c, i) => {
                const passed = ev.phase4_stages.map((s) => Object.values(s.criteria)[i])
                return (
                  <li key={c} className="flex items-center justify-between gap-3 border-b border-[var(--line)] pb-2 last:border-0">
                    <span>{c}</span>
                    <span className="flex gap-1.5">{passed.map((p, j) => <span key={j} className={`size-2.5 rounded-full ${p ? 'bg-sage' : 'bg-rust/70'}`} title={ev.phase4_stages[j].stage} />)}</span>
                  </li>
                )
              })}
            </ul>
          </Panel>
        </div>
        <p className="mt-6 max-w-[760px] text-[14px] leading-relaxed text-ink-3">
          Why: with the year already seen, the same model reaches ρ 0.65 — it learns “which year is this”, not “how is this field
          doing”. Every model also falls to baseline when yields are shuffled, so the weak result is not hiding leakage.
        </p>
      </Container>
    </section>
  )
}

/* ------------------------------------------------------------------ */

function Regional({ ev }: { ev: Ev }) {
  const cut = ev.eu_cutoffs
  const last = cut.find((c) => c.cutoff === '09-01')!
  const pts = useMemo(() => ev.eu_scatter.map(([y, p]) => ({ x: y, y: p, color: tokens.water, r: 2.2 })), [ev])
  const countries = Object.entries(ev.eu_per_country)
    .filter(([, v]) => v.n >= 50)
    .sort((a, b) => b[1].n - a[1].n)
  const baseRows = [
    { label: 'RMSE', model: last.rmse.value!, normal: last.baselines.normal_year.rmse.value!, trend: last.baselines.trend.rmse.value! },
    { label: 'MAE', model: last.mae.value!, normal: last.baselines.normal_year.mae.value!, trend: last.baselines.trend.mae.value! },
  ]
  const noDe = (ev.eu_controls.without_DE_eval as { metrics: { model_spearman: { value: number } } }).metrics.model_spearman.value
  return (
    <section id="regional" className="scroll-mt-20 py-20">
      <Container>
        <SectionHeader
          eyebrow="4 · Regions, EU"
          title="A small, certain signal about bad years — frozen before Austria."
          lede="LightGBM on CY-Bench maize statistics from 16 EU countries, Austria excluded. Each country is predicted by a model that never saw it (leave-one-country-out). Target: the region’s yield relative to its last five years."
          aside={<StrengthBadge strength="certain-small" />}
        />
        <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <Panel title="Rank correlation"><Metric label="Spearman ρ, 1 Sep" value={last.spearman.value} ci={[last.spearman.lo, last.spearman.hi]} n={last.n.toLocaleString('en-US')} tone="water" size="lg" /></Panel>
          <Panel title="Better than a normal year"><Metric label="Skill (RMSE)" value={last.skill_vs_normal.value} ci={[last.skill_vs_normal.lo, last.skill_vs_normal.hi]} size="lg" /></Panel>
          <Panel title="Explained variance"><Metric label="R²" value={last.r2.value} ci={[last.r2.lo, last.r2.hi]} size="lg" /></Panel>
          <Panel title="Within one year"><Metric label="Mean ρ between regions" value={last.within_year.value} ci={[last.within_year.lo, last.within_year.hi]} size="lg" note={`Across years: ρ ${fmt(last.yearly_mean_spearman, 2)} — it mostly learns the year.`} /></Panel>
        </div>
        <div className="mt-5 grid gap-5 lg:grid-cols-2">
          <Panel title="Model vs baselines on 1 Sep (lower is better)" source="results/2026-10-16_cybench_eu/metrics.json · pooled">
            <PairedBars rows={baseRows.map((r) => ({ label: r.label, a: r.model, b: r.normal }))} a={{ label: 'Model', color: tokens.water }} b={{ label: 'Normal year', color: tokens.ink4 }} format={(v) => fmt(v, 3)} />
            <p className="mt-3 text-[13px] text-ink-3">Linear trend baseline: RMSE {fmt(last.baselines.trend.rmse.value, 3)}, MAE {fmt(last.baselines.trend.mae.value, 3)}. The model beats both, by a small margin.</p>
            <Legend className="mt-4" items={[{ label: 'Model', color: tokens.water, kind: 'bar' }, { label: 'Normal year (YAS = 1)', color: tokens.ink4, kind: 'bar' }]} />
          </Panel>
          <Panel title="How early? Metrics by forecast date" source="results/2026-10-16_cybench_eu/metrics.json">
            <LineCi
              categories={cut.map((c) => CUT_LABEL(c.cutoff))}
              yDomain={[-0.1, 0.5]}
              series={[
                { label: 'Spearman ρ', color: tokens.water, values: cut.map((c) => ({ v: c.spearman.value, lo: c.spearman.lo, hi: c.spearman.hi })) },
                { label: 'ρ within year', color: tokens.sage, values: cut.map((c) => ({ v: c.within_year.value, lo: c.within_year.lo, hi: c.within_year.hi })) },
                { label: 'Skill vs normal', color: tokens.maize, values: cut.map((c) => ({ v: c.skill_vs_normal.value, lo: c.skill_vs_normal.lo, hi: c.skill_vs_normal.hi })) },
              ]}
            />
            <Legend className="mt-3" items={[{ label: 'Spearman ρ', color: tokens.water }, { label: 'ρ within year', color: tokens.sage }, { label: 'Skill vs normal year', color: tokens.maize }]} />
          </Panel>
          <Panel title="Predicted vs actual relative yield, 1 Sep (1 600 of 8 371)" source="results/2026-10-16_cybench_eu/predictions_loco.parquet · random sample, seed 42">
            <Scatter points={pts} xLabel="Actual (yield / 5-year normal)" yLabel="Predicted" xDomain={[0.2, 1.8]} yDomain={[0.6, 1.4]} diagonal height={320} opacity={0.35} xFmt={(v) => fmt(v, 1)} yFmt={(v) => fmt(v, 1)} />
            <p className="mt-3 text-[13px] text-ink-3">Predictions stay close to 1: the model is cautious and under-reacts to extreme years.</p>
          </Panel>
          <Panel title="Error distribution (predicted − actual)" source="results/2026-10-16_cybench_eu/predictions_loco.parquet · all 8 371">
            <Histogram edges={ev.eu_residuals.edges} series={[{ label: 'Model', counts: ev.eu_residuals.model, color: tokens.water }, { label: 'Normal year', counts: ev.eu_residuals.normal_year, color: tokens.ink3 }]} xLabel="Residual" height={230} />
            <Legend className="mt-3" items={[{ label: 'Model', color: tokens.water }, { label: 'Normal year', color: tokens.ink3 }]} />
          </Panel>
          <Panel title="Mean absolute error by actual yield range" source="results/2026-10-16_cybench_eu/predictions_loco.parquet">
            <PairedBars rows={ev.eu_by_range.map((r) => ({ label: r.bin, sub: `n = ${r.n}`, a: r.mae_model, b: r.mae_normal }))} a={{ label: 'Model', color: tokens.water }} b={{ label: 'Normal year', color: tokens.ink4 }} format={(v) => fmt(v, 2)} />
            <p className="mt-3 text-[13px] text-ink-3">The gain is in the bad and the very good years; in normal years the baseline is naturally hard to beat.</p>
          </Panel>
          <Panel title="By country (≥ 50 region-years), Spearman ρ" source="results/2026-10-16_cybench_eu/metrics.json · per_country">
            <PairedBars rows={countries.map(([c, v]) => ({ label: c, sub: `n = ${v.n}`, a: Math.max(0, v.spearman), b: Math.max(0, v.skill_vs_yas1) }))} a={{ label: 'ρ', color: tokens.water }} b={{ label: 'Skill', color: tokens.maize }} format={(v) => fmt(v, 2)} />
            <p className="mt-3 text-[13px] text-ink-3">Negative values shown as 0. Without Germany (31 % of the data) ρ is {fmt(noDe, 2)}.</p>
          </Panel>
        </div>
        <Reveal className="mt-5 panel p-6 text-[13.5px] leading-relaxed text-ink-2">
          <p className="eyebrow mb-3">Disclosed in the freeze protocol</p>
          The hyper-parameter grid was widened once after a pilot run, when first EU results were visible. EU numbers are therefore slightly
          optimistic; the Austria test is not affected. Model files and test rules are frozen with SHA-256 checksums (tag {ev.eu_meta.freeze},
          commit {ev.eu_meta.commit}).
        </Reveal>
      </Container>
    </section>
  )
}

/* ------------------------------------------------------------------ */

function Austria({ ev }: { ev: Ev }) {
  const at = ev.austria!
  const cuts = Object.keys(at.cutoffs)
  const last = at.cutoffs['09-01']
  const ndvi = last['V2-baseline_NDVI']
  const rows: CiRow[] = [
    { label: 'Stress score · site-years', sub: `Upper Austria trials · n = ${last['V2-A_stress_score'].n}`, value: last['V2-A_stress_score'].rho, lo: last['V2-A_stress_score'].lo, hi: last['V2-A_stress_score'].hi, emphasis: true, color: tokens.maize },
    ...(ndvi ? [{ label: 'Plain NDVI · same site-years', sub: 'no learning, comparison value', value: ndvi.rho, lo: ndvi.lo, hi: ndvi.hi, color: tokens.ink3 }] : []),
    { label: 'EU model · Austrian states', sub: `region-years · n = ${last.V1_regional_model.n}`, value: last.V1_regional_model.rho, lo: last.V1_regional_model.lo, hi: last.V1_regional_model.hi, color: tokens.water },
    { label: 'EU model · trial sites', sub: `n = ${last['V2-B_regional_model'].n}`, value: last['V2-B_regional_model'].rho, lo: last['V2-B_regional_model'].lo, hi: last['V2-B_regional_model'].hi, color: tokens.ink3 },
  ]
  const r = at.retrain?.['09-01']
  return (
    <section id="austria" className="scroll-mt-20 py-20">
      <Container>
        <SectionHeader
          eyebrow="5 · Austria, first test (exploratory)"
          title="Frozen models in Austria: the years rank, the fields do not yet."
          lede="Run once under the protocol frozen as freeze-at-1, without choosing a winner. Exploratory, because no field model had passed the “strong enough” criterion. The local test covers Upper Austria only: the Styrian trial sites had no variety trials and were excluded by the pre-registered filter."
          aside={<StrengthBadge strength="limited" />}
        />
        <div className="mt-12 grid gap-5 lg:grid-cols-[1.2fr_1fr]">
          <Panel title="Spearman ρ on 1 September, 95 % CI (clusters = years)" source="results/2026-10-17_at_test/metrics.json · reports/at_test_ergebnis.md">
            <CiRows rows={rows} domain={[-1, 1]} reference={0} />
          </Panel>
          <Panel title="Stress score by forecast date">
            <LineCi
              categories={cuts.map(CUT_LABEL)}
              yDomain={[-0.5, 1]}
              series={[
                { label: 'Stress score · sites', color: tokens.maize, values: cuts.map((c) => ({ v: at.cutoffs[c]['V2-A_stress_score'].rho, lo: at.cutoffs[c]['V2-A_stress_score'].lo, hi: at.cutoffs[c]['V2-A_stress_score'].hi })) },
                { label: 'EU model · states', color: tokens.water, values: cuts.map((c) => ({ v: at.cutoffs[c].V1_regional_model.rho, lo: at.cutoffs[c].V1_regional_model.lo, hi: at.cutoffs[c].V1_regional_model.hi })) },
              ]}
            />
            <Legend className="mt-3" items={[{ label: 'Stress score · Upper Austria sites', color: tokens.maize }, { label: 'EU model · Austrian states', color: tokens.water }]} />
          </Panel>
        </div>
        <div className="mt-5 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          <Panel title="Within one year">
            <Metric label="Median ρ between sites" value={last['V2-A_within_year'].median} digits={2} tone="rust" note={`${last['V2-A_within_year'].n_groups} years. The score does not rank sites against each other within a year.`} />
          </Panel>
          <Panel title="Within one site">
            <Metric label="Median ρ across years" value={last['V2-A_within_site'].median} digits={2} note={`${last['V2-A_within_site'].n_groups} sites. The signal is the difference between years.`} />
          </Panel>
          <Panel title="EU model error vs normal year">
            <Metric label="RMSE model − normal" value={last.V1_regional_model.rmse_diff} digits={3} ci={[last.V1_regional_model.rmse_diff_lo, last.V1_regional_model.rmse_diff_hi]} note="Positive = worse. Ranks the years, but not more accurate than assuming a normal year." />
          </Panel>
          {r && (
            <Panel title="Add-on: two-number recalibration">
              <Metric label="RMSE frozen → recalibrated" value={r.pred_r1.rmse} digits={3} prefix={`${fmt(r.pred_r0.rmse, 3)} → `} note={`With Austrian yields, leave-one-year-out, n = ${r.pred_r1.n}. A hint, not proof — and no longer a frozen model.`} />
            </Panel>
          )}
        </div>
        <Reveal className="mt-5 panel p-6 text-[13.5px] leading-relaxed text-ink-2">
          <p className="eyebrow mb-3">What may not be claimed</p>
          That the stress score does more than plain NDVI; that it separates fields or sites within a year; that the result holds for Styria;
          anything at field level — a field-level test (V3) still needs Austrian field yields.
        </Reveal>
      </Container>
    </section>
  )
}
