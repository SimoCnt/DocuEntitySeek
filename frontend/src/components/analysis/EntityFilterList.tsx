import type { EntityDefinition } from '../../types/analysis'


type EntityFilterListProps = {
    definitions: EntityDefinition[]
    activeLabels: string[]
    
    onToggleLabel: (label: string) => void
    onShowAll: () => void
    onHideAll: () => void
}


function EntityFilterList({ definitions, activeLabels, onToggleLabel, onShowAll, onHideAll }: EntityFilterListProps) {
    return (
        <div className="entity-filter-list">
            <div className="entity-filter-list__heading">
                <h3>Entità</h3>

                <div>
                    <button
                        type="button"
                        onClick={onShowAll}
                    >
                        Tutte
                    </button>

                    <button
                        type="button"
                        onClick={onHideAll}
                    >
                        Nessuna
                    </button>
                </div>
            </div>

            <div className="entity-filter-list__items">
                {definitions.map(
                    (definition) => {
                        const checked =
                            activeLabels.includes(definition.label)

                        return (
                            <label
                                key={definition.label}
                                className="entity-filter-item"
                            >
                                <input
                                    type="checkbox"
                                    checked={checked}
                                    onChange={() =>
                                        onToggleLabel(definition.label)
                                    }
                                />

                                <span
                                    className="entity-filter-item__color"
                                    style={{
                                        backgroundColor:
                                            definition.color,
                                    }}
                                />

                                <span>{definition.label}</span>
                            </label>
                        )
                    },
                )}
            </div>
        </div>
    )
}

export default EntityFilterList