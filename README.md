
# DocuEntitySeek

**Document Intelligence Platform — Named Entity Recognition & Structured Information Extraction**

DocuEntitySeek è una piattaforma di Document Intelligence progettata per analizzare documenti complessi mediante tecniche di Natural Language Processing (NLP) e Intelligenza Artificiale.

Il progetto si concentra inizialmente sul dominio **Procurement**, con particolare riferimento a:

- Bandi di gara
- Disciplinari di gara
- Capitolati
- Contratti
- Documentazione amministrativa

L'obiettivo è trasformare documenti non strutturati in informazioni organizzate e verificabili, mantenendo il collegamento tra i risultati estratti e il documento originale.

> **Stato attuale:** frontend React con routing, richieste HTTP tramite Fetch API, custom hook, tipizzazione TypeScript, gestione di loading/error/empty state e dati JSON mock. La pipeline AI è stata già implementata come prototipo separato, con relativi risultati. Backend FastAPI, database e integrazione AI end-to-end non sono ancora implementati.

---

## 1. Obiettivi

Gli obiettivi principali di DocuEntitySeek sono:

1. Riconoscere automaticamente le entità rilevanti.
2. Estrarre informazioni strutturate secondo uno schema di dominio.
3. Evidenziare le entità direttamente nel testo.
4. Associare le estrazioni alle pagine originali.
5. Ridurre il lavoro manuale di analisi documentale.
6. Permettere la futura personalizzazione degli schemi di estrazione.
7. Integrare frontend, backend e modelli AI in un'applicazione full-stack.

Il sistema distingue due funzionalità principali:

- **Entity Discovery (NER):** riconoscimento delle entità nominate.
- **Field Extraction (IE):** estrazione di informazioni strutturate.

Ulteriori funzionalità di Information Retrieval potranno essere integrate successivamente.

---

## 2. Funzionalità principali

### 2.1 Entity Discovery

La Named Entity Recognition individua informazioni rilevanti all'interno del testo.

Lo schema Procurement prevede categorie come:

| Entità | Descrizione |
|---|---|
| ORGANIZZAZIONE | Enti, amministrazioni e aziende |
| PERSONA | Persone fisiche |
| LOCALITA | Luoghi e riferimenti geografici |
| IMPORTO | Importi monetari |
| DATA | Date e scadenze |
| ORA | Orari |
| RIFERIMENTO_NORMATIVO | Riferimenti legislativi |
| IDENTIFICATIVO_GARA | CIG, CUP, CPV e altri identificativi |
| CERTIFICAZIONE | Certificazioni e attestazioni |
| PRODOTTO_SERVIZIO | Prodotti, servizi e forniture |

Il viewer dimostrativo consente di evidenziare, filtrare e selezionare le entità.

### 2.2 Structured Field Extraction

La Field Extraction produce informazioni strutturate.

Tra i campi Procurement previsti rientrano:

- Stazione appaltante
- Oggetto gara
- CIG
- CUP
- CPV
- Tipo procedura
- Importo complessivo
- Importo base d'asta
- Durata contratto
- Scadenza offerte
- Termine chiarimenti
- Criterio di aggiudicazione
- Responsabile procedimento
- Luogo esecuzione

Il prototipo AI include anche ulteriori campi, come il numero dei lotti.

Le informazioni sono progettate per essere mostrate separatamente dalle annotazioni NER.

### 2.3 Document Viewer

Il viewer frontend attuale permette di:

- Visualizzare segmenti di testo annotati.
- Evidenziare le entità con colori differenti.
- Attivare o disattivare le categorie NER.
- Selezionare un'entità.
- Navigare tra le pagine disponibili nella demo.
- Consultare i campi strutturati.

Il viewer non visualizza ancora un PDF reale: riceve dati strutturati da un endpoint JSON mock.

### 2.4 Provenance

La pipeline AI sperimentale prevede la conservazione di:

