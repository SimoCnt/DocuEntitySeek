
-- ============================================================
-- DOCUENTITYSEEK

-- Il database gestisce:
--   1. Piani di utilizzo dell'applicazione
--   2. Utenti
--   3. Schemi di estrazione
--   4. Versioni degli schemi
--   5. Definizioni delle entità NER
--   6. Definizioni dei campi da estrarre
--   7. Documenti caricati
--   8. Pagine dei documenti
--   9. Analisi dei documenti
--  10. Occorrenze delle entità riconosciute
--  11. Campi estratti
--  12. Valori candidati per i campi

-- ============================================================

BEGIN;


-- ============================================================
-- 1. TABELLA: plans
-- ============================================================

-- Memorizza i piani disponibili nell'applicazione.
--
-- Esempi:
--   BASE
--   PREMIUM
--
-- Ogni piano determina:
--   - quante analisi giornaliere sono consentite;
--   - se l'utente può creare schemi personalizzati.

CREATE TABLE plans (
    -- Codice univoco del piano. Esempio: 'BASE' oppure 'PREMIUM'.
    code VARCHAR(20) PRIMARY KEY,

    -- Nome descrittivo del piano.
    name VARCHAR(50) NOT NULL UNIQUE,

    -- Numero massimo di analisi giornaliere. NULL significa che non esiste un limite.
    daily_analysis_limit SMALLINT,

    -- Indica se il piano permette di creare schemi di estrazione personalizzati.
    custom_schemas_enabled BOOLEAN NOT NULL DEFAULT FALSE,

    -- Data e ora di creazione del piano.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Sono ammessi soltanto i piani BASE e PREMIUM.
    CONSTRAINT ck_plans_code
        CHECK (code IN ('BASE', 'PREMIUM')),

    -- Il limite deve essere positivo oppure NULL.
    CONSTRAINT ck_plans_daily_limit
        CHECK (
            daily_analysis_limit IS NULL
            OR daily_analysis_limit > 0
        )
);


-- ============================================================
-- 2. TABELLA: users
-- ============================================================

-- Memorizza gli utenti dell'applicazione.
--
-- Ogni utente:
--   - possiede un identificatore UUID;
--   - è identificato da un indirizzo email;
--   - ha un ruolo USER oppure ADMIN;
--   - appartiene a un piano BASE o PREMIUM.

CREATE TABLE users (
    -- Identificatore univoco dell'utente.
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Indirizzo email dell'utente.
    email VARCHAR(320) NOT NULL,

    -- Password hash dell'utente
    password_hash TEXT,

    -- Ruolo applicativo.
    role VARCHAR(20) NOT NULL DEFAULT 'USER',

    -- Piano associato all'utente.
    plan_code VARCHAR(20) NOT NULL DEFAULT 'BASE',

    -- Data di creazione dell'utente.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Data dell'ultimo aggiornamento. Gli aggiornamenti successivi saranno gestiti dall'applicazione oppure da un trigger dedicato.
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Utente attivo / non attivo
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Ultimo logino
    last_login_at TIMESTAMPTZ,

    -- Sono ammessi soltanto due ruoli.
    CONSTRAINT ck_users_role
        CHECK (role IN ('USER', 'ADMIN')),

    -- Relazione tra utente e piano.
    CONSTRAINT fk_users_plan
        FOREIGN KEY (plan_code)
        REFERENCES plans(code)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,    
    
    CONSTRAINT ck_users_active_password
        CHECK (
            is_active = FALSE
            OR password_hash IS NOT NULL
        )
);


-- ============================================================
-- 3. TABELLA: extraction_schemas
-- ============================================================

-- Memorizza gli schemi utilizzati per l'estrazione delle informazioni dai documenti.
--
-- Uno schema definisce quali entità e quali campi devono essere riconosciuti.
-- Esempio:
--   Nome: "Analisi disciplinare di gara"
--   Dominio: "Appalti pubblici"
--
-- Esistono due tipologie:
--
-- 1. BUILTIN
--    Schemi predefiniti dell'applicazione. Non appartengono a un singolo utente.
--
-- 2. PERSONALIZZATI
--    Schemi creati da un utente specifico.

