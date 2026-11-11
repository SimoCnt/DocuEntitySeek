# DocuEntitySeek — Backend

Backend Python/FastAPI di **DocuEntitySeek**, piattaforma di Document Intelligence dedicata alla Named Entity Recognition (NER) e alla Structured Information Extraction (IE) su documenti PDF.

Il backend espone una REST API versionata, utilizza Pydantic per la definizione dei contratti dati e adotta un'architettura modulare che separa routing HTTP, configurazione, logica applicativa, validazione e persistenza.

> **Stato attuale:** FastAPI è implementato con routing modulare, Pydantic schema, dependency injection, gestione centralizzata degli errori, validazione preliminare dei PDF, CORS e documentazione OpenAPI. È inoltre disponibile un database PostgreSQL con schema relazionale e dati iniziali. Il backend utilizza ancora un `DocumentService` in memoria: l'integrazione FastAPI ↔ PostgreSQL verrà introdotta con SQLAlchemy.

---

## 1. Stack tecnologico

| Tecnologia | Utilizzo |
|---|---|
| Python | Linguaggio backend |
| FastAPI | Framework REST API |
| Uvicorn | Server ASGI di sviluppo |
| Pydantic | Validazione e serializzazione dei dati |
| pydantic-settings | Configurazione tramite variabili ambiente |
| python-multipart | Gestione upload `multipart/form-data` |
| PostgreSQL | Database relazionale |
| pgAdmin 4 | Amministrazione grafica di PostgreSQL |

### Prerequisiti

- Python compatibile con le dipendenze installate
- PostgreSQL
- pgAdmin 4
- Git

Il frontend React viene eseguito separatamente e non è ancora collegato direttamente al backend.

---

## 2. Installazione

Posizionarsi nella directory:

```text
DocuEntitySeek/backend
```

### Creazione dell'ambiente virtuale

Se l'ambiente virtuale non esiste ancora:

```powershell
python -m venv .venv
```

Attivarlo da PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Il prompt dovrebbe mostrare:

```text
(.venv)
```

### Installazione delle dipendenze

```powershell
python -m pip install -r requirements.txt
```

Il file:

```text
requirements.txt
```

contiene le dipendenze Python utilizzate dal backend.

---

## 3. Configurazione dell'ambiente

Il backend utilizza variabili ambiente.

File di riferimento:

```text
.env.example
```

Il file locale:

```text
.env
```

non deve essere versionato con Git.

Una configurazione di sviluppo può contenere:

```env
APP_NAME=DocuEntitySeek API
APP_VERSION=0.1.0
APP_ENV=development
DEBUG=true

API_V1_PREFIX=/api/v1

CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]

DB_HOST=localhost
DB_PORT=5432
DB_NAME=docuentityseek
DB_USER=docuentityseek_app
DB_PASSWORD=
```

La password PostgreSQL deve essere inserita esclusivamente nel file `.env` locale.

Le variabili `DB_*` documentano già la connessione PostgreSQL, ma non vengono ancora utilizzate dal `DocumentService`. Il collegamento applicativo al database verrà introdotto tramite SQLAlchemy.

---

## 4. Struttura del progetto

```text
backend/
|
+-- app/
|   |
|   +-- api/
|   |   |
|   |   +-- routes/
|   |   |   +-- health.py
|   |   |   +-- documents.py
|   |   |
|   |   +-- router.py
|   |
|   +-- core/
|   |   +-- config.py
|   |   +-- exceptions.py
|   |   +-- error_handlers.py
|   |
|   +-- data/
|   |   +-- mock_documents.py
|   |
|   +-- schemas/
|   |   +-- base.py
|   |   +-- common.py
|   |   +-- analysis.py
|   |   +-- document.py
|   |
|   +-- services/
|   |   +-- document_service.py
|   |   +-- file_validation.py
|   |
|   +-- dependencies.py
|   +-- main.py
|
+-- sql/
|   +-- 01_schema.sql
|   +-- 02_seed.sql
|   +-- 03_crud_lab.sql
|
+-- .env.example
+-- requirements.txt
+-- README.md
```

Gli ambienti virtuali, i file `.env` locali e gli altri file generati non devono essere versionati.

---

## 5. Architettura backend

Il backend segue una separazione delle responsabilità.

