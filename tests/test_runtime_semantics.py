"""Independent cross-record contract tests, not runtime or schema proof."""

import copy
import unittest

from scripts import check_kit as kit
from scripts import runtime_contracts as runtime


class RuntimeSemanticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = kit.read_json(kit.ROOT, "examples/reference-run.json")
        cls.config = kit.read_json(kit.ROOT, "examples/agent-config.json")
        cls.controller = kit.read_json(kit.ROOT, "inventories/controller-policy.json")
        cls.tools = {
            t["name"]: t
            for t in kit.read_json(kit.ROOT, "inventories/agent-tools.json")["tools"]
        }
        cls.components = {
            c["id"]: c
            for c in kit.read_json(kit.ROOT, "inventories/components.json")[
                "components"
            ]
        }
        cls.profiles = {
            "agent-starter": kit.read_profile(kit.ROOT / "profiles/agent-starter.yaml")
        }

    def scenario(self, name="success"):
        return copy.deepcopy(
            next(s for s in self.fixture["scenarios"] if s["id"] == name)
        )

    def payload(self, scenario, kind):
        return next(e["payload"] for e in scenario["events"] if e["kind"] == kind)

    def run_case(self, scenario, config=None):
        return runtime.replay(
            self.fixture, scenario, config or self.config, self.controller
        )

    def check_config(self, config):
        return runtime.check_config(config, self.tools, self.profiles, self.components)

    def test_nine_reference_paths(self):
        self.assertEqual(len(self.fixture["scenarios"]), 9)
        for scenario in self.fixture["scenarios"]:
            with self.subTest(scenario=scenario["id"]):
                self.run_case(scenario)
        runtime.check_reference(
            kit.ROOT,
            kit.read_json,
            self.config,
            self.fixture,
            self.tools,
            self.controller,
        )

    def test_optional_means_not_activated(self):
        active = self.check_config(self.config)
        self.assertNotIn("agent.coordination", active)
        self.assertNotIn("agent.retrieval", active)
        config = copy.deepcopy(self.config)
        config["enabled_extensions"] = ["client.terminal"]
        active = self.check_config(config)
        self.assertIn("agent.observation", active)
        self.assertNotIn("agent.coordination", active)
        self.assertFalse(any(x.startswith("host.") for x in active))

    def test_config_extensions_effects_and_context(self):
        for field, value, error in [
            ("enabled_extensions", ["host.desktop"], "non-optional extension"),
            ("selected_tools", ["workspace.create"], "effectful tool"),
        ]:
            config = copy.deepcopy(self.config)
            config[field] = value
            with self.assertRaisesRegex(ValueError, error):
                self.check_config(config)
        config = copy.deepcopy(self.config)
        config["context"]["input_tokens"] = config["context"]["window_tokens"]
        with self.assertRaisesRegex(ValueError, "allocations exceed"):
            self.check_config(config)

    def test_adapter_capability_and_retention_mismatch(self):
        config = copy.deepcopy(self.config)
        config["adapter"]["resume_mode"] = "unsupported"
        with self.assertRaisesRegex(ValueError, "resume capability"):
            self.check_config(config)
        config = copy.deepcopy(self.config)
        config["storage"]["receipts_days"] = 1
        with self.assertRaisesRegex(ValueError, "retention"):
            self.check_config(config)

    def test_usage_is_disjoint_and_unknown_is_held(self):
        usage = copy.deepcopy(self.fixture["adapter_stream"][-1]["usage"])
        usage["total_tokens"] += usage["input_cached"]
        with self.assertRaisesRegex(ValueError, "disjoint totals"):
            runtime.check_usage(usage)
        result = self.run_case(self.scenario("model-timeout"))
        self.assertEqual((result["spent_tokens"], result["held_tokens"]), (0, 1536))

    def test_token_and_cost_exhaustion_before_model(self):
        for key, message in [
            ("tokens", "token budget exhausted"),
            ("microcredits", "cost budget exhausted"),
        ]:
            scenario = self.scenario()
            self.payload(scenario, "reserve")[key] = 1000000000
            with self.assertRaisesRegex(ValueError, message):
                self.run_case(scenario)

    def test_model_requires_unused_adequate_reservation(self):
        for key, value, message in [
            ("reservation_id", "foreign", "unused reservation"),
            ("input_token_bound", 2000, "under-reserved"),
            ("model_binding_id", "foreign", "foreign model binding"),
        ]:
            scenario = self.scenario()
            self.payload(scenario, "model")[key] = value
            with self.assertRaisesRegex(ValueError, message):
                self.run_case(scenario)

    def test_call_and_time_limits(self):
        config = copy.deepcopy(self.config)
        config["budget"]["max_model_calls"] = 0
        with self.assertRaisesRegex(ValueError, "model call limit"):
            self.run_case(self.scenario(), config)
        config = copy.deepcopy(self.config)
        config["budget"]["deadline_seconds"] = 1
        with self.assertRaisesRegex(ValueError, "run deadline"):
            self.run_case(self.scenario(), config)

    def test_no_model_turn_during_external_wait(self):
        scenario = self.scenario("model-timeout")
        last = scenario["events"][-1]
        scenario["events"].append(
            dict(
                last,
                sequence=last["sequence"] + 1,
                kind="model",
                payload=copy.deepcopy(self.fixture["adapter_request"]),
            )
        )
        with self.assertRaisesRegex(ValueError, "model turn during wait"):
            self.run_case(scenario)

    def test_approval_guard_revalidates(self):
        for key, value in [
            ("decision", "denied"),
            ("expires_at", "2026-09-12T00:00:00Z"),
            ("grant_digest", "0" * 64),
        ]:
            scenario = self.scenario()
            self.payload(scenario, "approval")[key] = value
            with self.assertRaisesRegex(ValueError, "approval guard"):
                self.run_case(scenario)

    def test_dispatch_scope_input_and_binding(self):
        for key, value, message in [
            ("workspace_id", "foreign", "foreign dispatch workspace"),
            ("binding_digest", "0" * 64, "stale binding"),
            ("run_id", "foreign", "foreign grant run"),
        ]:
            scenario = self.scenario()
            self.payload(scenario, "dispatch")[key] = value
            with self.assertRaisesRegex(ValueError, message):
                self.run_case(scenario)
        scenario = self.scenario()
        self.payload(scenario, "dispatch")["input_artifact"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "changed input"):
            self.run_case(scenario)

    def test_grant_single_use(self):
        scenario = self.scenario()
        dispatch = self.payload(scenario, "dispatch")
        approval = self.payload(scenario, "approval")
        with self.assertRaisesRegex(ValueError, "grant replay"):
            runtime.authorize(
                dispatch,
                self.fixture["grant"],
                approval,
                self.fixture["binding"],
                self.fixture["run"],
                runtime.instant("2026-09-13T00:00:09Z"),
                1,
            )

    def test_receipt_scope_and_completion_evidence(self):
        scenario = self.scenario()
        self.payload(scenario, "receipt")["verification"] = []
        with self.assertRaisesRegex(ValueError, "completion without evidence"):
            self.run_case(scenario)
        scenario = self.scenario()
        self.payload(scenario, "receipt")["identity"]["source_digest"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "stale receipt"):
            self.run_case(scenario)
        scenario = self.scenario()
        self.payload(scenario, "receipt")["verification"][0]["level"] = "source"
        with self.assertRaisesRegex(ValueError, "insufficient evidence"):
            self.run_case(scenario)

    def test_no_terminal_state_hides_pending_call(self):
        scenario = self.scenario("tool-timeout")
        scenario["events"][-1]["payload"] = {
            "to": "CANCELLED",
            "guard": "failure_or_cancellation",
        }
        with self.assertRaisesRegex(ValueError, "conceals uncertain effect"):
            self.run_case(scenario)

    def test_duplicate_delivery_and_conflicting_replay(self):
        self.run_case(self.scenario("restart-resume"))
        scenario = self.scenario("restart-resume")
        scenario["events"][2]["payload"]["to"] = "FAILED"
        with self.assertRaisesRegex(ValueError, "conflicting duplicate"):
            self.run_case(scenario)

    def test_event_gap_and_foreign_run(self):
        for key, value, message in [
            ("sequence", 5, "sequence gap"),
            ("run_id", "foreign", "foreign event"),
        ]:
            scenario = self.scenario()
            scenario["events"][0][key] = value
            with self.assertRaisesRegex(ValueError, message):
                self.run_case(scenario)

    def test_resume_rejects_lost_pending_work_and_identity(self):
        for key, value, message in [
            ("pending_calls", [], "drops pending"),
            ("last_sequence", 0, "stale resume cursor"),
            ("open_requirements", [], "drops requirements"),
            ("next_action", "execute", "must reconcile"),
        ]:
            scenario = self.scenario("restart-resume")
            self.payload(scenario, "checkpoint")[key] = value
            with self.assertRaisesRegex(ValueError, message):
                self.run_case(scenario)
        scenario = self.scenario("restart-resume")
        self.payload(scenario, "checkpoint")["identity"]["policy_digest"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "stale resume identity"):
            self.run_case(scenario)

    def test_restart_rejects_changed_checkpoint(self):
        scenario = self.scenario("restart-resume")
        self.payload(scenario, "restart")["checkpoint_digest"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "checkpoint digest"):
            self.run_case(scenario)

    def test_stream_correlation_finish_and_duplicates(self):
        request = self.fixture["adapter_request"]
        for key, value, message in [
            ("request_id", "foreign", "foreign stream request"),
            ("sequence", 9, "stream sequence gap"),
            ("tool", "workspace.create", "unselected stream tool"),
        ]:
            stream = copy.deepcopy(self.fixture["adapter_stream"])
            stream[0][key] = value
            with self.assertRaisesRegex(ValueError, message):
                runtime.check_stream(request, stream)
        stream = copy.deepcopy(self.fixture["adapter_stream"])
        stream[-1]["reason"] = "stop"
        with self.assertRaisesRegex(ValueError, "finish reason"):
            runtime.check_stream(request, stream)
        stream = copy.deepcopy(self.fixture["adapter_stream"])
        stream.append(dict(stream[-1], sequence=3))
        with self.assertRaisesRegex(ValueError, "after settlement"):
            runtime.check_stream(request, stream)

    def test_adapter_error_classification(self):
        request = self.fixture["adapter_request"]
        event = {
            "request_id": request["request_id"],
            "sequence": 1,
            "kind": "error",
            "code": "authentication",
            "retryable": False,
            "usage": {"known": False, "reason": "unavailable"},
        }
        runtime.check_stream(request, [event])
        event["retryable"] = True
        with self.assertRaisesRegex(ValueError, "deterministic adapter error"):
            runtime.check_stream(request, [event])

    def test_revoked_grant_is_not_authority(self):
        scenario = self.scenario()
        grant = dict(self.fixture["grant"], state="revoked")
        with self.assertRaisesRegex(ValueError, "grant revoked"):
            runtime.authorize(
                self.payload(scenario, "dispatch"),
                grant,
                self.payload(scenario, "approval"),
                self.fixture["binding"],
                self.fixture["run"],
                runtime.instant("2026-09-13T00:00:09Z"),
                0,
            )

    def test_changed_task_invalidates_run(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["task"]["requirements"][0]["minimum_level"] = "source"
        with self.assertRaisesRegex(ValueError, "task digest mismatch"):
            runtime.replay(fixture, self.scenario(), self.config, self.controller)

    def test_reservation_id_cannot_be_reused_after_settlement(self):
        scenario = self.scenario("budget-exhausted")
        reserves = [e["payload"] for e in scenario["events"] if e["kind"] == "reserve"]
        reserves[1]["reservation_id"] = reserves[0]["reservation_id"]
        with self.assertRaisesRegex(ValueError, "duplicate reservation"):
            self.run_case(scenario)

    def test_receipt_cannot_predate_dispatch(self):
        scenario = self.scenario()
        self.payload(scenario, "receipt")["settled_at"] = "2026-09-13T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "outside dispatch window"):
            self.run_case(scenario)


if __name__ == "__main__":
    unittest.main()
