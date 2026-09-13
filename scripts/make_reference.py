"""Rebuild synthetic replay fixtures after reviewed contract/example changes."""

from copy import deepcopy

from check_kit import ROOT, read_json
from runtime_contracts import digest, encoded, schema_digest

BASE = "https://architecture-kit.invalid/schemas/"
AT = "2026-09-13T00:00:"
EXPIRES = "2026-09-13T00:10:00Z"


def artifact(identity, value):
    return {
        "id": identity,
        "sha256": digest(value),
        "media_type": "application/json",
        "size_bytes": len(encoded(value)),
    }


def build_reference():
    config = read_json(ROOT, "examples/agent-config.json")
    catalog = read_json(ROOT, "inventories/agent-tools.json")["tools"]
    tool = next(t for t in catalog if t["name"] == "workspace.read")
    inputs = read_json(ROOT, "examples/tool-inputs.json")
    input_value = next(c["input"] for c in inputs if c["tool"] == tool["name"])
    result = next(
        c["result"]
        for c in read_json(ROOT, "examples/tool-results.json")
        if c["schema_ref"] == tool["output_schema"]
    )
    result = deepcopy(result)
    result["data"]["text"] = "G"
    result["coverage"]["scope"] = "selected"
    binding = {
        "tool": tool["name"],
        "definition_digest": digest(tool),
        "handler_id": "synthetic-read-handler",
        "handler_digest": digest("synthetic-handler"),
        **{
            k: tool[k]
            for k in (
                "input_schema",
                "output_schema",
                "executor",
                "authority",
                "effects",
            )
        },
        "idempotency": "read-only",
        "cancellation": "best-effort",
    }
    identity = {
        "source_digest": digest("synthetic-workspace-snapshot"),
        "policy_digest": digest("synthetic-exact-read-policy"),
        "toolchain_digest": digest("synthetic-worker-toolchain"),
        "registry_digest": digest(catalog),
        "config_digest": digest(config),
        "schema_digest": schema_digest(ROOT),
    }
    result["provenance"].update(
        call_id="read-call",
        source_sha256=identity["source_digest"],
        definition_sha256=binding["definition_digest"],
        policy_sha256=identity["policy_digest"],
        toolchain_sha256=identity["toolchain_digest"],
    )
    result["data"]["sha256"] = identity["source_digest"]
    task = {
        "task_id": "read-task",
        "objective": "Read one bounded synthetic source window.",
        "workspace_id": "example",
        "requirements": [
            {
                "id": "read-evidence",
                "description": "Correlated read result",
                "minimum_level": "focused-test",
            }
        ],
    }
    identity["task_digest"] = digest(task)
    run = {
        "run_id": "read-run",
        "task_id": task["task_id"],
        "agent_id": config["agent_id"],
        "identity": identity,
        "state": "QUEUED",
        "created_at": AT + "00Z",
    }
    grant = {
        "grant_id": "read-grant",
        "run_id": run["run_id"],
        "workspace_id": "example",
        "tool": tool["name"],
        "input_digest": digest(input_value),
        "identity": identity,
        "binding_digest": digest(binding),
        "expires_at": EXPIRES,
        "max_uses": 1,
        "state": "active",
    }
    approval = {
        "approval_id": "read-approval",
        "grant_id": grant["grant_id"],
        "grant_digest": digest(grant),
        "decision": "granted",
        "decided_at": AT + "00Z",
        "expires_at": EXPIRES,
    }
    request = {
        "request_id": "model-request",
        "run_id": run["run_id"],
        "adapter_id": config["adapter"]["adapter_id"],
        "model_binding_id": config["model"]["binding_id"],
        "identity": identity,
        "messages": [
            {"role": "user", "content": [{"kind": "text", "text": task["objective"]}]}
        ],
        "allowed_tools": [tool["name"]],
        "input_token_bound": 1024,
        "max_output_tokens": 512,
        "deadline": EXPIRES,
        "reservation_id": "model-reservation",
    }
    usage = {
        "known": True,
        "input_uncached": 700,
        "input_cached": 100,
        "output_visible": 160,
        "output_reasoning": 40,
        "total_tokens": 1000,
        "microcredits": 500,
    }
    unknown = {"known": False, "reason": "interrupted"}
    dispatch = {
        "call_id": "read-call",
        "run_id": run["run_id"],
        "workspace_id": "example",
        "tool": tool["name"],
        "input_artifact": artifact("read-input", input_value),
        "identity": identity,
        "binding_digest": digest(binding),
        "grant_id": grant["grant_id"],
        "approval_id": approval["approval_id"],
        "deadline": EXPIRES,
    }
    output = artifact("read-output", result)
    receipt = {
        "receipt_id": "read-receipt",
        "run_id": run["run_id"],
        "call_id": "read-call",
        "identity": identity,
        "input_digest": digest(input_value),
        "output": output,
        "result_class": "ok",
        "settled_at": AT + "10Z",
        "verification": [
            {
                "requirement_id": "read-evidence",
                "level": "focused-test",
                "status": "passed",
                "output_digest": output["sha256"],
            }
        ],
    }

    def transition(to, guard="authorized_next_step"):
        return ("transition", {"to": to, "guard": guard})

    reserve = (
        "reserve",
        {
            "reservation_id": "model-reservation",
            "request_id": "model-request",
            "tokens": 1536,
            "microcredits": 1000,
        },
    )
    settle = ("settle", {"reservation_id": "model-reservation", "usage": usage})
    start = [
        transition("PREFLIGHT"),
        transition("PLAN"),
        reserve,
        ("model", request),
        settle,
    ]
    approve = [
        transition("WAITING_APPROVAL"),
        ("approval", approval),
        transition("EXECUTE_STEP", "approval_granted_and_revalidated"),
    ]
    complete = [
        transition("OBSERVE", "new_evidence"),
        transition("VERIFY", "new_evidence"),
        transition("COMPLETE", "all_requirements_verified"),
    ]
    failed = "failure_or_cancellation"
    scenarios = []

    def scenario(name, operations, state, spent=1000, held=0, cost=500, held_cost=0):
        events = [
            {
                "run_id": run["run_id"],
                "sequence": i,
                "at": AT + f"{i:02d}Z",
                "kind": kind,
                "payload": deepcopy(payload),
            }
            for i, (kind, payload) in enumerate(operations, 1)
        ]
        scenarios.append(
            {
                "id": name,
                "events": events,
                "expected_state": state,
                "expected_spent_tokens": spent,
                "expected_held_tokens": held,
                "expected_spent_microcredits": cost,
                "expected_held_microcredits": held_cost,
            }
        )
        return events

    scenario(
        "success",
        start + approve + [("dispatch", dispatch), ("receipt", receipt)] + complete,
        "COMPLETE",
    )
    denied = dict(approval, decision="denied")
    scenario(
        "approval-denied",
        start
        + [
            transition("WAITING_APPROVAL"),
            ("approval", denied),
            transition("BLOCKED", failed),
        ],
        "BLOCKED",
    )
    interrupted = start[:-1] + [
        ("settle", {"reservation_id": "model-reservation", "usage": unknown})
    ]
    scenario(
        "model-timeout",
        interrupted + [transition("WAITING_EXTERNAL")],
        "WAITING_EXTERNAL",
        spent=0,
        held=1536,
        cost=0,
        held_cost=1000,
    )
    scenario(
        "cancelled-before-dispatch",
        start + [transition("CANCELLED", failed)],
        "CANCELLED",
    )
    scenario(
        "unknown-usage-reconciled",
        interrupted
        + [transition("WAITING_EXTERNAL"), settle, transition("CANCELLED", failed)],
        "CANCELLED",
    )
    exhausted_usage = dict(
        usage, input_uncached=5300, output_visible=560, total_tokens=6000
    )
    exhausted_calls = []
    for index in range(2):
        reservation_id = f"budget-reservation-{index}"
        request_id = f"budget-request-{index}"
        exhausted_calls.extend(
            [
                (
                    "reserve",
                    dict(
                        reserve[1],
                        tokens=6000,
                        reservation_id=reservation_id,
                        request_id=request_id,
                    ),
                ),
                (
                    "model",
                    dict(
                        request,
                        input_token_bound=5400,
                        max_output_tokens=600,
                        reservation_id=reservation_id,
                        request_id=request_id,
                    ),
                ),
                (
                    "settle",
                    {"reservation_id": reservation_id, "usage": exhausted_usage},
                ),
            ]
        )
    scenario(
        "budget-exhausted",
        [transition("PREFLIGHT"), transition("PLAN")]
        + exhausted_calls
        + [transition("BLOCKED", failed)],
        "BLOCKED",
        spent=12000,
        cost=1000,
    )
    prefix = start + approve + [("dispatch", dispatch)]
    packet = {
        "run_id": run["run_id"],
        "identity": identity,
        "last_sequence": len(prefix),
        "controller_state": "EXECUTE_STEP",
        "pending_calls": ["read-call"],
        "open_requirements": ["read-evidence"],
        "next_action": "reconcile",
        "expires_at": EXPIRES,
    }
    events = scenario(
        "restart-resume",
        prefix
        + [
            ("checkpoint", packet),
            ("restart", {"checkpoint_digest": digest(packet)}),
            ("reconcile", receipt),
        ]
        + [transition("OBSERVE", "external_result_correlated")]
        + complete[1:],
        "COMPLETE",
    )
    # At-least-once identical delivery is harmless; conflicting duplicate bytes fail.
    events.insert(2, deepcopy(events[1]))
    scenario(
        "tool-timeout",
        prefix + [transition("OUTCOME_UNCERTAIN", "reconciliation_required")],
        "OUTCOME_UNCERTAIN",
    )
    scenario(
        "cancel-after-dispatch",
        prefix
        + [
            transition("OUTCOME_UNCERTAIN", "reconciliation_required"),
            ("reconcile", receipt),
            transition("CANCELLED", failed),
        ],
        "CANCELLED",
    )
    stream = [
        {
            "request_id": request["request_id"],
            "sequence": 1,
            "kind": "tool-call",
            "call_id": "read-call",
            "tool": tool["name"],
            "arguments": dispatch["input_artifact"],
        },
        {
            "request_id": request["request_id"],
            "sequence": 2,
            "kind": "finish",
            "reason": "tool-calls",
            "usage": usage,
        },
    ]
    return {
        "$schema": BASE + "reference-run.schema.json",
        "synthetic": True,
        "config_path": "examples/agent-config.json",
        "task": task,
        "run": run,
        "grant": grant,
        "binding": binding,
        "input": input_value,
        "result": result,
        "adapter_request": request,
        "adapter_stream": stream,
        "adapter_control": {
            "request_id": request["request_id"],
            "run_id": run["run_id"],
            "operation": "cancel",
            "identity": identity,
            "deadline": EXPIRES,
            "resume": None,
        },
        "scenarios": scenarios,
    }


if __name__ == "__main__":
    import json

    target = ROOT / "examples/reference-run.json"
    if target.is_symlink():
        raise ValueError("reference symlink")
    target.write_text(json.dumps(build_reference(), indent=2) + "\n", encoding="utf-8")
    print("Refreshed synthetic reference fixture; no runtime receipt issued.")
