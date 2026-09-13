# Greenfield rebuild guide

This guide turns the architecture into an implementation program. It is
technology-neutral except that NixOS/Linux is the reference host.

## Start with a profile

Choose exactly one profile and resolve its component dependencies. For the
smallest agent platform on existing infrastructure, use `agent-starter` and
[STARTER.md](STARTER.md). It leaves Host and Home Manager implementations in
their own repositories and defines only the required service interfaces.
Use `greenfield-minimal` for the reference laptop, or `agent-platform`
for the broader portable capability set. Use
`full-workstation` only when the optional research, browser, voice, client, and
VM surfaces are needed.

Before implementation, create a requirement-to-evidence matrix from the selected
profile, ADR references, component dependencies, and verification gates. Do not
interpret an unselected component as a missing requirement.

## Validate the kit first

Run the local checks in README.md, select one profile and resolve its dependency
closure. Implement only selected components. The phases below express dependency
order; an agent-starter or agent-platform deployment uses existing host services instead of
rebuilding the reference laptop. Optional clients and services are not required
to prove a minimal core. Refer to TOOLING.md for exact operation contracts.

The host-free starter skips phases 1 and 10. Reviewed builds, additional harnesses,
coordination and richer clients are selected extensions or later proof milestones,
not prerequisites for the synthetic starter contract suite.

## Phase 1 — Declarative host foundation

Establish pinned inputs, host/user composition, hardware separation, storage,
rollback, owner-only state roots, encrypted-secret deployment, and a minimal
development toolchain.

Completion evidence: source safety, evaluation, build, explicit activation,
rollback, and a fresh-session host observation.

## Phase 2 — Policy, launcher, and workspace identity

Implement canonical repository and worktree identity, workspace grants,
immutable launch policy, authority algebra, state-root overlap checks, resource
ceilings, and deterministic registry selection.

Completion evidence: policy combination fixtures, digest stability, path and
grant negative cases, and installed launch preview.

## Phase 3 — Isolated execution and lifecycle

Implement safe source materialization, read-only Git metadata, fresh no-network
workers, exact writable paths, argv-only execution, toolchain receipts, process
supervision, deadlines, cancellation, descendant reaping, and uncertain-outcome
reconciliation. Add the typed reviewed build boundary so an exact
source-bound registered recipe can be built by the host without exposing a general
build daemon or shell to the agent.

Completion evidence: installed worker self-check, hostile path fixtures,
resource exhaustion, parent-death, timeout, cancellation, zero process growth,
and correlated positive and negative build request/result cases.

## Phase 4 — Canonical definitions and broker

Create one typed definition source and derive policy, catalog, schemas, result
contracts, receipts, inventory, and adapter views. Add exact approvals and
bounded local transport.

Completion evidence: deterministic registry digest, closed-schema tests,
duplicate/unknown rejection, approval replay denial, and result-bound tests.

## Phase 5 — Harness and model boundary

Implement the immutable harness registry, neutral adapter contract, host model
gateway, provider bindings, session retention, output/usage normalization, and
one registered adapter for starter integration. The stronger portability
milestone adds at least two independent external adapters.

Completion evidence: two real adapters plus a synthetic third, multiple
provider shapes, credential isolation, cancellation, resume, approval, and
identical tool-policy parity.

## Phase 6 — Required controller and optional first-party loop

The goal controller, context/resume owner and receipts are required independently
of which harness supplies the loop. Implement these for every starter. If a
first-party loop is selected, add it as an ordinary adapter with turn sequencing,
streaming, tool correlation, context budgeting, compaction, explicit finish
reasons, and local recovery. Add the host-owned goal controller, step receipts,
progress deltas, retry fingerprints, WAITING_EXTERNAL, and finite slice budgets.
Limit automatic context to policy, active goal, selected requirement matrix, and
one digest-bound resume packet. Decompose large implementation handoffs into
bounded issues and retire them from active context after settlement.

Completion evidence: mixed-harness operation, illegal state-transition denial,
no-turn external waiting, unchanged-retry refusal, exact budget stops, approval
continuation, controller-owned completion, digest mismatch rejection, and
bounded fresh-launch/resume/compaction context.

## Phase 7 — Progressive capability families

Add dynamic workspaces, precise retrieval, skills, runtime documentation,
research, browser, compute, WASM, artifacts, verification receipts, and reviewed
memory in that order. Keep each family absent unless selected.

Completion evidence: family-specific authority, stale-input, continuation,
cleanup, privacy, and resource tests. No optional capability expands the
default coding profile.

## Phase 8 — Coordination and observation

Basic observation can project the single-agent run log without coordination.
Add the following only when multi-agent coordination is selected.

Implement host-issued agent profiles, finite scheduler buckets, grant-scoped
peer directory, durable coordination ledger, Agent Cards, optional A2A
projection, asynchronous observation, deterministic reducers, snapshot/cursor
recovery, and typed controls.

Completion evidence: mixed-profile saturation, multi-workspace isolation,
revocation, uncertain dispatch, one atomic claimant, slow/stopped collector, and
resynchronization tests.

## Phase 9 — Product clients

Implement Focus, Swarm, and Observe once as shared contracts. Build terminal and
web clients as presentations over those contracts, with shared theme tokens,
accessibility, and keyboard-reachable parity.

Completion evidence: the same synthetic and live scenarios drive both clients;
presentation pause never affects agents; no client owns policy or durable state.

## Phase 10 — Optional workstation surfaces

Add desktop applications, local/cloud voice, personal desktop VM, hardened
worker VM, installer, and other host conveniences only when selected. Keep
security and usability roles distinct.

Completion evidence: separate role, theme, device, secret, network, share,
activation, and rollback tests.

## Phase 11 — Distribution

Produce signed, versioned artifacts for the portable core and host-specific
implementations. Add bounded installers only after exact artifacts and platform
conformance exist.

Completion evidence: clean installation, signature verification, rollback,
uninstallation, fresh-session behavior, and equivalent supported-host
boundaries.

## Cost controls

Prefer focused checks and source work before expensive builds. Run fast
verification once per coherent source snapshot and full verification once before
handoff. Request exact external builds through typed requests instead of
copy-paste. Keep large logs outside model context. Defer optional capabilities
rather than weakening their boundaries.

Do not claim savings from fewer tool calls alone. Compare verified task outcome,
failed attempts, elapsed time, model-visible bytes, resource use, setup cost,
external service cost, and repair rounds.
