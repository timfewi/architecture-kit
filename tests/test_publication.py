import tempfile
import unittest
from pathlib import Path

from scripts import check_publication


class PublicationPrivacyTests(unittest.TestCase):
    def test_clean_synthetic_tree_passes(self):
        with tempfile.TemporaryDirectory(prefix="kit-publication-") as directory:
            root = Path(directory)
            (root / "README.md").write_text(
                "Synthetic data and relative/path only.\n", encoding="utf-8"
            )
            self.assertEqual(check_publication.findings(root), [])

    def test_private_data_and_secret_files_are_reported(self):
        with tempfile.TemporaryDirectory(prefix="kit-publication-") as directory:
            root = Path(directory)
            (root / "notes.txt").write_text(
                "Contact person" + "@example.org from /" + "home/person/project.\n",
                encoding="utf-8",
            )
            (root / "identity.pem").write_text("synthetic\n", encoding="utf-8")
            labels = {label for _, label, _ in check_publication.findings(root)}
            self.assertEqual(
                labels,
                {
                    "Unix home-directory path",
                    "email address",
                    "secret-bearing filename",
                },
            )

    def test_generated_state_is_ignored(self):
        with tempfile.TemporaryDirectory(prefix="kit-publication-") as directory:
            root = Path(directory)
            cache = root / ".direnv"
            cache.mkdir()
            (cache / "local.txt").write_text(
                "person" + "@example.org /" + "home/person/project\n", encoding="utf-8"
            )
            self.assertEqual(check_publication.findings(root), [])


if __name__ == "__main__":
    unittest.main()
