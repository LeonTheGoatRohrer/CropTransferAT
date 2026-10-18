import { useMemo, useState } from 'react'
import type { Evidence as Ev } from '../api/types'
import { CiRows, Histogram, LineCi, PairedBars, Scatter, Strip, type CiRow } from '../components/charts/Stats'
import { Legend } from '../components/charts/core'
import { StrengthBadge, type Strength } from '../components/ui/Badge'
import { Metric } from '../components/ui/Metric'
import { Reveal } from '../components/ui/Reveal'
import { Backdrop } from '../components/ui/Backdrop'
import { Container, SectionHeader, Source } from '../components/ui/Section'
import { ErrorNote, Skeleton } from '../components/ui/States'
import { Tabs } from '../components/ui/Tabs'
import { keepGreek } from '../components/ui/Text'
import { tokens } from '../lib/color'
import { fmt, fmtCi, fmtInt, fmtPct, fmtSigned } from '../lib/format'
import { useResource } from '../lib/useResource'
import { getEvidence } from '../services/evidenceService'

const CUT_LABEL = (c: string) => {
  const [m, d] = c.split('-').map(Number)
  return `${d}. ${['', '', '', '', '', '', 'Jun', 'Jul', 'Aug', 'Sep'][m]}`
}

const MODEL_NAMES: Record<string, string> = {
  B1: 'Baseline B1 · nur NDVI-Maximum',
  'M-S': 'Satellit',
  'M-W': 'Wetter',
  'M-B': 'Boden und Gelände',
  'M-B+': 'Boden + SSURGO',
  'M-WB': 'Wetter + Boden',
  'M-SW': 'Satellit + Wetter',
  'M-SB': 'Satellit + Boden',
  'M-alle': 'Satellit + Wetter + Boden',
}

/** Display names for model kinds from evidence.json (values stay as logic keys). */
const KIND_LABEL: Record<string, string> = { ridge: 'Ridge', lgbm: 'LightGBM' }

/** Yield-range bins arrive from evidence.json with decimal points; show them with a decimal comma. */
const binLabel = (b: string) => b.replace(/(\d)\.(\d)/g, '$1,$2')

