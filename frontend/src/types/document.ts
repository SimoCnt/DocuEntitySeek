export type DocumentStatus =
    | 'READY'
    | 'PROCESSING'
    | 'ERROR'


export type DocumentCategory =
    | 'DISCIPLINARE'
    | 'CAPITOLATO'
    | 'CONTRATTO'
    | 'BANDO'
    | 'ALTRO'


export type DocumentSummary = {
    id: string
    name: string
    category: DocumentCategory
    pages: number
    status: DocumentStatus
    uploadedAt: string
}


export type DocumentDetailResponse = {
    document: DocumentSummary
}