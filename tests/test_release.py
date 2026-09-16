import json
import tempfile
import unittest
from pathlib import Path

from scripts import check_release


class ReleaseAuditTests(unittest.TestCase):
    def make_root(self, directory):
        root = Path(directory)
        for name in check_release.REQUIRED_POLICIES:
            (root / name).write_text("Synthetic policy.\n", encoding="utf-8")
        (root / "manifest.json").write_text(
            json.dumps({"language": "en"}), encoding="utf-8"
        )
        return root

    def test_complete_local_release_scaffold_passes(self):
        with tempfile.TemporaryDirectory(prefix="kit-release-") as directory:
            root = self.make_root(directory)
            (root / "LICENSE").write_text("Synthetic license text.\n", encoding="utf-8")
            self.assertEqual(check_release.audit(root), [])

    def test_missing_license_is_a_blocker(self):
        with tempfile.TemporaryDirectory(prefix="kit-release-") as directory:
            root = self.make_root(directory)
            self.assertIn("missing release license", check_release.audit(root))

    def test_language_and_privacy_findings_are_blockers(self):
        with tempfile.TemporaryDirectory(prefix="kit-release-") as directory:
            root = self.make_root(directory)
            (root / "LICENSE").write_text("Synthetic license text.\n", encoding="utf-8")
            (root / "manifest.json").write_text(
                json.dumps({"language": "de"}), encoding="utf-8"
            )
            (root / "local.txt").write_text(
                "/" + "home/person/private-data\n", encoding="utf-8"
            )
            problems = check_release.audit(root)
            self.assertIn("manifest language must be en", problems)
            self.assertTrue(
                any(item.startswith("privacy finding:") for item in problems)
            )


if __name__ == "__main__":
    unittest.main()
