# DocuEntitySeek

**Full-Stack Document Intelligence Platform | React · FastAPI · PostgreSQL · GLiNER2.5**

DocuEntitySeek is an educational, portfolio-oriented **Document Intelligence web platform** designed to process PDF documents, identify named entities through *Named Entity Recognition (NER)*, and extract structured information through *Information Extraction (IE)* using customizable semantic schemas.

The platform integrates a React frontend, a FastAPI backend, a PostgreSQL database, S3-compatible document storage, and a self-hosted NLP model, providing an end-to-end workflow for document processing, result persistence, and interactive visualization.

> **Project Purpose**
>
> DocuEntitySeek is an educational and professional portfolio project primarily intended to explore and demonstrate the design, development, and integration of a **full-stack application with Artificial Intelligence capabilities**.
>
> The project **does not focus on optimizing GLiNER2.5 model performance**. The model is used in its pretrained form, without task-specific fine-tuning, comparative benchmarking, or domain-specific training.
>
> The primary focus is on software architecture, separation of concerns, data management, API design, application security, AI integration, and containerization of the complete system.

---

## 1. Project Objectives

DocuEntitySeek was designed to provide practical experience across the full software development lifecycle.

Its main objectives are:

- **Frontend development:** Build a modular, strongly typed React interface using reusable components.
- **Backend development:** Design REST APIs with FastAPI and separate routing, business logic, data access, and application services.
- **Data persistence:** Design and manage a relational PostgreSQL database using SQLAlchemy.
- **Authentication and authorization:** Implement JWT authentication, user roles, application plans, and resource-level access control.
- **AI integration:** Incorporate a pretrained NLP model into a document processing pipeline.
- **Document management:** Implement PDF uploads, validation, private storage, and document retrieval.
- **Result traceability:** Associate extracted information with its original location within a document.
- **Infrastructure:** Containerize the application using Docker Compose, environment-based configuration, and persistent volumes.
- **Testing and maintainability:** Organize source code and tests to support future development, debugging, and reproducibility.

Artificial Intelligence is therefore an important functional component of the platform, but not its sole purpose.

---

## 2. Core Features

### User Management

- User registration and JWT authentication.
- Authenticated user profile retrieval.
- Application roles: `USER` and `ADMIN`.
- Active and disabled user accounts.
- Separation between administrative roles and subscription plans.
- Backend authorization based on resource ownership.

### Document Management

- PDF document uploads.
- File format and size validation.
- PDF page counting.
- Original document storage.
- Document metadata persistence in PostgreSQL.
- Document listing and retrieval.
- Original PDF visualization using PDF.js.
- Authenticated document access with HTTP Range support.

### Intelligent Document Analysis

- Text extraction using PyMuPDF.
- Document processing with page and text-offset mapping.
- Named Entity Recognition using GLiNER2.5.
- Structured Information Extraction using semantic schemas.
- Long-document processing through configurable chunking.
- Overlap handling and alternative candidate management.
- Persistent analysis results.
- Analysis history and retrieval.

### Result Visualization

- Display of recognized entities.
- Structured field visualization.
- Confidence scores, when available.
- Page references and text offsets.
- Highlighting of extracted occurrences in the original PDF when text alignment is available.
- Result filtering and navigation.
- Access to previous analyses of the same document.

### Extraction Schemas

- Built-in general-purpose extraction schema.
- Custom schemas for authorized users.
- Custom NER entity definitions and IE fields.
- Schema versioning.
- Schema duplication and archiving.
- Association between analysis results and the schema version used.

---

## 3. GLiNER2.5: Model Selection and Integration

DocuEntitySeek uses the following model:

```text
fastino/gliner2.5-multi-v1
```

