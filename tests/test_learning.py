"""Behavioral regressions for deliberate, source-bound learning maintenance."""

import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import review_tools as review


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class LearningTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="kit-learning-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.collection = self.root / "sources with spaces"
        self.kit = self.root / "kit"
        (self.collection / "public/tool/src").mkdir(parents=True)
        (self.collection / "private/unused").mkdir(parents=True)
        (self.collection / "public/kit").mkdir()
        (self.kit / "research").mkdir(parents=True)
        (self.kit / "scripts").mkdir()
        (self.kit / "scripts/review_tools.py").write_bytes(
            Path(review.__file__).read_bytes()
        )
        (self.kit / "LEARNING.md").write_text(
            '<a id="review"></a>\nReviewed explanation.\n'
        )
        (self.collection / "README.md").write_text("Canonical sources.\n")
        (self.collection / "public/tool/README.md").write_text("Tool declaration.\n")
        # This must be read as bytes, never imported or invoked by a review.
        (self.collection / "public/tool/src/main.py").write_text(
            "from pathlib import Path\nPath('EXECUTED').write_text('private-fixture-output')\n"
        )
        self.document = {
            "$schema": review.SCHEMA,
            "version": 1,
            "reviewed_on": "2026-09-13",
            "scope": "Selected fixture evidence only.",
            "collection_files": {"README.md": digest(self.collection / "README.md")},
            "sources": [
                {
                    "id": "tool",
                    "checkout": "public/tool",
                    "role": "tool",
                    "purpose": "One source reader.",
                    "observation": "Source review is not runtime evidence.",
                    "files": {
                        name: digest(self.collection / "public/tool" / name)
                        for name in ("README.md", "src/main.py")
                    },
                },
                {
                    "id": "kit",
                    "checkout": "public/kit",
                    "role": "kit",
                    "purpose": "Self-integrity lives in the kit manifest.",
                    "observation": "Avoid a self-referential receipt.",
                    "files": {},
                },
                {
                    "id": "unused",
                    "checkout": "private/unused",
                    "role": "empty",
                    "purpose": "Reserved directory.",
                    "observation": "No implementation exists.",
                    "files": {},
                },
            ],
            "lessons": [
                {
                    "id": "L01",
                    "claim": "Source bytes need a reviewed explanation.",
                    "sources": ["tool"],
                    "adopted_in": ["LEARNING.md#review"],
                }
            ],
        }
        self.save()

    def save(self, document=None):
        (self.kit / review.REGISTER).write_text(json.dumps(document or self.document))

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, "-B", str(self.kit / "scripts/review_tools.py"), *args],
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

    def test_standalone_and_external_checks_are_distinct(self):
        standalone = self.cli()
        self.assertEqual(standalone.returncode, 0, standalone.stderr)
        self.assertFalse(json.loads(standalone.stdout)["external_sources_checked"])
        external = self.cli("--sources-root", str(self.collection))
        self.assertEqual(external.returncode, 0, external.stderr)
        self.assertEqual(
            json.loads(external.stdout)["status"], "selected-evidence-current"
        )
        self.assertFalse((self.root / "EXECUTED").exists())

    def test_changed_source_requires_review_and_capture_never_writes(self):
        before = (self.kit / review.REGISTER).read_bytes()
        path = self.collection / "public/tool/src/main.py"
        path.write_text("Changed behavior; private-fixture-output.\n")
        result = self.cli("--sources-root", str(self.collection), "--capture")
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "stale")
        self.assertEqual(
            report["problems"],
            [{"path": "public/tool/src/main.py", "status": "changed"}],
        )
        self.assertEqual(
            report["candidate_receipts"]["sources"]["tool"]["src/main.py"], digest(path)
        )
        self.assertNotIn("private-fixture-output", result.stdout + result.stderr)
        self.assertEqual((self.kit / review.REGISTER).read_bytes(), before)

    def test_symlinked_map_requires_an_explicit_regular_document(self):
        document = self.root / "workspace map.md"
        original = self.collection / "README.md"
        document.write_bytes(original.read_bytes())
        original.unlink()
        original.symlink_to(document)
        self.assertEqual(self.cli("--sources-root", str(self.collection)).returncode, 1)
        result = self.cli(
            "--sources-root", str(self.collection), "--source-map", str(document)
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["explicit_source_map"])
        self.assertNotIn(str(self.root), result.stdout + result.stderr)
        document.write_text("Changed canonical source map.\n")
        self.assertEqual(
            self.cli(
                "--sources-root", str(self.collection), "--source-map", str(document)
            ).returncode,
            1,
        )
        self.assertEqual(self.cli("--source-map", str(document)).returncode, 2)

    def test_added_removed_and_no_longer_empty_directories(self):
        (self.collection / "public/new-tool").mkdir()
        (self.collection / "public/kit").rmdir()
        (self.collection / "private/unused/README.md").write_text(
            "New implementation.\n"
        )
        result = review.inspect_sources(self.document, self.collection)
        self.assertEqual(result["status"], "stale")
        self.assertCountEqual(
            result["problems"],
            [
                {"checkout": "public/new-tool", "status": "unreviewed"},
                {"checkout": "public/kit", "status": "missing"},
                {"checkout": "private/unused", "status": "no-longer-empty"},
            ],
        )

    def test_canonical_map_and_missing_evidence_invalidate_review(self):
        (self.collection / "README.md").write_text("Changed development source.\n")
        (self.collection / "public/tool/README.md").unlink()
        problems = review.inspect_sources(self.document, self.collection)["problems"]
        self.assertIn({"path": "README.md", "status": "changed"}, problems)
        self.assertIn(
            {"path": "public/tool/README.md", "status": "unavailable"}, problems
        )

    def test_symlinks_traversal_and_credentials_are_not_evidence(self):
        for path in (
            "../outside.md",
            "/outside.md",
            "a/../b.md",
            "a//b.md",
            ".env",
            ".ssh/key.json",
            "C:/a.md",
        ):
            with self.subTest(path=path), self.assertRaises(ValueError):
                review.read_file(self.collection, path)
        target = self.collection / "public/tool/src/main.py"
        target.unlink()
        target.symlink_to(self.collection / "README.md")
        problems = review.inspect_sources(self.document, self.collection)["problems"]
        self.assertIn(
            {"path": "public/tool/src/main.py", "status": "unavailable"}, problems
        )
        directory = self.collection / "public/tool/src"
        target.unlink()
        directory.rmdir()
        directory.symlink_to(
            self.collection / "private/unused", target_is_directory=True
        )
        with self.assertRaises(ValueError):
            review.read_file(self.collection, "public/tool/src/main.py")
        (self.collection / "public/linked").symlink_to(
            self.kit, target_is_directory=True
        )
        self.assertEqual(self.cli("--sources-root", str(self.collection)).returncode, 2)

    def test_special_and_oversized_files_are_unavailable_without_hanging(self):
        path = self.collection / "public/tool/src/main.py"
        path.unlink()
        os.mkfifo(path)
        result = self.cli("--sources-root", str(self.collection))
        self.assertEqual(result.returncode, 1)
        path.unlink()
        path.write_bytes(b"x" * (review.LIMIT + 1))
        result = self.cli("--sources-root", str(self.collection))
        self.assertEqual(result.returncode, 1)

    def test_broken_lesson_adoption_and_unreviewed_tools_fail_internal_gate(self):
        for mutation in (
            "source",
            "adoption",
            "duplicate",
            "uncovered",
            "date",
            "hash",
        ):
            document = copy.deepcopy(self.document)
            if mutation == "source":
                document["lessons"][0]["sources"] = ["unknown"]
            elif mutation == "adoption":
                document["lessons"][0]["adopted_in"] = ["LEARNING.md#missing"]
            elif mutation == "duplicate":
                document["sources"].append(copy.deepcopy(document["sources"][0]))
            elif mutation == "uncovered":
                extra = copy.deepcopy(document["sources"][0])
                extra.update(id="uncovered", checkout="private/uncovered")
                document["sources"].append(extra)
            elif mutation == "date":
                document["reviewed_on"] = "9999-12-31"
            else:
                document["collection_files"]["README.md"] = "invalid"
            self.save(document)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                review.validate(self.kit)

    def test_invalid_json_and_missing_root_do_not_echo_private_data(self):
        (self.kit / review.REGISTER).write_text('{"private-fixture-output": invalid}')
        result = self.cli()
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("private-fixture-output", result.stdout + result.stderr)
        self.save()
        result = self.cli("--sources-root", str(self.root / "missing"))
        self.assertEqual(result.returncode, 2)
        self.assertNotIn(str(self.root), result.stdout + result.stderr)
        self.assertEqual(self.cli("--capture").returncode, 2)

    def test_scope_does_not_claim_uncited_files_or_nested_mirrors(self):
        (self.collection / "public/tool/uncited.py").write_text(
            "Changed uncited behavior.\n"
        )
        (self.collection / "private/.cache").mkdir()
        result = review.inspect_sources(self.document, self.collection)
        self.assertEqual(result["status"], "selected-evidence-current")
        self.assertIn("explicitly selected", result["scope"])


if __name__ == "__main__":
    unittest.main()
