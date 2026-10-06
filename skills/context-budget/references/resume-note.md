# Resume note

Write one before compaction, handoff or a long wait. Keep it short enough to load
automatically; replace the previous note instead of appending to it.

| Field | Content |
| --- | --- |
| Goal | The request and its acceptance criteria, each marked open, met or blocked. |
| Decisions | What was chosen and why; alternatives already rejected. |
| State | Changed files and other effects, with the digest, revision or job identity each was observed at. |
| Evidence | Commands run, their result class and where large output is stored. |
| Failures | Failed actions by fingerprint, so a resumed session does not repeat them. |
| Waiting | The exact request issued, what result is expected and what resumes the work. |
| Unverified | Checks not run, unavailable evidence and untested claims. |
| Next | The single next action. |

On resume, recheck the working tree and any source whose digest differs from the
note, then trust the rest. A note is a claim about an earlier moment, not
evidence that it still holds.

Keep credentials, personal data and raw traces out of the note; refer to them by
handle. Do not copy large output into it.
