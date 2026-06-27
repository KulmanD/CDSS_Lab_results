# Workstreams And Current Split

Use this file to coordinate work between Denis and the second teammate. It shows what is complete, what is active, and what should wait.

## Completed And Merged

- #1 Define data models for patient demographics, lab records, history, and rule results.
- #2 Implement anemia-like rule family.
- #3 Implement glucose-risk rule family.
- #4 Implement kidney/eGFR rule family.
- #5 Implement trend analysis for anemia and kidney checks.
- #6 Implement deterministic rule dispatcher.
- #7 Build FastAPI JSON analysis endpoint.
- #8 Build FastAPI CSV upload endpoint.
- #9 Build React/Vite UI for manual entry, CSV upload, results, disclaimer, and trends.
- #10 Create synthetic MVP evaluation dataset with expected outcomes.
- #11 Add coverage for normal, borderline, abnormal, and trend cases.
- #12 Add CI for backend tests and MVP validation.
- #13 Review MVP against mini-project guidance.

## Active Implementation

Denis is implementing the remaining future-enhancement issues end-to-end on branch `denis/future-enhancements`:

- #14 Research and implement lipid-risk rules.
- #15 Research and implement CRP/inflammation rules.
- #16 Add optional saved patient history after MVP.
- #17 Add expanded evaluation data for postponed rule families.

Primary files in this chunk:

- `backend/cdss_core/`
- `backend/api/`
- `backend/app/`
- `backend/tests/`
- `data/evaluation/`
- `backend/evaluation.py`
- `frontend/src/App.jsx`
- `docs/`

## Teammate Review Lane

The second teammate should review after `denis/future-enhancements` is pushed:

- Lipid and CRP threshold implementation against `docs/thresholds.md`.
- API contract versus actual history endpoint behavior.
- Synthetic lipid/CRP evaluation cases and missing edge cases.
- Final alignment with the mini-project guidance and non-diagnostic wording.

Claude Max is best used here as an independent reviewer/evaluator rather than parallel implementation on the same files.

## No Remaining Parallel Implementation Lane

After this branch is pushed, the second teammate should review rather than implement overlapping changes. If new issues are found, create follow-up issues from the review findings.

## Coordination Rules

- Use clear branch names such as `denis/end-to-end-mvp`.
- Prefer one pull request per chunk.
- Reference issue numbers in commits and pull requests.
- Do not add Gemini, OpenAI, LLM, or model-generated runtime behavior.
- Runtime behavior must remain deterministic and traceable to `docs/thresholds.md`.
