/**
 * Validate selected PDF type and size before network submission.
 */

const MAX_PDF_SIZE_BYTES = 25 * 1024 * 1024


/**
 * Reject unsupported PDF selection by type or file size.
 */
export function validatePdfFile(file: File | null): string | null {
    if (!file) {
        return 'Seleziona un documento PDF.'
    }

    const hasPdfExtension = file.name.toLowerCase().endsWith('.pdf')
    const hasCompatibleMimeType =
        file.type === 'application/pdf' ||
        file.type === ''

    if (!hasPdfExtension || !hasCompatibleMimeType) {
        return 'Il file selezionato deve essere un PDF.'
    }

    if (file.size > MAX_PDF_SIZE_BYTES) {
        return 'Il PDF non può superare 25 MB.'
    }

    return null
}
