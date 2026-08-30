#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path

from release_manifest import (
    load_public_baseline,
    load_template,
    validate_package_layout,
    validate_public_baseline,
    validate_workflow_publish_contract,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "nutrient-document-processing"
CONFLICT_MARKERS = ("<" * 7, "=" * 7, ">" * 7)
TEXT_SUFFIXES = {".json", ".md", ".txt", ".py", ".yaml", ".yml", ".svg", ".gitignore"}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def check_required_paths() -> None:
    required = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "CHANGELOG.md",
        SKILL_DIR / "SKILL.md",
        SKILL_DIR / "LICENSE.txt",
        SKILL_DIR / "references" / "REFERENCE.md",
        SKILL_DIR / "scripts" / "lib" / "common.py",
        SKILL_DIR / "tests" / "testing-guide.md",
        REPO_ROOT / "tests" / "test_common_contracts.py",
        REPO_ROOT / "tests" / "test_skill_contracts.py",
        REPO_ROOT / "tools" / "quick_validate.py",
        REPO_ROOT / "tools" / "release_manifest.py",
        REPO_ROOT / "docs" / "clawhub-release" / "release-manifest.template.json",
        REPO_ROOT / "docs" / "clawhub-release" / "public-baseline.json",
        REPO_ROOT / "docs" / "clawhub-release" / "README.md",
        REPO_ROOT / ".github" / "workflows" / "clawhub-release.yml",
    ]
    missing = [str(path.relative_to(REPO_ROOT)) for path in required if not path.exists()]
    if missing:
        fail("Missing required files:\n- " + "\n- ".join(missing))


def iter_text_files() -> list[Path]:
    files: list[Path] = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts:
            continue
        if path.suffix in TEXT_SUFFIXES or path.name in TEXT_SUFFIXES:
            files.append(path)
    return files


def check_conflict_markers() -> None:
    offenders: list[str] = []
    for path in iter_text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if any(marker in text for marker in CONFLICT_MARKERS):
            offenders.append(str(path.relative_to(REPO_ROOT)))
    if offenders:
        fail("Unresolved merge markers found:\n- " + "\n- ".join(sorted(offenders)))


def check_skill_frontmatter() -> None:
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        fail("SKILL.md is missing a frontmatter block.")
    frontmatter = match.group(1)
    for field in ("name:", "description:", "license:"):
        if field not in frontmatter:
            fail(f"SKILL.md frontmatter is missing `{field[:-1]}`.")
    if not re.search(r"(?m)^license:\s*MIT-0\s*$", frontmatter):
        fail("SKILL.md must declare the ClawHub MIT-0 package license.")


def check_readme_links() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    if 'href="nutrient-document-processing/LICENSE.txt"' not in readme:
        fail("README.md does not point its license badge at nutrient-document-processing/LICENSE.txt.")
    if "[MIT-0](nutrient-document-processing/LICENSE.txt)" not in readme:
        fail("README.md does not point its license section at nutrient-document-processing/LICENSE.txt.")

    license_text = (SKILL_DIR / "LICENSE.txt").read_text(encoding="utf-8")
    if not license_text.startswith("MIT No Attribution"):
        fail("LICENSE.txt must contain the MIT No Attribution license.")


def check_reference_links() -> None:
    reference_path = SKILL_DIR / "references" / "REFERENCE.md"
    text = reference_path.read_text(encoding="utf-8")
    links = re.findall(r"\(([^)]+)\)", text)
    missing: list[str] = []
    for link in links:
        if "://" in link or link.startswith("#"):
            continue
        target = (reference_path.parent / link).resolve()
        if not target.exists():
            missing.append(link)
    if missing:
        fail("REFERENCE.md contains missing relative links:\n- " + "\n- ".join(sorted(missing)))


