import { requestJson } from './http'
import type { AnalysisDetail, AnalysisStartResponse, AnalysisSummary } from '../types/analysis'


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


export function getDocumentAnalyses(documentId: string, token: string, signal?: AbortSignal) {
    return requestJson<AnalysisSummary[]>(`/documents/${encodeURIComponent(documentId)}/analyses`, {
        method: 'GET',
        token,
        signal,
    })
}


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