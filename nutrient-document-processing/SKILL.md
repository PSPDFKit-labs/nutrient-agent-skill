---
name: nutrient-document-processing
description: Use when tasks involve generating PDFs from HTML or URLs, converting Office/images/PDFs, assembling or splitting PDFs, OCRing and extracting content, redacting, watermarking, signing, filling, or producing compliance outputs like PDF/A, PDF/UA, and linearized PDFs with Nutrient DWS. Triggers include convert to PDF, OCR this scan, extract tables, merge these PDFs, redact PII, sign this PDF, make this PDF/A, or linearize for web delivery. Prefer the Nutrient MCP server when it is already configured, otherwise call the API directly.
metadata:
  short-description: Generate, convert, assemble, OCR, redact, sign, archive, and optimize documents
---

# Nutrient Document Processing

Use Nutrient DWS for managed document workflows where fidelity, compliance, or multi-step processing matters more than local-tool convenience.

## Setup assumptions
- Direct API calls use `Authorization: Bearer $NUTRIENT_API_KEY`.
- MCP setups commonly use `@nutrient-sdk/dws-mcp-server` with `NUTRIENT_DWS_API_KEY`.
- Open `references/request-basics.md` first when authentication or payload shape is the blocker.

## When to use
- Generate PDFs from HTML templates, uploaded assets, or remote URLs.
- Convert Office, HTML, image, and PDF files between supported formats.
- OCR scans and extract text, tables, or key-value pairs.
- Redact PII, watermark, sign, fill forms, merge, split, rotate, flatten, or encrypt PDFs.
- Produce delivery targets like PDF/A, PDF/UA, optimized PDFs, or linearized PDFs.
- Check credits before large, batch, or AI-heavy runs.

## Tool preference
1. Prefer the Nutrient MCP server when it is already configured. It handles file I/O and reduces multipart-request boilerplate.
2. Fall back to direct API calls when MCP is unavailable or the workflow is easier to express as an explicit payload.
3. Use local PDF utilities only for lightweight inspection. Use Nutrient when output fidelity or compliance matters.

## Request model
- Most workflows use `POST https://api.nutrient.io/build`.
- Use multipart requests when uploading local files. Use JSON requests when all inputs are remote URLs.
- `parts` describes source files, HTML inputs, remote URLs, page ranges, and passwords.
- `actions` applies ordered transformations such as OCR, redaction, watermarking, signing, flattening, or rotation.
- `output` selects the final format and delivery options such as `pdf`, `text`, `docx`, `png`, `pdfa`, `pdfua`, or optimized PDF output.
- Dedicated endpoints also exist for some tools such as PDF/UA auto-tagging, but `/build` is the default mental model.

Minimal direct-call template:

```bash
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F document.pdf=@document.pdf \
  -F 'instructions={"parts":[{"file":"document.pdf"}]}' \
  -o result.pdf
```

## Workflow
1. Identify the source type and the required final artifact.
2. Decide whether the job is generation, conversion, extraction, security/compliance, or a chained workflow.
3. Express the full pipeline in one payload when the ordering is clear and the artifact should stay in-memory on the server.
4. Save outputs with stable suffixes such as `-ocr`, `-redacted`, `-pdfa`, `-pdfua`, or `-linearized`.

## Decision rules
- If you control the source markup, prefer HTML generation over browser print workflows.
- Use remote `file.url` inputs when the source already lives at a stable URL and you want to avoid local uploads.
- Use `output.type` for conversion and finalization targets. Use `actions` for transformations.
- OCR before text extraction, key-value extraction, or semantic redaction on scans.
- Prefer preset or regex redaction when the target is explicit. Use AI redaction only for contextual or natural-language requests.
- Use the PDF manipulation reference for merge, split, rotate, flatten, and page-range workflows instead of inferring those payloads from conversion examples.
- Treat PDF/A and PDF/UA as compliance targets, not cosmetic export formats. Choose the target up front and validate final artifacts when requirements are contractual.
- For PDF/UA, clean born-digital inputs and structured HTML usually tag better than rasterized or flattened source PDFs.
- For delivery optimization, linearize or optimize unsigned output artifacts instead of mutating already signed files.
- When the user asks for multiple steps, keep destructive or final steps late in the sequence. Use the workflow recipes when ordering is ambiguous.

## Anti-patterns
- Do not OCR born-digital PDFs just because the task mentions extraction. Extract first and OCR only if the text layer is missing.
- Do not flatten forms or annotations until the user confirms the artifact no longer needs to stay editable.
- Do not sign, archive, or linearize intermediate working files. Keep those as final-delivery steps.
- Do not promise PDF/A or PDF/UA compliance without a validation step when the requirement is contractual.

## Reference map
Read only what you need:

- `references/request-basics.md` -> endpoint model, auth, multipart vs JSON, credits, limits, and errors
- `references/generation-and-conversion.md` -> HTML/URL generation and format conversion
- `references/pdf-manipulation.md` -> merge, split, page-range, rotate, and flatten workflows
- `references/extraction-and-ocr.md` -> OCR, text extraction, tables, and key-value workflows
- `references/security-signing-and-forms.md` -> redaction, watermarking, signatures, forms, and passwords
- `references/compliance-and-optimization.md` -> PDF/A, PDF/UA, optimization, and linearization
- `references/workflow-recipes.md` -> end-to-end sequencing patterns for common business document workflows

## References
- [Reference index](references/REFERENCE.md)
- [API docs](https://www.nutrient.io/api/documentation/)
- [Processor API overview](https://www.nutrient.io/api/processor-api/)
- [API playground](https://dashboard.nutrient.io/processor-api/playground/)
- [MCP server](https://github.com/PSPDFKit/nutrient-dws-mcp-server)
