import { useMemo, useState } from 'react'

import PdfDocumentViewer from '../pdf/PdfDocumentViewer'

import type {
  AnalysisExtractedField,
  AnalysisResult,
} from '../../types/analysis'


type AnalysisResultViewerProps = {
  documentId: string
  analysisId: string
  documentName: string
  result: AnalysisResult
}

function AnalysisResultViewer({ documentId, analysisId, documentName, result }: AnalysisResultViewerProps) {
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
  const [selectedFieldId, setSelectedFieldId] = useState<string | null>(null)
  const [activeLabels, setActiveLabels] = useState<Set<string>>(
    () => new Set(orderedEntityDefinitions.map((definition) => definition.label)),
  )

  const selectedPage =
    orderedPages.find((page) => page.pageNumber === selectedPageNumber) ??
    orderedPages[0] ??
    null

  const selectedEntity = entities.find((entity) => entity.id === selectedEntityId) ?? null

  const entityColors = useMemo(() => Object.fromEntries(schema.entityDefinitions.map((definition) => [definition.label, definition.color])), [schema.entityDefinitions])

  const fieldDefinitionByKey = useMemo(
    () => new Map(schema.fieldDefinitions.map((definition) => [definition.fieldKey, definition])),
    [schema.fieldDefinitions],
  )

  const fieldByKey = useMemo(
    () => new Map(fields.map((field) => [field.fieldKey, field])),
    [fields],
  )

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
    setSelectedFieldId(null)
  }

  function goToField(field: AnalysisExtractedField) {
    if (field.page === null) return
    goToPage(field.page)
    setSelectedFieldId(field.id)
  }

  function renderField(field: AnalysisExtractedField | undefined, fieldKey: string) {
    const definition = fieldDefinitionByKey.get(fieldKey)

    if (!definition) return null

    return (
      <article key={fieldKey} className="analysis-viewer__field">
        <div className="analysis-viewer__field-header">
          <div>
            <strong>{definition.label}</strong>
            <span className="analysis-viewer__field-key">{definition.fieldKey}</span>
          </div>
        </div>

        <p className="analysis-viewer__field-description">{definition.description}</p>
        <div className="analysis-viewer__field-value">{field?.status === 'ERROR' ? 'Errore durante l’estrazione' : field?.value ?? 'Nessun valore estratto'}</div>

        <div className="analysis-viewer__field-meta">
          {field?.page !== null && field?.page !== undefined && (
            <button
              type="button"
              className="button button--secondary"
              onClick={() => goToField(field)}
            >
              Pagina {field.page}
            </button>
          )}
        </div>
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
              <span>Pagina {selectedEntity.page}</span>
            </div>
          )}
        </aside>

        <main className="analysis-viewer__document">
          <PdfDocumentViewer
            documentId={documentId}
            analysisId={analysisId}
            pageNumber={selectedPage?.pageNumber ?? 1}
            onPageChange={goToPage}
            activeLabels={[...activeLabels]}
            entityColors={entityColors}
            selectedEntityId={selectedEntityId}
            selectedFieldId={selectedFieldId}
            onRegionSelect={(kind, id) => {
              if (kind === 'entity') { setSelectedEntityId(id); setSelectedFieldId(null) }
              else { setSelectedFieldId(id); setSelectedEntityId(null) }
            }}
          />
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