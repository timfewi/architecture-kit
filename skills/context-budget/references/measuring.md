# Measuring context savings

Fewer bytes or calls alone do not show a better result. Compare equal tasks with
the same model, harness and settings, old method against new.

Record for each run:

- Whole-task correctness against the same oracle, and completion.
- Elapsed time, tool calls, output bytes and rereads.
- Repair work: failed attempts, retries, compaction and re-verification.
- Provider token usage when the host reports it.

Bytes measure bytes. Do not convert them to tokens or claim token savings; leave
token usage null when it was not reported, and keep null distinct from zero.

A shorter answer that omits required evidence fails the correctness gate. For
exploratory samples report medians and dispersion, not a universal ordering. A
routing pilot checks which skill a request selects; it says nothing about task
quality or savings.
