/**
 * Guide PDF selection, validation, confirmation, and upload.
 */

import { useState, type FormEvent, useEffect } from 'react'
import { Link, useNavigate } from 'react-router'

import ConfirmUploadDialog from '../components/upload/ConfirmUploadDialog'
import DocumentUploadForm from '../components/upload/DocumentUploadForm'
import UploadSummary from '../components/upload/UploadSummary'
import Panel from '../components/common/Panel'
import useDocumentTitle from '../hooks/useDocumentTitle'
import { validatePdfFile } from '../utils/fileValidation'
import ErrorState from '../components/feedback/ErrorState'
import useCreateDocument from '../hooks/useCreateDocument'
import { useAuth } from '../auth/AuthContext'
import useAvailableSchemas from '../hooks/useAvailableSchemas'


/**
 * Guide the user from local PDF validation to upload confirmation.
 */
function NewDocumentPage() {
    useDocumentTitle('Nuovo documento | DocuEntitySeek')

    const [selectedFile, setSelectedFile] = useState<File | null>(null)
    const [errorMessage, setErrorMessage] = useState<string | null>(null)
    const [schemaSelectionError, setSchemaSelectionError] = useState<string | null>(null)
    const [isConfirmationOpen, setIsConfirmationOpen] = useState(false)    
    const navigate = useNavigate()
    const {uploadDocument, isSubmitting, error: uploadError} = useCreateDocument()

    const { user } = useAuth()
    const customSchemasEnabled = user?.plan.customSchemasEnabled === true

    const { schemas, isLoading: schemasLoading, error: schemasError } = useAvailableSchemas(customSchemasEnabled)
    const [selectedSchemaVersionId, setSelectedSchemaVersionId] = useState<string | undefined>(undefined)

    useEffect(() => {
        if (!customSchemasEnabled) {
            setSelectedSchemaVersionId(undefined)
            return
        }

        if (schemas.length === 0) {
            return
        }

        setSelectedSchemaVersionId(
            (current) => {
                if (
                    current &&
                    schemas.some(
                        (schema) =>
                            schema.schemaVersionId === current
                    )
                ) {
                    return current
                }

                const builtInSchema = schemas.find(
                    (schema) => schema.isBuiltin
                )

                return (
                    builtInSchema?.schemaVersionId ??
                    schemas[0].schemaVersionId
                )
            }
        )
    }, [
        customSchemasEnabled,
        schemas,
    ])


    function handleFileChange(file: File | null) {
        setSelectedFile(file)
        setErrorMessage(null)        
    }


    function handleSchemaVersionChange(schemaVersionId: string) {
        setSelectedSchemaVersionId(schemaVersionId)
        setSchemaSelectionError(null)
    }


    function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()

        const validationError = validatePdfFile(selectedFile)

        if (validationError) {
            setErrorMessage(validationError)
            return
        }

        if (customSchemasEnabled) {
            if (schemasLoading) {
            setSchemaSelectionError('Attendi il caricamento degli schemi disponibili.')
            return
            }

            if (schemasError) {
            setSchemaSelectionError('Impossibile caricare gli schemi disponibili.')
            return
            }

            if (!selectedSchemaVersionId) {
            setSchemaSelectionError('Seleziona uno schema di estrazione.')
            return
            }
        }

        setErrorMessage(null)
        setSchemaSelectionError(null)
        setIsConfirmationOpen(true)
    }


    async function handleConfirm() {
        if (!selectedFile) {
            return
        }

        setIsConfirmationOpen(false)
        
        const document = await uploadDocument(selectedFile, customSchemasEnabled ? selectedSchemaVersionId : undefined)

        if (!document) {
            return
        }

        navigate('/documents', { replace: true })
        }


    const selectedSchema = schemas.find(
        (schema) => schema.schemaVersionId === selectedSchemaVersionId,
    )

    const schemaDisplayName = customSchemasEnabled
        ? selectedSchema?.name ?? 'Schema non selezionato'
        : 'Schema predefinito'    


    return (
        <>
            <header className="page-hero">
                <div className="page-hero__content">
                    <Link to="/documents" className="back-link">← Documenti</Link>
                    <span className="page-hero__eyebrow">Nuovo documento</span>
                    <h1>Carica un documento</h1>
                    <p>Prepara un PDF per l'analisi di DocuEntitySeek.</p>
                </div>
            </header>

            <section className="page-section page-section--workspace">
                <div className="upload-layout">
                    <Panel
                        title="Documento"
                        description="Seleziona il PDF e lo schema di estrazione."
                    >
                        <DocumentUploadForm
                            selectedFile={selectedFile}
                            errorMessage={errorMessage}
                            showSchemaSelector={
                                customSchemasEnabled
                            }
                            schemas={schemas}
                            schemasLoading={
                                schemasLoading
                            }
                            schemaVersionId={
                                selectedSchemaVersionId ??
                                ''
                            }
                            schemaErrorMessage={
                                schemaSelectionError ??
                                schemasError?.message ??
                                null
                            }
                            onSchemaVersionChange={
                                handleSchemaVersionChange
                            }
                            onFileChange={
                                handleFileChange
                            }
                            onSubmit={
                                handleSubmit
                            }
                        />
                    </Panel>

                    <Panel
                        title="Riepilogo"
                        description="Informazioni che verranno associate al documento."
                    >
                        {selectedFile ? (
                            <UploadSummary
                                file={selectedFile}
                                schemaName={schemaDisplayName}
                            />
                        ) : (
                            <div className="upload-empty-summary">Seleziona un PDF per visualizzare il riepilogo.</div>
                        )}
                    </Panel>
                </div>

                {isSubmitting && (
                    <div
                        className="frontend-notice"
                        role="status"
                    >                    
                        <p>Invio del documento al backend...</p>
                    </div>
                )}

                {uploadError && (
                    <ErrorState
                        message={uploadError.message}
                    />
                )}

                <ConfirmUploadDialog
                    isOpen={isConfirmationOpen}
                    file={selectedFile}
                    schemaName={schemaDisplayName}
                    onCancel={() =>
                        setIsConfirmationOpen(
                            false,
                        )
                    }
                    onConfirm={handleConfirm}
                />
            </section>
        </>
    )
}

export default NewDocumentPage
