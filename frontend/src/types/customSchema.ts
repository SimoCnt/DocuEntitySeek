/**
 * Define custom extraction schema commands, versions, and response types.
 */

/**
 * TypeScript contract for custom entity definition input values.
 */
export type CustomEntityDefinitionInput = {
    label: string
    description: string
}


/**
 * TypeScript contract for custom field definition input values.
 */
export type CustomFieldDefinitionInput = {
    fieldKey: string
    label: string
    description: string
    isRequired: boolean
}


/**
 * Request payload for custom schema create operations.
 */
export type CustomSchemaCreateRequest = {
    name: string
    domain: string
    entities: CustomEntityDefinitionInput[]
    fields: CustomFieldDefinitionInput[]
}


/**
 * TypeScript contract for custom entity definition values.
 */
export type CustomEntityDefinition = {
    id: string
    label: string
    description: string
    color: string
    sortOrder: number
}


/**
 * TypeScript contract for custom field definition values.
 */
export type CustomFieldDefinition = {
    id: string
    fieldKey: string
    label: string
    description: string
    dataType: string
    isRequired: boolean
    sortOrder: number
}


/**
 * User-owned schema version with entity/field definitions.
 */
export type CustomSchema = {
    schemaId: string
    schemaVersionId: string
    name: string
    domain: string
    version: number
    createdAt: string
    archivedAt: string | null
    isArchived: boolean
    entities: CustomEntityDefinition[]
    fields: CustomFieldDefinition[]
}


/**
 * Schema metadata used in the management listing.
 */
export type CustomSchemaSummary = {
    schemaId: string
    schemaVersionId: string
    name: string
    domain: string
    version: number
    entityCount: number
    fieldCount: number
    createdAt: string
    archivedAt: string | null
    isArchived: boolean
}


/**
 * API response for custom schema archive operations.
 */
export type CustomSchemaArchiveResponse = {
    schemaId: string
    archivedAt: string
}


/**
 * Request payload for custom schema duplicate operations.
 */
export type CustomSchemaDuplicateRequest = {
    name: string
}
