type LoadingStateProps = {
    message?: string
}


function LoadingState({ message = 'Caricamento in corso...' }: LoadingStateProps) {
    return (
        <div
            className="request-state"
            role="status"
        >
            <span
                className="request-spinner"
                aria-hidden="true"
            />
            <p>{message}</p>
        </div>
    )
}

export default LoadingState