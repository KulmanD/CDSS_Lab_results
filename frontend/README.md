# Frontend

React + Vite web client.

The frontend should call the API and render deterministic backend outputs. It must not perform independent medical classification or call AI services.

Expected MVP screens:

- Manual entry form.
- CSV upload.
- Result cards or table.
- Safety disclaimer.
- Trend display when history is provided.

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
