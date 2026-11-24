/**
 * Create or edit entity and field definitions with client-side schema validation.
 */

import { useEffect, useState, type FormEvent } from 'react'

import type { CustomFieldDefinitionInput, CustomSchemaCreateRequest, CustomSchema, CustomSchemaSummary } from '../../types/customSchema'
import { validateCustomSchema } from '../../utils/customSchemaValidation'


type EntityDraft = {
    id: string
    label: string
    description: string
}


type FieldDraft = CustomFieldDefinitionInput & {
    id: string
}


/**
 * Properties configuring the custom schema form component.
 */
type CustomSchemaFormProps = {
    isSubmitting: boolean
    errorMessage: string | null
    existingSchemas: CustomSchemaSummary[]
    initialValue?: CustomSchema
    submitLabel?: string
    onCancel?: () => void
    onSubmit: (
        payload: CustomSchemaCreateRequest,
    ) => Promise<boolean>
}


/**
 * Return an empty entity row with a stable client-only identifier.
 */
function createEntityDraft(): EntityDraft {
    return {
        id: crypto.randomUUID(),
        label: '',
        description: '',
    }
}


/**
 * Return an empty field row with a stable client-only identifier.
 */
function createFieldDraft(): FieldDraft {
    return {
        id: crypto.randomUUID(),
        fieldKey: '',
        label: '',
        description: '',
        isRequired: false,
    }
}


/**
 * Validate and edit versioned entity/field definitions before submission.
 */
