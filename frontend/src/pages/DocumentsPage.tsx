import { Link } from 'react-router'

import ErrorState from '../components/feedback/ErrorState'
import LoadingState from '../components/feedback/LoadingState'
import useDocumentTitle from '../hooks/useDocumentTitle'
import useDocuments from '../hooks/useDocuments'
import type { DocumentStatus } from '../types/document'


function getStatusLabel(status: DocumentStatus) {
    switch (status) {
        case 'READY':
            return 'Pronto'

        case 'PROCESSING':
            return 'In elaborazione'

        case 'ERROR':
            return 'Errore'
    }
}


function DocumentsPage() {
    useDocumentTitle('Documenti | DocuEntitySeek')

    const { documents, isLoading, error, reload } = useDocuments()

    if (isLoading) {
        return (
            <section className="page-section">
                <LoadingState
                    message="Caricamento dei documenti..."
                />
            </section>
        )
    }

    if (error) {
        return (
            <section className="page-section">
                <ErrorState
                    message={error.message}
                    onRetry={reload}
                />
            </section>
        )
    }

    return (
        <section className="page-section">
            <div className="page-heading">
                <span className="section-heading__eyebrow">Workspace</span>
                <h1>I tuoi documenti</h1>
                <p>Consulta i documenti caricati e apri quelli per cui l'analisi è già disponibile.</p>
            </div>

            {documents.length === 0 ? (
                <div className="empty-state">
                    <h2>Nessun documento</h2>
                    <p>Non sono ancora presenti documenti.</p>
                </div>
            ) : (
                <div className="documents-grid">
                    {documents.map((document) => (
                        <article
                            key={document.id}
                            className="document-card"
                        >
                            <div className="document-card__header">
                                <span className="document-card__type">{document.category}</span>
                                <span className={`document-status ` + `document-status--${document.status.toLowerCase()}`}>{getStatusLabel(document.status)}</span>
                            </div>

                            <h2>{document.name}</h2>

                            <div className="document-card__meta">
                                <span>{document.pages} pagine</span>
                                <span>Caricato il{' '}{document.uploadedAt}</span>
                            </div>

                            {document.status === 'READY' ? (
                                <Link
                                    to={`/documents/${document.id}`}
                                    className="button button--primary"
                                >
                                    Apri documento
                                </Link>
                            ) : (
                                <button
                                    type="button"
                                    className="button button--secondary"
                                    disabled
                                >
                                    Non disponibile
                                </button>
                            )}
                        </article>
                    ))}
                </div>
            )}
        </section>
    )
}

export default DocumentsPage