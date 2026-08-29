from __future__ import annotations

import copy
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import release_manifest


EXACT_SHA = "a" * 40
EXACT_REF = "refs/heads/main"
WORKFLOW_PATH = release_manifest.REPO_ROOT / ".github" / "workflows" / "clawhub-release.yml"


def mutate_actual_publish(workflow: str, old: str, new: str) -> str:
    marker = "      - name: Publish exact canonical skill"
    prefix, actual = workflow.split(marker, maxsplit=1)
    if old not in actual:
        raise AssertionError(f"actual publish block does not contain {old!r}")
    return prefix + marker + actual.replace(old, new, 1)


def find_clawhub_skills_reader() -> Path:
    candidates: list[Path] = []
    if shutil.which("asdf"):
        resolved = subprocess.run(
            ["asdf", "which", "clawhub"], capture_output=True, text=True, check=False
        )
        if resolved.returncode == 0:
            executable = Path(resolved.stdout.strip())
            candidates.extend(
                [
                    executable.parents[1] / "lib" / "node_modules" / "clawhub" / "dist" / "skills.js",
                    executable.resolve().parents[1] / "dist" / "skills.js",
                ]
            )
    npm_root = Path(
        subprocess.run(
            ["npm", "root", "-g"], check=True, capture_output=True, text=True
        ).stdout.strip()
    )
    candidates.append(npm_root / "clawhub" / "dist" / "skills.js")
    reader = next((path for path in candidates if path.is_file()), None)
    if reader is None:
        raise AssertionError("pinned ClawHub skills reader was not found")
    return reader


