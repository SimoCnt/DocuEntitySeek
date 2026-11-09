import { Link } from 'react-router'


function HeroSection() {
  return (
    <section className="hero">
      <div className="hero__content">
        <span className="hero__eyebrow">Procurement Document Intelligence</span>
        <h1>Trasforma documenti complessi in informazioni strutturate.</h1>
        <p className="hero__description">DocuEntitySeek identifica entità e informazioni rilevanti all'interno di bandi, disciplinari, capitolati e contratti, mantenendo sempre il collegamento con il documento originale.</p>

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