# Nutrient Document Processing — Agent Skill

<p align="center">
  <a href="https://www.nutrient.io/api/"><img src="https://img.shields.io/badge/Nutrient-DWS%20API-blue" alt="Nutrient DWS API"></a>
  <a href="https://www.npmjs.com/package/@nutrient-sdk/dws-mcp-server"><img src="https://img.shields.io/npm/v/@nutrient-sdk/dws-mcp-server" alt="npm version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-green" alt="License"></a>
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/Agent%20Skills-compatible-purple" alt="Agent Skills"></a>
</p>

A universal [Agent Skill](https://agentskills.io) for document processing powered by the [Nutrient DWS Processor API](https://www.nutrient.io/api/). Works with **40+ AI coding agents** including Claude Code, Codex CLI, Gemini CLI, Cursor, GitHub Copilot, Windsurf, OpenCode, and more.

## Features

| Capability | Description |
|------------|-------------|
| 📄 **Document Conversion** | PDF ↔ DOCX/XLSX/PPTX, HTML → PDF, images → PDF |
| 📝 **Text Extraction** | Extract text, tables, and key-value pairs from PDFs |
| 🔍 **OCR** | Multi-language optical character recognition for scanned documents |
| 🔒 **Redaction** | Pattern-based (SSN, email, credit card) + AI-powered PII detection |
| 💧 **Watermarks** | Text or image watermarks with full styling control |
| ✍️ **Digital Signatures** | CMS and CAdES (PAdES-compliant) digital signatures |
| 📋 **Form Filling** | Fill PDF form fields programmatically |
| 📊 **Credit Tracking** | Monitor API usage and credit balance |

## Quick Start

### Get an API Key

Sign up free at **<https://dashboard.nutrient.io/sign_up/?product=processor>**

### Install the Skill

#### Using `npx skills` (Recommended — works with 40+ agents)

```bash
# Install to all detected agents
npx skills add PSPDFKit-labs/nutrient-agent-skill

# Install to specific agents
npx skills add PSPDFKit-labs/nutrient-agent-skill -a claude-code -a codex -a cursor

# Install globally (available across all projects)
npx skills add PSPDFKit-labs/nutrient-agent-skill -g
```

#### Manual Installation

Copy the `nutrient-document-processing/` folder to your agent's skills directory:

| Agent | Project Path | Global Path |
|-------|-------------|-------------|
| **Claude Code** | `.claude/skills/` | `~/.claude/skills/` |
| **Codex CLI** | `.codex/skills/` | `~/.codex/skills/` |
| **Gemini CLI** | `.gemini/skills/` | `~/.gemini/skills/` |
| **Cursor** | `.cursor/skills/` | `~/.cursor/skills/` |
| **GitHub Copilot** | `.github/skills/` | `~/.copilot/skills/` |
| **OpenCode** | `.opencode/skills/` | `~/.config/opencode/skills/` |
| **Windsurf** | `.windsurf/skills/` | `~/.codeium/windsurf/skills/` |
| **Amp** | `.agents/skills/` | `~/.config/agents/skills/` |
| **OpenClaw** | `skills/` | `~/.moltbot/skills/` |
| **Roo Code** | `.roo/skills/` | `~/.roo/skills/` |

Example for Claude Code:

```bash
git clone https://github.com/PSPDFKit-labs/nutrient-agent-skill.git
cp -r nutrient-agent-skill/nutrient-document-processing ~/.claude/skills/
```

## Alternative Integrations

### MCP Server (Best for agents with MCP support)

The **Nutrient DWS MCP Server** provides all operations as native agent tools with file I/O handling and sandboxing.

```bash
npx @nutrient-sdk/dws-mcp-server
```

Add to your MCP config (e.g., `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "nutrient-dws": {
      "command": "npx",
      "args": ["-y", "@nutrient-sdk/dws-mcp-server"],
      "env": {
        "NUTRIENT_DWS_API_KEY": "YOUR_API_KEY",
        "SANDBOX_PATH": "/path/to/working/directory"
      }
    }
  }
}
```

📦 [npm](https://www.npmjs.com/package/@nutrient-sdk/dws-mcp-server) · [GitHub](https://github.com/PSPDFKit/nutrient-dws-mcp-server)

### OpenClaw Plugin

For [OpenClaw](https://openclaw.com) users:

```bash
openclaw plugins install @nutrient-sdk/nutrient-openclaw
```

📦 [npm](https://www.npmjs.com/package/@nutrient-sdk/nutrient-openclaw)

## Usage

Once installed, simply mention document processing tasks in your agent:

- *"Convert report.docx to PDF"*
- *"Extract all tables from financial-statement.pdf"*
- *"Redact all PII from patient-records.pdf"*
- *"OCR this scanned document in German"*
- *"Add a CONFIDENTIAL watermark to draft.pdf"*
- *"Digitally sign contract.pdf"*
- *"Merge invoice1.pdf and invoice2.pdf"*

The agent will automatically activate the skill based on the task.

## Skill Structure

```
nutrient-document-processing/
├── SKILL.md              # Main instructions (loaded by agents)
├── references/
│   └── REFERENCE.md      # Full API reference (loaded on demand)
├── LICENSE               # Apache-2.0
└── README.md             # This file
```

## Documentation

- **[SKILL.md](nutrient-document-processing/SKILL.md)** — Agent instructions with setup and operation examples
- **[REFERENCE.md](nutrient-document-processing/references/REFERENCE.md)** — Complete API reference with all endpoints, parameters, and error codes
- **[API Playground](https://dashboard.nutrient.io/processor-api/playground/)** — Interactive API testing
- **[Official API Docs](https://www.nutrient.io/guides/dws-processor/)** — Nutrient documentation

## About

Built by [Nutrient](https://www.nutrient.io/) (formerly PSPDFKit), the company behind document SDKs used by thousands of companies worldwide.

## License

[Apache-2.0](nutrient-document-processing/LICENSE)
