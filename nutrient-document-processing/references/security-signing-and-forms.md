# Security, Signing, and Forms

## Redaction is staged

Creating redaction annotations does not remove content. The current deterministic preset action is:

```json
{
  "parts": [
    {
      "file": "document",
      "actions": [
        {
          "type": "createRedactions",
          "strategy": "preset",
          "strategyOptions": {"preset": "email-address"}
        }
      ]
    }
  ],
  "output": {"type": "pdf"}
}
```

Regex uses the same action with `strategy: "regex"` and `strategyOptions.regex`. The pinned `BuildActions.create_redactions_preset()` and `create_redactions_regex()` helpers are the source of truth for optional settings.

For contextual matching, `scripts/redact-ai.py` calls the separate AI-redaction route through the typed client, accepts only a local PDF, and always requests `stage`. It never offers an immediate apply mode.

After staging:

1. render and visually review every page;
2. check false positives and missed sensitive values;
3. present a new credit estimate and irreversible-action warning;
4. obtain fresh approval;
5. apply with `client.apply_redactions(staged_pdf)` or `BuildActions.apply_redactions()`;
6. render again and search/extract to verify sensitive content is gone.

Never describe a staged artifact as redacted.

## Watermark

The text action uses `text` directly. Dimensions are objects, not percentage strings:

```json
{
  "type": "watermark",
  "text": "DRAFT",
  "opacity": 0.3,
  "rotation": 45,
  "width": {"value": 50, "unit": "%"},
  "height": {"value": 50, "unit": "%"}
}
```

Use `scripts/watermark-text.py` or the pinned builder. Image watermarks use `image` and should be registered by `BuildActions.watermark_image()`; do not invent `watermarkType` or `imagePath`.

## Signing

Signing is a separate `/sign` operation exposed as `client.sign()`; it is not a `/build` `sign` action. The primary PDF must be local.

`scripts/sign.py` requires a JSON configuration file. Minimal examples:

```json
{"signatureType": "cms", "flatten": false}
```

```json
{"signatureType": "cades", "cadesLevel": "b-lt", "flatten": false}
```

Do not rely on an implicit default signature. Confirm CMS versus CAdES, CAdES level, field/position, appearance, and any signing images before the run. After writing the PDF, the helper verifies the PDF container; independently validate that the expected signature is embedded and that its trust chain and timestamp meet the user's requirements.

## Form data

The current Processor build actions are `applyInstantJson` and `applyXfdf`, with the data file registered by the typed builder. There is no `fillForm` action. Use `BuildActions.apply_instant_json(file)` or `BuildActions.apply_xfdf(file, options)` in the custom workflow template and use real PDF field names.

## Password protection

Use `scripts/password-protect.py`. It reads user and owner passwords from separate owner-only local files, not command arguments:

```bash
chmod 600 /protected/path/user-password /protected/path/owner-password
uv run scripts/password-protect.py \
  --input document.pdf \
  --user-password-file /protected/path/user-password \
  --owner-password-file /protected/path/owner-password \
  --out protected.pdf \
  --estimated-credits APPROVED_NUMBER \
  --confirm-external-processing
```

Delete temporary secret files with the user's approval and normal secure-storage workflow. Do not print their contents.

## Ordering

Fill, redact, flatten, assemble, and optimize before signing. Treat an applied redaction and a signature as final-artifact operations, each with independent approval and verification.

## Official sources

- [Processor tools and APIs](https://www.nutrient.io/api/documentation/tools-and-api/)
- [Processor API overview](https://www.nutrient.io/api/processor-api/)
