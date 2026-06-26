# Project Map

This repo is organized so teammates and agents can find the next task without relying on private chat history.

## Directories

- `backend/`: planned Python package for schemas, deterministic rules, dispatcher, CSV parsing, FastAPI routes, and tests.
- `frontend/`: planned React + Vite client for manual entry, CSV upload, result cards, disclaimer text, and trend display.
- `data/`: synthetic CSV/JSON examples, evaluation datasets, and expected outcomes.
- `docs/`: source-of-truth planning and design documents.
- `.github/`: issue templates and pull request template.

## Reading Order

1. `README.md`
2. `docs/MINI_PROJECT_GUIDANCE_SUMMARY.md`
3. `docs/WORKSTREAMS.md`
4. `docs/ARCHITECTURE.md`
5. `docs/DATA_MODEL.md`
6. `docs/RULE_ENGINE_SPEC.md`
7. `docs/thresholds.md`
8. `docs/API_CONTRACT.md`
9. `docs/EVALUATION_PLAN.md`
10. `docs/SAFETY_AND_LIMITATIONS.md`
11. `docs/MVP_READINESS_REVIEW.md`
12. `docs/AGENT_HANDOFF.md`

## MVP Ownership Areas

- Backend rule engine: anemia, glucose risk, kidney function, trend checks, dispatcher.
- API: JSON analysis endpoint, CSV upload endpoint, health endpoint.
- Frontend: form input, CSV upload, structured result display, disclaimer.
- Evaluation: synthetic records, expected outcomes, metric script.
- Documentation: thresholds, limitations, rule descriptions, user instructions.
