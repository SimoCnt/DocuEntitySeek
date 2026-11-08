function HeroSection() {
  return (
    <section className="hero">
      <div className="hero__content">
        <span className="hero__eyebrow">Procurement Document Intelligence</span>
        <h1>Trasforma documenti complessi in informazioni strutturate.</h1>
        <p className="hero__description">DocuEntitySeek identifica entità e informazioni rilevanti all'interno di bandi, disciplinari, capitolati e contratti, mantenendo sempre il collegamento con il documento originale.</p>

        <div className="hero__actions">
          <button type="button" className="button button--primary">
            Analizza documento
          </button>

          <button type="button" className="button button--secondary">
            Scopri le funzionalità
          </button>
        </div>
      </div>
    </section>
  )
}

export default HeroSection