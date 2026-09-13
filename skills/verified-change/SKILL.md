---
name: verified-change
description: Select and run proportionate repository checks for an implemented change and report their evidence and limits. Use when completing a change; not for investigating whether test doubles have drifted.
metadata:
  provenance: architecture-kit-authored
  capabilities: source.read,vcs.inspect,execution.run
---

# Verified change

Derive checks from the changed behavior and the repository's declared environment.
Start with the narrow useful check, then run required combined gates on the final
source. Do not rerun expensive unchanged checks merely to obtain another record.

Use the available authorized executor or direct local commands. A missing pinned
dependency is an environment blocker, not a passing check or necessarily a code
failure. Do not install packages, weaken a gate or refresh expected outputs merely
to restore green.

For affected boundaries, test the real producer and consumer with synthetic data.
A unit mock establishes only the branches it exercises. Inspect the final diff
for accidental state, generated files, unrelated edits and unnecessary complexity.

Bind reusable results to declared implementation, tests, contracts, fixtures,
configuration, dependency and toolchain identities. Changed inputs request review.
An identical digest says only that declared inputs did not change.

Report commands actually run, result classes, relevant evidence level and gaps.
Source tests do not prove build, deployment or live service behavior. Completion
claims must remain within the evidence and the user's requested scope.
