# Architecture

The CDSS will use a simple three-layer architecture: deterministic backend rule engine, FastAPI middleware, and React/Vite frontend.

## Backend

The backend owns all clinical rule decisions. It should contain:

- Data schemas for patient demographics, lab records, historical records, and rule results.
- Central threshold definitions.
- One rule module per implemented pattern.
- A dispatcher that runs all implemented rules and returns structured results.
- CSV parsing and validation.
- Optional temporary in-memory history storage for demo trend workflows.
- Evaluation script and pytest tests.

The backend must be usable without a web server so unit tests and evaluation scripts can call the rule engine directly.

## API

FastAPI exposes the rule engine over HTTP. Implemented endpoints:

- `GET /api/health`
- `POST /api/analyze`
- `POST /api/analyze/upload`
- `POST /api/analyze/csv`
- `POST /api/analyze/pdf`
- `GET /api/history/{patient_id}`
- `POST /api/history/{patient_id}`
- `DELETE /api/history/{patient_id}`

The API must not implement separate medical logic. It validates inputs, routes uploads by detected file type, calls the deterministic backend, and returns the rule outputs with disclaimers.

The frontend should use the unified upload endpoint. PDF upload is limited to text-based PDFs whose extracted text already contains CSV-compatible lab rows. OCR and arbitrary lab-report layout recognition are intentionally out of scope.

## Frontend

The frontend is a React + Vite web client. It should provide:

- Manual lab entry form.
- Single upload control for CSV or text-based PDF files.
- Result cards or tables with severity coloring.
- Plain-language explanations from deterministic rule outputs.
- Visible safety disclaimer.
- Trend visualization when historical values are provided.

## Data Flow

1. User enters lab data or uploads a CSV/PDF file.
2. API validates the payload and routes uploaded files to the matching parser.
3. Uploaded files are split into latest current results and older historical results by marker/date.
4. Rule dispatcher runs implemented rules.
5. API returns structured rule results, evidence, limitations, disclaimer, and upload metadata when available.
6. Frontend renders a calm recommendation first and keeps detailed rule evidence collapsed until requested.
