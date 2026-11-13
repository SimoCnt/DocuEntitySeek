
import { Navigate, Outlet } from 'react-router'

import { useAuth } from '../../auth/AuthContext'
import ErrorState from '../feedback/ErrorState'
import LoadingState from '../feedback/LoadingState'

function GuestRoute() {
  const { status, error, refreshUser } = useAuth()

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
        <ErrorState message={error?.message ?? 'Impossibile verificare la sessione.'} onRetry={refreshUser} />
      </section>
    )
  }

  if (status === 'authenticated') {
    return <Navigate to="/documents" replace />
  }

  return <Outlet />
}

export default GuestRoute
