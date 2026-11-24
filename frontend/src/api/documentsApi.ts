/**
 * Typed document-list, document-detail, and PDF-upload requests.
 */

import { requestJson } from './http'
import type { DocumentDetailResponse, DocumentSummary } from '../types/document'


/**
 * Fetch document summaries owned by the authenticated user.
 */
export function getDocuments(token: string, signal?: AbortSignal) {
    return requestJson<DocumentSummary[]>('/documents', {
        method: 'GET',
        token,
        signal,
    })
}


/**
 * Fetch detail metadata for one owner-scoped document.
 */
export function getDocumentDetail(documentId: string, token: string, signal?: AbortSignal) {
    return requestJson<DocumentDetailResponse>(`/documents/${encodeURIComponent(documentId)}`, {
        method: 'GET',
        token,
        signal,
    })
}


/**
 * Upload an original PDF with authentication and multipart encoding.
 */
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
