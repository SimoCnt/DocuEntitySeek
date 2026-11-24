# DocuEntitySeek — Frontend

**React 19 · TypeScript · Vite · PDF.js · REST API Integration**

Web frontend for **DocuEntitySeek**, a full-stack Document Intelligence platform that enables users to upload PDF documents, run Named Entity Recognition (NER) and Structured Information Extraction (IE) analyses, and explore results through an interactive interface.

The application is built with React and TypeScript, communicates with the FastAPI backend through authenticated REST APIs, and uses PDF.js to display original documents and extracted information.

> **Educational Purpose**
>
> DocuEntitySeek is an educational and professional portfolio project primarily focused on exploring the design and development of full-stack applications with AI integration.
>
> The project does not aim to optimize GLiNER2.5 model performance. The backend uses a pretrained model without task-specific fine-tuning.
>
> The frontend focuses on user interface design, React component architecture, state management, API integration, authentication, document visualization, and communication across application layers.

For a complete project overview, see the [main README](../README.md). For API and NLP pipeline details, see the [backend README](../backend/README.md).

---

## 1. Objectives and Responsibilities

The frontend provides the interaction layer between users and the DocuEntitySeek application services.

Its main responsibilities include:

- Providing a web interface for document management.
- Managing user registration, login, logout, and authenticated sessions.
- Communicating with the backend through REST APIs.
- Displaying user information and plan-dependent features.
- Supporting PDF uploads and preliminary file validation.
- Starting NER/IE analyses and displaying their execution status.
- Managing extraction schema selection.
- Rendering original PDF documents using PDF.js.
- Displaying recognized entities and structured extraction results.
- Connecting extracted information to its source location within a document.
- Managing custom extraction schemas and schema versioning.
- Providing consistent feedback during loading, processing, and error states.

The frontend does not perform AI inference directly and does not independently access PostgreSQL or private S3 storage.

These operations are handled by the backend.

---

## 2. Technology Stack

| Area | Technology |
|---|---|
| UI Library | React 19 |
| Language | TypeScript |
| Development and Build | Vite |
| Routing | React Router |
| HTTP Communication | Fetch API |
| PDF Visualization | PDF.js (`pdfjs-dist`) |
| State Management | React Hooks, Context API |
| Styling | CSS |
| Static Analysis | TypeScript, Oxlint |
| Testing | Vitest, React Testing Library |
| Portfolio Deployment | Docker, Nginx |

The application follows a Single Page Application (SPA) architecture.

The FastAPI backend acts as the source of application data and AI analysis results.

---

## 3. Frontend Architecture

The source code separates pages, components, hooks, API clients, and TypeScript types.

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

Pages represent the application's main screens.

They coordinate components, hooks, and user interactions.

### Components

Components implement reusable interface elements, including forms, dialogs, navigation, feedback, analysis results, and PDF visualization.

### Hooks

Custom hooks encapsulate reusable logic for data fetching, asynchronous operations, polling, and state management.

### API Layer

API modules organize HTTP requests by application domain.

### Types

TypeScript interfaces and types describe the data structures exchanged and used throughout the frontend.

This organization reduces coupling between presentation logic, data access, and backend application behavior.

---

## 4. Project Structure

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

This structure illustrates the main modules. Additional specialized files and components may be present.

### Application Entry Points

`src/main.tsx` initializes React, the router, and the authentication provider.

`src/App.tsx` defines the application's main routes and navigation structure.

---

## 5. Routing and Navigation

Client-side routing is implemented using React Router.

The main routes include:

| Path | Description |
|---|---|
| `/` | Homepage |
| `/login` | Login |
| `/register` | User registration |
| `/documents` | Document list |
| `/documents/new` | PDF upload |
| `/documents/:documentId` | Document details and analyses |
| `/schemas` | Extraction schema management |
| `/premium` | Premium information page |

### Protected Routes

The `ProtectedRoute` and `GuestRoute` components manage navigation for authenticated and unauthenticated users.

### Shared Layout

