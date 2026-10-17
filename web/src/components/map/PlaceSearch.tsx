import { Loader2, Search } from 'lucide-react'
import { useEffect, useState } from 'react'
import { searchPlaces, type Place } from '../../services/geocodeService'

export function PlaceSearch({ onPick, countryCode }: { onPick: (p: Place) => void; countryCode?: string }) {
  const [q, setQ] = useState('')
  const [hits, setHits] = useState<Place[]>([])
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    if (q.trim().length < 3) {
      setHits([])
      return
    }
    const ctrl = new AbortController()
    const t = setTimeout(() => {
      setBusy(true)
      searchPlaces(q, ctrl.signal, countryCode)
        .then((h) => {
          setHits(h)
          setErr(null)
          setOpen(true)
        })
        .catch((e: Error) => e.name !== 'AbortError' && setErr('Place search is unavailable offline.'))
        .finally(() => setBusy(false))
    }, 450)
    return () => {
      clearTimeout(t)
      ctrl.abort()
    }
  }, [q, countryCode])

  return (
    <div className="pointer-events-auto relative w-full max-w-[340px]">
      <div className="panel-glass flex h-10 items-center gap-2 px-3">
        {busy ? <Loader2 className="size-4 animate-spin text-ink-3" /> : <Search className="size-4 text-ink-3" />}
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onFocus={() => hits.length && setOpen(true)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && hits[0]) {
              onPick(hits[0])
              setOpen(false)
            }
            if (e.key === 'Escape') setOpen(false)
          }}
          placeholder="Search a place, e.g. Leibnitz"
          aria-label="Search a place"
          className="h-full w-full bg-transparent text-[13.5px] text-ink placeholder:text-ink-4 focus:outline-none"
        />
      </div>
      {(open && hits.length > 0) || err ? (
        <div className="panel-glass absolute inset-x-0 top-12 z-20 overflow-hidden p-1">
          {err ? (
            <p className="px-3 py-2 text-[12.5px] text-ink-3">{err}</p>
          ) : (
            hits.map((h) => (
              <button
                key={h.id}
                type="button"
                onClick={() => {
                  onPick(h)
                  setOpen(false)
                  setQ(h.name)
                }}
                className="block w-full rounded-lg px-3 py-2 text-left hover:bg-white/[0.06]"
              >
                <span className="block text-[13.5px] text-ink">{h.name}</span>
                <span className="block truncate text-[11.5px] text-ink-3">{h.detail}</span>
              </button>
            ))
          )}
          <p className="px-3 pb-1 pt-1.5 text-[10px] text-ink-4">Search © OpenStreetMap contributors (Nominatim)</p>
        </div>
      ) : null}
    </div>
  )
}
