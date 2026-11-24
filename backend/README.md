# DocuEntitySeek — Backend

**FastAPI · PostgreSQL · SQLAlchemy · GLiNER2.5 · S3-Compatible Storage**

Python backend for **DocuEntitySeek**, a full-stack Document Intelligence platform designed to process PDF documents through Named Entity Recognition (NER) and Structured Information Extraction (IE).

The backend exposes REST APIs, handles authentication and authorization, coordinates data and document persistence, enforces business rules, and integrates a self-hosted NLP pipeline powered by GLiNER2.5.

> **Educational Purpose**
>
> DocuEntitySeek is an educational and professional portfolio project primarily focused on designing and developing full-stack applications with AI capabilities.
>
> GLiNER2.5 is used in its pretrained form, without task-specific fine-tuning. The project does not aim to optimize or demonstrate model performance through benchmarking.
>
> The backend is intended to demonstrate how an NLP model can be integrated into a modular software architecture, with particular attention to API design, application services, persistence, application security, document management, traceability, and infrastructure.

For an overview of the complete platform, see the [main README](../README.md).

---

## 1. Objectives and Responsibilities

The backend is the central application layer of DocuEntitySeek.

Its main responsibilities include:

- Exposing REST APIs using FastAPI.
- Validating requests and data using Pydantic.
- Managing user registration, JWT authentication, and authorization.
- Enforcing application roles, plans, and daily analysis quotas.
- Managing PDF documents and metadata.
- Storing original documents through a dedicated storage abstraction.
- Managing built-in and custom extraction schemas.
- Orchestrating document processing workflows.
- Integrating GLiNER2.5 for NER and Information Extraction.
- Persisting analyses, named entities, extracted fields, and associated metadata.
- Providing analysis results and PDF geometry information to the frontend.
- Managing application errors, logging, and environment configuration.

Business logic, data access, and AI inference are kept separate from HTTP route handlers.

---

## 2. Technology Stack

| Area | Technologies |
|---|---|
| Language | Python |
| REST API | FastAPI, Uvicorn |
| Validation and configuration | Pydantic, pydantic-settings |
| Persistence | PostgreSQL, SQLAlchemy |
| Authentication | JWT, password hashing |
| PDF processing | PyMuPDF |
| AI / NLP | GLiNER2.5, PyTorch, Transformers |
| Document storage | Local filesystem, S3-compatible / SILO |
| Testing | pytest |
| Infrastructure | Docker, Docker Compose |

NLP inference runs directly within the application infrastructure, without relying on external commercial AI inference APIs.

---

## 3. Backend Architecture

The project follows a modular architecture based on separation of concerns.

```text
HTTP Request
     |
     v
FastAPI Router
     |
     v
Pydantic Validation
     |
     v
Dependency Injection
     |
     v
Application Services
     |
     +----------------+----------------+
     |                |                |
     v                v                v
Repositories      AI Pipeline     Document Storage
     |                |                |
     v                v                v
SQLAlchemy       GLiNER2.5       Local / S3
     |
     v
PostgreSQL
```

### API Routes

Route handlers manage HTTP requests, parameters, status codes, and response serialization.

They do not directly implement SQL queries or model inference logic.

### Application Services

Application services implement business rules and coordinate high-level operations.

The main services include:

- `AuthService`
- `DocumentService`
- `AnalysisService`
- `AnalysisQueryService`
- `AnalysisQuotaService`
- `SchemaAccessService`
- `CustomSchemaService`

### Repositories

Repositories encapsulate PostgreSQL data access through SQLAlchemy.

This allows business logic to remain independent of persistence operations.

### AI Pipeline

The AI pipeline contains components responsible for document preparation, configuration resolution, model loading, named entity recognition, structured extraction, text-offset mapping, and result persistence.

### Dependency Injection

The `app/dependencies.py` module defines and connects dependencies used by API routes, including application services, SQLAlchemy sessions, authentication, storage, and AI components.

