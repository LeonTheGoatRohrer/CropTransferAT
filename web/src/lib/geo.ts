import type { FieldGeometry, Polygon } from '../api/types'

const R = 6371008.8
const rad = (d: number) => (d * Math.PI) / 180

/** Local equirectangular projection around a latitude: degrees -> metres. */
export function metresPerDegree(lat: number) {
  return { x: (Math.PI / 180) * R * Math.cos(rad(lat)), y: (Math.PI / 180) * R }
}

export function ringOf(p: Polygon): number[][] {
  return p.coordinates[0]
}

/** Outer rings of all parts. */
export function outerRings(g: FieldGeometry): number[][][] {
  return g.type === 'Polygon' ? [g.coordinates[0]] : g.coordinates.map((poly) => poly[0])
}

export function bbox(p: FieldGeometry): [number, number, number, number] {
  let [x0, y0, x1, y1] = [Infinity, Infinity, -Infinity, -Infinity]
  for (const [x, y] of outerRings(p).flat()) {
    x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y)
  }
  return [x0, y0, x1, y1]
}

export function centroid(p: FieldGeometry): [number, number] {
  const [x0, y0, x1, y1] = bbox(p)
  return [(x0 + x1) / 2, (y0 + y1) / 2]
}

/** Planar area of the outer ring in m² (accurate enough for fields). */
export function areaM2(p: Polygon): number {
  const ring = ringOf(p)
  const lat = centroid(p)[1]
  const k = metresPerDegree(lat)
  let a = 0
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    a += ring[j][0] * k.x * ring[i][1] * k.y - ring[i][0] * k.x * ring[j][1] * k.y
  }
  return Math.abs(a / 2)
}

export function pointInPolygon(x: number, y: number, p: Polygon): boolean {
  const ring = ringOf(p)
  let inside = false
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i]
    const [xj, yj] = ring[j]
    if (yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside
  }
  return inside
}

/** Square cell polygons (lon/lat) around cell centres, for map layers. */
export function cellSquare(lon: number, lat: number, sizeM: number): number[][] {
  const k = metresPerDegree(lat)
  const dx = sizeM / 2 / k.x
  const dy = sizeM / 2 / k.y
  return [[lon - dx, lat - dy], [lon + dx, lat - dy], [lon + dx, lat + dy], [lon - dx, lat + dy], [lon - dx, lat - dy]]
}

export function hashPolygon(p: Polygon): number {
  let h = 2166136261
  for (const [x, y] of ringOf(p)) {
    for (const v of [x, y]) {
      const s = v.toFixed(5)
      for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619)
    }
  }
  return h >>> 0
}

/** Small deterministic PRNG (mulberry32). */
export function rng(seed: number) {
  let a = seed >>> 0
  return () => {
    a = (a + 0x6d2b79f5) >>> 0
    let t = a
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}
