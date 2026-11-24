# DocuEntitySeek — Frontend

**React 19 · TypeScript · Vite · PDF.js · REST API Integration**

Frontend web di **DocuEntitySeek**, una piattaforma full-stack di Document Intelligence che consente di caricare documenti PDF, avviare analisi basate su Named Entity Recognition (NER) e Structured Information Extraction (IE) e consultare i risultati attraverso un'interfaccia interattiva.

L'applicazione è sviluppata con React e TypeScript, comunica con il backend FastAPI attraverso API REST autenticate e utilizza PDF.js per visualizzare i documenti originali e le informazioni estratte.

> **Finalità didattica**
>
> DocuEntitySeek è un progetto didattico e di portfolio professionale, realizzato principalmente per approfondire la progettazione e lo sviluppo di applicazioni full-stack con integrazione AI.
>
> Il progetto non è orientato all'ottimizzazione delle prestazioni di GLiNER2.5, utilizzato nel backend come modello preaddestrato senza fine-tuning.
>
> Il frontend si concentra sulla progettazione dell'interfaccia, sull'organizzazione dei componenti React, sulla gestione dello stato, sull'integrazione delle API, sull'autenticazione, sulla visualizzazione documentale e sulla comunicazione tra i diversi livelli dell'applicazione.

Per una panoramica generale consultare il [README principale](../README.md). Per l'architettura delle API e della pipeline NLP consultare il [README del backend](../backend/README.md).

---

## 1. Obiettivi e responsabilità

Il frontend rappresenta il livello di interazione tra l'utente e i servizi applicativi di DocuEntitySeek.

Le sue principali responsabilità comprendono:

- Fornire un'interfaccia web per la gestione dei documenti.
- Gestire registrazione, login, logout e sessione autenticata.
- Comunicare con il backend attraverso API REST.
- Visualizzare il profilo utente e le funzionalità disponibili in base al piano.
- Consentire il caricamento e la validazione preliminare dei PDF.
- Avviare analisi NER/IE e visualizzarne lo stato.
- Gestire la selezione degli schemi di estrazione.
- Visualizzare il documento PDF originale mediante PDF.js.
- Mostrare entità riconosciute e informazioni strutturate.
- Collegare le estrazioni alle rispettive posizioni nel documento.
- Gestire schemi personalizzati e relativo versionamento.
- Fornire feedback coerenti durante caricamenti, errori ed elaborazioni.

Il frontend non esegue direttamente l'inferenza AI e non accede autonomamente al database PostgreSQL o al bucket S3.

Queste operazioni sono responsabilità del backend.

---

## 2. Stack tecnologico

| Area | Tecnologia |
|---|---|
| Libreria UI | React 19 |
| Linguaggio | TypeScript |
| Build e sviluppo | Vite |
| Routing | React Router |
| Comunicazione HTTP | Fetch API |
| Visualizzazione PDF | PDF.js (`pdfjs-dist`) |
| Gestione dello stato | React Hooks, Context API |
| Styling | CSS |
| Analisi statica | TypeScript, Oxlint |
| Testing | Vitest, React Testing Library |
| Distribuzione Portfolio | Docker, Nginx |

L'applicazione è una Single Page Application (SPA).

Il frontend utilizza il backend FastAPI come fonte dei dati applicativi e dei risultati AI.

---

## 3. Architettura del frontend

Il codice segue una separazione tra pagine, componenti, hook, client API e tipi TypeScript.

```text
                    React Page
                        |
                        v
                 UI Components
                        |
                        v
                   Custom Hooks
                        |
                        v
                  Domain API Layer
                        |
                        v
                 Shared HTTP Client
                        |
                        v
                     Fetch API
                        |
                        v
                  FastAPI Backend
                        |
            +-----------+-----------+
            |                       |
            v                       v
        PostgreSQL             AI / Storage
```

### Pages

Le pagine rappresentano le principali schermate dell'applicazione.

Coordinano componenti, hook e interazioni dell'utente.

### Components

I componenti gestiscono parti dell'interfaccia, come form, dialog, navigazione, feedback, risultati e visualizzazione PDF.

