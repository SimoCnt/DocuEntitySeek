/**
 * Define TypeScript contracts for analysis lifecycle, NER/IE results, quotas, and PDF highlighting.
 */

/**
 * Persisted analysis state used to control polling and result rendering.
 */
export type AnalysisStatus = 'QUEUED' | 'PROCESSING' | 'READY' | 'ERROR'
/**
 * Allowed values for extracted field status as defined by the API.
 */
export type ExtractedFieldStatus = 'EXTRACTED' | 'AMBIGUOUS' | 'NOT_FOUND' | 'ERROR'


/**
 * Counters and execution duration returned when an analysis completes.
 */
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

/**
 * Execution outcome returned by the synchronous analysis start endpoint.
 */
export type AnalysisStartResponse = {
    analysisId: string
    status: AnalysisStatus
    pipeline: AnalysisPipelineSummary
}

/**
 * Historical analysis metadata with the selected extraction schema name and version.
 */
export type AnalysisSummary = {
    id: string
    documentId: string
    status: AnalysisStatus
    createdAt: string
    startedAt: string | null
    completedAt: string | null
    errorMessage: string | null
    schemaVersionId: string
    schemaName: string
    schemaVersion: number
    aiRuntimeConfigId: string
}

/**
 * A PDF page's extracted text and its global provenance offset range.
 */
export type AnalysisResultPage = {
    pageNumber: number
    text: string
    globalStart: number
    globalEnd: number
}


/**
 * A recognized entity, including page-local text offsets and visibility.
 */
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


/**
 * A ranked alternative value for a structured extraction field.
 */
export type FieldCandidate = {
    id: string
    value: string
    confidence: number
    page: number | null
    globalStart: number
    globalEnd: number
    rank: number
}


/**
 * Resolved value or ambiguity status for one schema-defined field.
 */
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


/**
 * AI result containing source pages, schema definitions, NER spans, and resolved fields.
 */
export type AnalysisResult = {
    schema: AnalysisSchema
    pages: AnalysisResultPage[]
    entities: EntityOccurrence[]
    fields: AnalysisExtractedField[]
}


/**
 * Analysis state and optional results for the selected history entry.
 */
export type AnalysisDetail = AnalysisSummary & {
    result: AnalysisResult | null
}


/**
 * TypeScript contract for analysis quota exceeded details values.
 */
export type AnalysisQuotaExceededDetails = {
    dailyLimit: number
    used: number
    resetsAt: string
}


/**
 * TypeScript contract for analysis failed details values.
 */
export type AnalysisFailedDetails = {
    analysisId: string
}


/**
 * TypeScript contract for analysis entity definition values.
 */
export type AnalysisEntityDefinition = {
    label: string
    description: string
    color: string
    sortOrder: number
}


/**
 * TypeScript contract for analysis field definition values.
 */
export type AnalysisFieldDefinition = {
    fieldKey: string
    label: string
    description: string
    dataType: string
    isRequired: boolean
    sortOrder: number
}


/**
 * TypeScript contract for analysis schema values.
 */
export type AnalysisSchema = {
    schemaId: string
    schemaVersionId: string
    name: string
    domain: string
    version: number
    entityDefinitions: AnalysisEntityDefinition[]
    fieldDefinitions: AnalysisFieldDefinition[]
}
