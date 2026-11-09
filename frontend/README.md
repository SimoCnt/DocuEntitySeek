
# DocuEntitySeek — Frontend

Frontend di **DocuEntitySeek**, piattaforma di Document Intelligence dedicata al riconoscimento di entità e all'estrazione strutturata di informazioni da documenti complessi.

L'interfaccia è sviluppata con React, TypeScript e Vite e rappresenta il livello di presentazione della futura applicazione full-stack.

> **Stato attuale:** frontend navigabile con dati mock. Le funzionalità di analisi visualizzate non sono ancora collegate al backend o alla pipeline AI.

---

## 1. Stack tecnologico

| Tecnologia | Utilizzo |
|---|---|
| React 19 | Interfaccia utente |
| TypeScript | Tipizzazione statica |
| Vite 8 | Development server e build |
| React Router 8 | Routing client-side |
| CSS | Stili e layout responsive |
| Oxlint | Analisi statica del codice |

L'applicazione utilizza componenti funzionali React e React Hooks.

---

## 2. Installazione

### Prerequisiti

- Node.js compatibile con Vite 8
- npm

### Installare le dipendenze

Dalla cartella `frontend`:

```bash
npm install
```

### Avviare il development server

```bash
npm run dev
```

Vite mostrerà l'indirizzo locale dell'applicazione, normalmente:

`http://localhost:5173`

Il development server supporta Hot Module Replacement (HMR).

---

## 3. Comandi disponibili

| Comando | Descrizione |
|---|---|
| `npm install` | Installa le dipendenze |
| `npm run dev` | Avvia il server di sviluppo |
| `npm run build` | Esegue i controlli TypeScript e genera la build |
| `npm run preview` | Avvia l'anteprima locale della build |
| `npm run lint` | Esegue Oxlint |

### Build

```bash
npm run build
```

La build viene generata nella directory:

`dist/`

### Preview

Dopo la build:

```bash
npm run preview
```

### Lint

```bash
npm run lint
```

---

## 4. Struttura del frontend

```text
frontend/
|
+-- public/
|   +-- favicon.svg
|   +-- icons.svg
|
+-- src/
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
|   +-- data/
|   |   +-- analysisDemo.ts
|   |   +-- documents.ts
|   |
|   +-- hooks/
|   |   +-- useDocumentTitle.ts
|   |
|   +-- pages/
|   |   +-- HomePage.tsx
|   |   +-- DocumentsPage.tsx
|   |   +-- DocumentDetailPage.tsx
|   |   +-- SchemasPage.tsx
|   |   +-- NotFoundPage.tsx
|   |
|   +-- App.tsx
|   +-- App.css
|   +-- main.tsx
|   +-- index.css
|
+-- index.html
+-- package.json
+-- package-lock.json
+-- vite.config.ts
+-- tsconfig.json
+-- tsconfig.app.json
+-- tsconfig.node.json
+-- .oxlintrc.json
+-- README.md
```

---

## 5. Architettura React

L'applicazione è organizzata in:

- Pages
- Reusable Components
- Layout Components
- Domain Components
- Mock Data
- Custom Hooks

### 5.1 Entry point

`src/main.tsx`

Si occupa di:

- Creare il root React.
- Attivare React Strict Mode.
- Configurare BrowserRouter.
- Renderizzare il componente App.

### 5.2 Routing

`src/App.tsx`

Definisce le rotte dell'applicazione attraverso React Router.

| Route | Componente |
|---|---|
| `/` | HomePage |
| `/documents` | DocumentsPage |
| `/documents/:documentId` | DocumentDetailPage |
| `/schemas` | SchemasPage |
| `*` | NotFoundPage |

### 5.3 Layout condiviso

`src/components/layout/AppLayout.tsx`

Definisce la struttura comune:

```text
AppLayout
 |
 +-- Header
 |
 +-- main
 |    |
 |    +-- Outlet
 |         |
 |         +-- Pagina corrente
 |
 +-- Footer
```

L'utilizzo di `Outlet` permette di condividere Header e Footer tra le diverse pagine.

---

## 6. Pagine

### HomePage

`src/pages/HomePage.tsx`

Contiene:

- HeroSection
- FeaturesSection
- PlansSection

Presenta gli obiettivi e le funzionalità previste di DocuEntitySeek.

### DocumentsPage

`src/pages/DocumentsPage.tsx`

Visualizza un elenco di documenti dimostrativi.

Ogni documento presenta:

- Nome
- Categoria
- Numero di pagine
- Data di caricamento
- Stato di elaborazione

Gli stati previsti sono:

| Stato | Significato |
|---|---|
| READY | Analisi disponibile |
| PROCESSING | Elaborazione in corso |
| ERROR | Errore di elaborazione |

