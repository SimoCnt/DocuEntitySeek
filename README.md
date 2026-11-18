# DocuEntitySeek

**Document Intelligence Platform — Named Entity Recognition & Structured Information Extraction**

DocuEntitySeek è una piattaforma full-stack di Document Intelligence per l'analisi di documenti PDF mediante Natural Language Processing e modelli di Intelligenza Artificiale self-hosted.

Il sistema trasforma testo documentale non strutturato in:

- entità riconosciute mediante Named Entity Recognition (NER);
- informazioni strutturate mediante Information Extraction (IE);
- risultati verificabili con pagina, offset e confidence;
- analisi persistenti e riproducibili associate alla versione dello schema utilizzata.


> **Stato attuale — checkpoint 19.23:** frontend React, backend FastAPI, PostgreSQL, autenticazione JWT, piani Base/Premium, quote di analisi, storage PDF, estrazione PyMuPDF, pipeline GLiNER2.5, persistenza dei risultati AI e gestione completa degli schemi custom Premium sono integrati. Il viewer frontend utilizza ancora in parte il precedente contratto dimostrativo e costituisce il prossimo blocco di refactoring.

---

## 1. Funzionalità implementate

### Autenticazione e utenti

DocuEntitySeek supporta:

- registrazione;
- login JWT;
- recupero dell'utente autenticato;
- account attivi/disabilitati;
- ruoli applicativi separati dai piani;
- protezione delle risorse in base al proprietario.

### Piani Base e Premium

#### Base

- schema built-in;
- massimo configurabile di analisi giornaliere;
- NER;
- Structured Information Extraction;
- consultazione dei risultati.

La configurazione iniziale prevede un limite di 5 nuove analisi al giorno.

#### Premium

Include le funzionalità Base e aggiunge:

- analisi senza limite giornaliero applicativo configurato;
- schemi di estrazione personalizzati;
- entità NER personalizzate;
- campi strutturati personalizzati;
- versionamento degli schemi;
- duplicazione;
- archiviazione;
- selezione dello schema prima dell'analisi.

Le autorizzazioni non dipendono dal solo frontend: vengono verificate anche dal backend.

---

## 2. Gestione dei documenti

Gli utenti autenticati possono:

1. caricare un PDF;
2. associare una categoria documentale;
3. avviare automaticamente l'analisi;
4. visualizzare lo stato di elaborazione;
5. consultare lo storico delle analisi.

Il documento viene persistito nel sistema di storage e i relativi metadati vengono registrati in PostgreSQL.

Il testo viene estratto mediante PyMuPDF mantenendo la relazione tra:

- testo globale;
- pagina;
- offset globali;
- offset relativi alla pagina.

### Aggiornamento automatico dello stato

La pagina dei documenti aggiorna automaticamente i documenti in stato `PROCESSING`.

Il polling viene eseguito soltanto mentre esistono documenti in elaborazione e viene interrotto quando non è più necessario.

---

## 3. Pipeline AI

La pipeline AI è integrata nel backend applicativo.

```text
PDF
 |
 v
Storage
 |
 v
PyMuPDF
 |
 v
Testo + pagine + offset
 |
 v
GLiNER2.5
 |
 +-------------------------+
 |                         |
 v                         v
Entity Discovery      Field Extraction
 |                         |
 v                         v
Long-context          Long-context
chunking              chunking
 |                         |
 v                         v
Deduplicazione        Candidate extraction
 |                         |
 v                         v
Overlap resolution    Field resolution
 |                         |
 +-----------+-------------+
             |
             v
      PostgreSQL
             |
             v
      Analysis API
```

### Modello

Il modello di riferimento attuale è:

```text
fastino/gliner2.5-multi-v1
```

L'architettura utilizza un provider dedicato al lifecycle del modello, evitando di caricarlo nuovamente a ogni richiesta.

### Long context

La pipeline supporta documenti più lunghi mediante chunking configurabile.

Valori baseline:

```text
chunk size    = 512
chunk overlap = 96
```

I parametri AI non sono hardcoded nella pipeline Python: la configurazione runtime viene recuperata dal database.

---

## 4. Schema di estrazione

Uno schema determina **cosa** deve essere estratto.

La pipeline determina **come** viene elaborato il documento.

```text
PIPELINE
= algoritmo di elaborazione

SCHEMA
= entità + campi richiesti
```

### Entità

Le entità sono definizioni NER ripetibili, ad esempio:

```text
PERSONA
ORGANIZZAZIONE
LOCALITA
```

Le label effettivamente utilizzate vengono recuperate dal database.

### Campi

I campi rappresentano informazioni strutturate.

Ogni campo può produrre:

```text
EXTRACTED
AMBIGUOUS
NOT_FOUND
ERROR
```

`NOT_FOUND` significa che il sistema non ha trovato un valore affidabile; non equivale necessariamente all'assenza dell'informazione nel documento.

---

## 5. Schemi custom Premium

