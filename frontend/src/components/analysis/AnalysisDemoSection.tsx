import { useState } from 'react'

import { ENTITY_LABELS, MOCK_DOCUMENT_PAGES, MOCK_EXTRACTED_FIELDS, type EntityLabel } from '../../data/analysisDemo'
import useDocumentTitle from '../../hooks/useDocumentTitle'
import AnnotatedDocumentMock from './AnnotatedDocumentMock'
import EntityFilterList from './EntityFilterList'
import ExtractedFieldsPanel from './ExtractedFieldsPanel'


function AnalysisDemoSection() {
    const [currentPageIndex, setCurrentPageIndex] = useState(0)
    const [activeLabels, setActiveLabels] = useState<EntityLabel[]>(ENTITY_LABELS)
    const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null)
    const currentPage = MOCK_DOCUMENT_PAGES[currentPageIndex]

    useDocumentTitle(`DocuEntitySeek · Pagina ${currentPage.pageNumber}`)


    function handlePreviousPage() {
        setCurrentPageIndex((currentIndex) =>
            Math.max(0, currentIndex - 1),
        )
        setSelectedEntityId(null)
    }


    function handleNextPage() {
        setCurrentPageIndex((currentIndex) =>
            Math.min(MOCK_DOCUMENT_PAGES.length - 1, currentIndex + 1),
        )
        setSelectedEntityId(null)
    }


    function handleToggleLabel(label: EntityLabel) {
        setActiveLabels((currentLabels) => {
            const isActive = currentLabels.includes(label)

            if (isActive) {
                return currentLabels.filter(
                    (currentLabel) =>
                        currentLabel !== label,
                )
            }

            return [...currentLabels, label]
        })
    }


    function handleShowAllLabels() {
        setActiveLabels(ENTITY_LABELS)
    }


    function handleHideAllLabels() {
        setActiveLabels([])
    }


    return (
        <section className="analysis-demo">
            <div className="section-heading">
                <span className="section-heading__eyebrow">Interactive demo</span>
                <h2>Esplora il documento attraverso entità e informazioni strutturate</h2>
                <p>Attiva o disattiva le categorie NER e naviga tra le pagine del documento.</p>
            </div>

            <div className="analysis-demo__workspace">
                <div className="analysis-demo__main">
                    <AnnotatedDocumentMock
                        page={currentPage}
                        activeLabels={activeLabels}
                        selectedEntityId={selectedEntityId}
                        onSelectEntity={setSelectedEntityId}
                    />

                    <div className="analysis-demo__pagination">
                        <button
                            type="button"
                            onClick={handlePreviousPage}
                            disabled={currentPageIndex === 0}
                        >
                            ← Precedente
                        </button>

                        <span>Pagina {currentPage.pageNumber}</span>

                        <button
                            type="button"
                            onClick={handleNextPage}
                            disabled={
                                currentPageIndex ===
                                MOCK_DOCUMENT_PAGES.length - 1
                            }
                        >
                            Successiva →
                        </button>
                    </div>
                </div>

                <aside className="analysis-demo__sidebar">
                    <EntityFilterList
                        activeLabels={activeLabels}
                        onToggleLabel={handleToggleLabel}
                        onShowAll={handleShowAllLabels}
                        onHideAll={handleHideAllLabels}
                    />

                    <ExtractedFieldsPanel
                        fields={MOCK_EXTRACTED_FIELDS}
                    />
                </aside>
            </div>
        </section>
    )
}

export default AnalysisDemoSection