`AppLayout` provides shared interface elements, including the header, navigation, and page content structure.

Frontend route restrictions improve user experience but do not replace backend authorization.

---

## 6. HTTP Client and REST Integration

The shared HTTP client is implemented in:

```text
src/api/http.ts
```

Its responsibilities include:

- API base URL management.
- HTTP requests through the Fetch API.
- Bearer token injection when required.
- HTTP methods and JSON payload handling.
- Response parsing.
- Error normalization.
- HTTP status handling.
- `AbortSignal` support.

### Separation Between UI and API Communication

A typical application request follows this flow:

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

Components generally interact with custom hooks and domain-specific API functions rather than implementing HTTP request logic directly.

Specialized components, such as the PDF viewer, perform dedicated requests to retrieve documents and highlighting geometry.

### Error Handling

HTTP errors are normalized into a consistent structure that can be consumed by UI components.

This allows the application to display appropriate feedback for:

- Authentication failures.
- Missing resources.
- Validation errors.
- Analysis quota limits.
- Insufficient permissions.
- AI processing failures.
- Network errors.

TypeScript typing does not replace server-side validation or security checks.

---

## 7. Authentication and Session Management

Frontend authentication is managed through `AuthContext`.

The context maintains:

- Authenticated user information.
- JWT access token.
- Login and logout operations.
- Authentication status.
- User profile retrieval.
- Application plan information.
- Daily analysis quota.

### Token Storage

The access token is stored in browser `sessionStorage` through functions defined in:

```text
src/auth/authStorage.ts
```

The storage key is:

```text
docuentityseek.access-token
```

Protected requests include the token using:

```text
Authorization: Bearer <access_token>
```

Frontend token storage does not guarantee complete token security. The browser is an untrusted environment, and JavaScript-accessible tokens require careful protection against client-side vulnerabilities, including XSS.

### Login

The application authenticates through FastAPI using the OAuth2 Password Request Form format.

### Resource Access

Users can interact with the features exposed by their authenticated session and application plan.

Actual resource authorization is always enforced by the backend.

---

## 8. PDF Document Management

The document section allows users to:

- List uploaded documents.
- View available metadata.
- Display document page counts.
- Upload new PDFs.
- Open document details.
- Review previous analyses.
- Start new analyses.
- Display original PDF files.

### Upload Workflow

`NewDocumentPage` coordinates the document upload process.

```text
PDF Selection
      |
      v
Preliminary Validation
      |
      v
Schema Selection (if available)
      |
      v
Upload Confirmation
      |
      v
POST /documents
      |
      v
Start Analysis
      |
      v
Navigate to /documents
```

Client-side validation provides immediate feedback.

The backend performs authoritative file validation before accepting uploaded documents.

### Extraction Schema Selection

Base users rely on the default built-in extraction schema.

Users with custom schema permissions can select from the available extraction schemas before starting an analysis.

### Automatic Analysis

The upload workflow starts the initial analysis after successfully creating the document.

This behavior does not imply a separate AI worker: the backend currently executes the processing pipeline synchronously within the analysis request.

---

## 9. NER and Information Extraction Analyses

The frontend provides access to AI processing features without executing GLiNER2.5 locally in the browser.

Users can:

- Start a document analysis.
- Select an extraction schema when authorized.
- Review previous analysis executions.
- Monitor processing status.
- Access completed results.
- Explore recognized named entities.
- Inspect structured extraction fields.

### Starting an Analysis

The frontend uses:

```text
POST /api/v1/documents/{document_id}/analyses
```

A `schemaVersionId` may be provided when allowed by the user's plan and the available extraction schemas.

### Analysis History

A document may have multiple associated analyses.

The interface supports retrieving and selecting a specific analysis, including its schema name and version.

### Analysis Statuses

The backend exposes the following analysis states:

```text
QUEUED
PROCESSING
READY
ERROR
```

Finalized results are displayed when an analysis reaches `READY`.

---

## 10. Polling and Asynchronous UI State

