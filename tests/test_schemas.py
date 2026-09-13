"""Full Draft 2020-12 acceptance tests; missing validator is an error, never a skip."""

import copy
import unittest

from scripts import check_kit as kit


class SchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jsonschema, referencing = kit.validator_environment()
        cls.data = kit.semantic_check(kit.ROOT)
        cls.registry = referencing.Registry().with_resources(
            [
                (uri, referencing.Resource.from_contents(doc))
                for uri, doc in cls.data["schemas"].items()
            ]
        )
        cls.examples = kit.read_json(kit.ROOT, "examples/tool-inputs.json")
        cls.checker = kit.format_checker(cls.jsonschema)
        cls.outputs = kit.read_json(kit.ROOT, "examples/tool-results.json")

    def validator(self, ref):
        # Keep the parent $id so local definitions resolve in their own resource.
        schema = {"$schema": kit.DIALECT, "$ref": kit.BASE + ref}
        return self.jsonschema.Draft202012Validator(
            schema, registry=self.registry, format_checker=self.checker
        )

    def test_every_tool_input_and_unknown_field(self):
        self.assertEqual({x["tool"] for x in self.examples}, set(self.data["tools"]))
        for case in self.examples:
            with self.subTest(tool=case["tool"]):
                validator = self.validator(
                    self.data["tools"][case["tool"]]["input_schema"]
                )
                validator.validate(case["input"])
                invalid = dict(case["input"], invented_authority=True)
                self.assertFalse(validator.is_valid(invalid))
                schema = kit.resolve_schema(
                    self.data["tools"][case["tool"]]["input_schema"],
                    self.data["schemas"],
                )
                for required in schema["required"]:
                    missing = dict(case["input"])
                    del missing[required]
                    self.assertFalse(validator.is_valid(missing))

    def test_excess_limits_paths_and_types(self):
        validator = self.validator(self.data["tools"]["workspace.read"]["input_schema"])
        good = next(x["input"] for x in self.examples if x["tool"] == "workspace.read")
        for field, value in [
            ("max_bytes", 16385),
            ("max_bytes", True),
            ("offset_bytes", -1),
            ("path", "../secret"),
            ("path", "/etc/passwd"),
            ("expected_sha256", "not-a-digest"),
        ]:
            invalid = dict(good)
            invalid[field] = value
            with self.subTest(field=field, value=value):
                self.assertFalse(validator.is_valid(invalid))

    def result(self):
        digest = "0" * 64
        return {
            "status": "ok",
            "data": {"items": [], "total": 0},
            "error": None,
            "coverage": {
                "scope": "exhaustive",
                "completeness": "complete",
                "freshness": "current",
                "returned": 0,
                "truncated": False,
            },
            "provenance": {
                "call_id": "call",
                "source_sha256": digest,
                "definition_sha256": digest,
                "policy_sha256": digest,
                "toolchain_sha256": None,
                "elapsed_ms": 0,
            },
            "continuation": None,
            "artifact": None,
        }

    def test_composed_result_is_closed(self):
        validator = self.validator(
            self.data["tools"]["workspace.search"]["output_schema"]
        )
        result = self.result()
        validator.validate(result)
        result["unexpected"] = True
        self.assertFalse(validator.is_valid(result))
        result = self.result()
        result["data"]["unexpected"] = True
        self.assertFalse(validator.is_valid(result))

    def test_empty_partial_is_not_no_match(self):
        validator = self.validator(
            self.data["tools"]["workspace.search"]["output_schema"]
        )
        result = self.result()
        result["status"] = "no_match"
        validator.validate(result)
        result["coverage"]["completeness"] = "partial"
        self.assertFalse(validator.is_valid(result))
        result["status"] = "partial"
        validator.validate(result)
        result["status"] = "no_match"
        result["coverage"]["completeness"] = "complete"
        for field, value in [
            ("scope", "ranked"),
            ("freshness", "stale"),
            ("returned", 1),
        ]:
            invalid = dict(result, coverage=dict(result["coverage"], **{field: value}))
            self.assertFalse(validator.is_valid(invalid))

    def test_error_and_uncertain_are_not_success(self):
        validator = self.validator(
            self.data["tools"]["workspace.search"]["output_schema"]
        )
        result = self.result()
        result["status"] = "error"
        self.assertFalse(validator.is_valid(result))
        result["data"] = None
        result["error"] = {
            "code": "denied",
            "message": "outside grant",
            "retryable": False,
            "retry_requires": "changed_authority",
        }
        validator.validate(result)
        result["status"] = "outcome_uncertain"
        self.assertFalse(validator.is_valid(result))
        result["error"].update(
            code="outcome_uncertain",
            retryable=False,
            retry_requires="reconcile_outcome",
        )
        validator.validate(result)
        result["error"]["retryable"] = True
        self.assertFalse(validator.is_valid(result))

    def test_all_result_shapes_and_tool_bindings(self):
        outputs = {case["schema_ref"]: case["result"] for case in self.outputs}
        self.assertEqual(
            set(outputs),
            {tool["output_schema"] for tool in self.data["tools"].values()},
        )
        for tool in self.data["tools"].values():
            with self.subTest(tool=tool["name"]):
                ref = tool["output_schema"]
                validator = self.validator(ref)
                result = copy.deepcopy(outputs[ref])
                validator.validate(result)
                result["unexpected"] = True
                self.assertFalse(validator.is_valid(result))
                result = copy.deepcopy(outputs[ref])
                result["data"]["unexpected"] = True
                self.assertFalse(validator.is_valid(result))
                for field in outputs[ref]:
                    invalid = copy.deepcopy(outputs[ref])
                    del invalid[field]
                    self.assertFalse(validator.is_valid(invalid))

    def test_cursor_inputs_and_result_round_trip(self):
        cursor = {
            "cursor": "page-two",
            "input_sha256": "0" * 64,
            "source_sha256": "0" * 64,
            "expires_at": "2026-09-13T12:00:00Z",
        }
        for case in self.examples:
            ref = self.data["tools"][case["tool"]]["input_schema"]
            schema = kit.resolve_schema(ref, self.data["schemas"])
            validator = self.validator(ref)
            candidate = dict(case["input"], cursor=cursor)
            with self.subTest(tool=case["tool"]):
                if "cursor" in schema["properties"]:
                    validator.validate(candidate)
                    invalid = dict(candidate, cursor=dict(cursor, input_sha256="bad"))
                    self.assertFalse(validator.is_valid(invalid))
                else:
                    self.assertFalse(validator.is_valid(candidate))
        result = self.result()
        result["status"] = "partial"
        result["coverage"].update(completeness="partial", truncated=True)
        result["continuation"] = cursor
        validator = self.validator(
            self.data["tools"]["workspace.search"]["output_schema"]
        )
        validator.validate(result)
        for status in ["ok", "no_match"]:
            self.assertFalse(validator.is_valid(dict(result, status=status)))
        result["continuation"]["expires_at"] = "2026-02-30T12:00:00Z"
        self.assertFalse(validator.is_valid(result))

    def test_settled_process_has_exactly_one_exit_kind(self):
        case = next(
            x for x in self.outputs if x["schema_ref"].endswith("result.process")
        )
        validator = self.validator(case["schema_ref"])
        result = copy.deepcopy(case["result"])
        validator.validate(result)
        result["data"]["signal"] = 15
        self.assertFalse(validator.is_valid(result))
        result["data"]["exit_code"] = None
        validator.validate(result)
        result["data"]["signal"] = None
        self.assertFalse(validator.is_valid(result))

    def test_successful_build_requires_result_artifact(self):
        case = next(x for x in self.outputs if x["schema_ref"].endswith("result.job"))
        validator = self.validator(case["schema_ref"])
        result = copy.deepcopy(case["result"])
        validator.validate(result)
        result["data"]["result"] = None
        self.assertFalse(validator.is_valid(result))
        for state in ["queued", "running", "failed", "cancelled", "outcome_uncertain"]:
            result["data"]["state"] = state
            validator.validate(result)
            invalid = copy.deepcopy(result)
            invalid["data"]["result"] = case["result"]["data"]["result"]
            self.assertFalse(validator.is_valid(invalid))

    def test_format_assertion_and_missing_external_ref(self):
        checker = self.jsonschema.Draft202012Validator(
            {"type": "string", "format": "date"}, format_checker=self.checker
        )
        self.assertFalse(checker.is_valid("2026-02-30"))
        from referencing.exceptions import Unresolvable

        with self.assertRaises(Unresolvable):
            self.registry.resolver().lookup("https://unavailable.invalid/schema")

    def test_all_inventory_and_profile_schemas(self):
        kit.full_schema_check(kit.ROOT, self.data)


if __name__ == "__main__":
    unittest.main()