### Hooks

Gli hook personalizzati incapsulano logiche riutilizzabili per il caricamento dei dati, le operazioni asincrone, il polling e la gestione degli stati.

### API layer

I moduli API raccolgono le chiamate HTTP relative ai diversi domini applicativi.

### Types

Le interfacce e i tipi TypeScript descrivono le strutture dati utilizzate dal frontend.

Questa organizzazione limita l'accoppiamento tra presentazione, accesso ai dati e logica applicativa del client.

---

## 4. Struttura del progetto

```text
frontend/
|
+-- src/
|   +-- api/
|   |   +-- http.ts
|   |   +-- ...
|   |
|   +-- auth/
|   |   +-- AuthContext.tsx
|   |   +-- authStorage.ts
|   |
|   +-- components/
|   |   +-- analysis/
|   |   +-- auth/
|   |   +-- feedback/
|   |   +-- layout/
|   |   +-- pdf/
|   |   +-- upload/
|   |   +-- ...
|   |
|   +-- hooks/
|   +-- pages/
|   +-- types/
|   +-- utils/
|   |
|   +-- App.tsx
|   +-- main.tsx
|   +-- App.css
|   +-- index.css
|
+-- public/
+-- package.json
+-- .env.example
+-- README.md
```

La struttura rappresenta i moduli principali; possono essere presenti ulteriori file e componenti specifici.

### File di ingresso

`src/main.tsx` inizializza React, il router e il provider di autenticazione.

`src/App.tsx` definisce le principali route applicative e la loro organizzazione.

---

## 5. Routing e navigazione

Il routing è gestito tramite React Router.

Le principali route sono:

| Percorso | Funzione |
|---|---|
| `/` | Homepage |
| `/login` | Accesso |
| `/register` | Registrazione |
| `/documents` | Elenco documenti |
| `/documents/new` | Caricamento PDF |
| `/documents/:documentId` | Dettaglio documento e analisi |
| `/schemas` | Gestione schemi di estrazione |
| `/premium` | Pagina informativa Premium |

### Route protette

I componenti `ProtectedRoute` e `GuestRoute` gestiscono rispettivamente l'accesso alle schermate riservate agli utenti autenticati e alle pagine destinate agli utenti non autenticati.

### Layout condiviso

`AppLayout` organizza gli elementi comuni dell'interfaccia, come header, navigazione e contenuto delle pagine.

Le limitazioni della navigazione frontend migliorano l'esperienza utente, ma non sostituiscono i controlli di autorizzazione del backend.

---

## 6. Client HTTP e integrazione REST

Il client HTTP condiviso è implementato in:

```text
src/api/http.ts
```

Le sue responsabilità comprendono:

- Gestione della base URL.
- Invio delle richieste tramite Fetch API.
- Inserimento dell'header Bearer quando richiesto.
- Gestione dei metodi HTTP e dei payload JSON.
- Parsing delle risposte.
- Normalizzazione degli errori.
- Gestione degli status code.
- Supporto ad `AbortSignal`.

### Separazione tra componenti e API

Il flusso applicativo tipico è:

```text
React Component
      |
      v
Custom Hook
      |
      v
Domain API Function
      |
      v
requestJson()
      |
      v
FastAPI
```

I componenti utilizzano preferibilmente hook e client di dominio anziché implementare direttamente la logica HTTP.

Alcuni componenti specializzati, come il viewer PDF, effettuano richieste dedicate per il caricamento dei documenti e delle coordinate geometriche.

### Gestione degli errori

Gli errori HTTP vengono normalizzati in una struttura utilizzabile dall'interfaccia.

Il frontend può così mostrare messaggi coerenti in presenza di:

- Errori di autenticazione.
- Risorse inesistenti.
- Validazioni non superate.
- Quote esaurite.
- Permessi insufficienti.
- Errori di elaborazione AI.
- Problemi di rete.

La tipizzazione TypeScript non rappresenta una validazione di sicurezza: il backend verifica sempre autonomamente le richieste.