```text
HTTP Request
      |
      v
   FastAPI
      |
      v
   APIRouter
      |
      v
Pydantic Validation
      |
      v
Dependency Injection
      |
      v
Application Service
      |
      v
Temporary In-Memory Store
      |
      v
Pydantic Response
      |
      v
 JSON / HTTP Response
```

Nello stato attuale il livello di persistenza utilizzato dalle API è ancora in memoria.

L'architettura prevista diventerà:

```text
HTTP Request
      |
      v
   FastAPI
      |
      v
   APIRouter
      |
      v
Pydantic Validation
      |
      v
Dependency Injection
      |
      v
Application Service
      |
      v
   SQLAlchemy
      |
      v
  PostgreSQL
```

---

## 6. Entry point dell'applicazione

File:

```text
app/main.py
```

Il modulo costruisce l'applicazione FastAPI mediante una application factory:

```text
create_application()
```

La factory configura:

- metadati dell'API;
- CORS;
- exception handler;
- router principale;
- prefisso API;
- Swagger UI;
- ReDoc;
- OpenAPI.

L'istanza ASGI esportata è:

```text
app
```

e viene utilizzata da Uvicorn attraverso:

```text
app.main:app
```

---

## 7. Avvio del backend

Dalla directory:

```text
DocuEntitySeek/backend
```

con l'ambiente virtuale attivo:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Il backend viene normalmente esposto su:

```text
http://127.0.0.1:8000
```

Il flag:

```text
--reload
```

è destinato esclusivamente allo sviluppo locale.

---

## 8. API versioning

Le API applicative utilizzano il prefisso:

```text
/api/v1
```

La versione API è separata dalla versione dell'applicazione.

Questa struttura permette di introdurre in futuro nuove versioni degli endpoint senza modificare immediatamente i client che utilizzano una versione precedente.

---

## 9. Routing

Il router principale si trova in:

```text
app/api/router.py
```

I router specifici del dominio si trovano in:

```text
app/api/routes/
```

Attualmente sono presenti:

```text
health.py
documents.py
```

La struttura è:

```text
FastAPI application
        |
        v
    api_router
        |
        +-- health.router
        |
        +-- documents.router
```

L'utilizzo di `APIRouter` evita di concentrare tutte le route in `main.py`.

---

## 10. Endpoint REST

### 10.1 Health check

```http
GET /api/v1/health
```

Verifica che l'applicazione FastAPI sia raggiungibile.

Esempio di risposta:

```json
{
    "status": "ok",
    "service": "DocuEntitySeek API",
    "version": "0.1.0"
}
```

---

### 10.2 Elenco documenti

```http
GET /api/v1/documents
```

Restituisce l'elenco dei documenti conosciuti dal `DocumentService`.

Risposta:

```text
DocumentSummary[]
```

I dati provengono attualmente dallo storage in memoria.

---

### 10.3 Dettaglio documento

```http
GET /api/v1/documents/{document_id}
```

Restituisce:

```text
DocumentDetailResponse
```

contenente:

```text
document
analysis
```

Se il documento non esiste viene restituito:

```http
404 Not Found
```

---

### 10.4 Creazione documento

```http
POST /api/v1/documents
```

La richiesta utilizza:

```text
multipart/form-data
```

e contiene:

```text
file
category
```

Il campo `file` rappresenta il PDF.

Il campo `category` rappresenta la categoria documentale.

Categorie previste:

```text
DISCIPLINARE
CAPITOLATO
CONTRATTO
BANDO
ALTRO
```

Una creazione valida restituisce:

```http
201 Created
```

Il documento viene attualmente registrato soltanto nello storage in memoria.

I byte del PDF non vengono ancora conservati permanentemente.

---

## 11. Pydantic schema

Directory:

```text
app/schemas/
```

Gli schema Pydantic definiscono i contratti dell'API.

### base.py

Contiene il modello base:

```text
ApiModel
```

utilizzato dagli altri schema.

La configurazione permette di utilizzare:

```text
snake_case
```

nel codice Python e:

```text
camelCase
```

nelle risposte JSON.

Esempio:

```text
uploaded_at
```

viene serializzato come:

```text
uploadedAt
```

---

### common.py

Contiene strutture comuni come:

```text
HealthResponse
ErrorDetail
ErrorResponse
```

---

### document.py

Contiene i modelli relativi ai documenti.

Tra questi:

