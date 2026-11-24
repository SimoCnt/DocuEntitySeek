/**
 * Typed HTTP client functions for starting analyses and reading their history and results.
 */

import { requestJson } from './http'
import type { AnalysisDetail, AnalysisStartResponse, AnalysisSummary } from '../types/analysis'


/**
 * Submit an analysis using the specified extraction schema version.
 */
export function startAnalysis(
  documentId: string,
  token: string,
  schemaVersionId?: string,
  signal?: AbortSignal,
) {
  return requestJson<AnalysisStartResponse>(
    `/documents/${encodeURIComponent(documentId)}/analyses`,
    {
      method: 'POST',
      token,
      signal,
      body: JSON.stringify({ schemaVersionId: schemaVersionId ?? null }),
      headers: { 'Content-Type': 'application/json' },
    },
  )
}


/**
 * Retrieve an owned document's analysis history.
 */
export function getDocumentAnalyses(documentId: string, token: string, signal?: AbortSignal) {
    return requestJson<AnalysisSummary[]>(`/documents/${encodeURIComponent(documentId)}/analyses`, {
        method: 'GET',
        token,
        signal,
    })
}


/**
 * Retrieve analysis status and extraction results for a document.
 */
export function getAnalysis(documentId: string, analysisId: string, token: string, signal?: AbortSignal) {
    return requestJson<AnalysisDetail>(
        `/documents/${encodeURIComponent(documentId)}/analyses/${encodeURIComponent(analysisId)}`,
        {
            method: 'GET',
            token,
            signal,
        },
    )
}
