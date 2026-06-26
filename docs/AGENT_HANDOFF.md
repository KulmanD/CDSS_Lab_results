# Agent Handoff

Use this file when starting a new Codex or teammate session.

## Current State

This repo is in documentation bootstrap state. It defines the planned architecture, MVP rule scope, data model, API contract, and issue structure. Implementation code is intentionally not part of this first pass.

## Hard Constraints

- Do not add Gemini, OpenAI, LLM, or AI runtime dependencies.
- Do not rely on user-provided reference ranges as the only source of clinical classification.
- Do not commit real patient data.
- Do not present results as diagnoses.
- Keep threshold values traceable in `docs/thresholds.md`.

## MVP Rule Scope

Implement these first:

- Anemia-like pattern: hemoglobin plus MCV.
- Glucose-risk pattern: fasting glucose plus HbA1c.
- Kidney-function alert: creatinine plus eGFR.

Postpone these:

- Lipid-risk rules.
- CRP/inflammation rules.

## Suggested Next Step

Pick one GitHub issue from the `Backend Rule Engine MVP` milestone. Read `docs/DATA_MODEL.md`, `docs/RULE_ENGINE_SPEC.md`, and `docs/thresholds.md` before writing code.

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

