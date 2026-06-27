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

Optional query parameter:

- `use_saved_history=true`: merge temporary in-memory history for `patient.patient_id` into trend analysis. If this is true, `patient_id` is required.

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
  "disclaimer": "This educational prototype does not provide diagnosis or treatment. It uses predefined rules to highlight values that may deserve attention. Discuss abnormal or concerning results with a qualified clinician.",
  "overall_urgency": "monitor",
  "results": [
    {
      "rule_id": "anemia_hgb_mcv",
      "pattern": "anemia",
      "triggered": true,
      "urgency_level": "monitor",
      "message": "Hemoglobin is below the MVP threshold.",
      "plain_language_explanation": "Your hemoglobin value is lower than the threshold used by this educational prototype. This can happen for many reasons and should be reviewed with a clinician.",
      "evidence": [
        "hemoglobin 11.4 g/dL compared with threshold 12 g/dL",
        "MCV is missing, so red-cell size context cannot be classified.",
        "Trend analysis skipped because no previous value was provided."
      ],
      "limitations": [
        "This rule does not diagnose anemia.",
        "Iron studies, hematocrit, B12, folate, medications, bleeding history, and clinical context may be needed.",
        "Trend analysis skipped because no previous value was provided."
      ]
    }
  ]
}
```

The example above is the exact response for a single `hemoglobin` of 11.4 g/dL with `patient.sex = "female"`, age 45, no MCV, and no history. When MCV or historical values are supplied, the `message`, `evidence`, and `limitations` fields expand accordingly (MCV size context and trend findings are appended).

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

Custom validation errors for unsupported tests, malformed CSV rows, and missing CSV columns use HTTP 422 with this shape:

```json
{
  "detail": {
    "errors": [
      {
        "row": 2,
        "field": "value",
        "message": "value must be numeric."
      }
    ]
  }
}
```

FastAPI/Pydantic request-body validation errors may use FastAPI's standard 422 `detail` list.

## Temporary History Endpoints

These endpoints support optional demo history only. They store data in API process memory and reset when the backend restarts. They are not production persistence.

### `GET /api/history/{patient_id}`

Returns saved records for the patient.

```json
{
  "patient_id": "demo-001",
  "count": 1,
  "records": [
    {
      "test_name": "hemoglobin",
      "value": 13.8,
      "unit": "g/dL",
      "collected_at": "2026-05-01"
    }
  ]
}
```

### `POST /api/history/{patient_id}`

Replaces saved records for the patient.

Request body:

```json
{
  "records": [
    {
      "test_name": "hemoglobin",
      "value": 13.8,
      "unit": "g/dL",
      "collected_at": "2026-05-01"
    }
  ]
}
```

### `DELETE /api/history/{patient_id}`

Deletes saved records for the patient and returns the deleted count.

```json
{
  "patient_id": "demo-001",
  "deleted_count": 1
}
```

## Supported Test Names

The API accepts common aliases that normalize to these deterministic marker names:

- `hemoglobin`
- `mcv`
- `fasting_glucose`
- `hba1c`
- `creatinine`
- `egfr`
- `total_cholesterol`
- `ldl`
- `hdl`
- `triglycerides`
- `vldl`
- `crp`
