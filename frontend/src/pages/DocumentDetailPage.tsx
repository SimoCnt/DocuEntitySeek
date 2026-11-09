import { Link, useParams } from 'react-router'

import AnalysisDemoSection from '../components/analysis/AnalysisDemoSection'
import ErrorState from '../components/feedback/ErrorState'
import LoadingState from '../components/feedback/LoadingState'
import useDocumentDetail from '../hooks/useDocumentDetail'
import useDocumentTitle from '../hooks/useDocumentTitle'


function DocumentDetailPage() {
    const { documentId = '' } = useParams()
    const { data, isLoading, error, reload } = useDocumentDetail(documentId)

    useDocumentTitle(
        data
            ? `${data.document.name} | DocuEntitySeek`
            : 'Documento | DocuEntitySeek',
    )

    if (isLoading) {
        return (
            <section className="page-section">
                <LoadingState
                    message="Caricamento del documento..."
                />
            </section>
        )
    }

    if (error?.status === 404) {
        return (
            <section className="page-section">
                <div className="empty-state">
                    <span className="empty-state__code">Documento non trovato</span>
                    <h1>Il documento richiesto non esiste.</h1>

                    <Link
                        to="/documents"
                        className="button button--primary"
                    >
                        Torna ai documenti
                    </Link>
                </div>
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

    if (!data) {
        return null
    }

    const {
        document,
        analysis,
    } = data

    if (
        document.status !== 'READY' ||
        !analysis
    ) {
        return (
            <section className="page-section">
                <div className="empty-state">
                    <h1>{document.name}</h1>
                    <p>L'analisi del documento non è attualmente disponibile.</p>

                    <Link
                        to="/documents"
                        className="button button--secondary"
                    >
                        Torna ai documenti
                    </Link>
                </div>
            </section>
        )
    }

    return (
        <>
            <section className="document-detail-heading">
                <div>
                    <Link
                        to="/documents"
                        className="back-link"
                    >
                        ← Documenti
                    </Link>

                    <span className="section-heading__eyebrow">{document.category}</span>
                    <h1>{document.name}</h1>
                    <p>
                        {document.pages} pagine
                        {' · '}
                        Analisi pronta
                    </p>
                </div>
            </section>

            <AnalysisDemoSection
                key={document.id}
                documentName={document.name}
                analysis={analysis}
            />
        </>
    )
}

export default DocumentDetailPage