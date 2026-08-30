#!/usr/bin/env python3
"""Validate and render an exact ClawHub release provenance manifest."""

from __future__ import annotations

import argparse
import json
import re
import shlex
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = REPO_ROOT / "docs" / "clawhub-release" / "release-manifest.template.json"
DEFAULT_BASELINE = REPO_ROOT / "docs" / "clawhub-release" / "public-baseline.json"
PACKAGE_PATH = REPO_ROOT / "nutrient-document-processing"
COMMIT_SENTINEL = "__EXACT_GITHUB_SHA__"
REF_SENTINEL = "__EXACT_GITHUB_REF__"
EXPECTED_IGNORE_RULES = (
    ".env",
    "__pycache__/",
    "*.pyc",
    "*.py[cod]",
    "tests/",
    "_meta.json",
)
EXPECTED_TEMPLATE = {
    "schema_version": 1,
    "release": {
        "kind": "clawhub-skill",
        "default_mode": "validate",
        "publisher": "jdrhyne",
        "slug": "nutrient-document-processing",
        "name": "Nutrient Document Processing",
        "version": "2.0.0",
        "changelog": (
            "Correct DWS 3.1.0 contracts, product routing, paid-run consent, "
            "credential handling, and safe outputs."
        ),
        "tags": ["latest"],
        "categories": ["integrations", "automation", "knowledge"],
        "topics": [
            "pdf",
            "document-processing",
            "ocr",
            "redaction",
            "document-conversion",
        ],
    },
    "cli": {
        "package": "clawhub",
        "version": "0.23.3",
        "command": ["clawhub", "skill", "publish"],
    },
    "source": {
        "repository": "PSPDFKit-labs/nutrient-agent-skill",
        "commit": COMMIT_SENTINEL,
        "ref": REF_SENTINEL,
        "path": "nutrient-document-processing",
    },
    "gates": {
        "required_publish_ref": "refs/heads/main",
        "required_environment": "clawhub-production",
        "release_enabled_variable": "CLAWHUB_RELEASE_ENABLED",
        "release_enabled_value": "true",
        "environment_reviewers_configured_externally": True,
        "publish_confirmation": "PUBLISH nutrient-document-processing 2.0.0",
        "expected_commit_must_match": True,
        "dry_run_before_publish": True,
        "slug_migration_enabled": False,
    },
    "prohibited_without_separate_approval": [
        "metered DWS request",
        "ClawHub publish",
        "ClawHub migration",
        "ClawHub rename",
        "ClawHub merge",
        "ClawHub hide",
        "ClawHub delete",
        "ClawHub transfer",
    ],
}
EXPECTED_PUBLIC_BASELINE = {
    "captured_at": "2026-08-29",
    "publisher": "jdrhyne",
    "migration_source": {
        "slug": "nutrient-document-processing-universal",
        "version": "1.1.2",
        "verification": "pass",
        "security": "clean",
        "provenance": "unavailable",
        "signature": "unsigned",
    },
    "canonical_target": {
        "slug": "nutrient-document-processing",
        "version": "2.0.0",
        "repository": "PSPDFKit-labs/nutrient-agent-skill",
        "path": "nutrient-document-processing",
        "commit_binding": "release-manifest-runtime",
    },
    "migration": {
        "enabled": False,
        "source_slug": "nutrient-document-processing-universal",
        "target_slug": "nutrient-document-processing",
    },
    "prohibited_until_final_approval": [
        "metered DWS request",
        "ClawHub publish",
        "ClawHub migration",
        "ClawHub rename",
        "ClawHub merge",
        "ClawHub hide",
        "ClawHub delete",
        "ClawHub transfer",
    ],
}
ALLOWED_CATEGORIES = {
    "integrations",
    "automation",
    "research",
    "development",
    "productivity",
    "communication",
    "creative",
    "knowledge",
    "agents",
    "operations",
    "security",
    "finance",
    "lifestyle",
    "other",
}
RESERVED_TOPICS = {
    "approved",
    "audited",
    "certified",
    "clawhub",
    "community",
    "curated",
    "endorsed",
    "featured",
    "official",
    "officials",
    "openclaw",
    "recommended",
    "staff-pick",
    "trusted",
    "trusted-publisher",
    "verified",
}


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects ambiguous duplicate mapping keys."""


def _construct_unique_mapping(
    loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(f"release workflow contains duplicate YAML key: {key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"release JSON contains duplicate key: {key}")
        result[key] = value
    return result


def _load_unique_json(path: Path) -> dict[str, Any]:
    data = json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=_unique_json_object
    )
    if not isinstance(data, dict):
        raise ValueError("release JSON root must be an object")
    return data


def load_template(path: Path = DEFAULT_TEMPLATE) -> dict[str, Any]:
    data = _load_unique_json(path)
    validate_template(data)
    return data


def load_public_baseline(path: Path = DEFAULT_BASELINE) -> dict[str, Any]:
    return _load_unique_json(path)


def validate_template(data: dict[str, Any]) -> None:
    release = data.get("release", {})
    source = data.get("source", {})
    cli = data.get("cli", {})
    gates = data.get("gates", {})

    if data.get("schema_version") != 1:
        raise ValueError("release manifest schema_version must be 1")
    if release.get("default_mode") != "validate":
        raise ValueError("release manifest must default to validation only")
    if release.get("slug") != source.get("path"):
        raise ValueError("canonical slug and source path must match")
    if source.get("repository") != "PSPDFKit-labs/nutrient-agent-skill":
        raise ValueError("unexpected source repository")
    if source.get("commit") != COMMIT_SENTINEL or source.get("ref") != REF_SENTINEL:
        raise ValueError("source commit/ref must use exact runtime sentinels")
    if cli.get("package") != "clawhub" or not re.fullmatch(
        r"\d+\.\d+\.\d+", str(cli.get("version", ""))
    ):
        raise ValueError("ClawHub CLI package/version must be pinned")
    if cli.get("command") != ["clawhub", "skill", "publish"]:
        raise ValueError("release command must use `clawhub skill publish`")

    categories = release.get("categories", [])
    if not 1 <= len(categories) <= 3 or set(categories) - ALLOWED_CATEGORIES:
        raise ValueError("release categories must be 1-3 current ClawHub slugs")
    topics = release.get("topics", [])
    if not 1 <= len(topics) <= 5:
        raise ValueError("release topics must contain 1-5 entries")
    if any(len(topic) > 48 or topic in RESERVED_TOPICS for topic in topics):
        raise ValueError("release topics contain a reserved or oversized value")

    if gates.get("publish_confirmation") != "PUBLISH nutrient-document-processing 2.0.0":
        raise ValueError("publish confirmation phrase changed unexpectedly")
    if gates.get("required_publish_ref") != "refs/heads/main":
        raise ValueError("publishing must be restricted to main")
    if gates.get("required_environment") != "clawhub-production":
        raise ValueError("publishing must use the named clawhub-production environment")
    if gates.get("release_enabled_variable") != "CLAWHUB_RELEASE_ENABLED":
        raise ValueError("release enablement variable changed unexpectedly")
    if gates.get("release_enabled_value") != "true":
        raise ValueError("release enablement must fail closed unless exactly true")
    if gates.get("environment_reviewers_configured_externally") is not True:
        raise ValueError("external environment reviewer configuration must be documented")
    if not gates.get("expected_commit_must_match") or not gates.get(
        "dry_run_before_publish"
    ):
        raise ValueError("publish commit and dry-run gates are required")
    if gates.get("slug_migration_enabled") is not False:
        raise ValueError("slug migration must remain disabled")
    if data != EXPECTED_TEMPLATE:
        raise ValueError("release manifest immutable snapshot drifted")


def validate_public_baseline(
    baseline: dict[str, Any], template: dict[str, Any]
) -> None:
    if baseline != EXPECTED_PUBLIC_BASELINE:
        raise ValueError("public baseline immutable snapshot drifted")
    expected_top_level = {
        "captured_at",
        "publisher",
        "migration_source",
        "canonical_target",
        "migration",
        "prohibited_until_final_approval",
    }
    if set(baseline) != expected_top_level:
        raise ValueError("public baseline fields must use the canonical migration schema")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(baseline.get("captured_at", ""))):
        raise ValueError("public baseline capture date must use YYYY-MM-DD")
    if baseline.get("publisher") != template["release"]["publisher"]:
        raise ValueError("public baseline publisher drifted from the manifest")

    migration_source = baseline.get("migration_source", {})
    canonical_target = baseline.get("canonical_target", {})
    migration = baseline.get("migration", {})
    release = template["release"]
    source = template["source"]

    if migration_source.get("slug") != "nutrient-document-processing-universal":
        raise ValueError("public baseline must identify only the stale migration source slug")
    if migration_source.get("version") != "1.1.2":
        raise ValueError("public baseline migration source version must remain 1.1.2")
    if canonical_target != {
        "slug": release["slug"],
        "version": release["version"],
        "repository": source["repository"],
        "path": source["path"],
        "commit_binding": "release-manifest-runtime",
    }:
        raise ValueError("public baseline canonical target drifted from the manifest")
    if migration != {
        "enabled": False,
        "source_slug": migration_source["slug"],
        "target_slug": canonical_target["slug"],
    }:
        raise ValueError("ClawHub slug migration must remain explicitly disabled")


def validate_ignore_rules(rules: list[str]) -> None:
    if rules != list(EXPECTED_IGNORE_RULES):
        raise ValueError("release package ignore rules or order drifted")


def validate_package_layout() -> None:
    if not PACKAGE_PATH.is_dir():
        raise ValueError("release package directory is missing")
    if not (PACKAGE_PATH / "SKILL.md").is_file():
        raise ValueError("release package SKILL.md is missing")
    ignore_path = PACKAGE_PATH / ".clawhubignore"
    if not ignore_path.is_file():
        raise ValueError("release package .clawhubignore is missing")
    validate_ignore_rules(ignore_path.read_text(encoding="utf-8").splitlines())


def canonical_publish_tokens(
    manifest: dict[str, Any], *, dry_run: bool
) -> list[str]:
    release = manifest["release"]
    source = manifest["source"]
    tokens = [
        "clawhub",
        "--no-input",
        "skill",
        "publish",
        source["path"],
        "--slug",
        release["slug"],
        "--name",
        release["name"],
        "--owner",
        release["publisher"],
        "--version",
        release["version"],
        "--changelog",
        release["changelog"],
        "--tags",
        ",".join(release["tags"]),
        "--categories",
        ",".join(release["categories"]),
        "--topics",
        ",".join(release["topics"]),
        "--source-repo",
        source["repository"],
        "--source-commit",
        "$GITHUB_SHA",
        "--source-ref",
        "$GITHUB_REF",
        "--source-path",
        source["path"],
    ]
    if dry_run:
        tokens.append("--dry-run")
    tokens.append("--json")
    return tokens


def extract_publish_commands(workflow: str) -> list[list[str]]:
    lines = workflow.splitlines()
    commands: list[list[str]] = []
    line_index = 0
    start_pattern = re.compile(r"^\s*clawhub\s+--no-input\s+skill\s+publish\b")
    while line_index < len(lines):
        line = lines[line_index]
        if not start_pattern.match(line):
            line_index += 1
            continue
        command_lines = [line.strip()]
        while command_lines[-1].rstrip().endswith("\\"):
            line_index += 1
            if line_index >= len(lines):
                raise ValueError("unterminated ClawHub publish command continuation")
            command_lines.append(lines[line_index].strip())
        normalized = " ".join(
            command_line.rstrip().removesuffix("\\").rstrip()
            for command_line in command_lines
        )
        commands.append(shlex.split(normalized))
        line_index += 1
    return commands


def validate_clawhub_invocation_allowlist(
    workflow: str, manifest: dict[str, Any]
) -> None:
    """Require the complete reviewed job/step/run surface, not command-name search."""
    try:
        document = yaml.load(workflow, Loader=UniqueKeyLoader)
    except (yaml.YAMLError, ValueError) as exc:
        raise ValueError(f"release workflow is not valid YAML: {exc}") from exc
    if not isinstance(document, dict) or not isinstance(document.get("jobs"), dict):
        raise ValueError("release workflow must define a jobs mapping")
    version = manifest["cli"]["version"]
    expected_document_controls = {
        "name": "ClawHub release provenance",
        True: {
            "workflow_dispatch": {
                "inputs": {
                    "mode": {
                        "description": (
                            "Validate only, preview with ClawHub dry-run, or publish "
                            "after all gates"
                        ),
                        "required": True,
                        "default": "validate",
                        "type": "choice",
                        "options": ["validate", "dry-run", "publish"],
                    },
                    "expected_source_commit": {
                        "description": (
                            "Full 40-character commit expected to be published "
                            "(required for publish)"
                        ),
                        "required": False,
                        "type": "string",
                    },
                    "publish_confirmation": {
                        "description": (
                            "Exact confirmation phrase recorded in the release manifest "
                            "(required for publish)"
                        ),
                        "required": False,
                        "type": "string",
                    },
                }
            }
        },
        "permissions": {"contents": "read"},
        "concurrency": {
            "group": "clawhub-nutrient-document-processing",
            "cancel-in-progress": False,
        },
    }
    actual_document_controls = {
        key: value for key, value in document.items() if key != "jobs"
    }
    if actual_document_controls != expected_document_controls:
        raise ValueError("release workflow trigger/permission controls drifted")

    expected_job_controls = {
        "validate-and-preview": {
            "runs-on": "ubuntu-latest",
            "timeout-minutes": 15,
        },
        "publish": {
            "if": "inputs.mode == 'publish'",
            "needs": "validate-and-preview",
            "runs-on": "ubuntu-latest",
            "timeout-minutes": 15,
            "environment": "clawhub-production",
        },
    }
    expected_steps = {
        "validate-and-preview": [
            ("Check out the exact workflow commit", "actions/checkout@v4"),
            ("Set up Python", "actions/setup-python@v5"),
            ("Set up Node.js", "actions/setup-node@v4"),
            ("Install pinned validation tools", "run"),
            ("Verify source and CLI provenance", "run"),
            ("Run complete offline validation", "run"),
            ("Render exact release manifest", "run"),
            ("Upload release provenance", "actions/upload-artifact@v4"),
            ("Preview canonical skill publication", "run"),
        ],
        "publish": [
            ("Check out the exact workflow commit", "actions/checkout@v4"),
            ("Set up Node.js", "actions/setup-node@v4"),
            ("Install pinned ClawHub CLI", "run"),
            ("Enforce human publication gates", "run"),
            ("Create owner-only ClawHub auth config", "run"),
            ("Verify ClawHub authentication", "run"),
            ("Publish exact canonical skill", "run"),
            ("Remove temporary ClawHub auth config", "run"),
        ],
    }
    if set(document["jobs"]) != set(expected_steps):
        raise ValueError("release workflow job surface drifted")

    run_steps: dict[tuple[str, str], str] = {}
    step_metadata: dict[tuple[str, str], dict[str, Any]] = {}
    for job_name, expected in expected_steps.items():
        job = document["jobs"][job_name]
        if not isinstance(job, dict) or not isinstance(job.get("steps"), list):
            raise ValueError("release workflow jobs must contain a steps list")
        actual_job_controls = {key: value for key, value in job.items() if key != "steps"}
        if actual_job_controls != expected_job_controls[job_name]:
            raise ValueError(f"release workflow {job_name} job controls drifted")
        actual: list[tuple[str, str]] = []
        for step in job["steps"]:
            if not isinstance(step, dict) or not isinstance(step.get("name"), str):
                raise ValueError("every release workflow step must have an exact name")
            name = step["name"]
            key = (job_name, name)
            if key in step_metadata:
                raise ValueError("release workflow contains duplicate step names")
            step_metadata[key] = {
                metadata_key: metadata_value
                for metadata_key, metadata_value in step.items()
                if metadata_key != "run"
            }
            if "run" in step:
                if "uses" in step or not isinstance(step["run"], str):
                    raise ValueError("release workflow run step shape drifted")
                kind = "run"
                if key in run_steps:
                    raise ValueError("release workflow contains duplicate run step names")
                run_steps[key] = step["run"]
            elif isinstance(step.get("uses"), str):
                kind = step["uses"]
            else:
                raise ValueError("release workflow step must use an allowlisted action or run")
            actual.append((name, kind))
        if actual != expected:
            raise ValueError(f"release workflow {job_name} step surface drifted")

    checkout_metadata = {
        "name": "Check out the exact workflow commit",
        "uses": "actions/checkout@v4",
        "with": {
            "ref": "${{ github.sha }}",
            "fetch-depth": 0,
            "persist-credentials": False,
        },
    }
    node_metadata = {
        "name": "Set up Node.js",
        "uses": "actions/setup-node@v4",
        "with": {"node-version": "22"},
    }
    config_env = {
        "CLAWHUB_CONFIG_PATH": "${{ runner.temp }}/clawhub/config.json"
    }
    expected_step_metadata = {
        ("validate-and-preview", "Check out the exact workflow commit"): checkout_metadata,
        ("validate-and-preview", "Set up Python"): {
            "name": "Set up Python",
            "uses": "actions/setup-python@v5",
            "with": {"python-version": "3.12"},
        },
        ("validate-and-preview", "Set up Node.js"): node_metadata,
        ("validate-and-preview", "Install pinned validation tools"): {
            "name": "Install pinned validation tools"
        },
        ("validate-and-preview", "Verify source and CLI provenance"): {
            "name": "Verify source and CLI provenance",
            "env": {
                "EXPECTED_REPOSITORY": "PSPDFKit-labs/nutrient-agent-skill",
                "EXPECTED_CLAWHUB_VERSION": version,
            },
        },
        ("validate-and-preview", "Run complete offline validation"): {
            "name": "Run complete offline validation"
        },
        ("validate-and-preview", "Render exact release manifest"): {
            "name": "Render exact release manifest"
        },
        ("validate-and-preview", "Upload release provenance"): {
            "name": "Upload release provenance",
            "uses": "actions/upload-artifact@v4",
            "with": {
                "name": "clawhub-release-provenance-${{ github.sha }}",
                "path": "${{ runner.temp }}/clawhub-release-manifest.json",
                "if-no-files-found": "error",
            },
        },
        ("validate-and-preview", "Preview canonical skill publication"): {
            "name": "Preview canonical skill publication",
            "if": "inputs.mode == 'dry-run' || inputs.mode == 'publish'",
        },
        ("publish", "Check out the exact workflow commit"): checkout_metadata,
        ("publish", "Set up Node.js"): node_metadata,
        ("publish", "Install pinned ClawHub CLI"): {
            "name": "Install pinned ClawHub CLI"
        },
        ("publish", "Enforce human publication gates"): {
            "name": "Enforce human publication gates",
            "env": {
                "EXPECTED_SOURCE_COMMIT": "${{ inputs.expected_source_commit }}",
                "PUBLISH_CONFIRMATION": "${{ inputs.publish_confirmation }}",
                "REQUIRED_CONFIRMATION": (
                    "PUBLISH nutrient-document-processing 2.0.0"
                ),
                "CLAWHUB_RELEASE_ENABLED": "${{ vars.CLAWHUB_RELEASE_ENABLED }}",
            },
        },
        ("publish", "Create owner-only ClawHub auth config"): {
            "name": "Create owner-only ClawHub auth config",
            "env": {
                "CLAWHUB_PUBLISH_TOKEN": "${{ secrets.CLAWHUB_TOKEN }}",
                **config_env,
            },
        },
        ("publish", "Verify ClawHub authentication"): {
            "name": "Verify ClawHub authentication",
            "env": config_env,
        },
        ("publish", "Publish exact canonical skill"): {
            "name": "Publish exact canonical skill",
            "env": config_env,
        },
        ("publish", "Remove temporary ClawHub auth config"): {
            "name": "Remove temporary ClawHub auth config",
            "if": "always()",
            "env": config_env,
        },
    }
    if step_metadata != expected_step_metadata:
        raise ValueError("release workflow action/run metadata drifted")

    expected_runs = {
        ("validate-and-preview", "Install pinned validation tools"): (
            "python -m pip install --disable-pip-version-check pyyaml\n"
            f"npm install --global clawhub@{version}\n"
        ),
        ("validate-and-preview", "Verify source and CLI provenance"): (
            "set -euo pipefail\n"
            'test "$GITHUB_REPOSITORY" = "$EXPECTED_REPOSITORY"\n'
            'test "$(clawhub --cli-version)" = "$EXPECTED_CLAWHUB_VERSION"\n'
        ),
        ("validate-and-preview", "Run complete offline validation"): (
            "set -euo pipefail\n"
            "python tools/validate-repo.py\n"
            "python tools/quick_validate.py nutrient-document-processing\n"
            "python -m unittest discover -s tests -v\n"
            "python -m unittest discover -s tools -p 'test_*.py' -v\n"
            "python -m py_compile nutrient-document-processing/scripts/*.py "
            "nutrient-document-processing/scripts/lib/common.py "
            "nutrient-document-processing/assets/templates/custom-workflow-template.py "
            "tools/*.py\n"
        ),
        ("validate-and-preview", "Render exact release manifest"): (
            "python tools/release_manifest.py \\\n"
            '  --commit "$GITHUB_SHA" \\\n'
            '  --ref "$GITHUB_REF" \\\n'
            '  --output "$RUNNER_TEMP/clawhub-release-manifest.json"\n'
        ),
        ("publish", "Install pinned ClawHub CLI"): (
            f"npm install --global clawhub@{version}"
        ),
        ("publish", "Enforce human publication gates"): (
            "set -euo pipefail\n"
            'test "$GITHUB_REPOSITORY" = "PSPDFKit-labs/nutrient-agent-skill"\n'
            'test "$GITHUB_REF" = "refs/heads/main"\n'
            'test "$EXPECTED_SOURCE_COMMIT" = "$GITHUB_SHA"\n'
            'test "$PUBLISH_CONFIRMATION" = "$REQUIRED_CONFIRMATION"\n'
            'test "$CLAWHUB_RELEASE_ENABLED" = "true"\n'
            f'test "$(clawhub --cli-version)" = "{version}"\n'
        ),
        ("publish", "Create owner-only ClawHub auth config"): (
            "set -euo pipefail\n"
            'test -n "$CLAWHUB_PUBLISH_TOKEN"\n'
            "umask 077\n"
            'mkdir -p "$(dirname "$CLAWHUB_CONFIG_PATH")"\n'
            'chmod 700 "$(dirname "$CLAWHUB_CONFIG_PATH")"\n'
            "node -e '\n"
            '  const fs = require("node:fs");\n'
            "  const token = process.env.CLAWHUB_PUBLISH_TOKEN;\n"
            "  const configPath = process.env.CLAWHUB_CONFIG_PATH;\n"
            "  if (!token || !configPath) process.exit(1);\n"
            "  fs.writeFileSync(\n"
            "    configPath,\n"
            '    `${JSON.stringify({ registry: "https://clawhub.ai", token }, null, 2)}\\n`,\n'
            '    { encoding: "utf8", mode: 0o600, flag: "wx" },\n'
            "  );\n"
            "  fs.chmodSync(configPath, 0o600);\n"
            "'\n"
            'test "$(stat -c \'%a\' "$CLAWHUB_CONFIG_PATH")" = "600"\n'
        ),
        ("publish", "Verify ClawHub authentication"): "clawhub --no-input whoami",
        ("publish", "Remove temporary ClawHub auth config"): (
            "set -euo pipefail\n"
            'rm -f -- "$CLAWHUB_CONFIG_PATH"\n'
            'rmdir -- "$(dirname "$CLAWHUB_CONFIG_PATH")" 2>/dev/null || true\n'
        ),
    }
    for key, expected in expected_runs.items():
        if run_steps.get(key) != expected:
            raise ValueError(f"release workflow run body drifted: {key[1]}")

    expected_run_keys = set(expected_runs) | {
        ("validate-and-preview", "Preview canonical skill publication"),
        ("publish", "Publish exact canonical skill"),
    }
    if set(run_steps) != expected_run_keys:
        raise ValueError("release workflow run-step surface drifted")


def validate_workflow_publish_contract(
    workflow: str, manifest: dict[str, Any]
) -> None:
    forbidden = {
        "stale universal slug": r"nutrient-document-processing-universal",
        "owner migration": r"--migrate-owner\b",
        "skill rename/merge": r"\bclawhub\b[^\n]*\bskill\s+(?:rename|merge)\b",
        "hide/delete": r"\bclawhub\b[^\n]*\b(?:hide|delete)\b",
        "token in process arguments": (
            r"(?im)^\s*(?:run:\s*)?clawhub\b[^\n]*"
            r"\b(?:login\b[^\n]*--token|token\b)"
        ),
        "legacy token environment": r"(?m)^\s*CLAWHUB_TOKEN\s*:",
        "secret value printing": (
            r"(?im)^\s*(?:echo|printf)\b[^\n]*(?:CLAWHUB_PUBLISH_TOKEN|CLAWHUB_TOKEN)"
            r"|\bconsole\.log\s*\([^\n]*\btoken\b"
        ),
        "raw authorization header": r"(?i)authorization\s*:\s*bearer",
        "authenticated curl": r"(?im)^\s*curl\b[^\n]*(?:authorization|token)",
    }
    for label, pattern in forbidden.items():
        if re.search(pattern, workflow, flags=re.IGNORECASE):
            raise ValueError(f"release workflow contains forbidden {label}")

    validate_clawhub_invocation_allowlist(workflow, manifest)

    commands = extract_publish_commands(workflow)
    if len(commands) != 2:
        raise ValueError("release workflow must contain exactly preview and publish commands")
    preview_commands = [command for command in commands if "--dry-run" in command]
    publish_commands = [command for command in commands if "--dry-run" not in command]
    if len(preview_commands) != 1 or len(publish_commands) != 1:
        raise ValueError("dry-run must appear only on the single preview command")
    if preview_commands[0] != canonical_publish_tokens(manifest, dry_run=True):
        raise ValueError("preview publish command differs from the canonical manifest arguments")
    if publish_commands[0] != canonical_publish_tokens(manifest, dry_run=False):
        raise ValueError("actual publish command differs from the canonical manifest arguments")


def _replace_runtime_values(value: Any, commit: str, ref: str) -> Any:
    if isinstance(value, dict):
        return {
            key: _replace_runtime_values(item, commit, ref)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_replace_runtime_values(item, commit, ref) for item in value]
    if value == COMMIT_SENTINEL:
        return commit
    if value == REF_SENTINEL:
        return ref
    return value


def render_manifest(template: dict[str, Any], commit: str, ref: str) -> dict[str, Any]:
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("source commit must be a full lowercase 40-character SHA")
    if not ref.startswith("refs/") or any(character.isspace() for character in ref):
        raise ValueError("source ref must be an exact refs/... value without whitespace")
    rendered = _replace_runtime_values(template, commit, ref)
    serialized = json.dumps(rendered, sort_keys=True)
    if COMMIT_SENTINEL in serialized or REF_SENTINEL in serialized:
        raise ValueError("runtime provenance sentinels were not fully replaced")
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    rendered = render_manifest(load_template(args.template), args.commit, args.ref)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rendered, indent=2) + "\n", encoding="utf-8")
    print(f"Rendered exact release manifest: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
