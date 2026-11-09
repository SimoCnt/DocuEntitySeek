
# DocuEntitySeek — Frontend

Frontend React di **DocuEntitySeek**, piattaforma per l'analisi intelligente dei documenti mediante Named Entity Recognition (NER) e Structured Information Extraction (IE).

L'applicazione è sviluppata con React, TypeScript e Vite.

Il frontend presenta un'architettura modulare e utilizza richieste HTTP per recuperare i documenti e i relativi risultati di analisi.

> **Stato attuale** implementati Fetch API, API Layer, custom hook per le richieste, tipizzazione TypeScript, loading state, error handling, retry, AbortController e mock API tramite file JSON statici. Non è ancora presente l'integrazione con FastAPI.

---

## 1. Stack tecnologico

| Tecnologia | Versione | Utilizzo |
|---|---|---|
| React | 19 | Componenti UI |
| TypeScript | 7 | Tipizzazione |
| Vite | 8 | Development server e build |
| React Router | 8 | Client-side routing |
| Fetch API | Browser API | Comunicazione HTTP |
| CSS | - | Layout responsive |
| Oxlint | 1 | Linting |

### Prerequisiti

- Node.js 22.22 o successivo
- npm

La versione minima indicata soddisfa il requisito Node.js dichiarato da React Router 8.5.1.

---

## 2. Installazione

Posizionarsi nella directory:

```text
DocuEntitySeek/frontend
```

Installare le dipendenze:

```bash
npm ci
```

### Configurare l'ambiente

Creare il file `.env.local`, se non presente.

Contenuto:

```env
VITE_API_BASE_URL=/mock-api
```

La variabile definisce il percorso base utilizzato dal client HTTP.

Il file `.env.example` documenta la configurazione.

### Avviare il progetto

```bash
npm run dev
```

Aprire l'indirizzo fornito dal terminale, normalmente:

`http://localhost:5173`

### Comandi disponibili

| Comando | Descrizione |
|---|---|
| `npm run dev` | Avvia Vite |
| `npm run build` | Type checking e build |
| `npm run preview` | Preview build |
| `npm run lint` | Controllo con Oxlint |

---

## 3. Struttura del progetto

```text
frontend/
|
+-- public/
|   +-- favicon.svg
|   +-- icons.svg
|   |
|   +-- mock-api/
|       +-- documents.json
|       +-- documents/
|           +-- disciplinare-palermo-2027.json
|           +-- capitolato-servizi-cloud.json
|           +-- contratto-servizio-demo.json
|
+-- src/
|   |
|   +-- api/
|   |   +-- http.ts
|   |   +-- documentsApi.ts
|   |
|   +-- assets/
|   |   +-- hero.png
|   |   +-- react.svg
|   |   +-- vite.svg
|   |
|   +-- components/
|   |   |
|   |   +-- analysis/
|   |   |   +-- AnalysisDemoSection.tsx
|   |   |   +-- AnnotatedDocumentMock.tsx
|   |   |   +-- EntityFilterList.tsx
|   |   |   +-- ExtractedFieldsPanel.tsx
|   |   |
|   |   +-- feedback/
|   |   |   +-- LoadingState.tsx
|   |   |   +-- ErrorState.tsx
|   |   |
|   |   +-- layout/
|   |   |   +-- AppLayout.tsx
|   |   |
|   |   +-- Header.tsx
|   |   +-- Footer.tsx
|   |   +-- HeroSection.tsx
|   |   +-- FeaturesSection.tsx
|   |   +-- FeatureCard.tsx
|   |   +-- PlansSection.tsx
|   |   +-- PlanCard.tsx
|   |
|   +-- hooks/
|   |   +-- useDocumentTitle.ts
|   |   +-- useDocuments.ts
|   |   +-- useDocumentDetail.ts
|   |
|   +-- pages/
|   |   +-- HomePage.tsx
|   |   +-- DocumentsPage.tsx
|   |   +-- DocumentDetailPage.tsx
|   |   +-- SchemasPage.tsx
|   |   +-- NotFoundPage.tsx
|   |
|   +-- types/
|   |   +-- document.ts
|   |   +-- analysis.ts
|   |
|   +-- App.tsx
|   +-- App.css
|   +-- main.tsx
|   +-- index.css
|
+-- .env.example
+-- .env.local
+-- .gitignore
+-- .oxlintrc.json
+-- index.html
+-- package.json
+-- package-lock.json
+-- vite.config.ts
+-- tsconfig.json
+-- tsconfig.app.json
+-- tsconfig.node.json
+-- README.md
```