---

## 4. Project Structure

```text
backend/
|
+-- app/
|   +-- api/
|   |   +-- routes/
|   |   +-- router.py
|   |
|   +-- core/
|   |   +-- config.py
|   |   +-- security.py
|   |   +-- exceptions.py
|   |   +-- error_handlers.py
|   |   +-- logging.py
|   |
|   +-- db/
|   |   +-- models.py
|   |   +-- session.py
|   |
|   +-- domain/
|   +-- pipeline/
|   +-- repositories/
|   +-- schemas/
|   +-- services/
|   |
|   +-- dependencies.py
|   +-- main.py
|
+-- sql/
|   +-- 01_schema.sql
|   +-- 02_seed.sql
|
+-- tests/
+-- requirements.txt
+-- .env.example
+-- README.md
```

This structure illustrates the main modules. Additional specialized components are organized within their respective directories.

---

## 5. REST API

The API uses the following prefix:

```text
/api/v1
```

### Authentication and Users

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/token` | Authenticate and issue a JWT |
| GET | `/auth/me` | Retrieve the authenticated user |
| GET | `/auth/me/analysis-quota` | Retrieve daily analysis quota |
| GET | `/admin/users` | List users; administrator access required |

Login uses the OAuth2 Password Request Form format.

### Documents

| Method | Endpoint | Description |
|---|---|---|
| GET | `/documents` | List the authenticated user's documents |
| POST | `/documents` | Upload a PDF document |
| GET | `/documents/{document_id}` | Retrieve document details |
| GET | `/documents/{document_id}/file` | Retrieve the original PDF with authentication |

The document file endpoint supports HTTP Range requests for partial content retrieval.

### Analyses

| Method | Endpoint | Description |
|---|---|---|
| POST | `/documents/{document_id}/analyses` | Start a document analysis |
| GET | `/documents/{document_id}/analyses` | Retrieve analysis history |
| GET | `/documents/{document_id}/analyses/{analysis_id}` | Retrieve analysis details and results |
| GET | `/documents/{document_id}/analyses/{analysis_id}/geometry` | Retrieve PDF highlighting coordinates |

The `geometry` endpoint requires the `page_number` query parameter.

### Extraction Schemas

Schema-related operations include:

- `GET /schemas/available`
- Custom schema creation.
- Listing and retrieval of user-owned schemas.
- Schema updates with versioning.
- Schema duplication.
- Schema archiving.

Custom schema operations are restricted according to the authenticated user's application plan.

### Health Checks

| Endpoint | Description |
|---|---|
| `GET /health` | Check service availability |
| `GET /health/database` | Check PostgreSQL connectivity |

All endpoints listed above are relative to `/api/v1`.

### OpenAPI Documentation

When running the backend locally:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

The generated OpenAPI schema provides the authoritative reference for API contracts.

---

## 6. PostgreSQL and Data Persistence

Application persistence is implemented using PostgreSQL and SQLAlchemy ORM.

The database manages users, documents, extraction schemas, schema versions, AI configurations, and analysis results as separate relational entities.

### Main Tables

```text
plans
users

extraction_schemas
extraction_schema_versions
entity_definitions
field_definitions

documents
document_pages

