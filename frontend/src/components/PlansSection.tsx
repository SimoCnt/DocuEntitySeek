import PlanCard from './PlanCard'


const baseFeatures = [
  'Schema Procurement predefinito',
  'Entity Discovery',
  'Field Extraction',
  'Viewer con annotazioni NER',
  '5 nuove analisi al giorno',
]

const premiumFeatures = [
  'Tutte le funzionalità Base',
  'Entità personalizzate',
  'Campi personalizzati',
  'Schemi di estrazione salvabili',
  'Utilizzo su domini personalizzati',
  'Analisi senza limite giornaliero applicativo',
]


function PlansSection() {
  return (
    <section id="plans" className="plans-section">
      <div className="section-heading">
        <span className="section-heading__eyebrow">Plans</span>
        <h2>Un piano per ogni livello di analisi</h2>
      </div>

      <div className="plans-grid">
        <PlanCard
          name="Base"
          description="Per analizzare documenti Procurement utilizzando lo schema predefinito di DocuEntitySeek."
          features={baseFeatures}
        />

        <PlanCard
          name="Premium"
          description="Per creare schemi personalizzati e adattare DocuEntitySeek a nuovi domini."
          features={premiumFeatures}
          highlighted
        />
      </div>
    </section>
  )
}

export default PlansSection