The frontend uses periodic updates to keep the interface synchronized with backend state.

### Document List

The `useDocuments` hook retrieves documents and conditionally refreshes the list when processing documents are present.

Temporary refresh attempts are also supported for recently uploaded documents.

Polling stops when it is no longer required.

### Document Details

`DocumentDetailPage` periodically refreshes:

- The document's analysis history.
- The selected analysis, while processing is still in progress.

Background refreshes are limited when the browser page is not visible.

### Request Cancellation

Where appropriate, HTTP requests use `AbortController` and `AbortSignal`.

This helps prevent intentionally canceled requests from being displayed as application errors, particularly when navigating between pages or unmounting components.

**Important:** frontend polling does not make backend execution asynchronous. It only keeps the UI synchronized with persisted application states.

---

## 11. PDF.js Document Viewer

The frontend integrates PDF.js to display original PDF documents.

The main component is:

```text
src/components/pdf/PdfDocumentViewer.tsx
```

### Features

The PDF viewer supports:

- Authenticated PDF retrieval.
- Canvas-based page rendering.
- Page navigation.
- Responsive sizing.
- Zoom controls.
- Integration with AI analysis results.
- Highlighting of recognized entities and extracted fields when available.
- Navigation to selected document regions.

### Original PDF Access

Documents are retrieved through the backend endpoint:

```text
GET /api/v1/documents/{document_id}/file
```

Requests include the user's JWT access token.

The FastAPI endpoint supports HTTP `200 OK` and `206 Partial Content` responses.

The frontend does not require public access to the S3 bucket.

### PDF.js Worker

PDF.js uses a Web Worker to process document content.

The worker is included in the Vite build and distributed as a JavaScript asset, typically with the `.mjs` extension.

In the Docker Portfolio environment, Nginx must serve `.mjs` files with an appropriate JavaScript MIME type, such as:

```text
application/javascript
```

Incorrect MIME configuration can prevent PDF.js initialization even when the document is correctly stored and accessible through the backend.

---

## 12. NER/IE Result Visualization

The main analysis result component is:

```text
src/components/analysis/AnalysisResultViewer.tsx
```

It consumes persisted analysis data, including:

```text
result.schema
result.pages
result.entities
result.fields
```

### Named Entity Recognition

Recognized entities are presented according to the definitions of the selected extraction schema.

The UI supports:

- Schema-defined entity colors.
- Entity category filters.
- Enabling and disabling specific labels.
- Entity selection.
- Linking entities to document locations.
- Navigating recognized occurrences.

### Information Extraction

Structured extraction fields are displayed using:

- Field name.
- Technical field key.
- Semantic description.
- Extracted value, when available.
- Source page reference, when available.

The backend may preserve additional information, including extraction statuses and alternative candidates. Not every field available in the API contract is necessarily exposed as an interactive frontend control.

### Provenance

Extraction results can be associated with PDF locations using geometry information calculated by the backend.

The relevant endpoint is:

```text
GET /api/v1/documents/{document_id}/analyses/{analysis_id}/geometry?page_number=1
```

Highlighting is performed only when the backend can reliably align persisted text with the original PDF content.

This prevents potentially incorrect visual associations.

Provenance improves result verification but does not guarantee the semantic accuracy of model predictions.

---

## 13. Custom Extraction Schemas

The `/schemas` section allows authorized users to manage their extraction configurations.

Supported operations include:

- Listing available schemas.
- Creating new extraction schemas.
- Defining NER entity categories.
- Defining IE fields.
- Updating schemas through versioning.
- Duplicating schemas.
- Archiving schemas.
- Reviewing archived schemas.

### NER Definitions

Entity labels specify the categories the model should identify.

Examples:

```text
PERSONA
ORGANIZZAZIONE
LOCALITA
IDENTIFICATIVO
```

### IE Fields

Structured fields use stable technical identifiers.

Examples:

```text
oggetto_principale
data_documento
nome_cliente
```

Semantic descriptions explain the meaning of the requested information.

### Validation

