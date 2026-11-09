import useDocumentTitle from '../hooks/useDocumentTitle'

const procurementEntities = [
    'ORGANIZZAZIONE',
    'PERSONA',
    'LOCALITA',
    'IMPORTO',
    'DATA',
    'ORA',
    'RIFERIMENTO_NORMATIVO',
    'IDENTIFICATIVO_GARA',
    'CERTIFICAZIONE',
    'PRODOTTO_SERVIZIO',
]

const procurementFields = [
    'Stazione appaltante',
    'Oggetto gara',
    'CIG',
    'CUP',
    'CPV',
    'Tipo procedura',
    'Importo complessivo',
    'Importo base asta',
    'Durata contratto',
    'Scadenza offerte',
    'Termine chiarimenti',
    'Criterio aggiudicazione',
    'Responsabile procedimento',
    'Luogo esecuzione',
]


function SchemasPage() {
    useDocumentTitle('Schemi | DocuEntitySeek')

    return (
        <section className="page-section">
            <div className="page-heading">
                <span className="section-heading__eyebrow">Extraction schemas</span>
                <h1>Schemi di estrazione</h1>
                <p>Lo schema definisce quali entità e quali informazioni strutturate DocuEntitySeek deve cercare nei documenti.</p>
            </div>

            <div className="schema-grid">
                <article className="schema-card">
                    <div className="schema-card__header">
                        <div>
                            <span className="schema-card__badge">BASE</span>
                            <h2>Procurement</h2>
                        </div>

                        <span>Predefinito</span>
                    </div>

                    <div className="schema-card__section">
                        <h3>Entità</h3>

                        <div className="schema-tags">
                            {procurementEntities.map((entity) => (
                                <span key={entity}>{entity}</span>
                            ))}
                        </div>
                    </div>

                    <div className="schema-card__section">
                        <h3>Campi strutturati</h3>

                        <ul>
                            {procurementFields.map((field) => (
                                <li key={field}>{field}</li>
                            ))}
                        </ul>
                    </div>
                </article>

                <article className="schema-card schema-card--premium">
                    <div className="schema-card__header">
                        <div>
                            <span className="schema-card__badge">PREMIUM</span>
                            <h2>Schema personalizzato</h2>
                        </div>
                    </div>

                    <p>Gli utenti Premium potranno creare entità e campi personalizzati e salvare configurazioni riutilizzabili.</p>

                    <button
                        type="button"
                        className="button button--secondary"
                        disabled
                    >
                        Editor disponibile prossimamente
                    </button>
                </article>
            </div>
        </section>
    )
}

export default SchemasPage