Attualmente gli stati sono simulati.

Solo i documenti in stato `READY` possono essere aperti attraverso il pulsante della relativa card.

### DocumentDetailPage

`src/pages/DocumentDetailPage.tsx`

Recupera l'identificativo del documento dalla rotta mediante `useParams`.

Gestisce tre situazioni:

1. Documento non trovato.
2. Analisi non disponibile.
3. Documento pronto per la visualizzazione.

Nel terzo caso viene renderizzato il componente `AnalysisDemoSection`.

### SchemasPage

`src/pages/SchemasPage.tsx`

Presenta:

- Schema Procurement predefinito.
- Elenco delle categorie NER.
- Elenco dei campi strutturati.
- Presentazione degli schemi personalizzati Premium.

L'editor Premium è attualmente disabilitato.

### NotFoundPage

`src/pages/NotFoundPage.tsx`

Gestisce gli indirizzi che non corrispondono alle rotte disponibili mediante una pagina 404.

---

## 7. Componenti di analisi

I componenti di dominio sono organizzati in:

`src/components/analysis/`

### 7.1 AnalysisDemoSection

`AnalysisDemoSection.tsx`

Componente principale della dimostrazione interattiva.

Gestisce:

- Pagina corrente.
- Categorie NER attive.
- Entità selezionata.
- Navigazione tra le pagine.
- Filtri delle annotazioni.

Utilizza `useState` per la gestione dello stato locale.

Le informazioni vengono passate ai componenti figli attraverso props.

### 7.2 AnnotatedDocumentMock

`AnnotatedDocumentMock.tsx`

Simula il viewer di un documento annotato.

Funzionalità:

- Visualizzazione del testo.
- Evidenziazione delle entità.
- Colori associati alle categorie.
- Selezione delle annotazioni.
- Visualizzazione del testo normale quando una categoria è disattivata.

Il componente non renderizza ancora un PDF reale.

### 7.3 EntityFilterList

`EntityFilterList.tsx`

Visualizza i controlli per filtrare le categorie NER.

Permette di:

- Attivare singole categorie.
- Disattivare singole categorie.
- Selezionare tutte le categorie.
- Deselezionare tutte le categorie.

È un componente controllato: riceve lo stato e le callback dal componente padre.

### 7.4 ExtractedFieldsPanel

`ExtractedFieldsPanel.tsx`

Visualizza le informazioni strutturate estratte.

Per ogni campo mostra:

- Nome del campo.
- Valore.
- Pagina di origine.
- Stato.

Attualmente visualizza informazioni dimostrative.

---

## 8. Gestione dei dati

I dati utilizzati dall'interfaccia sono contenuti nella directory:

`src/data/`

### documents.ts

Definisce:

- `DocumentStatus`
- `DocumentSummary`
- `MOCK_DOCUMENTS`

Contiene un insieme di documenti dimostrativi con stati differenti.

### analysisDemo.ts

Contiene i dati necessari alla dimostrazione del viewer, incluse:

- Etichette NER.
- Associazioni tra categorie e colori.
- Pagine dimostrative.
- Segmenti di testo.
- Annotazioni.
- Campi strutturati.

Questi dati permettono di sviluppare e verificare il comportamento dell'interfaccia indipendentemente dal backend.

### Limitazioni attuali

- Nessun caricamento reale di documenti.
- Nessuna chiamata HTTP al backend.
- Nessuna persistenza dei dati.
- Nessuna esecuzione del modello AI dal frontend.
- Nessuna autenticazione.
- Nessuna gestione effettiva dei piani Base/Premium.

---

## 9. React Hooks

Il progetto utilizza React Hooks per gestire lo stato e il comportamento dei componenti.

### useState

Utilizzato principalmente in `AnalysisDemoSection` per:

- Indice della pagina.
- Categorie attive.
- Entità selezionata.

Gli aggiornamenti dipendenti dallo stato precedente utilizzano functional updates.

### useEffect

Utilizzato nel custom Hook `useDocumentTitle`.

### useDocumentTitle

Percorso:

`src/hooks/useDocumentTitle.ts`

Permette di aggiornare il titolo della scheda del browser.

Esempio:

```tsx
useDocumentTitle('Documenti | DocuEntitySeek')
```

L'Hook utilizza `useEffect` e ripristina il titolo precedente durante il cleanup.

### State lifting

Lo stato condiviso tra viewer e filtri è gestito dal componente padre `AnalysisDemoSection`.

I componenti figli ricevono:

- Dati da visualizzare.
- Stato corrente.
- Callback per comunicare le interazioni.

