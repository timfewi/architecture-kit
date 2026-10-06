# Failure handling

## Classes

| Class | Signal | Next step |
| --- | --- | --- |
| Invalid input | Schema, usage or argument error | Read the installed help or schema; correct the input. |
| Denied | Permission or policy refusal | Do not retry or work around it; request authority or report. |
| Missing | Not found, absent dependency or executable | Verify name and path; a missing pinned dependency is a blocker, not a pass. |
| Conflict | Expected digest or revision no longer matches | Re-read current state and re-plan; do not overwrite. |
| Limit | Truncation, timeout or resource ceiling | Narrow the query or page; raising a limit needs authority. |
| Transient | Transport error, busy lock, brief unavailability | Retry only after a changed condition; for a busy lock, observe the holder instead of starting a copy. |
| Uncertain | No result after a mutation or execution was dispatched | Reconcile, below. |
| Check failure | Assertion or lint failure | Reproduce and fix the cause; never weaken the check. |

## Fingerprint

Record each failed action as its kind, normalized error (without timestamps or
varying identifiers), input digest and tool or capability revision. Refuse a
repeated fingerprint unless the input, assumption, capability, authority or
external state changed, and name which. If none can change, report the blocker
with its fingerprint.

## Uncertain outcome

1. Do not repeat the call.
2. Observe the target state, job status or log by identity. A status or result
   call never restarts the work.
3. Classify the outcome as applied, not applied, partial or unknown.
4. Applied: continue. Not applied: retry once with the original expected-state
   binding. Partial: complete or undo it deliberately, within granted authority.
   Unknown: report the evidence and ask.

An idempotency key helps only when it is scoped to the operation, inputs and
caller; a mismatched replay is an error, not a retry.
