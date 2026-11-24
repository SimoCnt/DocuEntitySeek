/**
 * Render a consistent loading indicator for pending operations.
 */

/**
 * Properties configuring the loading state component.
 */
type LoadingStateProps = {
    message?: string
}


/**
 * Display consistent feedback while asynchronous data is loading.
 */
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
