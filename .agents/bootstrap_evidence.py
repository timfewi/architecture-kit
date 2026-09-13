"""Small local fingerprints and records; no platform authority or runtime state."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import sys
import tempfile
from importlib import metadata
from pathlib import Path

LIMIT = 2 * 1024 * 1024
IGNORED = {".git", ".direnv", ".ruff_cache", "__pycache__", ".pytest_cache"}
IDENTIFIER = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate key: {key}")
        result[key] = value
    return result


def read_json(path):
    require(not path.is_symlink(), f"symlink: {path.name}")
    require(path.is_file() and path.stat().st_size <= LIMIT, f"invalid file: {path}")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def file_digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def local_path(root, name):
    require(isinstance(name, str) and 0 < len(name) <= 1024, "invalid relative path")
    require(
        not any(c in name for c in "\\:\x00")
        and all(ord(c) >= 32 for c in name)
        and all(p not in {"", ".", ".."} for p in name.split("/")),
        f"unsafe relative path: {name}",
    )
    path = root
    for part in name.split("/"):
        path = path / part
        require(not path.is_symlink(), f"symlink input: {name}")
    return path


def inputs(root, names):
    result = {}

    def visit(path, name):
        require(not path.is_symlink(), f"symlink input: {name}")
        if not path.exists():
            result[name] = None
        elif path.is_dir():
            result[name + "/"] = "directory"
            for child in sorted(path.iterdir()):
                if child.name not in IGNORED:
                    visit(child, f"{name}/{child.name}".removeprefix("./"))
        else:
            require(
                path.is_file() and path.stat().st_size <= LIMIT,
                f"invalid input: {name}",
            )
            result[name] = file_digest(path)
        require(len(result) <= 2000, "input set exceeds 2000 entries; narrow the check")

    for name in names:
        visit(root if name == "." else local_path(root, name), name)
    return dict(sorted(result.items()))


def environment():
    return {
        "PATH": os.environ.get("PATH", os.defpath),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }


def executable(check):
    argv = check["argv"]
    if not argv:
        return None
    name = argv[0]
    require("/" not in name and "\\" not in name, "use a PATH executable, not a path")
    path = (
        sys.executable
        if name == "python3"
        else shutil.which(name, path=environment()["PATH"])
    )
    return str(Path(path).absolute()) if path else None


def versions():
    packages = {}
    for name in ("jsonschema", "PyYAML", "referencing"):
        try:
            packages[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            packages[name] = None
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": packages,
    }


def binding(root, plan, task, check, cache=None):
    cache = {} if cache is None else cache
    key = (task["id"], check["id"])
    if key in cache:
        return cache[key]
    dependencies = {}
    by_id = {entry["id"]: entry for entry in plan["tasks"]}
    for identity in task["depends_on"]:
        dep = by_id[identity]
        for dep_check in dep["checks"]:
            dependencies[f"{identity}/{dep_check['id']}"] = digest(
                binding(root, plan, dep, dep_check, cache)
            )
    program = executable(check)
    names = list(dict.fromkeys(plan["shared_inputs"] + check["inputs"]))
    value = {
        "clone": digest(str(root)),
        "target": plan["target"],
        "dependencies": dependencies,
        "task": task,
        "check": check,
        "inputs": inputs(root, names),
        "environment": digest(environment()),
        "versions": versions(),
        "executable": {"path": program, "sha256": file_digest(Path(program))}
        if program
        else None,
    }
    cache[key] = value
    return value


def state_directory(root, value):
    if value is None:
        return None
    original = Path(value).absolute()
    for path in (original, *original.parents):
        require(not path.is_symlink(), "state path contains a symlink")
    path = original.resolve()
    require(
        not path.is_relative_to(root) and not root.is_relative_to(path),
        "state directory must be dedicated and outside the clone",
    )
    require(not path.exists() or path.is_dir(), "state path is not a directory")
    return path


def record_path(state, task_id, check_id):
    for name in (task_id, check_id):
        require(IDENTIFIER.fullmatch(name), "invalid task/check identifier")
    return state / f"{task_id}--{check_id}.json"


def save_record(state, task_id, check_id, record):
    state.mkdir(mode=0o700, parents=True, exist_ok=True)
    target = record_path(state, task_id, check_id)
    require(not target.is_symlink(), "symlink record")
    payload = json.dumps(record, sort_keys=True, indent=2) + "\n"
    require(len(payload.encode()) <= LIMIT, "record too large")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=state, delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def check_status(root, plan, task, check, state):
    if check["argv"] is None:
        return {"id": check["id"], "status": "unconfigured"}
    current = binding(root, plan, task, check)
    if current["executable"] is None:
        return {
            "id": check["id"],
            "status": "blocked",
            "reason": "executable unavailable",
        }
    path = record_path(state, task["id"], check["id"]) if state else None
    require(path is None or not path.is_symlink(), "symlink record")
    if path is None or not path.exists():
        return {"id": check["id"], "status": "not-run"}
    record = read_json(path)
    require(isinstance(record, dict), "record must be an object")
    require(isinstance(record.get("binding"), dict), "record binding must be an object")
    require(
        isinstance(record["binding"].get("inputs"), dict),
        "record inputs must be an object",
    )
    require(
        record["binding"].get("clone") == current["clone"],
        "state belongs to a different clone",
    )
    require(
        record.get("format") == "bootstrap-observation-v1", "unsupported record format"
    )
    require(
        record.get("task") == task["id"] and record.get("check") == check["id"],
        "foreign record",
    )
    require(
        record.get("status")
        in {
            "passed",
            "failed",
            "blocked",
            "timeout",
            "cancelled",
            "output-limit",
            "inputs-changed",
        },
        "invalid record status",
    )
    require(
        record.get("binding_sha256") == digest(record.get("binding")),
        "damaged record binding",
    )
    require(
        record["status"] != "passed" or record.get("exit_code") == 0,
        "contradictory pass",
    )
    if record["binding"] != current:
        old = record["binding"].get("inputs", {})
        changed = sorted(
            k
            for k in old.keys() | current["inputs"].keys()
            if old.get(k) != current["inputs"].get(k)
        )
        return {"id": check["id"], "status": "stale", "changed_inputs": changed[:20]}
    return {"id": check["id"], "status": record["status"], "level": check["level"]}
