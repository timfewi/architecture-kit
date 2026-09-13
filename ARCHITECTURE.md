# Architecture decisions

## Normative state

This document specifies a reference architecture. Decisions are recommendations
for the selected profile; acceptance clauses describe evidence an implementation
must produce. This kit alone is not proof of deployment, portability or speed.

The system has a portable agent core and optional reference host profiles. The platform
supports registered external harnesses and an optional first-party loop through
the same neutral contracts. The host owns policy, credentials, authority,
resource lifetimes, progress evaluation, and completion. Harnesses own only
their native model and session mechanics.

Each decision records context, decision, rationale, consequences, and
acceptance. Adjustable versions, limits, package choices, and tool membership
live in the inventories and profiles unless they establish a durable boundary.

## Decision index

| ID | Decision |
| --- | --- |
| ADR-001 | Optimize for correctness, authority, evidence, containment, and recovery |
| ADR-002 | Keep the reference laptop declarative and reproducible |
| ADR-003 | Separate portable policy from host identity and hardware |
| ADR-004 | Separate control plane from data plane |
| ADR-005 | Make the launcher the immutable authority composer |
| ADR-006 | Keep capability, authority, profile, and approval orthogonal |
| ADR-007 | Keep the core harness- and provider-neutral |
| ADR-008 | Route models through a host-owned model gateway |
| ADR-009 | Use one canonical typed tool-definition source |
| ADR-010 | Keep the default tool surface small and progressive |
| ADR-011 | Use stateless, bounded tool protocols with absolute deadlines |
| ADR-012 | Execute repository code only in fresh isolated workers |
| ADR-013 | Treat supervision, cancellation, and reaping as correctness |
| ADR-014 | Separate task, conversation, memory, evidence, and derived state |
| ADR-015 | Use precise, source-bound multilingual retrieval |
| ADR-016 | Use reviewed memory and receipt-bound evidence |
| ADR-017 | Enforce host-issued agent profiles and finite capacity |
| ADR-018 | Use capability-scoped peer discovery and a coordination ledger |
| ADR-019 | Keep observation asynchronous and reconstructible |
| ADR-020 | Provide one Focus, Swarm, and Observe product surface |
| ADR-021 | Keep external research and browser content untrusted |
| ADR-022 | Add the first-party loop as an ordinary optional harness |
| ADR-023 | Put autonomous progress in a host-owned state machine |
| ADR-024 | Bind retries, waiting, budgets, and completion to receipts |
| ADR-025 | Keep desktop, voice, personal VM, and hardened worker roles distinct |
| ADR-026 | Separate source, build, activation, live, and release evidence |
| ADR-027 | Package portable core separately from host implementations |
| ADR-028 | Load only digest-bound minimum context and resume packets |
| ADR-029 | Use a typed reviewed build capability |

## ADR-001 — Optimize for correctness, authority, evidence, containment, and recovery

Context: Agent systems can appear productive while weakening permission,
provenance, cleanup, or completion semantics.

Decision: Evaluate every subsystem against five equal qualities: functional
correctness, authority correctness, evidence correctness, containment, and
recoverability. Latency or token reduction is valid only after the same
correctness and security gates pass.

Rationale: Fast but unauthoritative or unrecoverable behavior creates hidden
work and unsafe retries.

Consequences: Measurements include failed and cancelled work. Unknown evidence
stays unknown. Convenience features do not bypass ownership boundaries.

Acceptance: Every public operation identifies its authority owner, failure
semantics, evidence class, resource bounds, and recovery behavior.

## ADR-002 — Keep the reference laptop declarative and reproducible

Context: A greenfield laptop must be rebuildable without ambient machine state.

Decision: For the optional Linux reference host, use declarative NixOS with
immutable external inputs, explicit
hardware composition, pinned toolchains, rollback, and separately selected
development profiles. Installation and activation are explicit operations.

Rationale: A reproducible source definition is easier to audit, recover, and
transfer than accumulated mutable setup.

Consequences: Missing offline inputs block only dependent evidence. Ordinary
workers never install packages or mutate lock data. Direct dependencies and pin
sources are recorded in the software inventory.

Acceptance: A clean evaluator can reproduce the declared outputs without
credentials, personal state, or undocumented package installation.

## ADR-003 — Separate portable policy from host identity and hardware

Context: Hardware declarations and public recipients may be source-controlled,
while private identity and runtime state may not.

