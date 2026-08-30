from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "nutrient-document-processing"
SCRIPTS_DIR = SKILL_DIR / "scripts"
FIXTURE = json.loads(
    (REPO_ROOT / "tests" / "fixtures" / "processor-3.1.0-contracts.json").read_text(
        encoding="utf-8"
    )
)


class PackageContractTests(unittest.TestCase):
    def test_clawhub_name_license_and_runtime_metadata(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = skill.split("---", 2)[1]
        self.assertIn(f"name: {SKILL_DIR.name}", frontmatter)
        self.assertIn("license: MIT-0", frontmatter)
        self.assertIn("openclaw:", frontmatter)
        self.assertIn("bins: [uv]", frontmatter)
        self.assertIn("env: [NUTRIENT_API_KEY]", frontmatter)
        self.assertIn("primaryEnv: NUTRIENT_API_KEY", frontmatter)
        license_text = (SKILL_DIR / "LICENSE.txt").read_text(encoding="utf-8")
        self.assertTrue(license_text.startswith("MIT No Attribution"))

    def test_every_runnable_pep_723_script_pins_sdk_3_1_0(self) -> None:
        runnable = sorted(SCRIPTS_DIR.glob("*.py")) + [
            SKILL_DIR / "assets" / "templates" / "custom-workflow-template.py"
        ]
        for path in runnable:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn('dependencies = ["nutrient-dws==3.1.0"]', text)


class OfflineBehaviorContractTests(unittest.TestCase):
    def test_all_helpers_have_paid_request_gate(self) -> None:
        for path in sorted(SCRIPTS_DIR.glob("*.py")):
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("add_processor_confirmation_args(parser", text)
                self.assertIn("create_client(args)", text)

    def test_all_helpers_print_help_without_key_or_sdk_import(self) -> None:
        environment = os.environ.copy()
        environment.pop("NUTRIENT_API_KEY", None)
        for path in sorted(SCRIPTS_DIR.glob("*.py")):
            with self.subTest(path=path.name):
                result = subprocess.run(
                    [sys.executable, str(path), "--help"],
                    cwd=REPO_ROOT,
                    env=environment,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_confirmation_blocks_before_api_key_or_network(self) -> None:
        environment = os.environ.copy()
        environment.pop("NUTRIENT_API_KEY", None)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "convert.py"),
                "--input",
                "document.pdf",
                "--format",
                "pdf",
                "--out",
                "never-created.pdf",
                "--estimated-credits",
                "1",
            ],
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Paid DWS request blocked", result.stderr)
        self.assertFalse((REPO_ROOT / "never-created.pdf").exists())

    def test_high_risk_helpers_are_explicit_and_staged(self) -> None:
        redact = (SCRIPTS_DIR / "redact-ai.py").read_text(encoding="utf-8")
        self.assertIn('"stage", pages', redact)
        self.assertNotIn('choices=["stage", "apply"]', redact)

        sign = (SCRIPTS_DIR / "sign.py").read_text(encoding="utf-8")
        self.assertIn('"--signature-json-file"', sign)
        self.assertIn("required=True", sign)
        self.assertNotIn('"--signature-json"', sign)

        passwords = (SCRIPTS_DIR / "password-protect.py").read_text(encoding="utf-8")
        self.assertIn('"--user-password-file"', passwords)
        self.assertIn('"--owner-password-file"', passwords)
        self.assertNotRegex(passwords, r'"--(?:user|owner)-password"')

    def test_convert_handles_content_output_and_template_is_portable(self) -> None:
        convert = (SCRIPTS_DIR / "convert.py").read_text(encoding="utf-8")
        self.assertIn("write_typed_output(result, args.out)", convert)
        template = (
            SKILL_DIR / "assets" / "templates" / "custom-workflow-template.py"
        ).read_text(encoding="utf-8")
        self.assertIn('os.environ.get("NUTRIENT_SKILL_DIR")', template)


class PayloadFixtureTests(unittest.TestCase):
    def test_every_json_reference_block_is_valid_json(self) -> None:
        for path in sorted((SKILL_DIR / "references").glob("*.md")):
            text = path.read_text(encoding="utf-8")
            blocks = re.findall(r"```json\n(.*?)\n```", text, flags=re.DOTALL)
            for index, block in enumerate(blocks):
                with self.subTest(path=path.name, block=index):
                    json.loads(block)

    def test_extraction_reference_matches_3_1_0_fixture(self) -> None:
        reference = (SKILL_DIR / "references" / "extraction-and-ocr.md").read_text(
            encoding="utf-8"
        )
        blocks = re.findall(r"```json\n(.*?)\n```", reference, flags=re.DOTALL)
        parsed = [json.loads(block) for block in blocks]
        outputs = [document.get("output") for document in parsed if "output" in document]
        for expected in FIXTURE["outputs"].values():
            self.assertIn(expected, outputs)

    def test_known_unsafe_raw_payloads_are_absent(self) -> None:
        references = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((SKILL_DIR / "references").glob("*.md"))
        )
        for unsafe in (
            '"type": "text"',
            '"type": "extraction"',
            '"type": "ai_redaction"',
            '"type": "sign"',
            '"type": "fillForm"',
            '"watermarkType"',
            '"imagePath"',
        ):
            with self.subTest(unsafe=unsafe):
                self.assertNotIn(unsafe, references)
        self.assertNotIn("end-exclusive", references)

    def test_published_package_has_no_shell_credential_expansion_or_printing(self) -> None:
        published_files = [REPO_ROOT / "README.md"] + [
            path
            for path in SKILL_DIR.rglob("*")
            if path.is_file() and path.suffix in {".md", ".py", ".yaml", ".yml", ".txt"}
        ]
        for path in published_files:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                self.assertNotRegex(text, r"(?i)authorization\s*:\s*bearer")
                self.assertNotRegex(text, r"(?im)^\s*curl\b")
                self.assertNotRegex(text, r"\$\{?NUTRIENT_(?:DWS_)?API_KEY\}?")
                self.assertNotRegex(
                    text,
                    r"(?is)(?:print|logger\.[a-z]+|logging\.[a-z]+)\s*\([^)]*(?:api_key|NUTRIENT_API_KEY)",
                )


if __name__ == "__main__":
    unittest.main()
