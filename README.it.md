# DocuEntitySeek

**Full-Stack Document Intelligence Platform | React · FastAPI · PostgreSQL · GLiNER2.5**

DocuEntitySeek è una piattaforma web di **analisi documentale intelligente**, sviluppata a scopo didattico e dimostrativo, che consente di caricare documenti PDF, identificare entità nominate (*Named Entity Recognition*) ed estrarre informazioni strutturate (*Information Extraction*) attraverso schemi semantici personalizzabili.

La piattaforma integra un frontend React, un backend FastAPI, un database PostgreSQL, uno storage S3-compatible e un modello NLP eseguito localmente, offrendo un flusso completo di elaborazione, persistenza e consultazione dei risultati.

> **Finalità del progetto**
>
> DocuEntitySeek nasce come progetto di studio e portfolio professionale, con l'obiettivo principale di esplorare e dimostrare la progettazione, lo sviluppo e l'integrazione di un'applicazione **full-stack con funzionalità di Intelligenza Artificiale**.
>
> Il progetto **non è focalizzato sull'ottimizzazione delle prestazioni di GLiNER2.5**: il modello viene utilizzato nella sua versione preaddestrata, senza fine-tuning dedicato, benchmark comparativi o adattamenti a domini specifici.
>
> L'attenzione è rivolta soprattutto all'architettura software, alla separazione delle responsabilità, alla gestione dei dati, alla progettazione delle API, alla sicurezza applicativa, all'integrazione AI e alla containerizzazione dell'intero sistema.

---

## 1. Obiettivi del progetto

DocuEntitySeek è stato progettato per mettere in pratica competenze che coinvolgono l'intero ciclo di sviluppo di un'applicazione software.

Gli obiettivi principali sono:

- **Sviluppo frontend:** realizzare un'interfaccia React modulare, tipizzata e organizzata in componenti riutilizzabili.
- **Sviluppo backend:** progettare API REST con FastAPI e separare routing, logica applicativa, accesso ai dati e servizi.
- **Persistenza:** modellare un database relazionale PostgreSQL utilizzando SQLAlchemy.
- **Autenticazione e autorizzazione:** gestire utenti, JWT, ruoli, piani applicativi e controllo degli accessi alle risorse.
- **Integrazione AI:** utilizzare un modello NLP preaddestrato all'interno di una pipeline documentale.
- **Gestione dei documenti:** implementare caricamento, validazione, archiviazione privata e consultazione dei PDF.
- **Tracciabilità dei risultati:** collegare le informazioni estratte alle rispettive posizioni nel documento originale.
- **Infrastruttura:** containerizzare i componenti con Docker Compose, configurazioni esterne e volumi persistenti.
- **Testing e manutenibilità:** organizzare codice e test in modo da favorire evoluzione, debugging e riproducibilità.

L'Intelligenza Artificiale costituisce quindi una componente funzionale della piattaforma, ma non il suo unico obiettivo.

---

## 2. Funzionalità principali

### Gestione degli utenti

- Registrazione e autenticazione mediante JWT.
- Recupero del profilo autenticato.
- Ruoli applicativi `USER` e `ADMIN`.
- Gestione degli account attivi e disabilitati.
- Distinzione tra ruolo amministrativo e piano di utilizzo.
- Autorizzazione backend sulle risorse appartenenti agli utenti.

### Gestione dei documenti

- Caricamento di documenti PDF.
- Validazione del formato e delle dimensioni.
- Conteggio delle pagine.
- Archiviazione del file originale.
- Persistenza dei metadati in PostgreSQL.
- Elenco e consultazione dei documenti caricati.
- Visualizzazione del PDF originale tramite PDF.js.
- Accesso autenticato ai file con supporto HTTP Range.

### Analisi intelligente

- Estrazione del testo mediante PyMuPDF.
- Suddivisione del contenuto in pagine e intervalli testuali.
- Named Entity Recognition mediante GLiNER2.5.
- Estrazione di informazioni strutturate mediante schemi semantici.
- Gestione di documenti lunghi mediante chunking.
- Gestione di sovrapposizioni e candidati alternativi.
- Persistenza delle analisi e dei risultati.
- Consultazione dello storico delle elaborazioni.

