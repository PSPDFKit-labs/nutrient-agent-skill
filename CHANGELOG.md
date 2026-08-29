# Changelog

## [2.0.0] - Unreleased

### Changed

- Establish `nutrient-document-processing` as the canonical ClawHub package and bind its release provenance to the exact `PSPDFKit-labs/nutrient-agent-skill` repository commit and skill path.
- Pin the Processor helper contract to `nutrient-dws==3.1.0`, correct inclusive page ranges and typed output handling, and separate Processor, Data Extraction, and Accessibility routing.
- Require action-time approval for every external credit-consuming request and safe no-overwrite output handling.

### Security

- Stage AI redactions for review before any separately approved irreversible application.
- Require explicit signing configuration, protected password input, and protected runtime credential injection without authenticated shell examples.

### Release

- Add offline contract tests, Agent Skill quick validation, an exact package-ignore profile, pinned-packager regression coverage, an exact provenance manifest, and a manual ClawHub workflow that defaults to validation and requires explicit commit, branch, confirmation, release-enablement variable, externally configured environment reviewers, and temporary owner-only JSON credential gates before publication.
- Keep publication, migration, rename, merge, hide, delete, and transfer actions unexecuted pending final human approval.