Decision: Keep reusable policy, host composition, and physical identity in
separate declarative owners. Track only public recipients and reviewed
ciphertext. Materialize private credentials into owner-scoped runtime paths
outside source and build outputs.

Rationale: Portability and secrecy require different lifecycles.

Consequences: The portable package uses role names and opaque identifiers.
Secrets are handles consumed by trusted brokers, never prompt text, argv,
general environment, tool output, or repository fixtures.

Acceptance: Source, build closure, agent container, logs, and package scans
contain no private keys, authentication stores, runtime databases, personal
corpora, or machine identity.

## ADR-004 — Separate control plane from data plane

Context: Model output, web content, and repository code are untrusted inputs.

Decision: The control plane selects repository, harness, model route, tool
profile, network mode, credentials, workspace grants, approvals, resource
limits, toolchain, and state roots. The data plane performs model calls, tools,
research, indexing, memory, computation, and user-facing requests under that
fixed selection.

Rationale: Data-plane work must not rewrite the authority under which it runs.

Consequences: Policy changes require a new session. Every operation binds to
the relevant session, repository, policy, schema, and deadline identities.

Acceptance: No model, harness, tool result, repository command, or external
document can add a capability or mutate current policy.

## ADR-005 — Make the launcher the immutable authority composer

Context: Scattered flags and implicit defaults can create authority escalation.

Decision: One launcher normalizes user selections, canonical paths, registry
metadata, toolchain evidence, state roots, and resource ceilings into an
immutable policy digest. It rejects ambiguity, overlap, stale mandatory inputs,
and unsupported combinations before starting a harness.

Rationale: One deterministic composition point makes authority reviewable.

Consequences: Existing sessions do not gain newly configured tools or
credentials. Broad presets remain shorthand whose explicit settings may narrow
them.

Acceptance: Equivalent inputs produce the same policy; changed authority,
workspace, harness, toolchain, or model routing changes its digest.

## ADR-006 — Keep capability, authority, profile, and approval orthogonal

Context: A visible tool does not by itself authorize a mutation.

Decision: Separate read/write, local/remote Git, GitHub, network, research,
browser, credentials, corpus, model, image, workspace, and tool-profile
authority. Approval is an additional exact, expiring, single-use decision.

Rationale: Bundled permissions hide unintended escalation.

Consequences: Coding does not imply Git write; network does not imply GitHub;
tool visibility does not imply task authorization; an advertised Agent Card
does not convey a grant.

Acceptance: Cross-product policy tests prove denial for every missing authority
and replay, expiry, identity mismatch, and stale-grant cases.

## ADR-007 — Keep the core harness- and provider-neutral

Context: External harnesses and providers use different configuration, wire,
session, reasoning, and output formats.

Decision: Register harnesses from one immutable registry. The neutral core owns
agent, task, run, workspace, lifecycle, capability, communication, and evidence
semantics. Each adapter owns only its executable, native configuration, model
wire codec, session codec, output mapping, and child transport. Harness names
are registry data, never core branches.

Rationale: At least two independent adapters and a synthetic third adapter are
the proof that the boundary is real.

Consequences: Neutral modules do not import harness implementations. Provider
usage fields are normalized honestly; unavailable measurements remain null and
overlapping counters are not double-counted.

Acceptance: All registered harnesses consume the same policy-selected tool
definitions and pass the same lifecycle, authority, cancellation, capacity, and
observation fixtures.

## ADR-008 — Route models through a host-owned model gateway

Context: Harnesses need model access without receiving provider credentials or
provider authority.

Decision: Use a provider-neutral, bounded gateway over authenticated local IPC.
The host selects an immutable provider binding, injects its credential, validates
exact endpoint, model, headers, body, response, redirect, byte, time, and
concurrency constraints, and owns cleanup.

Rationale: Provider SDKs and wire formats are mechanics, not agent authority.

Consequences: No provider key enters a harness container. Automatic provider
fallback is disabled. Each launch receives fresh accounting identity while an
explicit retained session may keep only its approved logical routing identity.

Acceptance: Multiple provider fixtures and live support checks prove exact
routing, credential isolation, cancellation, usage attribution, and denial of
foreign hosts, models, headers, and parameters.

## ADR-009 — Use one canonical typed tool-definition source

Context: Separate policy tables, schemas, docs, and adapters drift.

Decision: One immutable definition record owns tool name, description, policy,
input and output contracts, bounds, result semantics, provenance, side effects,
redaction, platform support, and handler identity. It deterministically produces
policy, catalog, schemas, fixtures, inventories, and adapter views.

