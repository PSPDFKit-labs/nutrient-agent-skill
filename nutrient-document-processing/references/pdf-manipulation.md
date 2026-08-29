# PDF Manipulation

Use the pinned helpers for page operations. They handle remote/local inputs consistently, gate the paid request, and refuse output overwrite.

## Merge

Part order controls merge order:

```json
{
  "parts": [
    {"file": "cover"},
    {"file": "body"},
    {"file": "appendix"}
  ],
  "output": {"type": "pdf"}
}
```

Use `scripts/merge.py` when possible.

## Inclusive page ranges

`pages.start` and `pages.end` are zero-based and inclusive:

```json
{
  "parts": [
    {"file": "document", "pages": {"start": 0, "end": 4}}
  ],
  "output": {"type": "pdf"}
}
```

This produces the first **five** pages. To reorder, reuse the source as multiple parts in the desired order. Use `scripts/split.py` for multiple output files and `scripts/duplicate-pages.py` for exact indexes.

## Rotate

Use `scripts/rotate.py` for full or selective rotation. The pinned typed helper uses `rotateBy` and assembles unselected pages correctly; do not invent a top-level `rotation`/`pages` action.

## Flatten

The current build action is `{ "type": "flatten" }`, nested on the affected part (optionally with `annotationIds`). Flatten only after the user confirms the form or annotations no longer need to remain editable.

## Rules

- Assemble and normalize the whole packet before watermarking, redacting, signing, or final optimization.
- Keep passwords on the affected part when a protected input is used.
- Signing and irreversible redaction apply steps require separate approval after assembly.

## Official sources

- [Processor API overview](https://www.nutrient.io/api/processor-api/)
- [Processor tools and APIs](https://www.nutrient.io/api/documentation/tools-and-api/)
