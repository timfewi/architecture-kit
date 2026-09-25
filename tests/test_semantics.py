"""Independent regressions for cross-file and parser invariants."""

import copy
import tempfile
import unittest
from pathlib import Path

from scripts import check_kit as kit


class SemanticTests(unittest.TestCase):
    def test_duplicate_keys_and_nonfinite_numbers(self):
        for text in ['{"a":1,"a":2}', '{"n":NaN}', '{"n":Infinity}', '{"n":1e9999}']:
            with self.subTest(text=text), self.assertRaises(kit.InvalidKit):
                kit.parse_json(text)

    def test_valid_unicode_and_json_types(self):
        self.assertEqual(
            kit.parse_json('{"ö":[null,false,0,""]}'), {"ö": [None, False, 0, ""]}
        )

    def test_depth_limit(self):
        with self.assertRaises(kit.InvalidKit):
            kit.parse_json("[" * 65 + "0" + "]" * 65)

    def test_path_boundaries(self):
        for path in [
            "/etc/passwd",
            "../a",
            "a/../b",
            "a//b",
            "a/./b",
            "C:/a",
            "a\\b",
            "a/\x00b",
            "a/",
        ]:
            with self.subTest(path=repr(path)), self.assertRaises(kit.InvalidKit):
                kit.safe_path(path)
        self.assertEqual(kit.safe_path("src/ä file.txt"), "src/ä file.txt")

    def test_duplicate_identity_is_not_object_equality(self):
        with self.assertRaises(kit.InvalidKit):
            kit.indexed(
                [{"id": "x", "purpose": "a"}, {"id": "x", "purpose": "b"}],
                "id",
                "fixture",
            )

    def test_dependency_cycles_missing_and_diamond(self):
        good = {
            "a": {"requires": ["b", "c"]},
            "b": {"requires": ["d"]},
            "c": {"requires": ["d"]},
            "d": {"requires": []},
        }
        self.assertEqual(kit.closure(["a"], good), set(good))
        bad = copy.deepcopy(good)
        bad["d"]["requires"] = ["a"]
        with self.assertRaises(kit.InvalidKit):
            kit.closure(["a"], bad)
        with self.assertRaises(kit.InvalidKit):
            kit.closure(["missing"], good)

    def test_reference_resolution_is_offline(self):
        uri = kit.BASE + "schemas/example.schema.json"
        docs = {uri: {"$defs": {"x": {"type": "string"}}}}
        self.assertEqual(kit.resolve_schema("#/$defs/x", docs, uri), {"type": "string"})
        for ref in ["https://example.org/remote", "#/$defs/missing", "../outside"]:
            with self.subTest(ref=ref), self.assertRaises(kit.InvalidKit):
                kit.resolve_schema(ref, docs, uri)

    def test_symlink_source_rejected(self):
        with tempfile.TemporaryDirectory(prefix="kit-fixture-") as directory:
            root = Path(directory)
            (root / "real.txt").write_text("fixture", encoding="utf-8")
            (root / "linked.txt").symlink_to("real.txt")
            with self.assertRaises(kit.InvalidKit):
                kit.source_files(root)

    def test_yaml_duplicates_and_aliases(self):
        with tempfile.TemporaryDirectory(prefix="kit-yaml-") as directory:
            path = Path(directory) / "profile.yaml"
            for text in ["id: a\nid: b\n", "a: &x [1]\nb: *x\n"]:
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(kit.InvalidKit):
                    kit.read_profile(path)

    def result_fixture(self, kind):
        return next(
            copy.deepcopy(case["result"])
            for case in kit.read_json(kit.ROOT, "examples/tool-results.json")
            if case["schema_ref"].endswith("result." + kind)
        )

    def test_all_shared_result_semantics(self):
        for case in kit.read_json(kit.ROOT, "examples/tool-results.json"):
            kind = case["schema_ref"].rsplit("result.", 1)[1]
            with self.subTest(kind=kind):
                kit.result_semantics(kind, case["result"])

    def test_result_count_and_total_disagreement(self):
        for kind in ["hits", "listing", "git_status", "table", "text", "job"]:
            result = self.result_fixture(kind)
            result["coverage"]["returned"] = 0
            with self.subTest(kind=kind), self.assertRaises(kit.InvalidKit):
                kit.result_semantics(kind, result)
        for kind in ["hits", "listing"]:
            result = self.result_fixture(kind)
            result["data"]["total"] = 0
            with self.subTest(kind=kind), self.assertRaises(kit.InvalidKit):
                kit.result_semantics(kind, result)

    def test_text_utf8_window_not_character_count(self):
        result = self.result_fixture("text")
        kit.result_semantics("text", result)
        result["data"]["total_bytes"] = len(result["data"]["text"])
        with self.assertRaises(kit.InvalidKit):
            kit.result_semantics("text", result)
        result["data"]["total_bytes"] = 8
        result["data"]["offset_bytes"] = 1
        with self.assertRaises(kit.InvalidKit):
            kit.result_semantics("text", result)

    def test_reversed_anchor_and_ragged_table(self):
        result = self.result_fixture("hits")
        result["data"]["items"][0]["anchor"]["start_byte"] = 100
        with self.assertRaises(kit.InvalidKit):
            kit.result_semantics("hits", result)
        result = self.result_fixture("table")
        result["data"]["rows"][0].pop()
        with self.assertRaises(kit.InvalidKit):
            kit.result_semantics("table", result)

    def test_cursor_source_and_consuming_input(self):
        result = self.result_fixture("hits")
        result["status"] = "partial"
        result["coverage"].update(completeness="partial", truncated=True)
        with self.assertRaises(kit.InvalidKit):
            kit.result_semantics("hits", result)
        result["continuation"] = {
            "cursor": "page-two",
            "input_sha256": "0" * 64,
            "source_sha256": "0" * 64,
            "expires_at": "2026-09-13T12:00:00Z",
        }
        kit.result_semantics("hits", result, {"properties": {"cursor": {}}})
        with self.assertRaises(kit.InvalidKit):
            kit.result_semantics("hits", result, {"properties": {}})
        result["continuation"]["source_sha256"] = "1" * 64
        with self.assertRaises(kit.InvalidKit):
            kit.result_semantics("hits", result)

    def test_absent_payload_does_not_report_records(self):
        result = self.result_fixture("hits")
        result.update(
            status="error",
            data=None,
            error={
                "code": "denied",
                "message": "Synthetic denial",
                "retryable": False,
                "retry_requires": "changed_authority",
            },
        )
        with self.assertRaises(kit.InvalidKit):
            kit.result_semantics("hits", result)
        result["coverage"]["returned"] = 0
        kit.result_semantics("hits", result)

    def test_development_artifact_kinds(self):
        for path, expected in {
            "flake.nix": "nix",
            "flake.lock": "json",
            ".envrc": "shell",
            "LICENSE": "text",
            "justfile": "just",
            ".github/ISSUE_TEMPLATE/bug_report.yml": "yaml",
        }.items():
            with self.subTest(path=path):
                self.assertEqual(kit.artifact_kind(path), expected)
        with self.assertRaises(kit.InvalidKit):
            kit.artifact_kind(".env")

    def test_local_direnv_state_excluded(self):
        with tempfile.TemporaryDirectory(prefix="kit-direnv-") as directory:
            root = Path(directory)
            (root / ".envrc").write_text("use flake .#default\n", encoding="utf-8")
            state = root / ".direnv"
            state.mkdir()
            (state / "cached-state").write_text("local machine state", encoding="utf-8")
            (state / "gc-root").symlink_to(root / "missing-store-path")
            self.assertEqual(kit.source_files(root), [".envrc"])

    def test_actual_kit_semantics(self):
        data = kit.semantic_check(kit.ROOT)
        self.assertEqual(len(data["tools"]), 51)
        portable = data["profiles"]["agent-platform"]
        components = kit.indexed(
            data["inventories"]["components"]["components"], "id", "component"
        )
        result = kit.closure(
            portable["essential"] + portable["recommended"] + portable["optional"],
            components,
        )
        self.assertFalse(any(x.startswith("host.") for x in result))


if __name__ == "__main__":
    unittest.main()