`.env.local` è una configurazione locale ignorata da Git.

---

## 4. Architettura frontend

L'applicazione è organizzata secondo una separazione delle responsabilità.

```text
React Page
    |
    v
Custom Hook
    |
    v
Domain API
    |
    v
HTTP Client
    |
    v
Fetch API
    |
    v
Mock HTTP Endpoint
    |
    v
JSON Response
    |
    v
Custom Hook State
    |
    v
React Page
    |
    v
UI Components
```

### Pages

Definiscono la presentazione delle schermate.

### Components

Contengono elementi riutilizzabili e componenti del dominio.

### Hooks

Gestiscono lo stato applicativo e gli effetti.

### API

Centralizzano la comunicazione HTTP.

### Types

Definiscono le strutture dati.

### Mock API

Fornisce dati dimostrativi attraverso richieste HTTP.

Questa architettura permette di mantenere separata la UI dalle funzioni di accesso ai dati.

---

## 5. Routing

Il routing è configurato in:

`src/App.tsx`

React Router gestisce le seguenti rotte:

| Route | Componente |
|---|---|
| `/` | HomePage |
| `/documents` | DocumentsPage |
| `/documents/:documentId` | DocumentDetailPage |
| `/schemas` | SchemasPage |
| `*` | NotFoundPage |

### Layout condiviso

File:

`src/components/layout/AppLayout.tsx`

Struttura:

```text
AppLayout
 |
 +-- Header
 |
 +-- main
 |    |
 |    +-- Outlet
 |
 +-- Footer
```

Il componente `Outlet` permette alle pagine di condividere il layout.

---

## 6. API Layer

Il passaggio 9 introduce un livello dedicato alla comunicazione HTTP.

Directory:

`src/api/`

### 6.1 http.ts

Contiene il client HTTP condiviso.

Responsabilità:

- Configurazione della base URL.
- Esecuzione delle richieste GET.
- Deserializzazione del JSON.
- Gestione delle risposte HTTP non riuscite.
- Normalizzazione degli errori.
- Supporto ad AbortSignal.

#### API_BASE_URL

La configurazione è recuperata tramite:

```ts
import.meta.env.VITE_API_BASE_URL
```

Se non viene configurata, è utilizzato il percorso di fallback `/mock-api`.

Gli slash finali vengono rimossi dalla base URL.

#### HttpError

Classe che estende `Error`.

Contiene:

- `message`
- `status`
- `url`

Viene utilizzata quando la risposta HTTP non è riuscita.

#### RequestError

Tipo che rappresenta gli errori utilizzati dall'interfaccia.

```ts
type RequestError = {
    message: string
    status?: number
}
```

#### getJson<T>()

Funzione asincrona generica che effettua una richiesta GET e restituisce il risultato tipizzato.

Firma:

```ts
getJson<T>(
    path: string,
    signal?: AbortSignal
): Promise<T>
```

Funzionamento:

1. Compone l'URL.
2. Esegue `fetch`.
3. Richiede una risposta JSON.
4. Verifica `response.ok`.
5. Genera un `HttpError` per una risposta HTTP non riuscita.
6. Legge il body mediante `response.json()`.
7. Restituisce il dato come tipo `T`.

