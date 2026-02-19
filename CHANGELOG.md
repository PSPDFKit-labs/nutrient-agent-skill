# Changelog

## 2.0.0

Migration from curl-based skill to Python script-based plugin architecture.

**Breaking:**
- Directory restructure: `nutrient-document-processing/` replaced by `plugins/nutrient-document-processor-api/`
- API key environment variable is `NUTRIENT_API_KEY`

**New:**
- 19 ready-to-run Python scripts replacing the curl-based approach
- Claude Code marketplace support (`.claude-plugin/marketplace.json`)
- OpenAI Codex CLI support (`agents/openai.yaml` + symlink installation)
- Custom workflow template for multi-step document pipelines
- Script catalog and custom pipeline guidelines in `references/`

**Requirements:**
- Python 3.10+ with [uv](https://docs.astral.sh/uv/)

## nutrient-document-processor-api 1.0.0

Initial release of the Nutrient DWS Processor API plugin.

**New:**
- 19 ready-to-run Python scripts for document conversion, extraction, transformation, and security operations
- Custom workflow template for multi-step document pipelines
- Support for Claude Code (via marketplace), OpenAI Codex, and manual agent installation
