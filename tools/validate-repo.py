#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "nutrient-document-processing"
CONFLICT_MARKERS = ("<" * 7, "=" * 7, ">" * 7)
TEXT_SUFFIXES = {".md", ".txt", ".py", ".yaml", ".yml", ".svg", ".gitignore"}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def check_required_paths() -> None:
    required = [
        REPO_ROOT / "README.md",
        SKILL_DIR / "SKILL.md",
        SKILL_DIR / "LICENSE.txt",
        SKILL_DIR / "references" / "REFERENCE.md",
        SKILL_DIR / "scripts" / "lib" / "common.py",
        SKILL_DIR / "tests" / "testing-guide.md",
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


def check_readme_links() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    if 'href="nutrient-document-processing/LICENSE.txt"' not in readme:
        fail("README.md does not point its license badge at nutrient-document-processing/LICENSE.txt.")
    if "[Apache-2.0](nutrient-document-processing/LICENSE.txt)" not in readme:
        fail("README.md does not point its license section at nutrient-document-processing/LICENSE.txt.")


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


def main() -> None:
    check_required_paths()
    check_conflict_markers()
    check_skill_frontmatter()
    check_readme_links()
    check_reference_links()
    print("Repository validation passed.")


if __name__ == "__main__":
    main()
