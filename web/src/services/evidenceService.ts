import { getJson } from '../api/client'
import type { Evidence, ExplorerPayload } from '../api/types'

/** Evaluation results of the real model runs (results/ folders). */
export const getEvidence = () => getJson<Evidence>('evidence.json')

/** All 365 maize field-years with measured yield (training data overview). */
export const getExplorer = () => getJson<ExplorerPayload>('explorer.json')
