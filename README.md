# Nutrient Document Processing — Agent Skill

<p align="center">
  <a href="https://www.nutrient.io/api/"><img src="https://img.shields.io/badge/Nutrient-DWS%20API-blue" alt="Nutrient DWS API"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-green" alt="License"></a>
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/Agent%20Skills-compatible-purple" alt="Agent Skills"></a>
</p>

Single-skill repository for document processing with the Nutrient DWS Python client.

## Quickstart

1. Get an API key: <https://dashboard.nutrient.io/sign_up/?product=processor>
2. Install the skill:

```bash
npx skills add PSPDFKit-labs/nutrient-agent-skill
```

3. Export API key:

```bash
export NUTRIENT_API_KEY="nutr_sk_..."
```

4. Ask your agent: `Extract text from invoice.pdf`

## Requirements

- Python 3.10+
- `uv` installed: <https://docs.astral.sh/uv/>
- Nutrient API key

## Installation

### Preferred: `npx skills`

```bash
# Install to all detected agents
npx skills add PSPDFKit-labs/nutrient-agent-skill

# Install to selected agents
npx skills add PSPDFKit-labs/nutrient-agent-skill -a claude-code -a codex -a cursor

# Global install
npx skills add PSPDFKit-labs/nutrient-agent-skill -g
```

### Local repository path

```bash
git clone https://github.com/PSPDFKit-labs/nutrient-agent-skill.git
cd nutrient-agent-skill
npx skills add .
```

### Manual install

Copy this repository as one skill directory named `nutrient-document-processing`:

- Project scope: `.agents/skills/nutrient-document-processing/`
- Global scope: `~/.config/agents/skills/nutrient-document-processing/`

## Script Model

- `scripts/*.py` are single-operation scripts only.
- Multi-step workflows must be generated at runtime in a temporary script from `assets/templates/custom-workflow-template.py`.
- Do not commit runtime pipeline scripts.

## Structure

```text
SKILL.md
scripts/
  *.py
  lib/common.py
assets/
  templates/custom-workflow-template.py
tests/
  testing-guide.md
agents/
  openai.yaml
```

## Documentation

- [SKILL.md](SKILL.md)
- [Testing Guide](tests/testing-guide.md)
- [Custom Workflow Template](assets/templates/custom-workflow-template.py)
- [API Playground](https://dashboard.nutrient.io/processor-api/playground/)
- [Official API Docs](https://www.nutrient.io/guides/dws-processor/)

## License

[Apache-2.0](LICENSE)
