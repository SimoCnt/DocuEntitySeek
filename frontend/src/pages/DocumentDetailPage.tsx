import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router'

import AnalysisDemoSection from '../components/analysis/AnalysisDemoSection'
import ErrorState from '../components/feedback/ErrorState'
import LoadingState from '../components/feedback/LoadingState'
import useAnalysis from '../hooks/useAnalysis'
import useDocumentAnalyses from '../hooks/useDocumentAnalyses'
import useDocumentDetail from '../hooks/useDocumentDetail'
import useDocumentTitle from '../hooks/useDocumentTitle'
import useStartAnalysis from '../hooks/useStartAnalysis'


function DocumentDetailPage() {
    const { documentId = '' } = useParams<{ documentId: string }>()
    const { data, isLoading, error, reload: reloadDocument } = useDocumentDetail(documentId)

    const {
        analyses,
        isLoading: analysesLoading,
        error: analysesError,
        reload: reloadAnalyses,
    } = useDocumentAnalyses(documentId || undefined)

    const {
        data: startedAnalysis,
        isLoading: analysisRunning,
        error: analysisStartError,
        run: runAnalysis,
    } = useStartAnalysis()

    const [selectedAnalysisId, setSelectedAnalysisId] = useState<string | undefined>(undefined)

    useEffect(() => {
        if (analyses.length === 0) {
            setSelectedAnalysisId(undefined)
            return
        }

        setSelectedAnalysisId((current) => {
            if (current && analyses.some((analysis) => analysis.id === current)) {
                return current
            }

            return analyses[0].id
        })
    }, [analyses])

    const {
        analysis: selectedAnalysis,
        isLoading: selectedAnalysisLoading,
        error: selectedAnalysisError,
        reload: reloadSelectedAnalysis,
    } = useAnalysis(documentId || undefined, selectedAnalysisId)

    useDocumentTitle(data ? `${data.document.name} | DocuEntitySeek` : 'Documento | DocuEntitySeek')

    
    async function handleStartAnalysis() {
        if (!documentId) return

        const result = await runAnalysis(documentId)

        if (!result) return

        setSelectedAnalysisId(result.analysisId)
        reloadAnalyses()
        reloadDocument()
    }

    if (isLoading) {
        return (
            <section className="page-section">
                <LoadingState message="Caricamento del documento..." />
            </section>
        )
    }

    if (error?.status === 404) {
        return (
            <section className="page-section">
                <div className="empty-state">
                    <span className="empty-state__code">Documento non trovato</span>
                    <h1>Il documento richiesto non esiste.</h1>
                    <Link to="/documents" className="button button--primary">
                        Torna ai documenti
                    </Link>
                </div>
            </section>
        )
    }

    if (error) {
        return (
            <section className="page-section">
                <ErrorState message={error.message} onRetry={reloadDocument} />
            </section>
        )
    }

    if (!data) return null

    const { document, analysis: viewerAnalysis } = data

    return (
        <>
            <section className="document-detail-heading">
                <div>
                    <Link to="/documents" className="back-link">
                        ← Documenti
                    </Link>

                    <span className="section-heading__eyebrow">{document.category}</span>
                    <h1>{document.name}</h1>

                    <p>
                        {document.pages} pagine
                        {' · '}
                        {analyses.length === 0
                            ? 'Nessuna analisi eseguita'
                            : `${analyses.length} analisi disponibili`}
                    </p>
                </div>
            </section>

            <section className="page-section">
                <div className="page-heading__top">
                    <div>
                        <span className="section-heading__eyebrow">Analisi AI</span>
                        <h2>Analizza il documento</h2>
                        <p>Avvia una nuova esecuzione AI sul PDF caricato.</p>
                    </div>

                    <button
                        type="button"
                        className="button button--primary"
                        disabled={analysisRunning}
                        onClick={() => void handleStartAnalysis()}
                    >
                        {analysisRunning ? 'Analisi in corso...' : 'Analizza documento'}
                    </button>
                </div>

                {analysisStartError && <ErrorState message={analysisStartError.message} />}

                {startedAnalysis && (
                    <div className="frontend-notice">
                        <strong>Ultima analisi completata: {startedAnalysis.status}</strong>
                        <p>
                            {startedAnalysis.pipeline.entityCount} entità
                            {' · '}
                            {startedAnalysis.pipeline.fieldCount} campi
                        </p>
                    </div>
                )}
            </section>

            <section className="page-section">
                <div className="section-heading">
                    <span className="section-heading__eyebrow">Cronologia</span>
                    <h2>Analisi del documento</h2>
                </div>

                {analysesLoading && <LoadingState message="Caricamento delle analisi..." />}

                {analysesError && (
                    <ErrorState message={analysesError.message} onRetry={reloadAnalyses} />
                )}

                {!analysesLoading && !analysesError && analyses.length === 0 && (
                    <div className="empty-state">
                        <h2>Nessuna analisi disponibile</h2>
                        <p>Avvia la prima analisi del documento.</p>
                    </div>
                )}

                {!analysesLoading && !analysesError && analyses.length > 0 && (
                    <div className="documents-grid">
                        {analyses.map((analysis) => (
                            <article key={analysis.id} className="document-card">
                                <div className="document-card__header">
                                    <span className="document-card__type">Analysis</span>

                                    <span className={`document-status document-status--${analysis.status.toLowerCase()}`}>
                                        {analysis.status}
                                    </span>
                                </div>

                                <h2>{new Date(analysis.createdAt).toLocaleString('it-IT')}</h2>

                                <div className="document-card__meta">
                                    <span>{analysis.id}</span>
                                </div>

                                <button
                                    type="button"
                                    className="button button--secondary"
                                    onClick={() => setSelectedAnalysisId(analysis.id)}
                                >
                                    {selectedAnalysisId === analysis.id ? 'Selezionata' : 'Apri analisi'}
                                </button>
                            </article>
                        ))}
                    </div>
                )}
            </section>

            {selectedAnalysisId && (
                <section className="page-section">
                    <div className="section-heading">
                        <span className="section-heading__eyebrow">Dettaglio API</span>
                        <h2>Analisi selezionata</h2>
                    </div>

                    {selectedAnalysisLoading && (
                        <LoadingState message="Caricamento del dettaglio analisi..." />
                    )}

                    {selectedAnalysisError && (
                        <ErrorState message={selectedAnalysisError.message} onRetry={reloadSelectedAnalysis} />
                    )}

                    {!selectedAnalysisLoading && !selectedAnalysisError && selectedAnalysis && (
                        <div className="frontend-notice">
                            <strong>Status: {selectedAnalysis.status}</strong>
                            <p>
                                {selectedAnalysis.result
                                    ? `${selectedAnalysis.result.pages.length} pagine · ${selectedAnalysis.result.entities.length} entità · ${selectedAnalysis.result.fields.length} campi`
                                    : 'Nessun risultato persistito disponibile per questa analisi.'}
                            </p>
                        </div>
                    )}
                </section>
            )}

            {viewerAnalysis ? (
                <AnalysisDemoSection
                    key={document.id}
                    documentName={document.name}
                    analysis={viewerAnalysis}
                />
            ) : (
                <section className="page-section">
                    <div className="empty-state">
                        <h2>Viewer non ancora disponibile</h2>
                        <p>
                            Quando un'analisi sarà completata con successo,
                            il risultato verrà mostrato qui.
                        </p>
                    </div>
                </section>
            )}
        </>
    )
}

export default DocumentDetailPage