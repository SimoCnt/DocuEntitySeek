import type { ChangeEvent, FormEvent } from 'react'

import type { DocumentCategory } from '../../types/upload'


type DocumentUploadFormProps = {
    selectedFile: File | null
    category: DocumentCategory
    errorMessage: string | null

    onFileChange: (
        file: File | null,
    ) => void

    onCategoryChange: (
        category: DocumentCategory,
    ) => void

    onSubmit: (
        event: FormEvent<HTMLFormElement>,
    ) => void
}


function DocumentUploadForm({ selectedFile, category, errorMessage, onFileChange, onCategoryChange, onSubmit }: DocumentUploadFormProps) {
    function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
        const file = event.target.files?.[0] ?? null
        onFileChange(file)
    }

    return (
        <form className="upload-form" onSubmit={onSubmit}>
            <div className="form-field">
                <label htmlFor="document-file">Documento PDF</label>

                <input
                    id="document-file"
                    name="documentFile"
                    type="file"
                    accept=".pdf,application/pdf"
                    onChange={handleFileChange}
                    aria-describedby={
                        errorMessage
                            ? 'document-file-help document-file-error'
                            : 'document-file-help'
                    }
                />

                <p id="document-file-help" className="form-field__help">Seleziona un documento PDF da analizzare.</p>

                {selectedFile && (
                    <p className="form-field__selection">File selezionato:{' '}<strong>{selectedFile.name}</strong></p>                      
                )}

                {errorMessage && (
                    <p
                        id="document-file-error"
                        className="form-field__error"
                        role="alert"
                    >
                        {errorMessage}
                    </p>
                )}
            </div>

            <div className="form-field">
                <label htmlFor="document-category">Tipo di documento</label>

                <select
                    id="document-category"
                    name="documentCategory"
                    value={category}
                    onChange={(event) =>
                        onCategoryChange(
                            event.target
                                .value as DocumentCategory,
                        )
                    }
                >
                    <option value="DISCIPLINARE">Disciplinare</option>
                    <option value="CAPITOLATO">Capitolato</option>
                    <option value="CONTRATTO">Contratto</option>
                    <option value="BANDO">Bando</option>
                    <option value="ALTRO">Altro</option>
                </select>
            </div>

            <div className="form-field">
                <span className="form-field__label">Schema di estrazione</span>

                <div className="schema-selection">
                    <strong>Procurement</strong>
                    <span>Schema predefinito</span>
                </div>

                <p className="form-field__help">Gli schemi personalizzati saranno disponibili agli utenti Premium.</p>
            </div>

            <div className="upload-form__actions">
                <button type="submit" className="button button--primary">Continua</button>
            </div>
        </form>
    )
}

export default DocumentUploadForm