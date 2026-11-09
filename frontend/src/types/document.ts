import type { DocumentAnalysis } from './analysis'


export type DocumentStatus =
    | 'READY'
    | 'PROCESSING'
    | 'ERROR'

export type DocumentSummary = {
    id: string
    name: string
    category: string
    pages: number
    status: DocumentStatus
    uploadedAt: string
}

export type DocumentDetailResponse = {
    document: DocumentSummary
    analysis: DocumentAnalysis | null
}