# Generation and Conversion

Use DWS Processor for document generation and conversion. Obtain an estimate and approval before invoking any example.

## HTML to PDF

Use the custom workflow template with the pinned typed builder. It registers the HTML upload and keeps layout options on the HTML part:

```python
result = await (
    client.workflow()
    .add_html_part(
        "index.html",
        options={"layout": {"orientation": "landscape", "size": "A4"}},
    )
    .output_pdf()
    .execute()
)
write_workflow_output(result, "result.pdf")
```

Create `client` with the template's confirmation-gated helper. Route asset registration through `add_html_part(..., assets=...)` rather than guessing multipart handles.

## Remote input

The pinned builder accepts a remote URL as a file input. Nutrient fetches that URL server-side:

```python
result = await client.convert("https://example.invalid/document.docx", "pdf")
```

Confirm the URL transfer and only allow expected HTTPS sources. Do not fetch arbitrary user-controlled URLs inside a privileged local network.

## Typed conversion

Use `scripts/convert.py`. `client.convert(input, target)` maps the current target correctly and may return:

- `buffer` for PDF, PDF/A, PDF/UA, Office, or image output;
- `content` for HTML or markdown;
- `data` for JSON-content when using a suitable workflow.

The helper handles all three shapes safely. This is preferred to hard-coding an Office or image output payload whose wire contract may evolve.

Example shape after the user approves the exact estimate and transfer:

```bash
uv run scripts/convert.py \
  --input document.pdf \
  --format markdown \
  --out document.md \
  --estimated-credits APPROVED_NUMBER \
  --confirm-external-processing
```

## Rules

- Generate from HTML when you control source markup and need reproducible layout.
- Use the typed helper for Office and image targets rather than inferring `output.type` fields.
- Page selections are inclusive.
- Choose a new output path; helpers refuse overwrite.
- High-fidelity markdown/spatial parsing is a Data Extraction job, not the same as Processor conversion to markdown.

## Official sources

- [PDF converter API](https://www.nutrient.io/api/pdf-converter-api/)
- [URL to PDF API](https://www.nutrient.io/api/url-to-pdf-api/)
- [Processor API overview](https://www.nutrient.io/api/processor-api/)
