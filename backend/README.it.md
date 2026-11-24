# DocuEntitySeek — Backend

**FastAPI · PostgreSQL · SQLAlchemy · GLiNER2.5 · S3-Compatible Storage**

Backend Python di **DocuEntitySeek**, una piattaforma full-stack di Document Intelligence progettata per analizzare documenti PDF mediante Named Entity Recognition (NER) e Structured Information Extraction (IE).

Il backend espone API REST, gestisce autenticazione e autorizzazione, coordina la persistenza dei dati e dei documenti, applica le regole di business e integra una pipeline NLP basata su GLiNER2.5.

> **Finalità didattica**
>
> DocuEntitySeek è un progetto didattico e di portfolio professionale, orientato principalmente alla progettazione e allo sviluppo di applicazioni full-stack con funzionalità AI.
>
> Il modello GLiNER2.5 viene utilizzato nella sua versione preaddestrata, senza fine-tuning specifico. Il progetto non si propone di ottimizzarne o dimostrarne le prestazioni attraverso benchmark.
>
> L'obiettivo del backend è mostrare come integrare un modello NLP in un'architettura software modulare, con attenzione a API, servizi, persistenza, sicurezza applicativa, gestione documentale, tracciabilità e infrastruttura.

Per una panoramica dell'intera piattaforma, consultare il [README principale](../README.md).

---

## 1. Obiettivi e responsabilità

Il backend costituisce il livello applicativo centrale di DocuEntitySeek.

Le sue principali responsabilità sono:

- Esporre API REST mediante FastAPI.
- Validare richieste e dati tramite Pydantic.
- Gestire registrazione, autenticazione JWT e autorizzazione.
- Applicare ruoli, piani e quote giornaliere.
- Gestire documenti PDF e metadati.
- Archiviare i file originali tramite un livello di storage dedicato.
- Gestire schemi di estrazione predefiniti e personalizzati.
- Orchestrare la pipeline di elaborazione documentale.
- Integrare GLiNER2.5 per NER e Information Extraction.
- Persistire analisi, entità, campi estratti e relativi metadati.
- Rendere disponibili i risultati e le coordinate per il frontend.
- Gestire errori applicativi, logging e configurazioni d'ambiente.

La logica di business, l'accesso ai dati e l'inferenza AI sono mantenuti separati dalle route HTTP.

---

## 2. Stack tecnologico

| Area | Tecnologie |
|---|---|
| Linguaggio | Python |
| API REST | FastAPI, Uvicorn |
| Validazione e configurazione | Pydantic, pydantic-settings |
| Persistenza | PostgreSQL, SQLAlchemy |
| Autenticazione | JWT, hashing delle password |
| Elaborazione PDF | PyMuPDF |
| AI / NLP | GLiNER2.5, PyTorch, Transformers |
| Storage documenti | Filesystem locale, S3-compatible / SILO |
| Testing | pytest |
| Infrastruttura | Docker, Docker Compose |

Il modello NLP viene eseguito direttamente nell'infrastruttura applicativa, senza utilizzare API commerciali esterne di inferenza.

---

## 3. Architettura del backend

Il progetto adotta un'organizzazione modulare con separazione delle responsabilità.

```text
HTTP Request
     |
     v
FastAPI Router
     |
     v
Pydantic Validation
     |
     v
Dependency Injection
     |
     v
Application Services
     |
     +----------------+----------------+
     |                |                |
     v                v                v
Repositories      AI Pipeline     Document Storage
     |                |                |
     v                v                v
SQLAlchemy       GLiNER2.5       Local / S3
     |
     v
PostgreSQL
```

### API routes

Gestiscono richieste HTTP, parametri, status code e serializzazione delle risposte.

Non contengono direttamente query SQL o logica di inferenza.

### Application services

Implementano le regole applicative e coordinano le operazioni di alto livello.

Tra i servizi principali:

- `AuthService`
- `DocumentService`
- `AnalysisService`
- `AnalysisQueryService`
- `AnalysisQuotaService`
- `SchemaAccessService`
- `CustomSchemaService`

### Repository

Isolano l'accesso ai dati PostgreSQL attraverso SQLAlchemy.

Permettono di mantenere distinta la logica applicativa dalle operazioni di persistenza.

### AI pipeline