**Nota:** il tipo generico `T` non valida a runtime la struttura della risposta. La validazione runtime dovrà essere valutata quando saranno disponibili API esterne reali.

#### normalizeRequestError()

Trasforma un errore generico in un oggetto `RequestError`.

Gestisce:

- Errori HTTP applicativi.
- Errori JavaScript.
- Valori inattesi.

#### isAbortError()

Riconosce gli errori di annullamento generati da una richiesta interrotta.

Viene utilizzata dai custom hook per evitare di mostrare errori dovuti alla cancellazione intenzionale di una richiesta.

---

## 7. Document API

File:

`src/api/documentsApi.ts`

Contiene le funzioni dedicate al recupero dei documenti.

### getDocuments()

Firma:

```ts
getDocuments(
    signal?: AbortSignal
)
```

Effettua la richiesta:

```http
GET /mock-api/documents.json
```

Restituisce:

```ts
Promise<DocumentSummary[]>
```

### getDocumentDetail()

Firma:

```ts
getDocumentDetail(
    documentId: string,
    signal?: AbortSignal
)
```

Effettua una richiesta al percorso:

```http
GET /mock-api/documents/{documentId}.json
```

Restituisce:

```ts
Promise<DocumentDetailResponse>
```

L'identificativo viene codificato mediante `encodeURIComponent()` prima di essere inserito nel percorso.

### Perché separare documentsApi da http?

`http.ts` contiene funzionalità HTTP generiche.

`documentsApi.ts` contiene operazioni specifiche del dominio documentale.

Questa distinzione evita di inserire direttamente `fetch` nei componenti React.

---

## 8. Custom Hooks

### 8.1 useDocuments

File:

`src/hooks/useDocuments.ts`

Si occupa del recupero dell'elenco dei documenti.

Restituisce:

```ts
{
    documents,
    isLoading,
    error,
    reload
}
```

#### documents

Contiene i documenti ricevuti dall'API.

#### isLoading

Indica se è in corso una richiesta.

#### error

Contiene l'eventuale errore normalizzato.

#### reload

Permette di ripetere la richiesta.

### Flusso

```text
Mount component
      |
      v
useEffect
      |
      v
AbortController
      |
      v
setIsLoading(true)
      |
      v
getDocuments()
      |
      +------------------+
      |                  |
      v                  v
   Success             Error
      |                  |
      v                  v
setDocuments()       setError()
      |                  |
      +--------+---------+
               |
               v
       setIsLoading(false)
```

Nel cleanup viene invocato `controller.abort()`.

### 8.2 useDocumentDetail

File:

`src/hooks/useDocumentDetail.ts`

Recupera i dettagli e l'analisi di un singolo documento.

Parametri:

```ts
useDocumentDetail(documentId)
```

Restituisce:

```ts
{
    data,
    isLoading,
    error,
    reload
}
```

Il recupero viene ripetuto quando cambia:

- `documentId`
- `reloadToken`

Il precedente risultato viene azzerato all'avvio di una nuova richiesta valida.

Il cleanup annulla la richiesta precedente.

### 8.3 useDocumentTitle

File:

`src/hooks/useDocumentTitle.ts`

Aggiorna il titolo della pagina nel browser utilizzando `useEffect`.

Durante il cleanup ripristina il titolo precedente.

---

## 9. Tipizzazione TypeScript

Directory:

`src/types/`

### 9.1 document.ts

Definisce i contratti relativi ai documenti.

#### DocumentStatus

```ts
type DocumentStatus =
    | 'READY'
    | 'PROCESSING'
    | 'ERROR'
```

#### DocumentSummary

```ts
type DocumentSummary = {
    id: string
    name: string
    category: string
    pages: number
    status: DocumentStatus
    uploadedAt: string
}
```

#### DocumentDetailResponse

```ts
type DocumentDetailResponse = {
    document: DocumentSummary
    analysis: DocumentAnalysis | null
}
```

### 9.2 analysis.ts

Contiene i tipi dell'analisi.

