import type { RequestError } from '../api/http'
import type { AnalysisFailedDetails, AnalysisQuotaExceededDetails } from '../types/analysis'


function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}


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