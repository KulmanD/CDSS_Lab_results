# Agent Handoff

Use this file when starting a new teammate or assistant session.

## Current State

This repo now contains the deterministic CDSS implementation for the mini-project scope. Backend rules, API endpoints, frontend entry forms, synthetic evaluation data, tests, CI, and documentation are present.

## Hard Constraints

- Do not add Gemini, OpenAI, LLM, or AI runtime dependencies.
- Do not rely on user-provided reference ranges as the only source of clinical classification.
- Do not commit real patient data.
- Do not present results as diagnoses.
- Keep threshold values traceable in `docs/thresholds.md`.

## Implemented Rule Scope

- Anemia-like pattern: hemoglobin plus MCV.
- Glucose-risk pattern: fasting glucose plus HbA1c.
- Kidney-function alert: creatinine plus eGFR.
- Lipid-risk pattern: total cholesterol, LDL, HDL, triglycerides, and optional VLDL.
- CRP/inflammation pattern: CRP.
- Optional temporary in-memory saved history for demo trend workflows.

## Suggested Next Step

Review the implementation against `docs/DATA_MODEL.md`, `docs/RULE_ENGINE_SPEC.md`, `docs/thresholds.md`, `docs/API_CONTRACT.md`, and `docs/SAFETY_AND_LIMITATIONS.md`. Focus on deterministic behavior, threshold traceability, non-diagnostic wording, tests, and edge cases.

## MiniProject Salvage Policy

The old MiniProject repo can be used only for ideas:

- CSV column shape.
- RCV trend concept.
- Sample-data inspiration.

Do not reuse:

- Gemini integration.
- Mandatory API-key startup validation.
- Reference-range-only rule logic.
- Plaintext-password account code.
