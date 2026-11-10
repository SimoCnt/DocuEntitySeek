export type DocumentCategory =
    | 'DISCIPLINARE'
    | 'CAPITOLATO'
    | 'CONTRATTO'
    | 'BANDO'
    | 'ALTRO'


export type UploadFormData = {
    file: File | null
    category: DocumentCategory
}