Contiene i componenti dedicati a preparazione documentale, configurazione, caricamento del modello, NER, IE, mappatura degli offset e persistenza dei risultati.

### Dependency injection

Il modulo `app/dependencies.py` definisce e collega le dipendenze utilizzate dalle route, compresi servizi, sessioni SQLAlchemy, autenticazione, storage e componenti AI.

---

## 4. Organizzazione del codice

```text
backend/
|
+-- app/
|   +-- api/
|   |   +-- routes/
|   |   +-- router.py
|   |
|   +-- core/
|   |   +-- config.py
|   |   +-- security.py
|   |   +-- exceptions.py
|   |   +-- error_handlers.py
|   |   +-- logging.py
|   |
|   +-- db/
|   |   +-- models.py
|   |   +-- session.py
|   |
|   +-- domain/
|   +-- pipeline/
|   +-- repositories/
|   +-- schemas/
|   +-- services/
|   |
|   +-- dependencies.py
|   +-- main.py
|
+-- sql/
|   +-- 01_schema.sql
|   +-- 02_seed.sql
|
+-- tests/
+-- requirements.txt
+-- .env.example
+-- README.md
```

Questa struttura rappresenta i moduli principali. Ulteriori componenti specifici sono organizzati nelle rispettive directory.

---

## 5. API REST

Le API sono esposte con prefisso:

```text
/api/v1
```

### Autenticazione e utenti

| Metodo | Endpoint | Funzione |
|---|---|---|
| POST | `/auth/register` | Registrazione utente |
| POST | `/auth/token` | Autenticazione e rilascio JWT |
| GET | `/auth/me` | Profilo autenticato |
| GET | `/auth/me/analysis-quota` | Stato della quota giornaliera |
| GET | `/admin/users` | Elenco utenti, riservato agli amministratori |

Il login utilizza il formato OAuth2 Password Request Form.

### Documenti

| Metodo | Endpoint | Funzione |
|---|---|---|
| GET | `/documents` | Elenco documenti dell'utente |
| POST | `/documents` | Caricamento PDF |
| GET | `/documents/{document_id}` | Dettaglio documento |
| GET | `/documents/{document_id}/file` | Lettura autenticata del PDF originale |

L'endpoint del file supporta richieste HTTP Range per la lettura parziale dei documenti.

### Analisi

| Metodo | Endpoint | Funzione |
|---|---|---|
| POST | `/documents/{document_id}/analyses` | Avvio di una nuova analisi |
| GET | `/documents/{document_id}/analyses` | Cronologia delle analisi |
| GET | `/documents/{document_id}/analyses/{analysis_id}` | Dettaglio e risultati |
| GET | `/documents/{document_id}/analyses/{analysis_id}/geometry` | Coordinate delle evidenziazioni PDF |

L'endpoint `geometry` richiede il parametro `page_number`.

### Schemi

Le API comprendono:

- `GET /schemas/available`
- Creazione di schemi personalizzati.
- Elenco e dettaglio degli schemi dell'utente.
- Modifica con versionamento.
- Duplicazione.
- Archiviazione.

Gli endpoint per gli schemi personalizzati sono disponibili in base al piano dell'utente.

### Health check

| Endpoint | Funzione |
|---|---|
| `GET /health` | Verifica disponibilità del servizio |
| `GET /health/database` | Verifica connessione PostgreSQL |

Tutti i percorsi della tabella sono relativi a `/api/v1`.

### Documentazione OpenAPI

Con il backend avviato localmente:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

Lo schema OpenAPI costituisce il riferimento aggiornato per i contratti delle API.

---

## 6. PostgreSQL e persistenza

La persistenza applicativa utilizza PostgreSQL e SQLAlchemy ORM.

Il database gestisce separatamente utenti, documenti, schemi di estrazione, versioni, configurazioni AI e risultati delle analisi.

### Tabelle principali

```text
plans
users

extraction_schemas
extraction_schema_versions
entity_definitions
field_definitions

documents
document_pages

ai_runtime_configs
analyses
entity_occurrences
extracted_fields
field_candidates
```

### Script SQL

Gli script di inizializzazione si trovano in `backend/sql/`.

**`01_schema.sql`**

Definisce la struttura iniziale del database, comprese tabelle, relazioni, vincoli e indici.