This checkpoint belongs to the [GLiNER2](https://github.com/fastino-ai/GLiNER2) family and is designed to support schema-driven information extraction tasks.

### Why GLiNER2?

GLiNER2 was selected because of several characteristics that make it particularly suitable for a Document Intelligence application.

**Schema-Driven Extraction**

The model allows developers to specify which entities and information should be extracted using semantic labels and descriptions.

This makes it possible to separate extraction requirements from the implementation of the processing pipeline.

**Cross-Domain Flexibility**

Entity categories and structured fields can be adapted to different document types and application domains.

A separate trained classifier is not necessarily required for every new NER label. However, extraction quality depends on the model, schema descriptions, and target domain.

**Multilingual Capabilities**

The selected checkpoint is multilingual, allowing experimentation with documents written in different languages.

Multilingual support does not imply uniform accuracy across all languages or document categories.

**NER and Information Extraction**

The GLiNER2 family supports multiple NLP extraction tasks, including named entity recognition and structured information extraction.

DocuEntitySeek currently focuses on two capabilities:

- **Named Entity Recognition (NER):** Identifying text spans corresponding to predefined or dynamically specified entity categories.
- **Information Extraction (IE):** Extracting values associated with semantic fields, which may represent more complex information than individual named entities.

**Self-Hosted Inference**

GLiNER2 can run directly within the application infrastructure through PyTorch, without sending document contents to external AI inference services.

Model weights may be downloaded from Hugging Face during initialization and subsequently stored in a local cache.

**Application-Level Integration**

Using a pretrained model makes it possible to focus development efforts on the surrounding software architecture, including APIs, processing pipelines, persistence, error handling, and user interfaces.

### What Has Not Been Done

Within this project:

- GLiNER2.5 has not been fine-tuned.
- No project-specific annotated training dataset has been created.
- No systematic precision, recall, or F1-score evaluation has been conducted.
- No comparative benchmarks against alternative models have been performed.
- No uniform performance guarantees are provided across languages or document domains.

AI-generated results should therefore be considered **indicative and subject to verification**, rather than necessarily complete or accurate.

The purpose is not to demonstrate that GLiNER2.5 is the best-performing model for every extraction task, but to illustrate how a pretrained NLP model can be integrated into a structured software platform.

Model documentation: [Hugging Face — GLiNER2.5 Multilingual](https://huggingface.co/fastino/gliner2.5-multi-v1).

---

## 4. Named Entity Recognition and Information Extraction

DocuEntitySeek distinguishes between two types of information extraction.

### Named Entity Recognition

NER identifies text spans corresponding to specific entity categories.

Example:

```text
On October 15, 2026, Mario Rossi met with
representatives of Example S.p.A. in Palermo.
```

Possible results:

| Entity | Extracted Text |
|---|---|
| PERSONA | Mario Rossi |
| DATA | October 15, 2026 |
| ORGANIZZAZIONE | Example S.p.A. |
| LOCALITA | Palermo |

### Information Extraction

Information Extraction aims to retrieve values associated with specific semantic fields.

Unlike simple named entity identification, an IE field may represent a conceptually more complex piece of information.

For example, an administrative document might contain information corresponding to:

```json
{
  "oggetto_principale": "Request for authorization to use municipal facilities"
}
```

Extraction depends on the model's capabilities and the presence of identifiable information in the document.

It does not necessarily represent free-form text generation or abstractive summarization.

### Default Extraction Schema

DocuEntitySeek includes the built-in `general_document` schema, designed for general-purpose documents.

The default NER entities are:

| Entity Label | Description |
|---|---|
| `PERSONA` | First and last name of a person |
| `ORGANIZZAZIONE` | Companies, public bodies, institutions, associations, and other organizations |
| `LOCALITA` | Places, municipalities, cities, addresses, and geographical references |
| `DATA` | Dates, periods, and date-based temporal references |
| `ORA` | Times and specific temporal references |
| `IMPORTO` | Monetary amounts and financial values |
| `EMAIL` | Email addresses |
| `TELEFONO` | Telephone numbers and contact numbers |
| `URL` | Web addresses and Internet links |
| `IDENTIFICATIVO` | Codes, protocol numbers, registration numbers, and other identifiers |

The default Information Extraction field is:

| Field | Technical Key | Description |
|---|---|---|
| Main Subject | `oggetto_principale` | Main topic or subject of the document |

This schema is automatically initialized through the project's SQL seed scripts.

---

## 5. Software Architecture

DocuEntitySeek follows a full-stack architecture that separates the user interface, APIs, application logic, data persistence, and AI inference.

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

The frontend is developed using React and TypeScript.

Its responsibilities include:

- Application routing and navigation.
- Authentication and session management.
- API communication.
- Document upload and management.
- Extraction schema selection.
- Analysis status visualization.
- NER and IE result rendering.
- Original PDF visualization.

The source code is organized into separate components, pages, hooks, types, and API clients.

### Backend

The backend is developed using FastAPI.

Its main responsibilities include:

- Exposing REST endpoints.
- Request validation.
- Authentication and authorization.
- User, document, and schema management.
- Analysis quota enforcement.
- AI pipeline orchestration.
- Document storage management.
- Result persistence and retrieval.

Data access is organized through SQLAlchemy repositories, while business logic is implemented in dedicated application services.

### Database

PostgreSQL stores the application's persistent data.

The main database entities include:

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

Original PDF files are not stored directly in PostgreSQL. Instead, the database maintains document metadata and references to the storage system.

### Document Storage

The platform implements an abstraction for document storage.

The Docker Portfolio environment uses private S3-compatible storage powered by SILO.

Documents are accessed through the backend using storage keys and authorization checks, without exposing the storage bucket publicly.

---

## 6. Document Processing Pipeline

Document analysis follows several processing stages.

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

### Text Extraction

PyMuPDF extracts textual content from individual document pages.

The pipeline preserves the information required to reconstruct the original text positions, including page numbers and offsets.

### Long-Document Processing

Document text is divided into configurable chunks to accommodate the model's processing window.

The initial configuration uses:

```text
chunk_size    = 512
chunk_overlap = 96
```

These values are processing parameters and should not be interpreted as benchmark-optimized settings.

### Model Execution

The pipeline uses a dedicated model provider responsible for model loading and reuse.

Runtime AI configuration is persisted in PostgreSQL and includes the model identifier, confidence thresholds, and processing parameters.

### Result Persistence

Recognized entities, extracted fields, and their associated metadata are stored in the database.

Each analysis maintains references to the extraction schema and AI configuration used, supporting historical inspection and comparison.

---

## 7. Provenance and Traceability

One of the main architectural features of DocuEntitySeek is **extraction traceability**.

When available, extraction results preserve:

- Extracted text.
- Entity label or field identifier.
- Confidence score.
- Source page.
- Global text offsets.
- Page-relative text offsets.
- Alternative candidate values, where applicable.

This information makes it possible to associate AI-generated results with their original document context.

The document viewer combines PDF.js with a backend text geometry service to highlight recognized occurrences.

Highlighting requires a valid alignment between the text used during analysis and the original PDF content. When alignment cannot be verified, the system avoids displaying potentially incorrect coordinates.

Traceability does not guarantee semantic correctness. Instead, it allows users to inspect and verify the origin of extracted information more easily.

---

## 8. Custom Extraction Schemas and Versioning

An extraction schema defines **what information should be extracted**, while the processing pipeline determines **how the document is analyzed**.

This separation allows NER and IE definitions to change without rewriting the entire analysis workflow.

Authorized users can:

- Create custom extraction schemas.
- Define entity labels and descriptions.
- Add structured extraction fields.
- Modify schemas through versioning.
- Duplicate existing schemas.
- Archive schemas.
- Select a schema version for document analysis.

Schema updates do not overwrite previous versions. Instead, a new version is created.

Historical analyses retain references to the schema versions used during execution.

This approach improves data consistency and supports historical result inspection.

---

## 9. Authentication, Roles, and Application Plans

DocuEntitySeek implements a demonstration-oriented authorization system based on users, roles, and application plans.

### Base Plan

The Base plan includes:

- Access to the built-in extraction schema.
- Named Entity Recognition.
- Structured Information Extraction.
- Document visualization.
- Analysis history.
- A configurable daily analysis quota.

The initial database seed configures a limit of **5 analyses per day**.

### Premium Plan

The Premium plan additionally provides:

- No configured application-level daily analysis limit.
- Custom extraction schema creation.
- Custom NER and IE definitions.
- Schema versioning.
- Schema duplication.
- Schema archiving.

Authorization rules are enforced by the backend rather than relying exclusively on frontend visibility.

The Base/Premium distinction was implemented to explore feature-based access control, analysis quotas, and application authorization.

**It does not represent a commercial subscription service or payment integration.**

---

## 10. Technology Stack

| Area | Technologies |
|---|---|
| Frontend | React 19, TypeScript, Vite, React Router, CSS |
| PDF Visualization | PDF.js |
| Backend | Python, FastAPI, Uvicorn, Pydantic |
| Data Persistence | PostgreSQL, SQLAlchemy |
| AI / NLP | GLiNER2.5, PyTorch, Transformers |
| PDF Processing | PyMuPDF |
| Authentication | JWT |
| Storage | S3-compatible / SILO |
| Infrastructure | Docker, Docker Compose, Nginx |
| Backend Testing | pytest |
| Frontend Testing | Vitest, React Testing Library |
| Code Quality | TypeScript, Oxlint |

The project provides separate configurations for local development and a Docker Portfolio environment intended to demonstrate the integration of the complete application stack.

---

## 11. Repository Structure

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

This structure provides a simplified overview of the main directories and configuration files.

For additional technical details:

- [Backend Documentation](backend/README.md)
- [Frontend Documentation](frontend/README.md)

---

## 12. Running the Application with Docker Compose

The Docker Portfolio environment allows the main application components to run in separate containers.

The services include:

- PostgreSQL database.
- SILO S3-compatible storage.
- Storage initialization service.
- FastAPI backend.
- React frontend served by Nginx.

### Prerequisites

- Git.
- Docker Desktop or Docker Engine with Docker Compose.
- Sufficient hardware resources to run PostgreSQL, web services, and GLiNER2.5 inference.

CPU-based inference is supported, although it may be slower than execution on hardware with dedicated acceleration.

### 12.1. Configuration

Clone the repository and navigate to the project root.

Create `.env.portfolio` from the provided example:

```powershell
Copy-Item .env.portfolio.example .env.portfolio
```

Configure the required environment variables, including:

```text
POSTGRES_ADMIN_PASSWORD
APP_DB_PASSWORD
JWT_SECRET_KEY
MINIO_ROOT_USER
MINIO_ROOT_PASSWORD
```

The email address displayed on the demonstration Premium page can also be configured.

Never commit real passwords, authentication tokens, or secrets to version control.

### 12.2. Configuration Validation

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml config --quiet
```

### 12.3. Starting the Application

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml up -d --build
```

Check the status of the services:

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml ps -a
```

The S3 initialization service may exit successfully with code `0` after creating the private storage bucket. It does not need to remain running.

### 12.4. Accessing the Application

Frontend:

```text
http://localhost:8080
```

API health check through Nginx:

```text
http://localhost:8080/api/v1/health
```

SILO storage console:

```text
http://localhost:9004
```

The Portfolio environment is configured for local access.

### 12.5. First Model Initialization

The first GLiNER2.5 execution may require downloading model weights from Hugging Face.

This process depends on network connectivity and available system resources. Downloaded model files are stored in the persistent cache configured for the Portfolio environment.

A longer processing time during the first analysis does not necessarily indicate a pipeline error.

### 12.6. Stopping the Application

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml down
```

This command stops the services without deleting persistent volumes.

**Warning:** Using the `-v` option removes volumes managed by the Compose project and may result in data loss within that environment.

---

## 13. Local Development

The frontend and backend can also be started independently during development.

### Backend

From the `backend/` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Configure the environment variables using the backend's example configuration and initialize the required services, including PostgreSQL.

Start FastAPI:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### Frontend

From the `frontend/` directory:

```powershell
npm ci
npm run dev
```

Development URL:

```text
http://localhost:5173
```

The `VITE_API_BASE_URL` environment variable must point to the FastAPI backend.

Refer to the component-specific README files for additional configuration details.

---

## 14. Testing and Validation

### Backend

```powershell
cd backend
python -m pytest
```

Python syntax validation:

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

Frontend tests can be executed using the scripts defined in `frontend/package.json`.

### Integration Validation

The Docker Portfolio environment has been used to manually verify the main application workflow:

```text
Registration
    |
    v
Login
    |
    v
PDF Upload
    |
    v
PostgreSQL / S3 Persistence
    |
    v
GLiNER2.5 Analysis
    |
    v
NER / IE Results
    |
    v
PDF.js Visualization
```

These checks demonstrate that the core application workflow is operational.

However, **they do not constitute comprehensive certification of production reliability, security, or performance**.

---

## 15. Security and Data Handling

The project implements several application-level security measures:

- JWT authentication.
- Resource ownership enforcement.
- Role-based and plan-based authorization.
- Backend analysis quota enforcement.
- Uploaded file validation.
- Private document storage.
- Authenticated PDF access.
- Environment-based configuration.

### Self-Hosted AI Inference

Running the NLP model within the application infrastructure allows documents to be processed without transmitting their contents to external AI inference providers.

This is an architectural advantage for applications requiring greater control over document processing.

However, **local inference does not automatically guarantee complete security or regulatory compliance**.

Processing sensitive documents requires additional consideration of infrastructure security, access management, logging, secret management, encryption, backups, and data protection requirements.

DocuEntitySeek should be considered a demonstration project rather than a certified platform for handling confidential information.

---

## 16. Current Limitations and Design Trade-offs

The main current limitations include:

**Non-Specialized Model**

GLiNER2.5 is used without task-specific fine-tuning. Extraction quality may vary considerably across document types, languages, and schemas.

**No Quantitative Model Evaluation**

The project does not provide sufficient experimental metrics to claim a specific level of model accuracy.

**Synchronous AI Processing**

The AI pipeline currently runs within the backend application process, keeping the HTTP request open while the analysis is performed.

A dedicated job queue and worker architecture would be a useful improvement for higher workloads.

**Execution Time and Resource Requirements**

Model loading and inference can require significant resources, particularly when processing long documents or running on CPU.

**No Integrated OCR**

PDF documents containing only scanned images are not currently processed through a dedicated OCR system.

**Provenance Limitations**

Text highlighting depends on the ability to accurately align extracted text with its corresponding location in the original PDF.

**Demonstration Environment**

The Docker Portfolio configuration simplifies application startup and reproducibility, but should not automatically be considered suitable for publicly exposed production deployments.

---

## 17. Potential Future Improvements

Possible future developments include:

- Asynchronous processing using dedicated job queues and workers.
- OCR support for scanned documents.
- Extended automated and end-to-end testing.
- Observability and monitoring.
- Improved error handling and interruption recovery.
- Quantitative extraction evaluation.
- Fine-tuning experiments or integration of alternative NLP models.
- Resource and performance optimization.
- Cloud deployment and infrastructure security hardening.

These represent potential improvements rather than currently available features.

---

## 18. Architectural Principles

DocuEntitySeek is based on a conceptual separation between:

```text
AI MODEL
    !=
EXTRACTION SCHEMA
    !=
DOCUMENT PROCESSING PIPELINE
    !=
APPLICATION LOGIC
    !=
USER INTERFACE
```

The AI model performs inference.

The extraction schema defines the information to retrieve.

The pipeline prepares documents, coordinates extraction, and processes results.

The backend enforces business rules and exposes data through APIs.

The frontend provides the user interface for interacting with the system.

This separation promotes modularity, maintainability, and future extensibility.

---

## 19. Conclusion

DocuEntitySeek is an educational project that uses Document Intelligence as a practical application domain for exploring real-world **full-stack software development challenges**.

Its primary value lies in the integration of multiple technologies and responsibilities: frontend development, backend services, relational databases, authentication, document storage, NLP pipelines, data persistence, interactive visualization, and Docker infrastructure.

GLiNER2.5 makes it possible to experiment with flexible, schema-driven information extraction without developing a Named Entity Recognition or Information Extraction model from scratch.

**The goal of DocuEntitySeek is not to demonstrate state-of-the-art AI model performance, but to design and implement a complete, modular, and functional full-stack application that integrates intelligent document processing capabilities.**

---

## References

- [GLiNER2 — Official Repository](https://github.com/fastino-ai/GLiNER2)
- [GLiNER2.5 Multilingual — Model Card](https://huggingface.co/fastino/gliner2.5-multi-v1)
- [GLiNER2 — Research Paper](https://arxiv.org/abs/2507.18546)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [PyMuPDF](https://pymupdf.readthedocs.io/)
- [PDF.js](https://mozilla.github.io/pdf.js/)
- [Docker](https://docs.docker.com/)