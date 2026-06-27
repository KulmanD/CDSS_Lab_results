# Frontend

React + Vite web client.

The frontend should call the API and render deterministic backend outputs. It must not perform independent medical classification or call AI services.

Expected MVP screens:

- Manual entry form.
- Single upload control for CSV or text-based PDF files.
- Result cards or table.
- Safety disclaimer.
- Trend display when history is provided.

The manual entry marker list includes anemia, glucose, kidney, lipid, and CRP markers. The frontend only submits records to the API and renders returned recommendation, evidence, limitations, and urgency levels; it does not classify lab values locally.

Uploaded CSV/PDF patient metadata is reflected in the patient record section when provided. Missing metadata remains blank or displays safe fallback text such as "Unknown" or "Not provided".

Install and run from this directory:

```bash
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://localhost:8000`. Start the backend separately from `backend/`:

```bash
uvicorn app.main:app --reload
```

For a different API origin, set `VITE_API_BASE_URL`.
