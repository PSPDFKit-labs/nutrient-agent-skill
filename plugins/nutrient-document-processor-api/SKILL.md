---
name: nutrient-document-processor-api
description: Execute common document-processing tasks with the nutrient-dws Python client via uv run scripts. Use when the user asks to convert, merge, split, OCR, extract text/tables/key-value pairs, watermark, redact, sign, optimize, protect, or reorder document content, or when they need a custom multi-step document pipeline script built from Nutrient DWS workflow actions.
---

# Nutrient Document Processor API

Export the API key before running any script:

```
export NUTRIENT_API_KEY="nutr_sk_..."
```

Run every script with `uv run` from the plugin root. The `nutrient-dws` package is fetched automatically.

Page ranges use `start:end` (0-based, end-exclusive). Negative indices count from the end. Comma-separate multiple ranges: `0:2,3:5,-2:-1`.

---

## Convert & Transform

**Convert format** — office-to-pdf, pdf-to-markdown/html/image, etc.
```
uv run scripts/convert.py --input doc.pdf --format docx --out doc.docx
```
Formats: pdf, pdfa, pdfua, docx, xlsx, pptx, png, jpeg, jpg, webp, html, markdown

**Merge files** — combine two or more documents into one PDF
```
uv run scripts/merge.py --inputs cover.pdf,report.pdf,appendix.pdf --out combined.pdf
```

**Split by page ranges** — split one PDF into multiple PDFs
```
uv run scripts/split.py --input report.pdf --ranges 0:2,3:5 --out-dir out --prefix section
```

**OCR** — make scanned documents searchable
```
uv run scripts/ocr.py --input scan.pdf --languages english --out scan-ocr.pdf
```
Multiple languages: `--languages english,german`

**Rotate pages** — rotate all or specific pages
```
uv run scripts/rotate.py --input doc.pdf --angle 90 --out rotated.pdf
```
Optional: `--pages 0:2` to rotate only specific pages. Angles: 90, 180, 270.

**Optimize PDF** — reduce file size
```
uv run scripts/optimize.py --input large.pdf --out optimized.pdf
```
Optional: `--options-json '{"mrcCompression":true}'`

---

## Extract & Analyze

**Extract text** — get text content as JSON
```
uv run scripts/extract-text.py --input doc.pdf --out text.json
```
Optional: `--pages 0:5` for specific pages, `--plain-out text.txt` for plain-text export

**Extract tables** — get table data as JSON
```
uv run scripts/extract-table.py --input report.pdf --out tables.json
```
Optional: `--pages 0:3`

**Extract key-value pairs** — pull structured data from forms/invoices
```
uv run scripts/extract-key-value-pairs.py --input invoice.pdf --out kvp.json
```
Optional: `--pages 0:1`

---

## Edit & Secure

**Text watermark** — stamp text on every page
```
uv run scripts/watermark-text.py --input doc.pdf --text CONFIDENTIAL --out watermarked.pdf
```
Optional: `--opacity 0.3 --font-size 72 --rotation 45`

**AI redaction** — redact content matching natural-language criteria
```
uv run scripts/redact-ai.py --input policy.pdf --criteria "Remove all email addresses" --mode apply --out redacted.pdf
```
Modes: `stage` (default, marks redactions) or `apply` (removes content). Optional: `--pages 0:5`

**Digital signature** — sign a PDF (local file input only)
```
uv run scripts/sign.py --input contract.pdf --out signed.pdf
```
Optional: `--signature-json '{"signerName":"Jane Doe","reason":"Approval"}'` or `--signature-json-file sig.json`, `--image sig.png`, `--graphic-image logo.png`

**Password protect** — encrypt with user/owner passwords
```
uv run scripts/password-protect.py --input doc.pdf --user-password upass --owner-password opass --out protected.pdf
```
Optional: `--permissions printing,modifying`

---

## Page Operations

**Add blank pages**
```
uv run scripts/add-pages.py --input doc.pdf --count 2 --out with-blanks.pdf
```
Optional: `--index 0` to insert at a specific position (default: end)

**Delete pages** — remove pages by 0-based index
```
uv run scripts/delete-pages.py --input doc.pdf --pages 0,2,-1 --out trimmed.pdf
```

**Duplicate/reorder pages** — build a new PDF from page indices (supports duplicates)
```
uv run scripts/duplicate-pages.py --input doc.pdf --pages 2,0,1,1 --out reordered.pdf
```

---

## Multi-Step Pipelines

Pre-built scripts that chain operations in a single run.

**OCR + watermark**
```
uv run scripts/ocr-watermark.py --input scan.pdf --text CONFIDENTIAL --out result.pdf
```
Optional: `--languages english,german --opacity 0.3 --rotation 45 --font-size 72`

**OCR + optimize**
```
uv run scripts/ocr-optimize.py --input scan.pdf --out optimized.pdf
```
Optional: `--language english`

**OCR + watermark (Codex variant)** — OCR then stamp with DRAFT watermark
```
uv run scripts/ocr-watermark-codex.py --input scan.pdf --out result.pdf
```
Optional: `--language english --watermark-text DRAFT --opacity 0.25 --rotation 45`

**Redact + watermark** — AI-redact then stamp REDACTED on every page
```
uv run scripts/redact-then-watermark.py --input doc.pdf --criteria "Remove all SSNs" --out redacted-stamped.pdf
```

**Merge + split** — merge two PDFs then split into two parts by range
```
uv run scripts/merge-then-split.py --inputs a.pdf,b.pdf --range-a 0:2 --range-b 2: --out-dir out
```

---

## Custom Pipelines

When no existing script covers the workflow, create a new one:

1. Copy `assets/templates/custom-workflow-template.py` to `scripts/<task-name>.py`.
2. Edit the `actions` list — use `BuildActions.ocr(lang)`, `BuildActions.watermark_text(text, opts)`, etc.
3. For multi-step tasks that mix direct methods and workflows, call `client.<method>()` first, then pass the result bytes into `client.workflow().add_file_part(buffer, actions=...)`.
4. Keep scripts CLI-driven (`--input`, `--out`, explicit options), deterministic, and runnable end-to-end.
5. Run the script with sample input to verify before finalizing.

## Rules

- Fail fast when required arguments are missing.
- `sign` only accepts local file paths (not URLs).
- Write outputs to explicit paths and print created files.
- Do not log secrets.
- All client methods are async — scripts use `asyncio.run(main())`.
- If the package import fails, install with `uv add nutrient-dws`.
