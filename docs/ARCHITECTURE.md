# Architecture

The CDSS will use a simple three-layer architecture: deterministic backend rule engine, FastAPI middleware, and React/Vite frontend.

## Backend

The backend owns all clinical rule decisions. It should contain:

- Data schemas for patient demographics, lab records, historical records, and rule results.
- Central threshold definitions.
- One rule module per MVP pattern.
- A dispatcher that runs all MVP rules and returns structured results.
- CSV parsing and validation.
- Evaluation script and pytest tests.

The backend must be usable without a web server so unit tests and evaluation scripts can call the rule engine directly.

## API

FastAPI exposes the rule engine over HTTP. Planned endpoints:

- `GET /api/health`
- `POST /api/analyze`
- `POST /api/analyze/csv`

The API must not implement separate medical logic. It validates inputs, calls the deterministic backend, and returns the rule outputs with disclaimers.

## Frontend

The frontend is a React + Vite web client. It should provide:

- Manual lab entry form.
- CSV upload.
- Result cards or tables with severity coloring.
- Plain-language explanations from deterministic rule outputs.
- Visible safety disclaimer.
- Trend visualization when historical values are provided.

## Data Flow

1. User enters lab data or uploads CSV.
2. API validates the payload.
3. Rule dispatcher runs MVP rules.
4. API returns structured rule results, evidence, limitations, and disclaimer.
5. Frontend renders results without changing clinical interpretation.

