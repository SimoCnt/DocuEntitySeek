import { Link } from 'react-router'

import { MOCK_DOCUMENTS, type DocumentStatus } from '../data/documents'
import useDocumentTitle from '../hooks/useDocumentTitle'


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

    return (
        <section className="page-section">
            <div className="page-heading">
                <span className="section-heading__eyebrow">Workspace</span>
                <h1>I tuoi documenti</h1>
                <p>Consulta i documenti caricati e apri quelli per cui l'analisi è già disponibile.</p>
            </div>

            <div className="documents-grid">
                {MOCK_DOCUMENTS.map((document) => (
                    <article
                        key={document.id}
                        className="document-card"
                    >
                        <div className="document-card__header">
                            <span className="document-card__type">{document.category}</span>
                            <span className={`document-status document-status--${document.status.toLowerCase()}`}>{getStatusLabel(document.status)}</span>
                        </div>

                        <h2>{document.name}</h2>

                        <div className="document-card__meta">
                            <span>{document.pages} pagine</span>
                            <span>Caricato il {document.uploadedAt}</span>
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
        </section>
    )
}

export default DocumentsPage