- Testo estratto
- Categoria dell'entità
- Campo strutturato
- Confidence
- Offset globali
- Pagina sorgente
- Offset relativi alla pagina

Queste informazioni permetteranno di verificare le estrazioni nel documento originale.

Il contratto JSON attualmente usato dal frontend è semplificato rispetto ai risultati completi della pipeline AI.

---

## 3. Modello applicativo previsto

DocuEntitySeek prevede due livelli di utilizzo.

### Base

- Schema Procurement predefinito
- Entity Discovery
- Field Extraction
- Viewer annotato
- Limite applicativo previsto di 5 nuove analisi al giorno

### Premium

- Tutte le funzionalità Base
- Entità personalizzate
- Campi personalizzati
- Schemi di estrazione riutilizzabili
- Supporto a ulteriori domini documentali
- Assenza del limite giornaliero applicativo Base

La distinzione Base/Premium è attualmente illustrata nel frontend. Non esistono ancora autenticazione, autorizzazioni, sottoscrizioni o enforcement delle quote.

---

## 4. Stack tecnologico

### Frontend implementato

| Tecnologia | Ruolo |
|---|---|
| React 19 | UI |
| TypeScript | Tipizzazione statica |
| Vite 8 | Build e sviluppo |
| React Router 8 | Client-side routing |
| Fetch API | Richieste HTTP |
| React Hooks | Gestione stato ed effetti |
| CSS | Layout e componenti |
| Oxlint | Analisi statica |

### AI / NLP prototipale

- Python
- PyMuPDF
- GLiNER2.5
- Pandas
- NumPy
- Jupyter Notebook

Modello sperimentale:

`fastino/gliner2.5-multi-v1`

### Backend previsto

- Python
- FastAPI
- API REST

### Database previsto

- PostgreSQL
- SQLAlchemy

### Infrastruttura prevista

- Docker
- Docker Compose
- Deployment cloud

---

## 5. Architettura attuale

Il passaggio 9 introduce un livello API nel frontend.

```text
                 REACT FRONTEND
                       |
                       v
                 React Pages
                       |
                       v
                  Custom Hooks
                       |
                       v
                   API Layer
                       |
                       v
                Fetch API (GET)
                       |
                       v
             Mock HTTP Endpoints
             Vite public/mock-api/
                       |
                       v
                  JSON Response
                       |
                       v
               Typed Application
                     State
                       |
                       v
                 React Components
```

### Separazione delle responsabilità

**Pages**

Gestiscono la presentazione delle pagine e i differenti stati dell'interfaccia.

**Custom Hooks**

Gestiscono richieste asincrone, dati, loading, errori e retry.

**API Layer**

Contiene le funzioni che effettuano le richieste HTTP.

**Types**

Definiscono le strutture dati attese.

**Mock API**

Simula un servizio remoto mediante file JSON statici serviti da Vite.

Questa separazione prepara il frontend alla futura integrazione con FastAPI.

---

## 6. Pipeline AI

### Flusso

```text
PDF
 |
 v
PyMuPDF
 |
 v
Estrazione testo e pagine
 |
 v
GLiNER2.5
 |
 +-----------------------+
 |                       |
 v                       v
Entity Discovery     Field Extraction
 |                       |
 v                       v
Normalizzazione      Normalizzazione
 |                       |
 v                       v
Deduplicazione       Gestione candidati
 |                       |
 v                       v
Risoluzione overlap  Selezione valori
 |                       |
 +-----------+-----------+
             |
             v
      Risultati strutturati
       con provenance
```

### Configurazione sperimentale

| Parametro | Valore |
|---|---|
| Model | fastino/gliner2.5-multi-v1 |
| Chunk size | 512 |
| Chunk overlap | 96 |
| Batch size | 8 |
| Entity threshold | 0.70 |
| Field threshold | 0.50 |
| Model overlap policy | allow |
| Viewer overlap policy | flat_confidence |

