import type { DocumentCategory } from "./document"


export type { DocumentCategory } from "./document"


export type UploadFormData = {
    file: File | null
    category: DocumentCategory
}