**`02_seed.sql`**

Inserisce i dati iniziali necessari al funzionamento dell'applicazione:

- Piani Base e Premium.
- Configurazione runtime AI predefinita.
- Schema built-in `general_document`.
- Versione attiva dello schema.
- Definizioni NER e IE predefinite.

Nell'ambiente Docker Portfolio questi script vengono eseguiti durante l'inizializzazione di un database vuoto.

**Importante:** modificare i seed non aggiorna automaticamente un database già inizializzato. Per gli ambienti esistenti sono necessarie operazioni di aggiornamento o migrazione controllate.

---

## 7. Schema di estrazione predefinito

Lo schema built-in è identificato dalla chiave:

```text
general_document
```

Il suo scopo è fornire una configurazione generale, indipendente da uno specifico settore applicativo.

### Entità NER

| Label | Descrizione |
|---|---|
| `PERSONA` | Nome e cognome di una persona |
| `ORGANIZZAZIONE` | Aziende, enti, istituzioni, associazioni e altre organizzazioni |
| `LOCALITA` | Luoghi, comuni, città, indirizzi e riferimenti geografici |
| `DATA` | Date, periodi e riferimenti temporali espressi come data |
| `ORA` | Orari e riferimenti temporali puntuali |
| `IMPORTO` | Somme di denaro e valori monetari |
| `EMAIL` | Indirizzi di posta elettronica |
| `TELEFONO` | Numeri e recapiti telefonici |
| `URL` | Indirizzi web e collegamenti Internet |
| `IDENTIFICATIVO` | Codici, protocolli, matricole e altri identificativi |

### Information Extraction

Lo schema predefinito contiene un solo campo strutturato:

| Proprietà | Valore |
|---|---|
| Label | Oggetto principale |
| `field_key` | `oggetto_principale` |
| Descrizione | Argomento o oggetto principale |
| Tipo | `string` |

Le definizioni vengono recuperate dal database e non sono codificate direttamente nella pipeline di inferenza.

---

## 8. GLiNER2.5 e integrazione AI

Il modello predefinito è:

```text
fastino/gliner2.5-multi-v1
```

La famiglia GLiNER2 consente di eseguire attività di estrazione delle informazioni mediante definizioni semantiche delle entità e dei campi richiesti.

### Motivazioni della scelta

**Schema-driven extraction**

Le categorie NER e i campi IE possono essere definiti attraverso uno schema, senza dover riscrivere la pipeline per ogni nuova configurazione.

**Flessibilità applicativa**

Il modello consente di sperimentare estrazioni su documenti e domini differenti, senza addestrare necessariamente un nuovo classificatore per ogni etichetta.

**Supporto multilingue**

Il checkpoint selezionato supporta più lingue, pur senza garantire accuratezza uniforme tra lingue e domini.

**NER e IE nello stesso ecosistema**

La libreria permette di integrare estrazione di entità e informazioni strutturate all'interno della medesima architettura applicativa.

**Inferenza self-hosted**

Il documento viene elaborato direttamente nell'infrastruttura del backend, senza inviarne il contenuto a provider esterni di inferenza AI.

### Scelte del progetto

- Utilizzo di un modello preaddestrato.
- Nessun fine-tuning.
- Nessuna valutazione quantitativa sistematica delle prestazioni.
- Nessun benchmark comparativo con altri modelli.
- Priorità all'integrazione software rispetto all'ottimizzazione del modello.

I risultati NLP non devono essere considerati automaticamente corretti o completi.

Il download iniziale dei pesi può richiedere una connessione a Hugging Face. I documenti analizzati non devono essere trasmessi al servizio per eseguire l'inferenza locale.

---

## 9. Configurazione runtime AI

Il backend separa la configurazione del modello dalla logica della pipeline.

La tabella `ai_runtime_configs` conserva informazioni come:

- Motore di inferenza.
- Identificativo e revisione del modello.
- Dimensione dei chunk.
- Sovrapposizione tra chunk.
- Batch size.
- Numero di worker.
- Politica di gestione delle sovrapposizioni.
- Soglie NER e IE.
- Stato di attivazione della configurazione.

### Configurazione iniziale

