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

## Trend Checks

Trend checks are MVP support logic for anemia and kidney rules. If history exists, compare the latest current value to the most recent previous value for the same test. If no history exists, return a limitation stating that trend analysis was skipped.

Initial MVP percentage-change thresholds:

- Hemoglobin: 10% or greater absolute change.
- eGFR: 20% or greater absolute change.
- Creatinine: 20% or greater absolute change.

These are prototype thresholds for demonstrating trend handling. They should be reviewed before clinical use and can later be replaced with marker-specific RCV values.