class ReleaseManifestTests(unittest.TestCase):
    def test_manifest_catalog_and_prohibited_values_are_immutable(self) -> None:
        attacks: list[dict[str, object]] = []
        for field, value in (
            ("name", "Drifted Name"),
            ("version", "2.0.1"),
            ("changelog", "Different but valid release notes."),
            ("categories", ["productivity"]),
            ("topics", ["pdf", "documents"]),
            ("publisher", "someone-else"),
        ):
            template = copy.deepcopy(release_manifest.load_template())
            template["release"][field] = value
            attacks.append(template)
        template = copy.deepcopy(release_manifest.load_template())
        template["cli"]["version"] = "9.9.9"
        attacks.append(template)
        template = copy.deepcopy(release_manifest.load_template())
        template["prohibited_without_separate_approval"] = ["ClawHub publish"]
        attacks.append(template)
        template = copy.deepcopy(release_manifest.load_template())
        template["extra"] = "drift"
        attacks.append(template)
        for template in attacks:
            with self.subTest(template=template):
                with self.assertRaisesRegex(ValueError, "immutable snapshot drifted"):
                    release_manifest.validate_template(template)

    def test_public_baseline_values_and_nested_schema_are_immutable(self) -> None:
        attacks: list[dict[str, object]] = []
        baseline = copy.deepcopy(release_manifest.load_public_baseline())
        baseline["captured_at"] = "2026-08-30"
        attacks.append(baseline)
        baseline = copy.deepcopy(release_manifest.load_public_baseline())
        baseline["migration_source"]["security"] = "suspicious"
        attacks.append(baseline)
        baseline = copy.deepcopy(release_manifest.load_public_baseline())
        del baseline["migration_source"]["provenance"]
        attacks.append(baseline)
        baseline = copy.deepcopy(release_manifest.load_public_baseline())
        baseline["migration_source"]["extra"] = "drift"
        attacks.append(baseline)
        baseline = copy.deepcopy(release_manifest.load_public_baseline())
        baseline["prohibited_until_final_approval"] = ["ClawHub publish"]
        attacks.append(baseline)
        for baseline in attacks:
            with self.subTest(baseline=baseline):
                with self.assertRaisesRegex(ValueError, "immutable snapshot drifted"):
                    release_manifest.validate_public_baseline(
                        baseline, release_manifest.load_template()
                    )

    def test_duplicate_manifest_and_baseline_json_keys_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            template_path = directory_path / "template.json"
            template_path.write_text(
                '{"schema_version": 1, "schema_version": 1}\n', encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "duplicate key"):
                release_manifest.load_template(template_path)
            baseline_path = directory_path / "baseline.json"
            baseline_path.write_text(
                '{"captured_at": "2026-08-29", "captured_at": "2026-08-29"}\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "duplicate key"):
                release_manifest.load_public_baseline(baseline_path)

    def test_package_layout_and_exact_ignore_contract(self) -> None:
        release_manifest.validate_package_layout()
        rules = (
            release_manifest.PACKAGE_PATH / ".clawhubignore"
        ).read_text(encoding="utf-8").splitlines()
        self.assertEqual(rules, list(release_manifest.EXPECTED_IGNORE_RULES))

    def test_ignore_negation_reordering_duplicates_and_extras_are_rejected(self) -> None:
        canonical = list(release_manifest.EXPECTED_IGNORE_RULES)
        attacks = [
            canonical + ["!_meta.json"],
            canonical + ["!tests/"],
            list(reversed(canonical)),
            canonical + [canonical[-1]],
            canonical + ["*.tmp"],
        ]
        for rules in attacks:
            with self.subTest(rules=rules):
                with self.assertRaisesRegex(ValueError, "ignore rules or order drifted"):
                    release_manifest.validate_ignore_rules(rules)

    def test_actual_pinned_packager_excludes_release_only_files(self) -> None:
        version = subprocess.run(
            ["clawhub", "--cli-version"], check=True, capture_output=True, text=True
        ).stdout.strip()
        self.assertEqual(version, "0.23.3")
        skills_reader = find_clawhub_skills_reader()

        reader_script = """
            const { listSkillFiles } = await import(process.argv[1]);
            const paths = (await listSkillFiles(process.argv[2]))
              .map((entry) => entry.relPath);
            if (!paths.includes("SKILL.md")) process.exit(3);
            const bad = paths.filter((path) =>
              path === ".env" ||
              path === "_meta.json" ||
              path === "tests" || path.startsWith("tests/") ||
              path === "__pycache__" || path.includes("/__pycache__/") ||
              path.endsWith(".pyc")
            );
            if (bad.length) process.exit(4);
        """
        subprocess.run(
            [
                "node",
                "--input-type=module",
                "-e",
                reader_script,
                skills_reader.as_uri(),
                str(release_manifest.PACKAGE_PATH),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_actual_pinned_packager_negation_reincludes_and_validator_rejects(self) -> None:
        version = subprocess.run(
            ["clawhub", "--cli-version"], check=True, capture_output=True, text=True
        ).stdout.strip()
        self.assertEqual(version, "0.23.3")
        skills_reader = find_clawhub_skills_reader()
        bad_rules = list(release_manifest.EXPECTED_IGNORE_RULES) + ["!_meta.json"]
        with self.assertRaisesRegex(ValueError, "ignore rules or order drifted"):
            release_manifest.validate_ignore_rules(bad_rules)

        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "skill"
            package.mkdir()
            (package / "SKILL.md").write_text(
                "---\nname: test\ndescription: test\n---\n", encoding="utf-8"
            )
            (package / "_meta.json").write_text("{}\n", encoding="utf-8")
            (package / ".clawhubignore").write_text(
                "_meta.json\n!_meta.json\n", encoding="utf-8"
            )
            reader_script = """
                const { listSkillFiles } = await import(process.argv[1]);
                const paths = (await listSkillFiles(process.argv[2]))
                  .map((entry) => entry.relPath);
                process.stdout.write(JSON.stringify(paths));
            """
            result = subprocess.run(
                [
                    "node",
                    "--input-type=module",
                    "-e",
                    reader_script,
                    skills_reader.as_uri(),
                    str(package),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("_meta.json", json.loads(result.stdout))

    def test_template_is_validation_only_and_catalog_metadata_is_bounded(self) -> None:
        template = release_manifest.load_template()
        self.assertEqual(template["release"]["default_mode"], "validate")
        self.assertEqual(template["cli"]["version"], "0.23.3")
        self.assertLessEqual(len(template["release"]["categories"]), 3)
        self.assertLessEqual(len(template["release"]["topics"]), 5)
        self.assertFalse(template["gates"]["slug_migration_enabled"])
        self.assertEqual(
            template["gates"]["release_enabled_variable"],
            "CLAWHUB_RELEASE_ENABLED",
        )
        self.assertEqual(template["gates"]["release_enabled_value"], "true")
        self.assertTrue(
            template["gates"]["environment_reviewers_configured_externally"]
        )

    def test_render_binds_exact_repo_commit_ref_and_path(self) -> None:
        rendered = release_manifest.render_manifest(
            release_manifest.load_template(), EXACT_SHA, EXACT_REF
        )
        self.assertEqual(
            rendered["source"],
            {
                "repository": "PSPDFKit-labs/nutrient-agent-skill",
                "commit": EXACT_SHA,
                "ref": EXACT_REF,
                "path": "nutrient-document-processing",
            },
        )
        serialized = json.dumps(rendered)
        self.assertNotIn(release_manifest.COMMIT_SENTINEL, serialized)
        self.assertNotIn(release_manifest.REF_SENTINEL, serialized)

    def test_short_commit_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "full lowercase"):
            release_manifest.render_manifest(
                release_manifest.load_template(), "abc123", EXACT_REF
            )

    def test_repository_drift_is_rejected(self) -> None:
        template = copy.deepcopy(release_manifest.load_template())
        template["source"]["repository"] = "attacker/example"
        with self.assertRaisesRegex(ValueError, "unexpected source repository"):
            release_manifest.validate_template(template)

    def test_manifest_cli_writes_only_provenance_data(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "release-manifest.json"
            rendered = release_manifest.render_manifest(
                release_manifest.load_template(), EXACT_SHA, EXACT_REF
            )
            output.write_text(json.dumps(rendered), encoding="utf-8")
            text = output.read_text(encoding="utf-8")
            self.assertNotIn("token", text.lower())
            self.assertNotIn("authorization", text.lower())

    def test_public_baseline_binds_migration_source_and_canonical_target(self) -> None:
        template = release_manifest.load_template()
        baseline = release_manifest.load_public_baseline()
        release_manifest.validate_public_baseline(baseline, template)
        self.assertEqual(
            baseline["migration_source"],
            {
                "slug": "nutrient-document-processing-universal",
                "version": "1.1.2",
                "verification": "pass",
                "security": "clean",
                "provenance": "unavailable",
                "signature": "unsigned",
            },
        )
        self.assertEqual(
            baseline["canonical_target"]["slug"], "nutrient-document-processing"
        )
        self.assertEqual(baseline["canonical_target"]["version"], "2.0.0")
        self.assertFalse(baseline["migration"]["enabled"])

    def test_workflow_publish_blocks_exactly_match_manifest(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        template = release_manifest.load_template()
        release_manifest.validate_workflow_publish_contract(workflow, template)
        commands = release_manifest.extract_publish_commands(workflow)
        self.assertEqual(len(commands), 2)
        self.assertEqual(
            ["--dry-run" in command for command in commands], [True, False]
        )

    def test_actual_publish_stale_slug_mutation_is_rejected(self) -> None:
        workflow = mutate_actual_publish(
            WORKFLOW_PATH.read_text(encoding="utf-8"),
            "--slug nutrient-document-processing",
            "--slug nutrient-document-processing-universal",
        )
        with self.assertRaisesRegex(ValueError, "stale universal slug"):
            release_manifest.validate_workflow_publish_contract(
                workflow, release_manifest.load_template()
            )

    def test_actual_publish_migration_mutation_is_rejected(self) -> None:
        workflow = mutate_actual_publish(
            WORKFLOW_PATH.read_text(encoding="utf-8"),
            "            --json",
            "            --migrate-owner \\\n            --json",
        )
        with self.assertRaisesRegex(ValueError, "owner migration"):
            release_manifest.validate_workflow_publish_contract(
                workflow, release_manifest.load_template()
            )

    def test_workflow_uses_owner_only_config_and_never_prints_secret(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn("CLAWHUB_CONFIG_PATH", workflow)
        self.assertIn("CLAWHUB_PUBLISH_TOKEN", workflow)
        self.assertIn(
            'JSON.stringify({ registry: "https://clawhub.ai", token }, null, 2)',
            workflow,
        )
        self.assertIn('mode: 0o600, flag: "wx"', workflow)
        self.assertIn("clawhub --no-input whoami", workflow)
        self.assertIn("if: always()", workflow)
        self.assertNotRegex(workflow, r"(?m)^\s*CLAWHUB_TOKEN\s*:")
        self.assertNotRegex(
            workflow,
            r"(?im)^\s*(?:echo|printf)\b[^\n]*(?:CLAWHUB_PUBLISH_TOKEN|CLAWHUB_TOKEN)",
        )
        self.assertNotRegex(workflow, r"\bconsole\.log\s*\([^\n]*\btoken\b")

    def test_workflow_auth_config_is_read_by_pinned_cli(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        script_match = re.search(
            r"(?ms)^\s*node -e '\n(?P<script>.*?)^\s*'\s*$", workflow
        )
        self.assertIsNotNone(script_match)
        version = subprocess.run(
            ["clawhub", "--cli-version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        self.assertEqual(version, "0.23.3")
        candidates: list[Path] = []
        if shutil.which("asdf"):
            resolved = subprocess.run(
                ["asdf", "which", "clawhub"],
                check=False,
                capture_output=True,
                text=True,
            )
            if resolved.returncode == 0:
                executable = Path(resolved.stdout.strip())
                candidates.append(
                    executable.parents[1]
                    / "lib"
                    / "node_modules"
                    / "clawhub"
                    / "dist"
                    / "cli"
                    / "authToken.js"
                )
                candidates.append(
                    executable.resolve().parents[1]
                    / "dist"
                    / "cli"
                    / "authToken.js"
                )
        npm_root = Path(
            subprocess.run(
                ["npm", "root", "-g"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
        candidates.append(npm_root / "clawhub" / "dist" / "cli" / "authToken.js")
        auth_reader = next((path for path in candidates if path.is_file()), None)
        self.assertIsNotNone(auth_reader)

        sentinel = "test-only-clawhub-token"
        with tempfile.TemporaryDirectory() as directory:
            config_dir = Path(directory) / "clawhub"
            config_path = config_dir / "config.json"
            config_dir.mkdir(mode=0o700)
            config_dir.chmod(0o700)
            env = os.environ.copy()
            env.update(
                {
                    "CLAWHUB_PUBLISH_TOKEN": sentinel,
                    "CLAWHUB_CONFIG_PATH": str(config_path),
                }
            )
            subprocess.run(
                ["node", "-e", script_match.group("script")],
                check=True,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                json.loads(config_path.read_text(encoding="utf-8")),
                {"registry": "https://clawhub.ai", "token": sentinel},
            )
            self.assertEqual(config_path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(config_dir.stat().st_mode & 0o777, 0o700)
            reader_script = """
                const { getOptionalAuthToken } = await import(process.argv[1]);
                if (await getOptionalAuthToken() !== process.argv[2]) process.exit(3);
            """
            subprocess.run(
                [
                    "node",
                    "--input-type=module",
                    "-e",
                    reader_script,
                    auth_reader.as_uri(),
                    sentinel,
                ],
                check=True,
                env=env,
                capture_output=True,
                text=True,
            )

    def test_extra_legacy_publish_alias_is_rejected(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8") + """
  extra:
    runs-on: ubuntu-latest
    steps:
      - run: clawhub --no-input publish nutrient-document-processing --version 2.0.0
"""
        with self.assertRaisesRegex(ValueError, "surface drifted"):
            release_manifest.validate_workflow_publish_contract(
                workflow, release_manifest.load_template()
            )

    def test_extra_sync_invocation_is_rejected(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8") + """
  extra:
    runs-on: ubuntu-latest
    steps:
      - run: clawhub --no-input sync
"""
        with self.assertRaisesRegex(ValueError, "surface drifted"):
            release_manifest.validate_workflow_publish_contract(
                workflow, release_manifest.load_template()
            )

    def test_reconstructed_stale_slug_through_alias_is_rejected(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8") + """
  extra:
    runs-on: ubuntu-latest
    steps:
      - run: clawhub --no-input publish "nutrient-document-processing-""universal"
"""
        with self.assertRaisesRegex(ValueError, "surface drifted"):
            release_manifest.validate_workflow_publish_contract(
                workflow, release_manifest.load_template()
            )

    def test_computed_global_binary_invocation_is_rejected(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8").replace(
            "      - name: Remove temporary ClawHub auth config",
            """      - name: Computed binary bypass
        run: $(npm prefix -g)/bin/clawhub --no-input sync

      - name: Remove temporary ClawHub auth config""",
            1,
        )
        with self.assertRaisesRegex(ValueError, "step surface drifted"):
            release_manifest.validate_workflow_publish_contract(
                workflow, release_manifest.load_template()
            )

    def test_split_executable_name_is_rejected(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8").replace(
            "      - name: Remove temporary ClawHub auth config",
            """      - name: Split executable bypass
        run: |
          CLI_NAME="claw"
          ${CLI_NAME}hub --no-input sync

      - name: Remove temporary ClawHub auth config""",
            1,
        )
        with self.assertRaisesRegex(ValueError, "step surface drifted"):
            release_manifest.validate_workflow_publish_contract(
                workflow, release_manifest.load_template()
            )

    def test_computed_binary_with_constructed_stale_slug_is_rejected(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8").replace(
            "      - name: Remove temporary ClawHub auth config",
            """      - name: Constructed stale slug bypass
        run: $(npm prefix -g)/bin/clawhub --no-input publish "nutrient-document-processing-""universal"

      - name: Remove temporary ClawHub auth config""",
            1,
        )
        with self.assertRaisesRegex(ValueError, "step surface drifted"):
            release_manifest.validate_workflow_publish_contract(
                workflow, release_manifest.load_template()
            )

    def test_publish_job_must_depend_on_preview(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8").replace(
            "    needs: validate-and-preview\n", "", 1
        )
        with self.assertRaisesRegex(ValueError, "job controls drifted"):
            release_manifest.validate_workflow_publish_contract(
                workflow, release_manifest.load_template()
            )

    def test_publish_checkout_must_bind_exact_workflow_sha(self) -> None:
        prefix, publish = WORKFLOW_PATH.read_text(encoding="utf-8").split(
            "\n  publish:\n", maxsplit=1
        )
        publish = publish.replace(
            "          ref: ${{ github.sha }}",
            "          ref: refs/heads/main",
            1,
        )
        workflow = prefix + "\n  publish:\n" + publish
        with self.assertRaisesRegex(ValueError, "metadata drifted"):
            release_manifest.validate_workflow_publish_contract(
                workflow, release_manifest.load_template()
            )

    def test_publish_condition_cannot_be_hidden_in_job_env(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8").replace(
            "  publish:\n    if: inputs.mode == 'publish'",
            "  publish:\n"
            "    if: always()\n"
            "    env:\n"
            "      CONTRACT_MARKER: \"inputs.mode == 'publish'\"",
            1,
        )
        with self.assertRaisesRegex(ValueError, "job controls drifted"):
            release_manifest.validate_workflow_publish_contract(
                workflow, release_manifest.load_template()
            )

    def test_duplicate_yaml_controls_are_rejected(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8").replace(
            "    needs: validate-and-preview\n",
            "    needs: validate-and-preview\n    needs: validate-and-preview\n",
            1,
        )
        with self.assertRaisesRegex(ValueError, "duplicate YAML key"):
            release_manifest.validate_workflow_publish_contract(
                workflow, release_manifest.load_template()
            )

    def test_release_enablement_and_external_reviewer_contract_is_documented(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        documentation = (
            release_manifest.REPO_ROOT / "docs" / "clawhub-release" / "README.md"
        ).read_text(encoding="utf-8")
        self.assertIn('test "$CLAWHUB_RELEASE_ENABLED" = "true"', workflow)
        self.assertIn("required reviewers", documentation)
        self.assertIn(
            "Merely naming the environment in workflow YAML does not add reviewer protection",
            documentation,
        )


if __name__ == "__main__":
    unittest.main()
