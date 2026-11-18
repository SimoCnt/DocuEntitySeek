import { useMemo, useState } from 'react'

import type {
  AnalysisExtractedField,
  AnalysisResult,
  AnalysisResultPage,
  EntityOccurrence,
} from '../../types/analysis'


type AnalysisResultViewerProps = {
  documentName: string
  result: AnalysisResult
}

type PageSegment =
  | {
      type: 'text'
      key: string
      text: string
    }
  | {
      type: 'entity'
      key: string
      text: string
      entity: EntityOccurrence
    }

const FIELD_STATUS_LABELS: Record<string, string> = {
  EXTRACTED: 'Estratto',
  AMBIGUOUS: 'Ambiguo',
  NOT_FOUND: 'Non trovato',
  ERROR: 'Errore',
}

function formatConfidence(confidence: number | null): string {
  if (confidence === null) return '—'
  return `${Math.round(confidence * 100)}%`
}

function buildPageSegments(
  page: AnalysisResultPage,
  entities: EntityOccurrence[],
  activeLabels: Set<string>,
): PageSegment[] {
  const pageEntities = entities
    .filter(
      (entity) =>
        entity.isVisible &&
        entity.page === page.pageNumber &&
        activeLabels.has(entity.label),
    )
    .filter(
      (entity) =>
        entity.pageStart >= 0 &&
        entity.pageEnd > entity.pageStart &&
        entity.pageEnd <= page.text.length,
    )
    .sort((left, right) => {
      if (left.pageStart !== right.pageStart) {
        return left.pageStart - right.pageStart
      }

      return right.pageEnd - left.pageEnd
    })

  const segments: PageSegment[] = []
  let cursor = 0

  for (const entity of pageEntities) {
    if (entity.pageStart < cursor) continue

    if (entity.pageStart > cursor) {
      segments.push({
        type: 'text',
        key: `text-${cursor}-${entity.pageStart}`,
        text: page.text.slice(cursor, entity.pageStart),
      })
    }

    segments.push({
      type: 'entity',
      key: entity.id,
      text: page.text.slice(entity.pageStart, entity.pageEnd),
      entity,
    })

    cursor = entity.pageEnd
  }

  if (cursor < page.text.length) {
    segments.push({
      type: 'text',
      key: `text-${cursor}-${page.text.length}`,
      text: page.text.slice(cursor),
    })
  }

  return segments
}