```text
DocumentStatus
DocumentCategory
DocumentSummary
DocumentDetailResponse
```

Gli stati documentali attualmente supportati sono:

```text
READY
PROCESSING
ERROR
```

---

### analysis.py

Contiene i contratti relativi ai risultati dell'analisi.

Tra questi:

```text
EntityDefinition
TextOnlySegment
EntitySegment
DocumentPage
ExtractedField
DocumentAnalysis
```

Gli stati di un campo estratto sono:

```text
EXTRACTED
AMBIGUOUS
NOT_FOUND
ERROR
```

---

## 12. Discriminated Union dei segmenti

Il testo analizzato viene rappresentato mediante segmenti.

Un segmento può essere:

```text
text
```

oppure:

```text
entity
```

Il campo:

```text
type
```

permette a Pydantic di identificare automaticamente il modello corretto.

Esempio concettuale:

```json
{
    "type": "text",
    "text": "La procedura è indetta da "
}
```

oppure:

```json
{
    "type": "entity",
    "id": "entity-1",
    "text": "Comune di Palermo",
    "label": "ORGANIZZAZIONE"
}
```

Questa struttura corrisponde al modello utilizzato dal frontend React.

---

## 13. Service Layer

Directory:

```text
app/services/
```

### DocumentService

File:

```text
app/services/document_service.py
```

Il service contiene la logica applicativa relativa ai documenti.

Operazioni attuali:

```text
list_documents()
get_document()
create_document()
```

Il router HTTP non accede direttamente allo storage.

La catena è:

```text
Router
  |
  v
DocumentService
  |
  v
Storage
```

Nello stato corrente lo storage è un dizionario Python.

Questa implementazione è temporanea.

Il futuro collegamento a PostgreSQL verrà realizzato senza spostare la logica applicativa direttamente nelle route FastAPI.

---

## 14. Dependency Injection

File:

```text
app/dependencies.py
```

FastAPI utilizza dependency injection per fornire il `DocumentService` alle route.

Il tipo:

```text
DocumentServiceDep
```

rappresenta la dipendenza utilizzata dagli endpoint.

Concettualmente:

```text
Route
  |
  v
Depends(...)
  |
  v
get_document_service()
  |
  v
DocumentService
```

In seguito lo stesso meccanismo verrà utilizzato per:

```text
database session
authenticated user
authorization
```

---

## 15. Validazione PDF

File:

```text
app/services/file_validation.py
```

Il backend esegue una validazione preliminare dei file PDF.

I controlli includono:

- presenza del nome del file;
- estensione `.pdf`;
- controllo preliminare del contenuto tramite signature PDF.

La validazione frontend non viene considerata sufficiente.

La validazione definitiva del documento verrà rafforzata quando la pipeline PyMuPDF verrà integrata nel backend.

---

## 16. Error handling

File:

```text
app/core/error_handlers.py
```

Gli errori vengono trasformati in un formato JSON uniforme.

Struttura generale:

```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Messaggio leggibile",
        "details": null
    }
}
```

Sono gestiti esplicitamente:

```text
DocumentNotFoundError
InvalidDocumentFileError
RequestValidationError
HTTPException
Exception
```

### Codici applicativi

Esempi:

```text
DOCUMENT_NOT_FOUND
INVALID_DOCUMENT_FILE
VALIDATION_ERROR
HTTP_ERROR
INTERNAL_SERVER_ERROR
```

Gli errori interni non espongono traceback o informazioni tecniche sensibili al client.

I dettagli vengono invece registrati attraverso il logging applicativo.

---

## 17. Status code HTTP

Il backend utilizza status code coerenti con il risultato dell'operazione.

| Status | Significato |
|---|---|
| `200 OK` | Lettura riuscita |
| `201 Created` | Risorsa creata |
| `400 Bad Request` | File o richiesta semanticamente non valida |
| `404 Not Found` | Risorsa inesistente |
| `422 Unprocessable Entity` | Validazione della richiesta fallita |
| `500 Internal Server Error` | Errore interno |

---

## 18. CORS

Il backend utilizza:

```text
CORSMiddleware
```

per consentire le richieste provenienti dal frontend di sviluppo.

Origin previsti:

```text
http://localhost:5173
http://127.0.0.1:5173
```

Non viene utilizzato:

```text
*
```

come origin globale.

