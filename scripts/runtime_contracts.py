"""Pure starter contract checks and synthetic replay; no provider or tool execution."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime

LEVELS = ["source", "focused-test", "build", "activation", "live", "release"]
TERMINAL = {"COMPLETE", "BLOCKED", "FAILED", "CANCELLED"}
ACTIVE = {"PLAN", "EXECUTE_STEP", "REPLAN"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def encoded(value):
    """Kit-local canonical JSON: sorted keys, compact separators, UTF-8, no NaN."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def schema_digest(root):
    return digest(
        {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted((root / "schemas").glob("*.schema.json"))
        }
    )


def instant(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def check_usage(usage):
    if not usage["known"]:
        return None
    total = sum(
        usage[key]
        for key in (
            "input_uncached",
            "input_cached",
            "output_visible",
            "output_reasoning",
        )
    )
    require(total == usage["total_tokens"], "usage counters are not disjoint totals")
    return total, usage["microcredits"]


def check_config(config, tools, profiles, components):
    require(config["profile_id"] == "agent-starter", "wrong starter profile")
    profile = profiles[config["profile_id"]]
    selected = set(config["enabled_extensions"])
    require(selected <= set(profile["optional"]), "unknown or non-optional extension")
    require(len(selected) == len(config["enabled_extensions"]), "duplicate extension")
    # Only explicitly selected extensions activate. Profile compatibility is separate.
    active = set(profile["essential"] + profile["recommended"]) | selected
    pending = list(active)
    while pending:
        for dependency in components[pending.pop()]["requires"]:
            if dependency not in active:
                active.add(dependency)
                pending.append(dependency)
    require(not any(x.startswith("host.") for x in active), "starter selects host")
    require(
        not active & set(profile["excludes"] + profile["defer"]), "excluded extension"
    )
    require(config["concurrency"] == 1, "starter is single-agent")
    require(set(config["selected_tools"]) <= set(tools), "unknown selected tool")
    require(
        len(set(config["selected_tools"])) == len(config["selected_tools"]),
        "duplicate tool",
    )
    if config["workspace"]["access"] == "read":
        require(
            all(tools[t]["effects"] == ["read"] for t in config["selected_tools"]),
            "read workspace selects effectful tool",
        )
    context = config["context"]
    require(
        context["input_tokens"] + context["output_tokens"] + context["safety_tokens"]
        <= context["window_tokens"],
        "context allocations exceed window",
    )
    require(
        context["input_tokens"] + context["output_tokens"]
        <= config["budget"]["run_tokens"],
        "one context slice exceeds run token budget",
    )
    adapter = config["adapter"]
    require(
        {"text", "tool-calls"} <= set(adapter["capabilities"]),
        "adapter lacks core capability",
    )
    require(
        ("resume" in adapter["capabilities"])
        == (adapter["resume_mode"] != "unsupported"),
        "resume capability mismatch",
    )
    require(
        ("cancel" in adapter["capabilities"])
        == (adapter["cancellation"] != "unsupported"),
        "cancel capability mismatch",
    )
    require(
        config["storage"]["receipts_days"] >= config["storage"]["events_days"],
        "receipt retention shorter than event retention",
    )
    return active


def check_stream(request, events):
    calls = set()
    ended = False
    for sequence, event in enumerate(events, 1):
        require(not ended, "stream event after settlement")
        require(event["request_id"] == request["request_id"], "foreign stream request")
        require(event["sequence"] == sequence, "stream sequence gap or duplicate")
        if event["kind"] == "tool-call":
            require(event["call_id"] not in calls, "duplicate stream call")
            require(event["tool"] in request["allowed_tools"], "unselected stream tool")
            calls.add(event["call_id"])
        if event["kind"] in {"finish", "error"}:
            check_usage(event["usage"])
            ended = True
            if event["kind"] == "finish":
                require(
                    (event["reason"] == "tool-calls") == bool(calls),
                    "finish reason contradicts tool calls",
                )
            elif event["code"] in {"unsupported", "authentication", "invalid-response"}:
                require(
                    not event["retryable"], "deterministic adapter error is retryable"
                )
    require(ended, "stream has no terminal event")
    return calls


def authorize(dispatch, grant, approval, binding, run, now, used):
    require(grant["state"] == "active", "grant revoked")
    require(dispatch["run_id"] == grant["run_id"] == run["run_id"], "foreign grant run")
    require(
        dispatch["identity"] == grant["identity"] == run["identity"], "stale identity"
    )
    require(dispatch["grant_id"] == grant["grant_id"], "wrong grant")
    require(dispatch["approval_id"] == approval["approval_id"], "wrong approval")
    require(approval["grant_id"] == grant["grant_id"], "approval grant mismatch")
    require(approval["grant_digest"] == digest(grant), "approval digest mismatch")
    require(approval["decision"] == "granted", "approval denied")
    require(
        instant(approval["decided_at"])
        <= now
        < min(
            instant(approval["expires_at"]),
            instant(grant["expires_at"]),
            instant(dispatch["deadline"]),
        ),
        "expired or future approval, grant or dispatch",
    )
    require(
        instant(approval["expires_at"]) <= instant(grant["expires_at"]),
        "approval extends grant",
    )
    require(dispatch["workspace_id"] == grant["workspace_id"], "foreign workspace")
    require(dispatch["tool"] == grant["tool"] == binding["tool"], "foreign tool")
    require(
        dispatch["input_artifact"]["sha256"] == grant["input_digest"], "changed input"
    )
    require(
        dispatch["binding_digest"] == grant["binding_digest"] == digest(binding),
        "stale binding",
    )
    require(used < grant["max_uses"], "grant replay")


def check_resume(packet, run, state, sequence, pending, open_requirements, now):
    require(packet["run_id"] == run["run_id"], "foreign resume run")
    require(packet["identity"] == run["identity"], "stale resume identity")
    require(packet["controller_state"] == state, "resume state mismatch")
    require(packet["last_sequence"] == sequence, "stale resume cursor")
    require(set(packet["pending_calls"]) == set(pending), "resume drops pending calls")
    require(
        set(packet["open_requirements"]) == set(open_requirements),
        "resume drops requirements",
    )
    require(now < instant(packet["expires_at"]), "expired resume")
    if pending:
        require(packet["next_action"] == "reconcile", "pending effect must reconcile")


def replay(fixture, scenario, config, controller):
    """Replay bounded supplied records in memory; never grant real authority."""
    run, task = fixture["run"], fixture["task"]
    require(run["task_id"] == task["task_id"], "foreign task")
    require(run["identity"]["task_digest"] == digest(task), "task digest mismatch")
    require(run["agent_id"] == config["agent_id"], "foreign agent")
    require(
        task["workspace_id"] == config["workspace"]["workspace_id"],
        "foreign task workspace",
    )
    state = run["state"]
    transitions = {(t["from"], t["to"]): t["guard"] for t in controller["transitions"]}
    requirements = {r["id"]: r["minimum_level"] for r in task["requirements"]}
    require(len(requirements) == len(task["requirements"]), "duplicate requirement")
    passed, pending, settled, reservations, approvals, seen = {}, {}, {}, {}, {}, {}
    spent_tokens = spent_cost = used = model_calls = tool_calls = 0
    reservation_ids, request_ids = set(), set()
    checkpoint = None
    previous = instant(run["created_at"])
    last_sequence = 0

    def held():
        return (
            sum(r["tokens"] for r in reservations.values()),
            sum(r["microcredits"] for r in reservations.values()),
        )

    for event in scenario["events"]:
        require(event["run_id"] == run["run_id"], "foreign event run")
        sequence = event["sequence"]
        if sequence in seen:
            require(seen[sequence] == digest(event), "conflicting duplicate event")
            continue
        require(sequence == last_sequence + 1, "event sequence gap")
        now = instant(event["at"])
        require(now >= previous, "event time reversal")
        require(
            (now - instant(run["created_at"])).total_seconds()
            <= config["budget"]["deadline_seconds"]
            or event["kind"]
            in {
                "settle",
                "reconcile",
                "receipt",
                "transition",
                "checkpoint",
                "restart",
            },
            "new work after run deadline",
        )
        previous = now
        kind, payload = event["kind"], event["payload"]
        if state in TERMINAL:
            require(kind == "settle", "work after terminal state")
        if kind == "transition":
            target = payload["to"]
            require(
                transitions.get((state, target)) == payload["guard"],
                "illegal controller transition",
            )
            if target == "COMPLETE":
                require(set(passed) == set(requirements), "completion without evidence")
                require(
                    not pending and not reservations, "completion with unsettled work"
                )
            if target in TERMINAL:
                require(not pending, "terminal state conceals uncertain effect")
            if state == "WAITING_APPROVAL" and target == "EXECUTE_STEP":
                require(
                    fixture["grant"]["state"] == "active"
                    and used < fixture["grant"]["max_uses"]
                    and any(
                        a["decision"] == "granted"
                        and a["grant_id"] == fixture["grant"]["grant_id"]
                        and a["grant_digest"] == digest(fixture["grant"])
                        and instant(a["decided_at"])
                        <= now
                        < min(
                            instant(a["expires_at"]),
                            instant(fixture["grant"]["expires_at"]),
                        )
                        for a in approvals.values()
                    ),
                    "approval guard not satisfied",
                )
            if (
                state in {"WAITING_EXTERNAL", "OUTCOME_UNCERTAIN"}
                and target == "OBSERVE"
            ):
                require(not pending and bool(settled), "external result not correlated")
            state = target
        elif kind == "reserve":
            require(state in ACTIVE, "reservation during wait or terminal state")
            key = payload["reservation_id"]
            require(key not in reservation_ids, "duplicate reservation")
            require(
                payload["request_id"] not in request_ids,
                "duplicate request reservation",
            )
            require(
                not any(
                    r["request_id"] == payload["request_id"]
                    for r in reservations.values()
                ),
                "duplicate request reservation",
            )
            h_tokens, h_cost = held()
            require(
                spent_tokens + h_tokens + payload["tokens"]
                <= config["budget"]["run_tokens"],
                "token budget exhausted",
            )
            require(
                spent_cost + h_cost + payload["microcredits"]
                <= config["budget"]["run_microcredits"],
                "cost budget exhausted",
            )
            reservation_ids.add(key)
            request_ids.add(payload["request_id"])
            reservations[key] = dict(payload, launched=False)
        elif kind == "model":
            require(state in ACTIVE, "model turn during wait")
            require(
                payload["run_id"] == run["run_id"]
                and payload["identity"] == run["identity"],
                "foreign model identity",
            )
            require(
                payload["adapter_id"] == config["adapter"]["adapter_id"],
                "foreign adapter",
            )
            require(
                payload["model_binding_id"] == config["model"]["binding_id"],
                "foreign model binding",
            )
            require(
                set(payload["allowed_tools"]) <= set(config["selected_tools"]),
                "model tool escalation",
            )
            require(now < instant(payload["deadline"]), "model deadline expired")
            reservation = reservations.get(payload["reservation_id"])
            require(
                reservation is not None and not reservation["launched"],
                "model lacks unused reservation",
            )
            require(
                reservation["request_id"] == payload["request_id"],
                "foreign reservation request",
            )
            require(
                payload["input_token_bound"] <= config["context"]["input_tokens"],
                "model input overflow",
            )
            require(
                payload["max_output_tokens"] <= config["context"]["output_tokens"],
                "model output overflow",
            )
            require(
                payload["input_token_bound"] + payload["max_output_tokens"]
                <= reservation["tokens"],
                "under-reserved model call",
            )
            model_calls += 1
            require(
                model_calls <= config["budget"]["max_model_calls"], "model call limit"
            )
            reservation["launched"] = True
            reservation["input_bound"] = payload["input_token_bound"]
            reservation["output_bound"] = payload["max_output_tokens"]
        elif kind == "settle":
            key = payload["reservation_id"]
            require(
                key in reservations and reservations[key]["launched"],
                "settlement without launched reservation",
            )
            amounts = check_usage(payload["usage"])
            if amounts is not None:
                tokens, cost = amounts
                require(
                    tokens <= reservations[key]["tokens"]
                    and cost <= reservations[key]["microcredits"],
                    "usage exceeds reservation",
                )
                usage = payload["usage"]
                require(
                    usage["input_uncached"] + usage["input_cached"]
                    <= reservations[key]["input_bound"]
                    and usage["output_visible"] + usage["output_reasoning"]
                    <= reservations[key]["output_bound"],
                    "usage exceeds model allocation",
                )
                spent_tokens += tokens
                spent_cost += cost
                del reservations[key]
        elif kind == "approval":
            require(state == "WAITING_APPROVAL", "approval outside approval wait")
            require(payload["approval_id"] not in approvals, "duplicate approval")
            approvals[payload["approval_id"]] = payload
        elif kind == "dispatch":
            require(state == "EXECUTE_STEP", "dispatch outside execution state")
            require(
                payload["call_id"] not in pending and payload["call_id"] not in settled,
                "call replay",
            )
            require(
                payload["tool"] in config["selected_tools"], "unselected dispatch tool"
            )
            require(
                payload["workspace_id"] == task["workspace_id"],
                "foreign dispatch workspace",
            )
            approval = approvals.get(payload["approval_id"])
            require(approval is not None, "missing approval")
            authorize(
                payload, fixture["grant"], approval, fixture["binding"], run, now, used
            )
            tool_calls += 1
            require(tool_calls <= config["budget"]["max_tool_calls"], "tool call limit")
            used += 1
            pending[payload["call_id"]] = dict(payload, dispatched_at=event["at"])
        elif kind in {"receipt", "reconcile"}:
            if kind == "reconcile":
                require(
                    state == "OUTCOME_UNCERTAIN", "reconcile without uncertain outcome"
                )
            require(payload["call_id"] in pending, "uncorrelated or duplicate receipt")
            call = pending[payload["call_id"]]
            require(
                payload["run_id"] == run["run_id"]
                and payload["identity"] == run["identity"],
                "stale receipt identity",
            )
            require(
                payload["input_digest"] == call["input_artifact"]["sha256"],
                "receipt input mismatch",
            )
            require(
                instant(call["dispatched_at"]) <= instant(payload["settled_at"]) <= now,
                "receipt settlement outside dispatch window",
            )
            for evidence in payload["verification"]:
                key = evidence["requirement_id"]
                require(key in requirements, "foreign verification requirement")
                require(
                    evidence["output_digest"] == payload["output"]["sha256"],
                    "verification output mismatch",
                )
                if evidence["status"] == "passed":
                    require(
                        payload["result_class"] == "ok", "failed receipt claims success"
                    )
                    require(
                        LEVELS.index(evidence["level"])
                        >= LEVELS.index(requirements[key]),
                        "insufficient evidence level",
                    )
                    passed[key] = evidence
            settled[payload["call_id"]] = payload
            del pending[payload["call_id"]]
        elif kind == "checkpoint":
            check_resume(
                payload,
                run,
                state,
                last_sequence,
                pending,
                set(requirements) - set(passed),
                now,
            )
            require(
                len(encoded(payload)) <= config["context"]["resume_bytes"],
                "resume exceeds byte budget",
            )
            checkpoint = payload
        elif kind == "restart":
            require(checkpoint is not None, "restart without checkpoint")
            require(
                payload["checkpoint_digest"] == digest(checkpoint),
                "checkpoint digest mismatch",
            )
            require(now < instant(checkpoint["expires_at"]), "expired checkpoint")
            require(
                checkpoint["identity"] == run["identity"], "changed recovery identity"
            )
            # The durable log, not the possibly older checkpoint, owns pending work,
            # spent/held budgets, approval consumption, requirements and the cursor.
            if pending:
                require(
                    (state, "OUTCOME_UNCERTAIN") in transitions,
                    "no uncertain recovery transition",
                )
                state = "OUTCOME_UNCERTAIN"
        else:
            raise ValueError("unknown replay event")
        seen[sequence] = digest(event)
        last_sequence = sequence
    h_tokens, h_cost = held()
    result = {
        "state": state,
        "spent_tokens": spent_tokens,
        "held_tokens": h_tokens,
        "spent_microcredits": spent_cost,
        "held_microcredits": h_cost,
    }
    for key, value in result.items():
        require(
            value == scenario["expected_" + key],
            "scenario expectation mismatch: " + key,
        )
    return result


def check_reference(root, read_json, config, fixture, tools, controller):
    """Bind local fixtures to current declarations, without executing handlers."""
    binding = fixture["binding"]
    definition = tools[binding["tool"]]
    require(
        binding["definition_digest"] == digest(definition), "definition digest drift"
    )
    for key in ("input_schema", "output_schema", "executor", "authority", "effects"):
        require(binding[key] == definition[key], "handler/catalog parity drift: " + key)
    require(
        fixture["run"]["identity"]["config_digest"] == digest(config),
        "config digest drift",
    )
    for instruction in config["instructions"]:
        content = (root / instruction["path"]).read_bytes()
        require(
            hashlib.sha256(content).hexdigest() == instruction["digest"],
            "instruction digest drift",
        )
    require(
        fixture["run"]["identity"]["registry_digest"] == digest(list(tools.values())),
        "registry digest drift",
    )
    request = fixture["adapter_request"]
    calls = check_stream(request, fixture["adapter_stream"])
    require(calls == {"read-call"}, "reference stream call drift")
    provenance = fixture["result"]["provenance"]
    identity = fixture["run"]["identity"]
    require(provenance["call_id"] == "read-call", "result call mismatch")
    for key in ("source", "policy", "toolchain"):
        require(
            provenance[key + "_sha256"] == identity[key + "_digest"],
            "result identity mismatch",
        )
    require(
        provenance["definition_sha256"] == binding["definition_digest"],
        "result definition mismatch",
    )
    control = fixture["adapter_control"]
    require(
        control["request_id"] == request["request_id"]
        and control["run_id"] == request["run_id"],
        "foreign adapter control",
    )
    require(control["identity"] == request["identity"], "stale adapter control")
    require(
        control["operation"] != "resume" or control["resume"] is not None,
        "resume control missing packet",
    )
    inputs = read_json(root, "examples/tool-inputs.json")
    input_value = next(c["input"] for c in inputs if c["tool"] == binding["tool"])
    require(fixture["input"] == input_value, "reference input drift")
    require(
        input_value["workspace_id"] == fixture["grant"]["workspace_id"],
        "input workspace mismatch",
    )
    require(
        len(fixture["result"]["data"]["text"].encode("utf-8"))
        <= input_value["max_bytes"],
        "read exceeds requested bytes",
    )
    require(
        fixture["result"]["data"]["offset_bytes"] == input_value["offset_bytes"],
        "read offset mismatch",
    )
    require(
        fixture["run"]["identity"]["schema_digest"] == schema_digest(root),
        "runtime schema digest drift",
    )
    require(
        fixture["grant"]["input_digest"] == digest(input_value),
        "reference input digest drift",
    )
    require(
        len({s["id"] for s in fixture["scenarios"]}) == len(fixture["scenarios"]),
        "duplicate scenario",
    )
    for scenario in fixture["scenarios"]:
        for event in scenario["events"]:
            if event["kind"] == "dispatch":
                artifact = event["payload"]["input_artifact"]
                require(
                    artifact["sha256"] == digest(input_value)
                    and artifact["size_bytes"] == len(encoded(input_value)),
                    "input artifact mismatch",
                )
            if event["kind"] in {"receipt", "reconcile"}:
                artifact = event["payload"]["output"]
                require(
                    artifact["sha256"] == digest(fixture["result"])
                    and artifact["size_bytes"] == len(encoded(fixture["result"])),
                    "output artifact mismatch",
                )
        replay(fixture, scenario, config, controller)
