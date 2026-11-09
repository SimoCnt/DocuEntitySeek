export type EntityDefinition = {
    label: string
    color: string
}

export type TextSegment =
    | {
        type: 'text'
        text: string
    }
    | {
        type: 'entity'
        id: string
        text: string
        label: string
    }

export type DocumentPage = {
    pageNumber: number
    segments: TextSegment[]
}

export type ExtractedFieldStatus =
    | 'EXTRACTED'
    | 'AMBIGUOUS'
    | 'NOT_FOUND'
    | 'ERROR'

export type ExtractedField = {
    id: string
    label: string
    value: string | null
    page: number | null
    confidence: number | null
    status: ExtractedFieldStatus
}

export type DocumentAnalysis = {
    entityDefinitions: EntityDefinition[]
    pages: DocumentPage[]
    extractedFields: ExtractedField[]
}