Questo permette di mantenere una configurazione compatibile con la futura autenticazione tramite header:

```text
Authorization
```

---

## 19. Documentazione OpenAPI

FastAPI genera automaticamente la documentazione dell'API.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

Swagger permette di:

- visualizzare gli endpoint;
- leggere request e response schema;
- effettuare richieste direttamente dal browser;
- controllare status code e response body.

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

### OpenAPI JSON

```text
http://127.0.0.1:8000/openapi.json
```

Il file OpenAPI rappresenta il contratto machine-readable dell'API.

---

## 20. PostgreSQL

DocuEntitySeek dispone di un database PostgreSQL locale.

Database:

```text
docuentityseek
```

Ruolo applicativo:

```text
docuentityseek_app
```

Configurazione locale:

```text
Host: localhost
Port: 5432
Database: docuentityseek
User: docuentityseek_app
```

Il ruolo applicativo non deve essere un superuser PostgreSQL.

L'amministrazione locale viene effettuata principalmente tramite:

```text
pgAdmin 4
```

---

## 21. Script SQL

Directory:

```text
backend/sql/
```

### 01_schema.sql

Definisce lo schema relazionale del database.

Contiene:

- tabelle;
- primary key;
- foreign key;
- check constraint;
- unique constraint;
- indici.

### 02_seed.sql

Inserisce i dati applicativi iniziali.

Il seed crea:

```text
2 piani
1 utente demo
1 schema Procurement
1 versione Procurement
10 definizioni NER
15 definizioni Field Extraction
```

I piani iniziali sono:

```text
BASE
PREMIUM
```

Il piano BASE prevede:

```text
daily_analysis_limit = 5
custom_schemas_enabled = false
```

Il piano PREMIUM prevede:

```text
daily_analysis_limit = NULL
custom_schemas_enabled = true
```

`NULL` indica l'assenza di un limite giornaliero applicativo configurato.

### 03_crud_lab.sql

Contiene query didattiche per studiare direttamente PostgreSQL.

Comprende esempi di:

```text
INSERT
SELECT
JOIN
UPDATE
DELETE
TRANSACTION
COMMIT
ROLLBACK
```

---

## 22. Modello relazionale

La struttura principale del database è:

```text
plans
  |
  v
users
  |
  +-------------------+
  |                   |
  v                   v
documents       extraction_schemas
  |                   |
  |                   v
  |          extraction_schema_versions
  |                   |
  |             +-----+-----+
  |             |           |
  |             v           v
  |   entity_definitions  field_definitions
  |
  +-- document_pages
  |
  v
analyses
  |
  +-- entity_occurrences
  |
  +-- extracted_fields
           |
           v
     field_candidates
```

---

## 23. Tabelle PostgreSQL

### plans

Contiene i piani applicativi.

Attualmente:

```text
BASE
PREMIUM
```

### users

Contiene gli utenti della piattaforma.

L'autenticazione non è ancora implementata.

L'utente demo esiste esclusivamente come dato iniziale per lo sviluppo.

### extraction_schemas

Contiene gli schemi di estrazione.

Lo schema predefinito iniziale è:

```text
Procurement
```

Gli schemi built-in non appartengono a un singolo utente.

Gli schemi personalizzati futuri saranno associati al proprietario.

### extraction_schema_versions

Permette di versionare gli schemi.

Un'analisi mantiene così il riferimento alla versione esatta utilizzata.

### entity_definitions

Contiene le categorie NER associate a una versione dello schema.

Il Procurement schema iniziale contiene 10 categorie.

### field_definitions

Contiene i campi strutturati da estrarre.

Il Procurement schema iniziale contiene 15 campi.

### documents

Contiene i metadati dei documenti PDF.

Il PDF non viene memorizzato direttamente nella tabella.

La posizione futura del file viene rappresentata tramite:

```text
storage_key
```

### document_pages

Contiene il testo estratto pagina per pagina.

Conserva anche:

```text
global_start
global_end
```

necessari alla provenance testuale.

### analyses

Rappresenta una singola esecuzione della pipeline AI.

Un documento può avere più analisi.

Ogni analisi fa riferimento a una specifica versione dello schema.

La configurazione tecnica variabile viene conservata in:

```text
JSONB
```

### entity_occurrences

Contiene le singole entità NER trovate nel documento.

Conserva:

