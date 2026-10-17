import { AnimatePresence, motion } from 'motion/react'
import { useState, type ReactNode } from 'react'
import type { Evidence } from '../api/types'
import { StrengthBadge, type Strength } from '../components/ui/Badge'
import { Reveal } from '../components/ui/Reveal'
import { Container } from '../components/ui/Section'
import { ErrorNote, Skeleton } from '../components/ui/States'
import { Tabs } from '../components/ui/Tabs'
import { fmt, fmtCi, fmtPct } from '../lib/format'
import { useResource } from '../lib/useResource'
import { getEvidence } from '../services/evidenceService'

type Card = {
  key: string
  name: string
  oneLine: string
  strength: Strength
  status: string
  rows: { k: string; v: ReactNode }[]
  failures: string[]
}

function cards(ev: Evidence): Card[] {
  const b0 = ev.innerfeld_main.untrained.BARC.B0
  const m1 = ev.innerfeld_main.E.BARC.M1
  const map = ev.within_field_map
  const a0 = ev.stress_models.A0
  const raw = ev.stress_models.A_roh
  const al = ev.alarm
  const eu = ev.eu_cutoffs.find((c) => c.cutoff === '09-01')!
  return [
    {
      key: 'map',
      name: 'Within-field map',
      oneLine: 'Ranks the 10-m cells of a field by expected yield and flags the weakest quarter.',
      strength: 'robust',
      status: 'Main result · not yet testable in Austria (no field yield maps)',
      rows: [
        { k: 'Architecture', v: <>Rule <b>B0</b>: median NDVI of the dekads 10 Jul – 18 Aug per cell, no training. Optional model <b>M1</b>: ridge regression (α = 1) on six z-scored NDVI/NDRE windows around the curve peak.</> },
        { k: 'Inputs', v: 'Sentinel-2 L2A, 10-day composites, Cloud Score+ masking (cs_cdf ≥ 0.60), 10-m cells; field edge buffer 10 m.' },
        { k: 'Target', v: 'Cell yield relative to the field mean, from combine yield maps. Low-yield zone: below 85 % of the field mean.' },
        { k: 'Training data', v: 'B0: none. M1: BARC, 41 field-years on 27 fields (Kayad 3 and Akron 6 field-years descriptive only).' },
        { k: 'Validation', v: 'Leave-one-field-out, leave-one-site-out and a site-to-site transfer matrix; bootstrap over fields. Rules fixed before the run (innerfeld_vorab.md).' },
        { k: 'Metrics', v: <>Median ρ B0 <b>{fmt(b0.rho_median, 2)}</b> {fmtCi(b0.rho_ci?.[0], b0.rho_ci?.[1])}; M1 <b>{fmt(m1.rho_median, 2)}</b> {fmtCi(m1.rho_ci?.[0], m1.rho_ci?.[1])}. Flagged quarter: {fmtPct(map.median_precision)} truly low vs {fmtPct(map.median_prevalence)} overall (lift × {fmt(map.median_lift, 1)}).</> },
        { k: 'Version', v: 'results/2026-10-17_innerfeld · pre-registration commit ca0f987 · seed 42' },
        { k: 'Intended use', v: 'Show where inside a known maize field to look first, from July–August imagery.' },
        { k: 'Not for', v: 'Absolute yield in t/ha, diagnosis of causes, or fields without a clear mid-summer scene.' },
      ],
      failures: [
        'Recurring weak zones can be soil — or tramlines and field edges.',
        'Near NDVI saturation (Kayad, 0.90–0.95) cells differ little and the ranking gets noisy.',
        'BARC yield maps are kriged to 10-m blocks, which smooths the truth the map is scored against.',
        'Conclusive only at one site; transfer to other regions is plausible but unproven.',
      ],
    },
    {
      key: 'score',
      name: 'Field stress score',
      oneLine: 'Flags field-years whose season curve falls below that of a healthy maize field.',
      strength: 'limited',
      status: 'freeze-at-1 · Austria: years rank (ρ 0.50), no better than NDVI',
      rows: [
        { k: 'Architecture', v: <>Score = mean of min(NDVI<sub>d</sub> − reference<sub>d</sub>, 0) over observed dekads from 1 June to the forecast date. Risk model <b>A0</b>: logistic regression (C = 1, class-balanced) on the score. Alarm threshold set conformally for ≤ 20 % false alarms.</> },
        { k: 'Inputs', v: 'NDVI dekads (Sentinel-2; HLS for the frozen Austria version). Reference = median curve of healthy field-years (≥ 95 % of normal yield), computed inside each training fold.' },
        { k: 'Target', v: 'At risk = relative yield below 0.85, where “normal” is the same field’s yield in at least two other years.' },
        { k: 'Training data', v: `${a0.n} field-years from 8 independent site-years (KBS Michigan, BARC Maryland).` },
        { k: 'Validation', v: 'Leave field group and year out (LOFYO); cluster bootstrap over site-years; label shuffle, coordinate ablation and adversarial validation as controls.' },
        { k: 'Metrics', v: <>PR-AUC A0 <b>{fmt(a0.pr_auc, 2)}</b> {fmtCi(a0.pr_auc_lo, a0.pr_auc_hi)}, raw score {fmt(raw.pr_auc, 2)}; chance {fmt(a0.prevalence, 2)}. At the threshold: recall {fmt(al.alarm_recall, 2)}, precision {fmt(al.alarm_precision, 2)}, false-alarm rate {fmt(al.alarm_fpr, 2)}.</> },
        { k: 'Version', v: 'results/2026-10-16_feinjust_ablation · Austria freeze: reports/freeze_protocol_at.md, reference curve of 77 HLS field-years' },
        { k: 'Intended use', v: 'A ranked watch-list of fields per region and year: which curves look unusual by 1 September.' },
        { k: 'Not for', v: 'Estimating the size of a loss, or explaining its cause.' },
      ],
      failures: [
        'Late sowing after a cover crop looks like stress: KBS organic plots are flagged every year, even in a normal 2020.',
        'Between plots with equal management the score does not rank correctly (median ρ −0.29).',
        'Losses that only show after August are missed (Field E on the Analyse page).',
        'Disease, pests and hail cannot be separated from drought without extra data.',
      ],
    },
    {
      key: 'eu',
      name: 'EU regional model',
      oneLine: 'Ranks region-years by their yield relative to the last five years, from weather and satellite summaries.',
      strength: 'certain-small',
      status: 'freeze-cybench-1 · Austria: years rank (ρ 0.52), not more accurate than normal',
      rows: [
        { k: 'Architecture', v: 'LightGBM regression with shallow trees (depth ≤ 3, 50–100 trees), one model per forecast date from 1 June to 1 September. Hyper-parameters chosen by leave-one-country-out inside the training countries.' },
        { k: 'Inputs', v: `Monthly mean/min/max of max and min temperature, precipitation, climatic water balance, root-zone and surface soil moisture, fPAR and NDVI from April to the forecast date, plus water capacity and bulk density — ${eu.n_features} features on 1 Sep. No coordinates, IDs or year.` },
        { k: 'Target', v: 'YAS = yield ÷ olympic mean (without max and min) of the same region’s previous five years.' },
        { k: 'Training data', v: `CY-Bench v1.10, maize, ${eu.countries} EU countries, ${eu.n.toLocaleString('en-US')} region-years from 2003–2021. Austria excluded by code and test.` },
        { k: 'Validation', v: 'Leave-one-country-out; bootstrap over region-years and, as a check, over years. Controls: label shuffle, training without Germany, country-balanced weights.' },
        { k: 'Metrics', v: <>Spearman ρ <b>{fmt(eu.spearman.value, 2)}</b> {fmtCi(eu.spearman.lo, eu.spearman.hi)}, R² {fmt(eu.r2.value, 2)}, skill vs normal year {fmt(eu.skill_vs_normal.value, 2)} {fmtCi(eu.skill_vs_normal.lo, eu.skill_vs_normal.hi)}. Within one year: ρ {fmt(eu.within_year.value, 2)}.</> },
        { k: 'Version', v: `${ev.eu_meta.freeze} · commit ${ev.eu_meta.commit} · seed 42 · SHA-256 checksums in reports/freeze_protocol_cybench.md` },
        { k: 'Intended use', v: 'Early indication whether a region’s maize year will be below its recent normal.' },
        { k: 'Not for', v: 'Single fields, or yield forecasts in t/ha.' },
      ],
      failures: [
        `It mostly learns which year it is (yearly means ρ ${fmt(eu.yearly_mean_spearman, 2)}), less the differences between regions.`,
        'Predictions stay close to normal and under-react to extreme years.',
        'Before 15 July it has essentially no skill.',
        'The grid was widened once after a pilot run: EU numbers are slightly optimistic (disclosed).',
      ],
    },
  ]
}

