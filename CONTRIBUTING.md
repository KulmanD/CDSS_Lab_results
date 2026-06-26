# Contributing

This repo is designed for handoff between teammates and coding agents. Keep changes small, documented, and traceable to GitHub issues.

## Workflow

1. Pick an issue from the current milestone.
2. Read the linked docs before editing code.
3. Create a feature branch.
4. Add or update tests for behavior changes.
5. Open a pull request with a concise summary and validation notes.

## Rules For Contributors

- Do not add Gemini, OpenAI, LLM, or AI runtime dependencies.
- Do not replace deterministic rules with model-generated conclusions.
- Keep thresholds centralized and cited in `docs/thresholds.md`.
- Every rule result must expose its evidence and limitations.
- Use synthetic/anonymized data only.
- Use non-diagnostic language in user-facing text.

## Definition Of Done

- The change is linked to an issue.
- Relevant docs are updated.
- Tests or validation steps are listed in the PR.
- Safety disclaimers are preserved.
- No real patient data is committed.