```text
label
text
confidence
page
global offsets
page offsets
```

### extracted_fields

Contiene il valore logico associato a ciascun campo strutturato.

Stati previsti:

```text
EXTRACTED
AMBIGUOUS
NOT_FOUND
ERROR
```

### field_candidates

Conserva i candidati alternativi associati a un campo estratto.

Permette di mantenere risultati alternativi senza perdere informazione.

---

## 24. NER e Field Extraction nel database

DocuEntitySeek mantiene separate le due operazioni.

### Entity Discovery

Una NER rappresenta un'occurrence nel testo.

Esempio:

```text
Comune di Palermo
ORGANIZZAZIONE
Pagina 12
Confidence 0.96
```

Viene conservata in:

```text
entity_occurrences
```

### Field Extraction

Un campo rappresenta invece una proprietà logica del documento.

Esempio:

```text
Stazione appaltante
→ Comune di Palermo
```

Viene conservato in:

```text
extracted_fields
```

Eventuali alternative vengono conservate in:

```text
field_candidates
```

---

## 25. Gestione dei PDF

I PDF non sono progettati per essere memorizzati direttamente come contenuto binario PostgreSQL.

La tabella:

```text
documents
```

conserva metadati e un riferimento:

```text
storage_key
```

Il file reale potrà essere memorizzato in futuro:

```text
filesystem locale
```

durante lo sviluppo oppure:

```text
object storage
```

nel deployment.

---

## 26. pgAdmin 4

pgAdmin 4 viene utilizzato come client grafico per amministrare PostgreSQL.

La connessione applicativa di sviluppo utilizza:

```text
Host: localhost
Port: 5432
Maintenance database: docuentityseek
Username: docuentityseek_app
```

Strumenti principali utilizzati:

```text
Object Explorer
Query Tool
View/Edit Data
ERD Tool
```

### Object Explorer

Permette di esplorare:

```text
Databases
Schemas
Tables
Columns
Constraints
Indexes
```

### Query Tool

Permette di eseguire gli script SQL presenti in:

```text
backend/sql/
```

### View/Edit Data

Permette di ispezionare graficamente le righe delle tabelle.

### ERD Tool

Permette di visualizzare le relazioni tra le tabelle.

---

## 27. Verifica del database

Dopo l'esecuzione di:

```text
01_schema.sql
02_seed.sql
```

è possibile verificare il seed con:

```sql
SELECT
    (SELECT COUNT(*) FROM plans)
        AS plans,

    (SELECT COUNT(*) FROM users)
        AS users,

    (SELECT COUNT(*) FROM extraction_schemas)
        AS schemas,

    (SELECT COUNT(*) FROM extraction_schema_versions)
        AS schema_versions,

    (SELECT COUNT(*) FROM entity_definitions)
        AS entities,

    (SELECT COUNT(*) FROM field_definitions)
        AS fields;
```

Su un database iniziale il risultato previsto è:

```text
plans            2
users            1
schemas          1
schema_versions  1
entities         10
fields           15
```

---

## 28. Stato della persistenza

PostgreSQL esiste ed è configurato, ma FastAPI non lo utilizza ancora direttamente.

La situazione attuale è:

```text
FastAPI
   |
   v
DocumentService
   |
   v
Python dictionary
```

Separatamente:

```text
PostgreSQL
   |
   v
Relational schema
```

Il prossimo livello architetturale sarà:

```text
FastAPI
   |
   v
DocumentService
   |
   v
SQLAlchemy
   |
   v
PostgreSQL
```

---

## 29. Test manuali API

### Test 1 — Health

Avviare:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Aprire:

```text
http://127.0.0.1:8000/api/v1/health
```

Risultato previsto:

```text
200 OK
```

---

### Test 2 — Elenco documenti

Da Swagger:

```http
GET /api/v1/documents
```

Risultato previsto:

```text
200 OK
```

---

### Test 3 — Documento esistente

```http
GET /api/v1/documents/disciplinare-palermo-2027
```

Risultato previsto:

```text
200 OK
```

---

### Test 4 — Documento inesistente

```http
GET /api/v1/documents/documento-inesistente
```

Risultato previsto:

```text
404 Not Found
```

con codice applicativo:

```text
DOCUMENT_NOT_FOUND
```

---

### Test 5 — Upload PDF valido

Da Swagger:

