import { useEffect, useRef } from 'react'

import UploadSummary from './UploadSummary'
import type { DocumentCategory } from '../../types/upload'


type ConfirmUploadDialogProps = {
    isOpen: boolean
    file: File | null
    category: DocumentCategory

    onCancel: () => void
    onConfirm: () => void
}


function ConfirmUploadDialog({ isOpen, file, category, onCancel, onConfirm }: ConfirmUploadDialogProps) {
    const dialogRef = useRef<HTMLDialogElement>(null)

    useEffect(() => {
        const dialog = dialogRef.current

        if (!dialog) {
            return
        }
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
                        category={category}
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