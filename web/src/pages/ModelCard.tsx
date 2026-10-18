import { AnimatePresence, motion } from 'motion/react'
import { Check, ChevronDown, X } from 'lucide-react'
import { useState, type ReactNode } from 'react'
import type { Evidence } from '../api/types'
import { Backdrop } from '../components/ui/Backdrop'
import { CountUp } from '../components/ui/CountUp'
import { StrengthBadge, type Strength } from '../components/ui/Badge'
import { Reveal } from '../components/ui/Reveal'
import { Container, SectionHeader, Source } from '../components/ui/Section'
import { ErrorNote, Skeleton } from '../components/ui/States'
import { MODEL_INVENTORY } from '../data/content/project'
import { fmt, fmtCi, fmtInt, fmtPct } from '../lib/format'
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
      name: 'Teilflächenkarte',
      oneLine: 'Zeigt, welcher Teil eines Feldes wahrscheinlich weniger Ertrag bringt.',
      strength: 'robust',
      good: ['Schwache Zonen innerhalb eines Feldes finden', 'Entscheiden, wo Sie ab Juli zuerst nachsehen'],
      notGood: ['Genauer Ertrag in t/ha', 'Erklären, warum eine Zone schwach ist'],
      more: [
        { k: 'Was es macht', v: 'Betrachtet ein Satellitenbild eines Maisfeldes im Hochsommer und färbt jede 10 × 10 m große Zelle von „wahrscheinlich gut“ bis „wahrscheinlich schwach“ ein.' },
        { k: 'Wie es funktioniert', v: <>Gesunder Mais ist im Juli und August grüner. Die einfache Version reiht die Zellen nach ihrem Grün, <b>ganz ohne Training</b>.</> },
        { k: 'Grundlage', v: 'Kostenlose Sentinel-2-Satellitenbilder (10 m Auflösung), von Wolken bereinigt.' },
        { k: 'Trainingsdaten', v: <>Ein öffentlicher Datensatz (USDA Maryland, Mähdrescher-Ertragskarten): <b>41 Feld-Jahre</b>, etwa <b>{fmtInt(24000)} Zellen</b>, rund <b>0,9 GB</b> Rohdaten. Die einfache Version nutzt davon nichts.</> },
        { k: 'Wie gut', v: <>Die Reihung der Zellen stimmt mit der echten Ertragskarte mit einem Wert von <b>{fmt(b0.rho_median, 2)}</b> {fmtCi(b0.rho_ci?.[0], b0.rho_ci?.[1])} überein (0 = zufällig, 1 = perfekt). Vom markierten schwächsten Viertel sind {fmtPct(map.median_precision)} wirklich schwach, gegenüber {fmtPct(map.median_prevalence)} bei Zufall.</> },
      ],
      failures: [
        'Schwache Zonen, die jedes Jahr wiederkehren, können am Boden liegen, aber auch an Fahrgassen und Feldrändern.',
        'Sehr dichte, dunkelgrüne Bestände lassen die Zellen ähnlich aussehen; die Reihung wird unruhig.',
        'Bisher an einem Standort nachgewiesen; andere Regionen sind plausibel, aber ungetestet.',
      ],
      tech: [
        { k: 'Architektur', v: <>Regel <b>B0</b>: Median-NDVI der Dekaden 10. Jul – 18. Aug je Zelle, ohne Training. Optionales Modell <b>M1</b>: Ridge-Regression (α = 1) auf sechs z-standardisierten NDVI/NDRE-Fenstern um das Kurvenmaximum.</> },
        { k: 'Eingaben', v: 'Sentinel-2 L2A, 10-Tage-Komposite, Cloud-Score+-Maskierung (cs_cdf ≥ 0,60), 10-m-Zellen; Randpuffer 10 m.' },
        { k: 'Zielgröße', v: 'Zellertrag relativ zum Feldmittel, aus Mähdrescher-Ertragskarten. Ertragsschwache Zone: unter 85 % des Feldmittels.' },
        { k: 'Trainingsdaten', v: 'B0: keine. M1: BARC, 41 Feld-Jahre auf 27 Feldern (Kayad 3 und Akron 6 Feld-Jahre nur beschreibend).' },
        { k: 'Validierung', v: 'Leave-one-field-out, Leave-one-site-out und eine Transfermatrix von Standort zu Standort; Bootstrap über Felder. Regeln vor dem Lauf festgelegt (innerfeld_vorab.md).' },
        { k: 'Metriken', v: <>Median-ρ B0 <b>{fmt(b0.rho_median, 2)}</b> {fmtCi(b0.rho_ci?.[0], b0.rho_ci?.[1])}; M1 <b>{fmt(m1.rho_median, 2)}</b> {fmtCi(m1.rho_ci?.[0], m1.rho_ci?.[1])}. Markiertes Viertel: {fmtPct(map.median_precision)} wirklich ertragsschwach ggü. {fmtPct(map.median_prevalence)} insgesamt (Lift × {fmt(map.median_lift, 1)}).</> },
        { k: 'Version', v: 'results/2026-10-17_innerfeld · Commit der Vorab-Festlegung ca0f987 · Seed 42' },
      ],
    },
    {
      key: 'score',
      name: 'Feld-Stress-Score',
      oneLine: 'Markiert Felder, deren Saison schlechter aussieht als die eines gesunden Feldes.',
      strength: 'limited',
      good: ['Eine Beobachtungsliste von Feldern je Region und Jahr', 'Auffällige Saisonen bis zum 1. September erkennen'],
      notGood: ['Wie groß ein Ausfall ist', 'Warum er entstanden ist'],
      more: [
        { k: 'Was es macht', v: 'Verfolgt das Grün eines Maisfeldes durch die Saison und vergleicht es mit einem gesunden Feld. Je weiter es zurückfällt, desto höher der Stress-Score.' },
        { k: 'Wie es funktioniert', v: 'Aus Feldern mit normaler Ernte wird eine „gesunde Referenzkurve“ gebildet. Ein einfaches statistisches Modell macht aus dem Abstand zu dieser Kurve ein Risiko für eine schlechte Ernte.' },
        { k: 'Grundlage', v: 'Satelliten-Grünwerte (Sentinel-2 und das harmonisierte HLS-Produkt) vom 1. Juni bis zum Prognosestichtag.' },
        { k: 'Trainingsdaten', v: <>Zwei öffentliche Datensätze (Michigan KBS, Maryland BARC): <b>{a0.n} Feld-Jahre</b> aus 8 unabhängigen Standort-Jahren, rund <b>1 GB</b> Rohdaten.</> },
        { k: 'Wie gut', v: <>Deutlich besser als Zufall (Wert <b>{fmt(a0.pr_auc, 2)}</b> {fmtCi(a0.pr_auc_lo, a0.pr_auc_hi)} gegenüber {fmt(a0.prevalence, 2)} bei Zufall), aber nicht besser als die einfache Grünkurve ({fmt(raw.pr_auc, 2)}). Er findet {fmtPct(al.alarm_recall)} der gefährdeten Felder bei einer Fehlalarmrate von {fmtPct(al.alarm_fpr)}.</> },
      ],
      failures: [
        'Späte Aussaat nach einer Zwischenfrucht sieht aus wie Stress: Bio-Parzellen werden jedes Jahr markiert.',
        'Zwischen Parzellen mit gleicher Bewirtschaftung reiht er nicht richtig.',
        'Ausfälle, die sich erst nach August zeigen, werden übersehen.',
        'Krankheiten, Schädlinge und Hagel lassen sich nicht von Trockenheit unterscheiden.',
      ],
      tech: [
        { k: 'Architektur', v: <>Score = Mittel von min(NDVI<sub>d</sub> − Referenz<sub>d</sub>, 0) über die beobachteten Dekaden vom 1. Juni bis zum Prognosestichtag. Risikomodell <b>A0</b>: logistische Regression (C = 1, klassenbalanciert) auf den Score. Alarmschwelle konform festgelegt für ≤ 20 % Fehlalarme.</> },
        { k: 'Eingaben', v: 'NDVI-Dekaden (Sentinel-2; HLS für die eingefrorene Österreich-Version). Referenz = Mediankurve gesunder Feld-Jahre (≥ 95 % des Normalertrags), innerhalb jedes Trainings-Folds berechnet.' },
        { k: 'Zielgröße', v: 'Gefährdet = relativer Ertrag unter 0,85, wobei „normal“ der Ertrag desselben Feldes in mindestens zwei anderen Jahren ist.' },
        { k: 'Trainingsdaten', v: `${a0.n} Feld-Jahre aus 8 unabhängigen Standort-Jahren (KBS Michigan, BARC Maryland).` },
        { k: 'Validierung', v: 'Feldgruppe und Jahr ausgelassen (LOFYO); Cluster-Bootstrap über Standort-Jahre; Label-Shuffle, Koordinaten-Ablation und Adversarial Validation als Kontrollen.' },
        { k: 'Metriken', v: <>PR-AUC A0 <b>{fmt(a0.pr_auc, 2)}</b> {fmtCi(a0.pr_auc_lo, a0.pr_auc_hi)}, roher Score {fmt(raw.pr_auc, 2)}; Zufallsniveau {fmt(a0.prevalence, 2)}. An der Schwelle: Recall {fmt(al.alarm_recall, 2)}, Präzision {fmt(al.alarm_precision, 2)}, Fehlalarmrate {fmt(al.alarm_fpr, 2)}.</> },
        { k: 'Version', v: 'results/2026-10-16_feinjust_ablation · Österreich-Freeze: reports/freeze_protocol_at.md, Referenzkurve aus 77 HLS-Feld-Jahren' },
      ],
    },
    {
      key: 'eu',
      name: 'EU-Regionalmodell',
      oneLine: 'Schätzt, ob das Maisjahr einer Region besser oder schlechter als üblich wird.',
      strength: 'certain-small',
      good: ['Ein früher Hinweis auf gute und schlechte Jahre je Region', 'Regionen und Jahre reihen'],
      notGood: ['Einzelne Felder', 'Prognosen in t/ha'],
      more: [
        { k: 'Was es macht', v: 'Schätzt vor der Ernte, ob das Maisjahr einer Region über oder unter ihrem üblichen Ertrag der letzten Jahre liegen wird.' },
        { k: 'Wie es funktioniert', v: 'Ein Machine-Learning-Modell (kleine Entscheidungsbäume) lernt aus vergangenen Jahren, wie Wetter, Bodenfeuchte und Pflanzengrün ab April mit dem Endertrag zusammenhängen. Ein Modell je Prognosestichtag, 1. Juni bis 1. September.' },
        { k: 'Grundlage', v: 'Monatliches Wetter, Bodenfeuchte, Satellitenwerte zur Pflanzengesundheit und Bodeneigenschaften. Ortsnamen, IDs oder das Jahr bekommt das Modell nicht.' },
        { k: 'Trainingsdaten', v: <>Ein öffentlicher Datensatz (CY-Bench): <b>{fmtInt(eu.n)} Region-Jahre</b> aus <b>{eu.countries} EU-Ländern</b>, 2003–2021, rund <b>0,9 GB</b> Rohdaten. Österreich ist vollständig ausgeschlossen.</> },
        { k: 'Wie gut', v: <>Reihung der Region-Jahre: Wert <b>{fmt(eu.spearman.value, 2)}</b> {fmtCi(eu.spearman.lo, eu.spearman.hi)} (0 = zufällig, 1 = perfekt), getestet an Ländern, die es nie gesehen hat. Vorteil gegenüber der einfachen Annahme eines Normaljahres: {fmt(eu.skill_vs_normal.value, 2)} {fmtCi(eu.skill_vs_normal.lo, eu.skill_vs_normal.hi)} – statistisch gesichert.</> },
      ],
      failures: [
        `Es lernt vor allem, welches Jahr es ist (Jahresmittel ρ ${fmt(eu.yearly_mean_spearman, 2)}), weniger die Unterschiede zwischen Regionen.`,
        'Die Vorhersagen bleiben nahe am Normalwert und reagieren zu schwach auf extreme Jahre.',
        'Vor dem 15. Juli hat es praktisch keine Vorhersagekraft.',
      ],
      tech: [
        { k: 'Architektur', v: 'LightGBM-Regression mit flachen Bäumen (Tiefe ≤ 3, 50–100 Bäume), ein Modell je Prognosestichtag vom 1. Juni bis 1. September. Hyperparameter per Leave-one-country-out innerhalb der Trainingsländer gewählt.' },
        { k: 'Eingaben', v: `Monatliches Mittel/Minimum/Maximum von Tageshöchst- und Tagestiefsttemperatur, Niederschlag, klimatischer Wasserbilanz, Bodenfeuchte im Wurzelraum und an der Oberfläche, fPAR und NDVI von April bis zum Prognosestichtag, dazu Wasserspeicherfähigkeit und Lagerungsdichte – ${eu.n_features} Merkmale am 1. Sep. Keine Koordinaten, IDs oder Jahr.` },
        { k: 'Zielgröße', v: 'YAS = Ertrag ÷ olympisches Mittel (ohne Maximum und Minimum) der fünf vorangegangenen Jahre derselben Region.' },
        { k: 'Trainingsdaten', v: `CY-Bench v1.10, Mais, ${eu.countries} EU-Länder, ${fmtInt(eu.n)} Region-Jahre aus 2003–2021. Österreich per Code und Test ausgeschlossen.` },
        { k: 'Validierung', v: 'Leave-one-country-out; Bootstrap über Region-Jahre und zur Kontrolle über Jahre. Kontrollen: Label-Shuffle, Training ohne Deutschland, länderbalancierte Gewichte.' },
        { k: 'Metriken', v: <>Spearman ρ <b>{fmt(eu.spearman.value, 2)}</b> {fmtCi(eu.spearman.lo, eu.spearman.hi)}, R² {fmt(eu.r2.value, 2)}, Skill ggü. Normaljahr {fmt(eu.skill_vs_normal.value, 2)} {fmtCi(eu.skill_vs_normal.lo, eu.skill_vs_normal.hi)}. Innerhalb eines Jahres: ρ {fmt(eu.within_year.value, 2)}.</> },
        { k: 'Version', v: `${ev.eu_meta.freeze} · Commit ${ev.eu_meta.commit} · Seed 42 · SHA-256-Prüfsummen in reports/freeze_protocol_cybench.md. Das Raster wurde nach einem Pilotlauf einmal erweitert; die Zahlen sind leicht optimistisch (offengelegt).` },
      ],
    },
  ]
}

