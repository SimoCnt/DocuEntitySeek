import { useEffect, useRef } from 'react'

type ArchiveSchemaDialogProps = {
  isOpen: boolean
  schemaName: string
  isSubmitting: boolean
  errorMessage: string | null
  onCancel: () => void
  onConfirm: () => Promise<void>
}


function ArchiveSchemaDialog({
  isOpen,
  schemaName,
  isSubmitting,
  errorMessage,
  onCancel,
  onConfirm,
}: ArchiveSchemaDialogProps) {
  const dialogRef = useRef<HTMLDialogElement>(null)

  useEffect(() => {
    const dialog = dialogRef.current

    if (!dialog) return

    if (isOpen && !dialog.open) {
      dialog.showModal()
      return
    }

    if (!isOpen && dialog.open) {
      dialog.close()
    }
  }, [isOpen])

  return (
    <dialog
      ref={dialogRef}
      className="upload-dialog"
      aria-labelledby="archive-schema-title"
      onClose={onCancel}
    >
      <div className="upload-dialog__content">
        <span className="section-heading__eyebrow">Archiviazione</span>
        <h2 id="archive-schema-title">Archivia schema</h2>

        <p>
          Vuoi archiviare <strong>{schemaName}</strong>?
        </p>

        <p>
          Non sarà più disponibile per nuove analisi, ma tutte
          le versioni e le Analysis storiche resteranno conservate.
        </p>

        {errorMessage && (
          <p className="form-field__error" role="alert">
            {errorMessage}
          </p>
        )}

        <div className="upload-dialog__actions">
          <button
            type="button"
            className="button button--secondary"
            disabled={isSubmitting}
            onClick={onCancel}
          >
            Annulla
          </button>

          <button
            type="button"
            className="button button--primary"
            disabled={isSubmitting}
            onClick={() => void onConfirm()}
          >
            {isSubmitting ? 'Archiviazione...' : 'Archivia schema'}
          </button>
        </div>
      </div>
    </dialog>
  )
}

export default ArchiveSchemaDialog