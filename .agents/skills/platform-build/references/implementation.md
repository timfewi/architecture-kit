# Implementation decisions

Start from STARTER.md and the existing agent-config, runtime-contracts and
tool-contracts schemas. Preserve their ownership and evidence levels. This kit
contains declarations and synthetic replay; verify every claimed runtime against
actual source, processes and tests in the clone.

For a coding-focused first milestone, use FAST-START.md to select the initial
operations and evidence sequence. It is an ordering guide over the same
contracts, not a reduced runtime or a source implementation.

## A small implementation

Select a repository-native stack at the implementation-design work item. Prefer
one core language and a small number of modules with clear owners over a package
per tool. Choose exact stable dependency revisions from authoritative current
documentation, record the source and date, and commit generated locks through
the repository's normal workflow. Existing candidates are not installed packages.
No new runtime dependency is selected by this bootstrap kit.

Group implementation around policy/registry, broker/execution, lifecycle/evidence,
adapters and optional consumers. Generate transport views from canonical contracts.
Reuse the reference scenario oracles with real producers and consumers; adapters
must never obtain extra authority through their native tools.

Resolve the six platform.services capabilities against the target host:
supervision, credential mediation, policy store, workspace isolation, private IPC
and durable store. Probe exact required guarantees. If a capability is absent,
identify the dependent requirement and the host-side prerequisite; do not implement
a silent unrestricted fallback. The host may be unrelated to the system that
authored this kit. Basic source work must not depend on those runtime services.

## Reuse assessment

If existing code is supplied for consideration, record its source revision,
license, module boundary, dependency closure, retained code size, test quality,
portability risks and estimated adaptation cost. Compare reuse, a small rewrite
and omission. Produce a separate recommendation; do not copy code as part of
the assessment. Private guidance is not automatically eligible for publication.

## Checks

Each real integration check declares producer, consumer, contract, tests,
fixtures, environment identity and behavior-affecting configuration as inputs.
Prefer directory inputs when additions must invalidate the result. Explain
omissions. A hash change requests review; it must not automatically regenerate
expected behavior. Keep real contract compatibility and domain effects distinct.

The current runner inherits only PATH and its explicitly fixed locale/Python
settings. A check needing additional services or environment belongs in a reviewed
host launcher with a declared identity; do not add arbitrary secret passthrough.

For the final profile, exercise source, focused, build and live gates with actual
platform owners. Two real independent adapters plus a synthetic third establish
the adapter portability milestone. User interfaces consume the same neutral
contracts; they never become state, authority or completion owners.
