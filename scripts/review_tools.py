"""Check reviewed local tool evidence without executing projects or rewriting lessons."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = "research/harness-tools.json"
SCHEMA = "https://architecture-kit.invalid/schemas/harness-tools.schema.json"
LIMIT = 2 * 1024 * 1024
ROLES = {"tool", "kit", "mirror", "empty", "archive", "preparation"}
FORBIDDEN = {".git", ".ssh", ".gnupg", ".direnv", "node_modules", "__pycache__"}
SUFFIXES = {".md", ".py", ".rs", ".nix", ".json", ".mjs", ".sh", ".jq", ".ts", ".toml"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def relative_path(value):
    require(isinstance(value, str) and 0 < len(value) <= 512, "invalid evidence path")
    require(
        not value.startswith("/")
        and "\\" not in value
        and ":" not in value
        and all(ord(c) >= 32 for c in value)
        and all(p not in {"", ".", ".."} for p in value.split("/")),
        "evidence path must be relative without traversal",
    )
    parts = value.split("/")
    require(
        not any(p in FORBIDDEN or p == ".env" or p.startswith(".env.") for p in parts),
        "credential or generated paths are not evidence",
    )
    return value


def local_path(root, relative):
    path = root
    for part in relative_path(relative).split("/"):
        path /= part
        require(not path.is_symlink(), "symlink is not evidence")
    return path


def read_file(root, relative):
    path = local_path(root, relative)
    require(
        path.suffix in SUFFIXES or path.name == "flake.lock",
        "unsupported evidence file",
    )
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        require(
            stat.S_ISREG(info.st_mode) and info.st_size <= LIMIT,
            "evidence must be a bounded regular file",
        )
        raw = stream.read(LIMIT + 1)
        after = os.fstat(stream.fileno())
    require(len(raw) <= LIMIT, "evidence exceeded its read budget")
    require(
        (info.st_size, info.st_mtime_ns) == (after.st_size, after.st_mtime_ns),
        "evidence changed while being read",
    )
    return raw


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate register key")
        result[key] = value
    return result


def validate(root):
    document = json.loads(read_file(root, REGISTER), object_pairs_hook=unique_object)
    require(
        document["$schema"] == SCHEMA and document["version"] == 1,
        "unsupported register",
    )
    require(
        date.fromisoformat(document["reviewed_on"]) <= date.today(),
        "review date is in the future",
    )
    sources = document["sources"]
    lessons = document["lessons"]
    require(
        0 < len(sources) <= 64 and 0 < len(lessons) <= 32,
        "register size exceeds its budget",
    )
    identities = set()
    checkouts = set()
    for source in sources:
        identity = source["id"]
        require(
            re.fullmatch(r"[a-z][a-z0-9-]{0,63}", identity), "invalid source identity"
        )
        require(identity not in identities, "duplicate source identity")
        identities.add(identity)
        checkout = relative_path(source["checkout"])
        require(
            len(checkout.split("/")) == 2
            and checkout.split("/")[0] in {"public", "private"},
            "checkout must name an immediate collection directory",
        )
        require(checkout not in checkouts, "duplicate checkout")
        checkouts.add(checkout)
        role = source["role"]
        require(role in ROLES, "unknown source role")
        require(
            bool(source["purpose"].strip()) and bool(source["observation"].strip()),
            "source needs a purpose and observation",
        )
        files = source["files"]
        require(len(files) <= 16, "too many selected evidence files")
        require(
            bool(files) == (role not in {"kit", "empty"}),
            "source role/evidence mismatch",
        )
        validate_receipts(files)
    validate_receipts(document["collection_files"])
    require(
        "README.md" in document["collection_files"],
        "canonical source map must be bound",
    )
    lesson_ids = set()
    used_sources = set()
    for lesson in lessons:
        require(re.fullmatch(r"L[0-9]{2}", lesson["id"]), "invalid lesson identity")
        require(lesson["id"] not in lesson_ids, "duplicate lesson identity")
        lesson_ids.add(lesson["id"])
        require(bool(lesson["claim"].strip()), "lesson needs a claim")
        require(
            bool(lesson["sources"]) and set(lesson["sources"]) <= identities,
            "unknown or missing lesson source",
        )
        used_sources.update(lesson["sources"])
        require(bool(lesson["adopted_in"]), "lesson needs an adoption location")
        for target in lesson["adopted_in"]:
            path, _, anchor = target.partition("#")
            text = read_file(root, path).decode("utf-8")
            if anchor:
                # Explicit anchors remain stable when a heading is rewritten.
                require(
                    f'<a id="{anchor}"></a>' in text, "missing lesson adoption anchor"
                )
    require(
        {s["id"] for s in sources if s["role"] == "tool"} <= used_sources,
        "every canonical tool needs a reviewed lesson",
    )
    return document


def validate_receipts(files):
    require(isinstance(files, dict), "evidence receipts must be a path/digest map")
    for path, digest in files.items():
        relative_path(path)
        require(
            isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest),
            "invalid evidence digest",
        )


def inspect_sources(document, root, *, capture=False, source_map=None):
    """Return metadata only. A capture is a proposal, never an accepted review."""
    problems = []
    receipts = {}
    expected = {s["checkout"] for s in document["sources"]}
    actual = set()
    for area in ("public", "private"):
        directory = local_path(root, area)
        require(directory.is_dir(), "collection needs public and private directories")
        with os.scandir(directory) as entries:
            for index, entry in enumerate(entries):
                require(index < 256, "too many collection entries")
                if entry.name.startswith("."):
                    continue
                require(not entry.is_symlink(), "symlink in collection inventory")
                if entry.is_dir(follow_symlinks=False):
                    actual.add(f"{area}/{entry.name}")
    for checkout in sorted(actual ^ expected):
        problems.append(
            {
                "checkout": checkout,
                "status": "unreviewed" if checkout in actual else "missing",
            }
        )

    def compare(prefix, files):
        current = {}
        for path, digest in files.items():
            relative = f"{prefix}/{path}" if prefix else path
            try:
                if not prefix and path == "README.md" and source_map is not None:
                    raw = read_file(
                        source_map.parent.resolve(strict=True), source_map.name
                    )
                else:
                    raw = read_file(root, relative)
                current[path] = hashlib.sha256(raw).hexdigest()
                if current[path] != digest:
                    problems.append({"path": relative, "status": "changed"})
            except (OSError, ValueError):
                problems.append({"path": relative, "status": "unavailable"})
        return current

    receipts["collection_files"] = compare("", document["collection_files"])
    receipts["sources"] = {}
    for source in document["sources"]:
        checkout = source["checkout"]
        if checkout not in actual:
            continue
        if source["role"] == "empty":
            with os.scandir(local_path(root, checkout)) as entries:
                if next(entries, None) is not None:
                    problems.append({"checkout": checkout, "status": "no-longer-empty"})
        receipts["sources"][source["id"]] = compare(checkout, source["files"])
    result = {
        "status": "stale" if problems else "selected-evidence-current",
        "reviewed_on": document["reviewed_on"],
        "explicit_source_map": source_map is not None,
        "scope": "Immediate directory inventory and explicitly selected file bytes; no runtime verification.",
        "problems": problems,
    }
    if capture:
        result["candidate_receipts"] = receipts
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sources-root",
        type=Path,
        help="Explicit local collection root; never retained",
    )
    parser.add_argument(
        "--source-map",
        type=Path,
        help="Explicit regular Markdown source map when the collection README is a symlink",
    )
    parser.add_argument(
        "--capture",
        action="store_true",
        help="Print candidate hashes; never write or accept a review",
    )
    args = parser.parse_args(argv)
    try:
        require(
            not args.capture or args.sources_root is not None,
            "capture needs an explicit sources root",
        )
        require(
            args.source_map is None or args.sources_root is not None,
            "source map needs a sources root",
        )
        require(
            args.source_map is None or args.source_map.suffix == ".md",
            "source map must be Markdown",
        )
        document = validate(ROOT)
        result = (
            inspect_sources(
                document,
                args.sources_root.resolve(strict=True),
                capture=args.capture,
                source_map=args.source_map,
            )
            if args.sources_root
            else {
                "status": "register-valid",
                "sources": len(document["sources"]),
                "lessons": len(document["lessons"]),
                "external_sources_checked": False,
            }
        )
        print(json.dumps(result, indent=2))
        return 1 if result["status"] == "stale" else 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        # Parser and filesystem diagnostics can contain private values or paths.
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": "Invalid register or unavailable bounded local evidence.",
                }
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
