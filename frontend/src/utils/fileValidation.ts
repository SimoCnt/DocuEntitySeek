export function validatePdfFile(file: File | null): string | null {
    if (!file) {
        return 'Seleziona un documento PDF.'
    }

    const hasPdfExtension = file.name.toLowerCase().endsWith('.pdf')
    const hasCompatibleMimeType = file.type === 'application/pdf' || file.type === ''

    if (!hasPdfExtension || !hasCompatibleMimeType) {
        return 'Il file selezionato deve essere un PDF.'
    }

    return null
}