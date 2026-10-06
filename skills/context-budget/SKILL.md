---
name: context-budget
description: Keep model-visible context small and recoverable on long or output-heavy tasks through summaries before bodies, bounded reads, projection, artifact handles, evidence preservation, resume notes and concise answers. Use when output volume, rereads or compaction threaten the task; not for choosing or sequencing tool calls.
metadata:
  provenance: architecture-kit-authored
  capabilities: source.read,source.search,execution.run
---

# Context budget

Context is a bounded resource. Spend it on what changes the next decision.

**Summaries first.** Ask for counts, paths, outlines or digests before bodies,
then read the smallest range that settles the question.

**Bound at the source.** Limit output with the tool's own range, limit or filter
options rather than trimming afterwards. Report truncation and never guess the
missing content. An exhaustive request still needs every page or an equivalent
complete query.

**Project.** Select fields, filter and aggregate locally so only decision-relevant
values enter context, provided the projection keeps what the answer needs:
identity, location, count and error.

**Hold handles, not bodies.** Store large output outside automatic context and
keep a handle: location, size, digest, the query that produced it and a short
excerpt. Reread by range. Do not reread a source whose path and digest are
unchanged.

**Preserve evidence.** Before compaction, handoff or a wait, keep requirement
status, decisions with reasons, exact identifiers, commands run with their result
class, failed attempts and unavailable evidence. Write them as a
[resume note](references/resume-note.md). After resuming, recheck only evidence
whose source may have changed.

**Answer briefly.** Lead with the result, then the evidence and limits. Do not
restate tool output. A shorter answer that omits evidence the request needs fails.

Claims of savings need a comparison; see [measuring](references/measuring.md).
Bytes are not tokens.
