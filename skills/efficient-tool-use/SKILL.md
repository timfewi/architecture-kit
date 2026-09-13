---
name: efficient-tool-use
description: Choose bounded retrieval and execution strategies for a task with many tools, large outputs or repeated investigation. Use when tool selection or context cost matters; not to impose overhead on trivial work.
metadata:
  provenance: architecture-kit-authored
  capabilities: source.read,source.search,execution.run
---

# Efficient tool use

Identify the next decision and its smallest useful evidence before calling tools.
Use compact metadata for discovery, exact known-file reads for confirmation and
bounded excerpts for context. Load full schemas only when constructing or
validating that operation. Prefer typed operations when actually available.

Map needed capabilities to the current host's declared tools. If no dedicated
tool exists, use a permitted local command; if authority is absent, report the
limitation. A skill or tool description never grants execution rights.

Batch independent read-only calls; serialize dependent operations and mutations.
Project fields, aggregate and filter locally when that reduces unnecessary output.
Keep completeness explicit: pagination or top-k cannot satisfy an exhaustive
request unless every required page or an equivalent complete query is processed.

Reuse evidence only when its declared source, query, configuration and environment
still match. After deterministic failure, inspect the failure class and change
the relevant assumption before retrying. Store large artifacts outside automatic
context and return bounded identities and useful excerpts.

Evaluate whole-task correctness, completion, elapsed time, output bytes and repair
work. Fewer calls alone do not establish better performance. Do not invent token
counts when only bytes are measured.