```text
engine           = GLINER2
model_id         = fastino/gliner2.5-multi-v1
chunk_size       = 512
chunk_overlap    = 96
batch_size       = 8
num_workers      = 0
overlap_policy   = allow
entity_threshold = 0.50
field_threshold  = 0.50
```

Questi parametri costituiscono una configurazione iniziale dimostrativa, non un insieme di valori ottimizzati mediante benchmark.

La pipeline risolve la configurazione attiva e la versione dello schema prima di eseguire l'analisi.

Ogni analisi conserva riferimenti e informazioni sulla configurazione utilizzata. Questo favorisce la tracciabilità delle esecuzioni, ma non garantisce risultati identici in tutte le condizioni hardware e software.

---

## 10. Pipeline di elaborazione

La pipeline coordina tutte le fasi comprese tra il documento originale e la persistenza dei risultati AI.

```text
PDF Upload
    |
    v
Document Validation
    |
    v
Storage Retrieval
    |
    v
PyMuPDF Text Extraction
    |
    v
Page Mapping & Provenance
    |
    v
AI Configuration Resolution
    |
    v
GLiNER2.5 Model Provider
    |
    +--------------------+
    |                    |
    v                    v
NER Extraction       Field Extraction
    |                    |
    v                    v
Deduplication        Candidate Resolution
    |                    |
    v                    v
Overlap Resolution   Field Mapping
    |                    |
    +---------+----------+
              |
              v
      PostgreSQL Persistence
              |
              v
        Analysis API
```

### Preparazione documentale

PyMuPDF estrae il testo e ne preserva l'organizzazione per pagina.

Per ogni pagina vengono memorizzati:

```text
page_number
extracted_text
global_start
global_end
```

### Elaborazione di documenti lunghi

Il testo viene suddiviso in chunk configurabili per consentire l'analisi di documenti che superano una singola finestra di elaborazione.

Le occorrenze vengono successivamente ricondotte agli offset globali.

### Gestione del modello

Un provider dedicato gestisce caricamento e riutilizzo del modello all'interno del processo backend, evitando caricamenti ripetuti per ogni richiesta quando la configurazione rimane invariata.

### NER

Il sistema:

1. Estrae entità secondo lo schema selezionato.
2. Riporta le occorrenze alle posizioni del documento.
3. Gestisce duplicati prodotti da chunk sovrapposti.
4. Applica una politica deterministica per la visibilità delle entità sovrapposte.

### Information Extraction

I campi vengono definiti dalla versione dello schema.

La pipeline identifica candidati, li associa al documento e determina un risultato per ciascun campo richiesto.

Gli stati previsti sono:

```text
EXTRACTED
AMBIGUOUS
NOT_FOUND
ERROR
```

Un campo `NOT_FOUND` indica che non è stato individuato un valore sufficientemente affidabile; non dimostra necessariamente che l'informazione sia assente dal documento.

---

## 11. Analysis lifecycle

`Analysis` rappresenta una singola esecuzione della pipeline.

Ogni analisi è associata a:

- Documento.
- Proprietario del documento.
- Versione dello schema.
- Configurazione AI.
- Stato di esecuzione.
- Timestamp.
- Entità riconosciute.
- Campi estratti e relativi candidati.

### Stati

```text
QUEUED
   |
   v
PROCESSING
   |
   +----> READY
   |
   +----> ERROR
```

Un'analisi completata con successo raggiunge `READY`.

I risultati definitivi sono disponibili attraverso le API quando l'analisi è pronta.

### Esecuzione sincrona

Nell'implementazione attuale, la richiesta HTTP che avvia l'analisi rimane aperta durante l'esecuzione della pipeline.

Lo stato `PROCESSING` viene persistito prima dell'elaborazione.

Questa scelta semplifica l'architettura didattica, ma presenta limiti relativi a timeout, concorrenza e interruzioni del processo.

Un'infrastruttura con job queue e worker dedicati rappresenta una possibile evoluzione.

---

## 12. Provenance, risultati e geometria PDF

Una caratteristica importante del backend è la conservazione delle informazioni necessarie a risalire all'origine delle estrazioni.

Per le entità vengono gestiti, quando disponibili:

- Label.
- Testo.
- Confidence.
- Pagina.
- Offset globali.
- Offset relativi alla pagina.
- Indicatore di visibilità nel viewer.

Per i campi IE vengono conservati anche stato, valore, posizione e possibili candidati alternativi.

