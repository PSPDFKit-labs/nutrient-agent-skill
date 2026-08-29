# Extraction and OCR

## Route the requested output

- Use **Processor JSON-content extraction** for page-level plain text, tables, key-value pairs, and structured text inside a Processor workflow.
- Use the separate **Data Extraction API** for high-fidelity markdown or spatial JSON parsing. It has a separate endpoint, credential, and credit pool; do not emulate it with a Processor `actions` payload.

## Processor text extraction

The contract used by `client.extract_text()` is:

```json
{
  "parts": [{"file": "document"}],
  "output": {
    "type": "json-content",
    "plainText": true,
    "tables": false
  }
}
```

Use `scripts/extract-text.py`. It writes the `data` object as JSON and can separately write page `plainText` values.

## Processor table extraction

The contract used by `client.extract_table()` is:

```json
{
  "parts": [{"file": "document"}],
  "output": {
    "type": "json-content",
    "plainText": false,
    "tables": true
  }
}
```

Use `scripts/extract-table.py`; there is no `extraction` build action and no promise that the result is XLSX.

## Processor key-value extraction

The contract used by `client.extract_key_value_pairs()` is:

```json
{
  "parts": [{"file": "document"}],
  "output": {
    "type": "json-content",
    "plainText": false,
    "tables": false,
    "keyValuePairs": true
  }
}
```

Use `scripts/extract-key-value-pairs.py`.

## OCR

OCR is a part action in the pinned client:

```json
{
  "parts": [
    {
      "file": "scan",
      "actions": [{"type": "ocr", "language": ["english", "german"]}]
    }
  ],
  "output": {"type": "pdf"}
}
```

Use `scripts/ocr.py` so the 3.1.0 `OcrLanguage` contract controls accepted language values. Do not copy an unverified language list into a raw request.

## Rules

- Extract first from born-digital files; OCR only when text is missing or unusable.
- OCR a scan before Processor extraction or text-matching redaction.
- Page ranges are zero-based and inclusive.
- A second OCR/extraction stage is another paid request and needs a new estimate and approval.

## Official sources

- [Data Extraction API](https://www.nutrient.io/api/data-extraction-api/)
- [Processor API overview](https://www.nutrient.io/api/processor-api/)
