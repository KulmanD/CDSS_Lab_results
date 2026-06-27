# CDSS Lab Results

Academic prototype for a deterministic, rule-based clinical decision support system (CDSS) that helps patients interpret selected laboratory results. The system is not a diagnostic tool and does not prescribe treatment. It classifies lab values into risk categories, highlights selected trends over time, and produces plain-language explanations that should be reviewed with a clinician.

## Implemented Scope

The project implements deterministic rules for the lab-result families from the mini-project guidance:

- Anemia-like pattern: hemoglobin with RBC indices such as MCV.
- Glucose-risk pattern: fasting glucose and HbA1c.
- Kidney-function alert: creatinine and eGFR.
- Lipid-risk pattern: total cholesterol, LDL, HDL, triglycerides, and VLDL when available.
- CRP/inflammation pattern: CRP threshold bands.

The API also includes optional temporary in-memory saved history for demo trend workflows. It is not production persistence and resets when the API process restarts.

Example upload files are available in `data/examples/`. The frontend uses one upload control for CSV or text-based PDF files. PDF upload is supported only when extracted text contains the same CSV-compatible columns; scanned PDFs and arbitrary lab-report layouts are out of scope.

## No AI Runtime Policy

This project must not require Gemini, OpenAI, LLMs, or any AI API key. Runtime behavior must come from deterministic rules, documented thresholds, and transparent evidence fields. AI tools may help contributors write code or documentation outside the application, but the application itself must remain rule-based.

## Planned Architecture

- `backend/`: Python rule engine, FastAPI API, pytest tests.
- `frontend/`: React + Vite web client.
- `data/`: synthetic example inputs, expected outcomes, and evaluation datasets.
- `docs/`: architecture, rules, thresholds, API contract, evaluation plan, safety notes, and agent handoff.

Start with:

- [Project map](docs/PROJECT_MAP.md)
- [Workstreams and no-conflict split](docs/WORKSTREAMS.md)
- [Mini-project guidance summary](docs/MINI_PROJECT_GUIDANCE_SUMMARY.md)
- [Rule engine spec](docs/RULE_ENGINE_SPEC.md)
- [Threshold references](docs/thresholds.md)
- [MVP readiness review](docs/MVP_READINESS_REVIEW.md)
- [Agent handoff](docs/AGENT_HANDOFF.md)

## Safety Notice

This prototype is educational software. It can flag values that match predefined rules, but it cannot diagnose disease, account for full clinical context, or replace professional medical advice. Every user-facing result must include a clear recommendation to discuss abnormal or concerning results with a qualified clinician.
