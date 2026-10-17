import { AnimatePresence, motion } from 'motion/react'
import { Check, ChevronDown, X } from 'lucide-react'
import { useState, type ReactNode } from 'react'
import type { Evidence } from '../api/types'
import { StrengthBadge, type Strength } from '../components/ui/Badge'
import { Reveal } from '../components/ui/Reveal'
import { Container } from '../components/ui/Section'
import { ErrorNote, Skeleton } from '../components/ui/States'
import { fmt, fmtCi, fmtPct } from '../lib/format'
import { useResource } from '../lib/useResource'
import { getEvidence } from '../services/evidenceService'

type Row = { k: string; v: ReactNode }

type Card = {
  key: string
  name: string
  oneLine: string
  strength: Strength
  good: string[]
  notGood: string[]
  /** Level 2: plain-language explanation. */
  more: Row[]
  failures: string[]
  /** Level 3: for readers who want the exact method. */
  tech: Row[]
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
      oneLine: 'Shows which part of a field is likely to yield less.',
      strength: 'robust',
      good: ['Finding the weak zones inside one field', 'Deciding where to look first, from July'],
      notGood: ['Exact yield in t/ha', 'Explaining why a zone is weak'],
      more: [
        { k: 'What it does', v: 'Looks at a satellite picture of one maize field in midsummer and colours every 10 × 10 m patch from “probably good” to “probably weak”.' },
        { k: 'How it works', v: <>Healthy maize is greener in July and August. The simple version ranks patches by greenness, <b>with no training at all</b>.</> },
        { k: 'Based on', v: 'Free Sentinel-2 satellite images (10 m detail), cleaned of clouds.' },
        { k: 'Training data', v: <>One public dataset (USDA Maryland, harvester yield maps): <b>41 field-years</b>, about <b>24,000 patches</b>, roughly <b>0.9 GB</b> raw. The simple version uses none of it.</> },
        { k: 'How good', v: <>Its ranking of patches matches the real yield map with a score of <b>{fmt(b0.rho_median, 2)}</b> {fmtCi(b0.rho_ci?.[0], b0.rho_ci?.[1])} (0 = random, 1 = perfect). Of the flagged weakest quarter, {fmtPct(map.median_precision)} is truly weak, against {fmtPct(map.median_prevalence)} by chance.</> },
      ],
      failures: [
        'Weak zones that return every year can be soil, but also tramlines and field edges.',
        'Very dense, dark-green crops make patches look alike and the ranking gets noisy.',
        'Proven at one site so far; other regions are plausible but untested.',
      ],
      tech: [
        { k: 'Architecture', v: <>Rule <b>B0</b>: median NDVI of the dekads 10 Jul – 18 Aug per cell, no training. Optional model <b>M1</b>: ridge regression (α = 1) on six z-scored NDVI/NDRE windows around the curve peak.</> },
        { k: 'Inputs', v: 'Sentinel-2 L2A, 10-day composites, Cloud Score+ masking (cs_cdf ≥ 0.60), 10-m cells; field edge buffer 10 m.' },
        { k: 'Target', v: 'Cell yield relative to the field mean, from combine yield maps. Low-yield zone: below 85 % of the field mean.' },
        { k: 'Training data', v: 'B0: none. M1: BARC, 41 field-years on 27 fields (Kayad 3 and Akron 6 field-years descriptive only).' },
        { k: 'Validation', v: 'Leave-one-field-out, leave-one-site-out and a site-to-site transfer matrix; bootstrap over fields. Rules fixed before the run (innerfeld_vorab.md).' },
        { k: 'Metrics', v: <>Median ρ B0 <b>{fmt(b0.rho_median, 2)}</b> {fmtCi(b0.rho_ci?.[0], b0.rho_ci?.[1])}; M1 <b>{fmt(m1.rho_median, 2)}</b> {fmtCi(m1.rho_ci?.[0], m1.rho_ci?.[1])}. Flagged quarter: {fmtPct(map.median_precision)} truly low vs {fmtPct(map.median_prevalence)} overall (lift × {fmt(map.median_lift, 1)}).</> },
        { k: 'Version', v: 'results/2026-10-17_innerfeld · pre-registration commit ca0f987 · seed 42' },
      ],
    },
    {
      key: 'score',
      name: 'Field stress score',
      oneLine: 'Flags fields whose season looks worse than that of a healthy field.',
      strength: 'limited',
      good: ['A watch-list of fields per region and year', 'Spotting unusual seasons by 1 September'],
      notGood: ['How large a loss is', 'Why it happened'],
      more: [
        { k: 'What it does', v: 'Follows the greenness of a maize field through the season and compares it with a healthy field. The further it falls behind, the higher the stress score.' },
        { k: 'How it works', v: 'A “healthy reference curve” is built from fields with a normal harvest. A simple statistical model turns the gap to that curve into a risk of a poor harvest.' },
        { k: 'Based on', v: 'Satellite greenness (Sentinel-2 and the harmonised HLS product) from 1 June until the forecast date.' },
        { k: 'Training data', v: <>Two public datasets (Michigan KBS, Maryland BARC): <b>{a0.n} field-years</b> from 8 independent site-years, roughly <b>1 GB</b> raw.</> },
        { k: 'How good', v: <>Clearly better than chance (score <b>{fmt(a0.pr_auc, 2)}</b> {fmtCi(a0.pr_auc_lo, a0.pr_auc_hi)} against {fmt(a0.prevalence, 2)} by chance), but not better than the plain greenness curve ({fmt(raw.pr_auc, 2)}). It finds {fmtPct(al.alarm_recall)} of at-risk fields at a {fmtPct(al.alarm_fpr)} false-alarm rate.</> },
      ],
      failures: [
        'Late sowing after a cover crop looks like stress: organic plots are flagged every year.',
        'Between plots with equal management it does not rank correctly.',
        'Losses that only show after August are missed.',
        'Disease, pests and hail cannot be told apart from drought.',
      ],
      tech: [
        { k: 'Architecture', v: <>Score = mean of min(NDVI<sub>d</sub> − reference<sub>d</sub>, 0) over observed dekads from 1 June to the forecast date. Risk model <b>A0</b>: logistic regression (C = 1, class-balanced) on the score. Alarm threshold set conformally for ≤ 20 % false alarms.</> },
        { k: 'Inputs', v: 'NDVI dekads (Sentinel-2; HLS for the frozen Austria version). Reference = median curve of healthy field-years (≥ 95 % of normal yield), computed inside each training fold.' },
        { k: 'Target', v: 'At risk = relative yield below 0.85, where “normal” is the same field’s yield in at least two other years.' },
        { k: 'Training data', v: `${a0.n} field-years from 8 independent site-years (KBS Michigan, BARC Maryland).` },
        { k: 'Validation', v: 'Leave field group and year out (LOFYO); cluster bootstrap over site-years; label shuffle, coordinate ablation and adversarial validation as controls.' },
        { k: 'Metrics', v: <>PR-AUC A0 <b>{fmt(a0.pr_auc, 2)}</b> {fmtCi(a0.pr_auc_lo, a0.pr_auc_hi)}, raw score {fmt(raw.pr_auc, 2)}; chance {fmt(a0.prevalence, 2)}. At the threshold: recall {fmt(al.alarm_recall, 2)}, precision {fmt(al.alarm_precision, 2)}, false-alarm rate {fmt(al.alarm_fpr, 2)}.</> },
        { k: 'Version', v: 'results/2026-10-16_feinjust_ablation · Austria freeze: reports/freeze_protocol_at.md, reference curve of 77 HLS field-years' },
      ],
    },
    {
      key: 'eu',
      name: 'EU regional model',
      oneLine: 'Estimates whether a region’s maize year will be better or worse than usual.',
      strength: 'certain-small',
      good: ['An early hint on good and bad years per region', 'Ranking regions and years'],
      notGood: ['Single fields', 'Forecasts in t/ha'],
      more: [
        { k: 'What it does', v: 'Estimates, before harvest, whether a region’s maize year will come out above or below its recent normal.' },
        { k: 'How it works', v: 'A machine-learning model (small decision trees) learns from past years how weather, soil moisture and plant greenness from April onwards relate to the final yield. One model per forecast date, 1 June to 1 September.' },
        { k: 'Based on', v: 'Monthly weather, soil moisture, satellite plant-health values and soil properties. No place names, IDs or year are given to the model.' },
        { k: 'Training data', v: <>One public dataset (CY-Bench): <b>{eu.n.toLocaleString('en-US')} region-years</b> from <b>{eu.countries} EU countries</b>, 2003–2021, roughly <b>0.9 GB</b> raw. Austria is left out entirely.</> },
        { k: 'How good', v: <>Ranking of region-years: score <b>{fmt(eu.spearman.value, 2)}</b> {fmtCi(eu.spearman.lo, eu.spearman.hi)} (0 = random, 1 = perfect), tested on countries it never saw. Advantage over simply assuming a normal year: {fmt(eu.skill_vs_normal.value, 2)} {fmtCi(eu.skill_vs_normal.lo, eu.skill_vs_normal.hi)}, small but certain.</> },
      ],
      failures: [
        `It mostly learns which year it is (yearly means ρ ${fmt(eu.yearly_mean_spearman, 2)}), less the differences between regions.`,
        'Predictions stay close to normal and under-react to extreme years.',
        'Before 15 July it has essentially no skill.',
      ],
      tech: [
        { k: 'Architecture', v: 'LightGBM regression with shallow trees (depth ≤ 3, 50–100 trees), one model per forecast date from 1 June to 1 September. Hyper-parameters chosen by leave-one-country-out inside the training countries.' },
        { k: 'Inputs', v: `Monthly mean/min/max of max and min temperature, precipitation, climatic water balance, root-zone and surface soil moisture, fPAR and NDVI from April to the forecast date, plus water capacity and bulk density — ${eu.n_features} features on 1 Sep. No coordinates, IDs or year.` },
        { k: 'Target', v: 'YAS = yield ÷ olympic mean (without max and min) of the same region’s previous five years.' },
        { k: 'Training data', v: `CY-Bench v1.10, maize, ${eu.countries} EU countries, ${eu.n.toLocaleString('en-US')} region-years from 2003–2021. Austria excluded by code and test.` },
        { k: 'Validation', v: 'Leave-one-country-out; bootstrap over region-years and, as a check, over years. Controls: label shuffle, training without Germany, country-balanced weights.' },
        { k: 'Metrics', v: <>Spearman ρ <b>{fmt(eu.spearman.value, 2)}</b> {fmtCi(eu.spearman.lo, eu.spearman.hi)}, R² {fmt(eu.r2.value, 2)}, skill vs normal year {fmt(eu.skill_vs_normal.value, 2)} {fmtCi(eu.skill_vs_normal.lo, eu.skill_vs_normal.hi)}. Within one year: ρ {fmt(eu.within_year.value, 2)}.</> },
        { k: 'Version', v: `${ev.eu_meta.freeze} · commit ${ev.eu_meta.commit} · seed 42 · SHA-256 checksums in reports/freeze_protocol_cybench.md. The grid was widened once after a pilot run; numbers are slightly optimistic (disclosed).` },
      ],
    },
  ]
}