---

## 7. Autenticazione e gestione della sessione

L'autenticazione frontend utilizza `AuthContext`.

Il contesto gestisce:

- Utente autenticato.
- Access token JWT.
- Login e logout.
- Stato di autenticazione.
- Recupero del profilo.
- Informazioni sul piano.
- Quota giornaliera delle analisi.

### Persistenza del token

Il token viene conservato nel browser attraverso `sessionStorage`, utilizzando le funzioni definite in:

```text
src/auth/authStorage.ts
```

La chiave utilizzata è:

```text
docuentityseek.access-token
```

Il token viene aggiunto alle richieste protette mediante:

```text
Authorization: Bearer <access_token>
```

La gestione lato frontend non costituisce una garanzia di sicurezza dei token: il browser è un ambiente non affidabile e i token accessibili a JavaScript richiedono particolare attenzione alla prevenzione di vulnerabilità XSS.

### Login

Il frontend utilizza il servizio di autenticazione FastAPI, inviando le credenziali mediante il formato OAuth2 Password Request Form.

### Accesso alle risorse

Un utente può visualizzare e utilizzare soltanto le funzionalità consentite dalla propria sessione e dal proprio piano.

L'autorizzazione effettiva viene sempre applicata dal backend.

---

## 8. Gestione dei documenti PDF

La sezione documenti consente di:

- Visualizzare i documenti caricati.
- Consultare i metadati disponibili.
- Visualizzare il numero delle pagine.
- Caricare nuovi PDF.
- Aprire il dettaglio di un documento.
- Consultare le analisi eseguite.
- Avviare nuove analisi.
- Aprire il PDF originale.

### Upload

La pagina `NewDocumentPage` coordina il caricamento del documento.

Il flusso prevede:

```text
Selezione PDF
      |
      v
Validazione preliminare
      |
      v
Selezione schema (quando disponibile)
      |
      v
Conferma upload
      |
      v
POST /documents
      |
      v
Avvio Analysis
      |
      v
Navigazione verso /documents
```

La validazione frontend fornisce feedback immediato, mentre la validazione definitiva del file viene effettuata dal backend.

### Schema di estrazione

Gli utenti Base utilizzano lo schema predefinito.

Gli utenti abilitati agli schemi personalizzati possono scegliere uno degli schemi disponibili prima dell'analisi.

### Elaborazione automatica

Dopo il caricamento, il flusso frontend avvia la prima analisi.

Questo comportamento non implica l'esistenza di un worker AI separato: l'elaborazione viene attualmente eseguita dal backend secondo il suo modello di esecuzione sincrono.

---

## 9. Analisi NER e Information Extraction

Il frontend consente di interagire con la pipeline AI senza eseguire direttamente il modello GLiNER2.5.

L'utente può:

- Avviare un'analisi.
- Selezionare lo schema quando consentito.
- Consultare le analisi precedenti.
- Visualizzare lo stato di elaborazione.
- Accedere ai risultati completati.
- Visualizzare le entità NER.
- Consultare le informazioni strutturate IE.

### Avvio dell'analisi

Il frontend utilizza:

```text
POST /api/v1/documents/{document_id}/analyses
```

È possibile specificare una `schemaVersionId` quando il piano e lo schema lo consentono.

### Storico delle analisi

Ogni documento può avere più analisi associate.

L'interfaccia permette di recuperare e selezionare una specifica esecuzione, mantenendo visibili i riferimenti allo schema e alla versione utilizzata.

### Stati applicativi

Le analisi attraversano gli stati:

```text
QUEUED
PROCESSING
READY
ERROR
```

I risultati definitivi vengono visualizzati quando l'analisi è nello stato `READY`.

---

## 10. Polling e gestione degli stati asincroni

Il frontend implementa meccanismi di aggiornamento periodico per mantenere coerente l'interfaccia con lo stato del backend.

### Elenco documenti

L'hook `useDocuments` recupera i documenti e aggiorna periodicamente l'elenco quando rileva operazioni in elaborazione.

Sono previste anche verifiche temporanee per documenti appena caricati.

