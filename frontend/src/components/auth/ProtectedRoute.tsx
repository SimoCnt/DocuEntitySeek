/**
 * Enforce login and optional subscription-based access for React routes.
 */

import { Navigate, Outlet, useLocation } from 'react-router'

import ErrorState from '../feedback/ErrorState'
import LoadingState from '../feedback/LoadingState'
import { useAuth } from '../../auth/AuthContext'


/**
 * Require authentication and enforce optional route-level plan restrictions.
 */
function ProtectedRoute() {
    const { status, error, refreshUser } = useAuth()
    const location = useLocation()

    if (status === 'checking') {
        return (
            <section className="page-section">
                <LoadingState message="Verifica della sessione..." />
            </section>
        )
    }

    if (status === 'error') {
        return (
            <section className="page-section">
                <ErrorState
                    message={error?.message ?? 'Impossibile verificare la sessione.'}
                    onRetry={refreshUser}
                />
            </section>
        )
    }

    if (status !== 'authenticated') {
        return <Navigate to="/login" replace state={{ from: location }} />
    }

    return <Outlet />
}

export default ProtectedRoute
