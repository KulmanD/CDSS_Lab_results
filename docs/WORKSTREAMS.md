# Workstreams And Current Split

Use this file to coordinate work between Denis and the second teammate. It shows what is complete, what is currently active, and which files each person should avoid touching to reduce merge conflicts.

## Current Status

Completed and merged:

- #1 Define data models for patient demographics, lab records, history, and rule results.
- #2 Implement anemia-like rule family.
- #3 Implement glucose-risk rule family.
- #4 Implement kidney/eGFR rule family.
- #5 Implement trend analysis for anemia and kidney checks.
- #6 Implement deterministic rule dispatcher.

Implemented so far:

- Dependency-free backend core in `backend/cdss_core/`.
- Dataclass models for demographics, lab records, rule results, and analysis responses.
- Deterministic anemia, glucose, and kidney MVP rules.
- Trend checks for hemoglobin, eGFR, and creatinine.
- Dispatcher with stable rule order, disclaimer, and overall urgency.
- Standard-library backend unit tests in `backend/tests/test_rule_engine.py`.

Still open:

- #7 Build FastAPI JSON analysis endpoint.
- #8 Build FastAPI CSV upload endpoint.
- #9 Build React/Vite UI for manual entry, CSV upload, results, disclaimer, and trends.
- #10 Create synthetic MVP evaluation dataset with expected outcomes.
- #11 Add pytest coverage for normal, borderline, abnormal, and trend cases.
- #12 Add CI for backend tests.
- #13 Review MVP against mini-project guidance.
- #14-#17 Future enhancement issues; do not start until the MVP is stable.

## Active Work Right Now

Denis lane:

- Active next chunk: #7 and #8, FastAPI API MVP.
- Planned branch name: `denis/api-mvp`.
- Primary files: `backend/api/`, `backend/app/`, backend dependency/config files, and API-specific tests.
- Do not edit: `frontend/` and `data/` evaluation datasets unless an API fixture is required.

Teammate lane:

- Recommended next chunk: #9, React/Vite frontend MVP.
- This is a good fit for the teammate using Claude Max because it can work from `docs/API_CONTRACT.md`, build the UI shell, and later wire to the API branch.
- Planned branch name: `teammate/frontend-mvp`.
- Primary files: `frontend/`.
- Do not edit: backend rule logic in `backend/cdss_core/`, API route files, or evaluation datasets.

## Next After API And Frontend

Shared remaining chunk:

- #10 Create synthetic MVP evaluation dataset with expected outcomes.
- #11 Expand test coverage beyond the backend core tests already added.
- #12 Add CI for backend tests.
- #13 Review MVP against mini-project guidance.

Recommended owner after current work:

- Teammate can take the synthetic dataset and expected outcomes if frontend is done first.
- Denis can take CI and final guidance review after API is merged.

## File Ownership Rules

Denis owns for the current API chunk:

- `backend/api/`
- `backend/app/`
- API tests under `backend/tests/`
- Backend dependency files if needed.

Teammate owns for the current frontend chunk:

- `frontend/`
- Frontend package/config files.
- Frontend README updates.

Shared only by coordination:

- `docs/API_CONTRACT.md`
- `docs/PROJECT_MAP.md`
- `docs/AGENT_HANDOFF.md`
- `README.md`

If a shared file must change, mention it in the pull request summary so the other person can rebase.

## Future Enhancements

Do not start these until anemia, glucose, kidney, API, frontend, and MVP evaluation are working:

- #14 Research and implement lipid-risk rules.
- #15 Research and implement CRP/inflammation rules.
- #16 Add optional saved patient history after MVP.
- #17 Add expanded evaluation data for postponed rule families.

## Coordination Rules

- Use clear branch names such as `denis/api-mvp` and `teammate/frontend-mvp`.
- Prefer one pull request per chunk.
- Reference issue numbers in commits and pull requests.
- Do not add Gemini, OpenAI, LLM, or model-generated runtime behavior.
- Runtime behavior must remain deterministic and traceable to `docs/thresholds.md`.
- If a change crosses file ownership boundaries, leave a GitHub issue comment before editing the other lane.