export default function ModelCard() {
  const ev = useResource(getEvidence, 'evidence')
  const list = ev.data ? cards(ev.data) : []
  return (
    <>
      <section className="pt-36 pb-12">
        <Container>
          <Reveal>
            <p className="eyebrow mb-5">The three models</p>
            <h1 className="max-w-[900px] text-balance text-[clamp(2.6rem,6vw,4.6rem)] leading-[0.98] tracking-[-0.04em]">What each one can do, and what not.</h1>
            <p className="mt-6 max-w-[680px] text-[17px] leading-relaxed text-ink-2">
              Each model gets better with every Austrian field that is added. Open a card for the explanation, or for the exact method.
            </p>
          </Reveal>
        </Container>
      </section>
      <section>
        <Container>
          {ev.status === 'loading' && <Skeleton className="h-[600px]" />}
          {ev.error && <ErrorNote error={ev.error} />}
          <div className="grid items-start gap-5 lg:grid-cols-3">
            {list.map((c, i) => (
              <Reveal key={c.key} delay={i * 0.08}>
                <ModelCardView card={c} />
              </Reveal>
            ))}
          </div>
          <p className="mt-10 max-w-[640px] text-[13.5px] leading-relaxed text-ink-3">
            Trained on US and EU data only; Austria is used purely as the final test. Success criteria were written down before each run and
            never changed. Every number can be reproduced from the code.
          </p>
        </Container>
      </section>
    </>
  )
}

