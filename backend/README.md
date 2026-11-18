# DocuEntitySeek — Backend

Backend Python/FastAPI di **DocuEntitySeek**, piattaforma full-stack di Document Intelligence per Named Entity Recognition (NER) e Structured Information Extraction (IE) su documenti PDF.

Il backend gestisce autenticazione, autorizzazione, documenti, storage, PostgreSQL, schema di estrazione, quote, lifecycle delle Analysis e pipeline AI self-hosted.

> **Stato attuale — checkpoint 19.23:** FastAPI e PostgreSQL sono completamente integrati tramite SQLAlchemy. La pipeline PyMuPDF + GLiNER2.5 viene eseguita dal backend e i risultati vengono persistiti. Sono inoltre implementati autenticazione JWT, Base/Premium, quote giornaliere e gestione versionata degli schemi custom Premium.

---

## 1. Stack

- Python
- FastAPI
- Uvicorn
- Pydantic
- pydantic-settings
- SQLAlchemy
- PostgreSQL
- PyMuPDF
- GLiNER2.5
- JWT
- pytest
- Docker / Docker Compose

---

## 2. Architettura

```text
HTTP Request
     |
     v
 FastAPI Route
     |
     v
Pydantic Schema
     |
     v
Dependencies
     |
     v
Application Service
     |
 +---+-------------------------+
 |                             |
 v                             v
Repository                 AI Pipeline
 |                             |
 v                             v
SQLAlchemy                   GLiNER
 |
 v
PostgreSQL
```

Il backend mantiene separate:

- route HTTP;
- schema API;
- business logic;
- repositories;
- ORM;
- pipeline AI;
- storage.

Le route non contengono direttamente query SQL né logica di inferenza.

---

## 3. Avvio locale

Dalla directory:

```text
backend/
```

creare l'ambiente virtuale:

```powershell
python -m venv .venv
```

attivarlo:

```powershell
.\.venv\Scripts\Activate.ps1
```

installare:

```powershell
python -m pip install -r requirements.txt
```

Creare `.env` utilizzando:

```text
.env.example
```

come riferimento.

Avviare:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

API:

```text
http://127.0.0.1:8000/api/v1
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

OpenAPI:

```text
http://127.0.0.1:8000/openapi.json
```

---

## 4. Configurazione

La configurazione viene caricata tramite `pydantic-settings`.

Le credenziali e i segreti devono essere memorizzati esclusivamente nei file ambiente locali o nel secret manager dell'ambiente di deployment.

Non versionare:

```text
.env
password PostgreSQL
JWT secret
token
credenziali
```

Per i nomi esatti delle variabili supportate utilizzare:

```text
backend/.env.example
```

---

## 5. CORS

Il backend utilizza `CORSMiddleware`.

Gli origin di sviluppo includono normalmente:

```text
http://localhost:5173
http://127.0.0.1:5173
```

Sono autorizzati i metodi utilizzati dal frontend, inclusi:

```text
GET
POST
PUT
PATCH
DELETE
```

Questo è necessario anche per i preflight `OPTIONS` generati dal browser.

---

## 6. Database

La persistenza utilizza PostgreSQL e SQLAlchemy.

### Modello principale

```text
plans
  |
users
  |
  +-----------------------------+
  |                             |
documents                extraction_schemas
  |                             |
document_pages           extraction_schema_versions
  |                             |
analyses                 +------+------+
  |                      |             |
  +-- entity_occurrences entity_definitions
  |
  +-- extracted_fields   field_definitions
         |
         +-- field_candidates

