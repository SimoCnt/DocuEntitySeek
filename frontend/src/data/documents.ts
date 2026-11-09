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

export const MOCK_DOCUMENTS: DocumentSummary[] = [
    {
        id: 'disciplinare-palermo-2027',
        name: 'Disciplinare_di_gara.pdf',
        category: 'Disciplinare',
        pages: 48,
        status: 'READY',
        uploadedAt: '09/11/2026',
    },
    {
        id: 'capitolato-servizi-cloud',
        name: 'Capitolato_servizi_cloud.pdf',
        category: 'Capitolato',
        pages: 72,
        status: 'PROCESSING',
        uploadedAt: '09/11/2026',
    },
    {
        id: 'contratto-servizio-demo',
        name: 'Contratto_servizio_demo.pdf',
        category: 'Contratto',
        pages: 31,
        status: 'ERROR',
        uploadedAt: '08/11/2026',
    },
]