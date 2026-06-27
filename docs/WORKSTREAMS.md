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
- #14 Research and implement lipid-risk rules.
- #15 Research and implement CRP/inflammation rules.
- #16 Add optional saved patient history after MVP.
- #17 Add expanded evaluation data for postponed rule families.

The future-enhancement issues (#14-#17) were delivered end-to-end in PR #21 (`denis/future-enhancements`) and are now part of `main`. Lipid-risk rules, CRP/inflammation rules, optional in-memory saved history, and the expanded lipid/CRP evaluation data are all implemented and covered by tests and the evaluation script.

Primary files touched by that work:

- `backend/cdss_core/`
- `backend/api/`
- `backend/app/`
- `backend/tests/`
- `data/evaluation/`
- `backend/evaluation.py`
- `frontend/src/App.jsx`
- `docs/`

## Active Implementation

No active implementation lane is open. The MVP and the future-enhancement rule families are complete and merged.

## Teammate Review Lane

PR #21 has been independently reviewed. Confirmed in that review:

- Lipid and CRP threshold implementation matches `docs/thresholds.md`.
- The API contract matches actual history endpoint behavior.
- Synthetic lipid/CRP evaluation cases pass (25 cases, F1 = 1.0 across all rule families).
- Wording stays aligned with the mini-project guidance and remains non-diagnostic.

Follow-up edge cases surfaced during review are tracked as GitHub issues rather than reopening this lane.

## No Remaining Parallel Implementation Lane

There is no remaining parallel implementation lane. New work should start from the follow-up review issues rather than overlapping edits to the merged files.

## Coordination Rules

- Use clear branch names such as `denis/end-to-end-mvp`.
- Prefer one pull request per chunk.
- Reference issue numbers in commits and pull requests.
- Do not add Gemini, OpenAI, LLM, or model-generated runtime behavior.
- Runtime behavior must remain deterministic and traceable to `docs/thresholds.md`.