CREATE TABLE extraction_schemas (
    -- Identificatore univoco dello schema.
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Utente proprietario dello schema.
    -- NULL per gli schemi predefiniti.
    -- UUID dell'utente per gli schemi personalizzati.
    owner_user_id UUID,

    -- Nome dello schema.
    name VARCHAR(120) NOT NULL,

    -- Dominio applicativo. Esempio: "Appalti pubblici".
    domain VARCHAR(120) NOT NULL,

    -- TRUE: schema predefinito.
    -- FALSE: schema creato da un utente.
    is_builtin BOOLEAN NOT NULL DEFAULT FALSE,

    -- Data di creazione.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Relazione con il proprietario.
    -- Se un utente viene eliminato, vengono eliminati anche gli schemi personalizzati che possiede.
    CONSTRAINT fk_extraction_schemas_owner
        FOREIGN KEY (owner_user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    -- Verifica la coerenza della proprietà.
    -- Uno schema builtin non deve avere proprietario.
    -- Uno schema personalizzato deve averne uno.
    CONSTRAINT ck_schema_ownership
        CHECK (
            (is_builtin = TRUE AND owner_user_id IS NULL)
            OR
            (is_builtin = FALSE AND owner_user_id IS NOT NULL)
        )
);


-- ============================================================
-- 4. TABELLA: extraction_schema_versions
-- ============================================================

-- Ogni schema può avere diverse versioni.
--
-- Esempio:
-- Schema: "Analisi disciplinare"
--   Versione 1
--   Versione 2
--   Versione 3
--
-- La gestione delle versioni permette di modificare nel tempo entità e campi senza perdere la storia.
-- Una sola versione per schema può essere attiva. Questa regola sarà garantita con un indice univoco.

CREATE TABLE extraction_schema_versions (
    -- Identificatore univoco della versione.
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Schema a cui appartiene la versione.
    schema_id UUID NOT NULL,

    -- Numero progressivo della versione.
    version INTEGER NOT NULL,

    -- Indica se questa versione è attiva.
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Data di creazione della versione.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Relazione con lo schema padre.
    -- Eliminando lo schema vengono eliminate anche le sue versioni, salvo relazioni che impediscono l'eliminazione.
    CONSTRAINT fk_schema_versions_schema
        FOREIGN KEY (schema_id)
        REFERENCES extraction_schemas(id)
        ON DELETE CASCADE,

    -- Il numero di versione deve essere positivo.
    CONSTRAINT ck_schema_version_positive
        CHECK (version > 0),

    -- Uno stesso schema non può contenere due versioni con il medesimo numero.
    CONSTRAINT uq_schema_version
        UNIQUE (schema_id, version)
);


-- ============================================================
-- 5. TABELLA: entity_definitions
-- ============================================================

-- Definisce le tipologie di entità che il modello NER deve riconoscere.
--
-- Esempi:
--   ORGANIZZAZIONE
--   IMPORTO
--   DATA
--   CODICE_CIG
--   CODICE_CUP
--
-- Ogni definizione appartiene a una specifica versione dello schema di estrazione.

CREATE TABLE entity_definitions (
    -- Identificatore della definizione.
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Versione dello schema di appartenenza.
    schema_version_id UUID NOT NULL,

    -- Etichetta dell'entità. Esempio: "ORGANIZZAZIONE".
    label VARCHAR(100) NOT NULL,

    -- Descrizione del significato dell'entità.
    description TEXT NOT NULL,

    -- Colore utilizzato per evidenziare l'entità nell'interfaccia React.
    -- Formato esadecimale: #RRGGBB
    color VARCHAR(7) NOT NULL,

    -- Ordine di visualizzazione.
    sort_order SMALLINT NOT NULL DEFAULT 0,

    -- Relazione con la versione dello schema.
    CONSTRAINT fk_entity_definition_version
        FOREIGN KEY (schema_version_id)
        REFERENCES extraction_schema_versions(id)
        ON DELETE CASCADE,

    -- Una stessa etichetta non può essere definita due volte nella medesima versione.
    CONSTRAINT uq_entity_definition_label
        UNIQUE (schema_version_id, label),

    -- Il colore deve rispettare il formato #RRGGBB.
    CONSTRAINT ck_entity_color
        CHECK (color ~ '^#[0-9A-Fa-f]{6}$')
);


-- ============================================================
-- 6. TABELLA: field_definitions
-- ============================================================

-- Definisce i campi che il sistema deve estrarre da un documento mediante Information Extraction.
--
-- Esempio:
-- field_key: "importo_base_asta"
-- label: "Importo a base d'asta"
-- data_type: "number"
--
-- Il campo field_key viene utilizzato come identificatore tecnico stabile nel backend e nelle API.

CREATE TABLE field_definitions (
    -- Identificatore della definizione.
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Versione dello schema di appartenenza.
    schema_version_id UUID NOT NULL,

    -- Identificatore tecnico del campo.
    -- Esempio:
    -- "stazione_appaltante"
    -- "importo_base_asta"
    field_key VARCHAR(100) NOT NULL,

    -- Nome leggibile mostrato nell'interfaccia.
    label VARCHAR(150) NOT NULL,

    -- Descrizione del contenuto da estrarre.
    description TEXT NOT NULL,

    -- Tipo del dato atteso.
    data_type VARCHAR(30) NOT NULL DEFAULT 'string',

    -- TRUE se il campo è obbligatorio nello schema.
    is_required BOOLEAN NOT NULL DEFAULT FALSE,

    -- Ordine di visualizzazione.
    sort_order SMALLINT NOT NULL DEFAULT 0,

    -- Relazione con la versione dello schema.
    CONSTRAINT fk_field_definition_version
        FOREIGN KEY (schema_version_id)
        REFERENCES extraction_schema_versions(id)
        ON DELETE CASCADE,

    -- Non sono ammessi due campi con la stessa chiave all'interno della medesima versione.
    CONSTRAINT uq_field_definition_key
        UNIQUE (schema_version_id, field_key),

    -- field_key può contenere:
    --   - lettere minuscole;
    --   - numeri;
    --   - underscore.
    -- Deve iniziare con una lettera minuscola.
    CONSTRAINT ck_field_key
        CHECK (field_key ~ '^[a-z][a-z0-9_]*$'),

    -- Tipologie di dato supportate.
    CONSTRAINT ck_field_data_type
        CHECK (
            data_type IN (
                'string',
                'integer',
                'number',
                'boolean',
                'date',
                'datetime'
            )
        )
);


-- ============================================================
-- 7. TABELLA: documents
-- ============================================================

-- Memorizza i metadati dei documenti caricati dagli utenti.
-- Esempi:
--   disciplinare.pdf
--   capitolato.pdf
--   contratto.pdf
--
-- Il PDF non viene memorizzato direttamente nel database.
-- La colonna storage_key contiene il riferimento al file presente nel sistema di archiviazione.
--
-- PostgreSQL conserva invece:
--   - il proprietario;
--   - il nome originale;
--   - la categoria;
--   - lo stato di elaborazione;
--   - i metadati;
--   - eventuali messaggi di errore.

CREATE TABLE documents (
    -- Identificatore univoco del documento.
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Utente proprietario del documento.
    owner_user_id UUID NOT NULL,

    -- Nome originale del file.
    original_name VARCHAR(255) NOT NULL,

    -- Categoria documentale.
    category VARCHAR(30) NOT NULL,

    -- Stato dell'elaborazione.
    status VARCHAR(30) NOT NULL DEFAULT 'PROCESSING',

    -- Tipo MIME del documento. Esempio: application/pdf.
    mime_type VARCHAR(100),

    -- Dimensione del file in byte.
    size_bytes BIGINT,

    -- Riferimento al file nell'archiviazione.
    storage_key TEXT,

    -- Numero delle pagine del documento.
    page_count INTEGER,

    -- Messaggio associato a un eventuale errore.
    error_message TEXT,

    -- Data di creazione del record.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Data dell'ultimo aggiornamento.
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Relazione con l'utente proprietario.
    -- Eliminando un utente vengono eliminati anche i record dei suoi documenti.
    CONSTRAINT fk_documents_owner
        FOREIGN KEY (owner_user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    -- Categorie documentali consentite.
    CONSTRAINT ck_document_category
        CHECK (
            category IN (
                'DISCIPLINARE',
                'CAPITOLATO',
                'CONTRATTO',
                'BANDO',
                'ALTRO'
            )
        ),

    -- Stati consentiti.
    CONSTRAINT ck_document_status
        CHECK (
            status IN (
                'PROCESSING',
                'READY',
                'ERROR'
            )
        ),

    -- La dimensione del file non può essere negativa.
    CONSTRAINT ck_document_size
        CHECK (
            size_bytes IS NULL
            OR size_bytes >= 0
        ),

    -- Il numero delle pagine non può essere negativo.
    CONSTRAINT ck_document_pages
        CHECK (
            page_count IS NULL
            OR page_count >= 0
        )
);


-- ============================================================
-- 8. TABELLA: document_pages
-- ============================================================

-- Memorizza il testo estratto dalle singole pagine.
-- Esempio:
-- Documento A
--   Pagina 1 -> testo della prima pagina
--   Pagina 2 -> testo della seconda pagina
--   Pagina 3 -> testo della terza pagina
--
-- global_start e global_end individuano l'intervallo occupato dalla pagina nel testo completo del documento.
-- Questa informazione è fondamentale per associare entità e valori estratti alla loro posizione originale.

CREATE TABLE document_pages (
    -- Identificatore univoco della pagina.
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Documento di appartenenza.
    document_id UUID NOT NULL,

    -- Numero della pagina. La numerazione parte da 1.
    page_number INTEGER NOT NULL,

    -- Testo ottenuto dall'estrazione della pagina.
    extracted_text TEXT NOT NULL,

    -- Posizione iniziale della pagina nel testo globale.
    global_start INTEGER NOT NULL,

    -- Posizione finale della pagina nel testo globale.
    global_end INTEGER NOT NULL,

    -- Relazione con il documento.
    CONSTRAINT fk_document_pages_document
        FOREIGN KEY (document_id)
        REFERENCES documents(id)
        ON DELETE CASCADE,

    -- Uno stesso documento può avere una sola pagina per ciascun numero.
    CONSTRAINT uq_document_page
        UNIQUE (document_id, page_number),

    -- Il numero di pagina deve essere almeno 1.
    CONSTRAINT ck_document_page_number
        CHECK (page_number >= 1),

    -- Controllo dell'intervallo globale.
    CONSTRAINT ck_document_page_global_span
        CHECK (
            global_start >= 0
            AND global_end >= global_start
        )
);


-- ============================================================
-- 9. TABELLA: analyses
-- ============================================================

-- Memorizza le esecuzioni delle analisi AI.
-- Un documento può essere analizzato più volte.
-- Ogni analisi:
--   - riguarda un documento;
--   - utilizza una specifica versione di schema;
--   - possiede una configurazione JSON;
--   - attraversa diversi stati di elaborazione.
-- Esempio:
-- Documento A
--   Analisi 1 -> schema versione 1
--   Analisi 2 -> schema versione 2

CREATE TABLE analyses (
    -- Identificatore univoco dell'analisi.
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Documento analizzato.
    document_id UUID NOT NULL,

    -- Versione dello schema utilizzata.
    schema_version_id UUID NOT NULL,

    -- Stato dell'analisi.
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING',

    -- Configurazione dell'analisi in formato JSON.
    -- Esempio:
    -- {"model": "ner_model", "threshold": 0.7}
    config JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Messaggio relativo a un eventuale errore.
    error_message TEXT,

    -- Data di creazione della richiesta.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Istante di avvio dell'elaborazione.
    started_at TIMESTAMPTZ,

    -- Istante di completamento.
    completed_at TIMESTAMPTZ,

    -- Relazione con il documento analizzato.
    CONSTRAINT fk_analyses_document
        FOREIGN KEY (document_id)
        REFERENCES documents(id)
        ON DELETE CASCADE,

    -- Relazione con la versione dello schema.
    -- RESTRICT impedisce di eliminare una versione che risulta utilizzata da un'analisi.
    CONSTRAINT fk_analyses_schema_version
        FOREIGN KEY (schema_version_id)
        REFERENCES extraction_schema_versions(id)
        ON DELETE RESTRICT,

    -- Stati dell'analisi consentiti.
    CONSTRAINT ck_analysis_status
        CHECK (
            status IN (
                'PENDING',
                'PROCESSING',
                'COMPLETED',
                'ERROR'
            )
        ),

    -- L'analisi non può terminare prima di iniziare.
    CONSTRAINT ck_analysis_times
        CHECK (
            completed_at IS NULL
            OR started_at IS NULL
            OR completed_at >= started_at
        )
);


-- ============================================================
-- 10. TABELLA: entity_occurrences
-- ============================================================

-- Memorizza le singole occorrenze delle entità riconosciute dal modello NER.
-- Esempio:
-- Testo:
-- "La gara è indetta dal Comune di Palermo."
-- Entità riconosciuta:
--   label: ORGANIZZAZIONE
--   text: Comune di Palermo
--   confidence: 0.9500
--
-- Oltre al testo vengono salvate le coordinate necessarie per evidenziarlo nell'interfaccia.
-- Le coordinate sono offset testuali, non coordinate geometriche della pagina PDF.

CREATE TABLE entity_occurrences (
    -- Identificatore univoco dell'occorrenza.
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Analisi che ha prodotto l'entità.
    analysis_id UUID NOT NULL,

    -- Etichetta NER assegnata.
    label VARCHAR(100) NOT NULL,

    -- Testo riconosciuto come entità.
    text TEXT NOT NULL,

    -- Confidenza del modello, compresa tra 0 e 1.
    confidence NUMERIC(5,4),

    -- Posizione iniziale nel testo globale.
    global_start INTEGER NOT NULL,

    -- Posizione finale nel testo globale.
    global_end INTEGER NOT NULL,

    -- Numero della pagina che contiene l'entità.
    page INTEGER NOT NULL,

    -- Offset iniziale relativo alla pagina.
    page_start INTEGER NOT NULL,

    -- Offset finale relativo alla pagina.
    page_end INTEGER NOT NULL,

    -- Indica se l'entità deve essere visibile nell'interfaccia utente.
    is_visible BOOLEAN NOT NULL DEFAULT TRUE,

    -- Relazione con l'analisi.
    CONSTRAINT fk_entity_occurrence_analysis
        FOREIGN KEY (analysis_id)
        REFERENCES analyses(id)
        ON DELETE CASCADE,

    -- La confidenza deve essere compresa tra 0 e 1.
    CONSTRAINT ck_entity_confidence
        CHECK (
            confidence IS NULL
            OR (confidence >= 0 AND confidence <= 1)
        ),

    -- L'intervallo globale deve essere valido.
    CONSTRAINT ck_entity_global_span
        CHECK (
            global_start >= 0
            AND global_end > global_start
        ),

    -- La pagina deve avere numero positivo.
    CONSTRAINT ck_entity_page
        CHECK (page >= 1),

    -- L'intervallo relativo alla pagina deve essere valido.
    CONSTRAINT ck_entity_page_span
        CHECK (
            page_start >= 0
            AND page_end > page_start
        )
);


-- ============================================================
-- 11. TABELLA: extracted_fields
-- ============================================================

-- Memorizza i risultati dell'Information Extraction.
-- A differenza della NER, che individua occorrenze testuali, l'Information Extraction cerca di assegnare valori a campi specifici.
-- Esempio:
-- field_key: "importo_base_asta"
-- value_text: "250000.00"
-- status: "EXTRACTED"
--
-- Possibili stati:
-- EXTRACTED
--   È stato identificato un valore.
-- AMBIGUOUS
--   Esistono più valori plausibili.
-- NOT_FOUND
--   Non è stato individuato un valore affidabile.
-- ERROR
--   Si è verificato un errore durante l'estrazione.

CREATE TABLE extracted_fields (
    -- Identificatore univoco del campo estratto.
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Analisi di appartenenza.
    analysis_id UUID NOT NULL,

    -- Identificatore tecnico del campo.
    field_key VARCHAR(100) NOT NULL,

    -- Valore testuale estratto. Può essere NULL se non è stato trovato.
    value_text TEXT,

    -- Stato dell'estrazione.
    status VARCHAR(30) NOT NULL,

    -- Confidenza del valore estratto.
    confidence NUMERIC(5,4),

    -- Numero della pagina associata al valore.
    page INTEGER,

    -- Offset iniziale globale.
    global_start INTEGER,

    -- Offset finale globale.
    global_end INTEGER,

    -- Relazione con l'analisi.
    CONSTRAINT fk_extracted_field_analysis
        FOREIGN KEY (analysis_id)
        REFERENCES analyses(id)
        ON DELETE CASCADE,

    -- Per ogni analisi deve esistere al massimo un risultato per ciascun field_key.
    CONSTRAINT uq_extracted_field
        UNIQUE (analysis_id, field_key),

    -- Stati ammessi.
    CONSTRAINT ck_extracted_field_status
        CHECK (
            status IN (
                'EXTRACTED',
                'AMBIGUOUS',
                'NOT_FOUND',
                'ERROR'
            )
        ),

    -- Validazione della confidenza.
    CONSTRAINT ck_extracted_field_confidence
        CHECK (
            confidence IS NULL
            OR (confidence >= 0 AND confidence <= 1)
        ),

    -- Validazione del numero di pagina.
    CONSTRAINT ck_extracted_field_page
        CHECK (
            page IS NULL
            OR page >= 1
        ),

    -- I due offset devono essere:
    --   - entrambi NULL;
    --   - oppure entrambi valorizzati e validi.
    CONSTRAINT ck_extracted_field_span
        CHECK (
            (
                global_start IS NULL
                AND global_end IS NULL
            )
            OR
            (
                global_start IS NOT NULL
                AND global_end IS NOT NULL
                AND global_start >= 0
                AND global_end > global_start
            )
        )
);


-- ============================================================
-- 12. TABELLA: field_candidates
-- ============================================================

-- Memorizza i possibili valori alternativi identificati per un campo estratto.
-- Questa tabella è importante quando un documento contiene più valori potenzialmente corretti.
-- Esempio:
-- Campo: importo_base_asta
-- Candidato 1:
--   value_text: "250.000 euro"
--   candidate_rank: 1
-- Candidato 2:
--   value_text: "270.000 euro"
--   candidate_rank: 2
--
-- Il backend può utilizzare queste informazioni per consentire una revisione manuale o per selezionare il valore più affidabile.

CREATE TABLE field_candidates (
    -- Identificatore univoco del candidato.
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Campo estratto al quale il candidato appartiene.
    extracted_field_id UUID NOT NULL,

    -- Valore testuale candidato.
    value_text TEXT NOT NULL,

    -- Confidenza assegnata al candidato.
    confidence NUMERIC(5,4),

    -- Pagina che contiene il candidato.
    page INTEGER,

    -- Offset iniziale nel testo globale.
    global_start INTEGER,

    -- Offset finale nel testo globale.
    global_end INTEGER,

    -- Posizione del candidato nella graduatoria.
    -- 1 = primo candidato
    -- 2 = secondo candidato
    -- 3 = terzo candidato
    candidate_rank SMALLINT NOT NULL,

    -- Relazione con il campo estratto.
    CONSTRAINT fk_field_candidate_field
        FOREIGN KEY (extracted_field_id)
        REFERENCES extracted_fields(id)
        ON DELETE CASCADE,

    -- Due candidati dello stesso campo non possono occupare la stessa posizione in graduatoria.
    CONSTRAINT uq_field_candidate_rank
        UNIQUE (extracted_field_id, candidate_rank),

    -- La posizione deve essere positiva.
    CONSTRAINT ck_candidate_rank
        CHECK (candidate_rank >= 1),

    -- La confidenza deve essere compresa tra 0 e 1.
    CONSTRAINT ck_candidate_confidence
        CHECK (
            confidence IS NULL
            OR (confidence >= 0 AND confidence <= 1)
        )
);


-- ============================================================
-- 13. INDICI UNIVOCI AGGIUNTIVI
-- ============================================================

-- Gli indici UNIQUE impediscono la presenza di valori duplicati.
-- Alcuni vincoli non possono essere espressi comodamente mediante un semplice UNIQUE sulle colonne originali.


-- ------------------------------------------------------------
-- 13.1 Email univoca senza distinzione maiuscole/minuscole
-- ------------------------------------------------------------

-- Impedisce di registrare contemporaneamente:
-- mario@example.com
-- MARIO@example.com
-- LOWER(email) normalizza il confronto.

CREATE UNIQUE INDEX uq_users_email_ci
    ON users (LOWER(email));


-- ------------------------------------------------------------
-- 13.2 Nomi univoci degli schemi predefiniti
-- ------------------------------------------------------------

-- Due schemi builtin non possono avere lo stesso nome, ignorando le differenze tra maiuscole e minuscole.
-- L'indice riguarda soltanto gli schemi senza proprietario.

CREATE UNIQUE INDEX uq_builtin_schema_name
    ON extraction_schemas (LOWER(name))
    WHERE owner_user_id IS NULL;


-- ------------------------------------------------------------
-- 13.3 Nomi univoci degli schemi personalizzati
-- ------------------------------------------------------------

-- Uno stesso utente non può creare due schemi con il medesimo nome.
-- Utenti differenti possono invece utilizzare lo stesso nome per i propri schemi.

CREATE UNIQUE INDEX uq_user_schema_name
    ON extraction_schemas (
        owner_user_id,
        LOWER(name)
    )
    WHERE owner_user_id IS NOT NULL;


-- ------------------------------------------------------------
-- 13.4 Una sola versione attiva per schema
-- ------------------------------------------------------------

-- Ogni schema può avere più versioni, ma al massimo una può risultare attiva.
-- L'indice prende in considerazione soltanto le versioni con is_active = TRUE.

CREATE UNIQUE INDEX uq_active_schema_version
    ON extraction_schema_versions (schema_id)
    WHERE is_active = TRUE;


-- ============================================================
-- 14. INDICI PER OTTIMIZZARE LE INTERROGAZIONI
-- ============================================================

-- Gli indici seguenti migliorano le prestazioni delle ricerche effettuate dal backend FastAPI.
-- Non modificano i dati e non introducono nuove relazioni tra le tabelle.


-- ------------------------------------------------------------
-- 14.1 Documenti di un utente ordinati per data
-- ------------------------------------------------------------

-- Utile per mostrare nella dashboard i documenti di un utente, dai più recenti ai più vecchi.

CREATE INDEX idx_documents_owner_created
    ON documents (owner_user_id, created_at DESC);


-- ------------------------------------------------------------
-- 14.2 Ricerca dei documenti per stato
-- ------------------------------------------------------------

-- Utile per individuare rapidamente i documenti:
-- PROCESSING, READY oppure ERROR.

CREATE INDEX idx_documents_status
    ON documents (status);


-- ------------------------------------------------------------
-- 14.3 Analisi di un documento ordinate per data
-- ------------------------------------------------------------

-- Utile per recuperare la cronologia delle analisi eseguite su uno specifico documento.

CREATE INDEX idx_analyses_document_created
    ON analyses (document_id, created_at DESC);


-- ------------------------------------------------------------
-- 14.4 Ricerca delle analisi per stato
-- ------------------------------------------------------------

-- Utile per individuare analisi in attesa, in elaborazione, completate oppure in errore.

CREATE INDEX idx_analyses_status
    ON analyses (status);


-- ------------------------------------------------------------
-- 14.5 Occorrenze NER di una determinata analisi
-- ------------------------------------------------------------

-- Consente di recuperare rapidamente le entità di un'analisi ordinate per pagina e posizione.

CREATE INDEX idx_entity_occurrences_analysis_page
    ON entity_occurrences (
        analysis_id,
        page,
        global_start
    );


-- ------------------------------------------------------------
-- 14.6 Campi estratti da una determinata analisi
-- ------------------------------------------------------------

-- Migliora il recupero dei risultati strutturati prodotti da un'analisi.

CREATE INDEX idx_extracted_fields_analysis
    ON extracted_fields (analysis_id);


-- ------------------------------------------------------------
-- 14.7 Candidati di un campo estratto
-- ------------------------------------------------------------

-- Migliora il recupero dei candidati di un campo, ordinati secondo la loro posizione in graduatoria.

CREATE INDEX idx_field_candidates_field
    ON field_candidates (
        extracted_field_id,
        candidate_rank
    );


-- ============================================================
-- 15. CONCLUSIONE DELLA TRANSAZIONE
-- ============================================================

-- COMMIT conferma definitivamente tutte le operazioni eseguite nella transazione.
-- Se tutte le istruzioni sono corrette, PostgreSQL rende disponibili le tabelle e gli indici creati.
COMMIT;

