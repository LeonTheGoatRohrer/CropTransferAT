import { AnimatePresence, motion, useReducedMotion } from 'motion/react'
import { Pause, Play } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import type { FieldAnalysis } from '../../api/types'
import { NDVI_LEGEND, relYieldColor } from '../../lib/color'
import { N_DEKADS, dekadLabel, monthTicks } from '../../lib/dekads'
import { fmt, fmtPct } from '../../lib/format'
import { Tabs } from '../ui/Tabs'
import { filledSeries } from '../../lib/series'
import { PixelField, type PixelMode } from './PixelField'

const LAST_SEASON_DEKAD = 17 // ~ 20 Sep
const STEP_MS = 420

type Stage = 'season' | 'yield' | 'weak'

/** Hero: one real field moving through its season, then revealing measured yield and the flagged zones. */
export function HeroField({ field }: { field: FieldAnalysis }) {
  const { t } = useTranslation()
  const px = field.pixels!
  const reduce = useReducedMotion()
  const [stage, setStage] = useState<Stage>('season')
  const [dekad, setDekad] = useState(reduce ? 12 : 3)
  const [playing, setPlaying] = useState(!reduce)

  // Autoplay loop: season (Apr → Sep) → measured yield → flagged zones → repeat.
  useEffect(() => {
    if (!playing) return
    let timer: ReturnType<typeof setTimeout>
    if (stage === 'season') {
      timer = setTimeout(() => {
        if (dekad < LAST_SEASON_DEKAD) setDekad((d) => d + 1)
        else setStage('yield')
      }, dekad === LAST_SEASON_DEKAD ? 900 : STEP_MS)
    } else if (stage === 'yield') timer = setTimeout(() => setStage('weak'), 3200)
    else
      timer = setTimeout(() => {
        setStage('season')
        setDekad(3)
      }, 4200)
    return () => clearTimeout(timer)
  }, [playing, stage, dekad])

  const filled = useMemo(() => (px.ndvi_by_dekad ? filledSeries(px.ndvi_by_dekad) : null), [px])
  const meanNdvi = useMemo(() => {
    const vals = (filled?.[dekad] ?? []).filter((v) => Number.isFinite(v))
    return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : null
  }, [filled, dekad])
  const observed = (px.ndvi_by_dekad?.[dekad] ?? []).some((v) => v != null)
  const ref = field.reference.ndvi.median[dekad]
  const mode: PixelMode = stage

  return (
    <div className="panel grain relative overflow-hidden p-4 sm:p-5">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setPlaying((p) => !p)}
            className="inline-flex size-8 items-center justify-center rounded-full border border-[var(--line-strong)] text-ink-2 transition hover:border-ink-3 hover:text-ink"
            aria-label={playing ? t('home.hero.pause') : t('home.hero.play')}
          >
            {playing ? <Pause className="size-3.5" /> : <Play className="size-3.5 translate-x-px" />}
          </button>
          <span className="font-mono text-[11px] uppercase tracking-[0.12em] text-ink-3">
            {field.site} · {field.field_id.replace(/_/g, '-')} · {field.year}
          </span>
        </div>
        <Tabs
          size="sm"
          label={t('home.hero.view')}
          value={stage}
          onChange={(v) => {
            setPlaying(false)
            setStage(v)
          }}
          items={[
            { value: 'season', label: t('home.hero.season') },
            { value: 'yield', label: t('home.hero.yield') },
            { value: 'weak', label: t('home.hero.flagged') },
          ]}
        />
      </div>

      <div className="relative rounded-xl bg-black/30 p-3 sm:p-5">
        <PixelField pixels={px} mode={mode} dekad={dekad} maxHeight={330} ariaLabel={t('home.hero.aria', { id: field.field_id, n: px.n_cells })} />
        <AnimatePresence mode="wait">
          <motion.div
            key={stage}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.35 }}
            className="panel-glass relative z-10 mt-3 inline-block px-3 py-2 sm:absolute sm:left-5 sm:top-5 sm:mt-0"
          >
            {stage === 'season' && (
              <>
                <p className="eyebrow !text-[10px]">{dekadLabel(dekad, field.year)}</p>
                <p className="font-mono text-[13px] tabular text-ink">
                  NDVI {fmt(meanNdvi, 2)} <span className="text-ink-3">· {t('home.hero.healthy')} {fmt(ref, 2)}</span>
                </p>
                {!observed && <p className="text-[11px] text-ink-3">{t('home.hero.noScene')}</p>}
              </>
            )}
            {stage === 'yield' && (
              <>
                <p className="eyebrow !text-[10px]">{t('home.hero.yieldMap')}</p>
                <p className="font-mono text-[13px] tabular text-ink">
                  {fmt(field.measured.yield_t_ha, 1)} t/ha <span className="text-ink-3">· {t('home.hero.ofNormal', { v: fmtPct(field.measured.relative_yield) })}</span>
                </p>
              </>
            )}
            {stage === 'weak' && (
              <>
                <p className="eyebrow !text-[10px]">{t('home.hero.weakQuarter')}</p>
                <p className="font-mono text-[13px] tabular text-ink">
                  {t('home.hero.trulyLow', { v: fmtPct(px.precision_weak) })} <span className="text-ink-3">· {t('home.hero.fieldShare', { v: fmtPct(px.prevalence_problem) })}</span>
                </p>
              </>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Season scrubber on the shared dekad axis */}
      <div className="mt-4">
        <input
          type="range"
          min={0}
          max={N_DEKADS - 1}
          value={dekad}
          aria-label={t('home.hero.seasonDate')}
          onChange={(e) => {
            setPlaying(false)
            setStage('season')
            setDekad(Number(e.target.value))
          }}
          className="h-1 w-full cursor-pointer appearance-none rounded-full bg-white/10 accent-[var(--color-maize)]"
        />
        <div className="mt-2 flex justify-between font-mono text-[10px] uppercase tracking-[0.1em] text-ink-4">
          {monthTicks().map((m) => (
            <span key={m.label}>{m.label}</span>
          ))}
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-[var(--line)] pt-4">
        {stage === 'yield' ? (
          <div className="flex items-center gap-2 text-[11px] text-ink-3">
            <span className="font-mono">{t('home.hero.yieldVsMean')}</span>
            {[0.5, 0.85, 1, 1.2].map((v) => (
              <span key={v} className="flex items-center gap-1">
                <span className="size-2.5 rounded-[2px]" style={{ background: relYieldColor(v) }} />
                {fmt(v * 100, 0)} %
              </span>
            ))}
          </div>
        ) : stage === 'weak' ? (
          <div className="flex items-center gap-3 text-[11px] text-ink-3">
            <span className="flex items-center gap-1.5"><span className="size-2.5 rounded-[2px] bg-rust" />{t('home.hero.flaggedCell')}</span>
            <span className="font-mono">{t('home.hero.rho', { v: fmt(px.rho, 2) })}</span>
          </div>
        ) : (
          <div className="flex items-center gap-1.5 text-[11px] text-ink-3">
            <span className="font-mono">NDVI</span>
            {NDVI_LEGEND.map((s) => (
              <span key={s.v} className="h-2.5 w-5 first:rounded-l-[3px] last:rounded-r-[3px]" style={{ background: s.c }} />
            ))}
            <span className="font-mono">{fmt(0.15, 2)} → {fmt(0.85, 2)}</span>
          </div>
        )}
        <span className="font-mono text-[10.5px] text-ink-4">{t('home.hero.realData', { n: px.n_cells })}</span>
      </div>
    </div>
  )
}