Frontend forms validate data before submitting requests.

Depending on the operation, validation includes:

- Schema name and domain.
- Presence of at least one definition.
- Definition count limits.
- NER label formatting.
- IE field key formatting.
- Duplicate definitions.
- Reserved identifiers.
- Backend validation errors.

The backend remains responsible for authoritative validation.

### Versioning

Schema modifications create new versions.

```text
Custom Extraction Schema
        |
        +-- v1 INACTIVE
        |
        +-- v2 ACTIVE
```

Historical analyses retain references to their original schema versions.

### Archiving

Archived schemas are no longer offered for new analyses, while historical information remains available according to application rules.

---

## 14. Base and Premium Plans

The frontend adapts selected screens and features to the authenticated user's application plan.

| Feature | Base | Premium |
|---|---|---|
| PDF upload | Yes | Yes |
| NER/IE analyses | Yes | Yes |
| Built-in schema | Yes | Yes |
| Custom schemas | No | Yes |
| Custom schema versioning | No | Yes |
| Daily quota | 5 in the initial seed | No application-level limit in the initial seed |

### Base Plan

Base users analyze documents using the built-in extraction schema.

Custom schema management tools are not available to this plan.

### Premium Plan

Premium users can use the built-in schema and their own active custom extraction schemas.

### Premium Information Page

The application includes a Premium information page with a configurable contact email.

The plan system was implemented for educational and demonstration purposes.

It does not include a complete commercial payment or subscription infrastructure.

### Authorization

Frontend visibility restrictions are not a security boundary.

The backend independently verifies the user's plan, role, resource ownership, and analysis quota.

---

## 15. User Feedback and Error Handling

The frontend explicitly manages common UI states:

```text
loading
empty
error
success
processing
ready
```

Dedicated components provide consistent feedback, including loading indicators and error states.

Application interactions may include:

- Loading indicators.
- Validation messages.
- Confirmation dialogs.
- Modal dialogs.
- Error messages.
- Retry actions.
- State updates without full-page reloads.

Backend errors are normalized into readable messages without exposing unnecessary internal implementation details or stack traces to users.

---

## 16. Environment Configuration

The frontend uses Vite environment variables.

The primary variable is:

```text
VITE_API_BASE_URL
```

This defines the FastAPI base URL.

### Local Development

Example:

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

### Docker Portfolio

In the Docker Portfolio environment, Nginx acts as a reverse proxy between the browser and FastAPI.

The API base URL can therefore use a relative path:

```dotenv
VITE_API_BASE_URL=/api/v1
```

### Premium Contact

The Portfolio build can also use:

```text
VITE_PREMIUM_CONTACT_EMAIL
```

to configure the contact email displayed on the Premium information page.

### Vite Environment Variables

Variables prefixed with `VITE_` are embedded into frontend build assets when referenced by the application.

**They must not contain passwords, private keys, authentication secrets, or other confidential credentials.**

Changes to build-time environment variables require rebuilding the frontend assets.

---

## 17. Local Development

### Prerequisites

- A compatible Node.js and npm installation.
- Installable frontend dependencies.
- An accessible FastAPI backend.
- Correctly configured environment variables.

From the `frontend/` directory:

### 17.1. Install Dependencies

```powershell
npm ci
```

### 17.2. Configure the Environment

```powershell
Copy-Item .env.example .env
```

Set `VITE_API_BASE_URL` to the correct backend development address.

### 17.3. Start Vite

```powershell
npm run dev
```

The application is normally available at:

```text
http://localhost:5173
```

The Vite development server is not the web server used for the Docker Portfolio deployment.

---

## 18. Build and Docker Deployment

### Build Static Assets

```powershell
npm run build
```

Vite generates the static assets required for deployment.

### Local Preview

```powershell
npm run preview
```

This command provides a local preview of the compiled application.

### Docker Portfolio

The frontend is compiled during the Docker image build and served through Nginx.

The deployment architecture is:

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

The Portfolio frontend is available at:

```text
http://localhost:8080
```

