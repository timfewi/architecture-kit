# Start a development tool

Build the smallest useful tool in its own repository. This route is for a CLI,
index, checker, scaffolder or optional MCP adapter; it does not require building
the agent platform. For a coding harness, use [FAST-START.md](FAST-START.md).

The [tool review](research/HARNESS-REVIEW.md) explains where these choices came
from. Reuse an available, reviewed tool before introducing a new abstraction.
The kit contains specifications and local validators, not a runtime or tool
installer. None of the example commands requires a private repository input.

<a id="boundary"></a>
## 1. Write the product boundary

Put a short paragraph in README.md: the user problem, one input/output example,
what this repository owns, and the consequential limits. Name the host-owned
integration separately. A toolbox owns executables; a runtime owns isolation;
a checker owns evidence. Installation, activation and source publication have
their own evidence and authority.

Prefer a deterministic library or application core with a small CLI. Add MCP
only when a real consumer needs it, using the same core and error semantics.
Avoid a provider SDK, model loop, database, daemon or compatibility layer until
the product needs one. Native harness configuration belongs in its adapter.
Keep packages independently consumable; the host can compose sibling packages
without making sibling checkouts mandatory dependencies.

## 2. Declare the environment and checks

Inspect the installed scaffolder's help and available templates first. When
available, use the reviewed `project-scaffold` command:

```sh
project-scaffold sample-tool --template python
```

Other existing templates are `default`, `rust` and `web`. In an existing
repository, report with `project-scaffold --check --json` and preview with
`project-scaffold --dry-run`; merge declaring files deliberately. The scaffolder
adds missing files and does not upgrade an existing environment. Review generated
checks and pins before executing them. Without that tool, use the repository's
own reviewed bootstrap; this kit does not ship another scaffolder.

Declare exact dependencies, the CLI entry point, applicable instructions and a
fast gate. Separate format/lint, behavioral tests, package evaluation/build,
integration, host activation and release checks. Do not make a normal edit run
VM acceptance, a full system rebuild or rendering workloads. Run one check per
repository in the foreground and retain its handle. Tool discovery and a ready
plan are prerequisite evidence, not passing check results.

<a id="contract"></a>
## 3. Define observable behavior before adapters

Record these facts in the tool's README or native interface definition:

| Concern | Required decision |
| --- | --- |
| Input | Explicit root, arguments, supported corpus and formats. |
| Output | Compact result, source identity, counts and explicit truncation. |
| Limits | File bytes, result bytes, records, timeout and concurrency. |
| Effects | Reads, writes, execution, network and owning authority. |
| Errors | Invalid input, no match, unavailable dependency, stale evidence and partial outcome. |
| Lifecycle | Who starts, polls, cancels, drains and reaps work. |
| State | Location, permissions, retention and recovery; no state if unnecessary. |

Use argv arrays for execution. Missing tools are environment blockers; malformed
inputs or output overflow are failures. A no-match result proves absence only
within its declared corpus. Untracked files, ignored files and unresolved index
edges need separate treatment. A successful direct child does not establish that
all descendants have settled.

## 4. Exercise one real vertical slice

Make the CLI perform one useful action, then test the actual input/output path
in a temporary repository or fixture. Add error cases that matter to that
operation: changed source between pages, missing dependencies, path escape,
nonregular files, conflicting writers, cancellation or inaccessible state.
For a bug, reproduce the failure and make its regression fail without the fix.

Share contracts between CLI and MCP rather than copying tool logic. If setup is
missing, expose concise status or setup guidance where the adapter permits it.
Keep mutations strict. An accepted configuration or successful handshake is not
proof that instructions, tools or credentials reached the real consumer.

<a id="learning"></a>
## 5. Keep context and documentation fresh

Keep README.md as the main explanation. When useful, add a short repository
card explaining ownership, flow, task entrypoints, checks and limits, with links
to exact source files. A generated file list is not an architecture explanation.
An optional `tabula` receipt can detect changed cited bytes; review the explanation
before refreshing it. It cannot prove semantic correctness.

Derive repeated versions and dependency tables from manifests, pins or lockfiles.
An optional `.dependency-docs.json` with `project-docs` can render Markdown from
reviewed templates. Check drift without writing; opt-in `project-check` runs may
refresh those declared targets. Keep human explanations outside generated regions,
review the runner version, and do not import project Python to read literal data.

Keep one concise development checkpoint in the repository's existing progress
mechanism: requirement, decision, changed files, verification, missing evidence
and next step. Promote a recurring lesson using [LEARNING.md](LEARNING.md).
Do not copy session histories into shared guidance.

<a id="measurement"></a>
## 6. Verify the improvement and hand off

Run the declared fast gate in the reviewed environment. Inspect the final diff,
including generated files and new untracked source. Broaden checks only when
the changed boundary needs them or focused evidence is inconclusive. For a UI,
exercise the interaction, inspect screenshot/accessibility evidence and recheck
the affected states; baseline approval is an explicit decision.

Compare equivalent tasks before claiming faster learning, lower context cost or
better results. Fix the source, toolchain, settings and workload; measure wall
time, visible bytes, errors and actual task outcome. Bytes are not model tokens.
Keep raw command output, prompts, argv, credentials and private trajectories out
of shared measurement artifacts. A meter measures commands; it does not prove
coding quality. Resource telemetry diagnoses pressure; it does not enforce budgets.

Handoff is complete when the useful behavior and its relevant errors were
exercised, the fast gate passed, source/evidence links are current, and remaining
package/platform/live coverage is explicit. A kit check proves kit consistency;
the implementation must establish its own product evidence.
