type ErrorStateProps = {
    title?: string
    message: string
    onRetry?: () => void
}


function ErrorState({ title = 'Qualcosa è andato storto', message, onRetry }: ErrorStateProps) {
    return (
        <div
            className="request-state request-state--error"
            role="alert"
        >
            <span className="request-state__label">Errore</span>
            <h2>{title}</h2>
            <p>{message}</p>

            {onRetry && (
                <button
                    type="button"
                    className="button button--secondary"
                    onClick={onRetry}
                >
                    Riprova
                </button>
            )}
        </div>
    )
}

export default ErrorState