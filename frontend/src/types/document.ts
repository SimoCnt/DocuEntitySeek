/**
 * Define document metadata and status contracts shared by components and API clients.
 */

/**
 * Document state returned by the API and displayed in the listing.
 */
export type DocumentStatus =
    | 'UPLOADED'
    | 'READY'
    | 'PROCESSING'
    | 'ERROR'



/**
 * Owner-scoped document metadata, page count, and current status.
 */
export type DocumentSummary = {
    id: string
    name: string
    pages: number
    status: DocumentStatus
    uploadedAt: string
}


/**
 * API wrapper containing the detail of one owned document.
 */
export type DocumentDetailResponse = {
    document: DocumentSummary
}
