# Workstreams And No-Conflict Split

Use this file to divide work between teammates and coding agents. Each workstream owns a distinct folder surface to reduce merge conflicts.

## Workstream A: Backend Core Rules

Recommended owner: Codex current session.

Issues:

- #1 Define data models for patient demographics, lab records, history, and rule results.
- #2 Implement anemia-like rule family.
- #3 Implement glucose-risk rule family.
- #4 Implement kidney/eGFR rule family.
- #5 Implement trend analysis for anemia and kidney checks.
- #6 Implement deterministic rule dispatcher.
- Backend portion of #11 Add pytest coverage.

Primary files:

- `backend/`
- `backend/tests/`

Do not edit:

- `frontend/`
- API route files once another owner starts API work.
- `data/` evaluation datasets except tiny fixtures needed for backend tests.

## Workstream B: FastAPI API

Recommended owner: teammate 1.

Issues:

- #7 Build FastAPI JSON analysis endpoint.
- #8 Build FastAPI CSV upload endpoint.

Primary files:

- `backend/app/`
- `backend/api/`
- API-specific tests.

Start condition:

- Wait until Workstream A defines importable schemas and dispatcher.

Do not edit:

- Core rule functions except through a separate issue/PR.
- `frontend/`.

## Workstream C: React/Vite Frontend

Recommended owner: teammate 2.

Issues:

- #9 Build React/Vite UI for manual entry, CSV upload, results, disclaimer, and trends.

Primary files:

- `frontend/`

Start condition:

- Can begin from `docs/API_CONTRACT.md`; update wiring after API endpoints are available.

Do not edit:

- `backend/` rule logic.
- `data/` evaluation datasets.

## Workstream D: Evaluation And CI

Recommended owner: teammate 3.

Issues:

- #10 Create synthetic MVP evaluation dataset with expected outcomes.
- Evaluation portion of #11 Add pytest coverage.
- #12 Add CI for backend tests.
- #13 Review MVP against mini-project guidance.

Primary files:

- `data/`
- `backend/tests/`
- `.github/workflows/`
- evaluation documentation updates.

Start condition:

- Can draft datasets immediately from `docs/thresholds.md`.
- CI should wait until backend dependency files exist.

Do not edit:

- Core rule implementation except to add test-driven bug reports.
- Frontend components.

## Workstream E: Future Enhancements

Recommended owner: no one until MVP is stable.

Issues:

- #14 Research and implement lipid-risk rules.
- #15 Research and implement CRP/inflammation rules.
- #16 Add optional saved patient history after MVP.
- #17 Add expanded evaluation data for postponed rule families.

Rule:

- Do not start these until anemia, glucose, kidney, API, frontend, and MVP evaluation are working.

## Coordination Rules

- Each owner should work on a separate branch.
- Prefer one PR per workstream chunk.
- Reference issue numbers in commits and PRs.
- Do not add AI, LLM, Gemini, OpenAI, or model-generated runtime behavior.
- If a change crosses workstream boundaries, leave a GitHub issue comment before editing the other owner surface.

