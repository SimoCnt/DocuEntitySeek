export type CustomEntityDefinitionInput = {
    label: string
    description: string
}


export type CustomFieldDefinitionInput = {
    fieldKey: string
    label: string
    description: string
    isRequired: boolean
}


export type CustomSchemaCreateRequest = {
    name: string
    domain: string
    entities: CustomEntityDefinitionInput[]
    fields: CustomFieldDefinitionInput[]
}


export type CustomEntityDefinition = {
    id: string
    label: string
    description: string
    color: string
    sortOrder: number
}


export type CustomFieldDefinition = {
    id: string
    fieldKey: string
    label: string
    description: string
    dataType: string
    isRequired: boolean
    sortOrder: number
}


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


export type CustomSchemaArchiveResponse = {
    schemaId: string
    archivedAt: string
}


export type CustomSchemaDuplicateRequest = {
    name: string
}