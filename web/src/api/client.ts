/**
 * Minimal data client. Today it reads static JSON exported from the project's
 * results (web/public/data). To connect a backend, point API_BASE at it
 * (VITE_API_BASE) and keep the same response shapes (src/api/types.ts).
 */

const API_BASE: string = import.meta.env.VITE_API_BASE ?? `${import.meta.env.BASE_URL}data`

const cache = new Map<string, Promise<unknown>>()

export class ApiError extends Error {
  readonly status: number
  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

export function getJson<T>(path: string): Promise<T> {
  const url = `${API_BASE}/${path}`
  const hit = cache.get(url)
  if (hit) return hit as Promise<T>
  const p = fetch(url, { headers: { Accept: 'application/json' } }).then(async (res) => {
    if (!res.ok) throw new ApiError(`Could not load ${path} (HTTP ${res.status}).`, res.status)
    const type = res.headers.get('content-type') ?? ''
    if (!type.includes('json')) throw new ApiError(`${path} is missing. Run web/scripts/export_web_data.py.`, 404)
    return (await res.json()) as T
  })
  p.catch(() => cache.delete(url))
  cache.set(url, p)
  return p
}
