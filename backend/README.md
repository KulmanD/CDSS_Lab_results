# Backend

Python backend for deterministic CDSS logic.

Current scope:

- Dependency-free rule-engine core in `cdss_core/`.
- Dataclass schemas for patient demographics, lab records, rule results, and analysis responses.
- MVP rules for anemia-like, glucose-risk, and kidney-function patterns.
- Trend support for hemoglobin, eGFR, and creatinine when historical records exist.
- Standard-library unit tests in `tests/`.

Run tests from this directory:

```bash
python3 -m unittest discover -s tests
```

The backend core does not call AI services and does not require API keys. FastAPI routes will be added in a later workstream.