Il polling si interrompe quando non è più necessario.

### Dettaglio documento

La pagina `DocumentDetailPage` aggiorna periodicamente:

- L'elenco delle analisi del documento.
- Lo stato dell'analisi selezionata, quando ancora in esecuzione.

L'aggiornamento viene limitato quando la pagina del browser non è visibile.

### Annullamento delle richieste

Le richieste supportano, dove previsto, `AbortController` e `AbortSignal`.

Questo evita di trattare come errori applicativi alcune operazioni annullate intenzionalmente, ad esempio durante il cambio pagina o lo smontaggio di un componente.

**Importante:** il polling frontend non trasforma l'esecuzione backend in un sistema di job asincroni. Serve ad aggiornare l'interfaccia sulla base degli stati persistiti.

---

## 11. Viewer PDF.js

Il frontend integra PDF.js per visualizzare il documento PDF originale.

Il componente principale è:

```text
src/components/pdf/PdfDocumentViewer.tsx
```

### Funzionalità

Il visualizzatore supporta:

- Caricamento autenticato del PDF.
- Rendering delle pagine su Canvas.
- Navigazione tra le pagine.
- Adattamento alle dimensioni del contenitore.
- Zoom.
- Integrazione con i risultati AI.
- Evidenziazione delle entità e dei campi quando disponibili.
- Navigazione verso porzioni selezionate del documento.

### Accesso al PDF originale

Il file viene richiesto al backend tramite:

```text
GET /api/v1/documents/{document_id}/file
```

La richiesta include il token JWT.

L'endpoint FastAPI può restituire il file mediante risposte HTTP `200` o `206 Partial Content`.

Il frontend non richiede un accesso pubblico al bucket S3.

### PDF.js Worker

PDF.js utilizza un Web Worker per l'elaborazione del documento.

Il worker viene integrato nella build Vite e distribuito come asset JavaScript, generalmente con estensione `.mjs`.

Nell'ambiente Docker Portfolio Nginx deve servire i file `.mjs` con un MIME type JavaScript valido, come:

```text
application/javascript
```

Una configurazione MIME errata può impedire l'inizializzazione di PDF.js anche quando il documento è correttamente presente nello storage.

---

## 12. Visualizzazione dei risultati NER/IE

Il componente principale per la consultazione dei risultati è:

```text
src/components/analysis/AnalysisResultViewer.tsx
```

Utilizza le informazioni dell'analisi persistita, tra cui:

```text
result.schema
result.pages
result.entities
result.fields
```

### Named Entity Recognition

Le entità vengono rappresentate mediante le definizioni dello schema utilizzato.

L'interfaccia supporta:

- Colori associati alle etichette.
- Filtri per categoria.
- Attivazione e disattivazione delle etichette.
- Selezione delle entità.
- Collegamento tra entità e posizione nel documento.
- Navigazione tra i risultati riconosciuti.

### Information Extraction

I campi IE vengono mostrati utilizzando:

- Nome del campo.
- Chiave tecnica.
- Descrizione.
- Valore estratto, quando disponibile.
- Eventuale riferimento alla pagina di origine.

Il backend conserva anche stati di estrazione e possibili candidati alternativi; non tutte le informazioni disponibili nel contratto API vengono necessariamente mostrate come controlli interattivi del frontend.

### Provenance

Le informazioni estratte possono essere collegate al PDF mediante le coordinate calcolate dal backend.

L'endpoint utilizzato è:

```text
GET /api/v1/documents/{document_id}/analyses/{analysis_id}/geometry?page_number=1
```

L'evidenziazione viene effettuata soltanto quando il backend riesce ad allineare correttamente il testo persistito al contenuto originale.

Questo evita di mostrare collegamenti visivi potenzialmente errati.

La provenance rende i risultati più verificabili, ma non garantisce che l'interpretazione del modello sia semanticamente corretta.

---

## 13. Schemi di estrazione personalizzati

La sezione `/schemas` permette agli utenti abilitati di gestire le proprie configurazioni di estrazione.

Le funzionalità comprendono:

