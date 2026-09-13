"""Behavioral tests for the temporary helper, runnable without platform services."""

import contextlib
import copy
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HELPERS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HELPERS))

import bootstrap as app  # noqa: E402
import bootstrap_checks as checks  # noqa: E402
import bootstrap_evidence as evidence  # noqa: E402


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="bootstrap-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "clone"
        self.root.mkdir()
        (self.root / ".agents").mkdir()
        (self.root / "src").mkdir()
        (self.root / "tests").mkdir()
        for name in ("bootstrap.py", "bootstrap_checks.py", "bootstrap_evidence.py"):
            shutil.copyfile(HELPERS / name, self.root / ".agents" / name)
        (self.root / "contract.txt").write_text("account_id", encoding="utf-8")
        (self.root / "src/producer.json").write_text(
            '{"account_id": 7}', encoding="utf-8"
        )
        (self.root / "tests/consumer.py").write_text(
            "import json\nfrom pathlib import Path\n"
            "value = json.loads(Path('src/producer.json').read_text())\n"
            "assert value['account_id'] == 7, 'wrong account'\nprint('verified real value')\n",
            encoding="utf-8",
        )
        self.state = self.base / "state"
        self.plan = {
            "format": "bootstrap-plan-v1",
            "target": "Synthetic test target",
            "shared_inputs": [
                ".agents/bootstrap.py",
                ".agents/bootstrap_evidence.py",
                ".agents/bootstrap_checks.py",
                "toolchain.json",
            ],
            "tasks": [
                {
                    "id": "first",
                    "title": "Check producer and consumer",
                    "depends_on": [],
                    "refs": ["contract.txt"],
                    "acceptance": ["Consumer reads account_id=7 from actual producer"],
                    "checks": [
                        {
                            "id": "contract",
                            "argv": ["python3", "-B", "tests/consumer.py"],
                            "inputs": ["contract.txt", "src", "tests"],
                            "level": "focused-test",
                            "timeout_seconds": 2,
                        }
                    ],
                }
            ],
        }
        self.write_plan()

    def write_plan(self):
        (self.root / ".agents/work-items.json").write_text(
            json.dumps(self.plan), encoding="utf-8"
        )

    def rows(self):
        plan, tasks, order = app.load_plan(self.root)
        return app.report(self.root, plan, tasks, order, self.state)

    def verify(self):
        plan, tasks, order = app.load_plan(self.root)
        return app.verify(
            self.root,
            plan,
            tasks,
            app.report(self.root, plan, tasks, order, self.state),
            self.state,
            "first",
            "contract",
        )

    def test_fresh_session_and_no_implicit_execution(self):
        self.assertEqual(self.rows()[0]["checks"][0]["status"], "not-run")
        self.assertFalse(self.state.exists())
        with contextlib.redirect_stdout(io.StringIO()) as stream:
            code = app.main(
                ["--root", str(self.root), "--state-dir", str(self.state), "resume"]
            )
        self.assertEqual(code, 0)
        projection = json.loads(stream.getvalue())
        self.assertEqual(projection["ready"], ["first"])
        self.assertIn("source_sha256", projection)
        self.assertFalse(self.state.exists())

    @unittest.skipUnless(os.name == "posix", "POSIX execution required")
    def test_positive_negative_behavior_and_reuse(self):
        result = self.verify()
        self.assertEqual(result["status"], "passed")
        self.assertEqual(self.rows()[0]["status"], "checks-passed")
        # A fresh process can recover the source-bound observation.
        fresh = checks.run_check(
            [
                sys.executable,
                "-B",
                str(HELPERS / "bootstrap.py"),
                "--root",
                str(self.root),
                "--state-dir",
                str(self.state),
                "next",
            ],
            self.root,
            evidence.environment(),
            3,
        )
        self.assertEqual(fresh["status"], "passed")
        self.assertEqual(
            json.loads(fresh["output_tail"])["tasks"][0]["status"], "checks-passed"
        )
        (self.root / "src/producer.json").write_text('{"id": 7}')
        self.assertEqual(self.rows()[0]["checks"][0]["status"], "stale")
        failed = self.verify()
        self.assertEqual(failed["status"], "failed")
        self.assertNotEqual(failed["exit_code"], 0)
        self.assertIn("KeyError", failed["output_tail"])
        (self.root / "src/producer.json").write_text('{"account_id": 7}')
        self.assertEqual(self.verify()["status"], "passed")

    @unittest.skipUnless(os.name == "posix", "POSIX execution required")
    def test_add_delete_contract_and_environment_change(self):
        self.verify()
        original = copy.deepcopy(self.plan)
        for path in ("src/new.json", "toolchain.json", "contract.txt"):
            target = self.root / path
            previous = target.read_bytes() if target.exists() else None
            target.write_text("changed")
            self.assertEqual(self.rows()[0]["checks"][0]["status"], "stale")
            if previous is None:
                target.unlink()
            else:
                target.write_bytes(previous)
            self.assertEqual(self.rows()[0]["status"], "checks-passed")
        self.plan["tasks"][0]["acceptance"] = ["Changed reviewed requirement"]
        self.write_plan()
        self.assertEqual(self.rows()[0]["checks"][0]["status"], "stale")
        self.plan = original
        self.write_plan()
        with patch.dict(os.environ, {"PATH": "/different/path"}):
            self.assertEqual(self.rows()[0]["checks"][0]["status"], "stale")

    def test_dependencies_cycle_unknown_and_unconfigured(self):
        second = copy.deepcopy(self.plan["tasks"][0])
        second.update(id="second", depends_on=["first"])
        second["checks"][0]["argv"] = None
        self.plan["tasks"].append(second)
        self.write_plan()
        self.assertEqual(self.rows()[1]["status"], "waiting")
        self.plan["tasks"][0]["depends_on"] = ["second"]
        self.write_plan()
        with self.assertRaisesRegex(evidence.Invalid, "cycle"):
            self.rows()
        self.plan["tasks"][0]["depends_on"] = ["missing"]
        self.write_plan()
        with self.assertRaisesRegex(evidence.Invalid, "unknown dependency"):
            self.rows()

    @unittest.skipUnless(os.name == "posix", "POSIX execution required")
    def test_stale_dependency_blocks_current_child(self):
        self.verify()
        second = copy.deepcopy(self.plan["tasks"][0])
        second.update(id="second", depends_on=["first"])
        self.plan["tasks"].append(second)
        self.write_plan()
        plan, tasks, order = app.load_plan(self.root)
        app.verify(
            self.root,
            plan,
            tasks,
            app.report(self.root, plan, tasks, order, self.state),
            self.state,
            "second",
            "contract",
        )
        self.assertEqual(self.rows()[1]["status"], "checks-passed")
        self.plan["tasks"][0]["acceptance"] = ["Changed parent"]
        self.write_plan()
        self.assertEqual(self.rows()[1]["status"], "waiting")
        self.verify()
        self.assertEqual(self.rows()[1]["checks"][0]["status"], "stale")

    def test_unsafe_inputs_and_state(self):
        for name in ("/etc/passwd", "../outside", "a/../b", "a//b"):
            with self.subTest(name=name), self.assertRaises(evidence.Invalid):
                evidence.local_path(self.root, name)
        for path in (self.root, self.root / ".agents/state", self.base):
            with self.assertRaises(evidence.Invalid):
                evidence.state_directory(self.root, str(path))
        (self.root / "src/link").symlink_to(self.base / "missing")
        with self.assertRaisesRegex(evidence.Invalid, "symlink"):
            self.rows()

    @unittest.skipUnless(os.name == "posix", "POSIX execution required")
    def test_malformed_or_contradictory_record_not_success(self):
        self.verify()
        path = evidence.record_path(self.state, "first", "contract")
        data = json.loads(path.read_text())
        data["exit_code"] = 9
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(evidence.Invalid, "contradictory"):
            self.rows()
        path.write_text("{broken")
        with self.assertRaises(ValueError):
            self.rows()
        for malformed in ([], {"binding": []}, {"binding": {"inputs": []}}):
            path.write_text(json.dumps(malformed))
            with self.assertRaises(evidence.Invalid):
                self.rows()

    def test_virtual_environment_interpreter_path_is_preserved(self):
        bin_dir = self.base / "venv/bin"
        bin_dir.mkdir(parents=True)
        invocation = bin_dir / "python3"
        invocation.symlink_to(sys.executable)
        with patch.object(sys, "executable", str(invocation)):
            self.assertEqual(
                evidence.executable({"argv": ["python3", "-B"]}), str(invocation)
            )

    @unittest.skipUnless(os.name == "posix", "POSIX execution required")
    def test_change_during_check_never_passes(self):
        self.plan["tasks"][0]["checks"][0]["argv"] = [
            "python3",
            "-c",
            "from pathlib import Path; Path('contract.txt').write_text('changed')",
        ]
        self.write_plan()
        self.assertEqual(self.verify()["status"], "inputs-changed")

    @unittest.skipUnless(os.name == "posix", "POSIX execution required")
    def test_timeout_output_bounds_cancellation_and_environment(self):
        def run(script, timeout=2):
            return checks.run_check(
                [sys.executable, "-c", script],
                self.root,
                evidence.environment(),
                timeout,
            )

        self.assertEqual(run("import time; time.sleep(10)", 1)["status"], "timeout")
        large = run("import sys; sys.stdout.write('x' * 1100000)")
        self.assertEqual(large["status"], "output-limit")
        self.assertLessEqual(large["output_bytes"], checks.MAX_OUTPUT + 1)
        self.assertLessEqual(len(large["output_tail"]), 4096)
        with patch.dict(os.environ, {"BOOTSTRAP_TEST_SECRET": "synthetic"}):
            self.assertEqual(
                run("import os; assert 'BOOTSTRAP_TEST_SECRET' not in os.environ")[
                    "status"
                ],
                "passed",
            )
        with patch(
            "selectors.EpollSelector.select"
            if sys.platform.startswith("linux")
            else "selectors.DefaultSelector.select",
            side_effect=KeyboardInterrupt,
        ):
            self.assertEqual(run("import time; time.sleep(10)")["status"], "cancelled")

    def test_retirement_does_not_delete(self):
        result = app.retirement(self.root, self.rows())
        self.assertEqual(result["status"], "not-ready")
        self.assertTrue((self.root / ".agents/bootstrap.py").exists())

    def test_malformed_plan_is_reported_without_traceback(self):
        self.plan["tasks"][0]["refs"] = [7]
        self.write_plan()
        with contextlib.redirect_stderr(io.StringIO()) as stream:
            result = app.main(["--root", str(self.root), "next"])
        self.assertEqual(result, 1)
        self.assertEqual(json.loads(stream.getvalue())["status"], "invalid")

    def test_real_backlog_and_temporary_skill(self):
        from scripts import check_skills

        entry = check_skills.skill_entry(
            HELPERS / "skills/platform-build", HELPERS.parent
        )
        self.assertEqual(entry["name"], "platform-build")
        plan, tasks, order = app.load_plan(HELPERS.parent)
        self.assertEqual(len(tasks), 15)
        self.assertEqual(order[0], "kit-baseline")
        self.assertIn("web", plan["target"])
        self.assertTrue(
            all(
                c["argv"] is None for t in list(tasks.values())[1:] for c in t["checks"]
            )
        )


if __name__ == "__main__":
    unittest.main()
