/**
 * Interpret standardized analysis quota and execution failure payloads.
 */

import type { RequestError } from '../api/http'
import type { AnalysisFailedDetails, AnalysisQuotaExceededDetails } from '../types/analysis'


/**
 * Check whether record.
 */
function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}


/**
 * Extract quota limit and reset metadata from an analysis error.
 */
export function getAnalysisQuotaExceededDetails(error: RequestError): AnalysisQuotaExceededDetails | null {
  if (error.code !== 'ANALYSIS_QUOTA_EXCEEDED' || !isRecord(error.details)) {
    return null
  }

  const { dailyLimit, used, resetsAt } = error.details

  if (typeof dailyLimit !== 'number' || typeof used !== 'number' || typeof resetsAt !== 'string') {
    return null
  }

  return { dailyLimit, used, resetsAt }
}


/**
 * Extract the analysis identifier from a failed execution response.
 */
export function getAnalysisFailedDetails(error: RequestError): AnalysisFailedDetails | null {
  if (error.code !== 'ANALYSIS_FAILED' || !isRecord(error.details)) {
    return null
  }

  const { analysisId } = error.details

  if (typeof analysisId !== 'string') {
    return null
  }

  return { analysisId }
}
