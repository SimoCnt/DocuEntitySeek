import { requestJson } from './http'
import type { DocumentDetailResponse, DocumentSummary } from '../types/document'


export function getDocuments(token: string, signal?: AbortSignal) {
    return requestJson<DocumentSummary[]>('/documents', {
        method: 'GET',
        token,
        signal,
    })
}


export function getDocumentDetail(documentId: string, token: string, signal?: AbortSignal) {
    return requestJson<DocumentDetailResponse>(`/documents/${encodeURIComponent(documentId)}`, {
        method: 'GET',
        token,
        signal,
    })
}


export function createDocument(file: File, token: string, signal?: AbortSignal) {
    const form = new FormData()

    form.append('file', file)

    return requestJson<DocumentSummary>('/documents', {
        method: 'POST',
        body: form,
        token,
        signal,
    })
}