- Visualizzazione degli schemi disponibili.
- Creazione di nuovi schemi.
- Definizione delle entità NER.
- Definizione dei campi IE.
- Modifica e versionamento.
- Duplicazione.
- Archiviazione.
- Consultazione degli schemi archiviati.

### Definizioni NER

Le etichette identificano le tipologie di entità che il modello deve ricercare.

Esempi:

```text
PERSONA
ORGANIZZAZIONE
LOCALITA
IDENTIFICATIVO
```

### Campi IE

I campi strutturati utilizzano chiavi tecniche stabili.

Esempi:

```text
oggetto_principale
data_documento
nome_cliente
```

Le descrizioni semantiche specificano il significato delle informazioni richieste.

### Validazione

Il frontend verifica i dati dei form prima dell'invio.

I controlli comprendono, a seconda dell'operazione:

- Nome e dominio.
- Presenza di almeno una definizione.
- Limiti delle definizioni.
- Formato delle label NER.
- Formato delle chiavi IE.
- Duplicati.
- Nomi riservati.
- Errori restituiti dal backend.

La validazione definitiva rimane una responsabilità del backend.

### Versionamento

Le modifiche creano nuove versioni dello schema.

```text
Schema personalizzato
        |
        +-- v1 INACTIVE
        |
        +-- v2 ACTIVE
```

Le analisi storiche mantengono il riferimento alla versione originariamente utilizzata.

### Archiviazione

Gli schemi archiviati non vengono proposti per nuove analisi, mentre le informazioni storiche restano disponibili secondo le regole applicative.

---

## 14. Piani Base e Premium

Il frontend adatta alcune schermate e funzionalità in base al piano associato all'utente.

| Funzionalità | Base | Premium |
|---|---|---|
| Caricamento PDF | Sì | Sì |
| Analisi NER/IE | Sì | Sì |
| Schema built-in | Sì | Sì |
| Schemi personalizzati | No | Sì |
| Versionamento degli schemi personalizzati | No | Sì |
| Quota giornaliera | 5 nel seed iniziale | Nessun limite applicativo nel seed |

### Piano Base

Gli utenti Base utilizzano lo schema di estrazione predefinito.

L'interfaccia non rende disponibili gli strumenti di creazione e gestione degli schemi personalizzati.

### Piano Premium

Gli utenti Premium possono utilizzare lo schema predefinito e i propri schemi personalizzati attivi.

### Pagina Premium

La piattaforma include una pagina informativa dedicata al passaggio a Premium, con un contatto configurabile.

Il sistema di piani ha finalità didattiche e dimostrative.

Non è implementata un'infrastruttura commerciale completa di pagamento o sottoscrizione.

### Sicurezza

Le restrizioni visibili nel frontend non costituiscono una barriera di autorizzazione.

Il backend verifica autonomamente piano, ruolo, proprietà delle risorse e quota disponibile.

---

## 15. Feedback e gestione degli errori

Il frontend distingue esplicitamente gli stati di interazione più comuni:

```text
loading
empty
error
success
processing
ready
```

Sono presenti componenti dedicati al feedback, come stati di caricamento e schermate di errore.

Le operazioni possono prevedere:

- Indicatori di caricamento.
- Messaggi di validazione.
- Conferme prima delle azioni.
- Dialog modali.
- Messaggi di errore.
- Azioni di ripetizione delle richieste.
- Aggiornamento dello stato senza ricaricare l'intera pagina.

Le risposte del backend vengono normalizzate e presentate con messaggi comprensibili, senza mostrare all'utente traceback o dettagli interni non necessari.

---

## 16. Configurazione dell'ambiente

Il frontend utilizza le variabili d'ambiente di Vite.

La variabile principale è:

```text
VITE_API_BASE_URL
```

Questa identifica la base URL delle API FastAPI.

### Ambiente di sviluppo

Esempio:

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

### Ambiente Docker Portfolio

Nell'ambiente Portfolio, frontend e backend comunicano attraverso il reverse proxy Nginx.

La base API può quindi essere configurata con un percorso relativo:

```dotenv
VITE_API_BASE_URL=/api/v1
```

### Contatto Premium

La build Portfolio può utilizzare anche:

```text
VITE_PREMIUM_CONTACT_EMAIL
```

per configurare il contatto mostrato dalla pagina Premium.

### Variabili Vite

Le variabili con prefisso `VITE_` sono incluse nel codice frontend compilato quando vengono utilizzate dall'applicazione.

**Non devono contenere password, token segreti, chiavi private o altre credenziali sensibili.**

Inoltre, una modifica delle variabili utilizzate durante la compilazione richiede una nuova build per aggiornare gli asset distribuiti.

---

## 17. Avvio locale

### Prerequisiti

- Node.js e npm compatibili con il progetto.
- Dipendenze frontend installabili.
- Backend FastAPI disponibile.
- Variabili d'ambiente configurate.

Dalla directory `frontend/`:

### 17.1. Installazione

```powershell
npm ci
```

### 17.2. Configurazione

```powershell
Copy-Item .env.example .env
```

Impostare `VITE_API_BASE_URL` in modo coerente con l'indirizzo del backend di sviluppo.

### 17.3. Avvio

```powershell
npm run dev
```

L'applicazione viene normalmente esposta su:

```text
http://localhost:5173
```

Il server Vite è destinato allo sviluppo e non costituisce il server utilizzato per distribuire il frontend Portfolio.

---

## 18. Build e distribuzione Docker

### Build di produzione degli asset

```powershell
npm run build
```

Vite genera gli asset statici necessari alla distribuzione.

### Preview locale

```powershell
npm run preview
```

Il comando consente di visualizzare localmente la build compilata.

### Docker Portfolio

Il frontend viene compilato durante la costruzione dell'immagine Docker e distribuito tramite Nginx.

L'architettura prevede:

```text
Browser
   |
   v
Nginx
   |
   +-- React Static Assets
   |
   +-- /api/v1/
          |
          v
      FastAPI
          |
          +-- PostgreSQL
          +-- S3 Storage
          +-- GLiNER2.5
```

Il frontend è accessibile su:

```text
http://localhost:8080
```

### Avvio completo

Dalla radice del repository:

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml up -d --build
```

### Ricostruzione del solo frontend

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml up -d --no-deps --build frontend
```