function ModelCardView({ card }: { card: Card }) {
  const [level, setLevel] = useState<0 | 1 | 2>(0)
  return (
    <article className="panel flex flex-col p-7">
      <StrengthBadge strength={card.strength} />
      <h2 className="mt-5 text-[26px] leading-tight">{card.name}</h2>
      <p className="mt-3 text-pretty text-[17px] leading-snug text-ink">{card.oneLine}</p>

      <div className="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
        <Checklist title="Good for" items={card.good} ok />
        <Checklist title="Not for" items={card.notGood} />
      </div>

      <div className="mt-7 flex flex-wrap gap-2">
        <Toggle open={level === 1} onClick={() => setLevel(level === 1 ? 0 : 1)}>More explanation</Toggle>
        <Toggle open={level === 2} onClick={() => setLevel(level === 2 ? 0 : 2)}>Technical details</Toggle>
      </div>

      <AnimatePresence initial={false} mode="wait">
        {level === 1 && (
          <Panel key="more">
            <Rows rows={card.more} />
            <p className="eyebrow mb-3 mt-6">Where it fails</p>
            <ul className="flex flex-col gap-3">
              {card.failures.map((f) => (
                <li key={f} className="flex gap-3 text-[13.5px] leading-relaxed text-ink-2">
                  <span className="mt-2 size-1.5 shrink-0 rounded-full bg-rust" />
                  {f}
                </li>
              ))}
            </ul>
          </Panel>
        )}
        {level === 2 && (
          <Panel key="tech">
            <Rows rows={card.tech} mono />
          </Panel>
        )}
      </AnimatePresence>
    </article>
  )
}