export default function ModelCard() {
  const ev = useResource(getEvidence, 'evidence')
  const list = ev.data ? cards(ev.data) : []
  return (
    <>
      <section className="relative isolate overflow-hidden pt-36 pb-16">
        <Backdrop name="modelle-pixelfelder" />
        <Container>
          <Reveal>
            <p className="eyebrow mb-5">Modelle</p>
            <h1 className="max-w-[900px] text-balance text-[clamp(2.6rem,6vw,4.6rem)] leading-[0.98] tracking-[-0.04em]">Wie aus Satellitendaten eine Warnung wird.</h1>
            <p className="mt-6 max-w-[680px] text-[17px] leading-relaxed text-ink-2">
              Zuerst die drei Modelle, die geblieben sind, dann alle Modellvarianten, die auf dem Weg dorthin trainiert wurden. Jedes Modell wird
              mit jedem österreichischen Feld besser, das dazukommt. Öffnen Sie eine Karte oder eine Zeile für mehr Details.
            </p>
          </Reveal>
        </Container>
      </section>
      <section id="drei-modelle" className="scroll-mt-20">
        <Container>
          <Reveal>
            <p className="eyebrow mb-3">Die drei Modelle</p>
            <h2 className="mb-8 text-[clamp(1.7rem,3vw,2.3rem)] leading-tight">Was jedes kann – und was nicht.</h2>
          </Reveal>
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
            Nur mit US- und EU-Daten trainiert; Österreich dient ausschließlich als abschließender Test. Die Erfolgskriterien wurden vor
            jedem Lauf schriftlich festgelegt und nie geändert. Jede Zahl lässt sich aus dem Code reproduzieren.
          </p>
        </Container>
      </section>
      <ModelInventory />
    </>
  )
}