### Controllo della configurazione Nginx

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml exec frontend nginx -t
```

Per la configurazione completa dello stack consultare il [README principale](../README.md).

---

## 19. Testing e qualità del codice

Il frontend utilizza TypeScript e strumenti di verifica del codice.

### Controllo TypeScript

```powershell
npx tsc -b
```

### Linting

```powershell
npm run lint
```

### Build

```powershell
npm run build
```

### Test

Il progetto include l'ecosistema Vitest / React Testing Library per i test frontend.

La copertura automatizzata può essere ampliata per includere:

- Autenticazione e route protette.
- Gestione delle richieste HTTP.
- Upload PDF.
- Quote.
- Polling delle analisi.
- Gestione degli schemi.
- Rendering dei risultati.
- Comportamento di PDF.js.
- Gestione degli errori.

I controlli di compilazione e type checking non sostituiscono i test comportamentali o end-to-end.

---

## 20. Sicurezza frontend

Il frontend applica alcune misure di protezione e gestione dell'accesso:

- Route riservate agli utenti autenticati.
- Utilizzo di token Bearer.
- Gestione del logout.
- Visibilità condizionale delle funzionalità.
- Validazione preliminare degli input.
- Gestione degli errori di autorizzazione.
- Accesso ai PDF attraverso endpoint autenticati.

Tuttavia, il frontend non è considerato una fonte affidabile per applicare le regole di sicurezza.

In particolare:

- I controlli Base/Premium devono essere verificati dal backend.
- I token presenti nel browser richiedono protezione rispetto a vulnerabilità client-side.
- Il bucket S3 deve rimanere privato.
- La validazione definitiva dei documenti avviene lato server.
- I dati restituiti dalle API non devono essere considerati automaticamente attendibili dal punto di vista applicativo.

Il progetto non rappresenta una soluzione certificata per la gestione di dati sensibili.

---

## 21. Limitazioni attuali

### Dipendenza dal backend

Il frontend necessita delle API FastAPI per autenticazione, documenti, schemi e analisi.

Non è progettato come applicazione completamente autonoma o offline.

### Elaborazione sincrona AI

L'avvio dell'analisi utilizza attualmente una richiesta HTTP che può rimanere aperta per tutta la durata della pipeline.

Questo può comportare tempi di attesa elevati e richiede particolare attenzione a timeout e interruzioni.

### Accuratezza delle estrazioni

La qualità dei risultati dipende dal modello GLiNER2.5 e dalle definizioni dello schema.

Il frontend visualizza i risultati, ma non ne certifica la correttezza.

### Evidenziazione PDF

La visualizzazione delle evidenziazioni dipende dalla disponibilità e dall'allineamento delle coordinate geometriche.

Non tutti i risultati possono essere necessariamente evidenziati sul PDF originale.

### OCR

Il sistema non integra attualmente una pipeline OCR per documenti costituiti esclusivamente da scansioni.

### Testing

La suite automatizzata può essere ulteriormente estesa, soprattutto per i flussi end-to-end che coinvolgono frontend, backend, storage e AI.

### Deployment

L'ambiente Docker Portfolio è una configurazione dimostrativa locale, non una distribuzione production-ready destinata all'esposizione pubblica.

---

## 22. Possibili evoluzioni

Tra i possibili sviluppi futuri:

- Miglioramento dell'accessibilità dell'interfaccia.
- Ampliamento dei test automatizzati.
- Test end-to-end completi.
- Visualizzazione più approfondita dei candidati IE.
- Miglioramento della gestione delle analisi lunghe.
- Integrazione con una futura pipeline AI asincrona.
- Ulteriori strumenti di navigazione e revisione delle estrazioni.
- Ottimizzazione del rendering di documenti molto grandi.
- Miglioramento della gestione degli errori e dell'osservabilità frontend.

Queste funzionalità rappresentano potenziali evoluzioni, non caratteristiche già disponibili.

---

## 23. Principi progettuali

L'architettura frontend di DocuEntitySeek mantiene separate le responsabilità:

```text
USER INTERFACE
      !=
PRESENTATION STATE
      !=
API COMMUNICATION
      !=
APPLICATION BUSINESS LOGIC
      !=
AI INFERENCE
      !=
DATA PERSISTENCE
```

L'interfaccia rappresenta i dati e permette l'interazione.

Gli hook gestiscono lo stato e coordinano le richieste.

Il livello API comunica con i servizi backend.

Il backend applica le regole di business, gestisce la persistenza ed esegue l'inferenza.

Questa separazione favorisce modularità, manutenibilità, riutilizzo dei componenti e possibilità di evoluzione.

---

## Conclusione

Il frontend di DocuEntitySeek rappresenta un esercizio di **sviluppo React/TypeScript integrato con un'architettura full-stack e una pipeline di Document Intelligence**.

Il suo valore principale risiede nella realizzazione di un'interfaccia funzionale per l'autenticazione, la gestione dei documenti, il versionamento degli schemi, la consultazione delle analisi e la visualizzazione delle informazioni estratte direttamente sul PDF originale.

**L'obiettivo non è dimostrare le migliori prestazioni possibili di un modello AI, ma progettare un'applicazione web modulare, comprensibile e concretamente integrata con servizi backend, database, storage e funzionalità NLP.**

---

## Riferimenti

- [DocuEntitySeek — README principale](../README.md)
- [DocuEntitySeek — Backend](../backend/README.md)
- [React](https://react.dev/)
- [TypeScript](https://www.typescriptlang.org/)
- [Vite](https://vite.dev/)
- [React Router](https://reactrouter.com/)
- [PDF.js](https://mozilla.github.io/pdf.js/)
- [Vitest](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Nginx](https://nginx.org/)
- [Docker](https://docs.docker.com/)