Questo permette di mantenere un'unica fonte di verità per lo stato dell'interfaccia.

---

## 10. Stili

La gestione degli stili utilizza CSS.

File principali:

### src/index.css

Contiene gli stili globali.

### src/App.css

Contiene gli stili dell'applicazione, delle pagine e dei componenti.

L'interfaccia utilizza classi CSS con una nomenclatura descrittiva e organizzata per componente.

Sono presenti layout responsive per adattare le sezioni principali a differenti dimensioni dello schermo.

---

## 11. Accessibilità e usabilità

Il frontend include alcune pratiche di accessibilità:

- Elementi HTML semantici.
- Pulsanti per le azioni.
- Link per la navigazione.
- Checkbox per i filtri NER.
- Attributi di disabilitazione per azioni non disponibili.
- Etichetta di navigazione principale.
- Titoli delle pagine aggiornati dinamicamente.

L'accessibilità complessiva richiederà ulteriori verifiche e test dedicati.

---

## 12. Integrazione futura con il backend

Il frontend sarà successivamente collegato alle API REST sviluppate con FastAPI.

Flusso previsto:

```text
React Frontend
      |
      | HTTP Requests
      v
FastAPI Backend
      |
      +------------------+
      |                  |
      v                  v
PostgreSQL          AI Pipeline
                    PyMuPDF
                    GLiNER2.5
                         |
                         v
                  Risultati NER/IE
                         |
                         v
                  Risposta JSON
                         |
                         v
                  React Frontend
```

L'integrazione dovrà permettere di sostituire i dati mock con risultati reali.

Attività previste:

1. Introduzione di un client API.
2. Gestione delle richieste HTTP.
3. Recupero dei documenti.
4. Upload dei PDF.
5. Avvio delle analisi.
6. Recupero dei risultati.
7. Rendering delle annotazioni reali.
8. Visualizzazione dei campi estratti.
9. Gestione degli stati loading, error ed empty.
10. Autenticazione e controllo degli accessi.

Le API e i relativi contratti non sono ancora implementati.

---

## 13. Stato di sviluppo

| Funzionalità | Stato |
|---|---|
| Struttura React | Implementata |
| TypeScript | Configurato |
| Vite | Configurato |
| Routing | Implementato |
| Layout condiviso | Implementato |
| Landing page | Implementata |
| Elenco documenti | Implementato con mock |
| Dettaglio documento | Implementato con mock |
| Viewer NER | Demo interattiva |
| Filtri categorie | Implementati nella demo |
| Navigazione pagine | Implementata nella demo |
| Selezione annotazioni | Implementata nella demo |
| Sidebar Field Extraction | Implementata con mock |
| Pagina schemi | Implementata a livello UI |
| Schemi Premium personalizzati | Da implementare |
| HTTP API Client | Da implementare |
| Integrazione FastAPI | Da implementare |
| Upload PDF | Da implementare |
| Analisi AI reale | Da integrare |
| Autenticazione | Da implementare |
| Testing automatico frontend | Da implementare |

---

## 14. Prossimi sviluppi

Le principali attività previste per il frontend sono:

- Collegamento alle API REST.
- Separazione tra dati mock e dati remoti.
- Gestione centralizzata delle richieste HTTP.
- Componenti per upload documenti.
- Gestione dello stato delle analisi.
- Viewer basato su risultati AI reali.
- Navigazione verso le fonti dei risultati.
- Editor degli schemi personalizzati.
- Gestione delle sessioni utente.
- Protezione delle rotte riservate.
- Testing dei componenti.
- Testing end-to-end.
- Ottimizzazione delle prestazioni.
- Ulteriori verifiche di accessibilità.

---

## 15. Documentazione correlata

Il frontend fa parte del progetto DocuEntitySeek.

Documentazione disponibile nel repository principale:

- `../README.md`
- `../docs/DocuEntitySeek_Requisiti_Funzionali.pdf`
- `../docs/DocuEntitySeek_User_Story.pdf`
- `../ai/notebooks/Extraction_Pipeline.ipynb`

Questi documenti descrivono i requisiti applicativi, le funzionalità previste e la sperimentazione della pipeline AI.

---

## 16. Finalità

Il frontend viene sviluppato progressivamente con l'obiettivo di realizzare un'interfaccia modulare, manutenibile ed estendibile.

Le principali competenze coinvolte sono:

- React
- TypeScript
- Component-Based Architecture
- React Hooks
- Client-Side Routing
- State Management
- UI/UX Design
- API Integration
- Frontend Testing

L'obiettivo finale è integrare il frontend con la pipeline AI e il backend di DocuEntitySeek, realizzando un'applicazione full-stack per l'analisi intelligente dei documenti.
