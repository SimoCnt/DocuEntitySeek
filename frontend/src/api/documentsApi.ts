import { requestJson } from './http'
import type { DocumentCategory, DocumentDetailResponse, DocumentSummary } from '../types/document'


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


export function createDocument(file: File, category: DocumentCategory, token: string, signal?: AbortSignal) {
    const form = new FormData()

    form.append('file', file)
    form.append('category', category)

    return requestJson<DocumentSummary>('/documents', {
        method: 'POST',
        body: form,
        token,
        signal,
    })
}