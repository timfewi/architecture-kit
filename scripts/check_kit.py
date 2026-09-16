"""Offline kit integrity and semantic checks; full mode also validates JSON Schema."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urldefrag, urljoin

if __package__:
    from . import check_skills, runtime_contracts
else:
    import check_skills
    import runtime_contracts

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://architecture-kit.invalid/"
DIALECT = "https://json-schema.org/draft/2020-12/schema"
IGNORED = {".git", ".direnv", ".ruff_cache", "__pycache__", ".pytest_cache"}
MAX_FILE_BYTES = 2 * 1024 * 1024


class InvalidKit(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidKit(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise InvalidKit(f"non-finite JSON constant: {value}")


def parse_json(text):
    result = json.loads(
        text, object_pairs_hook=unique_object, parse_constant=reject_constant
    )

    def finite(value, depth=0):
        require(depth <= 64, "JSON nesting exceeds 64")
        if isinstance(value, float):
            import math

            require(math.isfinite(value), "non-finite parsed number")
        elif isinstance(value, dict):
            for child in value.values():
                finite(child, depth + 1)
        elif isinstance(value, list):
            for child in value:
                finite(child, depth + 1)

    finite(result)
    return result


def safe_path(path):
    require(isinstance(path, str) and 0 < len(path) <= 1024, "invalid path length")
    require(
        not path.startswith("/") and "\\" not in path and ":" not in path,
        f"non-relative path: {path!r}",
    )
    require(
        all(part not in {"", ".", ".."} for part in path.split("/")),
        f"unsafe path component: {path!r}",
    )
    require(all(ord(c) >= 32 for c in path), "control character in path")
    return path


def source_files(root):
    result = []

    def visit(directory):
        for child in sorted(directory.iterdir()):
            if child.name in IGNORED:
                continue
            require(
                not child.is_symlink(), f"symlink in kit: {child.relative_to(root)}"
            )
            if child.is_dir():
                visit(child)
            else:
                require(child.is_file(), "non-regular kit entry")
                require(child.stat().st_size <= MAX_FILE_BYTES, "oversized kit file")
                result.append(child.relative_to(root).as_posix())
                require(len(result) <= 1000, "too many kit files")

    visit(root)
    return sorted(result)


def read_json(root, path):
    safe_path(path)
    return parse_json((root / path).read_text(encoding="utf-8"))


def read_profile(path):
    import yaml

    class UniqueLoader(yaml.SafeLoader):
        pass

    def mapping(loader, node, deep=False):
        require(
            not any(key.value == "<<" for key, _ in node.value),
            "YAML merge keys are not supported",
        )
        return unique_object(
            [
                (
                    loader.construct_object(key, deep=deep),
                    loader.construct_object(value, deep=deep),
                )
                for key, value in node.value
            ]
        )

    UniqueLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping
    )
    # Profiles are small declarative trees; aliases obscure review and can expand.
    text = path.read_text(encoding="utf-8")
    for event in yaml.parse(text):
        require(
            not isinstance(event, yaml.events.AliasEvent), "YAML aliases are forbidden"
        )
    return yaml.load(text, Loader=UniqueLoader)


def indexed(records, key, label):
    result = {}
    for record in records:
        identity = record[key]
        require(identity not in result, f"duplicate {label}: {identity}")
        result[identity] = record
    return result


def closure(selected, components):
    visited, active = set(), set()

    def walk(identity):
        require(identity in components, f"unknown component: {identity}")
        require(identity not in active, f"component cycle: {identity}")
        if identity in visited:
            return
        active.add(identity)
        for dep in components[identity]["requires"]:
            walk(dep)
        active.remove(identity)
        visited.add(identity)

    for identity in selected:
        walk(identity)
    return visited


def schema_documents(root):
    return {
        BASE + p: read_json(root, p)
        for p in source_files(root)
        if p.startswith("schemas/") and p.endswith(".schema.json")
    }


def resolve_schema(ref, documents, base=BASE):
    uri, fragment = urldefrag(urljoin(base, ref))
    require(uri in documents, f"unresolved/offline-only schema: {uri}")
    value = documents[uri]
    if fragment:
        require(fragment.startswith("/"), "only JSON Pointer fragments are supported")
        for token in fragment[1:].split("/"):
            token = token.replace("~1", "/").replace("~0", "~")
            require(
                isinstance(value, dict) and token in value,
                f"missing schema pointer: {ref}",
            )
            value = value[token]
    require(isinstance(value, (dict, bool)), f"non-schema reference: {ref}")
    return value


def walk_refs(value, documents, base):
    if isinstance(value, dict):
        if "$ref" in value:
            resolve_schema(value["$ref"], documents, base)
        for key, child in value.items():
            if key not in {"const", "enum", "examples"}:
                walk_refs(child, documents, base)
    elif isinstance(value, list):
        for child in value:
            walk_refs(child, documents, base)


def result_semantics(kind, result, input_schema=None):
    """Check cross-field invariants after shape validation; not a schema validator."""
    payload = result["data"]
    coverage = result["coverage"]
    cursor = result["continuation"]
    if cursor is not None:
        require(
            input_schema is None or "cursor" in input_schema["properties"],
            "output continuation has no consuming input",
        )
        require(
            cursor["source_sha256"] == result["provenance"]["source_sha256"],
            "cursor source identity drift",
        )
    if coverage["truncated"]:
        require(
            cursor is not None or result["artifact"] is not None,
            "truncated data has no continuation or artifact",
        )
    if payload is None:
        require(coverage["returned"] == 0, "absent payload has returned records")
        return
    collections = {
        "hits": "items",
        "listing": "entries",
        "git_status": "entries",
        "table": "rows",
    }
    field = collections.get(kind)
    count = len(payload[field]) if field else 1
    require(coverage["returned"] == count, "returned count disagrees with payload")
    if kind in {"hits", "listing"} and payload["total"] is not None:
        require(payload["total"] >= count, "total is smaller than returned page")
    if kind == "hits":
        for hit in payload["items"]:
            anchor = hit["anchor"]
            if anchor is not None:
                require(anchor["end_byte"] >= anchor["start_byte"], "reversed anchor")
    if kind == "text":
        require(
            payload["offset_bytes"] + len(payload["text"].encode("utf-8"))
            <= payload["total_bytes"],
            "text exceeds declared byte window",
        )
    if kind == "table":
        width = len(payload["columns"])
        require(
            all(len(row) == width for row in payload["rows"]),
            "table row width disagrees with columns",
        )


def contract_examples(root, tools, documents):
    inputs = indexed(
        read_json(root, "examples/tool-inputs.json"), "tool", "input fixture"
    )
    require(set(inputs) == set(tools), "input fixture coverage drift")
    results = indexed(
        read_json(root, "examples/tool-results.json"), "schema_ref", "result fixture"
    )
    require(
        set(results) == {tool["output_schema"] for tool in tools.values()},
        "result fixture coverage drift",
    )
    for tool in tools.values():
        ref = tool["output_schema"]
        result_semantics(
            ref.rsplit("result.", 1)[1],
            results[ref]["result"],
            resolve_schema(tool["input_schema"], documents),
        )
    return inputs, results


def semantic_check(root):
    check_skills.check(root)
    files = source_files(root)
    documents = schema_documents(root)
    json_files = {
        p: read_json(root, p) for p in files if p.endswith(".json") or p == "flake.lock"
    }
    inventories = {
        Path(p).stem: read_json(root, p)
        for p in files
        if p.startswith("inventories/") and p.endswith(".json")
    }
    for uri, schema in documents.items():
        require(schema.get("$schema") == DIALECT, f"wrong dialect: {uri}")
        require(schema.get("$id") == uri, f"wrong schema identity: {uri}")
        walk_refs(schema, documents, uri)
    for name, inv in inventories.items():
        require(
            inv["$schema"] == BASE + f"schemas/{name}.schema.json",
            f"wrong inventory schema: {name}",
        )
    decisions = indexed(inventories["decisions"]["decisions"], "id", "decision")
    components = indexed(inventories["components"]["components"], "id", "component")
    tools = indexed(inventories["agent-tools"]["tools"], "name", "tool")
    closure(components, components)
    for records in inventories.values():
        for collection in records.values():
            if isinstance(collection, list):
                for record in collection:
                    if isinstance(record, dict):
                        for ref in record.get("decision_refs", []):
                            require(ref in decisions, f"unknown decision: {ref}")
    architecture = (root / "ARCHITECTURE.md").read_text(encoding="utf-8")
    for identity, decision in decisions.items():
        require(
            decision["document"] == "ARCHITECTURE.md",
            "decision path must be kit-relative",
        )
        require(
            f"## {identity} — {decision['title']}" in architecture,
            f"missing decision heading: {identity}",
        )
        expected = re.sub(r"[^\w -]", "", decision["title"].lower()).replace(" ", "-")
        require(
            decision["anchor"] == identity.lower() + "-" + expected,
            f"wrong decision anchor: {identity}",
        )
    capabilities = indexed(
        inventories["capabilities"]["capabilities"], "id", "capability"
    )
    required_effects = {
        "workspace.create": {"workspace_write"},
        "workspace.mkdir": {"workspace_write"},
        "workspace.replace": {"workspace_write"},
        "memory.propose": {"state_write"},
        "git.fetch": {"network", "git_write"},
        "git.push": {"network", "external_write"},
        "browser.upload": {"network", "external_write"},
    }
    for name, effects in required_effects.items():
        require(
            effects <= set(tools[name]["effects"]),
            f"incorrect mutation effects: {name}",
        )
    grouped = {}
    for name, tool in tools.items():
        for field in ("input_schema", "output_schema"):
            resolve_schema(tool[field], documents)
        require(
            tool["bounds"]["default_records"] <= tool["bounds"]["max_records"],
            f"record bounds: {name}",
        )
        require(
            tool["bounds"]["default_timeout_ms"] <= tool["bounds"]["max_timeout_ms"],
            f"time bounds: {name}",
        )
        grouped.setdefault(tool["authority"], []).append(tool)
    require(set(grouped) == set(capabilities), "capability membership drift")
    for identity, members in grouped.items():
        cap = capabilities[identity]
        expected = {
            "tools": {t["name"] for t in members},
            "executors": {t["executor"] for t in members},
            "side_effects": {e for t in members for e in t["effects"]},
            "profiles": {p for t in members for p in t["profiles"]},
        }
        for key, values in expected.items():
            require(
                set(cap[key]) == values and len(cap[key]) == len(values),
                f"capability {identity}: {key} drift",
            )
    for name in ["interfaces", "software", "verification-gates"]:
        key = {
            "interfaces": "interfaces",
            "software": "direct_choices",
            "verification-gates": "gates",
        }[name]
        indexed(inventories[name][key], "id", name)
    profiles = {}
    for p in files:
        if not p.startswith("profiles/") or not p.endswith(".yaml"):
            continue
        profile = read_profile(root / p)
        identity = profile["profile_id"]
        require(
            identity == Path(p).stem and identity not in profiles,
            "profile identity drift",
        )
        profiles[identity] = profile
        groups = [
            profile[k]
            for k in ("essential", "recommended", "optional", "defer", "excludes")
        ]
        flat = [x for group in groups for x in group]
        require(
            len(flat) == len(set(flat)), f"overlapping profile selections: {identity}"
        )
        require(set(flat) <= set(components), f"unknown profile component: {identity}")
        selected = profile["essential"] + profile["recommended"] + profile["optional"]
        resolved = closure(selected, components)
        forbidden = set(profile["defer"] + profile["excludes"])
        require(
            not resolved & forbidden,
            f"excluded dependency: {identity}: {resolved & forbidden}",
        )
        if identity in {"agent-platform", "agent-starter"}:
            require(
                not any(x.startswith("host.") for x in resolved),
                "portable profile depends on reference host",
            )
    for choice in inventories["software"]["direct_choices"]:
        require(set(choice["profiles"]) <= set(profiles), "unknown software profile")
        require(set(choice["tool_refs"]) <= set(tools), "unknown software tool binding")
    for gate in inventories["verification-gates"]["gates"]:
        require(
            set(gate["applies_to"]) <= set(components) | {"all"}, "unknown gate target"
        )
    controller = inventories["controller-policy"]
    states = set(controller["states"])
    transitions = controller["transitions"]
    pairs = [(t["from"], t["to"]) for t in transitions]
    require(len(pairs) == len(set(pairs)), "duplicate controller transition")
    for t in transitions:
        require(t["from"] in states and t["to"] in states, "unknown controller state")
        require(
            t["from"] not in {"COMPLETE", "FAILED", "CANCELLED", "BLOCKED"},
            "terminal state has outgoing transition",
        )
        if t["to"] == "COMPLETE":
            require(
                t["from"] == "VERIFY" and t["guard"] == "all_requirements_verified",
                "completion without verification guard",
            )
    require(("OUTCOME_UNCERTAIN", "OBSERVE") in pairs, "missing reconciliation path")
    build = inventories["build-capability"]
    for key, tool_name in [
        ("request_contract", "build.request"),
        ("result_contract", "build.result"),
    ]:
        expected = build[key]["required_fields"]
        target = (
            tools[tool_name]["input_schema"]
            if key == "request_contract"
            else "schemas/tool-contracts.schema.json#/$defs/job"
        )
        require(
            expected == resolve_schema(target, documents)["required"],
            "build field parity drift",
        )
    contract_examples(root, tools, documents)
    config = read_json(root, controller["starter_config_ref"])
    runtime_contracts.check_config(config, tools, profiles, components)
    for instruction in config["instructions"]:
        safe_path(instruction["path"])
    reference = read_json(root, "examples/reference-run.json")
    runtime_contracts.check_reference(
        root, read_json, config, reference, tools, controller
    )
    result_semantics("text", reference["result"])
    for interface in inventories["interfaces"]["interfaces"]:
        target = interface["payload_schema"]
        if target is not None:
            schema = resolve_schema(target, documents)
            fields = schema.get("required")
            if fields is None:
                variants = schema["oneOf"]
                fields = [
                    k
                    for k in variants[0]["required"]
                    if all(k in v["required"] for v in variants)
                ]
            require(interface["fields"] == fields, "interface payload field drift")
    return {
        "files": files,
        "schemas": documents,
        "json_files": json_files,
        "inventories": inventories,
        "profiles": profiles,
        "tools": tools,
    }


def artifact_kind(path):
    kinds = {
        ".md": "markdown",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".json": "json",
        ".py": "python",
        ".mjs": "javascript",
        ".txt": "text",
        ".nix": "nix",
    }
    named = {
        ".gitignore": "text",
        ".envrc": "shell",
        "justfile": "just",
        "flake.lock": "json",
    }
    kind = (
        "json-schema"
        if path.endswith(".schema.json")
        else named.get(path, kinds.get(Path(path).suffix))
    )
    require(kind is not None, f"unclassified artifact: {path}")
    return kind


def manifest_for(root, data, generated_on=None):
    artifacts = []
    for path in data["files"]:
        if path == "manifest.json":
            continue
        raw = (root / path).read_bytes()
        kind = artifact_kind(path)
        artifacts.append(
            {
                "path": path,
                "kind": kind,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "size_bytes": len(raw),
            }
        )
    tools_raw = (root / "inventories/agent-tools.json").read_bytes()
    return {
        "$schema": BASE + "schemas/manifest.schema.json",
        "language": "en",
        "generated_on": generated_on
        or read_json(root, "manifest.json")["generated_on"],
        "artifacts": artifacts,
        "catalog": {
            "decision_count": len(data["inventories"]["decisions"]["decisions"]),
            "tool_count": len(data["tools"]),
            "default_tool_count": sum(
                t["default_surface"] for t in data["tools"].values()
            ),
            "tool_catalog_sha256": hashlib.sha256(tools_raw).hexdigest(),
        },
    }


def validator_environment():
    try:
        from importlib.metadata import version

        import jsonschema
        import referencing
    except ImportError as exc:
        raise InvalidKit(
            "ENVIRONMENT_BLOCKED: full schema validation requires "
            "jsonschema==4.26.0 and its reviewed dependency closure"
        ) from exc
    require(
        version("jsonschema") == "4.26.0",
        "ENVIRONMENT_BLOCKED: wrong jsonschema version",
    )
    return jsonschema, referencing


def format_checker(jsonschema):
    # The contract uses a deliberately narrow UTC timestamp, without leap seconds.
    # Register it explicitly; optional third-party format extras are not required.
    from datetime import datetime

    checker = jsonschema.FormatChecker(formats=["date"])

    @checker.checks("date-time", raises=ValueError)
    def utc_timestamp(value):
        if not isinstance(value, str):
            return True
        if not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z", value
        ):
            return False
        datetime.fromisoformat(value)
        return True

    return checker


def full_schema_check(root, data):
    jsonschema, referencing = validator_environment()
    registry = referencing.Registry().with_resources(
        [
            (uri, referencing.Resource.from_contents(doc))
            for uri, doc in data["schemas"].items()
        ]
    )
    checker = format_checker(jsonschema)
    for doc in data["schemas"].values():
        jsonschema.Draft202012Validator.check_schema(doc)
    instances = [(x, x["$schema"]) for x in data["inventories"].values()]
    instances += [
        (x, BASE + "schemas/profile.schema.json") for x in data["profiles"].values()
    ]
    instances.append(
        (read_json(root, "manifest.json"), BASE + "schemas/manifest.schema.json")
    )
    for path, instance in data["json_files"].items():
        if (
            path.startswith(("research/", "examples/"))
            and isinstance(instance, dict)
            and "$schema" in instance
        ):
            instances.append((instance, instance["$schema"]))
    for instance, uri in instances:
        jsonschema.Draft202012Validator(
            data["schemas"][uri], registry=registry, format_checker=checker
        ).validate(instance)
    inputs, results = contract_examples(root, data["tools"], data["schemas"])
    contracts = [
        (case["input"], data["tools"][name]["input_schema"])
        for name, case in inputs.items()
    ] + [(case["result"], ref) for ref, case in results.items()]
    for instance, ref in contracts:
        jsonschema.Draft202012Validator(
            {"$schema": DIALECT, "$ref": BASE + ref},
            registry=registry,
            format_checker=checker,
        ).validate(instance)
    return registry, checker


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--structural", action="store_true")
    modes.add_argument("--refresh-manifest", action="store_true")
    args = parser.parse_args()
    try:
        data = semantic_check(ROOT)
        expected = manifest_for(ROOT, data)
        if args.refresh_manifest:
            from datetime import datetime, timezone

            expected["generated_on"] = datetime.now(timezone.utc).date().isoformat()
            target = ROOT / "manifest.json"
            require(not target.is_symlink(), "manifest symlink")
            target.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8")
            print("Refreshed manifest.json; no validation receipt issued.")
            return 0
        require(
            read_json(ROOT, "manifest.json") == expected,
            "manifest drift; review then refresh",
        )
        if not args.structural:
            full_schema_check(ROOT, data)
        print(
            json.dumps(
                {
                    "status": "passed",
                    "coverage": "integrity-and-semantics"
                    if args.structural
                    else "integrity-semantics-and-json-schema",
                    "tools": len(data["tools"]),
                    "schemas": len(data["schemas"]),
                    "excluded": ["runtime", "deployment", "performance"]
                    + (["json-schema-validation"] if args.structural else []),
                }
            )
        )
        return 0
    except (InvalidKit, ValueError, KeyError, OSError, ImportError) as exc:
        print(str(exc), file=sys.stderr)
        return 2 if "ENVIRONMENT_BLOCKED" in str(exc) else 1


if __name__ == "__main__":
    sys.exit(main())