function Checklist({ title, items, ok = false }: { title: string; items: string[]; ok?: boolean }) {
  return (
    <div>
      <p className="eyebrow mb-3">{title}</p>
      <ul className="flex flex-col gap-2.5">
        {items.map((t) => (
          <li key={t} className="flex gap-2.5 text-[14px] leading-snug text-ink-2">
            {ok ? <Check className="mt-0.5 size-4 shrink-0 text-sage" /> : <X className="mt-0.5 size-4 shrink-0 text-rust" />}
            {t}
          </li>
        ))}
      </ul>
    </div>
  )
}

function Toggle({ open, onClick, children }: { open: boolean; onClick: () => void; children: ReactNode }) {
  return (
    <button
      type="button"
      aria-expanded={open}
      onClick={onClick}
      className={`inline-flex h-9 items-center gap-1.5 rounded-[var(--radius-control)] border px-3 text-[13px] transition ${open ? 'border-maize/40 bg-maize/10 text-maize' : 'border-[var(--line-strong)] text-ink-2 hover:border-ink-3 hover:text-ink'}`}
    >
      {children}
      <ChevronDown className={`size-3.5 transition-transform ${open ? 'rotate-180' : ''}`} />
    </button>
  )
}

function Panel({ children }: { children: ReactNode }) {
  return (
    <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} transition={{ duration: 0.25 }} className="overflow-hidden">
      <div className="mt-6 border-t border-[var(--line)] pt-6">{children}</div>
    </motion.div>
  )
}

function Rows({ rows, mono = false }: { rows: Row[]; mono?: boolean }) {
  return (
    <dl className="flex flex-col gap-4">
      {rows.map((r) => (
        <div key={r.k}>
          <dt className="eyebrow">{r.k}</dt>
          <dd className={`mt-1.5 text-pretty leading-relaxed text-ink [&_b]:font-semibold [&_b]:text-maize ${mono ? 'text-[13px]' : 'text-[14px]'}`}>{r.v}</dd>
        </div>
      ))}
    </dl>
  )
}
