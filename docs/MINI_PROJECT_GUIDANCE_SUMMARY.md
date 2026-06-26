# Mini-Project Guidance Summary

The guidance asks for an academic prototype of a rule-based CDSS for lab results. The system should classify selected lab values, highlight trends, and explain results in plain language. It must not diagnose, prescribe treatment, or imply medical certainty.

## Original Rule Families

The full guidance listed five candidate patterns:

- Anemia-like pattern: hemoglobin and RBC indices such as MCV.
- Glucose-risk pattern: fasting glucose and HbA1c.
- Lipid-risk pattern: total cholesterol, LDL, HDL, VLDL, triglycerides.
- Inflammation pattern: CRP, with possible future ESR/neutrophil additions.
- Kidney-function alert: eGFR and creatinine.

## MVP Decision

The MVP will implement:

- Anemia-like pattern.
- Glucose-risk pattern.
- Kidney-function alert.

Lipid-risk and CRP/inflammation rules are future enhancements because the MVP should prioritize the clearest, easiest-to-test cutoffs first.

## Required Project Capabilities

- Centralized thresholds with citations.
- Patient demographics, especially age and sex where thresholds depend on them.
- Rule functions that return `triggered`, `message`, `urgency_level`, and `evidence`.
- Dispatcher that runs every MVP rule on a record.
- Trend analysis where historical data is available.
- Unit tests for normal, borderline, abnormal, and trend cases.
- Evaluation dataset with expected outcomes.
- API layer for JSON records and CSV upload.
- Web client for manual entry, upload, results, and disclaimers.
- GitHub issues and milestones for collaboration.

## Safety Requirements

- Use non-diagnostic wording.
- Surface evidence and limitations.
- Recommend clinician review for abnormal or concerning results.
- Use synthetic or anonymized data only.
- Do not use AI/LLM services in runtime application behavior.