Gli utenti Premium possono creare schemi indipendenti dal built-in.

Ogni schema contiene:

```text
Schema
 |
 +-- Entity definitions
 |
 +-- Field definitions
```

### Versionamento

Uno schema non viene modificato in-place.

Esempio:

```text
Schema HR
 |
 +-- v1 INACTIVE
 |
 +-- v2 INACTIVE
 |
 +-- v3 ACTIVE
```

Quando lo schema viene modificato:

- viene creata una nuova versione;
- la precedente diventa inattiva;
- le analisi storiche continuano a puntare alla versione originaria.

Questo permette la riproducibilità dei risultati.

### Duplicazione

Uno schema può essere duplicato.

La copia:

- possiede un nuovo `schema_id`;
- possiede una nuova `structure_key`;
- riparte dalla versione 1;
- copia entità, campi e relative configurazioni.

### Archiviazione

Gli schemi non vengono eliminati fisicamente quando possono essere collegati ad analisi storiche.

L'archiviazione:

```text
archived_at != NULL
```

li rende indisponibili per nuove analisi mantenendo intatte versioni e risultati precedenti.

---

## 6. Analysis lifecycle

L'unità centrale dell'esecuzione AI è `Analysis`.

Concettualmente:

```text
Document
 |
 +-- Analysis 1
 |    +-- schema version
 |    +-- AI runtime config
 |    +-- entities
 |    +-- extracted fields
 |
 +-- Analysis 2
      +-- schema version
      +-- AI runtime config
      +-- entities
      +-- extracted fields
```

Gli stati applicativi principali dell'analisi sono:

```text
QUEUED
PROCESSING
READY
ERROR
```

`Analysis.status` è destinato a diventare la sorgente definitiva dello stato dell'esecuzione AI.

`documents.status` è ancora presente come elemento transitorio dell'architettura e verrà rifattorizzato nelle fasi successive.

---

## 7. Quote di analisi

Le quote vengono applicate sul backend.

Una nuova esecuzione AI:

- riserva quota quando viene accodata;
- consuma quota quando termina con successo;
- non consuma definitivamente quota in caso di errore interno;
- non consuma nuova quota quando viene semplicemente riaperta un'analisi già pronta.

Il frontend mostra all'utente il numero di analisi disponibili.

---

## 8. Provenance

Le estrazioni conservano informazioni utili alla verifica:

- testo;
- label;
- confidence;
- pagina;
- offset globali;
- offset relativi alla pagina.

I campi strutturati conservano anche eventuali candidati alternativi.

Questo permette al viewer di collegare il risultato AI alla porzione del documento da cui deriva.

---

## 9. Architettura

```text
                     React
                       |
                       v
                 HTTP / JSON
                       |
                       v
                   FastAPI
                       |
          +------------+-------------+
          |                          |
          v                          v
     Application                 AI Pipeline
       Services                      |
          |                          v
          v                     GLiNER2.5
     Repositories
          |
          v
      SQLAlchemy
          |
          v
      PostgreSQL

PDF storage <---- Document Service / Pipeline
```

La struttura segue una separazione tra:

- API routes;
- Pydantic schema;
- dependencies;
- application services;
- repositories;
- ORM models;
- AI pipeline;
- storage;
- frontend API layer;
- React hooks;
- React components.

---

## 10. Stack tecnologico

### Frontend

- React 19
- TypeScript
- Vite
- React Router
- Fetch API
- CSS
- Oxlint
- Vitest / React Testing Library per il testing frontend

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy
- PostgreSQL
- JWT authentication
- PyMuPDF

### AI

- GLiNER2.5
- PyTorch / Transformers ecosystem
- inferenza self-hosted

### Infrastruttura

- Docker
- Docker Compose
- storage persistente
- PostgreSQL

---

## 11. Struttura del repository

```text
DocuEntitySeek/
|
+-- ai/
|   +-- notebooks/
|
+-- backend/
|   +-- app/
|   |   +-- api/
|   |   +-- core/
|   |   +-- db/
|   |   +-- repositories/
|   |   +-- schemas/
|   |   +-- services/
|   |   +-- ...
|   |
|   +-- sql/
|   +-- tests/
|   +-- requirements.txt
|   +-- README.md
|
+-- frontend/
|   +-- src/
|   |   +-- api/
|   |   +-- auth/
|   |   +-- components/
|   |   +-- hooks/
|   |   +-- pages/
|   |   +-- types/
|   |   +-- utils/
|   |
|   +-- package.json
|   +-- README.md
|
+-- docs/
|
+-- compose.yaml / Docker Compose configuration
+-- README.md
```

Dipendenze installate, ambienti virtuali, model cache, file `.env` e altri file generati non devono essere versionati.

---

## 12. Avvio locale

### Backend

Dalla directory:

```text
backend/
```

creare e attivare l'ambiente virtuale:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

installare le dipendenze:

```powershell
python -m pip install -r requirements.txt
```