ai_runtime_configs
```

### Script SQL

Directory:

```text
backend/sql/
```

Gli script comprendono lo schema, i seed e gli aggiornamenti necessari allo sviluppo.

`04_ai_runtime_config.sql` contiene la configurazione SQL relativa al runtime AI e deve essere mantenuto insieme agli altri script del database.

---

## 7. Autenticazione

L'autenticazione utilizza JWT.

Il backend gestisce:

- registrazione;
- login;
- hashing delle password;
- token di accesso;
- utente corrente;
- account attivo/disabilitato;
- ruoli;
- piani.

Ruolo e piano sono concetti separati.

---

## 8. Piani

### BASE

Configurazione iniziale:

```text
daily_analysis_limit = 5
custom_schemas_enabled = false
```

### PREMIUM

Configurazione iniziale:

```text
daily_analysis_limit = NULL
custom_schemas_enabled = true
```

L'assenza di limite giornaliero è rappresentata da `NULL`.

La sicurezza non dipende dal frontend: il backend verifica sempre il piano dell'utente.

---

## 9. Quote

`AnalysisQuotaService` gestisce la disponibilità giornaliera.

Il conteggio considera anche Analysis già riservate/in elaborazione per evitare il superamento del limite tramite richieste concorrenti.

Una Analysis riuscita consuma quota.

Gli errori interni non devono consumare definitivamente un'analisi.

Il reset giornaliero utilizza attualmente finestre UTC.

---

## 10. Documenti

Il backend supporta:

- upload PDF;
- metadata persistence;
- ownership;
- storage;
- lista;
- dettaglio;
- pagine estratte;
- associazione alle Analysis.

Il PDF viene validato dal backend; la validazione React non è considerata una barriera di sicurezza.

---

## 11. Storage

Il file originale non viene salvato come blob PostgreSQL.

Il database conserva il riferimento allo storage attraverso `storage_key`.

Questo mantiene separati:

```text
metadati relazionali
```

e:

```text
contenuto binario
```

---

## 12. Estrazione del testo

PyMuPDF estrae il testo mantenendo la provenance delle pagine.

Per ciascuna pagina vengono conservati:

```text
page_number
extracted_text
global_start
global_end
```

Gli offset globali permettono di ricondurre le estrazioni AI alla pagina originale.

---

## 13. Configurazione AI

La configurazione runtime non è hardcoded nella pipeline.

La tabella:

```text
ai_runtime_configs
```

gestisce parametri come quelli relativi a:

- modello;
- chunking;
- overlap;
- threshold;
- batch/inferenza;
- policy della pipeline.

La configurazione usata da una Analysis viene conservata per garantire riproducibilità.

---

## 14. Model provider

Il modello viene gestito attraverso un provider/lifecycle dedicato.

Questo evita di ricaricare GLiNER2.5 a ogni richiesta.

Il modello di riferimento attuale è:

```text
fastino/gliner2.5-multi-v1
```

---

## 15. NER long-context

La pipeline usa un'estrazione long-context basata su chunk.

Baseline:

```text
chunk_size = 512
chunk_overlap = 96
```

Le occorrenze vengono riportate alle coordinate globali del documento.

La deduplicazione conserva la migliore occorrenza per la stessa combinazione di:

```text
label
global_start
global_end
```

---

## 16. Viewer overlap

Le entità persistite possono sovrapporsi nel risultato del modello.

La pipeline applica una risoluzione deterministica per stabilire quali entità debbano essere evidenziate nel viewer.

La selezione considera:

1. confidence;
2. lunghezza;
3. posizione iniziale;
4. label come tie-break deterministico.

L'informazione completa può comunque essere mantenuta nel database.

---

## 17. Field Extraction

I campi vengono definiti dinamicamente dalla versione dello schema.

La pipeline non deve conoscere in Python campi Procurement specifici.

Ogni campo può assumere:

```text
EXTRACTED
AMBIGUOUS
NOT_FOUND
ERROR
```

Sono persistiti:

- valore scelto;
- confidence;
- provenance;
- candidati alternativi.

---

## 18. Analysis

`Analysis` rappresenta una singola esecuzione AI.

Una Analysis collega:

```text
document
schema_version
ai_runtime_config
status
timestamps
results
```

Stati principali:

```text
QUEUED
PROCESSING
READY
ERROR
```

### Riproducibilità

Una Analysis mantiene il riferimento alla versione esatta dello schema utilizzata.

Se lo schema viene aggiornato da `v1` a `v2`, una Analysis storica eseguita con `v1` continua a puntare a `v1`.

---

## 19. Analysis API

Il backend espone operazioni per:

- avviare un'analisi;
- elencare le Analysis di un documento;
- recuperare il dettaglio;
- recuperare risultati persistiti.

La risposta READY include dati relativi a:

```text
pages
entities
fields
candidates
```

Le Analysis non READY non espongono risultati parziali come se fossero definitivi.

---

## 20. Schemi di estrazione

Lo schema è separato dalla pipeline.

```text
ExtractionSchema
 |
 +-- ExtractionSchemaVersion
      |
      +-- EntityDefinition[]
      |
      +-- FieldDefinition[]
