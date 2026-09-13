"""Host-independent build assistance. No runtime, model calls or agent launcher."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

from bootstrap_checks import run_check
from bootstrap_evidence import (
    IDENTIFIER,
    Invalid,
    binding,
    check_status,
    digest,
    environment,
    inputs,
    local_path,
    read_json,
    require,
    save_record,
    state_directory,
    versions,
)

ROOT = Path(__file__).resolve().parents[1]


def load_plan(root):
    plan = read_json(root / ".agents/work-items.json")
    require(isinstance(plan, dict), "plan must be an object")
    require(
        set(plan) == {"format", "target", "shared_inputs", "tasks"},
        "invalid plan fields",
    )
    require(plan["format"] == "bootstrap-plan-v1", "unsupported plan format")
    require(
        isinstance(plan["target"], str) and 0 < len(plan["target"]) < 1024,
        "invalid target",
    )
    require(
        isinstance(plan["shared_inputs"], list) and plan["shared_inputs"],
        "missing shared inputs",
    )
    require(
        isinstance(plan["tasks"], list) and 0 < len(plan["tasks"]) <= 40,
        "invalid task count",
    )
    tasks = {}
    for task in plan["tasks"]:
        require(isinstance(task, dict), "task must be an object")
        require(
            set(task) == {"id", "title", "depends_on", "refs", "acceptance", "checks"},
            "invalid task fields",
        )
        require(
            isinstance(task["id"], str) and IDENTIFIER.fullmatch(task["id"]),
            "invalid task ID",
        )
        require(task["id"] not in tasks, f"duplicate task: {task['id']}")
        for field in ("refs", "acceptance", "checks"):
            require(
                isinstance(task[field], list) and task[field], f"missing task {field}"
            )
        require(
            isinstance(task["title"], str) and 0 < len(task["title"]) < 256,
            "invalid title",
        )
        require(
            all(isinstance(x, str) and 0 < len(x) < 2048 for x in task["acceptance"]),
            "invalid acceptance",
        )
        require(
            isinstance(task["depends_on"], list)
            and all(isinstance(x, str) for x in task["depends_on"]),
            "invalid dependencies",
        )
        require(
            len(set(task["depends_on"])) == len(task["depends_on"]),
            "duplicate dependency",
        )
        for ref in task["refs"]:
            require(isinstance(ref, str), "task reference must be a string")
            require(
                local_path(root, ref.split("#", 1)[0]).is_file(),
                f"missing task reference: {ref}",
            )
        seen = set()
        for check in task["checks"]:
            require(isinstance(check, dict), "check must be an object")
            require(
                set(check) == {"id", "argv", "inputs", "level", "timeout_seconds"},
                "invalid check fields",
            )
            require(
                isinstance(check["id"], str) and IDENTIFIER.fullmatch(check["id"]),
                "invalid check ID",
            )
            require(check["id"] not in seen, "duplicate check")
            seen.add(check["id"])
            require(
                check["level"] in {"source", "focused-test", "build", "live"},
                "invalid evidence level",
            )
            require(
                type(check["timeout_seconds"]) is int
                and 1 <= check["timeout_seconds"] <= 1800,
                "invalid timeout",
            )
            require(
                isinstance(check["inputs"], list) and check["inputs"],
                "missing check inputs",
            )
            for name in plan["shared_inputs"] + check["inputs"]:
                if name != ".":
                    local_path(root, name)
            argv = check["argv"]
            require(
                argv is None
                or (
                    isinstance(argv, list)
                    and 0 < len(argv) <= 64
                    and all(isinstance(x, str) and x and "\x00" not in x for x in argv)
                    and sum(len(x.encode()) for x in argv) <= 8192
                    and re.fullmatch(r"[A-Za-z0-9_.+-]+", argv[0])
                ),
                "invalid argv; use a named executable and explicit arguments",
            )
        tasks[task["id"]] = task
    order, active = [], set()

    def visit(identity):
        require(identity in tasks, f"unknown dependency: {identity}")
        require(identity not in active, f"dependency cycle: {identity}")
        if identity in order:
            return
        active.add(identity)
        for dep in tasks[identity]["depends_on"]:
            visit(dep)
        active.remove(identity)
        order.append(identity)

    for identity in tasks:
        visit(identity)
    return plan, tasks, order


def report(root, plan, tasks, order, state):
    rows, passed = [], set()
    for identity in order:
        task = tasks[identity]
        checks = [
            check_status(root, plan, task, check, state) for check in task["checks"]
        ]
        missing = [dep for dep in task["depends_on"] if dep not in passed]
        status = "waiting" if missing else "ready"
        if not missing and all(c["status"] == "passed" for c in checks):
            status = "checks-passed"
            passed.add(identity)
        rows.append(
            {
                "id": identity,
                "status": status,
                "dependencies_pending": missing,
                "checks": checks,
            }
        )
    return rows


def doctor(root, plan):
    requirements = {}
    actual = versions()
    for line in (root / "requirements.txt").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            name, expected = line.strip().split("==")
            found = actual["packages"].get(name)
            requirements[name] = {
                "expected": expected,
                "actual": found,
                "matches": found == expected,
            }
    tools = {
        name: shutil.which(name) is not None
        for name in ("python3", "just", "ruff", "shellcheck", "nixfmt")
    }
    return {
        "status": "ready"
        if all(x["matches"] for x in requirements.values()) and all(tools.values())
        else "blocked",
        "bootstrap_reader": "ready",
        "versions": actual,
        "requirements": requirements,
        "tools": tools,
        "target": plan["target"],
        "scope": "environment inspection only; no checks or host capability probes executed",
        "next_action": "Provision missing pinned check inputs through your host; do not install during checks.",
    }


def verify(root, plan, tasks, rows, state, task_id, check_id):
    require(state is not None, "verify requires --state-dir outside the clone")
    require(task_id in tasks, f"unknown task: {task_id}")
    task = tasks[task_id]
    row = next(r for r in rows if r["id"] == task_id)
    require(not row["dependencies_pending"], "verify dependencies first")
    check = next((c for c in task["checks"] if c["id"] == check_id), None)
    require(check is not None, f"unknown check: {check_id}")
    require(
        check["argv"] is not None,
        "unconfigured check: bind a reviewed real implementation check first",
    )
    before = binding(root, plan, task, check)
    if before["executable"] is None:
        return {"status": "blocked", "reason": "executable unavailable"}
    argv = [before["executable"]["path"], *check["argv"][1:]]
    result = run_check(argv, root, environment(), check["timeout_seconds"])
    # The check itself may have changed source or its own declaration.
    try:
        after_plan, after_tasks, _ = load_plan(root)
        after_task = after_tasks[task_id]
        after_check = next(c for c in after_task["checks"] if c["id"] == check_id)
        unchanged = before == binding(root, after_plan, after_task, after_check)
    except (Invalid, OSError, ValueError, KeyError, StopIteration):
        unchanged = False
    if not unchanged:
        result["status"] = "inputs-changed"
    record = {
        "format": "bootstrap-observation-v1",
        "task": task_id,
        "check": check_id,
        "observed_at": datetime.now(UTC).isoformat(),
        "binding": before,
        "binding_sha256": digest(before),
        **{k: v for k, v in result.items() if k != "output_tail"},
    }
    save_record(state, task_id, check_id, record)
    return {"task": task_id, "check": check_id, **result}


def retirement(root, rows):
    references = []
    expected = {
        "AGENTS.md",
        "README.md",
        "DEVELOPMENT.md",
        "VERIFICATION.md",
        "justfile",
        "manifest.json",
    }
    for name, value in inputs(root, ["."]).items():
        if value in {None, "directory"} or name.startswith(".agents/"):
            continue
        path = local_path(root, name)
        if ".agents/" in path.read_text(encoding="utf-8", errors="replace"):
            references.append(name)
    pending = [r["id"] for r in rows if r["status"] != "checks-passed"]
    blockers = sorted(set(references) - expected)
    return {
        "status": "eligible-for-review"
        if not pending and not blockers
        else "not-ready",
        "pending_tasks": pending,
        "permanent_dependency_references": blockers,
        "integration_edits": sorted(set(references) & expected),
        "action": "Review retirement.md, transfer required evidence, then explicitly remove temporary integration. Nothing deleted.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--state-dir")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("doctor", "next", "resume", "retirement-check"):
        commands.add_parser(name)
    check = commands.add_parser("verify")
    check.add_argument("task")
    check.add_argument("check")
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve(strict=True)
        state = state_directory(root, args.state_dir)
        plan, tasks, order = load_plan(root)
        if args.command == "doctor":
            output = doctor(root, plan)
        else:
            rows = report(root, plan, tasks, order, state)
            ready = [r["id"] for r in rows if r["status"] == "ready"]
            if args.command == "verify":
                output = verify(root, plan, tasks, rows, state, args.task, args.check)
            elif args.command == "retirement-check":
                output = retirement(root, rows)
            else:
                output = {
                    "format": "bootstrap-projection-v1",
                    "target": plan["target"],
                    "plan_sha256": digest(plan),
                    "ready": ready,
                    "tasks": rows,
                    "next_action": f"Read work item {ready[0]} and configure/run its checks."
                    if ready
                    else "Review unresolved evidence or retirement readiness.",
                    "scope": "local observations; not authenticated platform evidence",
                }
                if args.command == "resume":
                    output["source_sha256"] = digest(inputs(root, ["."]))
                    output["handoff_template"] = ".agents/templates/handoff.md"
        print(json.dumps(output, indent=2, sort_keys=True))
        return (
            0
            if output.get("status") in {None, "ready", "passed", "eligible-for-review"}
            else 2
        )
    except (Invalid, OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        print(json.dumps({"status": "invalid", "reason": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
