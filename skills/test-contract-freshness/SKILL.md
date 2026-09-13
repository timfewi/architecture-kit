---
name: test-contract-freshness
description: Investigate passing tests that may use stale mocks, fixtures or interfaces. Use for test-validity audits and narrow freshness guards; not for ordinary test execution.
metadata:
  provenance: architecture-kit-authored
  capabilities: source.read,source.search,execution.run
---

# Test contract freshness

Trace the intended behavior from requirement to real producer, consumer, test
double and assertion. Identify a defect that the assertion should detect.

Compare current message shape, values, defaults, errors and state transitions.
Exercise the real consumer against the real producer on a small synthetic case.
If unavailable, name the integration gap instead of substituting another mock.

For a reproduced defect or high-risk validity audit, check a known-bad behavior
and its positive control in an authorized isolated copy. A compile error,
unrelated timeout or changed fingerprint is not behavioral detection. Assert
domain effects separately from serialization agreement.

Use fingerprints only for fragile boundaries that benefit from explicit review.
Declare producer, consumer, schema, fixture, tests and behavior-affecting
environment inputs; additions and missing inputs matter. Keep baseline values
reviewable. Update a baseline only after semantic review and relevant checks.

A source hash detects byte changes. It neither proves the test oracle nor
authenticates an observation. Do not add mandatory hashes to every test or a
repository-wide mutation gate because one boundary was audited.

Use the repository's supported environment and report real boundaries exercised,
controls, omissions and any remaining external dependency.
