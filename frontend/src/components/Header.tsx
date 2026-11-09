import { NavLink } from 'react-router'


function Header() {
  return (
    <header className="app-header">
      <NavLink
        to="/"
        className="app-header__brand"
      >
        <span className="app-header__logo">DES</span>

        <div>
          <strong>DocuEntitySeek</strong>
          <span className="app-header__tagline">Document Intelligence</span>
        </div>
      </NavLink>

      <nav
        className="app-header__nav"
        aria-label="Navigazione principale"
      >
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            isActive
              ? 'app-header__link app-header__link--active'
              : 'app-header__link'
          }
        >
          Home
        </NavLink>

        <NavLink
          to="/documents"
          className={({ isActive }) =>
            isActive
              ? 'app-header__link app-header__link--active'
              : 'app-header__link'
          }
        >
          Documenti
        </NavLink>

        <NavLink
          to="/schemas"
          className={({ isActive }) =>
            isActive
              ? 'app-header__link app-header__link--active'
              : 'app-header__link'
          }
        >
          Schemi
        </NavLink>
      </nav>
    </header>
  )
}

export default Header