export default function ModelCard() {
  const ev = useResource(getEvidence, 'evidence')
  const [tab, setTab] = useState('map')
  const list = ev.data ? cards(ev.data) : []
  const card = list.find((c) => c.key === tab)
  return (
    <>
      <section className="pt-36 pb-12">
        <Container>
          <Reveal>
            <p className="eyebrow mb-5">Model card</p>
            <h1 className="max-w-[900px] text-balance text-[clamp(2.6rem,6vw,4.6rem)] leading-[0.98] tracking-[-0.04em]">Three models. What each one is, and is not.</h1>
            <p className="mt-6 max-w-[680px] text-[17px] leading-relaxed text-ink-2">
              Following the model-card practice: architecture, data, validation, metrics, version — and the cases where each model fails.
            </p>
          </Reveal>
        </Container>
      </section>
      <section>
        <Container>
          {ev.status === 'loading' && <Skeleton className="h-[600px]" />}
          {ev.error && <ErrorNote error={ev.error} />}
          {card && (
            <>
              <Tabs label="Model" value={tab} onChange={setTab} items={list.map((c) => ({ value: c.key, label: c.name }))} />
              <AnimatePresence mode="wait">
                <motion.div key={card.key} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} transition={{ duration: 0.3 }} className="mt-8 grid gap-5 lg:grid-cols-[1fr_340px]">
                  <article className="panel overflow-hidden">
                    <header className="flex flex-col gap-4 border-b border-[var(--line)] p-7 sm:flex-row sm:items-start sm:justify-between sm:p-9">
                      <div className="min-w-0 flex-1">
                        <h2 className="text-[clamp(1.8rem,3vw,2.4rem)]">{card.name}</h2>
                        <p className="mt-3 max-w-[560px] text-[15.5px] leading-relaxed text-ink-2">{card.oneLine}</p>
                      </div>
                      <div className="flex shrink-0 flex-col items-start gap-2 sm:items-end">
                        <StrengthBadge strength={card.strength} />
                        <span className="font-mono text-[11px] text-ink-3">{card.status}</span>
                      </div>
                    </header>
                    <dl>
                      {card.rows.map((r) => (
                        <div key={r.k} className="grid gap-2 border-b border-[var(--line)] px-7 py-5 last:border-0 sm:grid-cols-[180px_1fr] sm:px-9">
                          <dt className="eyebrow pt-0.5">{r.k}</dt>
                          <dd className="text-pretty text-[14.5px] leading-relaxed text-ink [&_b]:font-semibold [&_b]:text-maize">{r.v}</dd>
                        </div>
                      ))}
                    </dl>
                  </article>
                  <aside className="flex flex-col gap-5">
                    <div className="panel p-7">
                      <p className="eyebrow mb-5">Known failure cases</p>
                      <ul className="flex flex-col gap-4">
                        {card.failures.map((f) => (
                          <li key={f} className="flex gap-3 text-[14px] leading-relaxed text-ink-2">
                            <span className="mt-2 size-1.5 shrink-0 rounded-full bg-rust" />
                            {f}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div className="panel p-7">
                      <p className="eyebrow mb-4">Shared rules</p>
                      <ul className="flex flex-col gap-3 text-[13.5px] leading-relaxed text-ink-2">
                        <li>No Austrian value in training, features, thresholds or model choice.</li>
                        <li>Every criterion written down before the run; never changed afterwards.</li>
                        <li>95 % intervals by cluster bootstrap; n counts independent units.</li>
                        <li>Seeds fixed; every number reproducible from the commit.</li>
                      </ul>
                    </div>
                  </aside>
                </motion.div>
              </AnimatePresence>
            </>
          )}
        </Container>
      </section>
    </>
  )
}