ai_runtime_configs
analyses
entity_occurrences
extracted_fields
field_candidates
```

### SQL Initialization Scripts

Database initialization scripts are located in `backend/sql/`.

**`01_schema.sql`**

Defines the initial database structure, including tables, relationships, constraints, and indexes.

**`02_seed.sql`**

Populates the database with the initial application data:

- Base and Premium plans.
- Default AI runtime configuration.
- Built-in `general_document` extraction schema.
- Active extraction schema version.
- Default NER and IE definitions.

In the Docker Portfolio environment, these scripts run when an empty database is initialized.

**Important:** modifying the seed scripts does not automatically update an existing initialized database. Existing environments require controlled update or migration procedures.

---

## 7. Default Extraction Schema

The built-in extraction schema is identified by:

```text
general_document
```

Its purpose is to provide a general-purpose configuration independent of a specific application domain.

### Named Entity Recognition

| Label | Description |
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

### Information Extraction

The default schema contains one structured extraction field:

| Property | Value |
|---|---|
| Label | Main Subject |
| `field_key` | `oggetto_principale` |
| Description | Main topic or subject of the document |
| Data type | `string` |

Definitions are retrieved from the database rather than being hardcoded into the inference pipeline.

---

## 8. GLiNER2.5 and AI Integration

The default model is:

```text
fastino/gliner2.5-multi-v1
```

The GLiNER2 family supports information extraction tasks driven by semantic definitions of the requested entities and fields.

### Why GLiNER2?

**Schema-Driven Extraction**

NER categories and IE fields can be defined through an extraction schema without rewriting the processing pipeline for each new configuration.

**Cross-Domain Flexibility**

The model enables experimentation across different document types and application domains without necessarily training a dedicated classifier for each entity label.

**Multilingual Support**

The selected checkpoint supports multiple languages, although uniform extraction accuracy across languages and domains is not guaranteed.

**NER and IE Within the Same Ecosystem**

The library enables named entity recognition and structured information extraction to be integrated into the same application architecture.

**Self-Hosted Inference**

Documents are processed directly within the backend infrastructure rather than being submitted to external AI inference providers.

### Project Decisions

- Use of a pretrained model.
- No task-specific fine-tuning.
- No systematic quantitative model evaluation.
- No comparative benchmarks against alternative models.
- Greater emphasis on software integration than model optimization.

NLP results should not be assumed to be complete or accurate in every case.

The initial model download may require a connection to Hugging Face. Document contents do not need to be transmitted to that service for local inference.

---

## 9. AI Runtime Configuration

The backend separates model configuration from pipeline implementation.

The `ai_runtime_configs` table stores settings such as:

- Inference engine.
- Model identifier and revision.
- Chunk size.
- Chunk overlap.
- Batch size.
- Number of workers.
- Overlap handling policy.
- NER and IE confidence thresholds.
- Configuration activation status.

### Initial Configuration

```text
engine           = GLINER2
model_id         = fastino/gliner2.5-multi-v1
chunk_size       = 512
chunk_overlap    = 96
batch_size       = 8
num_workers      = 0
overlap_policy   = allow
entity_threshold = 0.50
field_threshold  = 0.50
```

These values represent an initial demonstration configuration rather than a benchmark-optimized setup.

Before execution, the pipeline resolves the active AI configuration and extraction schema version.

Each analysis preserves references to, and information about, the configuration used. This improves execution traceability but does not guarantee identical results across different hardware and software environments.

---

## 10. Document Processing Pipeline

The pipeline coordinates all stages between the original document and persistent AI results.

```text
PDF Upload
    |
    v
Document Validation
    |
    v
Storage Retrieval
    |
    v
PyMuPDF Text Extraction
    |
    v
Page Mapping & Provenance
    |
    v
AI Configuration Resolution
    |
    v
GLiNER2.5 Model Provider
    |
    +--------------------+
    |                    |
    v                    v
NER Extraction       Field Extraction
    |                    |
    v                    v
Deduplication        Candidate Resolution
    |                    |
    v                    v
Overlap Resolution   Field Mapping
    |                    |
    +---------+----------+
              |
              v
      PostgreSQL Persistence
              |
              v
        Analysis API
