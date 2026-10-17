import { AnimatePresence, motion } from 'motion/react'
import { Check, CloudSun, Cpu, Layers, Mountain, Satellite, Sigma } from 'lucide-react'
import type { ReactNode } from 'react'
import { PIPELINE, STAGE_TITLES, type AnalysisState, type PipelineStage } from '../../state/analysisMachine'

const ICONS: Record<PipelineStage, ReactNode> = {
  loadingSatellite: <Satellite className="size-4" />,
  processingSatellite: <Layers className="size-4" />,
  loadingWeather: <CloudSun className="size-4" />,
  loadingEnvironment: <Mountain className="size-4" />,
  featureEngineering: <Sigma className="size-4" />,
  runningModel: <Cpu className="size-4" />,
}

/** Pipeline as a vertical sequence of stages that fill with real facts as they finish. */
export function PipelinePanel({ state }: { state: AnalysisState }) {
  const activeIdx = PIPELINE.indexOf(state.status as PipelineStage)
  return (
    <ol className="relative flex flex-col">
      {PIPELINE.map((stage, i) => {
        const facts = state.facts[stage]
        const done = Boolean(facts)
        const active = activeIdx === i
        const pending = !done && !active
        return (
          <li key={stage} className="relative flex gap-4 pb-5 last:pb-0">
            {i < PIPELINE.length - 1 && (
              <span className="absolute left-[15px] top-9 bottom-0 w-px bg-[var(--line)]">
                <motion.span className="absolute inset-x-0 top-0 bg-maize/60" initial={false} animate={{ height: done ? '100%' : '0%' }} transition={{ duration: 0.5 }} />
              </span>
            )}
            <span
              className={`relative z-10 mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-full border transition-colors duration-300 ${
                done ? 'border-maize/50 bg-maize/15 text-maize' : active ? 'border-maize text-maize' : 'border-[var(--line-strong)] text-ink-4'
              }`}
            >
              {active && <span className="absolute inset-0 animate-ping rounded-full border border-maize/40" />}
              {done ? <Check className="size-4" /> : ICONS[stage]}
            </span>
            <div className="min-w-0 flex-1">
              <div className="flex items-baseline justify-between gap-3">
                <p className={`text-[14px] font-medium ${pending ? 'text-ink-4' : 'text-ink'}`}>{STAGE_TITLES[stage].title}</p>
                <span className="font-mono text-[10px] uppercase tracking-[0.12em] text-ink-4">{String(i + 1).padStart(2, '0')}</span>
              </div>
              <AnimatePresence mode="wait" initial={false}>
                {active && !done && (
                  <motion.p key="run" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="mt-1 text-[13px] text-ink-3">
                    {STAGE_TITLES[stage].running}
                    <span className="ml-2 inline-block h-[3px] w-16 overflow-hidden rounded-full bg-white/10 align-middle">
                      <motion.span className="block h-full w-1/2 rounded-full bg-maize" animate={{ x: ['-100%', '200%'] }} transition={{ repeat: Infinity, duration: 1.1, ease: 'easeInOut' }} />
                    </span>
                  </motion.p>
                )}
                {done && facts && (
                  <motion.div key="done" initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }}>
                    <p className="mt-1 font-display text-[16px] font-semibold tracking-[-0.01em] text-ink">{facts.headline}</p>
                    <dl className="mt-2 grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-[12px]">
                      {facts.items.map((it) => (
                        <div key={it.label} className="contents">
                          <dt className="text-ink-4">{it.label}</dt>
                          <dd className="text-right font-mono text-ink-2 tabular [overflow-wrap:anywhere]">{it.value}</dd>
                        </div>
                      ))}
                    </dl>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </li>
        )
      })}
    </ol>
  )
}
