# Backend

Python backend for deterministic CDSS logic.

Current scope:

- Dependency-free rule-engine core in `cdss_core/`.
- Dataclass schemas for patient demographics, lab records, rule results, and analysis responses.
- Rules for anemia-like, glucose-risk, kidney-function, lipid-risk, and CRP/inflammation patterns.
- Trend support for hemoglobin, eGFR, and creatinine when historical records exist.
- Optional temporary in-memory history endpoints for demo trend workflows.
- FastAPI endpoints in `app/` and API validation helpers in `api/`.
- Standard-library unit tests in `tests/`.
- CSV upload parsing and narrow text-PDF upload parsing.

Install API dependencies from this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the API locally:

```bash
uvicorn app.main:app --reload
```

Run tests from this directory:

```bash
python3 -m pytest tests
```

The backend core and API do not call AI services and do not require API keys.
