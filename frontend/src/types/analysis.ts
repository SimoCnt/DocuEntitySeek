export type AnalysisStatus = 'QUEUED' | 'PROCESSING' | 'READY' | 'ERROR'
export type ExtractedFieldStatus = 'EXTRACTED' | 'AMBIGUOUS' | 'NOT_FOUND' | 'ERROR'


export type AnalysisPipelineSummary = {
    pageCount: number
    documentCharacters: number
    entityCount: number
    visibleEntityCount: number
    hiddenEntityCount: number
    rejectedEntityCount: number
    fieldCount: number
    fieldCandidateCount: number
    extractedFieldCount: number
    ambiguousFieldCount: number
    notFoundFieldCount: number
    rejectedFieldCandidateCount: number
    elapsedMs: number
}

export type AnalysisStartResponse = {
    analysisId: string
    status: AnalysisStatus
    pipeline: AnalysisPipelineSummary
}

export type AnalysisSummary = {
    id: string
    documentId: string
    status: AnalysisStatus
    createdAt: string
    startedAt: string | null
    completedAt: string | null
    errorMessage: string | null
    schemaVersionId: string
    aiRuntimeConfigId: string
}

export type AnalysisResultPage = {
    pageNumber: number
    text: string
    globalStart: number
    globalEnd: number
}


export type EntityOccurrence = {
    id: string
    label: string
    text: string
    confidence: number
    globalStart: number
    globalEnd: number
    page: number
    pageStart: number
    pageEnd: number
    isVisible: boolean
}


export type FieldCandidate = {
    id: string
    value: string
    confidence: number
    page: number | null
    globalStart: number
    globalEnd: number
    rank: number
}


export type AnalysisExtractedField = {
    id: string
    fieldKey: string
    status: ExtractedFieldStatus
    value: string | null
    confidence: number | null
    page: number | null
    globalStart: number | null
    globalEnd: number | null
    candidates: FieldCandidate[]
}


export type AnalysisResult = {
    pages: AnalysisResultPage[]
    entities: EntityOccurrence[]
    fields: AnalysisExtractedField[]
}


export type AnalysisDetail = AnalysisSummary & {
    result: AnalysisResult | null
}


export type AnalysisQuotaExceededDetails = {
    dailyLimit: number
    used: number
    resetsAt: string
}


export type AnalysisFailedDetails = {
    analysisId: string
}