Rationale: Generated parity makes drift observable.

Consequences: Duplicate names, open schemas, unbounded values, unknown fields,
and unmatched handlers fail closed. Documentation is never an authority source.

Acceptance: Every source-catalog tool appears exactly once and every generated
view binds to the same definition digest.

## ADR-010 — Keep the default tool surface small and progressive

Context: Large catalogs increase selection cost and obscure the normal coding
path.

Decision: Start with the small surface declared in the tool inventory and load
one additional operation through capability search when policy and task need
it. Tune the surface against routing accuracy and full task cost. Prefer semantic operations over provider-named or generic action tools.

Rationale: Progressive exposure lowers context and routing cost without hiding
available capability.

Consequences: Typed read and write operations remain separate. Broad remote or
provider multiplexer tools are replaced by exact operations. Internal services
need not be model-visible.

Acceptance: Catalog tests prove the default count, profile membership,
deterministic ordering, unavailable-family absence, and exact authority mapping.

## ADR-011 — Use stateless, bounded tool protocols with absolute deadlines

Context: Layer-local timeouts and permissive JSON create ambiguous outcomes.

Decision: Every request carries protocol, client capability, call lineage,
policy/schema bindings, and one absolute monotonic deadline. Inputs and outputs
use closed finite schemas, stable result types, byte and record bounds, explicit
truncation and continuation, and structured errors.

Rationale: One deadline and finite envelope preserve causality and cleanup.

Consequences: Inner work consumes remaining time rather than restarting clocks.
A continuation reauthorizes against current scope and cannot splice changed
input.

Acceptance: Unknown fields, duplicate keys, invalid enums, non-finite numbers,
oversized content, expired deadlines, and changed continuation identity fail
before dispatch or return a typed uncertain outcome.

## ADR-012 — Execute repository code only in fresh isolated workers

Context: Repository code may be hostile, accidental, or supply-chain controlled.

Decision: Repository execution uses argv-only calls in a fresh no-network
worker with the exact writable workspace, read-only Git metadata and immutable
toolchain, private executable scratch, private PID/proc views, minimal devices,
no credentials or broker socket, and explicit resource limits.

Rationale: A harness container alone is not an execution boundary.

Consequences: Static reads remain distinct from repository-code execution.
Source evaluation uses a safe materialized snapshot that excludes ignored state,
unsafe links, Git metadata, and credentials.

Acceptance: Path traversal, absolute links, escaping symlinks, ambient PATH
fallback, network, credential access, foreign mounts, and descendant escape are
covered by negative tests and installed self-checks.

## ADR-013 — Treat supervision, cancellation, and reaping as correctness

Context: Process groups, nested sessions, adopted descendants, transport
disconnects, and partial external effects make termination difficult.

Decision: One lifecycle owner records child identity before dispatch, applies
parent-death behavior, terminates the complete owned scope, reaps adopted
children, and settles the operation before admitting replacement work. Cleanup
runs on success, error, timeout, cancellation, signal, disconnect, and resource
exhaustion.

Rationale: A returned response is not completion while owned work survives.

Consequences: Uncertain dispatch retains capacity until reconciled. Partial
audio, external mutation, or provider work is not silently replayed.

Acceptance: Failure injection covers nested process groups, new-session
boundaries, late output, start exhaustion, parent death, repeated cancellation,
and no PID or cgroup growth across calls.

## ADR-014 — Separate task, conversation, memory, evidence, and derived state

Context: Conflated state causes stale recovery, privacy leaks, and false
completion.

Decision: Keep source, build, session, runtime, durable task ledger, conversation
projection, evidence receipts, reviewed memory, indexes, caches, and opt-in
archives in separate owners and roots. Derived state is rebuildable; personal
archives are never preloaded.

Rationale: Each state class needs different retention, trust, and invalidation.

Consequences: Retained sessions preserve only bounded, approved state. Snapshot,
cursor, grant, source, schema, and toolchain identities control reuse.

Acceptance: Restart, expiry, revocation, corruption, stale source, and missing
state tests cannot revive terminal tasks, reuse foreign data, or convert absence
into success.

## ADR-015 — Use precise, source-bound multilingual retrieval

Context: Lexical search, structural search, symbol relations, and semantic
retrieval answer different questions.

Decision: Route by question semantics across literal text, syntax, ranked
documents, exact source, outline, bounded context, and stable symbol relations.
Every result binds to repository scope, source generation, freshness,
completeness, provenance, truncation, and continuation.

