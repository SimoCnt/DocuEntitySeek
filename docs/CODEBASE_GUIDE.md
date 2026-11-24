# DocuEntitySeek — Codebase Guide

## Overview

DocuEntitySeek is a full-stack document intelligence application for analyzing PDF documents using Named Entity Recognition (NER) and structured Information Extraction (IE).

The application combines a React and TypeScript frontend with a FastAPI backend, PostgreSQL persistence, configurable document storage, and a GLiNER2-based extraction pipeline.

This document describes the current implementation and its architectural boundaries.

## Backend architecture

The backend follows a layered architecture:

| Directory | Responsibility |
|---|---|
| `api/routes/` | HTTP endpoints, request handling, response serialization |
| `schemas/` | Pydantic request and response contracts |
| `services/` | Application workflows, business rules and transactions |
| `repositories/` | SQLAlchemy persistence operations |
| `db/` | ORM models, database engine and sessions |
| `pipeline/` | PDF extraction, AI inference, mapping and result resolution |
| `core/` | Configuration, security, logging and exception handling |
| `dependencies.py` | FastAPI dependency injection and service composition |

API routes delegate application operations to services. Services coordinate repositories and, when needed, the document analysis pipeline.

Database transactions are generally managed at the service level.

## Document upload workflow

The document upload workflow is coordinated by `DocumentService`.

1. The API validates the uploaded file.
2. PyMuPDF reads the PDF to determine its page count.
3. A document record is created in PostgreSQL.
4. The original PDF is uploaded to the configured storage backend.
5. The storage key and page count are persisted.
6. The database transaction is committed.

If an error occurs, the service rolls back the database transaction and attempts to delete any uploaded object.

The storage abstraction supports both local filesystem storage and private S3-compatible object storage.

The current S3 implementation also supports reading legacy files from local storage when the object is unavailable remotely.

## AI analysis workflow

The analysis workflow is coordinated by `AnalysisService` and `AnalysisPipeline`.

`AnalysisService` is responsible for document ownership checks, schema authorization, runtime configuration resolution, quota enforcement and analysis lifecycle management.

The analysis lifecycle uses the following states:

- `QUEUED`
- `PROCESSING`
- `READY`
- `ERROR`

**Current execution model:** analysis execution is synchronous. The service persists a `QUEUED` record but immediately executes the pipeline within the initiating HTTP request. A distributed job queue or independent AI worker is not implemented.

### Pipeline stages

`AnalysisPipeline.execute()` coordinates the following operations:

1. Prepare the PDF and extract its text.
2. Load or retrieve the configured AI model.
3. Extract named entities.
4. Deduplicate NER candidates and resolve overlapping highlights.
5. Extract structured field candidates.
6. Resolve field results and map candidate offsets to document pages.
7. Persist entity occurrences and extracted fields.
8. Return execution statistics.

The pipeline is configured through runtime settings and versioned extraction schemas.

## PDF text provenance and visual highlights

The system preserves text offsets so that AI extraction results can be associated with pages of the original document.

`DocumentProvenanceBuilder` constructs the document text representation and its page boundaries.

`PageSpanMapper` converts global text offsets into page-local coordinates and rejects invalid mappings, including spans that cross page boundaries.

`PdfGeometryService` uses PyMuPDF to recover visual rectangles from the original PDF.

Before returning highlight coordinates, it checks that the PDF text used for geometry matches the text persisted for analysis. If the representations differ, the API returns an unaligned result rather than potentially incorrect highlights.

The frontend renders the PDF using PDF.js and positions highlights using normalized rectangle coordinates.

## Authentication and authorization

Authentication uses bearer access tokens signed with JWT.

The API verifies token claims, identifies the current user and enforces account activation.

Document access is restricted by document ownership. Administrative endpoints require an administrative user role.

The application also distinguishes Base and Premium plans. Plan capabilities affect analysis quotas and access to custom extraction schemas.

Authorization is enforced by backend services rather than relying on frontend visibility controls.

## Frontend architecture

The frontend is organized into:

| Directory | Responsibility |
|---|---|
| `pages/` | Route-level screens |
| `components/` | Reusable UI and feature components |
| `hooks/` | Data fetching and UI state management |
| `api/` | Typed requests to FastAPI |
| `auth/` | Authentication context and token storage |
| `types/` | TypeScript data contracts |
| `utils/` | Error handling and validation helpers |

`AuthContext` maintains the authenticated user, access token and analysis quota information.

The application currently stores the access token in browser session storage.

The shared HTTP client provides a consistent interface for API requests and errors.

PDF rendering and AI-result presentation are separated into dedicated components.

## Persistence and storage

PostgreSQL stores users, plans, documents, extraction schemas, schema versions, analysis records, entity occurrences, extracted fields and candidate values.

Original PDF files are stored outside PostgreSQL.

The database stores a storage key that identifies the original object.

The PDF download endpoint requires authentication and supports HTTP byte-range requests for the document viewer.

## Known architectural constraints

The current implementation has several intentional boundaries, as this is a study project and not a development platform:

- AI inference runs synchronously within the API request.
- AI accuracy can be improved with fine-tuning on a specific context, but this is not the goal of this project.
- Distributed task queues and independent AI workers are not implemented.
- Automatic OCR of image-only PDFs is not established by the inspected pipeline.


## Documentation conventions

Python code uses concise English docstrings describing responsibilities, inputs, outputs, exceptional behavior and important side effects.

TypeScript uses JSDoc for reusable components, complex hooks and non-obvious lifecycle behavior.

Comments should explain design decisions and invariants, not restate self-explanatory code.
