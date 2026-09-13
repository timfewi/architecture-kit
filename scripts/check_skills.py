"""Validate portable SKILL.md packages and their derived metadata catalog."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def metadata(text):
    parts = text.split("---\n", 2)
    require(len(parts) == 3 and parts[0] == "", "missing skill frontmatter")

    class Loader(yaml.SafeLoader):
        pass

    def mapping(loader, node):
        result = {}
        for key, value in node.value:
            name = loader.construct_object(key)
            require(
                isinstance(name, str) and name not in result,
                "duplicate/invalid metadata key",
            )
            result[name] = loader.construct_object(value)
        return result

    Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    require(
        not any(isinstance(e, yaml.events.AliasEvent) for e in yaml.parse(parts[1])),
        "skill aliases forbidden",
    )
    data = yaml.load(parts[1], Loader=Loader)
    require(isinstance(data, dict), "invalid skill metadata")
    require(
        set(data) <= {"name", "description", "metadata", "license", "compatibility"},
        "unsupported metadata",
    )
    require(
        isinstance(data.get("name"), str)
        and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", data["name"])
        and len(data["name"]) <= 64,
        "invalid skill name",
    )
    require(
        isinstance(data.get("description"), str)
        and 0 < len(data["description"]) <= 1024,
        "invalid skill description",
    )
    extra = data.get("metadata", {})
    require(
        isinstance(extra, dict)
        and all(isinstance(k, str) and isinstance(v, str) for k, v in extra.items()),
        "metadata must be string pairs",
    )
    require(
        parts[2].strip() and len(text.splitlines()) < 500, "empty/oversized skill body"
    )
    return data, parts[2]


def skill_entry(directory, root):
    require(not directory.is_symlink(), "symlink skill directory")
    source = directory / "SKILL.md"
    require(source.is_file() and not source.is_symlink(), "missing/linked SKILL.md")
    raw = source.read_bytes()
    require(len(raw) <= 64000, "skill too large")
    data, body = metadata(raw.decode("utf-8"))
    require(data["name"] == directory.name, "skill name/path mismatch")
    files = {}
    for path in sorted(directory.rglob("*")):
        require(not path.is_symlink(), "symlink skill resource")
        if path.is_file():
            require(path.stat().st_size <= 2 * 1024 * 1024, "oversized resource")
            files[path.relative_to(directory).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    require(len(files) <= 100, "too many skill resources")
    for link in re.findall(r"\]\(([^)]+)\)", body):
        if link.startswith(("https://", "#")):
            continue
        name = link.split("#", 1)[0]
        require(
            name in files and all(p not in {"", ".", ".."} for p in name.split("/")),
            f"missing/escaping skill reference: {name}",
        )
    extra = data.get("metadata", {})
    capabilities = (
        extra.get("capabilities", "").split(",") if extra.get("capabilities") else []
    )
    require(len(set(capabilities)) == len(capabilities), "duplicate capability hint")
    return {
        "name": data["name"],
        "description": data["description"],
        "path": source.relative_to(root).as_posix(),
        "provenance": extra.get("provenance", "unspecified"),
        "capabilities": capabilities,
        "files": files,
        "content_sha256": hashlib.sha256(
            json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }


def catalog(root):
    directory = root / "skills"
    require(
        directory.is_dir() and not directory.is_symlink(), "invalid skill package root"
    )
    entries = [skill_entry(p, root) for p in sorted(directory.iterdir()) if p.is_dir()]
    require(entries and len(entries) <= 100, "invalid skill count")
    return {"format": "portable-skill-catalog-v1", "skills": entries}


def check(root):
    expected = catalog(root)
    path = root / "skills/catalog.json"
    require(not path.is_symlink(), "symlink catalog")
    require(
        json.loads(path.read_text(encoding="utf-8")) == expected,
        "skill catalog drift; review then refresh",
    )
    names = {s["name"] for s in expected["skills"]}
    pilot = json.loads((root / "skills/routing-pilot.json").read_text(encoding="utf-8"))
    require(
        all(set(case["expected"]) <= names for case in pilot["cases"]),
        "unknown routing-pilot skill",
    )
    return expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    try:
        if args.refresh:
            value = catalog(ROOT)
            target = ROOT / "skills/catalog.json"
            require(not target.is_symlink(), "symlink catalog")
            target.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
            print("Refreshed skill catalog; no behavioral evidence issued.")
        else:
            value = check(ROOT)
            print(
                json.dumps(
                    {
                        "status": "passed",
                        "skills": len(value["skills"]),
                        "coverage": "metadata-resources-catalog",
                    }
                )
            )
        return 0
    except (ValueError, OSError, yaml.YAMLError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
