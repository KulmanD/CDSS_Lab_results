# API Contract

The API will expose deterministic rule analysis through FastAPI. It must not contain independent medical logic beyond validation and routing to the backend rule engine.

## `GET /api/health`

Returns service health.

Example response:

```json
{
  "status": "ok",
  "service": "cdss-lab-results"
}
```

## `POST /api/analyze`

Analyzes one patient payload.

Request body:

```json
{
  "patient": {
    "patient_id": "demo-001",
    "age": 45,
    "sex": "female",
    "pregnant": false
  },
  "current_results": [
    {
      "test_name": "hemoglobin",
      "value": 11.4,
      "unit": "g/dL",
      "collected_at": "2026-06-26"
    }
  ],
  "historical_results": []
}
```

Response body:

```json
{
  "disclaimer": "This educational prototype does not provide diagnosis or treatment. Discuss abnormal or concerning results with a clinician.",
  "overall_urgency": "monitor",
  "results": [
    {
      "rule_id": "anemia_hgb_mcv",
      "pattern": "anemia",
      "triggered": true,
      "urgency_level": "monitor",
      "message": "Hemoglobin is below the MVP threshold for this demographic group.",
      "plain_language_explanation": "Your hemoglobin value is lower than the rule threshold used by this prototype. This can happen for many reasons and should be reviewed with a clinician.",
      "evidence": [
        "hemoglobin 11.4 g/dL compared with threshold 12 g/dL"
      ],
      "limitations": [
        "This rule does not diagnose anemia.",
        "MCV or other RBC indices may be needed for context."
      ]
    }
  ]
}
```

## `POST /api/analyze/csv`

Accepts a CSV upload and returns the same response shape as `/api/analyze`.

Minimum CSV columns:

- `patient_id`
- `age`
- `sex`
- `test_name`
- `value`
- `unit`
- `collected_at`

Optional columns:

- `pregnant`
- `reference_min`
- `reference_max`
- `source_label`