function AnalysisResultViewer({ documentName, result }: AnalysisResultViewerProps) {
  const { schema, pages, entities, fields } = result

  const orderedPages = useMemo(
    () => [...pages].sort((left, right) => left.pageNumber - right.pageNumber),
    [pages],
  )

  const orderedEntityDefinitions = useMemo(
    () => [...schema.entityDefinitions].sort((left, right) => left.sortOrder - right.sortOrder),
    [schema.entityDefinitions],
  )

  const orderedFieldDefinitions = useMemo(
    () => [...schema.fieldDefinitions].sort((left, right) => left.sortOrder - right.sortOrder),
    [schema.fieldDefinitions],
  )

  const [selectedPageNumber, setSelectedPageNumber] = useState<number | null>(
    orderedPages[0]?.pageNumber ?? null,
  )
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null)
  const [activeLabels, setActiveLabels] = useState<Set<string>>(
    () => new Set(orderedEntityDefinitions.map((definition) => definition.label)),
  )

  const selectedPage =
    orderedPages.find((page) => page.pageNumber === selectedPageNumber) ??
    orderedPages[0] ??
    null

  const selectedEntity = entities.find((entity) => entity.id === selectedEntityId) ?? null

  const entityDefinitionByLabel = useMemo(
    () => new Map(schema.entityDefinitions.map((definition) => [definition.label, definition])),
    [schema.entityDefinitions],
  )

  const fieldDefinitionByKey = useMemo(
    () => new Map(schema.fieldDefinitions.map((definition) => [definition.fieldKey, definition])),
    [schema.fieldDefinitions],
  )

  const fieldByKey = useMemo(
    () => new Map(fields.map((field) => [field.fieldKey, field])),
    [fields],
  )

  const pageSegments = useMemo(
    () => selectedPage ? buildPageSegments(selectedPage, entities, activeLabels) : [],
    [selectedPage, entities, activeLabels],
  )

  const currentPageIndex = selectedPage
    ? orderedPages.findIndex((page) => page.pageNumber === selectedPage.pageNumber)
    : -1

  function toggleLabel(label: string) {
    setActiveLabels((current) => {
      const next = new Set(current)

      if (next.has(label)) {
        next.delete(label)
      } else {
        next.add(label)
      }

      return next
    })
  }

  function showAllLabels() {
    setActiveLabels(new Set(orderedEntityDefinitions.map((definition) => definition.label)))
  }

  function hideAllLabels() {
    setActiveLabels(new Set())
    setSelectedEntityId(null)
  }

  function goToPage(pageNumber: number | null) {
    if (pageNumber === null) return

    const exists = orderedPages.some((page) => page.pageNumber === pageNumber)

    if (!exists) return

    setSelectedPageNumber(pageNumber)
    setSelectedEntityId(null)
  }

  function renderField(field: AnalysisExtractedField | undefined, fieldKey: string) {
    const definition = fieldDefinitionByKey.get(fieldKey)

    if (!definition) return null

    const status = field?.status ?? 'NOT_FOUND'

    return (
      <article key={fieldKey} className="analysis-viewer__field">
        <div className="analysis-viewer__field-header">
          <div>
            <strong>{definition.label}</strong>
            <span className="analysis-viewer__field-key">{definition.fieldKey}</span>
          </div>

          <span className={`analysis-viewer__field-status analysis-viewer__field-status--${status.toLowerCase()}`}>
            {FIELD_STATUS_LABELS[status] ?? status}
          </span>
        </div>

        <p className="analysis-viewer__field-description">{definition.description}</p>
        <div className="analysis-viewer__field-value">{field?.value ?? 'Nessun valore estratto'}</div>

        <div className="analysis-viewer__field-meta">
          <span>Confidence: {formatConfidence(field?.confidence ?? null)}</span>

          {field?.page !== null && field?.page !== undefined && (
            <button
              type="button"
              className="button button--secondary"
              onClick={() => goToPage(field.page)}
            >
              Pagina {field.page}
            </button>
          )}
        </div>

        {field && field.candidates.length > 0 && (
          <details className="analysis-viewer__candidates">
            <summary>Candidati alternativi ({field.candidates.length})</summary>

            <div className="analysis-viewer__candidate-list">
              {[...field.candidates]
                .sort((left, right) => left.rank - right.rank)
                .map((candidate) => (
                  <div key={candidate.id} className="analysis-viewer__candidate">
                    <div>
                      <strong>{candidate.value}</strong>
                      <span>Confidence: {formatConfidence(candidate.confidence)}</span>
                    </div>

                    {candidate.page !== null && (
                      <button
                        type="button"
                        className="button button--secondary"
                        onClick={() => goToPage(candidate.page)}
                      >
                        Pagina {candidate.page}
                      </button>
                    )}
                  </div>
                ))}
            </div>
          </details>
        )}
      </article>
    )
  }

  if (orderedPages.length === 0) {
    return (
      <section className="page-section">
        <div className="empty-state">
          <h2>Risultato senza pagine</h2>
          <p>L’Analysis è stata completata, ma non contiene testo visualizzabile.</p>
        </div>
      </section>
    )
  }

  return (
    <section className="analysis-viewer">
      <header className="analysis-viewer__header">
        <div>
          <span className="section-heading__eyebrow">Risultato AI</span>
          <h2>{documentName}</h2>

          <p>
            Schema <strong>{schema.name}</strong> · {schema.domain} · v{schema.version}
          </p>
        </div>

        <div className="analysis-viewer__stats">
          <span>{orderedPages.length} pagine</span>
          <span>{entities.length} entità</span>
          <span>{fields.length} campi</span>
        </div>
      </header>

      <div className="analysis-viewer__layout">
        <aside className="analysis-viewer__sidebar">
          <div className="analysis-viewer__filter-header">
            <h3>Entità</h3>

            <div>
              <button
                type="button"
                className="button button--secondary"
                onClick={showAllLabels}
              >
                Tutte
              </button>

              <button
                type="button"
                className="button button--secondary"
                onClick={hideAllLabels}
              >
                Nessuna
              </button>
            </div>
          </div>

          <div className="analysis-viewer__filters">
            {orderedEntityDefinitions.map((definition) => {
              const active = activeLabels.has(definition.label)

              return (
                <label key={definition.label} className="analysis-viewer__filter">
                  <input
                    type="checkbox"
                    checked={active}
                    onChange={() => toggleLabel(definition.label)}
                  />

                  <span
                    className="analysis-viewer__color"
                    style={{ backgroundColor: definition.color }}
                  />

                  <span>
                    <strong>{definition.label}</strong>
                    <small>{definition.description}</small>
                  </span>
                </label>
              )
            })}
          </div>

          {selectedEntity && (
            <div className="analysis-viewer__selected-entity">
              <span className="section-heading__eyebrow">Entità selezionata</span>
              <strong>{selectedEntity.text}</strong>
              <span>{selectedEntity.label}</span>
              <span>Confidence: {formatConfidence(selectedEntity.confidence)}</span>
              <span>Pagina {selectedEntity.page}</span>
            </div>
          )}
        </aside>

        <main className="analysis-viewer__document">
          <div className="analysis-viewer__page-nav">
            <button
              type="button"
              className="button button--secondary"
              disabled={currentPageIndex <= 0}
              onClick={() => {
                const previous = orderedPages[currentPageIndex - 1]

                if (previous) {
                  goToPage(previous.pageNumber)
                }
              }}
            >
              ← Precedente
            </button>

            <span>
              Pagina {selectedPage?.pageNumber} · {currentPageIndex + 1} di {orderedPages.length}
            </span>

            <button
              type="button"
              className="button button--secondary"
              disabled={currentPageIndex === orderedPages.length - 1}
              onClick={() => {
                const next = orderedPages[currentPageIndex + 1]

                if (next) {
                  goToPage(next.pageNumber)
                }
              }}
            >
              Successiva →
            </button>
          </div>

          <article className="analysis-viewer__page">
            {pageSegments.map((segment) => {
              if (segment.type === 'text') {
                return <span key={segment.key}>{segment.text}</span>
              }

              const definition = entityDefinitionByLabel.get(segment.entity.label)
              const selected = segment.entity.id === selectedEntityId

              return (
                <button
                  key={segment.key}
                  type="button"
                  className={
                    selected
                      ? 'analysis-viewer__entity analysis-viewer__entity--selected'
                      : 'analysis-viewer__entity'
                  }
                  style={{ backgroundColor: definition?.color ?? '#e5e7eb' }}
                  title={`${segment.entity.label} · ${formatConfidence(segment.entity.confidence)}`}
                  onClick={() => setSelectedEntityId(segment.entity.id)}
                >
                  {segment.text}
                </button>
              )
            })}
          </article>
        </main>

        <aside className="analysis-viewer__fields">
          <h3>Campi estratti</h3>

          {orderedFieldDefinitions.length === 0 ? (
            <p>Lo schema non contiene campi strutturati.</p>
          ) : (
            orderedFieldDefinitions.map((definition) =>
              renderField(fieldByKey.get(definition.fieldKey), definition.fieldKey),
            )
          )}
        </aside>
      </div>
    </section>
  )
}

export default AnalysisResultViewer