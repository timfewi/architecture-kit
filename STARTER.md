# Portable agent starter

Use this path when host setup and Home Manager already live in separate
repositories. This kit defines their required service boundary, not their
configuration. It adds no host modules, user packages, service units or secrets.

The deliverable is a specification, resolved configuration example, and executable
synthetic contract replay. It is **not a runnable production agent**. The example
adapter, model, handlers, service IDs, grants and receipts are synthetic. Their
digests express fixture identity, not executable availability or approval.

## Start here

1. Select [agent-starter](profiles/agent-starter.yaml).
2. Review [agent-config.json](examples/agent-config.json), especially the explicit
   tools, external service bindings and finite budgets.
3. Use the [runtime payloads](schemas/runtime-contracts.schema.json) and existing
   [tool contracts](schemas/tool-contracts.schema.json) as implementation boundaries.
4. Run `just check-fast` for independent semantic checks, and `just check` in
   the provisioned validator environment for full schema acceptance.
5. Implement one registered adapter and the platform owners. Supply real
   integration/isolation evidence before treating the configuration as usable.

The core requires one agent, one adapter/model binding, immutable launch policy,
canonical tools, an approval broker, isolated workers, lifecycle, a goal
controller, context/resume ownership, a declared toolchain and verification.
A first-party model loop is optional: an external harness can supply the loop.
The controller and recovery contracts are required either way.

Retrieval, skills, memory, coordination, research/browser, observation, terminal,
web, reviewed builds and compute are explicit extensions. Profile `optional`
means compatible, not activated. `enabled_extensions` activates only named
components plus their dependencies. Basic observation and terminal use do not
activate multi-agent coordination. No `host.*` dependency is permitted.

## Requirement-to-evidence map

| Starter requirement | Definition and local check | Still required from an implementation |
| --- | --- | --- |
| Minimal core | Profile closure and explicit extension activation | One usable registered adapter and worker |
| Launch configuration | Closed config, instruction digests, catalog/tool parity | Trusted loader, registry and secret resolver |
| Task/run lifecycle | Task, Run, RunEvent, StepReceipt, ResumePacket; transition replay | Durable controller and evidence issuer |
| Adapter boundary | Messages, requests, stream/control schemas; correlation negatives | Real wire codecs, credential isolation, cancel/resume |
| Grants and dispatch | Exact grant, decision, handler binding, input artifact; denial/replay checks | Authenticated broker, revocation races, confinement |
| Context and cost | Numeric allocations, reservations, unknown usage retained | Real token counting, pricing and accounting integration |
| Persistence | Atomicity/recovery policy, duplicate/checkpoint/reconcile fixtures | Transaction/crash, migration, retention and redaction tests |
| Reference workflow | Nine synthetic scenarios and negative mutations | Same scenarios against actual platform owners |

The existing two-real-adapter plus synthetic-third gate remains the stronger
portability milestone. One adapter can establish starter integration, not
harness/provider neutrality. Build, activation, live and release evidence never
follow automatically from contract tests.

## Configuration and precedence

`agent-config.schema.json` validates a **fully resolved launch intent**. Every
field is required; empty extensions/skills and a null secret reference are
explicit. No schema default injects settings, and no loader is implemented here.

Resolution order for an implementation:

1. Load a digest-pinned kit/profile baseline.
2. Apply reviewed repository/task configuration only to fields the launcher
   permits. Reject unknown fields, conflicting bindings and unselected extensions.
3. Resolve model, adapter, handler, skill and external service IDs through trusted
   registries. Verify every digest; do not interpret IDs as commands or URLs.
4. Apply explicit operator task overrides. They may narrow tools, grants,
   deadlines and budgets; widening requires a newly authorized launch.
5. Intersect all requests with immutable launcher policy. Policy wins over every
   earlier layer. Freeze the resolved config digest in the Run identity.

Repository text, model output, ambient environment and retrieved instructions
cannot change authority. No arbitrary environment interpolation or shell
evaluation is part of this contract. Instruction files are bounded, relative,
digest-pinned data; skills are loaded only when selected. Registry/secret
resolution happens outside model context. A secret reference is an opaque
credential-broker handle, never the credential or a host filesystem path.

The example uses one read tool. The 13-tool initial discovery surface in the
general catalog does not activate or authorize those tools in this configuration.
The example's synthetic model is not a recommendation of a provider or version.
Before a real binding is selected, verify its exact revision, supported context,
usage mapping, current pricing and documentation; commit the reviewed binding
and pricing digests. Automatic provider fallback is disabled.

