import * as maplibregl from 'maplibre-gl'
import type { GeoJSONSource, LngLatBoundsLike, Map as MlMap, MapLayerMouseEvent } from 'maplibre-gl'
import { useEffect, useRef, useState } from 'react'
import { TerraDraw, TerraDrawPolygonMode, TerraDrawSelectMode } from 'terra-draw'
import { TerraDrawMapLibreGLAdapter } from 'terra-draw-maplibre-gl-adapter'
import type { FieldGeometry, Polygon } from '../../api/types'
import { bbox } from '../../lib/geo'
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url'

// MapLibre 6 resolves its worker relative to its own module; give it the bundled worker instead.
maplibregl.setWorkerUrl(workerUrl)

export type Basemap = 'satellite' | 'sentinel' | 'terrain'

export type MapField = { id: string; label: string; geometry: FieldGeometry; role: string }

export type CellOverlay = { type: 'FeatureCollection'; features: GeoJSON.Feature<GeoJSON.Polygon, { color: string; opacity: number }>[] }

type Props = {
  fields: MapField[]
  selectedId: string | null
  selectedGeometry: FieldGeometry | null
  overlay: CellOverlay | null
  basemap: Basemap
  drawing: boolean
  onSelectField: (id: string) => void
  onPolygon: (p: Polygon | null) => void
  flyTo: { center: [number, number]; zoom?: number; bbox?: [number, number, number, number]; key: number } | null
  className?: string
}

const RASTERS: Record<Basemap, { tiles: string[]; maxzoom: number; attribution: string }> = {
  satellite: {
    tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],
    maxzoom: 19,
    attribution: 'Imagery © Esri, Maxar, Earthstar Geographics',
  },
  sentinel: {
    tiles: ['https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2020_3857/default/g/{z}/{y}/{x}.jpg'],
    maxzoom: 15,
    attribution: 'Sentinel-2 cloudless 2020 by EOX IT Services GmbH (contains modified Copernicus Sentinel data 2020)',
  },
  terrain: {
    tiles: ['https://a.tile.opentopomap.org/{z}/{x}/{y}.png', 'https://b.tile.opentopomap.org/{z}/{x}/{y}.png'],
    maxzoom: 17,
    attribution: '© OpenStreetMap contributors, SRTM · style © OpenTopoMap (CC-BY-SA)',
  },
}

const EMPTY: GeoJSON.FeatureCollection = { type: 'FeatureCollection', features: [] }

function boundsOf(p: FieldGeometry): LngLatBoundsLike {
  const [x0, y0, x1, y1] = bbox(p)
  return [[x0, y0], [x1, y1]]
}

