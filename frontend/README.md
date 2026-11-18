# DocuEntitySeek — Frontend

Frontend React di **DocuEntitySeek**, piattaforma di Document Intelligence per Named Entity Recognition (NER) e Structured Information Extraction (IE).

L'applicazione comunica con il backend FastAPI reale tramite REST API autenticate e gestisce documenti, Analysis, quote e schemi di estrazione custom Premium.

> **Stato attuale — checkpoint 19.23:** autenticazione, upload PDF, avvio automatico delle Analysis, polling degli stati, quote, storico Analysis e gestione degli schemi custom Premium sono collegati al backend. Il viewer dei risultati utilizza ancora in parte il precedente modello dimostrativo e costituisce il prossimo refactoring.

---

## 1. Stack

- React 19
- TypeScript
- Vite
- React Router
- Fetch API
- CSS
- Oxlint
- Vitest / React Testing Library

---

## 2. Installazione

Dalla directory:

```text
frontend/
```

installare:

```powershell
npm ci
```

configurare l'ambiente utilizzando:

```text
.env.example
```

come riferimento.

La variabile API deve puntare al backend FastAPI di sviluppo.

Avviare:

```powershell
npm run dev
```

Normalmente:

```text
http://localhost:5173
```

---

## 3. Comandi

```powershell
npm run dev
npm run build
npm run lint
npm run preview
```

Type checking separato:

```powershell
npx tsc -b
```

---

## 4. Architettura

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
FastAPI
```

Le responsabilità sono separate tra:

```text
pages/
components/
hooks/
api/
types/
utils/
auth/
```

I componenti React non eseguono direttamente `fetch` quando può essere delegato all'API layer.

---

## 5. HTTP client

`src/api/http.ts` rappresenta il client condiviso.

Gestisce:

- base URL;
- Bearer token;
- metodi HTTP;
- body JSON;
- parsing delle response;
- errori applicativi;
- `AbortSignal`;
- normalizzazione degli errori.

La tipizzazione TypeScript non sostituisce la validazione server-side.

---

## 6. Autenticazione

`AuthContext` mantiene lo stato della sessione.

Gestisce:

- utente;
- access token;
- login;
- logout;
- refresh dell'utente;
- piano;
- quota di analisi.

Le pagine protette richiedono una sessione autenticata.

---

## 7. Piani

Il frontend legge:

```text
user.plan
```

ma non considera questo controllo una barriera di sicurezza.

Il backend verifica sempre autonomamente le autorizzazioni.

### Base

Non mostra gli strumenti di gestione degli schema personalizzati.

### Premium

Espone:

```text
/schemas
```

con gestione completa degli schema custom.

---

## 8. Documenti

La sezione documenti permette di:

- elencare i documenti dell'utente;
- caricare nuovi PDF;
- scegliere una categoria;
- scegliere lo schema quando previsto;
- aprire il dettaglio;
- consultare Analysis e risultati.

---

## 9. Upload

Il caricamento avviene attraverso la pagina dedicata.

Dopo un upload valido:

```text
PDF upload
    ↓
documento creato
    ↓
Analysis avviata automaticamente
    ↓
redirect /documents
```

Non è necessario entrare nel dettaglio per avviare la prima analisi.

---

## 10. Polling della lista documenti

`useDocuments` effettua polling condizionale.

```text
esiste PROCESSING?
       |
      sì
       |
poll periodico
       |
nessun PROCESSING
       |
      stop
```

Questo permette alla card di passare automaticamente da:

```text
In elaborazione
```

a:

```text
Pronto
```

senza refresh del browser.

Il polling non viene mantenuto inutilmente quando non esistono documenti in elaborazione.

---

## 11. Analysis

Il frontend dispone di API/hook dedicati per:

- avvio Analysis;
- lista Analysis di un documento;
- dettaglio Analysis;
- gestione degli errori;
- quota.

L'avvio di una nuova Analysis supporta una specifica:

```text
schemaVersionId
```

quando prevista.

---

## 12. Quota

Il numero di analisi disponibili viene recuperato dal backend e mostrato all'utente.

Il frontend aggiorna la quota dopo l'avvio di un'Analysis.

La logica di enforcement rimane sul backend.

---

## 13. Schema di estrazione durante upload

### Base

Utilizza automaticamente lo schema built-in.

### Premium

La pagina di upload recupera gli schema disponibili e mostra un selector.

Gli schema disponibili includono:

- built-in;
- propri schema custom attivi.

Non includono:

- custom di altri utenti;
- versioni inattive;
- schema archiviati.

---

## 14. Schemi custom

La pagina:

```text
/schemas
```

permette a un utente Premium di gestire i propri schema.

Funzioni implementate:

- lista;
- creazione;
- modifica;
- versionamento;
- duplicazione;
- archiviazione.

---

## 15. Form schema custom

Uno schema può contenere:

```text
Entity definitions
Field definitions
```

Il form permette di aggiungere e rimuovere dinamicamente entrambe le tipologie.

### Entità

Una label usa la forma:

```text
PERSONA
ORGANIZZAZIONE
MIO_TIPO_ENTITA
```

### Campi

Una chiave tecnica usa la forma:

```text
titolo_documento
data_documento
nome_cliente
```

La chiave:

```text
confidence
```

è riservata e non può essere utilizzata come field custom.

---

## 16. Validazione schema

Il frontend verifica prima della richiesta:

- nome;
- dominio;
- almeno un'entità o un field;
- massimo configurato di entità;
- massimo configurato di field;
- formato delle label;
- label duplicate;
- formato delle field key;
- field key duplicate;
- `confidence`;
- nomi schema duplicati.

Il backend ripete comunque la validazione.

---

## 17. Versionamento

La modifica non sovrascrive lo schema precedente.

La UI informa l'utente della nuova versione:

```text
v1
↓ modifica
v2
↓ modifica
v3
```

Dopo un update la lista viene ricaricata automaticamente.

---

## 18. Duplicazione

La duplicazione utilizza un dialog dedicato.

La nuova copia:

- richiede un nome differente;
- diventa un nuovo schema;
- parte dalla versione 1.

La lista viene aggiornata senza refresh manuale.

---

## 19. Archiviazione

L'archiviazione utilizza un dialog di conferma.

Dopo l'operazione:

```text
Schemi attivi
     ↓