La pipeline utilizza:

- `extract_entities_long()`
- `extract_json_long()`

---

## 7. Elaborazione AI self-hosted e riservatezza dei dati

DocuEntitySeek è progettato secondo un approccio self-hosted AI, privilegiando l'esecuzione dei modelli di Intelligenza Artificiale direttamente nell'infrastruttura applicativa, senza dipendere da API di inferenza di provider esterni, come OpenAI.

La pipeline sperimentale utilizza **GLiNER2.5** per le attività di Named Entity Recognition (NER) e Structured Information Extraction (IE).

Questa scelta architetturale offre diversi vantaggi:

- **Riservatezza dei documenti:** l'elaborazione AI può avvenire all'interno dell'infrastruttura applicativa, senza trasmettere i contenuti a servizi esterni di inferenza.

- **Maggiore controllo sui dati:** il gestore della piattaforma può definire le politiche di conservazione, accesso ed eliminazione dei documenti.

- **Indipendenza dai provider AI:** le funzionalità di analisi non richiedono l'utilizzo di API commerciali per ogni richiesta.

- **Prevedibilità dei costi:** l'inferenza non comporta tariffe a consumo per token o chiamate API esterne, pur richiedendo risorse computazionali e infrastrutturali proprie.

### 7.1 Gestione dei dati degli utenti

L'esecuzione locale del modello AI non implica che i documenti rimangano sul dispositivo dell'utente.

Nell'architettura full-stack prevista, i documenti caricati saranno trasmessi al backend di DocuEntitySeek ed eventualmente conservati nell'infrastruttura server, secondo le politiche di persistenza e conservazione che verranno definite.

L'obiettivo è mantenere l'elaborazione AI sotto il controllo dell'infrastruttura applicativa, limitando la condivisione dei contenuti con servizi di inferenza di terze parti.

### 7.2 Sicurezza e limitazioni

L'adozione di modelli AI self-hosted costituisce una scelta architetturale favorevole alla riservatezza e al controllo dei dati, ma non garantisce automaticamente la sicurezza delle informazioni o la conformità alla normativa sulla protezione dei dati personali.

La futura implementazione dovrà prevedere adeguati meccanismi di autenticazione, autorizzazione, isolamento dei dati tra utenti, cifratura delle comunicazioni, protezione dello storage e gestione della conservazione e cancellazione dei documenti.

**Stato di implementazione:** attualmente l'inferenza AI è disponibile come prototipo sperimentale in ambiente Jupyter. L'integrazione del modello all'interno del backend applicativo e i relativi meccanismi di sicurezza sono previsti nelle successive fasi di sviluppo.

---

## 8. Struttura del repository

```text
DocuEntitySeek/
|
+-- backend/
|   +-- [backend applicativo da implementare]
|
+-- docs/
|   +-- DocuEntitySeek_Requisiti_Funzionali.pdf
|   +-- DocuEntitySeek_User_Story.pdf
|
+-- frontend/
|   |
|   +-- public/
|   |   +-- mock-api/
|   |       +-- documents.json
|   |       +-- documents/
|   |           +-- disciplinare-palermo-2027.json
|   |           +-- capitolato-servizi-cloud.json
|   |           +-- contratto-servizio-demo.json
|   |
|   +-- src/
|   |   +-- api/
|   |   |   +-- http.ts
|   |   |   +-- documentsApi.ts
|   |   |
|   |   +-- assets/
|   |   |
|   |   +-- components/
|   |   |   +-- analysis/
|   |   |   +-- feedback/
|   |   |   +-- layout/
|   |   |
|   |   +-- hooks/
|   |   |   +-- useDocuments.ts
|   |   |   +-- useDocumentDetail.ts
|   |   |   +-- useDocumentTitle.ts
|   |   |
|   |   +-- pages/
|   |   |
|   |   +-- types/
|   |   |   +-- document.ts
|   |   |   +-- analysis.ts
|   |   |
|   |   +-- App.tsx
|   |   +-- App.css
|   |   +-- main.tsx
|   |   +-- index.css
|   |
|   +-- .env.example
|   +-- package.json
|   +-- package-lock.json
|   +-- README.md
|
+-- .gitignore
+-- README.md
```

