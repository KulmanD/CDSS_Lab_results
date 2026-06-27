# Safety And Limitations

This project is an academic prototype. It must prioritize transparency and caution over broad medical claims.

## Required User-Facing Disclaimer

Use wording equivalent to:

> This educational prototype does not provide diagnosis or treatment. It uses predefined rules to highlight values that may deserve attention. Discuss abnormal or concerning results with a qualified clinician.

## Non-Diagnostic Language

Use:

- "may suggest"
- "is in a range that should be reviewed"
- "is consistent with"
- "needs clinician review"

Avoid:

- "you have anemia"
- "you are diabetic"
- "you have CKD"
- "treatment is required"

## Known Limitations

- Lab thresholds vary by laboratory, population, age, sex, pregnancy status, and clinical context.
- A single abnormal result can be transient or affected by illness, medications, hydration, or collection conditions.
- CKD staging requires persistence and clinical confirmation.
- Glucose and HbA1c interpretation depends on testing context and repeat confirmation.
- Anemia interpretation often needs additional markers such as ferritin, hematocrit, MCHC, B12, folate, and clinical history.
- Lipid interpretation depends on overall cardiovascular risk, fasting status, diabetes status, pregnancy, medications, and treatment goals set by a clinician.
- CRP is nonspecific and cannot diagnose infection, autoimmune disease, cardiovascular disease, or another inflammatory condition by itself.
- Saved patient history is temporary in-memory demo state, not durable storage or a clinical record.

## Data Safety

- Use synthetic or anonymized data only.
- Do not commit real names, IDs, dates of birth, medical record numbers, or raw clinical documents.
- Keep examples simple and clearly marked as synthetic.
