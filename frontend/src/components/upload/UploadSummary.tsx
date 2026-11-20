

type UploadSummaryProps = {
    file: File
    schemaName: string
}


function formatFileSize(bytes: number) {
    if (bytes < 1024) return `${bytes} B`

    const kilobytes = bytes / 1024

    if (kilobytes < 1024) return `${kilobytes.toFixed(1)} KB`

    const megabytes = kilobytes / 1024

    return `${megabytes.toFixed(1)} MB`
}


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