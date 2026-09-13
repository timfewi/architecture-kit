# Lessons from building the architecture

These are design lessons to test against your workload. Their historical
provenance was not supplied with the kit; they are not independent proof that
this reference architecture is deployed. The research register identifies
primary evidence for the mechanisms used here.

## Progress must be host-observable

A long-running model turn is not evidence of progress. Repeated reads, broad
searches, status commentary, unchanged verification, and deterministic retries
can consume substantial context while leaving every acceptance criterion
unchanged.

The adopted rule is to let the controller measure progress as a source or
evidence delta. A step advances only when it changes relevant source, moves a
requirement, observes new external state, or obtains primary evidence that
changes the next action.

## Waiting is a real state

A common deadlock is to require a build before completion while withholding the
build request until completion. Continued model turns cannot resolve that
cycle.

The adopted rule is to emit one exact, typed external request after static and
focused checks, then enter WAITING_EXTERNAL. The controller resumes only when a
matching result or changed external state arrives.

## Deterministic failures require fingerprints

Retrying the same denied execution, malformed request, or transport failure with
unchanged inputs rarely adds evidence.

The adopted rule fingerprints action kind, normalized error, input digest, and
capability revision. A repeated fingerprint is refused unless the input,
assumption, capability, tool, authority, or external state changed.

## Context is a bounded resource

Repeated attachment reads, full staged diffs, broad searches, duplicate manifest
loads, and reloading after compaction can dominate cost. Large successful output
often adds less decision value than a digest and one relevant excerpt.

The adopted rule budgets retrieval calls and model-visible bytes per phase,
deduplicates reads by path and digest, keeps large artifacts outside context,
and creates short digest-bound resume packages. Automatic context is limited to
policy, active goal, requirement matrix, and the resume packet. Large handoffs
are decomposed into bounded issue records, loaded progressively, and removed
from active context after their settled decisions and evidence are retained.

## Use the smallest relevant guidance surface

Loading many skills or broad documentation sets can repeat generic rules and
hide task-specific evidence.

The adopted rule selects the smallest relevant skill set and progressively
loads only references needed for the current decision.

## A package definition is not a package

Writing declarative packaging before the first real build leaves assumptions
about source layout, dependency closure, installation behavior, and executable
identity unconfirmed.

The adopted rule distinguishes source design from build evidence and requires a
typed build request/result boundary when the agent cannot run the build itself.
The request binds source, exact registered recipe, expected inputs, network policy,
and timeout. The host returns only a correlated result with store identity,
status, diagnostics, and evidence. The controller waits without model turns
while the reviewed build runs.

## Toolchain freshness is snapshot-scoped

A toolchain can become stale while a session continues. Invalidating every
check wastes time, while ignoring the change creates false evidence.

The adopted rule binds toolchains and receipts to source digests and reruns only
checks affected by the changed inputs.

## Narrow tests do not decide completion

Focused tests are efficient and necessary, but they prove only their contract.
Treating them as release evidence hides packaging, isolation, activation, and
live failures.

The adopted rule gives the host controller ownership of the verification matrix
and allows only the matching evidence level to close each requirement.

## Lifecycle cleanup is part of the result

Process groups, nested sessions, descendant adoption, disconnects, and partial
external effects made cleanup one of the hardest boundaries. Waiting only for a
direct child can leave work alive after a tool result.

The adopted rule gives one supervisor exclusive child ownership, explicit
termination and reaping, bounded settlement, uncertain outcomes, and capacity
retention until reconciliation.

## Capability is not authority

A tool schema, Agent Card, peer message, network route, or visible profile can
look like permission. Treating descriptive metadata as authority creates
cross-agent and cross-workspace escalation.

The adopted rule keeps effective grants host-issued, revision-bound, expiring,
and independently checked at every dispatch.

## Neutrality must be proven by independent consumers

Moving provider or harness branches into a shared module does not create a
neutral core. Hidden imports, native session assumptions, and result codecs can
preserve the coupling.

The adopted rule requires multiple independent adapters plus a synthetic third
consumer, with neutral imports and byte-identical canonical tool definitions.

## Observation must not control work

A live dashboard is tempting to place on the dispatch path. Slow clients,
rendering, or full queues would then change scheduling and outcomes.

The adopted rule uses immediate bounded offers and reconstructible projections.
Drops require visible resynchronization but never alter authoritative task
state.

## External content remains data

Research, rendered pages, provider responses, and indexes can contain convincing
instructions. Sanitizing content does not make it an authority source.

The adopted rule treats all external and derived content as untrusted evidence,
with explicit provenance, bounded retrieval, and no power to select credentials,
commands, URLs, permissions, or follow-up actions.

## One writer avoids false coordination

A shared heavily modified checkout makes concurrent writers difficult to
reconcile and can invalidate receipts silently.

The adopted rule uses one writer per isolated worktree or source snapshot.
Other agents investigate or review read-only unless they have separately
authorized isolated workspaces.

## Maintenance should not compete with active work

Index refresh, package preparation, memory review, and other maintenance can
consume the same resources as a user task.

The adopted rule runs maintenance only when explicitly scheduled or idle,
records its resource ownership, and never lets maintenance silently change an
active task's policy or evidence.
