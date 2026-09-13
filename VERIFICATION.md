# Verification and evidence contract

Verification is part of the architecture. The host controller owns the
requirement matrix and completion decision; a model may report evidence but may
not promote or close it.

## Evidence levels

| Level | Proves |
| --- | --- |
| Source | The intended declaration and static invariants exist. |
| Focused test | One bounded contract behaves under its fixtures. |
| Build | Exact source and inputs produce the intended artifact. |
| Activation | The artifact is installed and its services start. |
| Live | The running system performs the intended realistic operation. |
| Release | Required supported-host, rollback, packaging, and fresh-session gates pass together. |

Evidence never automatically promotes to a higher level.

## Required evidence identity

Every accepted record binds requirement, source snapshot, policy, toolchain,
registry/schema, profile, operation or check, exit and result classification,
output digest, relevant bounded observation, timestamp, evidence level, and
remaining risk. A changed binding invalidates only dependent evidence.

## Status vocabulary

- passed: the exact requirement passed at the stated level;
- failed: behavior contradicted the requirement;
- blocked: required environment, authority, input, or external state was absent;
- cancelled: work was intentionally stopped before settlement;
- outcome_uncertain: dispatch occurred but the durable outcome is not yet known;
- not_applicable: the selected profile excludes the requirement.

Blocked, cancelled, uncertain, and not-applicable are never aliases for passed.

## Controller completion rule

The controller may enter COMPLETE only when every selected requirement is
passed at its declared minimum level or explicitly not applicable. It rejects
model-authored completion, stale receipts, changed source, missing required
gates, and broad claims derived from narrow tests.

WAITING_EXTERNAL is used when an exact build, approval, provider job, or operator
action can advance the matrix. No model turn runs in that state. BLOCKED is used
only when no executable authorized next step exists.

## Verification layers

Static and source gates cover secrets, machine-state exclusion, formatting,
linting, types, shell and policy scanners, dependency pins, inventory, safe
source materialization, schema parity, and path boundaries.

Runtime gates cover policy combinations, approvals, tool dispatch, workspace
grants, process cleanup, deadlines, retry fingerprints, goal-state transitions,
harness parity, provider isolation, memory freshness, index generations,
coordination, observation, and client projections.

Build and activation gates cover exact closures, installed executables, service
sockets, ownership, cgroups, egress, secret paths, rollback, and fresh sessions.

Live and release gates cover providers, browser and terminal interaction,
multi-agent communication, workload budgets, performance regressions, VMs,
installer behavior, supported platforms, and recovery.

## Key negative scenarios

Verification includes denial of private paths and credentials, authority
escalation, stale grants, duplicate approvals, deterministic retry, changed
continuation input, foreign workspace identity, provider redirect, process
escape, descendant leaks, observation backpressure, peer discovery without
scope, Agent Card over-disclosure, first-party privilege, work during external
wait, and completion without evidence.

## Performance and cost evidence

Performance comparisons freeze task oracle, source, model, harness, policy,
schema, toolchain, resource limits, and warm/cold state. They include failures,
cancellation, queue time, setup, verification, delegated work, retries,
model-visible bytes, and external cost. Unknown provider counters stay unknown.

Sample count, estimator, confidence method, and stopping rule are declared
before measurement. A small exploratory sample cannot establish tail latency.
Correctness and security pass before latency or token comparisons are accepted.

## Handoff

A handoff reports the selected profile, satisfied requirements, evidence
identities, unresolved blockers, uncertain outcomes, external requests, budget
consumed, changed source summary, and first executable next action. It links
large logs or artifacts by digest instead of embedding them.

## Checking this kit

The requirement matrix for the kit is separate from deployment acceptance:

| Requirement | Local evidence |
| --- | --- |
| Stable architecture names and portable profiles | Generic IDs, transitive component closure and reference-host exclusion check. |
| Precise tools and software choices | 51 referenced input contracts, shared result schemas, capability/effect parity, 22 conditional software choices. |
| Strict shape and cross-file semantics | Full Draft 2020-12 validation plus independent parser, ID, dependency, transition, path and result cross-field checks. |
| Research-backed selection | Primary-source register, inspected coverage and explicit unsupported claims in research/FINDINGS.md. |
| Honest efficiency evidence | Raw synthetic retrieval samples, executable/runner/corpus identities and separate metadata byte counts; tokens remain unavailable. |
| Single-agent starter | Closed config/runtime schemas, catalog/binding parity, nine synthetic replays and independent negative mutations; no provider, broker, database or isolation implementation. |
| Reproducible package contents | Exact artifact hashes, sizes, references and deterministic manifest comparison. |

The local checker does not implement or simulate the 51 runtime handlers.
It now replays supplied starter events in memory to check cross-record
invariants; this is not actual model/tool execution or durable storage recovery.
See [STARTER.md](STARTER.md) for the requirement-to-evidence matrix.
The 51 input examples and ten shared result examples are checked by full mode.
Schema negatives cover closed shapes, required fields, cursor inputs, status
contradictions, successful-build artifacts and mutually exclusive process exits.
Independent semantic tests cover counts, UTF-8 windows, anchors, table widths
and cursor source/consumer consistency. Positive/negative fixtures prove schema
acceptance only after the standard validator actually runs. They cannot prove grant checks, filesystem race
resistance, DNS policy, cancellation or deployment.

[DEVELOPMENT.md](DEVELOPMENT.md) documents the optional pinned environment.
`just check` combines the generic acceptance commands; `just baseline` is
the separately supplied host security gate. The Justfile also checks Nix
formatting and statically lints .envrc without executing it.

Run these commands in a provisioned isolated environment:

```sh
ruff check --isolated --select E4,E7,E9,F,I,PLW1510 scripts tests
ruff format --isolated --check scripts tests
python3 -B -m unittest discover -s tests -p 'test_semantics.py'
python3 -B -m unittest discover -s tests -p 'test_runtime_semantics.py'
python3 -B scripts/check_kit.py --structural
python3 -B scripts/check_kit.py
python3 -B -m unittest discover -s tests -p 'test_schemas.py'
project-check baseline
```

The full validator requires jsonschema 4.26.0 and its resolved dependencies.
PyYAML 6.0.3 parses profiles with duplicate keys, aliases and merge keys rejected.
All schema references resolve in memory; a missing reference cannot fetch data.
The timestamp contract restricts date-time to UTC with optional microseconds and
no leap seconds; an explicit format checker enforces that subset.

Ruff checks formatting, imports and common Python defects. No static type checker
or type-check configuration existed in the supplied kit; type-check coverage is
not claimed. The installed baseline scanner covers selected Python security
patterns, not JSON Schema or deployment. Report its actual file/rule/parser
coverage, including excluded test fixtures, with the result.

A missing validator is an environment blocker for the full suite. Structural
checks are available independently and identify excluded coverage. Do not
replace the missing validator with a permissive schema imitation, skip failing
contract tests, or call a structural pass full schema verification.

Run the benchmark separately when the candidate/workload changes. Store accepted
raw receipts, never fabricated token counters. Do not rerun expensive unchanged
work merely to produce another receipt.
