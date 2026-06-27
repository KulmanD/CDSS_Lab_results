# Threshold References

This file is the source of truth for MVP threshold values. Implementation code should reference centralized constants that match this document.

## Anemia-Like Pattern

Inputs:

- Hemoglobin.
- MCV.

Initial MVP thresholds:

- Hemoglobin below 12 g/dL in pre-menopausal women suggests anemia-range low hemoglobin.
- Hemoglobin below 13 g/dL in men and post-menopausal women suggests anemia-range low hemoglobin.
- Hemoglobin above 17.5 g/dL in men (15.5 g/dL in women) is above the common upper reference range and is highlighted for review. This is not a diagnosis; high hemoglobin can reflect dehydration, smoking, lung disease, or a primary marrow condition. Unknown sex uses the higher 17.5 g/dL cutoff to avoid over-flagging.
- Hemoglobin below 7 g/dL or above 20 g/dL is a critical value that escalates to urgent review.
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

- Fasting glucose below 54 mg/dL: critically low, escalates to urgent review.
- Fasting glucose below 70 mg/dL: low glucose warning.
- Fasting glucose below 100 mg/dL: normal range.
- Fasting glucose 100-125 mg/dL: prediabetes-risk range.
- Fasting glucose 126 mg/dL or higher: diabetes-range value that needs clinician review.
- Fasting glucose 400 mg/dL or higher: critically high, escalates to urgent review.
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
- Creatinine 4.0 mg/dL or higher is a critical value that escalates to urgent review.

Primary sources from guidance:

- Creatinine blood test - MedlinePlus: https://medlineplus.gov/ency/article/003475.htm
- Estimated Glomerular Filtration Rate - Cleveland Clinic: https://my.clevelandclinic.org/health/diagnostics/21593-estimated-glomerular-filtration-rate-egfr

## Lipid-Risk Pattern

Inputs:

- Total cholesterol.
- LDL.
- HDL.
- Triglycerides.
- VLDL when available.

Implemented thresholds:

- LDL below 100 mg/dL: optimal.
- LDL 100-129 mg/dL: near optimal.
- LDL 130-159 mg/dL: borderline high.
- LDL 160-189 mg/dL: high.
- LDL 190 mg/dL or higher: very high.
- Total cholesterol below 200 mg/dL: desirable.
- Total cholesterol 200-239 mg/dL: borderline high.
- Total cholesterol 240 mg/dL or higher: high.
- HDL below 40 mg/dL in men: low.
- HDL below 50 mg/dL in women: low.
- Triglycerides below 150 mg/dL: normal.
- Triglycerides 150-199 mg/dL: borderline high.
- Triglycerides 200-499 mg/dL: high.
- Triglycerides 500 mg/dL or higher: very high.
- VLDL below 30 mg/dL: usual range.
- VLDL 30 mg/dL or higher: above usual range.

Implementation notes:

- LDL 100-129 mg/dL is reported as near optimal but does not trigger the rule by itself.
- Lipid treatment goals depend on overall cardiovascular risk, diabetes, medications, fasting status, pregnancy, and clinician context.
- The prototype expects lipid values in mg/dL and does not convert units.

Sources from guidance:

- LDL: The Bad Cholesterol - MedlinePlus: https://medlineplus.gov/ldlthebadcholesterol.html
- Cholesterol levels - Cleveland Clinic: https://my.clevelandclinic.org/health/articles/11920-cholesterol-numbers-what-do-they-mean

## CRP/Inflammation Pattern

Input:

- CRP.

Implemented thresholds:

- CRP below 0.9 mg/dL: typical normal range.
- CRP 0.9-0.99 mg/dL: near upper reference range, reported without triggering.
- CRP 1.0-10 mg/dL: moderate elevation.
- CRP above 10 mg/dL: marked elevation.
- CRP above 50 mg/dL: severe elevation.

Implementation notes:

- CRP is nonspecific and does not diagnose infection, inflammatory disease, autoimmune disease, or cardiovascular disease by itself.
- The prototype expects CRP values in mg/dL and does not convert units.

Source from guidance:

- C-Reactive Protein Test - Cleveland Clinic: https://my.clevelandclinic.org/health/diagnostics/23056-c-reactive-protein-crp-test
