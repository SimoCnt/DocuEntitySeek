import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router'

import ConfirmUploadDialog from '../components/upload/ConfirmUploadDialog'
import DocumentUploadForm from '../components/upload/DocumentUploadForm'
import UploadSummary from '../components/upload/UploadSummary'
import Panel from '../components/common/Panel'
import useDocumentTitle from '../hooks/useDocumentTitle'
import { validatePdfFile } from '../utils/fileValidation'
import type { DocumentCategory } from '../types/upload'
import ErrorState from '../components/feedback/ErrorState'
import useCreateDocument from '../hooks/useCreateDocument'


function NewDocumentPage() {
    useDocumentTitle('Nuovo documento | DocuEntitySeek')

    const [selectedFile, setSelectedFile] = useState<File | null>(null)
    const [category, setCategory] = useState<DocumentCategory>('DISCIPLINARE')
    const [errorMessage, setErrorMessage] = useState<string | null>(null)
    const [isConfirmationOpen, setIsConfirmationOpen] = useState(false)    
    const navigate = useNavigate()
    const {uploadDocument, isSubmitting, error: uploadError} = useCreateDocument()


    function handleFileChange(file: File | null) {
        setSelectedFile(file)
        setErrorMessage(null)        
    }


    function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()
        const validationError = validatePdfFile(selectedFile)

        if (validationError) {
            setErrorMessage(validationError)
            return
        }

        setErrorMessage(null)
        setIsConfirmationOpen(true)
    }


    async function handleConfirm() {
        if (!selectedFile) {
            return
        }

        setIsConfirmationOpen(false)

        const document = await uploadDocument(selectedFile, category)

        if (!document) {
            return
        }

        navigate('/documents', { replace: true })
        }


    return (
        <section className="page-section">
            <div className="page-heading">
                <Link
                    to="/documents"
                    className="back-link"
                >
                    ← Documenti
                </Link>

                <span className="section-heading__eyebrow">New document</span>
                <h1>Carica un documento</h1>
                <p>Prepara un PDF per l'analisi di DocuEntitySeek.</p>
            </div>

            <div className="upload-layout">
                <Panel
                    title="Documento"
                    description="Seleziona il PDF e specifica il tipo di documento."
                >
                    <DocumentUploadForm
                        selectedFile={selectedFile}
                        category={category}
                        errorMessage={errorMessage}
                        onFileChange={handleFileChange}
                        onCategoryChange={setCategory}
                        onSubmit={handleSubmit}
                    />
                </Panel>

                <Panel
                    title="Riepilogo"
                    description="Informazioni che verranno associate al documento."
                >
                    {selectedFile ? (
                        <UploadSummary
                            file={selectedFile}
                            category={category}
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
                category={category}
                onCancel={() =>
                    setIsConfirmationOpen(
                        false,
                    )
                }
                onConfirm={handleConfirm}
            />
        </section>
    )
}

export default NewDocumentPage