# Nutrient ClawHub refresh wave plan

This plan uses the shared `contract-architect`, `implementation-worker`, and `critic-reviewer` roles. The live DWS API contract is the source of truth; the stale `nutrient-document-processing-universal` package is comparison evidence only.

No DWS request may be made during implementation. The exact metered boundary is a request to the DWS Processor API; any later live smoke requires a separate estimate and approval immediately before that request.

## Execution ledger

| Task | Status | Owner | Evidence / blocker |
| --- | --- | --- | --- |
| ND-T1 | completed | contract-architect | Current source, published `1.1.2`, SDK `3.1.0`, and provider contract deltas are mapped; no DWS request was made. |
| ND-T2 | completed | implementation-worker | Product routing, SDK 3.1.0 helpers, portable paths, metered-call consent, irreversible-operation checks, credential safety, and 17 offline tests pass critic review. |
| ND-T3 | completed | contract-architect | Validator, CI, 2.0.0 changelog, exact-source manifest, validation-only default, dry-run preview, and explicit future publish gates pass offline validation. |
| ND-T4 | completed | critic-reviewer | Final critic closed CLI-auth, command-surface, workflow-control, immutable catalog/baseline, duplicate-key, and package-ignore drift findings; 17 skill tests and 29 adversarial release tests pass, including the pinned 0.23.3 config reader, packager behavior, and exact trigger/job/step metadata checks. Compilation, YAML parsing, manifest rendering, and repository validation pass with all external mutations unexecuted. |

## Release gates

- Offline tests and source validation must pass before any live smoke is considered.
- A live DWS smoke is paid and requires a separate action-time approval.
- ClawHub publishing, renaming, merging, hiding, or deleting remains unexecuted until final approval.