### Evidenziazione sul documento

Il frontend utilizza PDF.js per visualizzare il documento originale.

Il backend espone un endpoint dedicato al calcolo delle coordinate di evidenziazione delle entità e dei campi estratti.

Le coordinate sono prodotte soltanto quando il testo persistito può essere allineato in modo affidabile al contenuto del PDF.

Questo evita di evidenziare porzioni di documento non corrispondenti ai risultati.

La provenance facilita la verifica delle estrazioni, ma non rappresenta una garanzia della loro correttezza semantica.

---

## 13. Storage dei documenti

Il backend separa i metadati relazionali dal contenuto binario dei documenti.

PostgreSQL conserva il riferimento al file tramite `storage_key`, mentre il documento originale viene archiviato nel sistema di storage.

Sono supportate due modalità applicative:

- `local`: archiviazione su filesystem.
- `s3`: archiviazione su storage S3-compatible.

Nell'ambiente Docker Portfolio viene utilizzato SILO con bucket privato.

### Accesso ai PDF

L'endpoint:

```text
GET /api/v1/documents/{document_id}/file
```

verifica l'accesso al documento e restituisce il contenuto PDF tramite il backend.

Supporta richieste HTTP Range e risposte `206 Partial Content`, utili al visualizzatore PDF.js.

Il bucket S3 non deve essere esposto pubblicamente per consentire la visualizzazione dei documenti.

---

## 14. Autenticazione, autorizzazione e piani

### Autenticazione

Il backend utilizza:

- Hashing delle password.
- Token JWT.
- Validazione dei token.
- Identificazione dell'utente corrente.
- Controllo dello stato dell'account.

Le route protette richiedono un token valido.

### Autorizzazione

Le verifiche comprendono:

- Proprietà dei documenti.
- Accesso alle analisi.
- Proprietà degli schemi custom.
- Permessi del ruolo amministrativo.
- Disponibilità delle funzionalità previste dal piano.

I controlli vengono eseguiti lato backend anche se il frontend nasconde determinate funzionalità.

### Piani applicativi

| Funzionalità | BASE | PREMIUM |
|---|---|---|
| Schema built-in | Sì | Sì |
| NER e IE | Sì | Sì |
| Quote giornaliere | 5 nel seed | Nessun limite applicativo nel seed |
| Schemi custom | No | Sì |
| Versionamento schemi custom | No | Sì |

La distinzione Base/Premium ha finalità dimostrative e non costituisce un sistema commerciale di pagamento o abbonamento.

### Quote

`AnalysisQuotaService` gestisce il conteggio delle analisi giornaliere.

La logica considera le analisi riservate o in elaborazione per ridurre il rischio di superamento del limite tramite richieste concorrenti.

La quota viene consumata al completamento positivo; gli errori interni non dovrebbero consumarla definitivamente.

Le finestre giornaliere sono basate su UTC.

---

## 15. Configurazione d'ambiente

Il backend utilizza `pydantic-settings`.

La configurazione viene definita in:

```text
app/core/config.py
```

I valori locali possono essere forniti attraverso variabili d'ambiente e il file `.env`.

### Variabili principali

| Variabile | Funzione |
|---|---|
| `APP_ENV` | Ambiente applicativo |
| `APP_LOG_LEVEL` | Livello di logging |
| `DB_HOST` | Host PostgreSQL |
| `DB_PORT` | Porta PostgreSQL |
| `DB_NAME` | Nome database |
| `DB_USER` | Utente applicativo |
| `DB_PASSWORD` | Password database |
| `JWT_SECRET_KEY` | Chiave di firma JWT |
| `DOCUMENT_STORAGE_BACKEND` | `local` oppure `s3` |
| `DOCUMENT_STORAGE_ROOT` | Directory storage locale |
| `DOCUMENT_S3_ENDPOINT_URL` | Endpoint S3 |
| `DOCUMENT_S3_BUCKET` | Bucket documenti |
| `DOCUMENT_S3_ACCESS_KEY` | Credenziale di accesso S3 |
| `DOCUMENT_S3_SECRET_KEY` | Credenziale segreta S3 |
| `AI_MODEL_DEVICE` | Dispositivo di inferenza |
| `AI_MODEL_QUANTIZE` | Abilitazione quantizzazione |
| `AI_MODEL_COMPILE` | Abilitazione compilazione |

