import type { RequestError } from '../api/http'


export function getCustomSchemaErrorMessage(error: RequestError | null): string | null {
  if (!error) return null

  switch (error.code) {
    case 'CUSTOM_SCHEMA_NAME_CONFLICT':
      return 'Esiste già uno schema personalizzato con questo nome.'

    case 'CUSTOM_SCHEMA_ARCHIVED':
      return 'Lo schema è archiviato e non può più essere modificato.'

    case 'CUSTOM_SCHEMAS_NOT_AVAILABLE':
      return 'Il piano corrente non consente di utilizzare schemi personalizzati.'

    case 'EXTRACTION_SCHEMA_NOT_FOUND':
      return 'Lo schema richiesto non esiste oppure non è più disponibile.'

    default:
      break
  }

  if (error.status === 422) {
    return 'Alcuni dati dello schema non sono validi. Controlla entità e campi inseriti.'
  }

  if (error.status === 409) {
    return 'Non è possibile completare l’operazione perché lo schema è in conflitto con uno già esistente.'
  }

  return error.message
}