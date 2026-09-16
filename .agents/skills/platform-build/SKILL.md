---
name: platform-build
description: Implement the portable agent platform from an architecture-kit clone, or resume that implementation from its bounded handoff. Do not activate for routine kit edits or operating an already implemented platform.
---

# Platform build

Use the clone's work-items.json as the dependency-ordered implementation backlog.
Start with the bootstrap doctor and next commands in the temporary build guide.
Read the selected task's source references and acceptance criteria; do not preload
all architecture files or require the platform's future tools to orient yourself.

When the requested first milestone is a useful coding workflow, read the clone
root's `FAST-START.md` and use its initial slice to order the relevant backlog
items. The fast start does not waive dependencies, acceptance criteria or the
remaining work for a complete platform target.

Implement one bounded work item at a time. Preserve the final selected target
through compaction and handoffs. A starter integration is a milestone, not
completion of the whole platform. Add narrowly scoped child tasks when a work
item exceeds one useful session; retain its acceptance criteria.

Load [implementation.md](references/implementation.md) when choosing modules,
host bindings, runtime pins or verification boundaries. Load
[handoff.md](references/handoff.md) when settling a session or recovering one.

Before declaring a work item covered, replace its null check commands with real
integration or behavioral checks, review their input closure and run them through
an authorized execution facility. Local bootstrap records are hints for the next
agent; only the implemented trusted controller can issue platform evidence.

Keep the public operating skills independent of this temporary skill.
Do not recreate host/dotfiles setup, import private code, publish artifacts or
launch additional agent sessions as an implied part of following these instructions.