configurare il file `.env` utilizzando `.env.example` come riferimento.

Avviare:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```powershell
cd frontend
npm ci
npm run dev
```

Il frontend di sviluppo viene normalmente esposto su:

```text
http://localhost:5173
```

La base URL deve puntare alle API FastAPI secondo la configurazione documentata in `frontend/.env.example`.

### Docker Compose

Il repository contiene uno stack Docker Compose per lo sviluppo.

Utilizzare la configurazione Compose e i relativi file `.env` del progetto per avviare i servizi previsti.

---

## 13. Database

Il modello PostgreSQL comprende, tra le altre, le tabelle:

```text
plans
users

extraction_schemas
extraction_schema_versions
entity_definitions
field_definitions

documents
document_pages

analyses
entity_occurrences
extracted_fields
field_candidates

ai_runtime_configs
```

Gli script SQL di bootstrap e aggiornamento si trovano in:

```text
backend/sql/
```

---

## 14. Sicurezza

Il backend applica:

- JWT;
- ownership delle risorse;
- controllo del piano;
- controllo delle quote;
- validazione backend dei PDF;
- validazione degli schema custom;
- CORS esplicito per il frontend di sviluppo;
- separazione tra ruolo e piano.

Gli schemi custom appartenenti ad altri utenti non vengono esposti.

L'AI viene eseguita nell'infrastruttura applicativa senza richiedere API commerciali di inferenza esterne.

Questo non sostituisce le misure di sicurezza infrastrutturali necessarie in produzione.

---

## 15. Limitazioni attuali

### Viewer

Il backend espone già risultati AI persistiti, ma il viewer React utilizza ancora in parte il precedente modello `DocumentAnalysis`.

Il prossimo refactoring collegherà direttamente il viewer a:

```text
AnalysisDetail.result
```

### Elaborazione sincrona

L'endpoint che avvia l'analisi mantiene attualmente aperta la richiesta HTTP durante l'esecuzione della pipeline.

È adeguato alla fase di sviluppo, ma prima del deployment verrà valutato un sistema di job/worker per l'inferenza pesante.

### OCR

I PDF costituiti esclusivamente da scansioni non vengono attualmente sottoposti a OCR.

La pipeline richiede testo digitale estraibile dal PDF.

### Dominio built-in

Lo schema built-in attuale deriva dal dominio Procurement.

Prima della release verrà valutata e validata una configurazione Base realmente generica.

---

## 16. Testing

### Backend

```powershell
cd backend
python -m pytest
```

Controllo sintattico:

```powershell
python -m compileall -q app
```

### Frontend

```powershell
cd frontend
npx tsc -b
npm run build
npm run lint
```

I test end-to-end completi della pipeline full-stack costituiscono una delle fasi successive.

---

## 17. Stato del progetto

| Area | Stato |
|---|---|
| Requisiti e user story | Implementati/documentati |
| React routing e UI | Implementati |
| FastAPI REST | Implementato |
| PostgreSQL / SQLAlchemy | Implementati |
| Autenticazione JWT | Implementata |
| Piani Base/Premium | Implementati |
| Quote giornaliere | Implementate |
| Upload PDF | Implementato |
| Storage documenti | Implementato |
| PyMuPDF | Integrato |
| Runtime configuration AI | Implementata |
| GLiNER2.5 provider | Integrato |
| NER long-context | Implementata |
| IE long-context | Implementata |
| Provenance | Implementata |
| Persistenza risultati AI | Implementata |
| Analysis API | Implementata |
| Analisi automatica dopo upload | Implementata |
| Aggiornamento stato documenti | Implementato |
| Schemi custom Premium | Implementati |
| Versionamento schema | Implementato |
| Duplicazione schema | Implementata |
| Archiviazione schema | Implementata |
| Viewer AI su API reale | In refactoring |
| Testing E2E completo | Da completare |
| Generalizzazione schema Base | Da completare |
| Deployment cloud | Da completare |

---

## 18. Prossime fasi

Il blocco successivo dello sviluppo riguarda il viewer reale:

1. collegamento diretto ad `AnalysisDetail.result`;
2. rendering delle pagine reali;
3. evidenziazione delle entità persistite;
4. filtri dinamici;
5. visualizzazione dei field strutturati;
6. provenance e candidati alternativi;
7. cronologia delle analisi;
8. rimozione progressiva del modello demo/legacy.

Successivamente verranno completati:

- test full-stack;
- generalizzazione dello schema Base;
- benchmark e ottimizzazione delle prestazioni;
- eventuale OCR;
- hardening sicurezza;
- deployment cloud;
- osservabilità e documentazione finale.

---

## 19. Principio architetturale

DocuEntitySeek separa intenzionalmente:

```text
MODELLO AI
≠
SCHEMA DI DOMINIO
≠
PIPELINE
≠
INTERFACCIA
```

L'obiettivo è permettere di cambiare dominio, schema o configurazione AI senza riscrivere la pipeline applicativa.