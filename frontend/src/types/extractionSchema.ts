/**
 * Define the summary of an extraction schema available for analysis.
 */

/**
 * Authorized schema version available in the analysis picker.
 */
export type AvailableExtractionSchema = {
    schemaId: string
    schemaVersionId: string
    name: string
    domain: string
    version: number
    isBuiltin: boolean
}
