# Architecture kit

A reusable reference architecture for agent systems: a portable core, optional
Linux host profiles, precise tool contracts, and an evidence-based selection
process. It specifies what an implementation must demonstrate. It does not
claim that a runtime, isolation policy, or performance improvement is deployed.

For a host-free single-agent starting point, use [STARTER.md](STARTER.md), the
[agent-starter profile](profiles/agent-starter.yaml) and the
[resolved configuration example](examples/agent-config.json). Host and Home
Manager setup can remain in separate repositories.

Use [TOOLING.md](TOOLING.md) for concrete tool choices and
[research/FINDINGS.md](research/FINDINGS.md) for sources, comparisons and limits.
Choose a target in [profiles/](profiles/), then use
[ARCHITECTURE.md](ARCHITECTURE.md) and [REBUILD-GUIDE.md](REBUILD-GUIDE.md).
[VERIFICATION.md](VERIFICATION.md) distinguishes kit checks from runtime proof.

<!-- bootstrap-start -->
To turn repeated clones into an implementation project, start with
[the temporary build assistance](.agents/README.md). It supplies resumable work
items and local check helpers, not a platform runtime or agent launcher.
<!-- bootstrap-end -->

[Portable operating skills](skills/README.md) remain useful after implementation
and can be loaded as ordinary files on an independent host.

## What is included

- 51 transport-neutral reference operations with explicit input and result
  contracts; 13 are initially visible. `tools.search` discovers optional
  operations and `tools.describe` loads one definition.
- Closed JSON Schema contracts, bounded values, shared definitions, typed
  errors, provenance, completeness, freshness and continuation.
- Component dependencies, configurable controller budgets, optional Linux
  choices, a measurement contract, 51 synthetic input examples and ten shared
  [result examples](examples/tool-results.json).
- Typed launch, task/run/event, adapter, grant/approval, dispatch, receipt and
  resume contracts, concrete context/cost/storage policies, and nine complete
  [synthetic reference scenarios](examples/reference-run.json).
- A local integrity/semantic checker and a full standards-based schema check.

This is a specification and verification toolkit, not an agent runtime. Tool
names describe proposed capabilities. A live registry still decides which
implementations and authorities are available.

## Profiles

| Profile | Use |
| --- | --- |
| `agent-starter` | Minimal single-agent core, explicit extensions, no Host/Home Manager implementation. |
| `agent-platform` | Portable core on any host satisfying `platform.services`; no desktop or NixOS dependency. |
| `host-foundation` | Optional declarative Linux/NixOS reference host. |
| `greenfield-minimal` | Small reference laptop and essential agent services. |
| `full-workstation` | All selected client, research, voice and VM roles. |

Resolve component dependencies transitively. Optional components are checked for
compatibility but activate only when explicitly selected. A dependency in `excludes` or
`defer` is an error, not an implicit override. Profiles select requirements;
they do not grant authority or demonstrate availability.

## Stable names and reproducibility

Architecture and interface names have no generation suffix. Content digests
identify snapshots. The JSON Schema dialect remains explicitly pinned to Draft
2020-12; upstream protocol identifiers and executable versions retain their
technical meaning. Schema IDs use `https://architecture-kit.invalid/schemas/`
as an offline namespace, never as a network endpoint. Artifact and decision
references are relative to the kit root; JSON Schema `$ref` follows standard
URI resolution against `$id`.

A changed schema digest requires compatibility validation of saved examples and
consumers. Never silently reinterpret stored data. Reject incompatible data or
use an explicit conversion bound to both old and new schema digests.

## Local checks

A pinned [Flake, Direnv entry point and Just recipes](DEVELOPMENT.md) provide
the optional Linux development environment. After its reviewed host setup,
use `just check` for full acceptance or `just check-fast` for explicitly
narrower coverage. Initial lock generation/provisioning is a separate step.

The underlying commands remain usable in any approved equivalent environment:

```sh
python3 -B scripts/check_kit.py --structural
python3 -B -m unittest discover -s tests -p 'test_semantics.py'
python3 -B -m unittest discover -s tests -p 'test_runtime_semantics.py'
python3 -B scripts/check_kit.py
python3 -B -m unittest discover -s tests -p 'test_schemas.py'
```

The full check requires the exact validator dependencies listed in
`requirements.txt`, supplied by a reviewed immutable environment. It never
downloads dependencies or resolves schemas over the network. Missing validator
dependencies are a blocker for the full check; the structural command reports
its narrower coverage explicitly.

After intentional kit changes, refresh only the derived manifest:

```sh
python3 -B scripts/check_kit.py --refresh-manifest
```

Inventories, contracts and Markdown are source files. The manifest is derived;
its own bytes are excluded from its artifact list to avoid a self-hash cycle.
The local check validates references, metadata parity and content hashes.

## Context strategy

Keep current policy, goal, selected requirements and a short resume packet in
context. Search compact capability metadata before loading schemas. Compute
counts, joins and projections locally, then expose required evidence with
anchors. An exhaustive request remains exhaustive even when presentation is
paged. Measure whole-task quality, tokens, bytes, latency and repair work before
claiming an optimization.

English is used for reusable contracts and documentation. The research includes
concrete adoption criteria; no numeric savings or universal fastest-tool claim
is assumed.