const barColor: Partial<Record<Strength, string>> = { robust: 'bg-sage', 'certain-small': 'bg-water', limited: 'bg-maize', failed: 'bg-rust' }

/** How many model variants were trained per block, as proportional bars; each row opens to show what came out. */
function ModelInventory() {
  const [open, setOpen] = useState<string | null>(null)
  const total = MODEL_INVENTORY.reduce((s, b) => s + b.count, 0)
  const max = Math.max(...MODEL_INVENTORY.map((b) => b.count))
  return (
    <section id="varianten" className="scroll-mt-20 pt-24">
      <Container>
        <SectionHeader
          eyebrow="Modellvarianten"
          title={<><CountUp value={total} digits={0} /> trainierte Modellvarianten. Drei Ergebnisse sind geblieben.</>}
          lede={`Verteilt auf ${MODEL_INVENTORY.length} Experimentblöcke. Eine Variante ist ein Modell mit festen Merkmalen und festem Stichtag, bewertet an einem vorab festgelegten Kriterium. Weil jede Variante in einer Kreuzvalidierung mehrfach trainiert wurde, sind es mehrere Tausend einzelne Trainingsläufe. Klicken Sie auf einen Block für Details.`}
        />
        <Reveal className="panel mt-12 p-3 sm:p-5">
          <ul className="flex flex-col">
            {MODEL_INVENTORY.map((b) => {
              const isOpen = open === b.block
              return (
                <li key={b.block} className="border-b border-[var(--line)] last:border-b-0">
                  <button
                    type="button"
                    aria-expanded={isOpen}
                    onClick={() => setOpen(isOpen ? null : b.block)}
                    className={`grid w-full gap-2 rounded-xl px-3 py-4 text-left transition-colors hover:bg-white/[0.03] sm:grid-cols-[minmax(0,260px)_minmax(0,1fr)_56px_20px] sm:items-center sm:gap-6 ${isOpen ? 'bg-white/[0.03]' : ''}`}
                  >
                    <div className="min-w-0">
                      <p className="text-[15px] text-ink">{b.block}</p>
                      <p className="text-[12.5px] leading-snug text-ink-3">{b.what}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-white/[0.04]">
                        <div className={`h-full rounded-full ${barColor[b.status] ?? 'bg-ink-3'}`} style={{ width: `${Math.max((b.count / max) * 100, 1.5)}%` }} />
                      </div>
                      <span className="w-10 text-right font-mono text-[14px] tabular text-ink sm:hidden">{b.count}</span>
                      <ChevronDown className={`size-4 shrink-0 text-ink-3 transition-transform sm:hidden ${isOpen ? 'rotate-180' : ''}`} />
                    </div>
                    <span className="hidden text-right font-mono text-[15px] tabular text-ink sm:block">{b.count}</span>
                    <ChevronDown className={`hidden size-4 text-ink-3 transition-transform sm:block ${isOpen ? 'rotate-180' : ''}`} />
                  </button>
                  <AnimatePresence initial={false}>
                    {isOpen && (
                      <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} transition={{ duration: 0.25 }} className="overflow-hidden">
                        <div className="grid gap-6 px-3 pb-6 pt-2 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
                          <div>
                            <StrengthBadge strength={b.status} />
                            <p className="eyebrow mb-1.5 mt-4">Was trainiert wurde</p>
                            <p className="text-[14px] leading-relaxed text-ink-2">{b.detail}</p>
                          </div>
                          <div>
                            <p className="eyebrow mb-1.5">Was herauskam</p>
                            <p className="text-[14px] leading-relaxed text-ink">{b.result}</p>
                            <div className="mt-4 flex flex-wrap gap-2">
                              {b.numbers.map((n) => (
                                <span key={n.label} className="rounded-lg border border-[var(--line)] bg-white/[0.02] px-2.5 py-1 font-mono text-[11.5px] text-ink-2">
                                  {n.label} <span className="text-ink">{n.value}</span>
                                </span>
                              ))}
                            </div>
                            <Source className="mt-3">{b.source}</Source>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </li>
              )
            })}
          </ul>
          <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 border-t border-[var(--line)] px-3 pt-5 text-[12.5px] text-ink-3">
            {(['robust', 'certain-small', 'limited', 'failed'] as Strength[]).map((st) => (
              <StrengthBadge key={st} strength={st} />
            ))}
          </div>
        </Reveal>
        <div className="mt-10 grid gap-5 md:grid-cols-2">
          {[
            ['Die einfachsten Methoden haben gewonnen', 'Die Teilflächenkarte beruht auf einer NDVI-Regel, der Stress-Score auf einer festen Referenzkurve. Gelernte Modelle waren dort nicht besser. Eingefroren und gespeichert sind nur die 7 Modelle des EU-Regionalmodells.'],
            ['Nicht mitgezählt', 'Regeln ohne Training (NDVI-Regeln, Stress-Score, Normaljahr- und Trend-Baselines), die Glättung aus Runde 2, die Kalibrierung der Warnschwellen und alle Label-Shuffle-Kontrollen. Die Österreich-Tests haben nur eingefrorene Modelle angewendet.'],
          ].map(([t, body]) => (
            <Reveal key={t} className="border-t border-[var(--line-strong)] pt-5">
              <h3 className="text-[17px]">{t}</h3>
              <p className="mt-2 text-[13.5px] leading-relaxed text-ink-2">{body}</p>
            </Reveal>
          ))}
        </div>
        <Source className="mt-6">results/ (alle Branches), gezählt am 2026-10-18 · reports/doku/hauptergebnis.md §5</Source>
      </Container>
    </section>
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
        <Checklist title="Geeignet für" items={card.good} ok />
        <Checklist title="Nicht geeignet für" items={card.notGood} />
      </div>

      <div className="mt-7 flex flex-wrap gap-2">
        <Toggle open={level === 1} onClick={() => setLevel(level === 1 ? 0 : 1)}>Mehr Erklärung</Toggle>
        <Toggle open={level === 2} onClick={() => setLevel(level === 2 ? 0 : 2)}>Technische Details</Toggle>
      </div>

      <AnimatePresence initial={false} mode="wait">
        {level === 1 && (
          <Panel key="more">
            <Rows rows={card.more} />
            <p className="eyebrow mb-3 mt-6">Wo es scheitert</p>
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
