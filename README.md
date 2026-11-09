
# DocuEntitySeek

**Document Intelligence Platform — Entity Discovery & Structured Information Extraction**

DocuEntitySeek è una piattaforma di Document Intelligence progettata per analizzare documenti complessi mediante tecniche di Natural Language Processing (NLP) e Intelligenza Artificiale.

L'applicazione si concentra inizialmente sul dominio **Procurement**, con particolare riferimento a:

- Bandi di gara
- Disciplinari di gara
- Capitolati
- Contratti
- Documentazione amministrativa

L'obiettivo è trasformare documenti non strutturati in informazioni organizzate, consultabili e verificabili, mantenendo il collegamento tra ogni risultato estratto e il documento originale.

> **Stato del progetto:** in sviluppo. Il frontend dispone di un'interfaccia navigabile basata su dati dimostrativi. La pipeline AI è stata prototipata in un notebook Jupyter. Backend, database e integrazione end-to-end sono ancora da implementare.

---

## 1. Obiettivi

DocuEntitySeek nasce per semplificare l'analisi di documenti lunghi e complessi.

Gli obiettivi principali sono:

1. Individuare automaticamente le entità rilevanti.
2. Estrarre informazioni strutturate secondo uno schema configurabile.
3. Evidenziare le entità direttamente nel testo.
4. Associare i risultati alle pagine e alle posizioni originali.
5. Ridurre la necessità di consultare manualmente interi documenti.
6. Consentire la futura personalizzazione degli schemi per domini differenti dal Procurement.

Il sistema è progettato per distinguere chiaramente due funzionalità:

- **Entity Discovery (NER):** riconoscimento delle entità nel testo.
- **Field Extraction (IE):** estrazione di informazioni strutturate.

## 2. Funzionalità

### 2.1 Entity Discovery

Individuazione automatica di entità nominate mediante Named Entity Recognition.

Lo schema Procurement prevede inizialmente:

| Entità | Descrizione |
|---|---|
| ORGANIZZAZIONE | Enti, amministrazioni, aziende e organizzazioni |
| PERSONA | Nomi di persone fisiche |
| LOCALITA | Luoghi e riferimenti geografici |
| IMPORTO | Importi monetari e valori economici |
| DATA | Date e scadenze |
| ORA | Orari |
| RIFERIMENTO_NORMATIVO | Leggi, decreti e altri riferimenti normativi |
| IDENTIFICATIVO_GARA | CIG, CUP, CPV e identificativi ufficiali |
| CERTIFICAZIONE | Certificazioni e attestazioni |
| PRODOTTO_SERVIZIO | Prodotti, servizi e forniture |

Le entità sono associate a etichette e colori utilizzabili dal document viewer.

### 2.2 Structured Field Extraction

Estrazione di valori strutturati secondo uno schema di dominio.

I campi previsti dal prototipo AI comprendono:

- Stazione appaltante
- Oggetto gara
- CIG
- CUP
- CPV
- Tipo procedura
- Importo complessivo
- Importo base d'asta
- Numero lotti
- Durata contratto
- Scadenza offerte
- Termine chiarimenti
- Criterio di aggiudicazione
- Responsabile procedimento
- Luogo esecuzione

I risultati dell'estrazione sono destinati a una sidebar separata dalle annotazioni NER.

### 2.3 Document Viewer

Il viewer è progettato per:

- Visualizzare il testo del documento.
- Evidenziare le entità mediante colori.
- Filtrare le categorie NER.
- Navigare tra le pagine.
- Selezionare le annotazioni.
- Consultare le informazioni strutturate.
- Mantenere il riferimento alla fonte.

Nel frontend attuale queste interazioni utilizzano dati mock.

### 2.4 Provenienza delle informazioni

La pipeline AI sperimentale conserva informazioni utili a verificare i risultati:

- Testo estratto
- Etichetta dell'entità o nome del campo
- Confidence, quando disponibile
- Offset iniziale e finale nel testo completo
- Pagina di origine
- Offset relativi alla pagina

La provenienza permette di ricondurre le estrazioni al contenuto originale.

I risultati prodotti dall'AI devono essere considerati informazioni da verificare, non dati automaticamente certificati.

---

## 3. Modello di utilizzo previsto

DocuEntitySeek prevede due livelli funzionali.

### Base

Pensato per analizzare documenti Procurement mediante uno schema predefinito.

Funzionalità previste:

- Entity Discovery
- Field Extraction
- Schema Procurement
- Viewer annotato
- Limite applicativo di 5 nuove analisi giornaliere

### Premium

Pensato per estendere l'analisi ad altri domini documentali.

Funzionalità previste:

- Tutte le funzionalità Base
- Entità personalizzate
- Campi personalizzati
- Schemi di estrazione riutilizzabili
- Analisi di documenti appartenenti a domini differenti
- Assenza del limite giornaliero applicativo previsto per Base

