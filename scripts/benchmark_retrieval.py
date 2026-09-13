"""Synthetic literal-search comparison. Writes no repository files; emits JSON."""

import hashlib
import json
import platform
import shutil
import statistics
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from check_kit import ROOT, read_json

QUERIES = [
    ("positive", "needle"),
    ("negative", "missing-marker"),
    ("ambiguous", "alpha"),
]
SAMPLES = 20


def identity(executable):
    with open(executable, "rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    version = (
        subprocess.run(
            [executable, "--version"],
            capture_output=True,
            check=True,
            timeout=5,
            env={"LC_ALL": "C"},
        )
        .stdout.decode()
        .splitlines()[0]
    )
    return {"version": version, "executable_sha256": digest}


def run():
    executables = {name: shutil.which(name) for name in ["rg", "grep"]}
    if not all(executables.values()):
        raise RuntimeError(
            "ENVIRONMENT_BLOCKED: provision rg and grep in the immutable worker"
        )
    identities = {name: identity(path) for name, path in executables.items()}
    records = []
    with tempfile.TemporaryDirectory(prefix="kit-retrieval-") as directory:
        root = Path(directory)
        contents = {}
        for number in range(100):
            name = f"file-{number:03}.txt"
            contents[name] = f"record {number}\nalpha definition\n# alpha comment\n"
            if number % 10 == 0:
                contents[name] += "needle exact hit\n"
        contents[".hidden.txt"] = "needle hidden hit\n"
        contents["space name.txt"] = "alpha string and unicode ä\n"
        for name, text in contents.items():
            (root / name).write_text(text, encoding="utf-8")
        paths = sorted(contents)
        corpus_sha256 = hashlib.sha256(
            json.dumps(contents, sort_keys=True).encode()
        ).hexdigest()
        for classification, query in QUERIES:
            expected = "".join(
                f"{name}:{line}:{text}\n"
                for name in paths
                for line, text in enumerate(contents[name].splitlines(), 1)
                if query in text
            ).encode()
            expected_exit = 0 if expected else 1
            for name, executable in executables.items():
                flags = ["--no-config", "--sort", "path"] if name == "rg" else []
                args = flags + ["--color=never", "-F", "-n", "-H", "--", query] + paths
                raw_ms = []
                for repetition in range(SAMPLES + 1):
                    start = time.perf_counter_ns()
                    result = subprocess.run(
                        [executable, *args],
                        cwd=root,
                        capture_output=True,
                        timeout=5,
                        check=False,
                        env={"LC_ALL": "C"},
                    )
                    elapsed = (time.perf_counter_ns() - start) / 1_000_000
                    if (
                        result.returncode != expected_exit
                        or result.stdout != expected
                        or result.stderr
                    ):
                        raise RuntimeError(
                            f"correctness gate failed: {name}/{classification}"
                        )
                    if repetition:
                        raw_ms.append(elapsed)
                records.append(
                    {
                        "candidate": name,
                        "case": classification,
                        "argv": [name, *args],
                        "samples_ms": raw_ms,
                        "median_ms": statistics.median(raw_ms),
                        "exit_code": expected_exit,
                        "stdout_bytes": len(expected),
                        "result_sha256": hashlib.sha256(expected).hexdigest(),
                        "correct": True,
                    }
                )
    catalog = read_json(ROOT, "inventories/agent-tools.json")["tools"]

    def compact(obj):
        return len(json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode())

    metadata = [{"name": t["name"], "purpose": t["purpose"]} for t in catalog]
    return {
        "$schema": "https://architecture-kit.invalid/schemas/benchmark.schema.json",
        "kind": "synthetic-retrieval",
        "observed_on": datetime.now(timezone.utc).date().isoformat(),
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "catalog_sha256": hashlib.sha256(
            (ROOT / "inventories/agent-tools.json").read_bytes()
        ).hexdigest(),
        "environment": {
            "system": platform.system(),
            "architecture": platform.machine(),
            "python": platform.python_version(),
            "memory_limit_bytes": None,
        },
        "corpus_sha256": corpus_sha256,
        "identities": identities,
        "semantics": "fixed-string, explicit sorted UTF-8 files including hidden; C locale; no symlinks",
        "warmup_runs": 1,
        "samples_per_case": SAMPLES,
        "cache_state": "warm-uncontrolled",
        "estimator": "median of raw wall-clock milliseconds; no tail or confidence claim",
        "records": records,
        "context_bytes": {
            "all_tool_metadata": compact(catalog),
            "discovery_summaries": compact(metadata),
            "initial_tool_metadata": compact(
                [t for t in catalog if t["default_surface"]]
            ),
        },
        "tokens": None,
        "limitations": [
            "synthetic corpus only",
            "process startup included",
            "no real provider evaluation",
            "no schema expansion counted in metadata sizes",
            "no cold-cache or tail-latency evidence",
            "no security-isolation benchmark",
            "no indexing/data-engine comparison",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
