import { useEffect, useRef } from 'react'

import UploadSummary from './UploadSummary'


type ConfirmUploadDialogProps = {
  isOpen: boolean
  file: File | null
  schemaName: string
  onCancel: () => void
  onConfirm: () => void
}


function ConfirmUploadDialog({
  isOpen,
  file,
  schemaName,
  onCancel,
  onConfirm,
}: ConfirmUploadDialogProps) {
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
      aria-labelledby="upload-dialog-title"
      onClose={onCancel}
    >
      <div className="upload-dialog__content">
        <span className="section-heading__eyebrow">Conferma</span>
        <h2 id="upload-dialog-title">Confermare il documento?</h2>
        <p>Controlla le informazioni prima di procedere.</p>

        {file && (
          <UploadSummary
            file={file}
            schemaName={schemaName}
          />
        )}

        <div className="upload-dialog__actions">
          <button
            type="button"
            className="button button--secondary"
            onClick={onCancel}
            autoFocus
          >
            Annulla
          </button>

          <button
            type="button"
            className="button button--primary"
            onClick={onConfirm}
          >
            Conferma
          </button>
        </div>
      </div>
    </dialog>
  )
}

export default ConfirmUploadDialog