# Data

This directory will hold synthetic inputs, expected outcomes, and evaluation datasets.

Rules:

- Do not commit real patient data.
- Mark all examples as synthetic.
- Keep expected outcomes manually authored and traceable to `docs/thresholds.md`.

Current files:

- `evaluation/mvp_cases.json`: 26 synthetic cases covering anemia, glucose, kidney, lipids, CRP, missing markers, borderline values, abnormal values, high-urgency values, and trend scenarios.
- `examples/`: upload-ready synthetic CSV files for manual frontend/API testing.

Run the evaluation from `backend/`:

```bash
python3 evaluation.py --data ../data/evaluation/mvp_cases.json
```
