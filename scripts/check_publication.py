"""Reject common private data and credential forms in reusable kit artifacts."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

IGNORED_DIRECTORIES = {
    ".git",
    ".direnv",
    ".ruff_cache",
    "__pycache__",
    ".pytest_cache",
}
SENSITIVE_NAMES = {
    ".env",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "id_rsa",
}
SENSITIVE_SUFFIXES = {".key", ".p12", ".pem", ".pfx"}


def rules():
    # Split signatures keep the scanner's own source from matching its rules.
    return {
        "Unix home-directory path": re.compile(
            rb"/" + rb"(?:home|Users)/[A-Za-z0-9._-]+/"
        ),
        "Windows user-directory path": re.compile(
            rb"[A-Za-z]:" + rb"[\\/]+Users[\\/]+[^\\/\s]+[\\/]"
        ),
        "email address": re.compile(
            rb"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
            rb"@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
            rb"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+"
        ),
        "private-key marker": re.compile(
            rb"BEGIN " + rb"(?:RSA |EC |OPENSSH )?PRIVATE KEY"
        ),
        "AWS access-key identifier": re.compile(rb"AK" + rb"IA[0-9A-Z]{16}"),
        "GitHub token": re.compile(rb"gh" + rb"[pousr]_[A-Za-z0-9_]{20,}"),
        "OpenAI-style secret key": re.compile(
            rb"sk" + rb"-(?:[A-Za-z0-9]{32,}|(?:proj|svcacct)-[A-Za-z0-9_-]{20,})"
        ),
    }


def source_files(root):
    for path in sorted(root.rglob("*")):
        if any(part in IGNORED_DIRECTORIES for part in path.relative_to(root).parts):
            continue
        if path.is_file() and not path.is_symlink():
            yield path


def findings(root):
    result = []
    patterns = rules()
    for path in source_files(root):
        relative = path.relative_to(root).as_posix()
        if path.name in SENSITIVE_NAMES or path.suffix.lower() in SENSITIVE_SUFFIXES:
            result.append((relative, "secret-bearing filename", None))
        raw = path.read_bytes()
        for label, pattern in patterns.items():
            for match in pattern.finditer(raw):
                line = raw.count(b"\n", 0, match.start()) + 1
                result.append((relative, label, line))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    root = args.root.resolve()
    problems = findings(root)
    for path, label, line in problems:
        location = f"{path}:{line}" if line is not None else path
        print(f"{location}: {label}")
    if problems:
        raise SystemExit(f"privacy check failed with {len(problems)} finding(s)")
    print("Privacy check passed for reusable kit artifacts.")


if __name__ == "__main__":
    main()
