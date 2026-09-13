set shell := ["sh", "-eu", "-c"]
set dotenv-load := false

# List available commands.
default:
    @just --list

# Full kit acceptance; missing validator dependencies are an error.
check: lint format-check test verify

# Narrow checks without the JSON Schema validator; not full acceptance.
check-fast: lint format-check test-semantics structural

# Lint Python and the Direnv entry point without executing .envrc.
lint:
    ruff check --isolated --select E4,E7,E9,F,I,PLW1510 scripts tests
    shellcheck --shell=bash .envrc

# Check formatting without changing files.
format-check:
    ruff format --isolated --check scripts tests
    nixfmt --check flake.nix
    just --fmt --check

# Format source files; review changes before refreshing the manifest.
format:
    ruff format --isolated scripts tests
    nixfmt flake.nix
    just --fmt

# Run semantic and full JSON Schema regression tests.
test:
    python3 -B -m unittest discover -s tests

# Run only the independent semantic regressions.
test-semantics:
    python3 -B -m unittest discover -s tests -p 'test_semantics.py'

# Validate manifest, semantics and all JSON Schema contracts.
verify:
    python3 -B scripts/check_kit.py

# Check integrity and semantics without claiming JSON Schema coverage.
structural:
    python3 -B scripts/check_kit.py --structural

# Refresh derived hashes only after intentional, reviewed source changes.
refresh-manifest:
    python3 -B scripts/check_kit.py --refresh-manifest

# Print a fresh synthetic measurement; do not overwrite accepted evidence.
benchmark:
    python3 -B scripts/benchmark_retrieval.py

# Optional host-provided security gate; project-check is not a Nixpkgs dependency.
baseline:
    project-check baseline