```

### Document Preparation

PyMuPDF extracts document text while preserving page-level information.

The following values are stored for each page:

```text
page_number
extracted_text
global_start
global_end
```

### Long-Document Processing

Document text is divided into configurable chunks to support documents that exceed a single model processing window.

Extracted occurrences are subsequently mapped back to global document offsets.

### Model Management

A dedicated model provider manages model loading and reuse within the backend process, avoiding repeated loading for each request when the active configuration remains unchanged.

### Named Entity Recognition

The system:

1. Extracts entities according to the selected schema.
2. Maps occurrences to their document positions.
3. Handles duplicates caused by overlapping chunks.
4. Applies a deterministic policy to resolve overlapping entities for viewer visibility.

### Information Extraction

Structured fields are defined by the selected schema version.

The pipeline identifies candidate values, maps them to the document, and resolves a result for each requested field.

Supported field statuses are:

```text
EXTRACTED
AMBIGUOUS
NOT_FOUND
ERROR
```

A `NOT_FOUND` status indicates that no sufficiently reliable value was identified. It does not necessarily prove that the information is absent from the document.

---

## 11. Analysis Lifecycle

An `Analysis` represents a single execution of the AI pipeline.

Each analysis is associated with:

- A document.
- The document owner.
- An extraction schema version.
- An AI runtime configuration.
- An execution status.
- Timestamps.
- Recognized entities.
- Extracted fields and candidate values.

### Execution States

```text
QUEUED
   |
   v
PROCESSING
   |
   +----> READY
   |
   +----> ERROR
```

A successfully completed analysis reaches the `READY` state.

Finalized results become available through the API once the analysis is ready.

### Synchronous Execution

In the current implementation, the HTTP request that starts an analysis remains open while the processing pipeline executes.

The `PROCESSING` status is persisted before inference begins.

This design simplifies the educational architecture but introduces limitations involving HTTP timeouts, concurrency, and process interruptions.

A dedicated job queue and worker architecture would be a possible future improvement.

---

## 12. Provenance, Results, and PDF Geometry

An important backend feature is the preservation of metadata required to trace extracted information back to its source document.

For named entities, the system maintains, when available:

- Entity label.
- Extracted text.
- Confidence score.
- Source page.
- Global text offsets.
- Page-relative text offsets.
- Viewer visibility status.

For IE fields, the system also stores extraction status, selected value, location, and alternative candidates.

### PDF Highlighting

The frontend uses PDF.js to display original documents.

The backend exposes a dedicated endpoint for calculating highlighting coordinates for extracted entities and fields.

Coordinates are generated only when the persisted text can be reliably aligned with the original PDF content.

This prevents potentially incorrect document regions from being highlighted.

Provenance improves result verification but does not guarantee semantic correctness.

---

## 13. Document Storage

The backend separates relational metadata from binary document content.

PostgreSQL stores the document's `storage_key`, while the original file is maintained in a separate storage system.

Two application storage modes are supported:

- `local`: local filesystem storage.
- `s3`: S3-compatible object storage.

The Docker Portfolio environment uses SILO with a private bucket.

### PDF Access

The following endpoint:

```text
GET /api/v1/documents/{document_id}/file
```

enforces document access permissions and serves PDF content through the backend.

It supports HTTP Range requests and `206 Partial Content` responses, which are useful for the PDF.js viewer.

The S3 bucket does not need to be publicly accessible for documents to be displayed.

---

## 14. Authentication, Authorization, and Plans

### Authentication

The backend implements:

- Password hashing.
- JWT access tokens.
- Token validation.
- Authenticated user identification.
- Account status checks.

Protected routes require valid authentication credentials.

### Authorization

Authorization checks cover:

- Document ownership.
- Analysis access.
- Custom schema ownership.
- Administrative permissions.
- Plan-based feature availability.

These rules are enforced by the backend even when the frontend hides restricted features.

### Application Plans

| Feature | BASE | PREMIUM |
|---|---|---|
| Built-in schema | Yes | Yes |
| NER and IE | Yes | Yes |
| Daily analysis quota | 5 in the initial seed | No application-level limit in the initial seed |
| Custom schemas | No | Yes |
| Custom schema versioning | No | Yes |

The Base/Premium distinction is implemented for demonstration purposes and does not represent a commercial payment or subscription system.

### Analysis Quotas

`AnalysisQuotaService` manages daily analysis availability.

The quota logic accounts for reserved and in-progress analyses to reduce the risk of exceeding limits through concurrent requests.

Quota consumption is finalized upon successful completion; internal processing failures should not permanently consume an analysis.

Daily quota windows are based on UTC.

---

## 15. Environment Configuration

The backend uses `pydantic-settings`.

Application configuration is defined in:

```text
app/core/config.py
```

Local values can be provided through environment variables and the `.env` file.

### Main Environment Variables

| Variable | Purpose |
|---|---|
| `APP_ENV` | Application environment |
| `APP_LOG_LEVEL` | Logging level |
| `DB_HOST` | PostgreSQL host |
| `DB_PORT` | PostgreSQL port |
| `DB_NAME` | Database name |
| `DB_USER` | Application database user |
| `DB_PASSWORD` | Database password |
| `JWT_SECRET_KEY` | JWT signing secret |
| `DOCUMENT_STORAGE_BACKEND` | `local` or `s3` |
| `DOCUMENT_STORAGE_ROOT` | Local storage directory |
| `DOCUMENT_S3_ENDPOINT_URL` | S3 endpoint |
| `DOCUMENT_S3_BUCKET` | Document bucket |
| `DOCUMENT_S3_ACCESS_KEY` | S3 access key |
| `DOCUMENT_S3_SECRET_KEY` | S3 secret key |
| `AI_MODEL_DEVICE` | Inference device |
| `AI_MODEL_QUANTIZE` | Quantization setting |
| `AI_MODEL_COMPILE` | Model compilation setting |

Use `.env.example` as the reference for local development configuration.

The JWT secret must satisfy application validation requirements, including a minimum length of 64 characters.

**Do not commit `.env` files containing real credentials.**

---

## 16. Local Development

### Prerequisites

- Python and pip.
- A configured and reachable PostgreSQL instance.
- Correctly configured environment variables.
- Network access to download model weights if they are not cached.

From the `backend/` directory:

### 16.1. Create a Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 16.2. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### 16.3. Configure the Environment

```powershell
Copy-Item .env.example .env
```

Update the required variables in `.env`.

The target database must be initialized before starting the backend.

### 16.4. Start FastAPI

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

API base URL:

```text
http://127.0.0.1:8000/api/v1
```

Health check:

```text
http://127.0.0.1:8000/api/v1/health
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

