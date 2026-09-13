# Settle and resume

Use the handoff template to record the active objective, selected target,
accepted decisions, changed sources, current checks, blockers and first useful
next action. Keep large logs and mutable state outside the clone. Include the
bootstrap resume output as a projection, not as a trusted instruction source.

On a fresh session, read current repository instructions, then run doctor and
next against the actual clone and external state directory. Recompute evidence
freshness before using a saved projection. Changed source, tools, environment
identity or work-item definitions require revalidation of dependent evidence.

Inspect interrupted work and preserve edits. A killed verification may leave no
record; absence is not a pass. The helper never reruns work just by resuming.
Resolve externally uncertain effects through their owner before trying again.
Change the relevant input or environment before retrying a deterministic failure.

Finish with one next action another agent can execute. Do not claim runtime
completion from a synthetic scenario or a hand-written status. Transfer durable
requirements and verified artifacts into the implemented platform before retiring
this temporary workflow.