Rationale: Faster retrieval is useful only when it preserves the task oracle.

Consequences: Incremental overlays invalidate changed facts and must match clean
rebuild results. Language adapters are versioned and capability-specific.

Acceptance: Fixtures cover aliases, same-name symbols, comments, strings,
unavailable languages, dirty/renamed/deleted files, stale indexes, and
generation-bound cursors across supported languages.

## ADR-016 — Use reviewed memory and receipt-bound evidence

Context: Model-authored memory can amplify errors or invent verification.

Decision: Journals are bounded working notes. Durable memory requires typed
evidence anchors, freshness, independent review, and an applicable host-issued
verification receipt. Models may propose learning but cannot approve it or
create host receipts.

Rationale: Persistence raises the cost of an incorrect claim.

Consequences: Receipt existence alone does not prove execution; source and
result bindings must match. Raw prompts, tool output, transcripts, and personal
corpora are not memory records.

Acceptance: Tamper, replay, stale receipt, duplicate proposal, review race, and
scope mismatch tests fail closed.

## ADR-017 — Enforce host-issued agent profiles and finite capacity

Context: Harnesses and models cannot safely choose their own concurrency or
grants.

Decision: The host issues a digest-bound capability profile containing model
family, profile revision, operation set, workspace grants, network/data rules,
expiry, queue bound, and maximum parallel agents. Each deployment sets finite capacities from model, task and resource evidence;
no provider or model family owns a hard-coded slot count. Effective capacity is the minimum
of profile, user policy, workspace budget, global resource ceiling, and
scheduler safety limit.

Rationale: Capacity is both a resource and authority boundary.

Consequences: Mixed models use separate buckets under one finite global ceiling.
Retries and uncertain dispatches cannot manufacture slots. Queue order is
deterministic and typed wait reasons include governing bucket and occupancy.

Acceptance: Saturation, lower overrides, cancellation, retry, uncertain launch,
mixed profiles, fairness, restart, and lost-capacity recovery never exceed any
limit.

## ADR-018 — Use capability-scoped peer discovery and a coordination ledger

Context: Repository location or display identity does not authorize peer access.

Decision: A host-owned directory reveals a peer only where the requester's
current grant intersects the peer's active workspace or worktree membership.
A durable coordination ledger owns messages, tasks, claims, leases,
idempotency, acceptance, and bounded artifact references. A2A-compatible
semantics project this ledger; they do not replace it.

Rationale: Horizontal agent communication needs independent reauthorization.

Consequences: Messages and cards cannot grant MCP or filesystem authority. A
mutating delegated task requires current write authority for requester and
receiver, then executes in the receiver's fresh worker.

Acceptance: Multi-workspace, downgrade, expiry, revocation, crash, reconnect,
duplicate, atomic claimant, terminal immutability, and artifact-boundary tests
preserve isolation and convergence.

## ADR-019 — Keep observation asynchronous and reconstructible

Context: Synchronous telemetry on the agent hot path can stall real work.

Decision: Observation uses immediate bounded offers, content-minimized events,
owner-only local transport, deterministic reducers, published snapshots, epochs,
cursors, replay, and explicit resynchronization. Scheduling and task durability
do not traverse the observation queue.

Rationale: Observation must not become a second control plane.

Consequences: Drops and gaps are counted, visible, and repaired from authorized
snapshots. No second live database or general message broker is introduced.

Acceptance: Stopped collectors, full queues, slow clients, duplicates, reorder,
restart, and overflow leave scheduling and terminal outcomes unchanged and
converge after resync.

## ADR-020 — Provide one Focus, Swarm, and Observe product surface

Context: Separate dashboards create inconsistent controls and state.

Decision: One product surface exposes Focus for a selected run, Swarm for
capacity-aware agent coordination, and Observe for workspace maps, activity,
and diagnostics. Terminal and Web clients consume the same state, conversation,
and control contracts and provide functional, not visual, parity.

Rationale: Presentation must not own policy, providers, schedulers, or durable
state.

Consequences: Terminal is the default local client with accessible fallback.
Web uses authenticated loopback transport, strict content policy, shared theme
tokens, accessibility, and reduced motion. Selection and drafts survive view
changes.

Acceptance: Identical fixtures drive both clients through normal, denied,
waiting, uncertain, stale, gap, reconnect, and resync scenarios for every
registered harness.

## ADR-021 — Keep external research and browser content untrusted

