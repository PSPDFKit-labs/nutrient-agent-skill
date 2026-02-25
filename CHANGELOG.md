# Changelog

## 2.1.0

Refined Python skill architecture to enforce single-operation committed scripts and flat skill layout.

**Breaking:**
- Flattened repository layout to a single top-level skill (`SKILL.md` at repo root).
- Removed Claude marketplace plugin scaffolding (`.claude-plugin/`, `plugins/...`).
- Removed committed multi-operation pipeline scripts from `scripts/`.

**New/Changed:**
- `npx skills add` is now the primary installation path for all agents.
- Multi-step workflows are generated at runtime in temporary scripts from `assets/templates/custom-workflow-template.py`.
- Updated README, skill instructions, and testing guide to reflect the runtime-pipeline model.

**Requirements:**
- Python 3.10+ with [uv](https://docs.astral.sh/uv/)
- `NUTRIENT_API_KEY`

## 2.0.0

Migration from curl-based skill to Python script-based plugin architecture.