Per la configurazione di sviluppo utilizzare `.env.example` come riferimento.

La chiave JWT deve rispettare i requisiti di validazione dell'applicazione, inclusa una lunghezza minima di 64 caratteri.

**Non versionare file `.env` contenenti credenziali reali.**

---

## 16. Avvio locale

### Prerequisiti

- Python e pip.
- PostgreSQL configurato e raggiungibile.
- Variabili d'ambiente correttamente impostate.
- Connettività per scaricare il modello, se non è già nella cache.

Dalla directory `backend/`:

### 16.1. Ambiente virtuale

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 16.2. Dipendenze

```powershell
python -m pip install -r requirements.txt
```

### 16.3. Configurazione

```powershell
Copy-Item .env.example .env
```

Personalizzare le variabili nel file `.env`.

Prima di avviare il backend è necessario che il database richiesto sia stato inizializzato.

### 16.4. Avvio FastAPI

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

API:

```text
http://127.0.0.1:8000/api/v1
```

Health check:

```text
http://127.0.0.1:8000/api/v1/health
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## 17. Ambiente Docker Portfolio

Il backend è incluso nello stack Docker Portfolio definito nella radice del repository.

La configurazione comprende:

- PostgreSQL con volume persistente.
- Storage privato S3-compatible.
- Inizializzazione dello storage.
- Backend FastAPI.
- Frontend React servito tramite Nginx.
- Cache persistente del modello AI.

### Avvio completo

Dalla radice di DocuEntitySeek:

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml up -d --build
```

### Stato dei servizi

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml ps -a
```

### Log backend

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml logs -f backend
```

### Health check attraverso Nginx

```text
http://localhost:8080/api/v1/health
```

### Arresto

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml down
```

Il comando non elimina i volumi persistenti.

Evitare `down -v` salvo esplicita intenzione di cancellare i dati del progetto Compose.

Per la configurazione completa dell'ambiente consultare il [README principale](../README.md).

---

## 18. Testing

Il backend utilizza pytest.

Dalla directory `backend/`:

```powershell
python -m pytest
```

### Verifica sintattica

```powershell
python -m compileall -q app
```

### Database di test

Il database di test deve essere separato dal database di sviluppo e dal database Portfolio.

È importante utilizzare configurazioni, credenziali e privilegi coerenti con le fixture e gli script dei test.

I test che modificano tabelle o schemi non devono essere eseguiti accidentalmente sul database contenente dati da conservare.

### Verifiche di integrazione

Il flusso principale è stato verificato manualmente nell'ambiente Docker Portfolio:

```text
User Registration
      |
      v
JWT Authentication
      |
      v
PDF Upload
      |
      v
PostgreSQL + S3 Storage
      |
      v
Document Preparation
      |
      v
GLiNER2.5 NER / IE
      |
      v
Analysis Persistence
      |
      v
