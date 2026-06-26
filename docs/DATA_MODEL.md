# Data Model

The implementation should use explicit schemas so rule behavior is predictable and testable.

## Patient Demographics

Required fields:

- `patient_id`: local synthetic identifier or optional client-provided ID.
- `age`: integer years.
- `sex`: `female`, `male`, or `other_unknown`.
- `pregnant`: optional boolean, default `null`.

Sex and age are needed for hemoglobin, creatinine, HDL, and future threshold adjustments.

## Lab Record

Required fields:

- `test_name`: normalized test name such as `hemoglobin`, `mcv`, `fasting_glucose`, `hba1c`, `creatinine`, `egfr`.
- `value`: numeric result.
- `unit`: result unit.
- `collected_at`: ISO date.

Optional fields:

- `source_label`: original uploaded test label.
- `reference_min`: lab-provided lower range for display only.
- `reference_max`: lab-provided upper range for display only.

Lab-provided reference ranges are useful context, but they must not replace the documented rule thresholds.

## Historical Record

A historical record uses the same lab fields plus a collection date. Historical records are optional. Rules must still run when history is unavailable and must mark trend checks as skipped.

## Rule Result

Every rule returns:

- `rule_id`: stable ID such as `anemia_hgb_mcv`.
- `pattern`: `anemia`, `glucose`, `kidney`, or future family.
- `triggered`: boolean.
- `urgency_level`: `routine`, `monitor`, `prompt_review`, or `urgent_review`.
- `message`: short clinical-style summary.
- `plain_language_explanation`: patient-friendly explanation.
- `evidence`: list of exact values, thresholds, and comparisons used.
- `limitations`: caveats and reasons to consult a clinician.