function CustomSchemaForm({
    isSubmitting,
    errorMessage,
    existingSchemas,
    initialValue,
    submitLabel='Crea schema',
    onCancel,
    onSubmit
}: CustomSchemaFormProps) {
    const [name, setName] = useState('')
    const [domain, setDomain] = useState('')
    const [entities, setEntities] = useState<EntityDraft[]>([createEntityDraft()])
    const [fields, setFields] = useState<FieldDraft[]>([])
    const [validationError, setValidationError] = useState<string | null>(null)

    useEffect(() => {
        if (!initialValue) return

        setName(initialValue.name)
        setDomain(initialValue.domain)

        setEntities(
            initialValue.entities.map((entity) => ({
            id: entity.id,
            label: entity.label,
            description: entity.description,
            })),
        )

        setFields(
            initialValue.fields.map((field) => ({
            id: field.id,
            fieldKey: field.fieldKey,
            label: field.label,
            description: field.description,
            isRequired: field.isRequired,
            })),
        )

        setValidationError(null)
        }, [initialValue])


    function updateEntity(id: string, property: 'label' | 'description', value: string) {
        setEntities((current) =>
            current.map((entity) =>
                entity.id === id ? { ...entity, [property]: value } : entity,
            ),
        )
    }


    function removeEntity(id: string) {
        setEntities((current) => current.filter((entity) => entity.id !== id))
    }


    function updateField(
        id: string,
        property: 'fieldKey' | 'label' | 'description' | 'isRequired',
        value: string | boolean,
    ) {
        setFields((current) =>
            current.map((field) =>
                field.id === id ? { ...field, [property]: value } : field,
            ),
        )
    }


    function removeField(id: string) {
        setFields((current) => current.filter((field) => field.id !== id))
    }

   
    function resetForm() {
        setName('')
        setDomain('')
        setEntities([createEntityDraft()])
        setFields([])
        setValidationError(null)
    }

    
    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()

        const payload: CustomSchemaCreateRequest = {
            name: name.trim(),
            domain: domain.trim(),
            entities: entities.map((entity) => ({
            label: entity.label.trim(),
            description: entity.description.trim(),
            })),
            fields: fields.map((field) => ({
            fieldKey: field.fieldKey.trim(),
            label: field.label.trim(),
            description: field.description.trim(),
            isRequired: field.isRequired,
            })),
        }

        const validationMessage = validateCustomSchema(payload, {
            existingSchemas,
            currentSchemaId: initialValue?.schemaId,
        })

        if (validationMessage) {
            setValidationError(validationMessage)
            return
        }

        setValidationError(null)

        const success = await onSubmit(payload)

        if (success && !initialValue) {
            resetForm()
        }
    }

    return (
        <form className="custom-schema-form" onSubmit={(event) => void handleSubmit(event)}>
            <div className="form-field">
                <label htmlFor="schema-name">Nome schema</label>

                <input
                    id="schema-name"
                    type="text"
                    required
                    maxLength={120}
                    value={name}
                    onChange={(event) => setName(event.target.value)}
                    placeholder="Es. Documenti HR"
                />
            </div>

            <div className="form-field">
                <label htmlFor="schema-domain">Dominio</label>

                <input
                    id="schema-domain"
                    type="text"
                    required
                    maxLength={120}
                    value={domain}
                    onChange={(event) => setDomain(event.target.value)}
                    placeholder="Es. Risorse umane"
                />
            </div>

            <section className="custom-schema-form__section">
                <div className="custom-schema-form__heading">
                    <div>
                        <h3>Entità NER</h3>
                        <p>Definisci le categorie che il modello deve individuare nel testo.</p>
                    </div>

                    <button
                        type="button"
                        className="button button--secondary"
                        disabled={
                            isSubmitting ||
                            entities.length >= 50
                        }
                        onClick={() => setEntities((current) => [...current, createEntityDraft()])}
                    >
                        Aggiungi entità
                    </button>
                </div>

                {entities.length === 0 && (
                    <p className="form-field__help">Nessuna entità configurata.</p>
                )}

                {entities.map((entity, index) => (
                    <div key={entity.id} className="custom-schema-definition">
                        <div className="custom-schema-definition__header">
                            <strong>Entità {index + 1}</strong>

                            <button
                                type="button"
                                className="button button--secondary"
                                onClick={() => removeEntity(entity.id)}
                            >
                                Rimuovi
                            </button>
                        </div>

                        <div className="form-field">
                            <label>Label</label>

                            <input
                                type="text"
                                required
                                maxLength={100}
                                pattern="[A-Z][A-Z0-9_]*"
                                value={entity.label}
                                onChange={(event) => updateEntity(entity.id, 'label', event.target.value)}
                                placeholder="Es. PERSONA"
                            />

                            <p className="form-field__help">
                                Usa lettere maiuscole, numeri e underscore.
                            </p>
                        </div>

                        <div className="form-field">
                            <label>Descrizione</label>

                            <textarea
                                required
                                maxLength={2000}
                                value={entity.description}
                                onChange={(event) => updateEntity(entity.id, 'description', event.target.value)}
                                placeholder="Descrivi chiaramente che cosa deve riconoscere il modello."
                            />
                        </div>
                    </div>
                ))}
            </section>

            <section className="custom-schema-form__section">
                <div className="custom-schema-form__heading">
                    <div>
                        <h3>Campi strutturati</h3>
                        <p>Definisci le informazioni che vuoi estrarre come valori strutturati.</p>
                    </div>

                    <button
                        type="button"
                        className="button button--secondary"
                        disabled={
                            isSubmitting ||
                            fields.length >= 50
                        }
                        onClick={() => setFields((current) => [...current, createFieldDraft()])}
                    >
                        Aggiungi campo
                    </button>
                </div>

                {fields.length === 0 && (
                    <p className="form-field__help">Nessun campo strutturato configurato.</p>
                )}

                {fields.map((field, index) => (
                    <div key={field.id} className="custom-schema-definition">
                        <div className="custom-schema-definition__header">
                            <strong>Campo {index + 1}</strong>

                            <button
                                type="button"
                                className="button button--secondary"
                                onClick={() => removeField(field.id)}
                            >
                                Rimuovi
                            </button>
                        </div>

                        <div className="form-field">
                            <label>Chiave tecnica</label>

                            <input
                                type="text"
                                required
                                maxLength={100}
                                pattern="[a-z][a-z0-9_]*"
                                value={field.fieldKey}
                                onChange={(event) => updateField(field.id, 'fieldKey', event.target.value)}
                                placeholder="Es. data_documento"
                            />

                            <p className="form-field__help">
                                Minuscole, numeri e underscore. Non usare “confidence”.
                            </p>
                        </div>

                        <div className="form-field">
                            <label>Nome visualizzato</label>

                            <input
                                type="text"
                                required
                                maxLength={150}
                                value={field.label}
                                onChange={(event) => updateField(field.id, 'label', event.target.value)}
                                placeholder="Es. Data documento"
                            />
                        </div>

                        <div className="form-field">
                            <label>Descrizione</label>

                            <textarea
                                required
                                maxLength={2000}
                                value={field.description}
                                onChange={(event) => updateField(field.id, 'description', event.target.value)}
                                placeholder="Descrivi quale informazione deve essere estratta."
                            />
                        </div>

                        <label className="custom-schema-checkbox">
                            <input
                                type="checkbox"
                                checked={field.isRequired}
                                onChange={(event) => updateField(field.id, 'isRequired', event.target.checked)}
                            />
                            Campo richiesto
                        </label>
                    </div>
                ))}
            </section>

            {(validationError || errorMessage) && (
                <p className="form-field__error" role="alert">
                    {validationError ?? errorMessage}
                </p>
            )}

            <div className="custom-schema-form__actions">
                {onCancel && (
                    <button
                        type="button"
                        className="button button--secondary"
                        disabled={isSubmitting}
                        onClick={onCancel}
                    >
                        Annulla
                    </button>
                )}

                <button
                    type="submit"
                    className="button button--primary"
                    disabled={isSubmitting}
                >
                    {isSubmitting
                        ? 'Salvataggio in corso...'
                        : submitLabel}
                </button>
            </div>
        </form>
    )
}

export default CustomSchemaForm
