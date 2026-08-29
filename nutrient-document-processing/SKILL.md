---
name: nutrient-document-processing
description: >-
  Process documents with Nutrient DWS Processor. Use for PDF generation and conversion, packet
  assembly, OCR, Processor JSON-content extraction, staged redaction, watermarking, signing,
  password protection, optimization, PDF/A, or PDF/UA output. Route high-fidelity markdown or
  spatial parsing to Nutrient Data Extraction, and accessibility auto-tagging/validation to Nutrient
  Accessibility instead of treating all three products as one API.
license: MIT-0
metadata:
  author: nutrient-sdk
  version: "2.0.0"
  homepage: "https://www.nutrient.io/api/"
  repository: "https://github.com/PSPDFKit-labs/nutrient-agent-skill"
  openclaw:
    requires:
      bins: [uv]
      env: [NUTRIENT_API_KEY]
    primaryEnv: NUTRIENT_API_KEY
---

# Nutrient Document Processing

Use this skill for managed document processing where fidelity, compliance, or a multi-step workflow justifies transferring the user's files to Nutrient DWS.

## Product router

Choose the product before estimating cost or selecting credentials:

| Need | Product | Route used here |
| --- | --- | --- |
| Convert, generate, assemble, OCR, JSON-content extraction, redact, sign, optimize, PDF/A or PDF/UA output | **DWS Processor** | Pinned Python helpers in `scripts/` using `NUTRIENT_API_KEY` |
| High-fidelity document parsing to markdown or spatial JSON | **Data Extraction** | Separate `/extraction/parse` product, credential, and credit pool; use its current official client/docs |
| Accessibility auto-tagging and PDF/UA validation workflow | **Accessibility** | Separate current Accessibility API/product; do not use the deprecated Processor `/processor/pdfua` endpoint |

Do not reuse Processor cost estimates, credentials, or payloads for Data Extraction or Accessibility.

## Setup

- Get a Processor API key from <https://dashboard.nutrient.io/sign_up/?product=processor>.
- Configure `NUTRIENT_API_KEY` through the agent host's protected runtime environment or secrets manager. Never ask the user to paste the key into chat, and never put it in command arguments, logs, generated scripts, or committed configuration. Verify only that the variable is present, not its value.

- Each script uses PEP 723 metadata pinned to `nutrient-dws==3.1.0`; run it with `uv run`.
- Run helpers by path from the installed skill directory. Never assume the current directory is the skill directory.
- Page ranges are zero-based and **inclusive**. `0:4` means five pages. Negative indexes count from the end.

## Paid-run approval gate

Every helper invocation sends document content to the external DWS Processor API and consumes credits. Before each run:

1. Identify the exact operation and every local file or remote URL transferred.
2. Obtain a current credit estimate from the dashboard/pricing applicable to that operation.
3. Present the product, operation, transferred inputs, estimate, and proposed output path to the user.
4. Wait for approval immediately before the request.
5. Only then pass both `--estimated-credits NUMBER` and `--confirm-external-processing`.

Approval never carries over to a retry, batch, second stage, redaction apply, or signature. Do not add the confirmation flag speculatively.

## Helper preference

1. Prefer a covered `scripts/*.py` helper; it uses the pinned typed client and safe output writer.
2. For a multi-step Processor job, copy and customize `assets/templates/custom-workflow-template.py` at runtime.
3. Use a raw request only when a current official contract is cited in the relevant reference. If the exact contract is uncertain, use the typed 3.1.0 helper instead of guessing.

All output helpers create files atomically with owner-only permissions and refuse to overwrite an existing path. Choose a new path for a retry.

## Single-operation helpers

- `convert.py`: `pdf`, `pdfa`, `pdfua`, `docx`, `xlsx`, `pptx`, `png`, `jpeg`, `jpg`, `webp`, `html`, or `markdown`; handles binary, text-content, and JSON-content results.
- `merge.py`, `split.py`, `add-pages.py`, `delete-pages.py`, `duplicate-pages.py`, `rotate.py`: page and packet operations.
- `ocr.py`, `extract-text.py`, `extract-table.py`, `extract-key-value-pairs.py`: Processor OCR and JSON-content extraction.
- `watermark-text.py`, `optimize.py`: delivery transformations.
- `redact-ai.py`: AI **staging only** for a local PDF. Visually review the staged result before a separately approved apply step.
- `sign.py`: local PDF only; requires an explicit JSON config file with `signatureType` and verifies the output is a PDF container. Independently validate the embedded signature and trust chain.
- `password-protect.py`: reads passwords only from owner-only local files (`chmod 600`), never argv.

## Multi-step workflow template

Do not commit a job-specific pipeline under `scripts/`. Copy the template to a task-specific temporary path, then point it back to the installed skill directory:

```bash
export NUTRIENT_SKILL_DIR="/absolute/path/to/nutrient-document-processing"
cp "$NUTRIENT_SKILL_DIR/assets/templates/custom-workflow-template.py" /tmp/ndp-workflow.py
# customize /tmp/ndp-workflow.py
NUTRIENT_SKILL_DIR="$NUTRIENT_SKILL_DIR" uv run /tmp/ndp-workflow.py --help
```

The final paid invocation still needs the operation estimate and explicit confirmation flags. Remove the temporary script when the job is complete unless the user asks to retain it.

## Safety rules

- OCR before extraction or redaction only when the source lacks a useful text layer.
- Redaction is two-stage: create annotations, visually review every match and missed match, then request separate approval to apply irreversibly. Search/render the final PDF to verify removal.
- Signing requires explicit CMS or CAdES configuration. Fill, flatten, redact, assemble, and optimize before signing; treat the signed PDF as immutable.
- Use real form field data expressed as Instant JSON or XFDF. Do not invent a `fillForm` build action.
- Keep passwords and signature secrets out of argv, logs, and committed JSON.
- Treat PDF/A and PDF/UA as compliance targets. Validate final artifacts with the user's required validator before claiming conformance.
- Never call the deprecated `/processor/pdfua` endpoint for a new integration.

## Reference map

- `references/request-basics.md`: product boundary, authentication, typed outputs, approval, and errors
- `references/generation-and-conversion.md`: current conversion and generation patterns
- `references/pdf-manipulation.md`: inclusive ranges and page operations
- `references/extraction-and-ocr.md`: Processor JSON-content extraction versus Data Extraction parsing
- `references/security-signing-and-forms.md`: staged redaction, signing, forms, passwords, and watermarking
- `references/compliance-and-optimization.md`: PDF/A, PDF/UA routing, optimization, and validation
- `references/workflow-recipes.md`: safe sequencing for multi-step jobs
