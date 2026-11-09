import { getJson } from './http'
import type { DocumentDetailResponse, DocumentSummary } from '../types/document'


export function getDocuments(signal?: AbortSignal) {
    return getJson<DocumentSummary[]>('/documents.json', signal)
}


export function getDocumentDetail(documentId: string, signal?: AbortSignal) {
    const safeDocumentId = encodeURIComponent(documentId)
    return getJson<DocumentDetailResponse>(`/documents/${safeDocumentId}.json`, signal)
}