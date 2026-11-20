export type DocumentStatus =
    | 'UPLOADED'
    | 'READY'
    | 'PROCESSING'
    | 'ERROR'



export type DocumentSummary = {
    id: string
    name: string
    pages: number
    status: DocumentStatus
    uploadedAt: string
}


export type DocumentDetailResponse = {
    document: DocumentSummary
}