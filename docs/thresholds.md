# Threshold References

This file is the source of truth for MVP threshold values. Implementation code should reference centralized constants that match this document.

## Anemia-Like Pattern

Inputs:

- Hemoglobin.
- MCV.

Initial MVP thresholds:

- Hemoglobin below 12 g/dL in pre-menopausal women suggests anemia-range low hemoglobin.
- Hemoglobin below 13 g/dL in men and post-menopausal women suggests anemia-range low hemoglobin.
- MCV below 80 fL is microcytic context.
- MCV 80-100 fL is normocytic context.
- MCV above 100 fL is macrocytic context.

Primary source from guidance:

- Anemia Screening - StatPearls - NCBI Bookshelf: https://www.ncbi.nlm.nih.gov/books/NBK499905/

## Glucose-Risk Pattern

Inputs:

- Fasting plasma glucose.
- HbA1c.

Initial MVP thresholds:

- Fasting glucose below 70 mg/dL: low glucose warning.
- Fasting glucose below 100 mg/dL: normal range.
- Fasting glucose 100-125 mg/dL: prediabetes-risk range.
- Fasting glucose 126 mg/dL or higher: diabetes-range value that needs clinician review.
- HbA1c below 5.7%: normal range.
- HbA1c 5.7%-6.4%: prediabetes-risk range.
- HbA1c 6.5% or higher: diabetes-range value that needs clinician review.

Primary source from guidance:

- Diabetes - Diagnosis and treatment - Mayo Clinic: https://www.mayoclinic.org/diseases-conditions/diabetes/diagnosis-treatment/drc-20371451

## Kidney-Function Alert

Inputs:

- eGFR.
- Creatinine.

Initial MVP thresholds:

- Creatinine 0.7-1.3 mg/dL for men: common reference range.
- Creatinine 0.5-0.95 mg/dL for women: common reference range.
- eGFR 90 or higher: Stage I range when other kidney-damage evidence exists.
- eGFR 60-89: Stage II range when other kidney-damage evidence exists.
- eGFR 30-59: Stage III range.
- eGFR 15-29: Stage IV range.
- eGFR below 15: Stage V range.
- eGFR below 60 for at least three months is a CKD concern that requires clinical confirmation.

Primary sources from guidance:

- Creatinine blood test - MedlinePlus: https://medlineplus.gov/ency/article/003475.htm
- Estimated Glomerular Filtration Rate - Cleveland Clinic: https://my.clevelandclinic.org/health/diagnostics/21593-estimated-glomerular-filtration-rate-egfr

## Future: Lipid-Risk Pattern

This is not part of the MVP implementation.

Candidate thresholds from guidance:

- LDL below 100 mg/dL: optimal.
- LDL 100-129 mg/dL: near optimal.
- LDL 130-159 mg/dL: borderline high.
- LDL 160-189 mg/dL: high.
- LDL 190 mg/dL or higher: very high.
- Total cholesterol below 200 mg/dL: desirable.
- HDL thresholds depend on sex.

Sources from guidance:

- LDL: The Bad Cholesterol - MedlinePlus: https://medlineplus.gov/ldlthebadcholesterol.html
- Cholesterol levels - Cleveland Clinic: https://my.clevelandclinic.org/health/articles/11920-cholesterol-numbers-what-do-they-mean

## Future: CRP/Inflammation Pattern

This is not part of the MVP implementation.

Candidate thresholds from guidance:

- CRP below 0.9 mg/dL: typical normal range.
- CRP 1.0-10 mg/dL: moderate elevation.
- CRP above 10 mg/dL: marked elevation.
- CRP above 50 mg/dL: severe elevation.

Source from guidance:

- C-Reactive Protein Test - Cleveland Clinic: https://my.clevelandclinic.org/health/diagnostics/23056-c-reactive-protein-crp-test