### Start the Complete Stack

From the repository root:

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml up -d --build
```

### Rebuild Only the Frontend

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml up -d --no-deps --build frontend
```

### Validate Nginx Configuration

```powershell
docker compose --env-file .env.portfolio -f compose.portfolio.yaml exec frontend nginx -t
```

For complete Docker setup instructions, see the [main README](../README.md).

---

## 19. Testing and Code Quality

The frontend uses TypeScript and static code analysis tools.

### Type Checking

```powershell
npx tsc -b
```

### Linting

```powershell
npm run lint
```

### Build Validation

```powershell
npm run build
```

### Testing

The project uses the Vitest / React Testing Library ecosystem for frontend testing.

Automated test coverage can be extended to include:

- Authentication and protected routes.
- API request handling.
- PDF uploads.
- Analysis quotas.
- Analysis polling.
- Extraction schema management.
- Result rendering.
- PDF.js behavior.
- Error handling.

Compilation and type checking do not replace behavioral or end-to-end testing.

---

## 20. Frontend Security

The frontend implements several access management and security-related mechanisms:

- Protected application routes.
- Bearer token authentication.
- Logout handling.
- Conditional feature visibility.
- Preliminary input validation.
- Authorization error handling.
- Authenticated PDF retrieval.

However, the frontend is not considered a trusted security boundary.

In particular:

- Base/Premium restrictions must be enforced by the backend.
- Browser-accessible tokens require protection against client-side vulnerabilities.
- S3 document buckets must remain private.
- Final document validation is performed server-side.
- API responses must not automatically be treated as trusted application input.

The project is not a certified solution for handling sensitive information.

---

## 21. Current Limitations

### Backend Dependency

The frontend requires FastAPI services for authentication, documents, extraction schemas, and analyses.

It is not designed as a fully standalone or offline application.

### Synchronous AI Processing

Starting an analysis currently involves an HTTP request that may remain open throughout the backend processing pipeline.

This may result in long waiting times and requires careful handling of timeouts and interruptions.

### Extraction Accuracy

Result quality depends on the GLiNER2.5 model and the selected extraction schema.

The frontend displays model output but does not certify its correctness.

### PDF Highlighting

Highlighting depends on the availability and alignment of geometric coordinates.

Not every extraction can necessarily be highlighted in the original PDF.

### OCR

The platform does not currently include a dedicated OCR pipeline for image-only or scanned PDF documents.

### Testing

Automated testing can be further expanded, especially for end-to-end workflows involving the frontend, backend, storage, and AI pipeline.

### Deployment

The Docker Portfolio environment is intended for local demonstration rather than production-ready public deployment.

---

## 22. Potential Improvements

Possible future developments include:

- Improved interface accessibility.
- Extended automated testing.
- Comprehensive end-to-end tests.
- More detailed visualization of alternative IE candidates.
- Improved handling of long-running analyses.
- Integration with a future asynchronous AI processing architecture.
- Additional tools for navigating and reviewing extracted information.
- Rendering optimizations for very large documents.
- Improved error handling and frontend observability.

These represent potential enhancements rather than currently implemented features.

---

## 23. Design Principles

The DocuEntitySeek frontend intentionally separates:

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

The interface presents data and enables user interaction.

Custom hooks coordinate state and data fetching.

The API layer communicates with backend services.

The backend enforces business rules, manages persistence, and performs AI inference.

This separation promotes modularity, maintainability, component reuse, and future extensibility.

---

## Conclusion

The DocuEntitySeek frontend is an exercise in **React and TypeScript development integrated with a full-stack Document Intelligence architecture**.

Its primary value lies in providing a functional interface for authentication, document management, extraction schema versioning, analysis history, and interactive visualization of information extracted from original PDF documents.

**The objective is not to demonstrate state-of-the-art AI model performance, but to design a modular, understandable, and fully integrated web application connected to backend services, relational databases, document storage, and NLP capabilities.**

---

## References

- [DocuEntitySeek — Main README](../README.md)
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