import { AlertTriangle } from 'lucide-react'

export function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`animate-pulse rounded-xl bg-white/[0.04] ${className}`} />
}

export function ErrorNote({ error }: { error: Error }) {
  return (
    <div role="alert" className="panel flex items-start gap-3 p-5 text-sm text-ink-2">
      <AlertTriangle className="mt-0.5 size-4 shrink-0 text-rust" />
      <div>
        <p className="font-medium text-ink">Data could not be loaded</p>
        <p className="mt-1">{error.message}</p>
      </div>
    </div>
  )
}
