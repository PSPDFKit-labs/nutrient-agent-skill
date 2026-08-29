#!/usr/bin/env python3
"""Minimal Agent Skills frontmatter and scaffold validation."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


MAX_SKILL_NAME_LENGTH = 64
ALLOWED_PROPERTIES = {"name", "description", "license", "allowed-tools", "metadata"}


def validate_skill(skill_path: str | Path) -> tuple[bool, str]:
    skill_md = Path(skill_path) / "SKILL.md"
    if not skill_md.is_file():
        return False, "SKILL.md not found"

    content = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, "Invalid or missing YAML frontmatter"

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return False, f"Invalid YAML in frontmatter: {exc}"
    if not isinstance(frontmatter, dict):
        return False, "Frontmatter must be a YAML dictionary"

    unexpected = set(frontmatter) - ALLOWED_PROPERTIES
    if unexpected:
        return False, f"Unexpected frontmatter keys: {', '.join(sorted(unexpected))}"
    for field in ("name", "description"):
        if field not in frontmatter:
            return False, f"Missing '{field}' in frontmatter"

    name = frontmatter["name"]
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        return False, "Skill name must be lowercase hyphen-case"
    if len(name) > MAX_SKILL_NAME_LENGTH:
        return False, f"Skill name exceeds {MAX_SKILL_NAME_LENGTH} characters"
    if Path(skill_path).name != name:
        return False, "Skill folder name must match frontmatter name"

    description = frontmatter["description"]
    if not isinstance(description, str):
        return False, "Description must be a string"
    if not description.strip() or len(description.strip()) > 1024:
        return False, "Description must contain 1-1024 characters"
    if "<" in description or ">" in description:
        return False, "Description cannot contain angle brackets"

    body = content[match.end() :]
    if re.search(r"(?m)^[ ]{0,3}\[TODO:[^\n]*\][ \t]*$", body):
        return False, "Skill instructions contain an unfinished TODO placeholder"
    return True, "Skill is valid!"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python tools/quick_validate.py <skill_directory>", file=sys.stderr)
        return 2
    valid, message = validate_skill(sys.argv[1])
    print(message, file=sys.stdout if valid else sys.stderr)
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
