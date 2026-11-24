/**
 * Select an authorized extraction schema version before launching document analysis.
 */

import { useEffect, useRef, useState, type FormEvent } from 'react'

import { useAuth } from '../../auth/AuthContext'
import useAvailableSchemas from '../../hooks/useAvailableSchemas'


/**
 * Properties configuring the start analysis schema dialog component.
 */
type StartAnalysisSchemaDialogProps = {
    isOpen: boolean
    isSubmitting: boolean
    errorMessage: string | null
    onCancel: () => void
    onConfirm: (schemaVersionId?: string) => Promise<void>
}


/**
 * Allow a user to choose an authorized schema version before analysis.
 */
function StartAnalysisSchemaDialog({ isOpen, isSubmitting, errorMessage, onCancel, onConfirm }: StartAnalysisSchemaDialogProps) {
    const dialogRef = useRef<HTMLDialogElement>(null)
    const { user } = useAuth()
    const customSchemasEnabled = user?.plan.customSchemasEnabled === true
    const { schemas, isLoading, error } = useAvailableSchemas(isOpen && customSchemasEnabled)
    const [chosenSchemaVersionId, setChosenSchemaVersionId] = useState('')
    const defaultSchema = schemas.find((schema) => schema.isBuiltin)
    const validSelection = schemas.some((schema) => schema.schemaVersionId === chosenSchemaVersionId)
    const selectedSchemaVersionId = validSelection ? chosenSchemaVersionId : defaultSchema?.schemaVersionId ?? schemas[0]?.schemaVersionId ?? ''
    const cannotSubmit = isSubmitting || (customSchemasEnabled && (isLoading || Boolean(error) || !selectedSchemaVersionId))

    useEffect(() => {
        const dialog = dialogRef.current
        if (!dialog) return
        if (isOpen && !dialog.open) dialog.showModal()
        if (!isOpen && dialog.open) dialog.close()
    }, [isOpen])

    function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()
        if (cannotSubmit) return
        // Per il piano Base il server seleziona lo schema predefinito.
        void onConfirm(customSchemasEnabled ? selectedSchemaVersionId : undefined)
    }

    return (
        <dialog
            ref={dialogRef}
            className="upload-dialog"
            aria-labelledby="start-analysis-schema-title"
            onClose={onCancel}
            onCancel={(event) => { if (isSubmitting) event.preventDefault() }}
        >
            <form className="upload-dialog__content" onSubmit={handleSubmit}>
                <span className="section-heading__eyebrow">Analisi AI</span>
                <h2 id="start-analysis-schema-title">Scegli lo schema di estrazione</h2>
                <p>Lo schema determina quali entità e campi verranno estratti dal PDF.</p>

                {customSchemasEnabled ? (
                    <div className="form-field">
                        <label htmlFor="analysis-schema-version">Schema da utilizzare</label>
                        {isLoading ? <p>Caricamento degli schemi...</p> : (
                            <select
                                id="analysis-schema-version"
                                value={selectedSchemaVersionId}
                                onChange={(event) => setChosenSchemaVersionId(event.target.value)}
                                required
                                disabled={isSubmitting || Boolean(error) || schemas.length === 0}
                            >
                                {schemas.length === 0 && <option value="">Nessuno schema disponibile</option>}
                                {schemas.map((schema) => (
                                    <option key={schema.schemaVersionId} value={schema.schemaVersionId}>
                                        {schema.name} — v{schema.version}{schema.isBuiltin ? ' (predefinito)' : ''}
                                    </option>
                                ))}
                            </select>
                        )}
                        {error && <p className="form-field__error" role="alert">{error.message}</p>}
                    </div>
                ) : (
                    <div className="form-field">
                        <label>Schema da utilizzare</label>
                        <p><strong>Schema predefinito</strong></p>
                        <p>Con il piano Base non è possibile utilizzare schemi personalizzati.</p>
                    </div>
                )}

                {errorMessage && <p className="form-field__error" role="alert">{errorMessage}</p>}

                <div className="upload-dialog__actions">
                    <button type="button" className="button button--secondary" disabled={isSubmitting} onClick={onCancel}>
                        Annulla
                    </button>
                    <button type="submit" className="button button--primary" disabled={cannotSubmit}>
                        {isSubmitting ? 'Analisi in corso...' : 'Avvia analisi'}
                    </button>
                </div>
            </form>
        </dialog>
    )
}

export default StartAnalysisSchemaDialog
