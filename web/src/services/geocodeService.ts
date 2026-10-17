/**
 * Place search via OpenStreetMap Nominatim (public instance, max 1 request/s,
 * attribution required). Swap for a self-hosted geocoder in production.
 */
export type Place = { id: string; name: string; detail: string; center: [number, number]; bbox?: [number, number, number, number] }

type NominatimHit = { place_id: number; display_name: string; lat: string; lon: string; boundingbox?: [string, string, string, string] }

export async function searchPlaces(query: string, signal?: AbortSignal): Promise<Place[]> {
  const q = query.trim()
  if (q.length < 2) return []
  const url = `https://nominatim.openstreetmap.org/search?format=json&limit=6&q=${encodeURIComponent(q)}`
  const res = await fetch(url, { signal, headers: { Accept: 'application/json' } })
  if (!res.ok) throw new Error(`Place search failed (HTTP ${res.status}).`)
  const hits = (await res.json()) as NominatimHit[]
  return hits.map((h) => {
    const [name, ...rest] = h.display_name.split(', ')
    const b = h.boundingbox?.map(Number)
    return {
      id: String(h.place_id),
      name,
      detail: rest.slice(0, 3).join(', '),
      center: [Number(h.lon), Number(h.lat)],
      bbox: b ? [b[2], b[0], b[3], b[1]] : undefined,
    }
  })
}