### Visualizzazione dei risultati

- Presentazione delle entità riconosciute.
- Visualizzazione dei campi strutturati.
- Indicazione dei punteggi di confidenza, quando disponibili.
- Associazione dei risultati alle pagine e agli offset testuali.
- Evidenziazione delle occorrenze sul PDF originale, quando l'allineamento testuale lo consente.
- Filtri e navigazione tra i risultati.
- Consultazione delle precedenti analisi dello stesso documento.

### Schemi di estrazione

- Schema generale predefinito.
- Schemi personalizzati per gli utenti abilitati.
- Definizione di entità NER e campi IE personalizzati.
- Versionamento.
- Duplicazione e archiviazione.
- Associazione delle analisi alla versione dello schema utilizzata.

---

## 3. GLiNER2.5: scelta e integrazione del modello

DocuEntitySeek utilizza il modello:

```text
fastino/gliner2.5-multi-v1
```

Il checkpoint appartiene alla famiglia [GLiNER2](https://github.com/fastino-ai/GLiNER2) ed è progettato per attività di estrazione delle informazioni guidate da schemi.

### Perché GLiNER2?

La scelta di GLiNER2 è motivata da alcune caratteristiche particolarmente interessanti per un progetto di Document Intelligence.

**Estrazione guidata da schemi**

Il modello permette di specificare quali entità e informazioni ricercare, attraverso etichette e descrizioni semantiche.

Questo consente di progettare un sistema in cui le definizioni dei dati da estrarre sono separate dal codice della pipeline.

**Flessibilità tra domini applicativi**

Le tipologie di entità e i campi richiesti possono cambiare in funzione del documento e dello schema utilizzato.

Non è necessario sviluppare un classificatore distinto per ogni nuova etichetta NER. Tuttavia, la capacità di riconoscere correttamente categorie nuove dipende dal modello, dalla formulazione dello schema e dal dominio.

**Capacità multilingue**

Il checkpoint utilizzato è multilingue e permette di sperimentare l'estrazione su documenti in lingue differenti.

Il supporto multilingue non implica accuratezza uniforme per tutte le lingue o tipologie documentali.

**NER e Information Extraction**

La famiglia GLiNER2 supporta diverse attività NLP, comprese l'identificazione delle entità e l'estrazione di informazioni strutturate.

DocuEntitySeek si concentra attualmente su queste due funzionalità:

- **NER:** individuazione di occorrenze testuali riconducibili a categorie definite.
- **IE:** estrazione di valori associati a campi semantici, che possono rappresentare informazioni più articolate rispetto a singole entità.

**Inferenza locale**

GLiNER2 può essere eseguito direttamente nell'infrastruttura applicativa tramite PyTorch, senza inviare il contenuto dei documenti a servizi esterni di inferenza AI.

I pesi del modello possono essere scaricati da Hugging Face durante l'inizializzazione e conservati nella cache locale.

**Integrazione applicativa**

L'utilizzo di un modello preaddestrato permette di dedicare maggiore attenzione alla progettazione dei componenti che lo circondano: API, pipeline, persistenza, gestione degli errori e interfaccia.

### Cosa non è stato fatto

Nel progetto:

- non è stato eseguito fine-tuning di GLiNER2.5;
- non è stato realizzato un dataset annotato specifico per il progetto;
- non sono state condotte valutazioni sistematiche di precision, recall o F1-score;
- non sono stati sviluppati benchmark comparativi rispetto ad altri modelli;
- non sono garantite prestazioni equivalenti su tutte le lingue e tutti i domini.

I risultati AI devono essere considerati **indicativi e verificabili**, non necessariamente completi o corretti.

L'obiettivo non è dimostrare che GLiNER2.5 sia il modello migliore per ogni compito, ma mostrare come integrare un modello NLP in una piattaforma software strutturata.

Documentazione del modello: [Hugging Face — GLiNER2.5 Multilingual](https://huggingface.co/fastino/gliner2.5-multi-v1).

---

## 4. Named Entity Recognition e Information Extraction

DocuEntitySeek distingue due forme di estrazione.

### Named Entity Recognition

La NER individua segmenti di testo che corrispondono a tipologie di entità.

Esempio:

```text
Il 15 ottobre 2026 Mario Rossi ha incontrato
i rappresentanti di Example S.p.A. a Palermo.
```

Possibili risultati:

| Entità | Testo |
|---|---|
| PERSONA | Mario Rossi |
| DATA | 15 ottobre 2026 |
| ORGANIZZAZIONE | Example S.p.A. |
| LOCALITA | Palermo |

### Information Extraction

La Information Extraction cerca di ricavare informazioni associate a specifici campi semantici.

A differenza della semplice individuazione di entità, un campo IE può rappresentare un'informazione concettualmente più articolata.

Per esempio, da un documento amministrativo può essere richiesto di identificare:

```json
{
  "oggetto_principale": "Richiesta di autorizzazione per l'utilizzo di locali comunali"
}
```

L'estrazione dipende dalle capacità del modello e dalla presenza di informazioni riconoscibili nel documento.

Non equivale necessariamente a generazione libera di testo o riassunto astrattivo.

### Schema predefinito

DocuEntitySeek include lo schema built-in `general_document`, pensato per documenti di carattere generale.

Le entità NER predefinite sono:

| Etichetta | Significato |
|---|---|
| `PERSONA` | Nome e cognome di una persona |
| `ORGANIZZAZIONE` | Aziende, enti, istituzioni, associazioni e altre organizzazioni |
| `LOCALITA` | Luoghi, comuni, città, indirizzi e riferimenti geografici |
| `DATA` | Date, periodi e riferimenti temporali espressi come data |
| `ORA` | Orari e riferimenti temporali puntuali |
| `IMPORTO` | Somme di denaro e altri valori monetari |
| `EMAIL` | Indirizzi di posta elettronica |
| `TELEFONO` | Numeri telefonici e recapiti telefonici |
| `URL` | Indirizzi web e collegamenti Internet |
| `IDENTIFICATIVO` | Codici, numeri di protocollo, matricole e altri identificativi |

Il campo IE predefinito è:

| Campo | Chiave tecnica | Descrizione |
|---|---|---|
| Oggetto principale | `oggetto_principale` | Argomento o oggetto principale |

Questo schema viene inizializzato automaticamente tramite gli script SQL del progetto.

---

## 5. Architettura software

DocuEntitySeek adotta un'architettura full-stack con separazione tra interfaccia, API, logica applicativa, persistenza e inferenza AI.

```text
                       USER
                        |
                        v
                React + TypeScript
                        |
                        v
                Nginx (Portfolio)
                        |
                        v
                     FastAPI
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
     Application    AI Pipeline    Document
       Services          |          Storage
          |              |             |
          v              v             v
     Repositories    GLiNER2.5    S3-compatible
          |
          v
      SQLAlchemy
          |
          v
      PostgreSQL
```

### Frontend

Il frontend è sviluppato con React e TypeScript.

È responsabile di:

- navigazione tra le pagine;
- autenticazione e gestione della sessione;
- interazione con le API;
- caricamento e consultazione dei documenti;
- selezione degli schemi di estrazione;
- visualizzazione dello stato delle analisi;
- rendering dei risultati NER/IE;
- visualizzazione del PDF originale.

Il codice è organizzato separando componenti, pagine, hook, tipi e client API.

### Backend

Il backend è sviluppato con FastAPI.

Le principali responsabilità sono:

- esposizione delle API REST;
- validazione delle richieste;
- autenticazione e autorizzazione;
- gestione di utenti, documenti e schemi;
- applicazione delle quote;
- orchestrazione della pipeline AI;
- gestione dello storage;
- persistenza e recupero dei risultati.

L'accesso ai dati è organizzato mediante repository SQLAlchemy, mentre la logica applicativa risiede nei servizi dedicati.

### Database

PostgreSQL conserva le informazioni persistenti dell'applicazione.

Tra le principali entità del modello dati:

```text
users
plans

documents
document_pages

extraction_schemas
extraction_schema_versions
entity_definitions
field_definitions

ai_runtime_configs
analyses
entity_occurrences
extracted_fields
field_candidates
```

I file PDF originali non vengono memorizzati direttamente nel database: PostgreSQL conserva i metadati e i riferimenti allo storage.

### Document storage

La piattaforma supporta un'astrazione dello storage documentale.

Nell'ambiente Docker Portfolio è utilizzato uno storage privato S3-compatible basato su SILO.

I documenti sono recuperati dal backend tramite chiavi di storage e controlli di autorizzazione, senza esporre pubblicamente il bucket.

---

## 6. Pipeline di elaborazione documentale

Il flusso di analisi segue diverse fasi.

```text
PDF Upload
    |
    v
Validation & Storage
    |
    v
PDF Text Extraction (PyMuPDF)
    |
    v
Page Mapping & Text Provenance
    |
    v
Configurable Chunking
    |
    v
GLiNER2.5
    |
    +----------------------+
    |                      |
    v                      v
Named Entity          Structured
Recognition           Information
    |                 Extraction
    v                      v
Span Mapping          Field Resolution
    |                      |
    +-----------+----------+
                |
                v
        PostgreSQL Persistence
                |
                v
           Analysis API
                |
                v
       React / PDF.js Viewer
```

### Estrazione del testo

PyMuPDF estrae il contenuto testuale dalle singole pagine.

La pipeline conserva le informazioni necessarie a ricostruire le posizioni del testo originale, comprese pagina e offset.

### Gestione dei documenti lunghi

Il testo viene suddiviso in porzioni configurabili per adattarsi alla finestra di elaborazione del modello.

La configurazione iniziale prevede:

```text
chunk_size    = 512
chunk_overlap = 96
```

Questi valori sono parametri di elaborazione e non rappresentano una configurazione ottimizzata mediante benchmark.

### Esecuzione del modello

La pipeline utilizza un provider dedicato al caricamento e al riutilizzo del modello AI.

La configurazione runtime è persistita in PostgreSQL e comprende modello, soglie e parametri di elaborazione.

### Persistenza dei risultati

Entità, campi e relativi metadati vengono salvati nel database.

Ogni analisi mantiene il riferimento allo schema e alla configurazione AI utilizzati, facilitando la consultazione e il confronto delle esecuzioni.

---

## 7. Provenance e tracciabilità

Una delle caratteristiche progettuali di DocuEntitySeek è la **tracciabilità delle informazioni estratte**.

Quando disponibili, i risultati conservano:

- testo individuato;
- tipologia o chiave del campo;
- punteggio di confidenza;
- pagina di origine;
- offset nel testo globale;
- offset relativi alla pagina;
- eventuali valori candidati alternativi.

Queste informazioni permettono di collegare i risultati della pipeline AI al contenuto del documento originale.

Il viewer utilizza PDF.js e un servizio backend di geometria testuale per evidenziare le occorrenze riconosciute.

L'evidenziazione richiede la corrispondenza tra il testo utilizzato per l'analisi e quello individuato nel PDF originale. In caso di mancato allineamento, il sistema evita di associare coordinate non affidabili.

La tracciabilità non garantisce la correttezza semantica dell'estrazione: consente invece all'utente di verificarne più facilmente l'origine.

---

## 8. Schemi personalizzati e versionamento

Uno schema di estrazione definisce **quali informazioni ricercare**, mentre la pipeline stabilisce **come elaborare il documento**.

Questa separazione permette di modificare le definizioni NER e IE senza riscrivere l'intero processo di analisi.

Gli utenti abilitati possono:

- creare nuovi schemi;
- definire etichette e descrizioni delle entità;
- aggiungere campi strutturati;
- modificare gli schemi creando nuove versioni;
- duplicare schemi esistenti;
- archiviare gli schemi;
- selezionare la versione da utilizzare per un'analisi.

Una modifica non sovrascrive direttamente la versione precedente: viene creata una nuova versione dello schema.

Le analisi storiche conservano il riferimento alla versione utilizzata al momento dell'esecuzione.

Questo approccio favorisce la consistenza dei dati e la consultazione dei risultati nel tempo.

---

## 9. Autenticazione, ruoli e piani

DocuEntitySeek implementa un sistema dimostrativo di autorizzazione basato su utenti, ruoli e piani applicativi.

### Piano Base

Prevede:

- utilizzo dello schema built-in;
- NER e Information Extraction;
- visualizzazione dei documenti;
- consultazione delle analisi;
- quota giornaliera configurabile.

Il seed iniziale prevede **5 analisi al giorno**.

### Piano Premium

Aggiunge:

- assenza di un limite giornaliero applicativo configurato;
- creazione di schemi personalizzati;
- gestione delle definizioni NER e IE;
- versionamento;
- duplicazione;
- archiviazione degli schemi.

I controlli di autorizzazione sono applicati dal backend, non soltanto dall'interfaccia.

La distinzione Base/Premium è stata introdotta per sperimentare gestione delle funzionalità, quote e controllo degli accessi. **Non rappresenta un servizio commerciale di abbonamento o un'integrazione di pagamento.**

---

## 10. Stack tecnologico

| Area | Tecnologie |
|---|---|
| Frontend | React 19, TypeScript, Vite, React Router, CSS |
| Visualizzazione PDF | PDF.js |
| Backend | Python, FastAPI, Uvicorn, Pydantic |
| Persistenza | PostgreSQL, SQLAlchemy |
| AI / NLP | GLiNER2.5, PyTorch, Transformers |
| Estrazione PDF | PyMuPDF |
| Autenticazione | JWT |
| Storage | S3-compatible / SILO |
| Infrastruttura | Docker, Docker Compose, Nginx |
| Testing backend | pytest |
| Testing frontend | Vitest, React Testing Library |
| Qualità del codice | TypeScript, Oxlint |

Il progetto distingue un ambiente di sviluppo da un ambiente Docker Portfolio, destinato a dimostrare l'integrazione dei diversi componenti.

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
|   |   +-- pipeline/
|   |   +-- repositories/
|   |   +-- schemas/
|   |   +-- services/
|   +-- sql/
|   |   +-- 01_schema.sql
|   |   +-- 02_seed.sql
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
|   +-- package.json
|   +-- README.md
|
+-- docs/
|
+-- compose.portfolio.yaml
+-- .env.portfolio.example
+-- README.md
```

La struttura mostrata è una rappresentazione sintetica delle principali directory e dei file di configurazione.

Per ulteriori dettagli:

- [Documentazione backend](backend/README.md)
- [Documentazione frontend](frontend/README.md)

---

## 12. Avvio con Docker Compose

L'ambiente Docker Portfolio permette di avviare i principali componenti dell'applicazione in container separati.

I servizi comprendono:

- PostgreSQL;
- storage S3-compatible SILO;
- inizializzazione dello storage;
- backend FastAPI;
- frontend React distribuito tramite Nginx.

### Prerequisiti

- Git;
- Docker Desktop oppure Docker Engine con Docker Compose;
- risorse hardware sufficienti per eseguire PostgreSQL, i servizi web e l'inferenza GLiNER2.5.

L'inferenza su CPU è supportata, ma può essere più lenta rispetto a un ambiente con accelerazione hardware.

### 12.1. Configurazione

Clonare il repository e posizionarsi nella directory principale.

Creare il file `.env.portfolio` partendo dall'esempio:

```powershell
Copy-Item .env.portfolio.example .env.portfolio
```

Configurare le variabili richieste, tra cui:

```text
POSTGRES_ADMIN_PASSWORD
APP_DB_PASSWORD
JWT_SECRET_KEY
MINIO_ROOT_USER
MINIO_ROOT_PASSWORD
```

È possibile configurare anche l'indirizzo email utilizzato dalla pagina dimostrativa Premium.

Non inserire password reali, token o altri segreti nei file versionati.

### 12.2. Verifica della configurazione

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml config --quiet
```

### 12.3. Avvio

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml up -d --build
```

Controllare lo stato dei servizi:

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml ps -a
```

Il servizio di inizializzazione S3 può terminare con codice `0` dopo aver creato il bucket privato: non è necessario che rimanga costantemente in esecuzione.

### 12.4. Accesso all'applicazione

Frontend:

```text
http://localhost:8080
```

API health check tramite Nginx:

```text
http://localhost:8080/api/v1/health
```

Console dello storage SILO:

```text
http://localhost:9004
```

Le porte dell'ambiente Portfolio sono configurate per l'utilizzo locale.

### 12.5. Primo avvio del modello

Il primo caricamento di GLiNER2.5 potrebbe richiedere il download dei pesi da Hugging Face.

L'operazione dipende dalla connettività e dalle risorse disponibili. I file scaricati vengono conservati nella cache persistente configurata per l'ambiente Portfolio.

Un tempo elevato durante la prima analisi non indica necessariamente un errore della pipeline.

### 12.6. Arresto

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml down
```

Il comando arresta i servizi senza eliminare i volumi persistenti.

**Attenzione:** l'utilizzo dell'opzione `-v` comporta la rimozione dei volumi gestiti dal progetto Compose e può causare la perdita dei dati del relativo ambiente.

---

## 13. Sviluppo locale

Frontend e backend possono essere avviati separatamente durante lo sviluppo.

### Backend

Dalla directory `backend/`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Configurare le variabili d'ambiente utilizzando il file di esempio del backend e predisporre i servizi richiesti, compreso PostgreSQL.

Avviare FastAPI:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Documentazione interattiva delle API:

```text
http://127.0.0.1:8000/docs
```

### Frontend

Dalla directory `frontend/`:

```powershell
npm ci
npm run dev
```

Indirizzo di sviluppo:

```text
http://localhost:5173
```

La configurazione `VITE_API_BASE_URL` deve puntare al backend FastAPI.

Per la configurazione specifica dei singoli componenti, consultare i rispettivi README.

---

## 14. Testing e verifiche

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
npm run lint
npm run build
```

I test frontend possono essere eseguiti con gli script previsti in `frontend/package.json`.

### Verifiche di integrazione

L'ambiente Portfolio è stato utilizzato per verificare manualmente il flusso:

```text
Registrazione
    |
    v
Login
    |
    v
Upload PDF
    |
    v
Persistenza PostgreSQL / S3
    |
    v
Analisi GLiNER2.5
    |
    v
Risultati NER / IE
    |
    v
Visualizzazione PDF.js
```

Queste verifiche dimostrano il funzionamento del percorso applicativo principale, ma **non costituiscono una certificazione completa di affidabilità, sicurezza o prestazioni in produzione**.

---

## 15. Sicurezza e gestione dei dati

Il progetto implementa diverse misure di sicurezza applicativa:

- autenticazione JWT;
- protezione delle risorse in base al proprietario;
- controllo dei ruoli e dei piani;
- verifica delle quote lato backend;
- validazione dei file caricati;
- storage privato;
- accesso autenticato ai PDF;
- separazione delle configurazioni tramite variabili d'ambiente.

### Inferenza self-hosted

L'esecuzione locale del modello consente di elaborare i documenti senza trasmetterli a provider esterni di inferenza AI.

Questa caratteristica rappresenta un vantaggio architetturale per applicazioni che richiedono maggiore controllo sul trattamento dei documenti.

Tuttavia, **inferenza locale non significa automaticamente sicurezza completa o conformità normativa**.

Il trattamento di documenti sensibili richiede ulteriori valutazioni relative a infrastruttura, accessi, logging, gestione dei segreti, cifratura, backup e protezione dei dati.

DocuEntitySeek deve essere considerato un progetto dimostrativo, non una piattaforma certificata per la gestione di informazioni riservate.

---

## 16. Limitazioni e scelte progettuali

Le principali limitazioni attuali sono:

**Modello non specializzato**

GLiNER2.5 viene utilizzato senza fine-tuning specifico. Le prestazioni possono variare significativamente a seconda dei documenti, delle lingue e degli schemi.

**Assenza di valutazione quantitativa**

Il progetto non presenta metriche sperimentali sufficienti per dichiarare un livello di accuratezza del modello.

**Elaborazione AI sincrona**

L'esecuzione della pipeline avviene attualmente all'interno del processo applicativo backend, mantenendo la richiesta HTTP aperta durante l'elaborazione.

Un sistema dedicato di job queue e worker rappresenterebbe un'evoluzione utile per carichi più elevati.

**Tempi di esecuzione**

Il caricamento del modello e l'inferenza possono richiedere risorse e tempi significativi, soprattutto su CPU o con documenti lunghi.

**Assenza di OCR integrato**

I documenti PDF privi di testo digitale estraibile non vengono attualmente elaborati tramite un sistema OCR dedicato.

**Limiti della provenance**

L'evidenziazione delle informazioni dipende dalla possibilità di allineare correttamente il testo estratto alle posizioni nel PDF originale.

**Ambiente dimostrativo**

La configurazione Docker Portfolio semplifica l'avvio e la riproducibilità dell'applicazione, ma non deve essere considerata automaticamente adatta a un'esposizione pubblica in produzione.

---

## 17. Possibili evoluzioni

Tra i possibili sviluppi futuri:

- pipeline asincrona con job queue e worker dedicati;
- OCR per documenti scansionati;
- ampliamento dei test automatici e dei test end-to-end;
- osservabilità e monitoraggio;
- miglioramento della gestione di errori e interruzioni;
- valutazione quantitativa delle estrazioni;
- sperimentazione di fine-tuning o modelli alternativi;
- ottimizzazione delle risorse e delle prestazioni;
- deployment cloud e hardening infrastrutturale.

Questi aspetti costituiscono opportunità di evoluzione e non funzionalità già disponibili.

---

## 18. Principio architetturale

DocuEntitySeek si fonda sulla separazione concettuale tra:

```text
MODELLO AI
    !=
SCHEMA DI ESTRAZIONE
    !=
PIPELINE DOCUMENTALE
    !=
LOGICA APPLICATIVA
    !=
INTERFACCIA UTENTE
```

Il modello AI è il componente che effettua l'inferenza.

Lo schema definisce quali informazioni richiedere.

La pipeline prepara il documento, coordina l'estrazione e gestisce i risultati.

Il backend applica le regole di business e rende disponibili i dati attraverso API.

Il frontend permette all'utente di interagire con il sistema.

Questa distinzione favorisce modularità, manutenibilità e possibilità di evoluzione.

---

## 19. Conclusioni

DocuEntitySeek è un progetto didattico che utilizza la Document Intelligence come contesto applicativo per affrontare problematiche concrete di **sviluppo software full-stack**.

Il valore principale del progetto risiede nell'integrazione di tecnologie e responsabilità differenti: frontend, backend, database, autenticazione, storage, pipeline NLP, persistenza, visualizzazione e infrastruttura Docker.

GLiNER2.5 permette di sperimentare l'estrazione di informazioni attraverso un approccio flessibile e guidato da schemi, senza sviluppare da zero un modello di Named Entity Recognition o Information Extraction.

**L'obiettivo di DocuEntitySeek non è dimostrare le migliori prestazioni possibili di un modello AI, ma progettare e realizzare un'applicazione full-stack completa, modulare e concretamente funzionante che integri capacità di elaborazione intelligente dei documenti.**

---

## Riferimenti

- [GLiNER2 — Repository ufficiale](https://github.com/fastino-ai/GLiNER2)
- [GLiNER2.5 Multilingual — Model Card](https://huggingface.co/fastino/gliner2.5-multi-v1)
- [GLiNER2 — Articolo scientifico](https://arxiv.org/abs/2507.18546)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [PyMuPDF](https://pymupdf.readthedocs.io/)
- [PDF.js](https://mozilla.github.io/pdf.js/)
- [Docker](https://docs.docker.com/)