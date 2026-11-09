import { ENTITY_COLORS, type DocumentPage, type EntityLabel } from '../../data/analysisDemo'


type AnnotatedDocumentMockProps = {
    page: DocumentPage
    activeLabels: EntityLabel[]
    selectedEntityId: string | null

    onSelectEntity: (entityId: string) => void
}


function AnnotatedDocumentMock({ page, activeLabels, selectedEntityId, onSelectEntity }: AnnotatedDocumentMockProps) {
    return (
        <div className="document-viewer">
            <div className="document-viewer__header">
                <strong>Disciplinare_di_gara.pdf</strong>
                <span>Pagina {page.pageNumber}</span>
            </div>

            <div className="document-viewer__content">
                {page.segments.map((segment, index) => {
                    if (segment.type === 'text') {
                        return (
                            <span key={`text-${index}`}>{segment.text}</span>
                        )
                    }

                    const isVisible = activeLabels.includes(segment.label)

                    if (!isVisible) {
                        return (
                            <span key={segment.id}>{segment.text}</span>
                        )
                    }

                    const isSelected = segment.id === selectedEntityId

                    return (
                        <button
                            key={segment.id}
                            type="button"
                            className={
                                isSelected
                                    ? 'entity-annotation entity-annotation--selected'
                                    : 'entity-annotation'
                            }
                            style={{
                                backgroundColor:
                                    ENTITY_COLORS[segment.label],
                            }}
                            onClick={() =>
                                onSelectEntity(segment.id)
                            }
                        >
                            <span>{segment.text}</span>
                            <small>{segment.label}</small>
                        </button>
                    )
                })}
            </div>
        </div>
    )
}

export default AnnotatedDocumentMock