/**
 * Render the landing page's primary message and call to action.
 */

import { Link } from 'react-router'


/**
 * Introduce the product and lead users to its core workflow.
 */
function HeroSection() {
  return (
    <section className="hero">
      <div className="hero__content">
        <span className="hero__eyebrow">Procurement Document Intelligence</span>
        <h1>Trasforma documenti complessi in informazioni strutturate.</h1>
        <p className="hero__description">DocuEntitySeek è una piattaforma intelligente di analisi documentale progettata per identificare entità ed estrarre informazioni strutturate attraverso schemi semantici personalizzabili, indipendentemente dalla lingua e dal dominio applicativo, preservando la tracciabilità delle informazioni estratte e favorendo la riservatezza ed il controllo senza la necessità di trasmettere dati sensibili ad API o servizi di intelligenza artificiale esterni.</p>

        <div className="hero__actions">
          <Link
            to="/documents"
            className="button button--primary"
          >
            Esplora i documenti
          </Link>

          <a
            href="#features"
            className="button button--secondary"
          >
            Scopri le funzionalità
          </a>
        </div>
      </div>
    </section>
  )
}

export default HeroSection