**Nota:** la distinzione Base/Premium è attualmente rappresentata nell'interfaccia. Autenticazione, autorizzazioni, quote e gestione dei piani non sono ancora implementate nel backend.

---

## 4. Stack tecnologico

### Frontend

- React 19
- TypeScript
- Vite
- React Router
- CSS
- Oxlint

### Backend previsto

- Python
- FastAPI
- API REST

### AI / NLP

- Python
- PyMuPDF
- GLiNER2.5
- Pandas
- NumPy
- Jupyter Notebook

Modello utilizzato nel notebook sperimentale:

`fastino/gliner2.5-multi-v1`

### Database previsto

- PostgreSQL
- SQLAlchemy

### Infrastructure prevista

- Docker
- Docker Compose

Backend, persistenza e infrastruttura sono componenti architetturali pianificati, non servizi già disponibili nello stato attuale del repository.

---

## 5. Architettura

L'architettura prevista separa tre componenti principali:

```text
                  FRONTEND
             React + TypeScript
                       |
                       | HTTP / REST
                       v
                   BACKEND
                    FastAPI
                       |
             +---------+---------+
             |                   |
             v                   v
         AI PIPELINE         DATABASE
         PyMuPDF             PostgreSQL
         GLiNER2.5           SQLAlchemy
             |
             v
     Entity Discovery
     Field Extraction
             |
             v
       Risultati con
         provenance
```

Questa rappresentazione descrive l'architettura obiettivo. Attualmente il frontend e il notebook AI sono separati.

## 6. Pipeline AI

Il notebook `Extraction_Pipeline.ipynb` implementa una pipeline sperimentale per l'analisi di documenti PDF.

Flusso logico:

```text
PDF
 |
 v
PyMuPDF
 |
 v
Estrazione del testo
pagina per pagina
 |
 v
Mappatura pagine e offset
 |
 v
GLiNER2.5 long-context
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
       Risultati con
         provenance
             |
             v
     Viewer e sidebar
```

### 6.1 Elaborazione long-context

La pipeline utilizza:

- `extract_entities_long()`
- `extract_json_long()`

Queste API consentono di analizzare testi lunghi mediante chunk sovrapposti.

Configurazione sperimentale:

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

I valori rappresentano una configurazione iniziale e richiedono validazione su documenti reali.

### 6.2 Gestione degli overlap

La pipeline distingue:

- Chunk overlap: sovrapposizione tra segmenti utilizzati durante l'inferenza.
- Entity overlap: sovrapposizione tra entità individuate nel testo.

Per il viewer viene adottata una politica deterministica che privilegia:

1. Confidence maggiore.
2. Span più lungo.
3. Posizione iniziale nel documento.

Lo scopo è produrre annotazioni non sovrapposte, mantenendo separati i risultati dell'estrazione strutturata.

### 6.3 Separazione pipeline e schema

Un principio architetturale fondamentale è separare la logica di analisi dalla definizione delle informazioni da cercare.

```text
PIPELINE = come analizzare il documento

SCHEMA = quali entità e campi estrarre
```

La stessa pipeline potrà essere riutilizzata con schemi differenti.

Nel notebook sono presenti:

- Schema Procurement predefinito
- Esempio di schema Premium per il dominio immobiliare

---

## 7. Struttura del repository

```text
DocuEntitySeek/
|
+-- ai/
|   +-- notebooks/
|       +-- Extraction_Pipeline.ipynb
|
+-- backend/
|   +-- [codice applicativo da implementare]
|
+-- docs/
|   +-- DocuEntitySeek_Requisiti_Funzionali.pdf
|   +-- DocuEntitySeek_User_Story.pdf
|
+-- frontend/
|   +-- public/
|   +-- src/
|   |   +-- assets/
|   |   +-- components/
|   |   |   +-- analysis/
|   |   |   +-- layout/
|   |   +-- data/
|   |   +-- hooks/
|   |   +-- pages/
|   |   +-- App.tsx
|   |   +-- App.css
|   |   +-- main.tsx
|   |   +-- index.css
|   +-- package.json
|   +-- package-lock.json
|   +-- vite.config.ts
|   +-- README.md
|
+-- .gitignore
+-- README.md
```

Gli ambienti virtuali e le dipendenze installate localmente non fanno parte del codice applicativo da versionare.

---

## 8. Avvio locale

### 8.1 Requisiti

Per il frontend:

- Node.js compatibile con la versione di Vite utilizzata
- npm
- Git (consigliato)

Per i notebook AI:

- Python compatibile con le librerie utilizzate
- Jupyter Notebook, JupyterLab oppure VS Code con supporto Jupyter
- Ambiente virtuale Python consigliato

### 8.2 Avviare il frontend

Dalla cartella principale:

```bash
cd frontend
npm install
npm run dev
```

Aprire nel browser l'indirizzo mostrato dal terminale, normalmente:

