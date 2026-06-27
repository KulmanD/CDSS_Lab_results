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
      ],
      "charts": [
        {
          "test_name": "hemoglobin",
          "display_name": "Hemoglobin",
          "value": 11.4,
          "unit": "g/dL",
          "axis_min": 6.34,
          "axis_max": 18.66,
          "reference_low": 12.0,
          "reference_high": null,
          "reference_label": "≥ 12 g/dL",
          "band_label": "Low",
          "range_position": "below",
          "severity": "high",
          "bands": [
            {"label": "Low", "lower": null, "upper": 12.0, "severity": "high"},
            {"label": "Normal", "lower": 12.0, "upper": null, "severity": "normal"}
          ],
          "trend": []
        }
      ]
    }
  ]
}
```

The example above is the exact response for a single `hemoglobin` of 11.4 g/dL with `patient.sex = "female"`, age 45, no MCV, and no history. When MCV or historical values are supplied, the `message`, `evidence`, `limitations`, and chart `trend` fields expand accordingly (MCV size context and trend findings are appended).

### Chart data (`results[].charts`)

Each rule result carries a `charts` array — one entry per marker the rule evaluated that was present in the request. It exists so the frontend can render a value-vs-reference-range visual without embedding or classifying thresholds itself; every number is derived deterministically from `docs/thresholds.md` / the backend threshold constants.

Per chart:

- `value`, `unit` — the patient's measured value.
- `axis_min`, `axis_max` — suggested numeric axis bounds for drawing (widened to include the value when it falls outside the typical display range).
- `reference_low`, `reference_high` — the normal/desirable band edges; either may be `null` for a one-sided marker (e.g. "normal when at or above X").
- `reference_label` — a human-readable reference range (e.g. `"≥ 12 g/dL"`, `"80–100 fL"`, `"< 0.9 mg/dL"`).
- `band_label`, `range_position` (`below` | `within` | `above`), `severity` (`normal` | `borderline` | `high` | `critical`) — where the value sits, for labelling and colour.
- `bands` — the full ordered list of reference bands (`label`, `lower`, `upper`, `severity`); open-ended edges are `null`.
- `trend` — dated `{collected_at, value}` points (oldest → newest) for a trend mini-line, including the current value. Empty unless at least two dated results exist for the marker.

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

## `POST /api/analyze/pdf`

Accepts a text-based PDF upload and returns the same response shape as `/api/analyze`.

This endpoint is intentionally narrow and deterministic:

- It extracts readable text from the PDF.
- The extracted text must contain CSV-compatible rows using the same required columns as `/api/analyze/csv`.
- It does not perform OCR.
- It does not infer lab values from arbitrary hospital/lab report layouts.
- Scanned/image PDFs are rejected with HTTP 422.

Use this for simple generated PDFs where the lab rows are embedded as text, for example a PDF export of one of the sample CSV files.

## `POST /api/analyze/upload`

Accepts one upload file and detects whether it is CSV or PDF by file extension and MIME type.

Supported uploads:

- `.csv`
- `.pdf`

The endpoint routes to the CSV or PDF parser, runs deterministic analysis, and includes parsed upload metadata for the frontend:

```json
{
  "disclaimer": "This educational prototype does not provide diagnosis or treatment...",
  "overall_urgency": "monitor",
  "results": [],
  "upload": {
    "file_type": "csv",
    "patient": {
      "patient_id": "demo-001",
      "patient_name": "Alex Demo",
      "date_of_birth": "1971-03-12",
      "age": 55,
      "sex": "female",
      "pregnant": false,
      "latest_collected_at": "2026-06-26",
      "record_count": 3
    },
    "current_results": [],
    "historical_results": []
  }
}
```

For uploaded CSV/PDF data, the parser keeps the latest dated row per marker in `current_results` and places older rows for the same marker in `historical_results`. This enables deterministic trend checks from a single uploaded file without login or persistent storage.

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