## 17. Docker Portfolio Environment

The backend is included in the Docker Portfolio stack defined at the repository root.

The stack includes:

- PostgreSQL with persistent storage.
- Private S3-compatible object storage.
- Storage initialization service.
- FastAPI backend.
- React frontend served through Nginx.
- Persistent AI model cache.

### Start the Complete Stack

From the DocuEntitySeek repository root:

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml up -d --build
```

### Check Service Status

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml ps -a
```

### Backend Logs

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml logs -f backend
```

### Health Check Through Nginx

```text
http://localhost:8080/api/v1/health
```

### Stop the Stack

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml down
```

This command preserves persistent volumes.

Avoid using `down -v` unless you intentionally want to delete the Docker Compose project's persistent data.

For complete environment setup instructions, refer to the [main README](../README.md).

---

## 18. Testing

The backend uses pytest.

From the `backend/` directory:

```powershell
python -m pytest
```

### Python Syntax Validation

```powershell
python -m compileall -q app
```

### Test Database

The test database must be isolated from both the development database and the Docker Portfolio database.

Test environment configuration, credentials, and database privileges must be consistent with the test fixtures and initialization scripts.

Tests that modify database structures or data must not accidentally run against an environment containing information that should be preserved.

### Integration Validation

The main workflow has been manually verified in the Docker Portfolio environment:

```text
User Registration
      |
      v
JWT Authentication
      |
      v
PDF Upload
      |
      v
PostgreSQL + S3 Storage
      |
      v
Document Preparation
      |
      v
GLiNER2.5 NER / IE
      |
      v
Analysis Persistence
      |
      v
Result Retrieval / PDF Viewer
```

