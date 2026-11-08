function Header() {
  return (
    <header className="app-header">
      <div className="app-header__brand">
        <span className="app-header__logo">DES</span>

        <div>
          <strong>DocuEntitySeek</strong>
          <span className="app-header__tagline">Document Intelligence</span>
        </div>
      </div>

      <nav className="app-header__nav" aria-label="Navigazione principale">
        <a href="#features">Funzionalità</a>
        <a href="#plans">Piani</a>
      </nav>
    </header>
  )
}

export default Header