set shell := ["sh", "-eu", "-c"]
set dotenv-load := false

# List available commands.
default:
    @just --list

# Full kit acceptance; missing validator dependencies are an error.
check: lint format-check privacy-check test test-bootstrap verify

# Narrow checks without the JSON Schema validator; not full acceptance.
check-fast: lint format-check privacy-check test-semantics test-runtime-semantics test-skills test-bootstrap structural

# Lint Python and the Direnv entry point without executing .envrc.
lint:
    ruff check --isolated --select E4,E7,E9,F,I,PLW1510 scripts tests .agents
    shellcheck --shell=bash .envrc

# Check formatting without changing files.
format-check:
    ruff format --isolated --check scripts tests .agents
    nixfmt --check flake.nix
    just --fmt --check

# Format source files; review changes before refreshing the manifest.
format:
    ruff format --isolated scripts tests .agents
    nixfmt flake.nix
    just --fmt

# Reject common personal paths, credentials and secret-bearing file types.
privacy-check:
    python3 -B scripts/check_publication.py

# Audit local release prerequisites without publishing or changing visibility.
release-audit:
    python3 -B scripts/check_release.py

# Run semantic and full JSON Schema regression tests.
test:
    python3 -B -m unittest discover -s tests

# Run only the independent semantic regressions.
test-semantics:
    python3 -B -m unittest discover -s tests -p 'test_semantics.py'

# Replay synthetic starter contracts and their independent negative cases.
test-runtime-semantics:
    python3 -B -m unittest discover -s tests -p 'test_runtime_semantics.py'

# Rebuild synthetic reference data after reviewed contract/example changes.
refresh-reference:
    python3 -B scripts/make_reference.py

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

# Portable skill catalog and package checks.
check-skills:
    python3 -B scripts/check_skills.py

test-skills:
    python3 -B -m unittest discover -s tests -p 'test_skills.py'

refresh-skills:
    python3 -B scripts/check_skills.py --refresh

# Temporary build assistance; remove this recipe at retirement.
test-bootstrap:
    python3 -B -m unittest discover -s .agents/tests

# Optional host-provided security gate; project-check is not a Nixpkgs dependency.
baseline:
    project-check baseline
