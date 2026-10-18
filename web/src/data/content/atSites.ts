/**
 * The six Austrian trial sites with the longest yield records in the project
 * (data/raw/at_trials.csv: variety-trial site means of the Landwirtschaftskammern).
 * Positions are approximate municipality centres, not field locations.
 */
export type AtSite = { id: string; name: string; region: string; lngLat: [number, number]; years: number; from: number; to: number; meanTHa: number }

export const AT_SITES: AtSite[] = [
  { id: 'wagna', name: 'Wagna', region: 'Steiermark', lngLat: [15.56, 46.77], years: 13, from: 2012, to: 2024, meanTHa: 9.0 },
  { id: 'walding', name: 'Walding', region: 'Oberösterreich', lngLat: [14.16, 48.35], years: 12, from: 2014, to: 2026, meanTHa: 12.5 },
  { id: 'mauthausen', name: 'Mauthausen', region: 'Oberösterreich', lngLat: [14.5, 48.24], years: 11, from: 2013, to: 2025, meanTHa: 12.4 },
  { id: 'kalsdorf', name: 'Kalsdorf bei Ilz', region: 'Steiermark', lngLat: [15.93, 47.05], years: 10, from: 2013, to: 2024, meanTHa: 12.3 },
  { id: 'wimsbach', name: 'Bad Wimsbach', region: 'Oberösterreich', lngLat: [13.92, 48.03], years: 11, from: 2015, to: 2026, meanTHa: 12.7 },
  { id: 'linden', name: 'Linden', region: 'Oberösterreich', lngLat: [14.02, 48.1], years: 13, from: 2013, to: 2026, meanTHa: 11.6 },
]

/** [west, south, east, north] */
export const AUSTRIA_BOUNDS: [number, number, number, number] = [9.45, 46.3, 17.25, 49.1]