```http
POST /api/v1/documents
```

fornire:

```text
file = PDF valido
category = DISCIPLINARE
```

Risultato previsto:

```text
201 Created
```

---

### Test 6 — File non PDF

Inviare un file non valido.

Risultato previsto:

```text
400 Bad Request
```

con:

```text
INVALID_DOCUMENT_FILE
```

---

### Test 7 — Categoria invalida

Inviare una categoria non prevista.

Risultato previsto:

```text
422 Unprocessable Entity
```

con:

```text
VALIDATION_ERROR
```

---

## 30. Stato di sviluppo

| Funzionalità | Stato |
|---|---|
| FastAPI | Implementato |
| Application factory | Implementata |
| API versioning | Implementato |
| APIRouter | Implementato |
| Health endpoint | Implementato |
| Document list endpoint | Implementato |
| Document detail endpoint | Implementato |
| PDF upload endpoint | Implementato a livello REST |
| Pydantic schema | Implementati |
| snake_case → camelCase | Implementato |
| Dependency Injection | Implementata |
| Service Layer | Implementato |
| PDF validation preliminare | Implementata |
| Error envelope | Implementato |
| Exception handler | Implementati |
| CORS | Configurato |
| Swagger UI | Disponibile |
| ReDoc | Disponibile |
| OpenAPI | Disponibile |
| PostgreSQL | Configurato |
| Schema relazionale | Implementato |
| Seed PostgreSQL | Implementato |
| pgAdmin 4 | Configurato |
| SQL CRUD didattico | Implementato |
| SQLAlchemy | Da implementare |
| FastAPI ↔ PostgreSQL | Da integrare |
| Persistenza PDF | Da implementare |
| Autenticazione | Da implementare |
| Autorizzazione | Da implementare |
| Quote BASE/PREMIUM | Modellate nel DB, da applicare |
| Pipeline AI nel backend | Da integrare |
| Test automatici | Da implementare |
| Docker | Da implementare |
| Deployment | Da implementare |

---

## 31. Limitazioni attuali

Il backend è ancora in una fase di sviluppo incrementale.

In particolare:

- i documenti delle API sono conservati in memoria;
- i record creati tramite REST vengono persi al riavvio del server;
- PostgreSQL non è ancora utilizzato da FastAPI;
- i PDF caricati non vengono conservati permanentemente;
- la pipeline PyMuPDF/GLiNER non è ancora integrata nel backend;
- non esiste autenticazione;
- non esiste isolamento reale dei documenti tra utenti;
- le quote BASE/PREMIUM non vengono ancora applicate;
- non è presente una suite automatizzata di test backend.

---

## 32. Prossimi sviluppi

Le successive fasi backend comprenderanno:

1. Introduzione di SQLAlchemy.
2. Configurazione dell'engine PostgreSQL.
3. Session management.
4. Mapping ORM delle tabelle.
5. Repository layer.
6. Sostituzione dello storage in memoria.
7. Persistenza reale dei documenti.
8. Autenticazione.
9. Autorizzazione.
10. Enforcement dei piani BASE/PREMIUM.
11. Testing backend.
12. Integrazione con React.
13. Integrazione della pipeline AI.
14. Docker Compose.
15. Deployment.

Lo sviluppo continuerà mantenendo separate le responsabilità tra HTTP layer, logica applicativa, persistenza e pipeline AI.

---

## 33. Documentazione correlata

README principale:

```text
../README.md
```

README frontend:

```text
../frontend/README.md
```

Requisiti funzionali:

```text
../docs/DocuEntitySeek_Requisiti_Funzionali.pdf
```

User Story:

```text
../docs/DocuEntitySeek_User_Story.pdf
```

---

## 34. Finalità

Il backend di DocuEntitySeek costituisce il livello applicativo responsabile della gestione delle API, dei documenti, degli schemi di estrazione, delle analisi e della futura integrazione con PostgreSQL e con la pipeline AI.

L'architettura viene sviluppata incrementalmente per rendere espliciti e comprensibili i diversi livelli del sistema:

```text
HTTP
→ FastAPI
→ Pydantic
→ Services
→ SQLAlchemy
→ PostgreSQL
→ AI Pipeline
```

L'obiettivo è mantenere il backend modulare, verificabile e sufficientemente indipendente dai dettagli della persistenza e dell'interfaccia frontend.