#### EntityDefinition

```ts
type EntityDefinition = {
    label: string
    color: string
}
```

#### TextSegment

Un segmento può essere:

- Testo normale.
- Entità annotata.

#### DocumentPage

Rappresenta una pagina di testo segmentato.

#### ExtractedField

Rappresenta un campo estratto.

Contiene:

- id
- label
- value
- page
- confidence
- status

#### ExtractedFieldStatus

Stati supportati:

- EXTRACTED
- AMBIGUOUS
- NOT_FOUND
- ERROR

#### DocumentAnalysis

```ts
type DocumentAnalysis = {
    entityDefinitions: EntityDefinition[]
    pages: DocumentPage[]
    extractedFields: ExtractedField[]
}
```

I tipi costituiscono il contratto frontend attuale.

---

## 10. Mock API

Directory:

`public/mock-api/`

I file JSON simulano le risposte di un backend.

### 10.1 Elenco documenti

File:

`public/mock-api/documents.json`

Contiene tre documenti:

| ID | Stato |
|---|---|
| disciplinare-palermo-2027 | READY |
| capitolato-servizi-cloud | PROCESSING |
| contratto-servizio-demo | ERROR |

### 10.2 Dettaglio documento

Directory:

`public/mock-api/documents/`

Ogni documento ha un file JSON associato.

La struttura prevista è:

```json
{
    "document": {
        "id": "example",
        "name": "Example.pdf",
        "category": "Documento",
        "pages": 10,
        "status": "PROCESSING",
        "uploadedAt": "09/11/2026"
    },
    "analysis": null
}
```

Quando l'analisi è disponibile, `analysis` contiene:

- entityDefinitions
- pages
- extractedFields

### 10.3 Documento READY

Il file:

`disciplinare-palermo-2027.json`

contiene una demo completa di NER e Field Extraction.

Include:

- Definizioni delle entità.
- Due pagine di testo annotato.
- Campi strutturati.

Le pagine dimostrative hanno numerazione 12 e 13; non costituiscono la rappresentazione integrale delle 48 pagine dichiarate nei metadati.

### 10.4 Stati non READY

I documenti PROCESSING ed ERROR hanno:

```json
{
    "analysis": null
}
```

Non presentano quindi un'analisi disponibile.

---

## 11. Componenti feedback

Directory:

`src/components/feedback/`

### LoadingState

File:

`LoadingState.tsx`

Mostra:

- Spinner.
- Messaggio di caricamento.
- Attributo `role="status"`.

Esempio:

```tsx
<LoadingState
    message="Caricamento dei documenti..."
/>
```

### ErrorState

File:

`ErrorState.tsx`

Mostra:

- Titolo dell'errore.
- Messaggio.
- Pulsante Riprova, quando viene fornita una callback.
- Attributo `role="alert"`.

Esempio:

```tsx
<ErrorState
    message={error.message}
    onRetry={reload}
/>
```

Il pulsante richiama la funzione `reload` del custom hook.

---

## 12. DocumentsPage

File:

`src/pages/DocumentsPage.tsx`

La pagina utilizza:

```ts
useDocuments()
```

per recuperare i documenti.

### Stati gestiti

#### Loading

Durante la richiesta viene mostrato `LoadingState`.

#### Error

Se la richiesta fallisce, viene mostrato `ErrorState`.

Il pulsante Riprova permette di ripetere la chiamata.

#### Empty

Se la risposta contiene un array vuoto, viene mostrato un messaggio di assenza documenti.

#### Success

I documenti sono visualizzati in una griglia di card.

Ogni card mostra:

- Categoria.
- Nome del documento.
- Numero di pagine.
- Data di caricamento.
- Stato.

I documenti READY possono essere aperti.

I documenti PROCESSING ed ERROR mostrano un pulsante disabilitato.

---

## 13. DocumentDetailPage

File:

`src/pages/DocumentDetailPage.tsx`