`http://localhost:5173`

Per ulteriori dettagli consultare [frontend/README.md](frontend/README.md).

### 8.3 Eseguire il notebook AI

Aprire:

`ai/notebooks/Extraction_Pipeline.ipynb`

Il notebook include una cella per installare le dipendenze principali:

```python
%pip install -U pymupdf pandas numpy "gliner2[local]"
```

Prima dell'esecuzione:

1. Selezionare un kernel Python compatibile.
2. Installare le dipendenze.
3. Modificare la variabile `PDF_PATH` indicando un PDF locale.
4. Eseguire le celle in ordine.
5. Verificare le entità e i campi estratti.

Il modello potrebbe richiedere un download alla prima esecuzione.

La pipeline è un prototipo sperimentale e non è ancora esposta tramite API REST.

---

## 9. Frontend

Il frontend comprende:

- Landing page
- Presentazione delle funzionalità
- Presentazione dei piani Base/Premium
- Elenco documenti dimostrativi
- Dettaglio documento
- Viewer NER interattivo basato su mock
- Sidebar delle entità
- Sidebar dei campi estratti
- Pagina degli schemi
- Gestione delle rotte non trovate

### Routing

| Percorso | Descrizione |
|---|---|
| `/` | Homepage |
| `/documents` | Elenco documenti |
| `/documents/:documentId` | Dettaglio e analisi dimostrativa |
| `/schemas` | Schemi di estrazione |
| `*` | Pagina 404 |

Il frontend utilizza React Router e componenti funzionali React.

---

## 10. Documentazione

La cartella `docs/` contiene i documenti di progettazione:

### Requisiti funzionali

`docs/DocuEntitySeek_Requisiti_Funzionali.pdf`

Descrive i requisiti dell'applicazione e le funzionalità previste.

### User Story

`docs/DocuEntitySeek_User_Story.pdf`

Descrive le funzionalità dal punto di vista degli utenti, includendo criteri di accettazione.

Questi documenti rappresentano il riferimento per le successive attività di implementazione e verifica.

---

## 11. Stato di sviluppo

| Componente | Stato |
|---|---|
| Requisiti funzionali | Documentati |
| User Story | Documentate |
| Pipeline AI | Prototipo notebook |
| Entity Discovery | Prototipo AI e demo frontend |
| Field Extraction | Prototipo AI e demo frontend |
| Landing page | Implementata |
| React Router | Implementato |
| Elenco documenti | Implementato con mock |
| Viewer annotato | Implementato con mock |
| Pagina schemi | Implementata a livello UI |
| Backend FastAPI | Da implementare |
| Integrazione frontend/backend | Da implementare |
| Database PostgreSQL | Da implementare |
| Autenticazione | Da implementare |
| Gestione piani e quote | Da implementare |
| Upload e analisi reali via web | Da implementare |
| Containerizzazione | Da implementare |
| Deployment | Da implementare |

**Importante:** le funzionalità mostrate attraverso dati mock non devono essere considerate equivalenti a funzionalità integrate con il modello AI.

---

## 12. Prossimi sviluppi

Le attività previste comprendono:

1. Consolidamento e validazione della pipeline AI.
2. Implementazione del backend FastAPI.
3. Definizione delle API REST.
4. Persistenza mediante PostgreSQL e SQLAlchemy.
5. Gestione dei documenti PDF.
6. Integrazione della pipeline AI nel backend.
7. Collegamento frontend/backend.
8. Autenticazione e autorizzazione degli utenti.
9. Gestione dei piani Base/Premium.
10. Creazione e gestione degli schemi personalizzati.
11. Testing e validazione end-to-end.
12. Containerizzazione e deployment.

---

## 13. Considerazioni sull'affidabilità

DocuEntitySeek utilizza modelli di AI che possono produrre:

- Entità non riconosciute
- Informazioni estratte in modo incompleto
- Valori ambigui
- Falsi positivi
- Collegamenti errati alla fonte

Per questo motivo la progettazione privilegia:

- Tracciabilità delle estrazioni
- Indicazione della pagina sorgente
- Conservazione degli span quando disponibili
- Separazione fra entità e campi strutturati
- Gestione esplicita dei casi ambigui o non trovati
- Verifica manuale dei risultati

Le informazioni prodotte dall'applicazione non sostituiscono la lettura e la verifica del documento originale.

---

## 14. Finalità

DocuEntitySeek è un progetto software in evoluzione, sviluppato con finalità di sperimentazione e realizzazione di una piattaforma full-stack per Document Intelligence.

L'obiettivo è integrare competenze di:

- Natural Language Processing
- Information Extraction
- Machine Learning
- Backend Development
- Frontend Development
- Database Design
- Software Architecture
- Deployment

Il progetto segue un approccio incrementale, separando la sperimentazione dei modelli AI dall'implementazione e dall'integrazione dei componenti applicativi.