## External service boundary

`platform_services` names six independently supplied capabilities:

- supervision: deadlines, process-tree cleanup and resource ceilings;
- credential mediation: provider credentials never enter repository workers;
- policy store: immutable task-scoped authority and revision identity;
- workspace isolation: broker-selected identities, mounts, toolchains and access;
- private IPC: authenticated, owner-restricted transport and bounded messages;
- durable store: transactional state, event log, receipts and outbox.

These are requirements on existing infrastructure. IDs in the example are
placeholders, not installed services. Host and Home Manager configuration remain
entirely outside this starter path.

## Runtime and authority ownership

Task owns objective, workspace and selected requirements. Run binds task, agent,
task content, source, policy, toolchain, registry, schema set and config. RunEvent has a
run-scoped monotonic sequence, broker timestamp, discriminated kind and typed
payload. The state vocabulary and permitted transitions come from
`inventories/controller-policy.json`, not adapter finish reasons.

The interface inventory links concrete payload schemas and checks required-field
parity. A null `payload_schema` explicitly marks older metadata-only contracts,
particularly optional peer/client projections; it is not instance validation.
Launch intent is separate from a scheduler-issued agent profile. Several older
receipt/request field lists now bind concrete payloads; consumers must review
that contract change instead of treating it as a silent storage migration.

A Grant binds one run/workspace, exact tool and input digest, all current
identities, handler binding, expiry and one use. Its current state is active or
revoked; expiry is evaluated at dispatch. A terminal Approval binds the complete
grant digest and decision. Absence of a decision means waiting. A decision cannot
extend grant expiry or grant a different operation.

Before dispatch the broker must authenticate the issuer, re-read current
revocation/policy state and validate both tool input and its content digest.
Visibility, a JSON document, a model recommendation or an approval ID is never
authority. Grant consumption and dispatch intent commit atomically. Changing
input, workspace, policy, schema, source, handler or expiry requires a new grant
and approval. An identical event delivery is deduplicated; a new call cannot
reuse the consumed grant.

HandlerBinding joins the canonical definition to a registered executable digest,
input/output schemas, executor, authority, effects, cancellation and idempotency.
Adapters cannot supply handler paths or executable code. Dispatch references
bounded input artifacts whose bytes must validate against the binding's schema.
Receipts bind call, identities, input and output digests and requirement evidence.
Only the trusted controller verifies requirements and enters COMPLETE.

## Adapter conformance

A model request carries normalized role/content messages, selected tool names,
current identities, deadline, reservation and bounded input/output allocations.
Tool-call and tool-result blocks correlate by call ID and reference artifacts;
arguments are not an untyped executable payload. Implementations validate role
ownership and complete tool history before constructing the request. Only
launcher-supplied policy may become a system message.

Normalize text streaming into ordered bounded text deltas. Buffer raw provider
tool-argument fragments within the selected input byte limit; emit one complete,
validated tool-call record per unique call ID, never dispatch partial arguments.
A stream ends once with finish or typed error. Reject foreign request IDs,
sequence gaps, duplicate calls, unselected tools, data after finish and finish
reasons inconsistent with the emitted calls. A finish is not goal completion.

Capabilities declare text, tool calls, streaming, cancellation and resume.
Unsupported operations return an explicit non-retryable unsupported error.
Resume must use either digest-bound normalized replay or a registered
provider-session codec; it never imports provider state as authority.
Cancellation is cooperative or best-effort and must retain uncertain effects
and unavailable usage. Authentication and invalid-response errors are not
unchanged automatic retries. Transient retry also needs policy, remaining
reservation, deadline and changed/backoff conditions; no implicit fallback.

The fixture covers a normalized adapter and contract error cases, not real
provider codecs, tokenizer behavior, secret transport or process cancellation.

## Context, tokens and cost

The example's **tunable starting values**, not measured optimal settings:

| Limit | Example |
| --- | ---: |
| Context window | 8,192 tokens |
| Input / reserved output / safety | 6,144 / 1,024 / 1,024 tokens |
| Model-visible tool output / resume packet | 16,384 / 8,192 bytes |
| Whole run | 12,000 tokens; 100,000 synthetic microcredits |
| Model calls / tool calls / elapsed time | 8 / 20 / 900 seconds |

Pack current policy, goal, requirement matrix and digest-bound resume first.
Then load only selected tool definitions and the bounded evidence needed for the
next action. Keep full history and large artifacts out of automatic context.
Count through the selected adapter or a verified conservative bound; bytes and
characters are not tokenizer counts. Reserve output and safety before packing.
If necessary compact once per phase, revalidate identities, then block if the
required context still cannot fit. Never truncate authority or requirements.

