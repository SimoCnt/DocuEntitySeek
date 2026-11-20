import { useState } from 'react'

import ErrorState from '../components/feedback/ErrorState'
import LoadingState from '../components/feedback/LoadingState'
import CustomSchemaForm from '../components/schemas/CustomSchemaForm'
import { useAuth } from '../auth/AuthContext'
import useCreateCustomSchema from '../hooks/useCreateCustomSchema'
import useCustomSchemaActions from '../hooks/useCustomSchemaActions'
import useCustomSchemas from '../hooks/useCustomSchemas'
import useDocumentTitle from '../hooks/useDocumentTitle'
import type { CustomSchema, CustomSchemaCreateRequest, CustomSchemaSummary } from '../types/customSchema'
import ArchiveSchemaDialog from '../components/schemas/ArchiveSchemaDialog'
import DuplicateSchemaDialog from '../components/schemas/DuplicateSchemaDialog'
import { getCustomSchemaErrorMessage } from '../utils/customSchemaErrors'


function SchemasPage() {
  const { user } = useAuth()
  const customSchemasEnabled = user?.plan.customSchemasEnabled === true
  const { schemas, isLoading, error, reload } = useCustomSchemas(customSchemasEnabled)

  const {
    isLoading: isCreating,
    error: createError,
    create,
    clearError: clearCreateError,
  } = useCreateCustomSchema()

  const {
    isLoading: isActing,
    error: actionError,
    load,
    update,
    duplicate,
    archive,
    clearError: clearActionError,
  } = useCustomSchemaActions()

  const [editingSchema, setEditingSchema] = useState<CustomSchema | null>(null)
  const [duplicatingSchema, setDuplicatingSchema] = useState<CustomSchemaSummary | null>(null)
  const [archivingSchema, setArchivingSchema] = useState<CustomSchemaSummary | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const [duplicateValidationError, setDuplicateValidationError] = useState<string | null>(null)

  const createErrorMessage = getCustomSchemaErrorMessage(createError)
  const actionErrorMessage = getCustomSchemaErrorMessage(actionError)

  useDocumentTitle('Schemi di estrazione | DocuEntitySeek')


  async function handleCreate(payload: CustomSchemaCreateRequest): Promise<boolean> {
    clearCreateError()
    setSuccessMessage(null)

    const result = await create(payload)

    if (!result) return false

    setSuccessMessage(`Schema "${result.name}" creato correttamente.`)
    reload()

    return true
  }


  async function handleOpenEdit(schemaId: string) {
    clearActionError()

    const result = await load(schemaId)

    if (!result) return

    setEditingSchema(result)
  }


  async function handleUpdate(payload: CustomSchemaCreateRequest): Promise<boolean> {
    if (!editingSchema) return false

    clearActionError()
    setSuccessMessage(null)

    const result = await update(editingSchema.schemaId, payload)

    if (!result) return false

    setEditingSchema(null)
    setSuccessMessage(`Schema aggiornato alla versione ${result.version}.`)
    reload()

    return true
  }


  function handleOpenDuplicate(schema: CustomSchemaSummary) {
    clearActionError()
    setSuccessMessage(null)
    setDuplicateValidationError(null)
    setDuplicatingSchema(schema)
  }


  async function handleConfirmDuplicate(name: string) {
    if (!duplicatingSchema) return

    const normalizedName = name.trim()

    const duplicatedName = schemas.some(
      (schema) => schema.name.trim().toLowerCase() === normalizedName.toLowerCase(),
    )

    if (duplicatedName) {
      setDuplicateValidationError(null)
      setDuplicateValidationError('Esiste già uno schema personalizzato con questo nome.')

      return
  }

    clearActionError()

    const result = await duplicate(duplicatingSchema.schemaId, normalizedName)

    if (!result) return

    setDuplicatingSchema(null)
    setSuccessMessage(`Schema "${result.name}" duplicato correttamente.`)
    reload()
  }


  function handleOpenArchive(schema: CustomSchemaSummary) {
    clearActionError()
    setSuccessMessage(null)
    setArchivingSchema(schema)
  }


  async function handleConfirmArchive() {
    if (!archivingSchema) {
        return
    }

    clearActionError()

    const schemaName = archivingSchema.name
    const success = await archive(archivingSchema.schemaId)

    if (!success) {
        return
    }

    if (
        editingSchema?.schemaId ===
        archivingSchema.schemaId
    ) {
        setEditingSchema(null)
    }

    setArchivingSchema(null)
    setSuccessMessage(`Schema "${schemaName}" archiviato correttamente.`)
    reload()
  }
  

  if (!customSchemasEnabled) {
    return (
      <>
        <header className="page-hero">
          <div className="page-hero__content">
            <span className="page-hero__eyebrow">Funzionalità Premium</span>
            <h1>Schemi personalizzati</h1>
            <p>Crea e gestisci schemi di estrazione personalizzati.</p>
          </div>
        </header>
        <section className="page-section page-section--workspace">
          <div className="empty-state">
            <h2>Funzionalità non disponibile</h2>
            <p>
              Il tuo piano attuale utilizza lo schema predefinito. La creazione e gestione di
              schemi personalizzati richiede un piano che abilita questa funzione.
            </p>
          </div>
        </section>
      </>
    )
  }

  const activeSchemas = schemas.filter((schema) => !schema.isArchived)
  const archivedSchemas = schemas.filter((schema) => schema.isArchived)

  return (
    <>
      <header className="page-hero">
        <div className="page-hero__content">
          <span className="page-hero__eyebrow">Premium</span>
          <h1>I miei schemi</h1>
          <p>Crea e versiona schemi di estrazione personalizzati.</p>
        </div>
      </header>

      {successMessage && (
        <div
            className="frontend-notice page-feedback"
            role="status"
        >
            <strong>
                Operazione completata
            </strong>

            <p>
                {successMessage}
            </p>
        </div>
      )}      

      {editingSchema ? (
        <section className="page-section page-section--workspace">
          <div className="section-heading">
            <span className="section-heading__eyebrow">Modifica schema</span>
            <h2>{editingSchema.name}</h2>
            <p>
              Il salvataggio creerà la versione {editingSchema.version + 1}.
              La versione attuale resterà nello storico.
            </p>
          </div>

          <CustomSchemaForm
            existingSchemas={schemas}
            initialValue={editingSchema}
            isSubmitting={isActing}
            errorMessage={createErrorMessage}
            submitLabel={`Salva come v${editingSchema.version + 1}`}
            onCancel={() => setEditingSchema(null)}
            onSubmit={handleUpdate}
          />
        </section>
      ) : (
        <section className="page-section page-section--workspace">
          <div className="section-heading">
            <span className="section-heading__eyebrow">Nuovo schema</span>
            <h2>Crea uno schema</h2>
          </div>

          <CustomSchemaForm            
            existingSchemas={schemas}
            isSubmitting={isCreating}
            errorMessage={createErrorMessage}
            onSubmit={handleCreate}
          />
        </section>
      )}

      <section className="page-section page-section--workspace">
        <div className="section-heading">
          <span className="section-heading__eyebrow">Schemi disponibili</span>
          <h2>Schemi attivi</h2>
        </div>

        {isLoading && <LoadingState message="Caricamento degli schemi..." />}

        {error && <ErrorState message={error.message} onRetry={reload} />}

        {!isLoading && !error && activeSchemas.length === 0 && (
          <div className="empty-state">
            <h2>Nessuno schema personalizzato</h2>
            <p>Crea il tuo primo schema utilizzando il modulo qui sopra.</p>
          </div>
        )}

        {!isLoading && !error && activeSchemas.length > 0 && (
          <div className="documents-grid">
            {activeSchemas.map((schema) => (
              <article key={schema.schemaId} className="document-card">
                <div className="document-card__header">
                  <span className="document-card__type">Schema custom</span>
                  <span className="document-status document-status--ready">Attivo</span>
                </div>

                <h3>{schema.name}</h3>
                <p>{schema.domain}</p>

                <div className="document-card__meta">
                  <span>Versione {schema.version}</span>
                  <span>{schema.entityCount} entità</span>
                  <span>{schema.fieldCount} campi</span>
                </div>

                <div className="schema-card__actions">
                  <button
                    type="button"
                    className="button button--secondary"
                    disabled={isActing}
                    onClick={() => void handleOpenEdit(schema.schemaId)}
                  >
                    Modifica
                  </button>

                  <button
                    type="button"
                    className="button button--secondary"
                    disabled={isActing}
                    onClick={() => handleOpenDuplicate(schema)}
                  >
                    Duplica
                  </button>

                  <button
                    type="button"
                    className="button button--secondary"
                    disabled={isActing}
                    onClick={() => handleOpenArchive(schema)}
                >
                    Archivia
                </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      {archivedSchemas.length > 0 && (
        <section className="page-section page-section--workspace">
          <div className="section-heading">
            <span className="section-heading__eyebrow">Storico</span>
            <h2>Schemi archiviati</h2>
          </div>

          <div className="documents-grid">
            {archivedSchemas.map((schema) => (
              <article key={schema.schemaId} className="document-card">
                <div className="document-card__header">
                  <span className="document-card__type">Schema custom</span>
                  <span className="document-status document-status--error">Archiviato</span>
                </div>

                <h3>{schema.name}</h3>
                <p>{schema.domain}</p>

                <div className="document-card__meta">
                  <span>Versione {schema.version}</span>
                  <span>{schema.entityCount} entità</span>
                  <span>{schema.fieldCount} campi</span>
                </div>
              </article>
            ))}
          </div>
        </section>
      )}

      <DuplicateSchemaDialog
          isOpen={
              duplicatingSchema !== null
          }
          schemaName={
              duplicatingSchema?.name ??
              ''
          }
          isSubmitting={isActing}
          errorMessage={
              duplicateValidationError ??
              actionErrorMessage
          }
          onCancel={() => {
              setDuplicatingSchema(null)
              setDuplicateValidationError(null)
              clearActionError()
          }}
          onConfirm={
              handleConfirmDuplicate
          }
      />


      <ArchiveSchemaDialog
          isOpen={
              archivingSchema !== null
          }
          schemaName={
              archivingSchema?.name ??
              ''
          }
          isSubmitting={isActing}
          errorMessage={
              actionErrorMessage
          }
          onCancel={() => {
              setArchivingSchema(null)
              clearActionError()
          }}
          onConfirm={
              handleConfirmArchive
          }
      />
    </>
  )
}

export default SchemasPage