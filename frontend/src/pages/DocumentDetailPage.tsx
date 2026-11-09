import { Link, useParams } from 'react-router'

import AnalysisDemoSection from '../components/analysis/AnalysisDemoSection'
import { MOCK_DOCUMENTS } from '../data/documents'


function DocumentDetailPage() {
    const { documentId } = useParams()
    const document = MOCK_DOCUMENTS.find((item) => item.id === documentId)

    if (!document) {
        return (
            <section className="page-section">
                <div className="empty-state">
                    <span className="empty-state__code">Documento non trovato</span>
                    <h1>Il documento richiesto non esiste.</h1>
                    <p>Controlla l'indirizzo oppure torna alla raccolta documenti.</p>

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

    if (document.status !== 'READY') {
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
                    <p>{document.pages} pagine · Analisi pronta</p>
                </div>
            </section>

            <AnalysisDemoSection
                documentName={document.name}
            />
        </>
    )
}

export default DocumentDetailPage