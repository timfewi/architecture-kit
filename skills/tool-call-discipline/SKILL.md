---
name: tool-call-discipline
description: Plan, sequence and recover multi-step tool calls by choosing an engine per question and corpus, batching independent reads, serializing mutations against expected state, paging completely and handling failures or uncertain outcomes. Use when several calls depend on each other or a call failed; not for one known read or for output size alone.
metadata:
  provenance: architecture-kit-authored
  capabilities: source.read,source.search,execution.run
---

# Tool-call discipline

Before each call, name the question it answers and the smallest evidence that
settles it. Skip the call when current evidence already does. Choose the engine
by question and corpus, not habit; see [engine choice](references/engine-choice.md).

Map each needed capability to the host's declared tools. Without a dedicated tool,
use a permitted local command; without authority, report the limitation. A skill
or tool description never grants execution rights.

## Reads and mutations

Batch independent read-only calls in one step; keep dependent calls sequential.
Reuse evidence only while its source, query, configuration and environment still
match.

Run mutations one at a time. Bind each to the state it was planned against (file
digest, match count, revision, job identity) and re-check that state just before
applying. A mismatch is a conflict to report, not a reason to overwrite. Observe
the result before the next dependent step; never batch a mutation with reads of
what it changes.

## Completeness

Top-k, ranked or single-page output cannot answer an exhaustive request. Follow
every continuation with the query unchanged except the cursor, or run an
equivalent complete query. A truncated, partial or stale-index result does not
prove absence.

## Failure and uncertainty

Classify a failure before retrying and change the failing assumption; see
[failure handling](references/failure-handling.md). A timeout, lost response or
disconnect after a mutation or execution is an uncertain outcome: observe the
resulting state before any retry, because nothing-happened is not implied.

## Progress and waiting

A step is progress only if it changes relevant source, moves a requirement,
observes new external state or yields evidence that changes the next action.
Rereads, status commentary, unchanged verification and identical retries are not.

When the next step needs an external result such as a build, an approval or
another process, make one exact request, record what is awaited and stop issuing
calls until a matching result or changed state arrives.