Sono omesse dalla rappresentazione le dipendenze installate, gli ambienti virtuali e i file generati automaticamente.

---

## 9. Avvio locale

### Requisiti

- Node.js compatibile con le dipendenze installate
- npm
- Python per il notebook AI
- Git consigliato

Per lo specifico stack frontend, utilizzare preferibilmente Node.js 22.22 o successivo: React Router 8.5.1 dichiara Node.js >=22.22.0 come requisito.

### Installazione frontend

Aprire un terminale nella directory principale del progetto.

```bash
cd frontend
npm ci
```

### Configurazione API

Creare, se assente, `frontend/.env.local` con:

```env
VITE_API_BASE_URL=/mock-api
```

Il file `.env.example` contiene la configurazione di riferimento.

### Avvio

```bash
npm run dev
```

Aprire l'indirizzo mostrato da Vite, normalmente:

`http://localhost:5173`

### Build

```bash
npm run build
```

### Controllo statico

```bash
npm run lint
```

### Preview della build

```bash
npm run preview
```

---

## 10. React API — Passaggio 9

Il passaggio 9 introduce la comunicazione HTTP nel frontend.

### 10.1 HTTP Client

File:

`frontend/src/api/http.ts`

Responsabilità:

- Leggere la base URL.
- Eseguire richieste GET tramite `fetch`.
- Gestire risposte HTTP non riuscite.
- Deserializzare risposte JSON.
- Applicare i tipi TypeScript.
- Supportare AbortSignal.
- Normalizzare gli errori.

Elementi principali:

- `API_BASE_URL`
- `HttpError`
- `RequestError`
- `getJson<T>()`
- `isAbortError()`
- `normalizeRequestError()`

La tipizzazione TypeScript non costituisce validazione runtime del contenuto JSON.

### 10.2 Document API

File:

`frontend/src/api/documentsApi.ts`

Espone:

- `getDocuments(signal?)`
- `getDocumentDetail(documentId, signal?)`

Entrambe le funzioni utilizzano il client HTTP condiviso.

### 10.3 Custom Hooks

File:

- `frontend/src/hooks/useDocuments.ts`
- `frontend/src/hooks/useDocumentDetail.ts`

Gestiscono:

- Esecuzione delle richieste.
- Stato di caricamento.
- Dati ricevuti.
- Errori.
- Retry.
- Annullamento delle richieste durante il cleanup.

### 10.4 Feedback UI

Componenti:

- `LoadingState`
- `ErrorState`

Le pagine gestiscono anche situazioni senza dati disponibili.

### 10.5 Mock API

Endpoint:

```http
GET /mock-api/documents.json
```

Restituisce l'elenco dei documenti.

```http
GET /mock-api/documents/{documentId}.json
```

Restituisce i dettagli di un documento e l'eventuale analisi.

I file JSON sono serviti staticamente da Vite.

**Non esiste ancora un backend HTTP applicativo.**

---

## 11. Contratti dei dati

### DocumentSummary

Contiene:

- id
- name
- category
- pages
- status
- uploadedAt

Gli stati possibili sono:

- READY
- PROCESSING
- ERROR

### DocumentDetailResponse

Contiene:

- `document`: metadati del documento.
- `analysis`: analisi del documento oppure `null`.

### DocumentAnalysis

Contiene:

- `entityDefinitions`
- `pages`
- `extractedFields`

La definizione TypeScript è presente in:

`frontend/src/types/analysis.ts`

Questi tipi rappresentano il contratto attuale della demo. Potranno essere estesi durante l'integrazione backend.

---

## 12. Frontend