def check_published_credential_boundary() -> None:
    files = [REPO_ROOT / "README.md"] + [
        path
        for path in SKILL_DIR.rglob("*")
        if path.is_file() and path.suffix in TEXT_SUFFIXES
    ]
    checks = {
        "raw bearer authorization header": re.compile(
            r"authorization\s*:\s*bearer", re.IGNORECASE
        ),
        "curl command": re.compile(r"^\s*curl\b", re.IGNORECASE | re.MULTILINE),
        "shell-expanded Nutrient API key": re.compile(
            r"\$\{?NUTRIENT_(?:DWS_)?API_KEY\}?"
        ),
    }
    failures: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for label, pattern in checks.items():
            if pattern.search(text):
                failures.append(f"{path.relative_to(REPO_ROOT)}: {label}")
    if failures:
        fail("Published credential boundary violations:\n- " + "\n- ".join(failures))


def check_release_contract() -> None:
    try:
        manifest = load_template()
        baseline = load_public_baseline()
        validate_public_baseline(baseline, manifest)
        validate_package_layout()
    except (OSError, ValueError) as exc:
        fail(f"Invalid ClawHub release provenance: {exc}")

    workflow = (
        REPO_ROOT / ".github" / "workflows" / "clawhub-release.yml"
    ).read_text(encoding="utf-8")
    required_fragments = (
        "default: validate",
        "if: inputs.mode == 'publish'",
        'test "$EXPECTED_SOURCE_COMMIT" = "$GITHUB_SHA"',
        'test "$PUBLISH_CONFIRMATION" = "$REQUIRED_CONFIRMATION"',
        'test "$GITHUB_REF" = "refs/heads/main"',
        'test "$CLAWHUB_RELEASE_ENABLED" = "true"',
        "CLAWHUB_RELEASE_ENABLED: ${{ vars.CLAWHUB_RELEASE_ENABLED }}",
        "CLAWHUB_PUBLISH_TOKEN: ${{ secrets.CLAWHUB_TOKEN }}",
        "CLAWHUB_CONFIG_PATH: ${{ runner.temp }}/clawhub/config.json",
        'JSON.stringify({ registry: "https://clawhub.ai", token }, null, 2)',
        'mode: 0o600, flag: "wx"',
        "run: clawhub --no-input whoami",
        "if: always()",
        'rm -f -- "$CLAWHUB_CONFIG_PATH"',
        "environment: clawhub-production",
        "cancel-in-progress: false",
    )
    missing = [fragment for fragment in required_fragments if fragment not in workflow]
    if missing:
        fail("ClawHub workflow is missing release gates:\n- " + "\n- ".join(missing))

    if f"clawhub@{manifest['cli']['version']}" not in workflow:
        fail("ClawHub workflow does not install the manifest-pinned CLI version.")
    try:
        validate_workflow_publish_contract(workflow, manifest)
    except ValueError as exc:
        fail(f"Invalid ClawHub workflow publish contract: {exc}")

    release_docs = (
        REPO_ROOT / "docs" / "clawhub-release" / "README.md"
    ).read_text(encoding="utf-8")
    documentation_requirements = (
        "required reviewers",
        "Merely naming the environment in workflow YAML does not add reviewer protection",
        "CLAWHUB_RELEASE_ENABLED",
        "exactly `true`",
    )
    undocumented = [
        requirement
        for requirement in documentation_requirements
        if requirement not in release_docs
    ]
    if undocumented:
        fail("ClawHub release safeguards are not fully documented:\n- " + "\n- ".join(undocumented))

    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if "## [2.0.0] - Unreleased" not in changelog or "canonical ClawHub package" not in changelog:
        fail("CHANGELOG.md is missing the unreleased 2.0.0 canonical package contract.")


def main() -> None:
    check_required_paths()
    check_conflict_markers()
    check_skill_frontmatter()
    check_readme_links()
    check_reference_links()
    check_published_credential_boundary()
    check_release_contract()
    print("Repository validation passed.")


if __name__ == "__main__":
    main()
