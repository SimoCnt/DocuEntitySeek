import { useState, type FormEvent } from 'react'
import { Link } from 'react-router'

import ConfirmUploadDialog from '../components/upload/ConfirmUploadDialog'
import DocumentUploadForm from '../components/upload/DocumentUploadForm'
import UploadSummary from '../components/upload/UploadSummary'
import Panel from '../components/common/Panel'
import useDocumentTitle from '../hooks/useDocumentTitle'
import { validatePdfFile } from '../utils/fileValidation'
import type { DocumentCategory } from '../types/upload'


function NewDocumentPage() {
    useDocumentTitle('Nuovo documento | DocuEntitySeek')

    const [selectedFile, setSelectedFile] = useState<File | null>(null)
    const [category, setCategory] = useState<DocumentCategory>('DISCIPLINARE')
    const [errorMessage, setErrorMessage] = useState<string | null>(null)
    const [isConfirmationOpen, setIsConfirmationOpen] = useState(false)
    const [isSimulationComplete, setIsSimulationComplete] = useState(false)


    function handleFileChange(file: File | null) {
        setSelectedFile(file)
        setErrorMessage(null)
        setIsSimulationComplete(false)
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


    function handleConfirm() {
        setIsConfirmationOpen(false)
        setIsSimulationComplete(true)
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

            {isSimulationComplete && (
                <div
                    className="frontend-notice"
                    role="status"
                >
                    <strong>Workflow frontend completato.</strong>
                    <p>Il documento non è stato ancora inviato: il vero upload verrà implementato in seguito tramite fastAPI.</p>
                </div>
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