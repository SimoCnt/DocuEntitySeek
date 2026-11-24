/**
 * Display selected PDF metadata and formatted size.
 */

/**
 * Properties configuring the upload summary component.
 */
type UploadSummaryProps = {
    file: File
    schemaName: string
}


/**
 * Format the size of a PDF for user-facing upload feedback.
 */
function formatFileSize(bytes: number) {
    if (bytes < 1024) return `${bytes} B`

    const kilobytes = bytes / 1024

    if (kilobytes < 1024) return `${kilobytes.toFixed(1)} KB`

    const megabytes = kilobytes / 1024

    return `${megabytes.toFixed(1)} MB`
}


/**
 * Summarize selected PDF filename, size, and content type.
 */
function UploadSummary({ file, schemaName }: UploadSummaryProps) {
    return (
        <dl className="upload-summary">
            <div>
                <dt>File</dt>
                <dd>{file.name}</dd>
            </div>

            <div>
                <dt>Dimensione</dt>
                <dd>{formatFileSize(file.size)}</dd>
            </div>

            <div>
                <dt>Schema</dt>
                <dd>{schemaName}</dd>
            </div>
        </dl>
    )
}

export default UploadSummary
