# Rule Engine Spec

The rule engine must be deterministic and transparent. It should never call an AI service or rely on generated medical reasoning.

## Rule Function Contract

Each MVP rule function accepts:

- Patient demographics.
- Current lab records.
- Optional historical lab records.

Each rule function returns one or more rule results using the contract in `docs/DATA_MODEL.md`.

## Dispatcher

The dispatcher should:

1. Normalize test names.
2. Build a lookup table of current records.
3. Run all MVP rules.
4. Run trend checks when history exists.
5. Collect results in a stable order.
6. Return a top-level response with disclaimer and overall urgency.

## MVP Rules

### Anemia-Like Pattern

Inputs:

- Hemoglobin.
- MCV when available.
- Patient sex and pregnancy status when available.

Expected behavior:

- Flag low hemoglobin using documented sex-aware thresholds.
- Classify MCV context as microcytic, normocytic, or macrocytic when available.
- Add limitation when pregnancy, acute illness, or missing MCV could affect interpretation.

### Glucose-Risk Pattern

Inputs:

- Fasting glucose.
- HbA1c.

Expected behavior:

- Classify normal, prediabetes-risk, diabetes-range, and low glucose warnings using documented thresholds.
- Detect a calm rising fasting-glucose trend when at least three dated fasting-glucose values for the same uploaded/analyzed patient are available.
- Trigger monitor-level review when fasting glucose is still below the diabetes-range threshold but rises meaningfully across recent tests.
- Avoid diagnosis language, especially for diabetes-range values.
- Prefer combined interpretation when both fasting glucose and HbA1c are present.

### Kidney-Function Alert

Inputs:

- eGFR.
- Creatinine.
- Patient sex and age.

Expected behavior:

- Stage eGFR using documented CKD stage bands.
- Flag eGFR below 60 as needing clinician review, especially if persistent in history.
- Interpret creatinine using sex-aware ranges.
- Explain that CKD requires persistence and clinical context.

### Lipid-Risk Pattern

Inputs:

- Total cholesterol.
- LDL.
- HDL.
- Triglycerides.
- VLDL when available.
- Patient sex for HDL threshold selection.

Expected behavior:

- Classify LDL as optimal, near optimal, borderline high, high, or very high.
- Flag total cholesterol 200 mg/dL or higher.
- Flag sex-aware low HDL.
- Flag triglycerides and VLDL outside documented bands.
- Explain that lipid goals and treatment decisions require overall cardiovascular-risk context.

### CRP/Inflammation Pattern

Inputs:

- CRP.

Expected behavior:

- Classify CRP as normal, near upper reference range, moderate elevation, marked elevation, or severe elevation.
- Escalate severe CRP elevation to urgent review.
- Explain that CRP is nonspecific and cannot diagnose an inflammatory condition by itself.

## Trend Checks

Trend checks are MVP support logic for the anemia, kidney, and fasting-glucose rules (`cdss_core/trends.py`). A single least-squares engine fits a straight line to all dated results for a marker (history plus the current value, de-duplicated by date) and decides whether the patient is moving in a clinically adverse direction. A trend is reported as significant only when **all** of the following hold:

1. **Direction** — the slope points in the marker's adverse direction (hemoglobin/eGFR falling, creatinine/fasting glucose rising). A favourable move never raises an alert.
2. **Data** — at least the per-marker minimum number of dated results, spanning at least the per-marker minimum number of days.
3. **Magnitude** — the modelled change across the window meets the per-marker percentage threshold (or absolute threshold where defined).
4. **Consistency** — the linear fit quality (R²) is at least 0.5, so scattered results do not confirm a trend. Fit quality is also surfaced as a confidence label (`clear` / `possible` / `noisy`).

If history is missing or insufficient, the engine returns a limitation stating that trend analysis was skipped.

Per-marker configuration (`TREND_CONFIG`):

| Marker | Adverse direction | Min points | Min span | % threshold | Absolute threshold |
| --- | --- | --- | --- | --- | --- |
| Hemoglobin | falling | 2 | 21 days | 10% | — |
| eGFR | falling | 2 | 30 days | 20% | — |
| Creatinine | rising | 2 | 30 days | 20% | — |
| Fasting glucose | rising | 3 | 21 days | 10% | 10 mg/dL |

Because the engine uses the slope of all points rather than a single most-recent comparison, a normal-but-rising value (for example fasting glucose 82 → 90 → 98 mg/dL) is flagged while it is still inside the normal band, and a single noisy dip no longer hides a real trend.

These are prototype thresholds for demonstrating trend handling. They should be reviewed before clinical use and can later be replaced with marker-specific RCV values.

## Optional Saved History

The API may store temporary in-memory history by `patient_id` for demo workflows. Saved history is not production persistence, is cleared when the API process restarts, and is used for analysis only when the caller explicitly requests it.
