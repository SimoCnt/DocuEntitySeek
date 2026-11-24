/**
 * Collect a new name when duplicating a custom schema.
 */

import { useEffect, useRef, useState, type FormEvent } from 'react'


/**
 * Properties configuring the duplicate schema dialog component.
 */
type DuplicateSchemaDialogProps = {
  isOpen: boolean
  schemaName: string
  isSubmitting: boolean
  errorMessage: string | null
  onCancel: () => void
  onConfirm: (name: string) => Promise<void>
}


/**
 * Collect a name before duplicating an existing extraction schema.
 */
function DuplicateSchemaDialog({
  isOpen,
  schemaName,
  isSubmitting,
  errorMessage,
  onCancel,
  onConfirm,
}: DuplicateSchemaDialogProps) {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const [name, setName] = useState('')

  useEffect(() => {
    if (isOpen) {
      setName(`${schemaName} - copia`)
    }
  }, [isOpen, schemaName])

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

  
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const normalized = name.trim()

    if (!normalized) return

    await onConfirm(normalized)
  }

  return (
    <dialog
      ref={dialogRef}
      className="upload-dialog"
      aria-labelledby="duplicate-schema-title"
      onClose={onCancel}
    >
      <form
        className="upload-dialog__content"
        onSubmit={(event) => void handleSubmit(event)}
      >
        <span className="section-heading__eyebrow">Duplicazione</span>
        <h2 id="duplicate-schema-title">Duplica schema</h2>
        <p>Verrà creato un nuovo schema indipendente con versione 1.</p>

        <div className="form-field">
          <label htmlFor="duplicate-schema-name">Nome nuovo schema</label>

          <input
            id="duplicate-schema-name"
            type="text"
            required
            maxLength={120}
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
        </div>

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
            type="submit"
            className="button button--primary"
            disabled={isSubmitting || !name.trim()}
          >
            {isSubmitting ? 'Duplicazione...' : 'Duplica'}
          </button>
        </div>
      </form>
    </dialog>
  )
}

export default DuplicateSchemaDialog
