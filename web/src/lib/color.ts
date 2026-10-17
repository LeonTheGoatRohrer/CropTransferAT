import { scaleLinear } from 'd3-scale'

/** NDVI ramp from bare soil to dense canopy (matches --color-ndvi-* tokens). */
const NDVI_STOPS = [0.15, 0.3, 0.45, 0.6, 0.72, 0.85]
const NDVI_COLORS = ['#4b3725', '#8a6a36', '#c4a44b', '#9dbb5c', '#55a05a', '#23704a']
export const ndviColor = scaleLinear<string>().domain(NDVI_STOPS).range(NDVI_COLORS).clamp(true)
export const NDVI_LEGEND = NDVI_STOPS.map((v, i) => ({ v, c: NDVI_COLORS[i] }))

/** Relative yield (share of field mean): rust below 0.85, neutral at 1, gold above. */
export const relYieldColor = scaleLinear<string>()
  .domain([0.4, 0.85, 1.0, 1.25])
  .range(['#7a2a1a', '#e4694a', '#c9c3a6', '#e6b450'])
  .clamp(true)

export const tokens = {
  ink: '#eceee6',
  ink2: '#b3baae',
  ink3: '#7c8679',
  ink4: '#566053',
  line: 'rgba(236,238,230,0.08)',
  lineStrong: 'rgba(236,238,230,0.16)',
  maize: '#e6b450',
  rust: '#e4694a',
  water: '#72aad9',
  sage: '#8fb59a',
  soil800: '#19211a',
}