/** MapLibre map with satellite basemaps, prepared fields, a 10-m cell overlay and polygon drawing. */
export function FieldMap({ fields, selectedId, selectedGeometry, overlay, basemap, drawing, onSelectField, onPolygon, flyTo, className = '' }: Props) {
  const el = useRef<HTMLDivElement>(null)
  const map = useRef<MlMap | null>(null)
  const draw = useRef<TerraDraw | null>(null)
  const [ready, setReady] = useState(false)
  const silent = useRef(false) // true while the map clears drawings itself
  const cb = useRef({ onSelectField, onPolygon })
  cb.current = { onSelectField, onPolygon }

  // Mount once.
  useEffect(() => {
    if (!el.current) return
    const m = new maplibregl.Map({
      container: el.current,
      style: {
        version: 8,
        sources: Object.fromEntries(
          (Object.keys(RASTERS) as Basemap[]).map((k) => [k, { type: 'raster', tiles: RASTERS[k].tiles, tileSize: 256, maxzoom: RASTERS[k].maxzoom, attribution: RASTERS[k].attribution }]),
        ),
        layers: [
          { id: 'bg', type: 'background', paint: { 'background-color': '#121812' } },
          ...(Object.keys(RASTERS) as Basemap[]).map((k) => ({
            id: `base-${k}`,
            type: 'raster' as const,
            source: k,
            layout: { visibility: (k === 'satellite' ? 'visible' : 'none') as 'visible' | 'none' },
            paint: { 'raster-fade-duration': 250, 'raster-saturation': k === 'terrain' ? -0.35 : -0.08, 'raster-brightness-max': k === 'terrain' ? 0.85 : 0.92 },
          })),
        ],
      },
      center: [-76.9, 39.02],
      zoom: 12.4,
      attributionControl: { compact: true },
      maxPitch: 0,
      dragRotate: false,
    })
    m.touchZoomRotate.disableRotation()
    m.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right')
    m.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-left')

    m.on('load', () => {
      m.addSource('fields', { type: 'geojson', data: EMPTY })
      m.addSource('cells', { type: 'geojson', data: EMPTY })
      m.addSource('selected', { type: 'geojson', data: EMPTY })
      m.addLayer({ id: 'fields-fill', type: 'fill', source: 'fields', paint: { 'fill-color': '#e6b450', 'fill-opacity': ['case', ['boolean', ['feature-state', 'hover'], false], 0.28, 0.12] } })
      m.addLayer({ id: 'fields-line', type: 'line', source: 'fields', paint: { 'line-color': '#e6b450', 'line-width': 1.4, 'line-opacity': 0.8 } })
      m.addLayer({ id: 'cells', type: 'fill', source: 'cells', paint: { 'fill-color': ['get', 'color'], 'fill-opacity': ['get', 'opacity'], 'fill-antialias': false } })
      m.addLayer({ id: 'selected-glow', type: 'line', source: 'selected', paint: { 'line-color': '#e6b450', 'line-width': 8, 'line-opacity': 0.18, 'line-blur': 4 } })
      m.addLayer({ id: 'selected-line', type: 'line', source: 'selected', paint: { 'line-color': '#f1cf86', 'line-width': 2 } })
      let hovered: string | number | undefined
      m.on('mousemove', 'fields-fill', (e: MapLayerMouseEvent) => {
        if (draw.current?.getMode() === 'polygon') return
        m.getCanvas().style.cursor = 'pointer'
        const id = e.features?.[0]?.id
        if (hovered != null) m.setFeatureState({ source: 'fields', id: hovered }, { hover: false })
        hovered = id
        if (id != null) m.setFeatureState({ source: 'fields', id }, { hover: true })
      })
      m.on('mouseleave', 'fields-fill', () => {
        m.getCanvas().style.cursor = ''
        if (hovered != null) m.setFeatureState({ source: 'fields', id: hovered }, { hover: false })
        hovered = undefined
      })
      m.on('click', 'fields-fill', (e: MapLayerMouseEvent) => {
        if (draw.current?.getMode() === 'polygon') return
        const fid = e.features?.[0]?.properties?.fid
        if (fid) cb.current.onSelectField(String(fid))
      })

      const td = new TerraDraw({
        adapter: new TerraDrawMapLibreGLAdapter({ map: m }),
        modes: [
          new TerraDrawPolygonMode({
            styles: { fillColor: '#e6b450', fillOpacity: 0.16, outlineColor: '#f1cf86', outlineWidth: 2, closingPointColor: '#e6b450', closingPointWidth: 5, closingPointOutlineColor: '#0b0f0c', closingPointOutlineWidth: 1 },
          }),
          new TerraDrawSelectMode({
            flags: { polygon: { feature: { draggable: true, coordinates: { midpoints: { draggable: true }, draggable: true, deletable: true } } } },
            styles: { selectedPolygonColor: '#e6b450', selectedPolygonFillOpacity: 0.14, selectedPolygonOutlineColor: '#f1cf86', selectedPolygonOutlineWidth: 2, selectionPointColor: '#f1cf86', selectionPointWidth: 5, selectionPointOutlineColor: '#0b0f0c', midPointColor: '#e6b450', midPointWidth: 3 },
          }),
        ],
      })
      td.start()
      td.setMode('select')
      const emit = () => {
        const poly = td.getSnapshot().find((f) => f.geometry.type === 'Polygon')
        cb.current.onPolygon(poly ? (poly.geometry as Polygon) : null)
      }
      td.on('finish', (id, ctx) => {
        if (ctx.action === 'draw') {
          // keep a single drawn field
          const others = td.getSnapshot().filter((f) => f.id !== id).map((f) => f.id as string)
          silent.current = true
          if (others.length) td.removeFeatures(others)
          silent.current = false
          td.setMode('select')
          td.selectFeature(id)
        }
        emit()
      })
      td.on('change', (_ids, type) => {
        if (type === 'delete' && !silent.current) emit()
      })
      draw.current = td
      setReady(true)
    })

    map.current = m
    return () => {
      draw.current?.stop()
      draw.current = null
      m.remove()
      map.current = null
    }
  }, [])

  // Basemap switch.
  useEffect(() => {
    const m = map.current
    if (!m || !ready) return
    ;(Object.keys(RASTERS) as Basemap[]).forEach((k) => m.setLayoutProperty(`base-${k}`, 'visibility', k === basemap ? 'visible' : 'none'))
  }, [basemap, ready])

  // Prepared fields.
  useEffect(() => {
    const m = map.current
    if (!m || !ready) return
    ;(m.getSource('fields') as GeoJSONSource).setData({
      type: 'FeatureCollection',
      features: fields.map((f, i) => ({ type: 'Feature', id: i + 1, geometry: f.geometry, properties: { fid: f.id, label: f.label } })),
    })
  }, [fields, ready])

  // Selected field outline + fit.
  useEffect(() => {
    const m = map.current
    if (!m || !ready) return
    ;(m.getSource('selected') as GeoJSONSource).setData(
      selectedGeometry && selectedId ? { type: 'Feature', geometry: selectedGeometry, properties: {} } : EMPTY,
    )
    if (selectedGeometry && selectedId) {
      m.fitBounds(boundsOf(selectedGeometry), { padding: { top: 90, bottom: 90, left: 60, right: 60 }, maxZoom: 17.2, duration: 1400, essential: true })
    }
  }, [selectedId, selectedGeometry, ready])

  // 10-m cell overlay.
  useEffect(() => {
    const m = map.current
    if (!m || !ready) return
    ;(m.getSource('cells') as GeoJSONSource).setData(overlay ?? EMPTY)
  }, [overlay, ready])

  // Drawing mode.
  useEffect(() => {
    const td = draw.current
    if (!td || !ready) return
    if (drawing) {
      silent.current = true
      td.clear()
      silent.current = false
      td.setMode('polygon')
      map.current!.getCanvas().style.cursor = 'crosshair'
    } else if (td.getMode() === 'polygon') {
      td.setMode('select')
      map.current!.getCanvas().style.cursor = ''
    }
  }, [drawing, ready])

  // Remove the drawn polygon when a prepared field is selected.
  useEffect(() => {
    if (selectedId && draw.current && ready && draw.current.getSnapshot().length) {
      silent.current = true
      draw.current.clear()
      silent.current = false
    }
  }, [selectedId, ready])

  // Search result fly-to.
  useEffect(() => {
    const m = map.current
    if (!m || !ready || !flyTo) return
    if (flyTo.bbox) {
      const [x0, y0, x1, y1] = flyTo.bbox
      m.fitBounds([[x0, y0], [x1, y1]], { padding: 40, maxZoom: 15, duration: 1600 })
    } else m.flyTo({ center: flyTo.center, zoom: flyTo.zoom ?? 14, duration: 1600 })
  }, [flyTo, ready])

  return <div ref={el} className={`h-full w-full ${className}`} aria-label="Field map" role="region" />
}