export default function Evidence() {
  const ev = useResource(getEvidence, 'evidence')
  return (
    <>
      <section className="relative isolate overflow-hidden pt-36 pb-16">
        <Backdrop name="belege-orbit" />
        <Container>
          <Reveal>
            <p className="eyebrow mb-5">Belege · Benchmarks</p>
            <h1 className="max-w-[900px] text-balance text-[clamp(2.6rem,6vw,4.6rem)] leading-[0.98] tracking-[-0.04em]">Jede Aussage – mit dem Test, den sie bestehen musste.</h1>
            <p className="mt-6 max-w-[680px] text-pretty text-[17px] leading-relaxed text-ink-2">
              Alle Zahlen unten stammen direkt aus den Ergebnisdateien des Projekts. Zu jeder gibt es ein 95-%-Konfidenzintervall aus einem
              Cluster-Bootstrap und die Zahl der unabhängigen Einheiten dahinter. Bei der Validierung werden immer ganze Felder, Jahre oder
              Länder zurückgehalten.
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
    { q: 'Wo im Feld fehlt Ertrag?', metric: 'Median Spearman ρ (NDVI ggü. Pixel-Ertrag)', value: fmt(b0.rho_median, 2), ci: fmtCi(b0.rho_ci?.[0], b0.rho_ci?.[1]), n: `${b0.n_fy} Feld-Jahre · ${b0.n_clusters} Felder`, baseline: 'nur Position: ρ 0,03', strength: 'robust', href: '#within-field' },
    { q: 'Welche Feld-Jahre sind gefährdet?', metric: 'PR-AUC am 1. Sep', value: fmt(a0.pr_auc, 2), ci: fmtCi(a0.pr_auc_lo, a0.pr_auc_hi), n: `${a0.n} Feld-Jahre · 8 Standort-Jahre`, baseline: `Zufallsniveau ${fmt(a0.prevalence, 2)}`, strength: 'limited', href: '#field-level' },
    { q: 'Wie viel schlechter wird das Jahr dieses Feldes?', metric: 'Spearman ρ, beste vorab festgelegte Runde', value: fmt(st.rho, 2), ci: fmtCi(st.rho_lo, st.rho_hi), n: `${st.n} Feld-Jahre · ${st.clusters} Standort-Jahre`, baseline: 'schlägt „Normaljahr“ nicht', strength: 'failed', href: '#year-models' },
    { q: 'Welche Jahre sind für eine Region schlechter?', metric: 'Spearman ρ am 1. Sep (EU, LOCO)', value: fmt(eu.spearman.value, 2), ci: fmtCi(eu.spearman.lo, eu.spearman.hi), n: `${fmtInt(eu.n)} Region-Jahre · ${eu.countries} Länder`, baseline: `Skill ${fmt(eu.skill_vs_normal.value, 2)} ggü. Normaljahr`, strength: 'certain-small', href: '#regional' },
  ]
  const at = ev.austria?.cutoffs['09-01']?.['V2-A_stress_score']
  if (at) rows.push({ q: 'Lässt es sich auf Österreich übertragen?', metric: 'Spearman ρ, eingefrorener Stress-Score, 1. Sep', value: fmt(at.rho, 2), ci: fmtCi(at.lo, at.hi), n: `${at.n} Standort-Jahre · ${at.clusters} Jahre`, baseline: `einfacher NDVI ρ ${fmt(ev.austria?.cutoffs['09-01']['V2-baseline_NDVI']?.rho, 2)}`, strength: 'limited', href: '#austria' })
  return (
    <section className="pb-12">
      <Container>
        <Reveal className="panel overflow-x-auto">
          <table className="w-full min-w-[860px] text-left text-[13.5px]">
            <thead>
              <tr className="border-b border-[var(--line)] text-ink-3">
                {['Frage', 'Metrik', 'Wert', '95-%-KI', 'Einheiten', 'Verglichen mit', 'Urteil'].map((h) => (
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
    { label: 'Modell M1 · trainierte Ridge', sub: 'NDVI/NDRE-Fenster, Leave-one-field-out', value: e.BARC.M1.rho_median, lo: e.BARC.M1.rho_ci?.[0], hi: e.BARC.M1.rho_ci?.[1], emphasis: true, color: tokens.sage },
    { label: 'Regel B0 · roher NDVI', sub: '10. Jul – 18. Aug, ohne Training', value: u.BARC.B0.rho_median, lo: u.BARC.B0.rho_ci?.[0], hi: u.BARC.B0.rho_ci?.[1], color: tokens.sage },
    { label: 'Regel B1 · NDVI am Maximum', sub: 'Fenster um das Kurvenmaximum', value: u.BARC.B1.rho_median, lo: u.BARC.B1.rho_ci?.[0], hi: u.BARC.B1.rho_ci?.[1] },
    { label: 'M1, an anderen Standorten trainiert', sub: 'Leave-one-site-out', value: l.BARC.M1.rho_median, lo: l.BARC.M1.rho_ci?.[0], hi: l.BARC.M1.rho_ci?.[1] },
    { label: 'Nur Position (Kontrolle)', sub: 'Zellkoordinaten, kein Satellit', value: e.BARC.KRAUM.rho_median, lo: e.BARC.KRAUM.rho_ci?.[0], hi: e.BARC.KRAUM.rho_ci?.[1], color: tokens.ink3 },
  ]
  const groups = (model: string, scheme: string) =>
    [
      { key: 'BARC', label: 'BARC', sub: 'Maryland · 41', color: tokens.sage },
      { key: 'KAYAD', label: 'Kayad', sub: 'Italien · 3', color: tokens.maize },
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
          eyebrow="1 · Innerhalb des Feldes"
          title="Der NDVI im Hochsommer findet die schwachen Zonen."
          lede="Je Feld-Jahr werden die 10-m-Zellen nach NDVI gereiht und mit der Ertragskarte des Mähdreschers verglichen. Ein trainiertes Modell bringt etwas mehr; die einfache Regel trägt bereits den Großteil des Signals."
          aside={<StrengthBadge strength="robust" />}
        />
        <div className="mt-12 grid gap-5 lg:grid-cols-[1.15fr_1fr]">
          <Panel title="Median-ρ über 41 BARC-Feld-Jahre, 95-%-KI" source="results/2026-10-17_innerfeld/metrics.json · Schemata E (je Standort) und L (Leave-one-site-out)">
            <CiRows rows={rows} domain={[-0.4, 1]} reference={0} />
          </Panel>
          <Panel title="Jeder Punkt ist ein Feld-Jahr · Regel B0" source="results/2026-10-17_innerfeld/per_fy.csv">
            <Strip groups={groups('B0', 'untrained')} domain={[-0.2, 1]} xLabel="Spearman ρ" reference={0} />
            <p className="mt-4 text-[13px] leading-relaxed text-ink-3">{nPos} von {b0All.length} Feld-Jahren sind positiv. Nur BARC hat genug Feld-Jahre für ein Urteil; Italien und Colorado zeigen in dieselbe Richtung.</p>
          </Panel>
        </div>
        <div className="mt-5 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          <Panel title="Markiertes Viertel ist wirklich schwach">
            <Metric label="Median-Präzision" value={map.median_precision} digits={2} n={`${map.n_fy} Feld-Jahre`} note={`gegenüber ${fmtPct(map.median_prevalence)} ertragsschwachen Zellen insgesamt`} />
          </Panel>
          <Panel title="Besser als Zufall">
            <Metric label="Median-Lift" value={map.median_lift} digits={1} prefix="× " note={`${fmtPct(map.median_recall)} der ertragsschwachen Zellen werden gefunden`} />
          </Panel>
          <Panel title="Label-Shuffle-Kontrolle">
            <Metric label="Mittleres ρ, gemischte Erträge" value={shuffle.mean} digits={2} note="20 Wiederholungen. Fällt wie erwartet auf null; einzelne Läufe erreichen ±0,45, was der Bericht offenlegt." />
          </Panel>
          <Panel title="Wie viel Luft bleibt (Kayad)">
            <Metric label="Karte ggü. Obergrenze" value={u.KAYAD.B0.rho_median} digits={2} note="Das Messrauschen des Mähdreschers begrenzt das erreichbare ρ auf diesem Feld auf 0,72–0,94." />
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
    { label: 'Stress-Score (roh)', sub: 'Rückstand unter der gesunden Referenz', value: sm.A_roh.pr_auc, lo: sm.A_roh.pr_auc_lo, hi: sm.A_roh.pr_auc_hi, emphasis: true, color: tokens.maize },
    { label: 'Risikomodell A0', sub: 'logistische Regression auf den Score', value: sm.A0.pr_auc, lo: sm.A0.pr_auc_lo, hi: sm.A0.pr_auc_hi, color: tokens.maize },
    ...(['M1', 'M2', 'M3', 'M4'] as const).map((k) => {
      const a = ev.ablation.find((r) => r.feature_set === k)!
      const names = { M1: '+ Radar (Sentinel-1)', M2: '+ Oberflächentemperatur, ET', M3: '+ Gradtag-Zeitachse', M4: '+ Ergrünungsdatum' }
      return { label: `A0 ${names[k]}`, sub: 'vorab festgelegte Ablation', value: a.pr_auc, lo: a.pr_auc_lo, hi: a.pr_auc_hi, color: tokens.ink3 }
    }),
    ...(() => {
      const last = p3.find((r) => r.cutoff === '09-01')!
      const a = last.a_threshold_on_pred_RY as { pr_auc: number; pr_auc_lo: number; pr_auc_hi: number }
      const b = last.b_direct_classifier as { pr_auc: number; pr_auc_lo: number; pr_auc_hi: number }
      return [
        { label: 'Gelerntes Ertragsmodell + Schwelle', sub: 'Ridge aus Runde 3', value: a.pr_auc, lo: a.pr_auc_lo, hi: a.pr_auc_hi, color: tokens.ink3 },
        { label: 'Direkter Klassifikator', sub: 'trainiert auf „gefährdet“', value: b.pr_auc, lo: b.pr_auc_lo, hi: b.pr_auc_hi, color: tokens.ink3 },
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
          <p>Score {fmtSigned(r.score, 3)} · relativer Ertrag {fmt(r.ry, 2)}</p>
          <p className={r.alarm ? 'text-rust' : 'text-ink-3'}>{r.alarm ? 'Alarm' : 'Kein Alarm'}{r.risk ? ' · gefährdet' : ''}</p>
        </>
      ),
    }))
  const cats = p3.map((r) => CUT_LABEL(r.cutoff))
  const series = [
    { key: 'reference_stress_score', label: 'Stress-Score', color: tokens.maize },
    { key: 'a_threshold_on_pred_RY', label: 'Gelerntes Modell + Schwelle', color: tokens.water },
    { key: 'b_direct_classifier', label: 'Direkter Klassifikator', color: tokens.ink3, dashed: true },
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
          eyebrow="2 · Ganze Felder"
          title="Der einfachste Score schlägt jedes gelernte Modell – mit einem Haken."
          lede="Ein Feld-Jahr gilt als gefährdet, wenn sein Ertrag mindestens 15 % unter seinem eigenen Normalertrag liegt. Ausgewertet nur auf ungesehenen Feldgruppen und Jahren (LOFYO): 89 Feld-Jahre aus 8 Standort-Jahren."
          aside={<StrengthBadge strength="limited" />}
        />
        <div className="mt-12 grid gap-5 lg:grid-cols-2">
          <Panel title={`PR-AUC am 1. September · Zufallsniveau = ${fmt(sm.A0.prevalence, 2)}`} source="results/2026-10-16_feinjust_ablation/metrics.json, metrics.csv · results/2026-10-16_round3/phase3.json">
            <CiRows rows={rows} domain={[0, 1]} reference={sm.A0.prevalence} referenceLabel="Zufallsniveau" />
          </Panel>
          <Panel title="Stress-Score ggü. gemessenem relativem Ertrag, 89 Feld-Jahre" source="results/2026-10-16_feinjust_ablation/oof.parquet (A_roh) · ranking.csv">
            <Scatter points={pts} xLabel="Stress-Score (negativer = weiter unter der Referenz)" yLabel="Relativer Ertrag" height={330} yDomain={[0.2, 1.6]} hLines={[{ v: 0.85, label: 'gefährdet unter 0,85', color: tokens.rust }]} xFmt={(v) => fmt(v, 2)} />
            <Legend
              className="mt-3"
              items={[
                { label: 'BARC', color: tokens.water, kind: 'dot' },
                { label: 'KBS', color: tokens.sage, kind: 'dot' },
                { label: 'KBS Bio-Parzellen T4', color: tokens.maize, kind: 'dot' },
                { label: 'Hohl = kein Alarm', color: tokens.ink3, kind: 'line' },
              ]}
            />
          </Panel>
        </div>
        <div className="mt-5 grid gap-5 lg:grid-cols-[1.3fr_1fr]">
          <Panel title="Wie früh? PR-AUC nach Prognosestichtag" source="results/2026-10-16_round3/phase3.json · der Score braucht beobachtete Dekaden ab Juni">
            <LineCi categories={cats} series={series} yDomain={[0, 1]} hLines={[{ v: sm.A0.prevalence, label: 'Zufallsniveau', color: tokens.ink4 }]} />
            <Legend className="mt-3" items={series.map((s) => ({ label: s.label, color: s.color, kind: s.dashed ? 'dash' : 'line' }))} />
          </Panel>
          <Panel title="Der Haken: Bewirtschaftung, nicht nur Stress">
            <div className="flex flex-col gap-6">
              <Metric label="PR-AUC ohne Bio-Parzellen (T4)" value={noT4?.pr_auc} ci={[noT4?.pr_auc_lo, noT4?.pr_auc_hi]} n={`${noT4?.n} · Zufallsniveau ${fmt(noT4?.prevalence, 2)}`} tone="maize" />
              <Metric label="ρ zwischen Parzellen mit gleicher Bewirtschaftung" value={withinTr?.median} digits={2} n={`${withinTr?.n_groups} Behandlungs-Jahre`} tone="rust" />
              <p className="text-[13.5px] leading-relaxed text-ink-2">
                Der Score markiert die spät gesäten Bio-Parzellen jedes Jahr – auch 2020, als sie normal erbrachten. Ohne sie schließt das
                Intervall das Zufallsniveau ein. Ein Alarm bedeutet daher „Kurve unter der Referenz“, keine Diagnose.
              </p>
            </div>
          </Panel>
        </div>
        <div className="mt-5 grid gap-5 md:grid-cols-3">
          <Panel title="Alarmschwelle">
            <Metric label="Fehlalarmrate" value={a.alarm_fpr} digits={2} note="Konforme Schwelle, festgelegt für höchstens 20 % Fehlalarme unter nicht gefährdeten Feldern." />
          </Panel>
          <Panel title="Zutreffende Alarme">
            <Metric label="Präzision" value={a.alarm_precision} digits={2} note={`${Math.round(a.alarm_precision * a.n_alarm)} von ${a.n_alarm} Alarmen waren gefährdete Feld-Jahre.`} />
          </Panel>
          <Panel title="Gefundene gefährdete Felder">
            <Metric label="Trefferquote (Recall)" value={a.alarm_recall} digits={2} note={`${a.main_phase_alarms.Juli} von ${a.n_alarm} Alarmen gingen vor allem auf den Juli zurück.`} />
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
    .map((r) => ({ label: MODEL_NAMES[r.model] ?? r.model, sub: `Skill ggü. Normaljahr ${fmtSigned(r.skill_b0, 2)}`, value: r.rho, lo: r.rho_lo, hi: r.rho_hi, color: r.model === 'B1' ? tokens.ink3 : r.skill_b0 > 0 ? tokens.sage : tokens.water }))
  const stageRows: CiRow[] = ev.phase4_stages.map((s) => ({ label: s.stage, sub: `${s.model} · ${KIND_LABEL[s.kind] ?? s.kind} · ${Object.values(s.criteria).filter(Boolean).length}/4 Kriterien`, value: s.rho, lo: s.rho_lo, hi: s.rho_hi, color: tokens.water }))
  return (
    <section id="year-models" className="scroll-mt-20 py-20">
      <Container>
        <SectionHeader
          eyebrow="3 · Von Jahr zu Jahr auf Feldebene"
          title="Vorhersagen, wie viel schlechter ein Jahr wird: nicht stark genug."
          lede="Die Modelle sollten den relativen Ertrag eines ungesehenen Feldes in einem ungesehenen Jahr schätzen. Mit nur 8–11 unabhängigen Standort-Jahren schlug beim Fehler keines die einfache Annahme eines Normaljahres. Das vorab festgelegte Urteil lautete „nicht stark genug“, daher wurde dieses Modell nie eingefroren."
          aside={<StrengthBadge strength="failed" />}
        />
        <div className="mt-12 grid gap-5 lg:grid-cols-2">
          <Panel title="Spearman ρ am 1. Sep, Sentinel-2-Merkmale, LOFYO" source="results/2026-10-16_phase2/metrics.csv · 89 Feld-Jahre / 8 Standort-Jahre">
            <div className="mb-5"><Tabs size="sm" label="Modellart" value={kind} onChange={setKind} items={[{ value: 'ridge', label: 'Ridge' }, { value: 'lgbm', label: 'LightGBM' }]} /></div>
            <CiRows rows={famRows} domain={[-0.6, 0.8]} reference={0} />
          </Panel>
          <Panel title="Vorab festgelegte Runden gegen die vier Kriterien" source="results/2026-10-16_{phase2,round1,round2,round3}/criteria*.json">
            <CiRows rows={stageRows} domain={[-0.6, 0.8]} reference={0.4} referenceLabel="Kriterium ρ ≥ 0,4" />
            <ul className="mt-5 grid gap-2 text-[13px] text-ink-2">
              {['Schlägt beide Baselines ab 1. Aug', 'ρ ≥ 0,4 am 1. Sep', 'Überträgt zwischen beiden US-Standorten', 'Label-Shuffle fällt auf Baseline-Niveau'].map((c, i) => {
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
          Warum: Kennt das Modell das Jahr bereits, erreicht es ρ 0,65 – es lernt „welches Jahr ist das“, nicht „wie geht es diesem
          Feld“. Mit gemischten Erträgen fällt zudem jedes Modell auf Baseline-Niveau; hinter dem schwachen Ergebnis steckt also kein Leakage.
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
          eyebrow="4 · Regionen, EU"
          title="Ein kleines, sicheres Signal für schlechte Jahre – eingefroren vor Österreich."
          lede="LightGBM auf CY-Bench-Maisstatistiken aus 16 EU-Ländern, ohne Österreich. Jedes Land wird von einem Modell vorhergesagt, das es nie gesehen hat (Leave-one-country-out). Zielgröße: der Ertrag der Region relativ zu ihren letzten fünf Jahren."
          aside={<StrengthBadge strength="certain-small" />}
        />
        <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <Panel title="Rangkorrelation"><Metric label="Spearman ρ, 1. Sep" value={last.spearman.value} ci={[last.spearman.lo, last.spearman.hi]} n={fmtInt(last.n)} tone="water" size="lg" /></Panel>
          <Panel title="Besser als ein Normaljahr"><Metric label="Skill (RMSE)" value={last.skill_vs_normal.value} ci={[last.skill_vs_normal.lo, last.skill_vs_normal.hi]} size="lg" /></Panel>
          <Panel title="Erklärte Varianz"><Metric label="R²" value={last.r2.value} ci={[last.r2.lo, last.r2.hi]} size="lg" /></Panel>
          <Panel title="Innerhalb eines Jahres"><Metric label="Mittleres ρ zwischen Regionen" value={last.within_year.value} ci={[last.within_year.lo, last.within_year.hi]} size="lg" note={`Über die Jahre: ρ ${fmt(last.yearly_mean_spearman, 2)} – es lernt vor allem das Jahr.`} /></Panel>
        </div>
        <div className="mt-5 grid gap-5 lg:grid-cols-2">
          <Panel title="Modell ggü. Baselines am 1. Sep (niedriger ist besser)" source="results/2026-10-16_cybench_eu/metrics.json · gepoolt">
            <PairedBars rows={baseRows.map((r) => ({ label: r.label, a: r.model, b: r.normal }))} a={{ label: 'Modell', color: tokens.water }} b={{ label: 'Normaljahr', color: tokens.ink4 }} format={(v) => fmt(v, 3)} />
            <p className="mt-3 text-[13px] text-ink-3">Lineare Trend-Baseline: RMSE {fmt(last.baselines.trend.rmse.value, 3)}, MAE {fmt(last.baselines.trend.mae.value, 3)}. Das Modell schlägt beide, wenn auch knapp.</p>
            <Legend className="mt-4" items={[{ label: 'Modell', color: tokens.water, kind: 'bar' }, { label: 'Normaljahr (YAS = 1)', color: tokens.ink4, kind: 'bar' }]} />
          </Panel>
          <Panel title="Wie früh? Metriken nach Prognosestichtag" source="results/2026-10-16_cybench_eu/metrics.json">
            <LineCi
              categories={cut.map((c) => CUT_LABEL(c.cutoff))}
              yDomain={[-0.1, 0.5]}
              series={[
                { label: 'Spearman ρ', color: tokens.water, values: cut.map((c) => ({ v: c.spearman.value, lo: c.spearman.lo, hi: c.spearman.hi })) },
                { label: 'ρ innerhalb des Jahres', color: tokens.sage, values: cut.map((c) => ({ v: c.within_year.value, lo: c.within_year.lo, hi: c.within_year.hi })) },
                { label: 'Skill ggü. Normaljahr', color: tokens.maize, values: cut.map((c) => ({ v: c.skill_vs_normal.value, lo: c.skill_vs_normal.lo, hi: c.skill_vs_normal.hi })) },
              ]}
            />
            <Legend className="mt-3" items={[{ label: 'Spearman ρ', color: tokens.water }, { label: 'ρ innerhalb des Jahres', color: tokens.sage }, { label: 'Skill ggü. Normaljahr', color: tokens.maize }]} />
          </Panel>
          <Panel title={`Vorhergesagter ggü. tatsächlichem relativem Ertrag, 1. Sep (${fmtInt(1600)} von ${fmtInt(8371)})`} source="results/2026-10-16_cybench_eu/predictions_loco.parquet · Zufallsstichprobe, Seed 42">
            <Scatter points={pts} xLabel="Tatsächlich (Ertrag / 5-Jahres-Normalwert)" yLabel="Vorhergesagt" xDomain={[0.2, 1.8]} yDomain={[0.6, 1.4]} diagonal height={320} opacity={0.35} xFmt={(v) => fmt(v, 1)} yFmt={(v) => fmt(v, 1)} />
            <p className="mt-3 text-[13px] text-ink-3">Die Vorhersagen bleiben nahe 1: Das Modell ist vorsichtig und reagiert zu schwach auf extreme Jahre.</p>
          </Panel>
          <Panel title="Fehlerverteilung (vorhergesagt − tatsächlich)" source={`results/2026-10-16_cybench_eu/predictions_loco.parquet · alle ${fmtInt(8371)}`}>
            <Histogram edges={ev.eu_residuals.edges} series={[{ label: 'Modell', counts: ev.eu_residuals.model, color: tokens.water }, { label: 'Normaljahr', counts: ev.eu_residuals.normal_year, color: tokens.ink3 }]} xLabel="Residuum" height={230} />
            <Legend className="mt-3" items={[{ label: 'Modell', color: tokens.water }, { label: 'Normaljahr', color: tokens.ink3 }]} />
          </Panel>
          <Panel title="Mittlerer absoluter Fehler nach tatsächlichem Ertragsbereich" source="results/2026-10-16_cybench_eu/predictions_loco.parquet">
            <PairedBars rows={ev.eu_by_range.map((r) => ({ label: binLabel(r.bin), sub: `n = ${fmtInt(r.n)}`, a: r.mae_model, b: r.mae_normal }))} a={{ label: 'Modell', color: tokens.water }} b={{ label: 'Normaljahr', color: tokens.ink4 }} format={(v) => fmt(v, 2)} />
            <p className="mt-3 text-[13px] text-ink-3">Der Gewinn liegt in den schlechten und den sehr guten Jahren; in normalen Jahren ist die Baseline naturgemäß schwer zu schlagen.</p>
          </Panel>
          <Panel title="Nach Land (≥ 50 Region-Jahre), Spearman ρ" source="results/2026-10-16_cybench_eu/metrics.json · per_country">
            <PairedBars rows={countries.map(([c, v]) => ({ label: c, sub: `n = ${fmtInt(v.n)}`, a: Math.max(0, v.spearman), b: Math.max(0, v.skill_vs_yas1) }))} a={{ label: 'ρ', color: tokens.water }} b={{ label: 'Skill', color: tokens.maize }} format={(v) => fmt(v, 2)} />
            <p className="mt-3 text-[13px] text-ink-3">Negative Werte als 0 dargestellt. Ohne Deutschland (31 % der Daten) liegt ρ bei {fmt(noDe, 2)}.</p>
          </Panel>
        </div>
        <Reveal className="mt-5 panel p-6 text-[13.5px] leading-relaxed text-ink-2">
          <p className="eyebrow mb-3">Im Freeze-Protokoll offengelegt</p>
          Das Hyperparameter-Raster wurde einmal nach einem Pilotlauf erweitert, als erste EU-Ergebnisse sichtbar waren. Die EU-Zahlen sind
          daher leicht optimistisch; der Österreich-Test ist davon nicht betroffen. Modelldateien und Testregeln sind mit SHA-256-Prüfsummen
          eingefroren (Tag {ev.eu_meta.freeze}, Commit {ev.eu_meta.commit}).
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
    { label: 'Stress-Score · Standort-Jahre', sub: `Versuche in Oberösterreich · n = ${last['V2-A_stress_score'].n}`, value: last['V2-A_stress_score'].rho, lo: last['V2-A_stress_score'].lo, hi: last['V2-A_stress_score'].hi, emphasis: true, color: tokens.maize },
    ...(ndvi ? [{ label: 'Einfacher NDVI · dieselben Standort-Jahre', sub: 'ohne Lernen, Vergleichswert', value: ndvi.rho, lo: ndvi.lo, hi: ndvi.hi, color: tokens.ink3 }] : []),
    { label: 'EU-Modell · Bundesländer', sub: `Region-Jahre · n = ${last.V1_regional_model.n}`, value: last.V1_regional_model.rho, lo: last.V1_regional_model.lo, hi: last.V1_regional_model.hi, color: tokens.water },
    { label: 'EU-Modell · Versuchsstandorte', sub: `n = ${last['V2-B_regional_model'].n}`, value: last['V2-B_regional_model'].rho, lo: last['V2-B_regional_model'].lo, hi: last['V2-B_regional_model'].hi, color: tokens.ink3 },
  ]
  const r = at.retrain?.['09-01']
  return (
    <section id="austria" className="scroll-mt-20 py-20">
      <Container>
        <SectionHeader
          eyebrow="5 · Österreich, erster Test (explorativ)"
          title="Eingefrorene Modelle in Österreich: Die Jahre lassen sich reihen, die Felder noch nicht."
          lede="Einmal ausgeführt nach dem als freeze-at-1 eingefrorenen Protokoll, ohne einen Sieger auszuwählen. Explorativ, weil kein Feldmodell das Kriterium „stark genug“ bestanden hatte. Der lokale Test umfasst nur Oberösterreich: Für die steirischen Versuchsstandorte gab es keine Sortenversuche, daher hat sie der vorab festgelegte Filter ausgeschlossen."
          aside={<StrengthBadge strength="limited" />}
        />
        <div className="mt-12 grid gap-5 lg:grid-cols-[1.2fr_1fr]">
          <Panel title="Spearman ρ am 1. September, 95-%-KI (Cluster = Jahre)" source="results/2026-10-17_at_test/metrics.json · reports/at_test_ergebnis.md">
            <CiRows rows={rows} domain={[-1, 1]} reference={0} />
          </Panel>
          <Panel title="Stress-Score nach Prognosestichtag">
            <LineCi
              categories={cuts.map(CUT_LABEL)}
              yDomain={[-0.5, 1]}
              series={[
                { label: 'Stress-Score · Standorte', color: tokens.maize, values: cuts.map((c) => ({ v: at.cutoffs[c]['V2-A_stress_score'].rho, lo: at.cutoffs[c]['V2-A_stress_score'].lo, hi: at.cutoffs[c]['V2-A_stress_score'].hi })) },
                { label: 'EU-Modell · Bundesländer', color: tokens.water, values: cuts.map((c) => ({ v: at.cutoffs[c].V1_regional_model.rho, lo: at.cutoffs[c].V1_regional_model.lo, hi: at.cutoffs[c].V1_regional_model.hi })) },
              ]}
            />
            <Legend className="mt-3" items={[{ label: 'Stress-Score · Standorte in Oberösterreich', color: tokens.maize }, { label: 'EU-Modell · österreichische Bundesländer', color: tokens.water }]} />
          </Panel>
        </div>
        <div className="mt-5 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          <Panel title="Innerhalb eines Jahres">
            <Metric label="Median-ρ zwischen Standorten" value={last['V2-A_within_year'].median} digits={2} tone="rust" note={`${last['V2-A_within_year'].n_groups} Jahre. Innerhalb eines Jahres reiht der Score die Standorte nicht richtig gegeneinander.`} />
          </Panel>
          <Panel title="Innerhalb eines Standorts">
            <Metric label="Median-ρ über die Jahre" value={last['V2-A_within_site'].median} digits={2} note={`${last['V2-A_within_site'].n_groups} Standorte. Das Signal ist der Unterschied zwischen den Jahren.`} />
          </Panel>
          <Panel title="Fehler des EU-Modells ggü. Normaljahr">
            <Metric label="RMSE Modell − Normaljahr" value={last.V1_regional_model.rmse_diff} digits={3} ci={[last.V1_regional_model.rmse_diff_lo, last.V1_regional_model.rmse_diff_hi]} note="Positiv = schlechter. Reiht die Jahre, ist aber nicht genauer als die Annahme eines Normaljahres." />
          </Panel>
          {r && (
            <Panel title="Zusatz: Nachkalibrierung mit zwei Zahlen">
              <Metric label="RMSE eingefroren → nachkalibriert" value={r.pred_r1.rmse} digits={3} prefix={`${fmt(r.pred_r0.rmse, 3)} → `} note={`Mit österreichischen Erträgen, Leave-one-year-out, n = ${r.pred_r1.n}. Ein Hinweis, kein Beweis – und kein eingefrorenes Modell mehr.`} />
            </Panel>
          )}
        </div>
        <Reveal className="mt-5 panel p-6 text-[13.5px] leading-relaxed text-ink-2">
          <p className="eyebrow mb-3">Was nicht behauptet werden darf</p>
          Dass der Stress-Score mehr leistet als einfacher NDVI; dass er Felder oder Standorte innerhalb eines Jahres unterscheidet; dass das
          Ergebnis für die Steiermark gilt; irgendetwas auf Feldebene – ein Test auf Feldebene (V3) braucht noch österreichische Feld-Erträge.
        </Reveal>
      </Container>
    </section>
  )
}