Context: Search results, documents, provider output, rendered pages, and remote
metadata may be hostile.

Decision: Expose semantic research operations through credential-isolated
brokers with neutral client identity, public HTTPS constraints, DNS/TLS and
redirect validation, random job-scoped identifiers, byte/cost/deadline bounds,
and explicit provenance. Static retrieval, PDF extraction, and browser
interaction remain distinct capabilities.

Rationale: External content is evidence, never policy or authority.

Consequences: Provider choice may appear in safe provenance but provider
credentials and unrestricted knobs remain host-owned. Prompt injection cannot
authorize a URL, command, credential request, or follow-up action.

Acceptance: Redirect, rebinding, private address, oversized document, parser
failure, malicious instruction, stale snapshot, cancellation, cleanup, and
cross-job identity tests pass.

## ADR-022 — Add the first-party loop as an ordinary optional harness

Context: A native headless loop can reduce dependency and give tighter control,
but can also duplicate the platform.

Decision: Register the first-party loop through the same adapter and descriptor
boundary as external harnesses. It owns model/tool turn sequencing, streaming,
conversation context, compaction, correlation, retry classification, local
recovery, and explicit finish reasons. It consumes existing policy, model
gateway, tools, scheduler, grants, coordination, retrieval, evidence, and
observation owners.

Rationale: The loop proves the neutral platform as a new consumer rather than
becoming privileged core logic.

Consequences: External and first-party harnesses remain concurrently selectable.
The loop has no separate UI, policy engine, tool router, identity registry,
scheduler, ledger, or statistics database.

Acceptance: Mixed-harness sessions pass identical authority, lifecycle,
communication, observation, cancellation, approval, budget, and recovery
fixtures without first-party special cases.

## ADR-023 — Put autonomous progress in a host-owned state machine

Context: A model can continue consuming time and context while producing no
measurable progress or waiting on an external prerequisite.

Decision: The host controller owns the states QUEUED, PREFLIGHT, PLAN,
EXECUTE_STEP, OBSERVE, VERIFY, REPLAN, WAITING_APPROVAL, WAITING_EXTERNAL,
COMPLETE, BLOCKED, FAILED, CANCELLED, and OUTCOME_UNCERTAIN. Only new evidence,
a changed requirement, or an executable next action may cause another model
turn.

Rationale: Prompt instructions cannot reliably enforce lifecycle or spending.

Consequences: WAITING_EXTERNAL performs no model turns. BLOCKED means no
executable authorized next step exists. REPLAN requires evidence that changes
the approach. The controller, not the model, confirms completion against the
requirement matrix.

Acceptance: State-transition tests reject illegal loops, completion without
satisfied criteria, work during external wait, unchanged retry, and model-authored
state escalation.

## ADR-024 — Bind retries, waiting, budgets, and completion to receipts

Context: Repeated reads, broad output, deterministic transport failures, and
unchanged full checks inflate cost without progress.

Decision: Every step writes a durable bounded receipt containing goal and step
identity, source snapshot, toolchain revision, exact action, required capability,
input and output digests, result classification, diff summary, verification
delta, consumed budget, and next state. A failure fingerprint binds action kind,
normalized error, input digest, and capability revision. The same fingerprint
cannot be retried without a changed assumption, input, tool, authority, or
external state.

Rationale: Measurable deltas and retry denial turn autonomy into a controlled
process.

Consequences: The controller inventory supplies configurable starter budgets.
They are workload hypotheses, not universal tool-use quotas. Budgets may stop a
slice without redefining the user's objective. Evidence of changed inputs or an
uncovered requirement justifies another check. Large logs remain external.

Acceptance: Identical reads, searches, deterministic errors, unchanged
verification, status-only messages, and repeated context loading do not count as
progress. Wall-time, token, cost, tool-call, and context-compaction budgets stop
or transition the slice predictably.

## ADR-025 — Keep desktop, voice, personal VM, and hardened worker roles distinct

Context: User convenience surfaces have different threat models from agent
workers.

Decision: Desktop, terminal, editor, browser, reader, TTS, dictation, personal
desktop VM, and hardened worker VM are separately selectable components.
Desktop and voice are consumers of bounded capabilities, never authority owners.
The personal VM is usability-oriented; the hardened worker uses reviewed,
digest-bound inputs and default-deny isolation.

Rationale: One ambiguous private or secure mode would hide incompatible goals.

