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
import type { RequestError } from '../api/http'
import type { AnalysisStatus } from '../types/analysis'
import { getAnalysisFailedDetails, getAnalysisQuotaExceededDetails } from '../utils/analysisErrors'


function getAnalysisStatusLabel(status: AnalysisStatus) {
  switch (status) {
    case 'QUEUED':
      return 'In coda'

    case 'PROCESSING':
      return 'In elaborazione'

    case 'READY':
      return 'Pronta'

    case 'ERROR':
      return 'Errore'
  }
}


function getAnalysisStartErrorContent(error: RequestError) {
  const quota = getAnalysisQuotaExceededDetails(error)

  if (quota) {
    const resetsAt = new Date(quota.resetsAt).toLocaleString('it-IT')

    return {
      title: 'Quota giornaliera raggiunta',
      message: `Hai utilizzato ${quota.used} analisi su ${quota.dailyLimit}. La quota sarà nuovamente disponibile dal ${resetsAt}.`
    }
  }

  switch (error.code) {
    case 'ANALYSIS_FAILED':
      return {
        title: 'Analisi non completata',
        message:
          'L’elaborazione AI è terminata con un errore. L’Analysis è stata registrata nella cronologia.'
      }

    case 'AI_CONFIGURATION_UNAVAILABLE':
      return {
        title: 'Servizio AI non disponibile',
        message: 'La configurazione del servizio AI non è attualmente disponibile.',
      }

    case 'DOCUMENT_NOT_FOUND':
      return {
        title: 'Documento non trovato',
        message: 'Il documento non è più disponibile o non appartiene al tuo account.',
      }

    default:
      return {
        title: 'Impossibile avviare l’analisi',
        message: error.message,
      }
  }
}


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

    const outcome = await runAnalysis(documentId)

    if (!outcome.ok) {
        const failedAnalysis = getAnalysisFailedDetails(outcome.error)

        if (failedAnalysis) {
        setSelectedAnalysisId(failedAnalysis.analysisId)
        reloadAnalyses()
        }

        return
    }

    setSelectedAnalysisId(outcome.data.analysisId)
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

    const analysisStartErrorContent = analysisStartError
        ? getAnalysisStartErrorContent(
            analysisStartError,
        )
        : null

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

                {analysisStartErrorContent && <ErrorState title={analysisStartErrorContent.title} message={analysisStartErrorContent.message} />}

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
                                        {getAnalysisStatusLabel(analysis.status)}
                                    </span>
                                </div>

                                <h2>{new Date(analysis.createdAt).toLocaleString('it-IT')}</h2>

                                <div className="document-card__meta">
                                    <span>{analysis.id}</span>
                                    {analysis.status === 'ERROR' &&
                                        analysis.errorMessage && (
                                            <span>
                                                {analysis.errorMessage}
                                            </span>
                                        )}
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

                    {!selectedAnalysisLoading && !selectedAnalysisError && selectedAnalysis?.status === 'QUEUED' && (
                        <div className="frontend-notice">
                            <strong>Analisi in coda</strong>
                            <p>L'analisi è stata registrata ed è in attesa di elaborazione.</p>
                            <button
                            type="button"
                            className="button button--secondary"
                            onClick={reloadSelectedAnalysis}
                            >
                            Aggiorna stato
                            </button>
                        </div>
                        )}

                        {!selectedAnalysisLoading && !selectedAnalysisError && selectedAnalysis?.status === 'PROCESSING' && (
                        <div className="frontend-notice">
                            <strong>Analisi in elaborazione</strong>
                            <p>Il documento è attualmente in elaborazione.</p>
                            <button
                            type="button"
                            className="button button--secondary"
                            onClick={reloadSelectedAnalysis}
                            >
                            Aggiorna stato
                            </button>
                        </div>
                        )}

                        {!selectedAnalysisLoading && !selectedAnalysisError && selectedAnalysis?.status === 'ERROR' && (
                        <ErrorState
                            title="Analisi non completata"
                            message={selectedAnalysis.errorMessage ?? 'L’analisi è terminata con un errore.'}
                        />
                        )}

                        {!selectedAnalysisLoading &&
                        !selectedAnalysisError &&
                        selectedAnalysis?.status === 'READY' &&
                        selectedAnalysis.result && (
                            <div className="frontend-notice">
                            <strong>Analisi pronta</strong>
                            <p>
                                {selectedAnalysis.result.pages.length} pagine
                                {' · '}
                                {selectedAnalysis.result.entities.length} entità
                                {' · '}
                                {selectedAnalysis.result.fields.length} campi
                            </p>
                            </div>
                        )}

                        {!selectedAnalysisLoading &&
                        !selectedAnalysisError &&
                        selectedAnalysis?.status === 'READY' &&
                        !selectedAnalysis.result && (
                            <ErrorState
                            title="Risultato non disponibile"
                            message="L'Analysis risulta completata, ma il risultato non è disponibile."
                            />
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