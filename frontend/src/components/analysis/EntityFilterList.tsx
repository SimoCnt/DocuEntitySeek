import { ENTITY_COLORS, ENTITY_LABELS, type EntityLabel } from '../../data/analysisDemo'


type EntityFilterListProps = {
    activeLabels: EntityLabel[]

    onToggleLabel: (label: EntityLabel) => void
    onShowAll: () => void
    onHideAll: () => void
}


function EntityFilterList({ activeLabels, onToggleLabel, onShowAll, onHideAll }: EntityFilterListProps) {
    return (
        <div className="entity-filter-list">
            <div className="entity-filter-list__heading">
                <h3>Entità</h3>

                <div>
                    <button type="button" onClick={onShowAll}>
                        Tutte
                    </button>

                    <button type="button" onClick={onHideAll}>
                        Nessuna
                    </button>
                </div>
            </div>

            <div className="entity-filter-list__items">
                {ENTITY_LABELS.map((label) => {
                    const checked = activeLabels.includes(label)

                    return (
                        <label
                            key={label}
                            className="entity-filter-item"
                        >
                            <input
                                type="checkbox"
                                checked={checked}
                                onChange={() => onToggleLabel(label)}
                            />

                            <span
                                className="entity-filter-item__color"
                                style={{
                                    backgroundColor: ENTITY_COLORS[label],
                                }}
                            />

                            <span>{label}</span>
                        </label>
                    )
                })}
            </div>
        </div>
    )
}

export default EntityFilterList