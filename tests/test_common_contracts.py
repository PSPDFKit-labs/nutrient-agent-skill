from __future__ import annotations

import argparse
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
COMMON_PATH = (
    REPO_ROOT / "nutrient-document-processing" / "scripts" / "lib" / "common.py"
)
SPEC = importlib.util.spec_from_file_location("ndp_common", COMMON_PATH)
assert SPEC and SPEC.loader
common = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(common)


class PageRangeContractTests(unittest.TestCase):
    def test_page_ranges_are_inclusive_and_keep_negative_indexes(self) -> None:
        self.assertEqual(common.parse_page_range("0:4"), {"start": 0, "end": 4})
        self.assertEqual(common.parse_page_range("-3:-1"), {"start": -3, "end": -1})
        self.assertEqual(common.parse_page_range("0:-1"), {"start": 0, "end": -1})

    def test_reversed_same_sign_range_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            common.parse_page_range("4:0")
        with self.assertRaises(ValueError):
            common.parse_page_range("-1:-3")


class OutputContractTests(unittest.TestCase):
    def test_all_typed_result_shapes_are_written(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary = root / "binary.pdf"
            content = root / "content.md"
            data = root / "data.json"

            common.write_typed_output(
                {"buffer": b"%PDF-test", "mimeType": "application/pdf"}, str(binary)
            )
            common.write_typed_output(
                {"content": "hello", "mimeType": "text/markdown"}, str(content)
            )
            common.write_typed_output({"data": {"ok": True}}, str(data))

            self.assertEqual(binary.read_bytes(), b"%PDF-test")
            self.assertEqual(content.read_text(encoding="utf-8"), "hello")
            self.assertIn('"ok": true', data.read_text(encoding="utf-8"))
            self.assertEqual(binary.stat().st_mode & 0o777, 0o600)

    def test_existing_output_is_never_replaced(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "existing.txt"
            destination.write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                common.write_text_output("replace", str(destination))
            self.assertEqual(destination.read_text(encoding="utf-8"), "keep")


class SecretAndConsentTests(unittest.TestCase):
    def test_secret_file_must_be_owner_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            secret = Path(directory) / "secret"
            secret.write_text("value\n", encoding="utf-8")
            os.chmod(secret, 0o600)
            self.assertEqual(common.read_secret_file(str(secret), "secret"), "value")
            os.chmod(secret, 0o644)
            with self.assertRaises(PermissionError):
                common.read_secret_file(str(secret), "secret")

    def test_paid_request_confirmation_is_per_invocation(self) -> None:
        blocked = argparse.Namespace(
            _processor_operation="convert document",
            estimated_credits=2.0,
            confirm_external_processing=False,
        )
        with self.assertRaisesRegex(RuntimeError, "Paid DWS request blocked"):
            common.require_processor_confirmation(blocked)

        approved = argparse.Namespace(confirm_external_processing=True)
        common.require_processor_confirmation(approved)


if __name__ == "__main__":
    unittest.main()
