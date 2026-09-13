"""Package integrity tests, distinct from model routing evaluation."""

import json
import tempfile
import unittest
from pathlib import Path

from scripts import check_skills


class SkillTests(unittest.TestCase):
    def test_actual_catalog_and_pilot_references(self):
        result = check_skills.check(check_skills.ROOT)
        self.assertEqual(len(result["skills"]), 4)

    def test_metadata_invalid_and_duplicate(self):
        cases = [
            "---\nname: x\nname: y\ndescription: Text\n---\nBody",
            "---\nname: Upper\ndescription: Text\n---\nBody",
            "---\nname: x\ndescription: ''\n---\nBody",
        ]
        for text in cases:
            with self.subTest(text=text), self.assertRaises(ValueError):
                check_skills.metadata(text)

    def test_resource_change_affects_digest_and_escape_fails(self):
        with tempfile.TemporaryDirectory(prefix="skill-test-") as temp:
            root = Path(temp)
            directory = root / "example"
            directory.mkdir()
            (directory / "references").mkdir()
            resource = directory / "references/guide.md"
            resource.write_text("Original", encoding="utf-8")
            source = directory / "SKILL.md"
            source.write_text(
                "---\nname: example\ndescription: Example\n---\nRead [guide](references/guide.md).",
                encoding="utf-8",
            )
            first = check_skills.skill_entry(directory, root)
            resource.write_text("Changed contract", encoding="utf-8")
            self.assertNotEqual(
                first["content_sha256"],
                check_skills.skill_entry(directory, root)["content_sha256"],
            )
            source.write_text(
                source.read_text().replace("references/guide.md", "../private.md")
            )
            with self.assertRaisesRegex(ValueError, "escaping"):
                check_skills.skill_entry(directory, root)

    def test_drift_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory(prefix="skill-test-") as temp:
            root = Path(temp)
            directory = root / "skills/example"
            directory.mkdir(parents=True)
            (directory / "SKILL.md").write_text(
                "---\nname: example\ndescription: Example\n---\nBody\n"
            )
            catalog = check_skills.catalog(root)
            (root / "skills/catalog.json").write_text(json.dumps(catalog))
            (root / "skills/routing-pilot.json").write_text('{"cases":[]}')
            check_skills.check(root)
            (directory / "SKILL.md").write_text(
                "---\nname: example\ndescription: Changed\n---\nBody\n"
            )
            with self.assertRaisesRegex(ValueError, "drift"):
                check_skills.check(root)
            (directory / "linked.md").symlink_to(root / "private.md")
            with self.assertRaisesRegex(ValueError, "symlink"):
                check_skills.catalog(root)


if __name__ == "__main__":
    unittest.main()