La pagina legge il parametro `documentId` dalla route mediante `useParams()`.

Utilizza:

```ts
useDocumentDetail(documentId)
```

per richiedere i dati.

### Stati gestiti

#### Loading

Visualizza `LoadingState`.

#### HTTP 404

Mostra un messaggio dedicato quando il documento non viene trovato.

#### Errore generico

Visualizza `ErrorState` e permette di ripetere la richiesta.

#### Analisi non disponibile

Se il documento non è READY oppure `analysis` è `null`, viene mostrato un messaggio dedicato.

#### Analisi disponibile

Viene renderizzato:

```tsx
<AnalysisDemoSection
    key={document.id}
    documentName={document.name}
    analysis={analysis}
/>
```

L'utilizzo della chiave basata sull'identificativo permette di reinizializzare lo stato locale del viewer quando cambia documento.

---

## 14. Componenti di analisi

Directory:

`src/components/analysis/`

### AnalysisDemoSection

Gestisce:

- Pagina selezionata.
- Categorie NER attive.
- Entità selezionata.
- Navigazione.
- Filtri.

Riceve i dati tramite props e non esegue direttamente richieste HTTP.

### AnnotatedDocumentMock

Visualizza il testo annotato.

Le entità vengono rappresentate come elementi selezionabili con colore associato alla categoria.

### EntityFilterList

Permette di:

- Attivare una categoria.
- Disattivare una categoria.
- Mostrare tutte le categorie.
- Nascondere tutte le categorie.

### ExtractedFieldsPanel

Visualizza:

- Nome del campo.
- Valore.
- Pagina sorgente, se disponibile.
- Stato dell'estrazione.

La confidence è presente nel contratto dati, ma non viene visualizzata dal componente attuale.

---

## 15. Pagine aggiuntive

### HomePage

Contiene:

- HeroSection
- FeaturesSection
- PlansSection

### SchemasPage

Presenta:

- Schema Procurement.
- Categorie NER previste.
- Campi strutturati.
- Funzionalità Premium pianificate.

L'editor Premium non è ancora utilizzabile.

### NotFoundPage

Gestisce le rotte non riconosciute.

---

## 16. Gestione richieste asincrone

Il frontend utilizza `async/await` e Promise.

### Flusso standard

1. Il componente viene montato.
2. Il custom hook avvia un effetto.
3. Viene creato un AbortController.
4. Lo stato loading viene attivato.
5. Il servizio API esegue la richiesta GET.
6. La risposta viene verificata.
7. Il JSON viene letto e tipizzato.
8. Lo stato React viene aggiornato.
9. Il loading viene disattivato.

### Error handling

Gli errori HTTP vengono rappresentati da `HttpError`.

Gli errori vengono convertiti in `RequestError` prima di essere mostrati nell'interfaccia.

### AbortController

Le richieste possono essere annullate quando:

- Il componente viene smontato.
- Cambia il documento richiesto.
- L'effetto viene rieseguito.

L'annullamento evita che una richiesta precedente aggiorni normalmente un componente dopo il cleanup.

### Retry

Entrambi i custom hook espongono `reload()`.

La funzione incrementa un contatore interno che provoca la riesecuzione dell'effetto.

---

## 17. Test manuali

I seguenti test possono essere eseguiti in locale.

### Test 1 — Avvio

```bash
npm run dev
```

Verificare l'apertura della homepage.

### Test 2 — Elenco documenti

Aprire:

`http://localhost:5173/documents`

Risultato previsto:

- Richiesta GET a `/mock-api/documents.json`.
- Comparsa delle tre card.
- Visualizzazione dei relativi stati.

### Test 3 — Dettaglio documento

Aprire:

`http://localhost:5173/documents/disciplinare-palermo-2027`

Risultato previsto:

- Richiesta GET al JSON di dettaglio.
- Visualizzazione del viewer.
- Visualizzazione delle entità.
- Visualizzazione dei campi estratti.

