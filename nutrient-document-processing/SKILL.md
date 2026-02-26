---
name: nutrient-document-processing
description: >-
  Process documents with the Nutrient DWS API. Use this skill when the user wants to convert documents
  (PDF, DOCX, XLSX, PPTX, HTML, images), extract text or tables from PDFs, OCR scanned documents,
  redact sensitive information (PII, SSN, emails, credit cards), add watermarks, digitally sign PDFs,
  fill PDF forms, or check API credit usage. Activates on keywords: PDF, document, convert, extract,
  OCR, redact, watermark, sign, merge, compress, form fill, document processing.
license: Apache-2.0
metadata:
  author: nutrient-sdk
  version: "1.0"
  homepage: "https://www.nutrient.io/api/"
  repository: "https://github.com/PSPDFKit-labs/nutrient-agent-skill"
  compatibility: "Requires Node.js 18+ and internet. Works with Claude Code, Codex CLI, Gemini CLI, OpenCode, Cursor, Windsurf, GitHub Copilot, Amp, or any Agent Skills-compatible product."
---

# Nutrient Document Processing

Process, convert, extract, redact, sign, and manipulate documents using the [Nutrient DWS Processor API](https://www.nutrient.io/api/).

## Setup

You need a Nutrient DWS API key. Get one free at <https://dashboard.nutrient.io/sign_up/?product=processor>.

Export the API key before running scripts:

```bash
export NUTRIENT_API_KEY="nutr_sk_..."
```

Scripts live inside this skill's own directory. Before running any script, locate the skill directory and change into it or use the full path.

Find the skill directory:

```bash
SKILL_DIR=$(find ~/.claude/skills .claude/skills -maxdepth 2 -name "SKILL.md" -path "*/nutrient-document-processing/*" -exec dirname {} \; 2>/dev/null | head -1)
```

Then run scripts using the full path:

```bash
uv run "$SKILL_DIR/scripts/<script>.py" --help
```

Page ranges use `start:end` (0-based, end-exclusive). Negative indices count from the end. Use comma-separated ranges like `0:2,3:5,-2:-1`.

## Single-Operation Scripts

- Convert format: `uv run "$SKILL_DIR/scripts/convert.py" --input doc.pdf --format docx --out doc.docx`
- Merge files: `uv run "$SKILL_DIR/scripts/merge.py" --inputs a.pdf,b.pdf --out merged.pdf`
- Split by ranges: `uv run "$SKILL_DIR/scripts/split.py" --input doc.pdf --ranges 0:2,2: --out-dir out --prefix part`
- OCR: `uv run "$SKILL_DIR/scripts/ocr.py" --input scan.pdf --languages english --out scan-ocr.pdf`
- Rotate pages: `uv run "$SKILL_DIR/scripts/rotate.py" --input doc.pdf --angle 90 --out rotated.pdf`
- Optimize: `uv run "$SKILL_DIR/scripts/optimize.py" --input doc.pdf --out optimized.pdf`
- Extract text: `uv run "$SKILL_DIR/scripts/extract-text.py" --input doc.pdf --out text.json`
- Extract tables: `uv run "$SKILL_DIR/scripts/extract-table.py" --input doc.pdf --out tables.json`
- Extract key-value pairs: `uv run "$SKILL_DIR/scripts/extract-key-value-pairs.py" --input doc.pdf --out kvp.json`
- Add text watermark: `uv run "$SKILL_DIR/scripts/watermark-text.py" --input doc.pdf --text CONFIDENTIAL --out watermarked.pdf`
- AI redact: `uv run "$SKILL_DIR/scripts/redact-ai.py" --input doc.pdf --criteria "Remove all SSNs" --mode apply --out redacted.pdf`
- Sign: `uv run "$SKILL_DIR/scripts/sign.py" --input doc.pdf --out signed.pdf`
- Password protect: `uv run "$SKILL_DIR/scripts/password-protect.py" --input doc.pdf --user-password upass --owner-password opass --out protected.pdf`
- Add pages: `uv run "$SKILL_DIR/scripts/add-pages.py" --input doc.pdf --count 2 --out with-pages.pdf`
- Delete pages: `uv run "$SKILL_DIR/scripts/delete-pages.py" --input doc.pdf --pages 0,2,-1 --out trimmed.pdf`
- Duplicate/reorder pages: `uv run "$SKILL_DIR/scripts/duplicate-pages.py" --input doc.pdf --pages 2,0,1,1 --out reordered.pdf`

## Multi-Step Workflow Rule

Do not add new committed pipeline scripts under `scripts/`.

When the user asks for multiple operations in one run:

1. Copy `"$SKILL_DIR/assets/templates/custom-workflow-template.py"` to a temporary location (for example `/tmp/ndp-workflow-<task>.py`).
2. Implement the combined workflow in that temporary script.
3. Run it with `uv run /tmp/ndp-workflow-<task>.py ...`.
4. Return generated output files.
5. Delete the temporary script unless the user explicitly asks to keep it.

## Rules

- Fail fast when required arguments are missing.
- `sign` only accepts local file paths (not URLs).
- Write outputs to explicit paths and print created files.
- Do not log secrets.
- All client methods are async and should run via `asyncio.run(main())`.
- If import fails, install dependency with `uv add nutrient-dws`.
