/**
 * Coordinate document metadata, original PDF viewing, analysis selection, and schema-driven execution.
 */

import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router'

import AnalysisResultViewer from '../components/analysis/AnalysisResultViewer'
import StartAnalysisSchemaDialog from '../components/analysis/StartAnalysisSchemaDialog'
import PdfDocumentViewer from '../components/pdf/PdfDocumentViewer'
import ErrorState from '../components/feedback/ErrorState'
import LoadingState from '../components/feedback/LoadingState'
import useAnalysis from '../hooks/useAnalysis'
import useDocumentAnalyses from '../hooks/useDocumentAnalyses'
import useDocumentDetail from '../hooks/useDocumentDetail'
import useDocumentTitle from '../hooks/useDocumentTitle'
import useStartAnalysis from '../hooks/useStartAnalysis'

/**
 * Coordinate the authenticated document-detail experience.
 *
 * Controls analysis selection and polling, launches the selected schema
 * version, and switches between PDF-only and completed-result views.
 */
function DocumentDetailPage() {
    const { documentId = '' } = useParams<{ documentId: string }>()
    const { data, isLoading, error, reload: reloadDocument } = useDocumentDetail(documentId)

    const {
        analyses,
        isLoading: analysesLoading,
        error: analysesError,
        reload: reloadAnalyses,
        refreshSilently: refreshAnalysesSilently,
    } = useDocumentAnalyses(documentId || undefined)

    const {
        data: startedAnalysis,
        isLoading: analysisRunning,
        error: analysisStartError,
        run: runAnalysis,
    } = useStartAnalysis()

    const [selectedAnalysisId, setSelectedAnalysisId] = useState<string | undefined>(undefined)

    const [isSchemaDialogOpen, setIsSchemaDialogOpen] = useState(false)

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
        refreshSilently: refreshSelectedAnalysisSilently,
    } = useAnalysis(documentId || undefined, selectedAnalysisId)

    const hasRunningAnalyses = analyses.some(
        (analysis) => analysis.status === 'QUEUED' || analysis.status === 'PROCESSING',
    )

    const selectedAnalysisIsRunning =
        selectedAnalysis?.status === 'QUEUED' || selectedAnalysis?.status === 'PROCESSING'

    useEffect(() => {
        if (!hasRunningAnalyses) return

        const intervalId = window.setInterval(() => {
            if (window.document.visibilityState === "visible") refreshAnalysesSilently()
        }, 6000)

        return () => window.clearInterval(intervalId)
    }, [hasRunningAnalyses, refreshAnalysesSilently])

    useEffect(() => {
        if (!selectedAnalysisId || !selectedAnalysisIsRunning) return

        const intervalId = window.setInterval(() => {
            if (window.document.visibilityState === "visible") refreshSelectedAnalysisSilently()
        }, 6000)

        return () => window.clearInterval(intervalId)
    }, [selectedAnalysisId, selectedAnalysisIsRunning, refreshSelectedAnalysisSilently])

    useDocumentTitle(data ? `${data.document.name} | DocuEntitySeek` : 'Documento | DocuEntitySeek')

    
    async function handleStartAnalysis(schemaVersionId?: string) {
        if (!documentId || hasRunningAnalyses || analysisRunning) return

        setIsSchemaDialogOpen(false)

        const outcome = await runAnalysis(documentId, schemaVersionId)
        if (!outcome.ok) return

        setSelectedAnalysisId(outcome.data.analysisId)
        void refreshAnalysesSilently()
    }



    if (isLoading) {
        return (
            <section className="page-section page-section--workspace">
                <LoadingState message="Caricamento del documento..." />
            </section>
        )
    }

    if (error?.status === 404) {
        return (
            <section className="page-section page-section--workspace">
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
            <section className="page-section page-section--workspace">
                <ErrorState message={error.message} onRetry={reloadDocument} />
            </section>
        )
    }

    if (!data) return null

    const { document } = data

    return (
        <>
            <StartAnalysisSchemaDialog
                isOpen={isSchemaDialogOpen}
                isSubmitting={analysisRunning}
                errorMessage={analysisStartError?.message ?? null}
                onCancel={() => setIsSchemaDialogOpen(false)}
                onConfirm={handleStartAnalysis}
            />
            <header className="page-hero">
                <div className="page-hero__content">
                    <Link to="/documents" className="back-link">
                        ← Documenti
                    </Link>

                    <span className="page-hero__eyebrow">Documento</span>
                    <h1>{document.name}</h1>

                    <p>
                        {document.pages} pagine
                        {' · '}
                        {analyses.length === 0
                            ? 'Nessuna analisi eseguita'
                            : `${analyses.length} analisi disponibili`}
                    </p>
                </div>
            </header>

            <section className="page-section page-section--workspace">
                <div className="page-heading__top">
                    <div>
                        <span className="section-heading__eyebrow">Analisi AI</span>
                        <h2>Analizza il documento</h2>
                        <p>Avvia una nuova esecuzione AI sul PDF caricato.</p>
                    </div>

                    <button
                        type="button"
                        className="button button--primary"
                        disabled={analysisRunning || hasRunningAnalyses}
                        onClick={() => setIsSchemaDialogOpen(true)}
                    >
                        {analysisRunning || hasRunningAnalyses ? 'Analisi in corso...' : 'Analizza documento'}
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

            <section className="page-section page-section--workspace">
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

                                <h3>{new Date(analysis.createdAt).toLocaleString('it-IT')}</h3>

                                <div className="document-card__meta">
                                    <span>Schema: <strong>{analysis.schemaName}</strong> · v{analysis.schemaVersion}</span>
                                    
                                    
                                </div>

                                {(analysis.status === 'QUEUED' || analysis.status === 'PROCESSING') && (
                                    <p className="document-card__processing" role="status">
                                        Elaborazione AI in corso...
                                    </p>
                                )}

                                <button
                                    type="button"
                                    className="button button--secondary"
                                    disabled={selectedAnalysisId === analysis.id}
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
                <section className="page-section page-section--workspace">
                    <div className="section-heading">
                        <span className="section-heading__eyebrow">Dettaglio API</span>
                        <h2>Analisi selezionata</h2>
                    </div>

                    {selectedAnalysisLoading && (
                        <LoadingState message="Caricamento del dettaglio analisi..." />
                    )}

                    {selectedAnalysisError && (
                        <ErrorState
                            message={selectedAnalysisError.message}
                            onRetry={reloadSelectedAnalysis}
                        />
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

            {selectedAnalysisId && selectedAnalysisLoading && (
                <section className="page-section page-section--workspace">
                    <LoadingState message="Caricamento del risultato dell’analisi..." />
                </section>
            )}

            {selectedAnalysisId && selectedAnalysisError && (
                <section className="page-section page-section--workspace">
                    <ErrorState
                        message={selectedAnalysisError.message}
                        onRetry={reloadSelectedAnalysis}
                    />
                </section>
            )}

            {(!selectedAnalysis || selectedAnalysis.status !== 'READY' || !selectedAnalysis.result) && (
                <section className="page-section page-section--workspace">
                    <div className="section-heading"><h2>Documento originale</h2></div>
                    <PdfDocumentViewer documentId={documentId} />
                </section>
            )}

            {selectedAnalysis?.status === 'READY' && selectedAnalysis.result && (
                <AnalysisResultViewer
                    key={selectedAnalysis.id}
                    documentId={documentId}
                    analysisId={selectedAnalysis.id}
                    documentName={document.name}
                    result={selectedAnalysis.result}
                />
            )}

            {selectedAnalysis?.status === 'READY' && !selectedAnalysis.result && (
                <section className="page-section page-section--workspace">
                    <div className="empty-state">
                        <h2>Risultato non disponibile</h2>
                        <p>
                            L’analisi risulta completata, ma non contiene un risultato visualizzabile.
                        </p>
                    </div>
                </section>
            )}

            {selectedAnalysis &&
                (selectedAnalysis.status === 'QUEUED' || selectedAnalysis.status === 'PROCESSING') && (
                    <section className="page-section page-section--workspace">
                        <div className="empty-state">
                            <h2>Analisi in elaborazione</h2>
                            <p>
                                Il risultato verrà mostrato automaticamente quando l’elaborazione sarà completata.
                            </p>
                        </div>
                    </section>
                )}

            {selectedAnalysis?.status === 'ERROR' && (
                <section className="page-section page-section--workspace">
                    <div className="empty-state">
                        <h2>Analisi non completata</h2>
                        <p>
                            {selectedAnalysis.errorMessage ?? 'Si è verificato un errore durante l’analisi.'}
                        </p>
                    </div>
                </section>
            )}

            {!selectedAnalysisId && !selectedAnalysisLoading && (
                <section className="page-section page-section--workspace">
                    <div className="empty-state">
                        <h2>Nessuna analisi selezionata</h2>
                        <p>Seleziona un’analisi disponibile oppure avviane una nuova.</p>
                    </div>
                </section>
            )}
        </>
    )
}

export default DocumentDetailPage
