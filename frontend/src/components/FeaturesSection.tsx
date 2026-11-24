/**
 * Render the publicly visible DocuEntitySeek feature overview.
 */

import FeatureCard from './FeatureCard'


const features = [
  {
    id: 'entity-discovery',
    badge: 'NER',
    title: 'Entity Discovery',
    description: 'Riconosce automaticamente entità di interesse, come persone, organizzazioni, luoghi, date e importi, adattandosi a categorie semantiche personalizzabili e a diversi contesti linguistici e applicativi.',
  },
  {
    id: 'field-extraction',
    badge: 'IE',
    title: 'Field Extraction',
    description: 'Estrae informazioni complesse e contestualizzate, andando oltre il riconoscimento delle singole entità per individuare e strutturare contenuti di interesse attraverso schemi semantici personalizzabili.',
  },
  {
    id: 'annotated-document',
    badge: 'UI',
    title: 'Annotated Document',
    description: 'Visualizza le informazioni estratte direttamente nel documento tramite etichette colorate e una sidebar di navigazione.'
  }
]

/**
 * List the platform's user-facing capabilities.
 */
function FeaturesSection() {
  return (
    <section id="features" className="features-section">
      <div className="section-heading">
        <span className="section-heading__eyebrow">Core capabilities</span>
        <h2>Analisi documentale focalizzata e verificabile</h2>
        <p>DocuEntitySeek concentra l'analisi sulle informazioni realmente utili e mantiene sempre la provenienza dei risultati.</p>
      </div>

      <div className="features-grid">
        {features.map((feature) => (
          <FeatureCard
            key={feature.id}
            badge={feature.badge}
            title={feature.title}
            description={feature.description}
          />
        ))}
      </div>
    </section>
  )
}

export default FeaturesSection