### Route implementate

| Route | Pagina |
|---|---|
| `/` | HomePage |
| `/documents` | DocumentsPage |
| `/documents/:documentId` | DocumentDetailPage |
| `/schemas` | SchemasPage |
| `*` | NotFoundPage |

### Documenti dimostrativi

Il progetto contiene tre documenti mock:

| Documento | Stato |
|---|---|
| Disciplinare_di_gara.pdf | READY |
| Capitolato_servizi_cloud.pdf | PROCESSING |
| Contratto_servizio_demo.pdf | ERROR |

Il documento READY presenta due pagine annotate dimostrative, numerate 12 e 13.

Non vengono caricati o elaborati PDF reali dal frontend.

---

## 13. Stato di sviluppo

| Componente | Stato |
|---|---|
| Requisiti funzionali | Documentati |
| User Story | Documentate |
| Pipeline AI | Prototipo notebook |
| Analisi e risultati AI | Prototipo notebook |
| Routing React | Implementato |
| Landing page | Implementata |
| Schema Procurement UI | Implementato |
| Document Viewer | Demo funzionante |
| API Layer frontend | Implementato |
| Fetch API GET | Implementato |
| Tipizzazione risposte | Implementata |
| Custom hook richieste | Implementati |
| Loading/error/empty state | Implementati |
| Retry richieste | Implementato |
| AbortController | Implementato |
| Endpoint JSON mock | Implementati |
| Backend FastAPI | Da implementare |
| Database PostgreSQL | Da implementare |
| Upload documenti | Da implementare |
| Analisi AI via API | Da implementare |
| Autenticazione | Da implementare |
| Gestione Base/Premium | Da implementare |
| Testing automatico dedicato | Da implementare |
| Docker Compose | Da implementare |
| Deployment cloud | Da implementare |

---

## 14. Prossimi sviluppi

Le attività successive seguiranno un approccio incrementale.

### Evoluzione frontend

- Miglioramento dell'architettura React.
- Introduzione di ulteriori componenti riutilizzabili.
- Gestione dello stato applicativo quando necessaria.
- Testing dei componenti.
- Miglioramento dell'accessibilità.

### Backend

- Creazione del progetto FastAPI.
- Definizione delle API REST.
- Persistenza dei documenti.
- Collegamento con PostgreSQL.
- Integrazione della pipeline AI.
- Autenticazione e autorizzazione.

### Integrazione

- Sostituzione degli endpoint mock.
- Upload PDF.
- Analisi tramite backend.
- Recupero dei risultati reali.
- Gestione degli schemi.
- Visualizzazione della provenance.
- Testing end-to-end.

### Deployment

- Dockerizzazione dei componenti.
- Docker Compose.
- Configurazione degli ambienti.
- Pubblicazione dell'applicazione.

---

## 15. Documentazione

Documentazione di progetto:

- `docs/DocuEntitySeek_Requisiti_Funzionali.pdf`
- `docs/DocuEntitySeek_User_Story.pdf`

Documentazione frontend:

- [frontend/README.md](frontend/README.md)

---

## 16. Affidabilità e limiti

I risultati prodotti dai modelli AI possono contenere:

- Falsi positivi.
- Entità non riconosciute.
- Informazioni incomplete.
- Valori ambigui.
- Riferimenti non corretti.

Il sistema è progettato per favorire la verificabilità delle informazioni.

I dati mock del frontend hanno finalità dimostrative e non rappresentano risultati di analisi automatica su PDF caricati dall'utente.

Le informazioni estratte dall'AI richiederanno sempre appropriate verifiche.

---

## 17. Finalità del progetto

DocuEntitySeek è un progetto di sviluppo software e sperimentazione orientato alla realizzazione di una piattaforma full-stack di Document Intelligence.

Lo sviluppo procede per passaggi incrementali, con particolare attenzione alla separazione delle responsabilità e alla manutenibilità.
