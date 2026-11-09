import type { DocumentPage, EntityDefinition } from '../../types/analysis'


type AnnotatedDocumentMockProps = {
    documentName: string
    page: DocumentPage
    entityDefinitions: EntityDefinition[]
    activeLabels: string[]
    selectedEntityId: string | null
    onSelectEntity: (entityId: string) => void
}


function AnnotatedDocumentMock({documentName, page, entityDefinitions, activeLabels, selectedEntityId, onSelectEntity}: AnnotatedDocumentMockProps) {
    function getEntityColor(label: string) {
        return (
            entityDefinitions.find(
                (definition) =>
                    definition.label === label,
            )?.color ?? '#edf0f4'
        )
    }

    return (
        <div className="document-viewer">
            <div className="document-viewer__header">
                <strong>{documentName}</strong>
                <span>Pagina {page.pageNumber}</span>
            </div>

            <div className="document-viewer__content">
                {page.segments.map(
                    (segment, index) => {
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
                                        getEntityColor(
                                            segment.label,
                                        ),
                                }}
                                onClick={() =>
                                    onSelectEntity(
                                        segment.id,
                                    )
                                }
                            >
                                <span>{segment.text}</span>
                                <small>{segment.label}</small>
                            </button>
                        )
                    },
                )}
            </div>
        </div>
    )
}

export default AnnotatedDocumentMock