Consequences: All user-facing programs use shared dark/light theme tokens where
supported. Local/cloud voice switching affects new requests without changing
agent policy. VM roles expose no implicit shares or ports.

Acceptance: Profile, theme, secret, device, network, share, activation, and role
tests prove that selecting one surface cannot enable another.

## ADR-026 — Separate source, build, activation, live, and release evidence

Context: Static declarations and synthetic fixtures do not prove deployed
behavior.

Decision: Record source, focused-test, build, activation, live, and release
evidence separately. A requirement-to-evidence matrix is host-owned and names
the exact source, policy, toolchain, registry, command/profile, output digest,
status, blocker, and remaining observation.

Rationale: Completion claims must match the evidence actually produced.

Consequences: Missing dependencies are environment blockers, not passing checks
or code failures. Narrow tests cannot close broader support gates. Release
evidence includes rollback and fresh-session behavior.

Acceptance: Reports cannot promote an evidence level, omit failed attempts, or
reuse evidence from changed source, policy, toolchain, registry, or schema.

## ADR-027 — Package portable core separately from host implementations

Context: Linux/NixOS is the reference, while future hosts have different
process, credential, sandbox, and service primitives.

Decision: Distribute the portable core, profiles, clients, and contracts
separately from host implementations. Linux/NixOS is the reference design; live conformance remains an implementation gate.
Other hosts must implement equivalent filesystem, credential, process,
cancellation, networking, IPC, and evidence boundaries before support.

Rationale: Portability is equivalent semantics, not shared filenames.

Consequences: Versioned signed artifacts precede installers. Installers select
an exact version, verify identity, write only bounded targets, and never
silently configure privileged services.

Acceptance: Platform conformance suites prove boundary equivalence, installation
rollback, uninstallation, and absence of privilege or credential leakage.

## ADR-028 — Load only digest-bound minimum context and resume packets

Context: Large permanent handoff documents and repeated context reconstruction
consume model budget, retain stale facts, and encourage rereading after
compaction.

Decision: Automatic context contains only current policy, the active goal, the
selected requirement matrix, and one short digest-bound resume packet. The
packet records the last settled step, relevant source and toolchain identities,
open requirements, current controller state, external requests, and the first
executable next action. Detailed work is decomposed into bounded task records and loaded progressively.
A local ledger or an optional issue-tracker adapter can store those records.
Settled detail leaves active context after durable evidence and rationale are
preserved; no hosting service is required.

Rationale: Context should carry the state needed for the next decision, not the
entire implementation history.

Consequences: Compaction creates a new minimal projection instead of replaying
large transcripts or handoffs. A changed source, policy, requirement matrix, or
toolchain invalidates only affected packet claims. Issue trackers coordinate
bounded work; they never become runtime authority or a second state owner.

Acceptance: Fresh launch, resume, compaction, changed-source, stale-packet, and
missing-issue tests load no unrelated history, preserve the exact next action,
and reject digest mismatch. Model-visible context size remains within the
declared phase budget.

## ADR-029 — Use a typed reviewed build capability

Context: When an ordinary worker cannot build a requested artifact, manual hash
and command copy-paste creates a circular dependency and an unaudited operator
boundary.

Decision: The agent submits a typed build request containing source digest,
registered recipe, expected input identities, network policy, and timeout. The
host validates the request against current policy and runs only that reviewed
build in its dedicated builder. The matching build result returns request
identity, job identity, terminal state and an immutable result artifact. The artifact
contains output identity, diagnostics and the build evidence receipt.

Rationale: A typed host capability lets the controller obtain build evidence
without granting a general build daemon, shell, network, or host mutation path.

Consequences: The controller enters WAITING_EXTERNAL while the build runs and
does not spend model turns. A result for another source, output, input set,
policy, or request cannot settle the step. User approval is required only when
the request expands policy or authorizes an independently sensitive operation.

Acceptance: Request validation, exact-output allowlisting, source/input mismatch,
network denial, timeout, cancellation, duplicate submission, result
correlation, artifact identity validation, and uncertain settlement tests pass. The
builder exposes no arbitrary command execution and never activates or deploys
the result.

## Contract and evidence ownership

TOOLING.md specifies result, retry, path, discovery and Linux adapter semantics.
The tool inventory and referenced schemas are the canonical payload definitions;
interface field lists are architectural summaries unless explicitly bound to a
payload schema. Research findings distinguish upstream facts, local checks and
unmeasured hypotheses. Kit integrity does not close any deployment gate.
