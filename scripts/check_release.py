"""Audit local open-source release prerequisites without publishing anything."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

if __package__:
    from . import check_publication
else:
    import check_publication

REQUIRED_POLICIES = {
    "README.md",
    "CHANGELOG.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "OPEN_SOURCE.md",
    "SECURITY.md",
}
LICENSE_NAMES = {"COPYING", "LICENSE", "LICENSE.md", "LICENSE.txt"}


def audit(root):
    failures = []
    for name in sorted(REQUIRED_POLICIES):
        path = root / name
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            failures.append(f"missing or empty policy: {name}")

    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        failures.append("missing manifest.json")
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            failures.append(f"invalid manifest.json: {error}")
        else:
            if manifest.get("language") != "en":
                failures.append("manifest language must be en")

    if not any((root / name).is_file() for name in LICENSE_NAMES):
        failures.append("missing release license")

    for path, label, line in check_publication.findings(root):
        location = f"{path}:{line}" if line is not None else path
        failures.append(f"privacy finding: {location}: {label}")
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    problems = audit(args.root.resolve())
    for problem in problems:
        print(problem)
    if problems:
        raise SystemExit(f"release audit failed with {len(problems)} blocker(s)")
    print("Local release prerequisites passed; no publication was performed.")


if __name__ == "__main__":
    main()
