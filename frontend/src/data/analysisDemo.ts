export type EntityLabel = 
  | 'ORGANIZZAZIONE'
  | 'IMPORTO'
  | 'DATA'
  | 'ORA'
  | 'RIFERIMENTO_NORMATIVO'


export type TextSegment =
  | {
      type: 'text'
      text: string
    }
  | {
      type: 'entity'
      id: string
      text: string
      label: EntityLabel
    }


export type DocumentPage = {
  pageNumber: number
  segments: TextSegment[]
}


export type ExtractedField = {
  id: string
  label: string
  value: string
  page: number
  status: 'EXTRACTED' | 'AMBIGUOUS' | 'NOT_FOUND'
}


export const ENTITY_LABELS: EntityLabel[] = [
  'ORGANIZZAZIONE',
  'IMPORTO',
  'DATA',
  'ORA',
  'RIFERIMENTO_NORMATIVO',
]


export const ENTITY_COLORS: Record<EntityLabel, string> = {
  ORGANIZZAZIONE: '#dcecff',
  IMPORTO: '#fff1b8',
  DATA: '#e8ddf8',
  ORA: '#f7d9ee',
  RIFERIMENTO_NORMATIVO: '#d9f0f0',
}


export const MOCK_DOCUMENT_PAGES: DocumentPage[] = [
  {
    pageNumber: 12,
    segments: [
      {
        type: 'text',
        text: 'La procedura è indetta da ',
      },
      {
        type: 'entity',
        id: 'entity-organization-1',
        text: 'Comune di Palermo',
        label: 'ORGANIZZAZIONE',
      },
      {
        type: 'text',
        text: '.\n\nL’importo complessivo della procedura è pari a ',
      },
      {
        type: 'entity',
        id: 'entity-amount-1',
        text: '€ 1.250.000,00',
        label: 'IMPORTO',
      },
      {
        type: 'text',
        text: ', mentre l’IVA prevista è pari a ',
      },
      {
        type: 'entity',
        id: 'entity-amount-2',
        text: '€ 275.000,00',
        label: 'IMPORTO',
      },
      {
        type: 'text',
        text: '.\n\nIl termine per la presentazione delle offerte è ',
      },
      {
        type: 'entity',
        id: 'entity-date-1',
        text: '31 marzo 2027',
        label: 'DATA',
      },
      {
        type: 'text',
        text: ' alle ore ',
      },
      {
        type: 'entity',
        id: 'entity-time-1',
        text: '12:00',
        label: 'ORA',
      },
      {
        type: 'text',
        text: '.',
      },
    ],
  },

  {
    pageNumber: 13,
    segments: [
      {
        type: 'text',
        text: 'La procedura è disciplinata dal ',
      },
      {
        type: 'entity',
        id: 'entity-law-1',
        text: 'D.Lgs. 36/2023',
        label: 'RIFERIMENTO_NORMATIVO',
      },
      {
        type: 'text',
        text: '.\n\nIl responsabile del procedimento opera per ',
      },
      {
        type: 'entity',
        id: 'entity-organization-2',
        text: 'Comune di Palermo',
        label: 'ORGANIZZAZIONE',
      },
      {
        type: 'text',
        text: '.',
      },
    ],
  },
]

export const MOCK_EXTRACTED_FIELDS: ExtractedField[] = [
  {
    id: 'field-contracting-authority',
    label: 'Stazione appaltante',
    value: 'Comune di Palermo',
    page: 12,
    status: 'EXTRACTED',
  },
  {
    id: 'field-total-amount',
    label: 'Importo complessivo',
    value: '€ 1.250.000,00',
    page: 12,
    status: 'EXTRACTED',
  },
  {
    id: 'field-deadline',
    label: 'Scadenza offerte',
    value: '31/03/2027 12:00',
    page: 12,
    status: 'EXTRACTED',
  },
]