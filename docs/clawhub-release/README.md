# ClawHub release gate

The `ClawHub release provenance` workflow is manual and defaults to validation only. Its preview and publish commands are bound to the exact repository, runtime commit, runtime ref, package path, version, publisher, and catalog metadata in `release-manifest.template.json`.

Before a future publication, an administrator must separately configure all of the following in GitHub:

- Create the `clawhub-production` environment and configure required reviewers. Merely naming the environment in workflow YAML does not add reviewer protection.
- Set the repository or `clawhub-production` environment variable `CLAWHUB_RELEASE_ENABLED` to exactly `true`. A missing value or any other value fails closed.
- Store the ClawHub credential as the `CLAWHUB_TOKEN` secret for the `clawhub-production` environment. The workflow writes it to a temporary owner-only ClawHub JSON config, uses that config for `whoami` and publication, and removes it in an always-run cleanup step.

The future human operator must select `publish`, provide the full commit SHA, and enter the exact confirmation phrase `PUBLISH nutrient-document-processing 2.0.0`. The validate and dry-run modes cannot publish.

`public-baseline.json` records `nutrient-document-processing-universal@1.1.2` only as the migration source and `nutrient-document-processing@2.0.0` as the canonical target. Publication, migration, rename, merge, hide, delete, and transfer actions remain disabled and require separate approval and implementation.
