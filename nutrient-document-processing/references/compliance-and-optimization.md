# Compliance and Optimization

## Choose Processor output or Accessibility workflow

- Processor can emit PDF/A and PDF/UA through `/build` and the pinned typed client. These are output transforms.
- Nutrient Accessibility is a separate product for current PDF/UA auto-tagging and validation workflows.
- Do not use the deprecated `/processor/pdfua` endpoint for a new integration.

## PDF/A with the typed client

Prefer `client.convert(input, "pdfa")` for the default or `workflow().output_pdfa(options)` when a specific supported conformance and vectorization/rasterization policy is required. Use only conformance values accepted by `nutrient-dws==3.1.0`; do not copy a broader unverified list into a raw payload.

PDF/A conversion can change live text and fonts. Validate the final artifact with the user's required archival validator before claiming conformance.

## PDF/UA Processor output

For a Processor output transform, use `client.convert(input, "pdfua")` or `workflow().output_pdfua(options)`. This maps to `/build` output type `pdfua` through the pinned client.

PDF/UA output is not a substitute for an accessibility validation workflow. Born-digital, well-structured sources generally provide a better starting point than flattened or raster-only content. Route current auto-tagging/validation requirements to the Accessibility product and validate with the user's required checker.

## Optimization

Use `scripts/optimize.py` and provide options via a reviewed JSON file when possible. Current pinned options include settings such as `mrcCompression`, `imageOptimizationQuality`, and `linearize`.

Rules:

- visually compare compression-sensitive pages;
- optimize before signing;
- use linearization for a final web-delivery PDF, not an intermediate;
- choose a new output path rather than overwriting the source;
- obtain a fresh estimate and approval for every separate request.

## Official sources

- [PDF to PDF/A API](https://www.nutrient.io/api/pdf-to-pdfa-api/)
- [PDF/UA auto-tagging API](https://www.nutrient.io/api/pdfua-auto-tagging-api/)
- [Accessibility API](https://www.nutrient.io/api/accessibility-api/)
- [Optimization API](https://www.nutrient.io/api/document-optimization-api/)
