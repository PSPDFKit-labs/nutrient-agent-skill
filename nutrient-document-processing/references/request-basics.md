# Request Basics

## Pick the product first

- **DWS Processor** (`POST https://api.nutrient.io/build` and typed Processor methods) handles conversion, generation, page operations, OCR, JSON-content extraction, redaction, signing, and output transforms. This package's scripts use `NUTRIENT_API_KEY`.
- **Data Extraction** (`/extraction/parse`) parses documents to markdown or spatial JSON. It is a separate product with separate credentials and credits.
- **Accessibility** provides current PDF/UA auto-tagging and validation workflows. The legacy Processor `/processor/pdfua` endpoint is deprecated for new integrations.

Do not move payloads, keys, or credit estimates between these products.

## Processor transport

Use the pinned typed client rather than constructing authenticated shell commands. The builder automatically registers a local path as a multipart upload and represents an HTTPS URL as a server-side remote input:

```python
local_result = await client.convert("document.docx", "pdf")
remote_result = await client.convert("https://example.invalid/document.docx", "pdf")
```

Create `client` only through `scripts/lib/common.py::create_client(args)` after the per-run confirmation gate. That helper reads the credential from the protected runtime environment without displaying it. Remote URL inputs cause Nutrient to fetch the URL; confirm that transfer just as you would confirm a local upload.

## Typed Python outputs in `nutrient-dws==3.1.0`

The pinned client returns three shapes:

| Result | Key | Typical targets |
| --- | --- | --- |
| `BufferOutput` | `buffer: bytes` | PDF, PDF/A, PDF/UA, Office, image |
| `ContentOutput` | `content: str` | HTML, markdown |
| `JsonContentOutput` | `data` | `json-content` extraction |

Use `scripts/lib/common.py::write_typed_output`; never assume every conversion has a `buffer`.

## Inclusive page ranges

Processor page indexes are zero-based and `start` and `end` are inclusive. `{ "start": 0, "end": 4 }` selects five pages. `-1` addresses the last page.

## Action-time approval

A Processor request transfers the named inputs to Nutrient and consumes credits. Immediately before every request, present:

1. product and exact operation;
2. every file or URL transferred;
3. current estimated credits;
4. output path and whether the step is irreversible.

Wait for approval, then pass `--estimated-credits NUMBER --confirm-external-processing`. A retry or next stage needs fresh approval. Obtain estimates from the account dashboard or current official pricing; this package intentionally does not guess via undocumented credit endpoints.

## Common failures

| Symptom | Check |
| --- | --- |
| `400` or validation error | Payload keys and nesting against current official docs or the pinned typed helper |
| `401` | `NUTRIENT_API_KEY` is present in the protected runtime environment; verify presence only and never print its value |
| `402` | Current product-specific credit balance and estimate |
| `413` | Current documented request limit and input size |
| empty text | Whether the source needs OCR before JSON-content extraction |
| output already exists | Choose a new path; helpers intentionally refuse overwrite |

## Official sources

- [Processor API overview](https://www.nutrient.io/api/processor-api/)
- [Processor documentation](https://www.nutrient.io/api/documentation/)
- [Data Extraction API](https://www.nutrient.io/api/data-extraction-api/)
- [Accessibility API](https://www.nutrient.io/api/accessibility-api/)