These manual integration checks do not replace a comprehensive automated end-to-end test suite.

---

## 19. Error Handling and Logging

The backend provides centralized application error handling.

API responses use appropriate HTTP status codes and, where applicable, structured application error codes.

Examples include:

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

Internal implementation details and stack traces should not be returned directly to API clients.

### Logging

The AI pipeline generates phase-oriented logs that help:

- Identify documents and analyses.
- Verify AI runtime configuration.
- Monitor document preparation and extraction.
- Diagnose model loading errors.
- Track persistence and completion.

Using application identifiers and processing phases supports debugging without requiring complete document contents to be written to logs.

---

## 20. Security

The implemented application-level measures include:

- JWT authentication.
- Password hashing.
- Resource ownership enforcement.
- Role-based and plan-based authorization.
- PDF upload validation.
- Authenticated access to original documents.
- Private document storage.
- CORS configuration for approved origins.
- Externalized secret configuration.
- AI inference within the application infrastructure.

Self-hosted inference reduces the need to transmit documents to external AI services, but it does not automatically guarantee security or regulatory compliance.

Public deployment would require additional measures such as HTTPS, centralized secret management, rate limiting, backups, monitoring, and infrastructure hardening.

---

## 21. Current Limitations

### Non-Optimized Model

GLiNER2.5 is used without task-specific fine-tuning or quantitative evaluation on dedicated datasets.

### Synchronous Processing

AI analyses currently run during the HTTP request that initiates processing.

No dedicated job queue is currently implemented for heavy inference workloads.

### Computational Requirements

Model loading and document analysis can be resource-intensive, especially on CPU and with long documents.

### OCR

There is currently no dedicated OCR pipeline for PDFs consisting exclusively of scanned images.

### Interruption Recovery

Unexpected process termination during an analysis may require an explicit recovery procedure for the application state.

### Deployment

The Docker Portfolio environment is intended for development and demonstration, rather than as a production-ready configuration for public exposure.

---

## 22. Potential Improvements

Possible future developments include:

- Dedicated AI job queues and workers.
- Automatic recovery of interrupted analyses.
- OCR support.
- Increased automated test coverage.
- Resource and performance monitoring.
- Advanced logging and observability.
- Structured database migrations.
- Quantitative extraction evaluation.
- Experiments with alternative NLP models and configurations.
- Infrastructure hardening and cloud deployment.

These are potential improvements rather than currently available features.

---

## 23. Architectural Principles

DocuEntitySeek intentionally separates:

```text
AI MODEL
    !=
EXTRACTION SCHEMA
    !=
DOCUMENT PIPELINE
    !=
APPLICATION SERVICES
    !=
PERSISTENCE
    !=
HTTP API
```

The AI model performs inference.

The extraction schema defines the requested entities and information.

The document pipeline coordinates processing.

Application services implement business rules.

Repositories handle data persistence.

HTTP APIs expose functionality to clients.

This separation promotes testability, maintainability, and future extensibility.

---

## Conclusion

The DocuEntitySeek backend is an exercise in **full-stack software engineering with AI integration**, where the main technical challenge lies in coordinating application components, relational data persistence, document storage, and NLP processing pipelines.

GLiNER2.5 serves as a flexible pretrained extraction engine without project-specific fine-tuning or benchmarking.

**The project's main value lies in its architectural decisions and the integration of different technologies into a modular, persistent, and functional application.**

---

## References

- [DocuEntitySeek — Main README](../README.md)
- [DocuEntitySeek — Frontend](../frontend/README.md)
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [PyMuPDF](https://pymupdf.readthedocs.io/)
- [GLiNER2 — Official Repository](https://github.com/fastino-ai/GLiNER2)
- [GLiNER2.5 Multilingual — Model Card](https://huggingface.co/fastino/gliner2.5-multi-v1)
- [Docker](https://docs.docker.com/)