```

Gli schema built-in non appartengono a un utente.

Gli schema custom possiedono `owner_user_id`.

---

## 21. Schemi custom Premium

Sono implementate API per:

- lista;
- dettaglio;
- creazione;
- modifica/versionamento;
- duplicazione;
- archiviazione;
- elenco degli schemi disponibili per nuove analisi.

### Versionamento

Una modifica crea una nuova versione.

```text
v1 INACTIVE
v2 ACTIVE
```

Le versioni precedenti non vengono sovrascritte.

### Archiviazione

Uno schema archiviato possiede:

```text
archived_at != NULL
```

Non viene più restituito tra gli schema utilizzabili per nuove Analysis.

Lo storico resta conservato.

### Duplicazione

La copia è un nuovo schema indipendente che riparte dalla versione 1.

---

## 22. Autorizzazione schema

Un utente può utilizzare:

### BASE

solo lo schema built-in disponibile.

### PREMIUM

- schema built-in;
- propri schema custom attivi.

Non può utilizzare:

- schema custom di altri utenti;
- versioni inattive;
- schema archiviati.

Il controllo avviene lato backend anche quando viene fornito manualmente uno UUID.

---

## 23. Error handling

Gli errori applicativi vengono normalizzati.

Esempi di codici:

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

I traceback non vengono restituiti al client.

---

## 24. Dependency injection

`app/dependencies.py` costruisce le dipendenze applicative.

Tra i servizi coinvolti:

```text
DocumentService
AuthService
AnalysisService
AnalysisQueryService
AnalysisQuotaService
SchemaAccessService
CustomSchemaService
AI configuration/provider/pipeline services
```

La sessione SQLAlchemy viene iniettata nei service/repository.

---

## 25. Repository layer

Le operazioni SQL sono isolate in repository dedicati.

Questo mantiene separati:

```text
HTTP
business logic
persistence
```

e rende i service più testabili.

---

## 26. Testing

Eseguire:

```powershell
python -m pytest
```

Controllo sintattico:

```powershell
python -m compileall -q app
```

Il database di test deve utilizzare credenziali e schema separati dal database di sviluppo.

---

## 27. OpenAPI

Con il backend attivo:

```text
Swagger
http://127.0.0.1:8000/docs

ReDoc
http://127.0.0.1:8000/redoc

OpenAPI
http://127.0.0.1:8000/openapi.json
```

---

## 28. Limitazioni attuali

### Esecuzione sincrona

L'avvio dell'Analysis mantiene attualmente aperta la richiesta mentre viene eseguita la pipeline.

Prima del deployment verrà valutato un worker/job system per l'inferenza pesante.

### OCR

Non è ancora presente una pipeline OCR.

Un PDF scansione privo di testo digitale non è quindi equivalente a un PDF testuale.

### Stato documento

`documents.status` è ancora utilizzato in alcune parti del flusso come elemento transitorio.

L'obiettivo architetturale è fare di `Analysis.status` la sorgente principale dello stato dell'esecuzione AI.

---

## 29. Sicurezza

Principi applicati:

- ownership delle risorse;
- JWT;
- piani verificati lato backend;
- quote backend;
- schema ownership;
- validazione PDF;
- CORS esplicito;
- no credenziali nel repository;
- inferenza AI self-hosted.

Prima della produzione sono ancora necessari hardening, HTTPS, gestione dei secret, rate limiting, backup e policy di conservazione.

---

## 30. Prossimo blocco

Il prossimo sviluppo riguarda il collegamento diretto del viewer frontend ai risultati reali:

```text
AnalysisDetail.result
```

Seguiranno:

- rendering pagine;
- entità;
- filtri;
- field;
- candidates;
- provenance;
- storico delle Analysis;
- rimozione del contratto demo legacy.