import { useState } from 'react'

import type { DocumentAnalysis } from '../../types/analysis'
import AnnotatedDocumentMock from './AnnotatedDocumentMock'
import EntityFilterList from './EntityFilterList'
import ExtractedFieldsPanel from './ExtractedFieldsPanel'


type AnalysisDemoSectionProps = {
    documentName: string
    analysis: DocumentAnalysis
}


function AnalysisDemoSection({ documentName, analysis }: AnalysisDemoSectionProps) {
    const availableLabels =
        analysis.entityDefinitions.map(
            (definition) =>
                definition.label,
        )
    const [currentPageIndex, setCurrentPageIndex] = useState(0)
    const [activeLabels, setActiveLabels] = useState<string[]>(availableLabels)
    const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null)
    const currentPage = analysis.pages[currentPageIndex]


    function handlePreviousPage() {
        setCurrentPageIndex(
            (currentIndex) =>
                Math.max(
                    0,
                    currentIndex - 1,
                ),
        )

        setSelectedEntityId(null)
    }


    function handleNextPage() {
        setCurrentPageIndex(
            (currentIndex) =>
                Math.min(
                    analysis.pages.length - 1,
                    currentIndex + 1,
                ),
        )

        setSelectedEntityId(null)
    }


    function handleToggleLabel(label: string) {
        setActiveLabels(
            (currentLabels) => {
                if (
                    currentLabels.includes(label)
                ) {
                    return currentLabels.filter(
                        (currentLabel) =>
                            currentLabel !== label,
                    )
                }

                return [
                    ...currentLabels,
                    label,
                ]
            },
        )
    }


    function handleShowAllLabels() {
        setActiveLabels(
            availableLabels,
        )
    }


    function handleHideAllLabels() {
        setActiveLabels([])
    }

    if (!currentPage) {
        return (
            <section className="analysis-demo">
                <div className="empty-state">
                    <h2>Nessuna pagina disponibile</h2>
                </div>
            </section>
        )
    }

    return (
        <section className="analysis-demo">
            <div className="section-heading">
                <span className="section-heading__eyebrow">Document analysis</span>

                <h2>Entità e informazioni strutturate</h2>
            </div>

            <div className="analysis-demo__workspace">
                <div className="analysis-demo__main">
                    <AnnotatedDocumentMock
                        documentName={documentName}
                        page={currentPage}
                        entityDefinitions={analysis.entityDefinitions}
                        activeLabels={activeLabels}
                        selectedEntityId={selectedEntityId}
                        onSelectEntity={setSelectedEntityId}
                    />

                    <div className="analysis-demo__pagination">
                        <button
                            type="button"
                            onClick={
                                handlePreviousPage
                            }
                            disabled={
                                currentPageIndex === 0
                            }
                        >
                            ← Precedente
                        </button>

                        <span>Pagina{' '}{currentPage.pageNumber}</span>

                        <button
                            type="button"
                            onClick={
                                handleNextPage
                            }
                            disabled={
                                currentPageIndex ===
                                analysis.pages.length - 1
                            }
                        >
                            Successiva →
                        </button>
                    </div>
                </div>

                <aside className="analysis-demo__sidebar">
                    <EntityFilterList
                        definitions={
                            analysis.entityDefinitions
                        }
                        activeLabels={activeLabels}
                        onToggleLabel={handleToggleLabel}
                        onShowAll={handleShowAllLabels}
                        onHideAll={handleHideAllLabels}
                    />

                    <ExtractedFieldsPanel
                        fields={analysis.extractedFields}
                    />
                </aside>
            </div>
        </section>
    )
}

export default AnalysisDemoSection