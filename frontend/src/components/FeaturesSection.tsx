import FeatureCard from './FeatureCard'


const features = [
  {
    id: 'entity-discovery',
    badge: 'NER',
    title: 'Entity Discovery',
    description: 'Individua automaticamente organizzazioni, persone, importi, date, riferimenti normativi e altre entità nel documento.',
  },
  {
    id: 'field-extraction',
    badge: 'IE',
    title: 'Field Extraction',
    description: 'Estrae informazioni strutturate come stazione appaltante, CIG, importi, scadenze e criteri di aggiudicazione.',
  },
  {
    id: 'annotated-document',
    badge: 'UI',
    title: 'Annotated Document',
    description: 'Visualizza le entità direttamente nel documento tramite etichette colorate e una sidebar di navigazione.'
  }
]

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