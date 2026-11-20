import { Link } from 'react-router'

import ErrorState from '../components/feedback/ErrorState'
import LoadingState from '../components/feedback/LoadingState'
import useDocumentTitle from '../hooks/useDocumentTitle'
import useDocuments from '../hooks/useDocuments'
import type { DocumentStatus } from '../types/document'


function getStatusLabel(status: DocumentStatus) {
    switch (status) {
        case 'UPLOADED':
            return 'Da analizzare'
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

    const pageHero = (
        <header className="page-hero">
            <div className="page-hero__top">
                <div className="page-hero__content">
                    <span className="page-hero__eyebrow">Workspace</span>
                    <h1>I tuoi documenti</h1>
                    <p>Consulta i documenti caricati e apri quelli per cui l'analisi è già disponibile.</p>
                </div>
                <Link to="/documents/new" className="button button--primary">Nuovo documento</Link>
            </div>
        </header>
    )

    if (isLoading) {
        return (
            <>
                {pageHero}
                <section className="page-section page-section--workspace">
                    <LoadingState message="Caricamento dei documenti..." />
                </section>
            </>
        )
    }

    if (error) {
        return (
            <>
                {pageHero}
                <section className="page-section page-section--workspace">
                    <ErrorState message={error.message} onRetry={reload} />
                </section>
            </>
        )
    }

    return (
        <>
            {pageHero}
            <section className="page-section page-section--workspace">
                <div className="section-heading">
                    <span className="section-heading__eyebrow">Archivio</span>
                    <h2>Documenti caricati</h2>
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
                                    <span className={`document-status ` + `document-status--${document.status.toLowerCase()}`}>{getStatusLabel(document.status)}</span>
                                </div>

                                <h3>{document.name}</h3>

                                <div className="document-card__meta">
                                    <span>{document.pages} pagine</span>
                                    <span>Caricato il{' '}{document.uploadedAt}</span>
                                </div>

                                <Link
                                    to={`/documents/${document.id}`}
                                    className="button button--primary"
                                >
                                    Apri documento
                                </Link>
                            
                            </article>
                        ))}
                    </div>
                )}
            </section>
        </>
    )
}

export default DocumentsPage