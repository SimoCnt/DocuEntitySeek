/**
 * Validate custom schema names, entity labels, fields, and duplicate definitions.
 */

import type { CustomSchemaCreateRequest, CustomSchemaSummary } from '../types/customSchema'

const ENTITY_LABEL_PATTERN = /^[A-Z][A-Z0-9_]*$/
const FIELD_KEY_PATTERN = /^[a-z][a-z0-9_]*$/


type ValidateCustomSchemaOptions = {
    existingSchemas: CustomSchemaSummary[]
    currentSchemaId?: string
}


/**
 * Validate schema names and field/entity definitions before submission.
 */
export function validateCustomSchema(
    payload: CustomSchemaCreateRequest,
    { existingSchemas, currentSchemaId }: ValidateCustomSchemaOptions,
): string | null {
    const name = payload.name.trim()
    const domain = payload.domain.trim()

    if (!name) return 'Inserisci il nome dello schema.'
    if (!domain) return 'Inserisci il dominio dello schema.'
    if (name.length > 120) return 'Il nome dello schema non può superare 120 caratteri.'
    if (domain.length > 120) return 'Il dominio non può superare 120 caratteri.'

    const duplicatedName = existingSchemas.some(
        (schema) => schema.schemaId !== currentSchemaId && schema.name.trim().toLowerCase() === name.toLowerCase(),
    )

    if (duplicatedName) {
        return 'Esiste già uno schema personalizzato con questo nome.'
    }

    if (payload.entities.length === 0 && payload.fields.length === 0) {
        return 'Aggiungi almeno un’entità o un campo strutturato.'
    }

    if (payload.entities.length > 50) {
        return 'Uno schema può contenere al massimo 50 entità.'
    }

    if (payload.fields.length > 50) {
        return 'Uno schema può contenere al massimo 50 campi strutturati.'
    }

    const entityLabels = new Set<string>()

    for (const entity of payload.entities) {
        const label = entity.label.trim()
        const description = entity.description.trim()

        if (!ENTITY_LABEL_PATTERN.test(label)) {
            return `La label "${label}" non è valida. Usa lettere maiuscole, numeri e underscore.`
        }

        if (!description) {
            return `Inserisci una descrizione per l’entità "${label}".`
        }

        if (entityLabels.has(label)) {
            return `La label "${label}" è presente più di una volta.`
        }

        entityLabels.add(label)
    }

    const fieldKeys = new Set<string>()

    for (const field of payload.fields) {
        const fieldKey = field.fieldKey.trim()

        if (!FIELD_KEY_PATTERN.test(fieldKey)) {
            return `La chiave "${fieldKey}" non è valida. Usa lettere minuscole, numeri e underscore.`
        }

        if (fieldKey === 'confidence') {
            return 'La chiave "confidence" è riservata dal motore di estrazione.'
        }

        if (!field.label.trim()) {
            return `Inserisci un nome visualizzato per il campo "${fieldKey}".`
        }

        if (!field.description.trim()) {
            return `Inserisci una descrizione per il campo "${fieldKey}".`
        }

        if (fieldKeys.has(fieldKey)) {
            return `La chiave "${fieldKey}" è presente più di una volta.`
        }

        fieldKeys.add(fieldKey)
    }

    return null
}