Result Retrieval / PDF Viewer
```

Questi test manuali non sostituiscono una suite end-to-end automatizzata completa.

---

## 19. Gestione degli errori e logging

Il backend centralizza la gestione degli errori applicativi.

Le risposte API utilizzano codici HTTP appropriati e, quando previsto, codici di errore applicativi.

Esempi:

```text
DOCUMENT_NOT_FOUND
INVALID_DOCUMENT_FILE
ANALYSIS_QUOTA_EXCEEDED
ANALYSIS_FAILED
AI_CONFIGURATION_UNAVAILABLE
EXTRACTION_SCHEMA_NOT_FOUND
CUSTOM_SCHEMAS_NOT_AVAILABLE
CUSTOM_SCHEMA_NAME_CONFLICT
CUSTOM_SCHEMA_ARCHIVED
VALIDATION_ERROR
INTERNAL_SERVER_ERROR
```

I dettagli interni e i traceback non devono essere esposti direttamente al client.

### Logging

La pipeline produce log strutturati per fase, utili per:

- Identificare il documento e l'analisi.
- Verificare la configurazione AI.
- Monitorare preparazione ed estrazione.
- Individuare errori nel caricamento del modello.
- Controllare persistenza e completamento.

L'utilizzo di identificativi e fasi applicative facilita il debugging senza richiedere l'inserimento del contenuto completo dei documenti nei log.

---

## 20. Sicurezza

Le principali misure implementate includono:

- Autenticazione JWT.
- Hashing delle password.
- Controllo del proprietario delle risorse.
- Autorizzazione basata su ruoli e piani.
- Validazione dei documenti PDF.
- Accesso autenticato ai documenti originali.
- Storage privato.
- Configurazione CORS per gli origin previsti.
- Gestione dei segreti tramite configurazioni esterne.
- Inferenza AI eseguita nell'infrastruttura applicativa.

L'inferenza locale riduce la necessità di trasmettere documenti a servizi esterni di AI, ma non garantisce automaticamente sicurezza o conformità normativa.

Per un deployment pubblico sarebbero necessarie ulteriori misure, tra cui HTTPS, gestione centralizzata dei segreti, rate limiting, backup, monitoraggio e hardening infrastrutturale.

---

## 21. Limitazioni attuali

### Modello non ottimizzato

GLiNER2.5 viene utilizzato senza fine-tuning e senza una valutazione quantitativa delle prestazioni su dataset specifici.

### Elaborazione sincrona

Le analisi AI vengono eseguite durante la richiesta HTTP che ne avvia l'elaborazione.

Non è attualmente presente una job queue dedicata per gestire separatamente le inferenze pesanti.

### Risorse computazionali

Il caricamento del modello e l'analisi dei documenti possono essere onerosi, soprattutto su CPU e con documenti lunghi.

### OCR

Non è integrata una pipeline OCR dedicata per PDF costituiti esclusivamente da immagini o scansioni.

### Gestione delle interruzioni

Un'interruzione improvvisa del processo durante un'analisi può richiedere una procedura di recupero dello stato applicativo.

### Deployment

L'ambiente Docker Portfolio è destinato allo sviluppo e alla dimostrazione della piattaforma, non costituisce una configurazione production-ready per esposizione pubblica.

---

## 22. Possibili evoluzioni

Le principali direzioni di miglioramento comprendono:

- Introduzione di job queue e worker AI dedicati.
- Recupero automatico delle analisi interrotte.
- Supporto OCR.
- Maggiore copertura dei test automatici.
- Monitoraggio delle risorse e delle performance.
- Logging e osservabilità avanzati.
- Migrazioni database strutturate.
- Valutazioni quantitative della qualità delle estrazioni.
- Sperimentazione di altri modelli NLP e configurazioni.
- Hardening e deployment cloud.

Questi elementi rappresentano possibili sviluppi e non funzionalità già disponibili.

---

## 23. Principio architetturale

DocuEntitySeek mantiene una separazione intenzionale tra:

```text
AI MODEL
    !=
EXTRACTION SCHEMA
    !=
DOCUMENT PIPELINE
    !=
APPLICATION SERVICES
    !=
PERSISTENCE
    !=
HTTP API
```

Il modello realizza l'inferenza.

Lo schema definisce le entità e le informazioni richieste.

La pipeline coordina l'elaborazione documentale.

I servizi applicano le regole di business.

I repository gestiscono la persistenza.

Le API espongono le funzionalità ai client.

Questa separazione favorisce testabilità, manutenibilità ed evoluzione del progetto.

---

## Conclusione

Il backend di DocuEntitySeek rappresenta un esercizio di **ingegneria del software full-stack con integrazione AI**, in cui la complessità principale riguarda il coordinamento tra componenti applicativi, database, storage documentale e pipeline NLP.

GLiNER2.5 viene utilizzato come motore di estrazione preaddestrato e flessibile, senza essere oggetto di fine-tuning o benchmarking specifico.

**Il valore del progetto risiede soprattutto nelle scelte architetturali e nella capacità di integrare tecnologie differenti all'interno di un sistema modulare, persistente e funzionante.**

---

## Riferimenti

- [DocuEntitySeek — README principale](../README.md)
- [DocuEntitySeek — Frontend](../frontend/README.md)
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [PyMuPDF](https://pymupdf.readthedocs.io/)
- [GLiNER2 — Repository ufficiale](https://github.com/fastino-ai/GLiNER2)
- [GLiNER2.5 Multilingual — Model Card](https://huggingface.co/fastino/gliner2.5-multi-v1)
- [Docker](https://docs.docker.com/)