import type { ChangeEvent, FormEvent } from 'react'

import type { AvailableExtractionSchema } from '../../types/extractionSchema'


type DocumentUploadFormProps = {
  selectedFile: File | null
  errorMessage: string | null
  showSchemaSelector: boolean
  schemas: AvailableExtractionSchema[]
  schemasLoading: boolean
  schemaVersionId: string
  schemaErrorMessage: string | null
  onSchemaVersionChange: (schemaVersionId: string) => void
  onFileChange: (file: File | null) => void
  onSubmit: (event: FormEvent<HTMLFormElement>) => void
}


function DocumentUploadForm({
  selectedFile,
  errorMessage,
  showSchemaSelector,
  schemas,
  schemasLoading,
  schemaVersionId,
  schemaErrorMessage,
  onSchemaVersionChange,
  onFileChange,
  onSubmit,
}: DocumentUploadFormProps) {
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

        <p id="document-file-help" className="form-field__help">
          Seleziona un documento PDF da analizzare.
        </p>

        {selectedFile && (
          <p className="form-field__selection">
            File selezionato: <strong>{selectedFile.name}</strong>
          </p>
        )}

        {errorMessage && (
          <p id="document-file-error" className="form-field__error" role="alert">
            {errorMessage}
          </p>
        )}
      </div>

      {showSchemaSelector && (
        <div className="form-field">
          <label htmlFor="schema-version">Schema di estrazione</label>

          <select
            id="schema-version"
            name="schemaVersion"
            value={schemaVersionId}
            disabled={schemasLoading || schemas.length === 0}
            onChange={(event) => onSchemaVersionChange(event.target.value)}
          >
            <option value="" disabled>
              {schemasLoading ? 'Caricamento schemi...' : 'Seleziona uno schema'}
            </option>

            {schemas.map((schema) => (
              <option key={schema.schemaVersionId} value={schema.schemaVersionId}>
                {schema.isBuiltin
                  ? `${schema.name} — predefinito`
                  : `${schema.name} — v${schema.version}`}
              </option>
            ))}
          </select>

          {schemaErrorMessage && (
            <p className="form-field__error" role="alert">
              {schemaErrorMessage}
            </p>
          )}
        </div>
      )}

      {!showSchemaSelector && (
        <div className="form-field">
          <span className="form-field__label">Schema di estrazione</span>

          <div className="schema-selection">
            <strong>Schema predefinito</strong>
            <span>Incluso nel piano Base</span>
          </div>
        </div>
      )}

      <div className="upload-form__actions">
        <button type="submit" className="button button--primary">
          Continua
        </button>
      </div>
    </form>
  )
}

export default DocumentUploadForm