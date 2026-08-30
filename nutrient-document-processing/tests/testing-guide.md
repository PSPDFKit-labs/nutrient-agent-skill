# Testing Guide

## Offline validation (default)

Run from the repository root. These commands do not need an API key and must not make a DWS request:

```bash
python tools/validate-repo.py
python -m py_compile nutrient-document-processing/scripts/*.py nutrient-document-processing/scripts/lib/common.py nutrient-document-processing/assets/templates/custom-workflow-template.py
python -m unittest discover -s tests -v
```

The offline suite verifies the pinned dependency, package metadata, inclusive page ranges, Processor JSON-content fixtures, ContentOutput handling, consent gate, staged-only AI redaction, protected password input, portable template, and atomic no-overwrite output behavior.

## Help smoke

The unittest suite invokes every single-operation script with `--help` using Python. Help must exit zero without an API key or installed SDK. Do not add `--confirm-external-processing` to a smoke test.

## Optional live validation

A live Processor request is paid and transfers the selected document to Nutrient. It is not part of repository validation.

Immediately before one live smoke:

1. select one exact operation and input;
2. obtain its current credit estimate;
3. show the user the product, operation, input transfer, estimate, and new output path;
4. wait for explicit approval;
5. run only that approved command with `--estimated-credits NUMBER --confirm-external-processing`;
6. inspect the artifact and account usage.

Do not batch all helpers into a live test. A retry, redaction apply, signature, or second operation needs a new estimate and approval. No live request was used to validate this package refresh.

## High-risk output checks

- **Staged redaction:** render every page, review matches and misses, and do not call it redacted.
- **Applied redaction:** after separate approval, render again and search/extract for the sensitive values.
- **Signing:** validate the expected embedded signature, certificate trust chain, timestamp, and post-signature modification state with an independent validator.
- **Compliance:** use the user's required PDF/A or accessibility validator; a successful request alone is not proof of conformance.