Before each model call, atomically reserve worst-case input plus output tokens
and a verified cost bound. Spent plus all held reservations must fit the run
limits. Check count/deadline limits before dispatch. Cancelled or rejected calls
release reservations only with authoritative evidence that no charge remains.

Normalized usage partitions tokens into disjoint uncached input, cached input,
visible output and reasoning output. Their sum is the total. If a provider
reports subsets, the adapter must normalize them without double counting.
Unavailable or ambiguous counters remain `known: false`: retain the reservation
and reconcile later. Never turn unknown usage into zero. Known settlement
releases the held amount and charges the actual total exactly once. Real
overruns must be durably recorded and block new work; the contract checker flags
them as a reservation violation rather than inventing lower usage.

Microcredits are integer accounting units. The fixture uses invented synthetic
credits, not money or provider prices. A production binding must define unit,
rounding, pricing digest and a sound upper bound. These numbers establish no
token savings; existing retrieval benchmarks remain byte-level evidence only.

## Storage, crashes and migrations

Use a per-run transactional log with unique `(run_id, sequence)`, compare-and-swap
state advancement and immutable event bytes. In one commit persist event, state
projection, reservation/approval consumption and outbox intent. Publish effects
only after commit. For results, materialize and verify bounded artifacts first,
then commit result receipt, requirement/accounting updates and outbox settlement.
Orphan artifacts can be collected later; a committed receipt must not point to
an incompletely written result.

Delivery is at least once, not exactly once. A duplicate with identical bytes is
ignored; the same sequence with different bytes fails closed. Call IDs and
reservation IDs cannot be reused. A checkpoint is an optimization, not the
durable owner: replay later events to restore pending calls, consumed grants,
spent/held budgets and requirement state.

| Crash window | Required recovery |
| --- | --- |
| Before intent commit | No effect may have been dispatched. |
| After commit, before a durable result | Treat dispatch as uncertain until reconciled by exact call identity. |
| Result committed, acknowledgment lost | Replay the stored receipt; do not execute again. |
| Checkpoint stale or identity changed | Revalidate against the event log/current identities; never silently replay under new authority. |

While an effect is unresolved, block new dispatch of that call and do not claim
COMPLETE, FAILED or CANCELLED as if its outcome were known. Reconcile via the
worker/provider owner's durable status. Without safe status/idempotency support,
remain OUTCOME_UNCERTAIN or WAITING_EXTERNAL. No model turns run in external or
approval wait. A cancelled run may retain unknown model charges for later
accounting settlement; that is not successful completion.

Redact secrets before persistence, model exposure and observation. Separate
conversation content, durable control records, evidence and rebuildable caches.
The sample retains events 30 days, receipts 90 days and artifacts 7 days.
Unresolved work and artifacts required by active evidence override those TTLs.
Garbage collection must honor references, write an audit tombstone and never
make unavailable evidence look verified. Production retention/privacy policy
must be reviewed before use; no retention worker is implemented here.

Reject unsupported schema digests. Migrate by an explicit conversion bound to
old/new schema sets: copy into a new namespace, validate shapes and invariants,
preserve identities/idempotency keys or map them auditably, test recovery, then
atomically switch the active pointer. Retain rollback evidence; never rewrite
the only log in place or reinterpret old grants under new policy.

## Reference cases and commands

`examples/reference-run.json` contains success, approval denial, model timeout,
cancellation before dispatch, later usage reconciliation, budget exhaustion,
restart/resume with duplicate delivery, tool timeout, and cancellation after
dispatch with reconciliation. Every case starts from its own fresh synthetic
store, even though readable fixture IDs are reused.

The replay runs in memory over supplied records; it does not create processes,
call models, operate a database, grant real access or enforce a sandbox.
Negative tests mutate scope, digests, budgets, states, evidence, cursors and
stream correlation. Real adapters/storage/brokers must reuse the scenario
oracles in their own integration tests.

```sh
just test-runtime-semantics
just check-fast
just check
```

After reviewed changes to declarations or example inputs, regenerate fixtures,
then inspect the diff and refresh the package manifest:

```sh
just refresh-reference
just refresh-manifest
```

Fixture generation is not a verification receipt. Full schema validation requires
the existing pinned validator environment; a semantic pass does not substitute
for it. See [VERIFICATION.md](VERIFICATION.md) for evidence limits.
