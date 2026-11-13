
import { Link, NavLink, useNavigate } from 'react-router'

import { useAuth } from '../auth/AuthContext'


const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  isActive ? 'app-header__link app-header__link--active' : 'app-header__link'


function Header() {
  const { user, status, logout, refreshUser } = useAuth()
  const navigate = useNavigate()


  function handleLogout() {
    logout()
    navigate('/', { replace: true })
  }

  
  return (
    <header className="app-header">
      <NavLink to="/" className="app-header__brand">
        <span className="app-header__logo">DES</span>
        <div>
          <strong>DocuEntitySeek</strong>
          <span className="app-header__tagline">Document Intelligence</span>
        </div>
      </NavLink>

      <nav className="app-header__nav" aria-label="Navigazione principale">
        <NavLink to="/" end className={navLinkClass}>Home</NavLink>
        {status === 'authenticated' && (
          <>
            <NavLink to="/documents" className={navLinkClass}>Documenti</NavLink>
            <NavLink to="/schemas" className={navLinkClass}>Schemi</NavLink>
          </>
        )}
      </nav>

      <div className="app-header__actions">
        {status === 'authenticated' && (
          <>
            <span className="app-header__user" title={user?.email}>{user?.email}</span>
            <button type="button" className="button button--secondary" onClick={handleLogout}>
              Esci
            </button>
          </>
        )}

        {status === 'anonymous' && (
          <>
            <Link to="/login" className="button button--secondary">Accedi</Link>
            <Link to="/register" className="button button--primary">Registrati</Link>
          </>
        )}

        {status === 'checking' && (
          <span className="app-header__user" role="status">Verifica sessione...</span>
        )}

        {status === 'error' && (
          <button type="button" className="button button--secondary" onClick={() => void refreshUser()}>
            Riprova sessione
          </button>
        )}
      </div>
    </header>
  )
}

export default Header
