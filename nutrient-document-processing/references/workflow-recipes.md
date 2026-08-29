# Workflow Recipes

Each numbered step that invokes DWS is a distinct external transfer and paid request unless combined into one reviewed custom Processor workflow. Present the exact operation, inputs, product, and estimate and obtain action-time approval for every request.

## Scan to searchable text

1. Inspect locally to confirm the PDF lacks a usable text layer.
2. Processor OCR.
3. Processor JSON-content extraction, or Data Extraction parsing when the requested output is high-fidelity markdown/spatial JSON.

Do not treat Processor and Data Extraction as the same key or credit pool.

## Scan to redacted delivery PDF

1. Processor OCR if required.
2. Stage deterministic or AI redaction annotations.
3. Render and visually review matches and misses.
4. Obtain separate approval for irreversible application.
5. Apply redactions.
6. Render and search/extract the final PDF to verify removal.
7. Optionally optimize, then sign last.

## HTML report to archival PDF

1. Generate with a typed HTML part and explicit layout options.
2. Emit PDF/A with the pinned Processor builder.
3. Validate with the required archival checker.

## Accessible output

1. Start from the cleanest structured source.
2. For a Processor output transform, use `/build` PDF/UA through the typed helper.
3. For current auto-tagging and PDF/UA validation workflows, route to the separate Accessibility product.
4. Validate; never claim compliance from code existence or a successful HTTP response alone.

## Form packet to signed output

1. Apply Instant JSON or XFDF using the pinned builder.
2. Flatten only if editability is no longer needed.
3. Complete all redaction, assembly, and optimization.
4. Confirm explicit CMS/CAdES configuration and sign last.
5. Independently validate the embedded signature and trust chain.

## Packet assembly and web delivery

1. Merge/reorder parts.
2. Select inclusive page ranges and fix rotation.
3. Apply final content changes.
4. Optimize/linearize for delivery.
5. Sign last if required.

All helpers refuse to overwrite existing outputs, so every intermediate and retry must have a deliberate new path.