### Test 4 — Documento inesistente

Aprire:

`http://localhost:5173/documents/documento-inesistente`

Risultato previsto:

- Richiesta a un endpoint inesistente.
- Gestione del relativo errore HTTP 404.
- Messaggio Documento non trovato.

### Test 5 — Errore HTTP

Configurare temporaneamente:

```env
VITE_API_BASE_URL=/percorso-inesistente
```

Riavviare Vite.

Aprire la pagina documenti.

Risultato previsto:

- Fallimento della richiesta.
- Visualizzazione di ErrorState.
- Disponibilità del pulsante Riprova.

Ripristinare successivamente:

```env
VITE_API_BASE_URL=/mock-api
```

### Test 6 — Build

```bash
npm run build
```

### Test 7 — Lint

```bash
npm run lint
```

I test manuali non sostituiscono una suite automatizzata.

---

## 18. Integrazione backend futura

L'architettura è predisposta per sostituire le Mock API con servizi FastAPI.

### Architettura prevista

```text
React Pages
     |
     v
Custom Hooks
     |
     v
Domain API Layer
     |
     v
HTTP Client
     |
     v
FastAPI REST Backend
     |
     +------------------+
     |                  |
     v                  v
PostgreSQL          AI Pipeline
                    PyMuPDF
                    GLiNER2.5
```

Per l'integrazione saranno necessari:

- Contratti API definitivi.
- Configurazione della base URL backend.
- Endpoint per i documenti.
- Endpoint per l'upload.
- Endpoint per le analisi.
- Gestione degli stati di elaborazione.
- Gestione degli errori backend.
- Autenticazione.
- Eventuale configurazione CORS.
- Validazione delle risposte.

I servizi attuali costituiscono la base didattica, non un'integrazione già disponibile.

---

## 19. Stato di sviluppo

| Funzionalità | Stato |
|---|---|
| React | Implementato |
| TypeScript | Configurato |
| Vite | Configurato |
| React Router | Implementato |
| Layout condiviso | Implementato |
| Landing page | Implementata |
| Elenco documenti | Implementato |
| Dettaglio documento | Implementato |
| Viewer NER | Demo |
| Filtri NER | Implementati |
| Sidebar campi | Demo |
| API Layer | Implementato |
| HTTP Client | Implementato |
| Fetch GET | Implementato |
| Tipi response | Implementati |
| Custom Hooks API | Implementati |
| Loading State | Implementato |
| Error State | Implementato |
| Empty State | Implementato |
| HTTP 404 handling | Implementato |
| Retry | Implementato |
| AbortController | Implementato |
| Mock JSON API | Implementata |
| FastAPI Integration | Da implementare |
| Upload PDF | Da implementare |
| Analisi AI reale | Da integrare |
| Autenticazione | Da implementare |
| Schemi personalizzati | Da implementare |
| Test automatizzati | Da implementare |
| Deployment | Da implementare |

---

## 20. Prossimi sviluppi

Le attività frontend successive comprenderanno:

1. Approfondimento di componenti React avanzati.
2. Miglioramento della riutilizzabilità del codice.
3. Gestione di stati applicativi più complessi.
4. Introduzione di ulteriori custom hook quando necessari.
5. Integrazione con il backend FastAPI.
6. Sostituzione dei file JSON mock.
7. Gestione dell'upload PDF.
8. Recupero dei risultati della pipeline AI.
9. Autenticazione e rotte protette.
10. Testing automatico.
11. Ottimizzazione e deployment.

L'evoluzione seguirà il piano di sviluppo incrementale di DocuEntitySeek.

---

## 21. Documentazione correlata

README principale:

`../README.md`

Requisiti funzionali:

`../docs/DocuEntitySeek_Requisiti_Funzionali.pdf`

User Story:

`../docs/DocuEntitySeek_User_Story.pdf`

Notebook AI:

`../ai/notebooks/Extraction_Pipeline.ipynb`

---