Schemi archiviati
```

Lo schema non compare più nella select dell'upload.

Lo storico rimane conservato.

---

## 20. Error handling schema

Gli errori applicativi vengono trasformati in messaggi comprensibili.

Tra quelli gestiti:

```text
CUSTOM_SCHEMA_NAME_CONFLICT
CUSTOM_SCHEMA_ARCHIVED
CUSTOM_SCHEMAS_NOT_AVAILABLE
EXTRACTION_SCHEMA_NOT_FOUND
```

Sono inoltre gestiti gli errori di validazione `422`.

---

## 21. API frontend principali

La directory:

```text
src/api/
```

contiene client di dominio per funzionalità come:

```text
auth
documents
analyses
schemas
custom schemas
```

Tutte utilizzano il client HTTP condiviso.

---

## 22. Hooks principali

La directory:

```text
src/hooks/
```

comprende hook dedicati a:

- document list;
- document detail;
- creazione documento;
- avvio Analysis;
- storico Analysis;
- dettaglio Analysis;
- schema disponibili;
- schema custom;
- azioni sugli schema custom;
- title del documento.

---

## 23. Feedback UI

Sono gestiti esplicitamente:

```text
loading
error
empty
success
processing
ready
```

Le richieste annullate intenzionalmente tramite `AbortController` non vengono mostrate come errori all'utente.

---

## 24. Routing

Le route principali comprendono:

```text
/
login / registrazione
/documents
/documents/new
/documents/:documentId
/schemas
```

Ulteriori route applicative possono essere presenti per funzionalità amministrative.

Il layout condiviso gestisce header, navigazione e contenuto tramite React Router.

---

## 25. Pagina Documents

La lista visualizza:

- nome;
- categoria;
- numero pagine;
- data;
- stato.

Gli stati principali sono:

```text
READY
PROCESSING
ERROR
```

I documenti in elaborazione vengono aggiornati automaticamente.

---

## 26. Document Detail

Il dettaglio combina:

- metadati documento;
- Analysis disponibili;
- Analysis selezionata;
- stato;
- risultati quando READY.

Una ri-Analysis conserva lo schema della Analysis selezionata, quando disponibile.

---

## 27. Viewer

Il viewer rappresenta l'ultima parte ancora transitoria del frontend.

Alcuni componenti utilizzano ancora il precedente contratto:

```text
DocumentAnalysis
```

e componenti nati per la demo.

Il backend espone invece il contratto persistito:

```text
AnalysisDetail.result
```

Il prossimo refactoring eliminerà progressivamente questo ponte.

---

## 28. Viewer reale previsto

Il viewer finale utilizzerà direttamente:

```text
result.pages
result.entities
result.fields
```

e supporterà:

- navigazione pagine;
- testo reale estratto;
- evidenziazione NER;
- colori dinamici;
- filtri label;
- entity selection;
- confidence;
- provenance;
- field status;
- candidati alternativi.

---

## 29. Mock legacy

Eventuali file/componenti mock ancora presenti nel repository devono essere considerati materiale legacy o dimostrativo.

Il runtime applicativo attuale utilizza FastAPI come backend reale.

La loro eliminazione definitiva avverrà durante il refactoring del viewer.

---

## 30. Sicurezza frontend

Il frontend migliora l'esperienza utente ma non costituisce la barriera di autorizzazione.

Controlli quali:

```text
Premium
ownership
quota
schema access
```

sono applicati definitivamente dal backend.

Il browser non deve essere considerato un ambiente affidabile.

---

## 31. Build

Prima di un commit significativo:

```powershell
npx tsc -b
npm run build
npm run lint
```

Il type checker deve terminare senza errori.

---

## 32. Testing

Il frontend utilizza/può utilizzare:

- Vitest;
- React Testing Library.

La suite verrà estesa nel blocco di testing completo per coprire:

- auth;
- documenti;
- polling;
- upload;
- quota;
- Analysis;
- schema selector;
- schema custom;
- viewer.

---

## 33. Stato delle funzionalità

| Funzionalità | Stato |
|---|---|
| Routing | Implementato |
| HTTP client | Implementato |
| FastAPI integration | Implementata |
| JWT | Implementato |
| Upload PDF | Implementato |
| Analisi automatica | Implementata |
| Polling documenti | Implementato |
| Quote | Implementate |
| Analysis history/detail | Implementati |
| Selector schema | Implementato |
| Custom schema Premium | Implementato |
| Versionamento | Implementato |
| Duplicazione | Implementata |
| Archiviazione | Implementata |
| Validazione custom schema | Implementata |
| Viewer API reale | Prossimo refactoring |
| Test frontend completo | Da completare |
| E2E | Da completare |
| Deployment | Da completare |

---

## 34. Prossimo sviluppo

Il prossimo blocco sostituirà il viewer dimostrativo con il viewer collegato direttamente alle Analysis persistite.

Ordine previsto:

```text
AnalysisDetail.result
        ↓
pages reali
        ↓
entities reali
        ↓
filters
        ↓
structured fields
        ↓
provenance
        ↓
analysis history
```

Al completamento verranno rimossi i componenti e i tipi legacy non più necessari.