# Research findings

Reviewed: 2026-09-13. Scope: the supplied architecture kit and Linux tools for
agent retrieval, execution, quality and context efficiency.

The strongest recommendation is a small, typed interface over established
tools, with workload-specific escalation. Adding more binaries, schemas or
agents is not itself an optimization. The supplied catalog is useful discovery
material, but its references to another repository and previous implementation
work do not prove anything about this kit.

## Audit of the supplied kit

| Requirement | Initial evidence | Change and remaining proof |
| --- | --- | --- |
| Reusable architecture | Core decisions mixed with a completed generation claim, model-family slot counts and Nix-specific build fields | Stable names, neutral capacity rules, generic reviewed recipes and an optional Linux reference. Runtime conformance remains required. |
| Precise tools | 78 metadata rows, generic descriptions, no concrete payload schemas | 51 distinct reference operations, 13 initially visible, per-operation inputs and shared typed result contracts. No handler implementation is claimed. |
| Correct authority metadata | mkdir/replace marked without effects; memory capture marked read; fetch omitted its local metadata write | Explicit multi-effect records and capability parity checks. Actual broker enforcement is a deployment gate. |
| Portable profile | Toolchain and research dependencies reached the declarative host | Explicit platform.services contract and transitive dependency check; portable selections exclude reference host components. |
| Strict schemas | Mostly object shells, unbounded strings/lists, a path accepting traversal, no cross-file validator | Bounded closed shapes, offline references, root-relative artifacts, duplicate-ID/dependency/transition checks and negative fixtures. |
| Self-contained verification | A generator and drift checks were described but absent | Local checker, standard validator entry point, synthetic tests and deterministic manifest refresh. |
| Proven cost improvement | No local receipt | A measured synthetic rg/grep experiment and actual catalog byte counts; no model-token or task-success claim. |

The initial repository had no commits, environment manifest, lockfile, AGENTS.md
or local implementation/test command. All original files were untracked.
There was therefore no committed baseline diff; the initial manifest supplied
file digests. Changes preserve the design's useful authority, supervision,
evidence and recovery principles while removing unsupported completion claims.

## What the primary evidence supports

1. **Text, syntax and symbols require different tools.** ripgrep's official
   guide documents its ignore, hidden, binary and symlink defaults [R1]. Those
   defaults change the corpus. SCIP encodes language-independent navigation
   facts [R3], but does not prove a current index, complete language coverage,
   resolved runtime calls or superiority over a warm LSP. Use literal search
   for literal questions; require a semantic oracle for references.

2. **Projection and streaming have different effects.** jq documents selected
   filters, compact output and incremental path/leaf streaming [R2]. Streaming
   can bound memory and improve first-result time. It may still produce more
   model-visible data. Projecting required fields and aggregating locally
   controls information volume. Neither mechanism proves a token percentage.

3. **Local indexes can help repeated work.** SQLite FTS5 supports a local full-text
   table, matching and relevance ordering [R4]. A result order is unspecified
   without an explicit sort. FTS is useful for finding documents; exact source
   evidence must retain anchors and freshness. DuckDB/Miller and embeddings
   remain optional workload trials, with no fabricated comparison here.

4. **Linux isolation is composed and version-sensitive.** Bubblewrap explicitly
   leaves policy construction to its caller [R5]. systemd resource control uses
   a cgroup hierarchy [R6]. Landlock restricts ambient rights as an additional
   layer [R7]. A container name or one flag proves none of the required combined
   boundaries. Probe the running kernel and required rights; reject an
   unsupported mandatory boundary. The fetched kernel documentation identifies
   a development kernel snapshot; it is not a recommended release pin.

5. **Wasm is useful for selected repeated computation.** Wasmtime describes
   deterministic fuel and less deterministic epoch interruption [R8]. Host
   calls, compilation, startup and memory still need their own limits and
   measurement. Do not replace inexpensive native transforms merely to add a
   runtime. Vendor overhead figures are not measurements of this kit.

6. **Schema shape validation and operational validation are distinct.** Draft
   2020-12 explicitly treats format primarily as annotation [R9]. Enable
   assertion checks deliberately. uniqueItems compares complete values; it
   cannot ensure unique IDs with different descriptions. Metadata, reference
   integrity, path ownership, expected-state equality, cursor scope and byte
   limits require additional checks. Composition closes at the outer result
   with unevaluatedProperties; reusable child definitions remain explicit.

7. **Microbenchmarks are supporting evidence.** Hyperfine documents warmups, raw
   exports and no-shell execution for small commands [R10]. The supplied
   runnable benchmark instead uses a fixed argv subprocess and standard-library
   monotonic timing to avoid adding a benchmark dependency. Its measurements
   include process startup; its small sample makes no tail claim.

## Actual local experiment

The recorded [receipt](retrieval-measurement.json) uses ripgrep 15.2.0 and GNU
grep 3.12, each bound to the actual executable SHA-256, across 102 explicit
synthetic files. Each candidate passed positive, negative and ambiguous literal
oracles, then ran twenty measured samples per case.

| Case | ripgrep median | grep median | Equal required output |
| --- | ---: | ---: | --- |
| Positive | 2.438 ms | 2.194 ms | yes |
| Negative | 2.660 ms | 2.253 ms | yes |
| Ambiguous literal | 2.768 ms | 2.167 ms | yes |

On this tiny explicit-file workload grep's measured median is lower. This
does not rank recursive repository traversal, regex engines or semantic indexes.
The measurements are exploratory, collected in candidate blocks with
uncontrolled warm caches; they are not randomized causal or tail estimates.

The actual catalog serializes to 37,251 compact metadata bytes. Discovery
summaries occupy 5,565 bytes; initial metadata occupies 9,583 bytes. These
figures exclude expanded schemas, messages, tool results and model calls.
They show a smaller presentation surface, not an 85% reduction in task tokens.

## Useful next designs to test

- **Evidence slices:** return the changed source ranges, adjacent declarations
  and the exact requirement they support. Retain a cursor to the complete
  result. Evaluate all-impact tasks to catch missing evidence.
- **Dependency-aware reuse:** cache only with query, corpus, scope, source,
  schema, toolchain and policy bindings. Invalidate affected dependencies and
  reauthorize every cache read. Count invalidation/setup costs.
- **Query planning outside the prompt:** choose exact text, syntax, symbols or
  aggregation from an explicit operation and oracle. Expose ambiguity when
  evidence cannot select a route; avoid opaque automatic semantic substitution.
- **Bounded batching:** group independent reads of known paths and selected
  fields while retaining per-item outcomes and one-writer mutation ownership.
  Measure coordination and error recovery as well as fewer tool calls.
- **Quality-first admission:** compare the Pareto frontier after equal
  correctness/security gates. Keep reference fallbacks and remove candidates
  that add closure/routing cost without measured task value.

These are proposals with tests, not implemented runtime optimizations.

## Documentation and version verification limits

Direct retrieval of json-schema.org and Anthropic articles returned HTTP 403.
Search discovered relevant Anthropic articles, but snippets were not promoted
to primary evidence. An initial search timed out. The official JSON Schema
release source on GitHub was accessible and was used instead.

Context7's nominal Draft 2020-12 query included a newer working-draft format
claim. It was cross-checked against the published release source and rejected
for this kit's dialect. This is why version-matched primary evidence matters.

The current upstream stable validator release was independently checked through
[GitHub's releases API](https://api.github.com/repos/python-jsonschema/jsonschema/releases/latest): jsonschema 4.26.0, not prerelease, with wheel SHA-256
`d489f15263b8d200f8387e64b4c3a75f06629559fb73deb8fdfb525f2dab50ce`.
Its exact-release referencing documentation supports the offline registry [R11].
PyYAML 6.0.3 was also confirmed as the upstream stable release [R12] and is
already present in the base worker. These are the only new development
dependency pins; a target must supply their resolved immutable closure.

This worker has no registered repository toolchain, jsonschema or referencing.
The full standards validator is therefore an environment dependency, not
something this research claims to have run. No networked installation, Direnv
trust change or substitute schema engine was used.

## Primary source register

All entries were retrieved on 2026-09-13. Digests and inspected coverage are
recorded in [sources.json](sources.json). A source establishes only the stated
mechanism. Mutable upstream branches are research snapshots, not executable
pins.

| ID | Source | Inspected evidence |
| --- | --- | --- |
| R1 | [ripgrep exact-release guide](https://github.com/BurntSushi/ripgrep/blob/15.2.0/GUIDE.md) | Literal/regex behavior and automatic filtering. |
| R2 | [jq 1.8 manual source](https://github.com/jqlang/jq/blob/master/docs/content/manual/v1.8/manual.yml) | Projection, stream, compact output, exit semantics. |
| R3 | [SCIP upstream](https://github.com/sourcegraph/scip) | Index purpose, schema and language indexers. |
| R4 | [SQLite FTS5](https://sqlite.org/fts5.html) | Table/query model and relevance ordering. |
| R5 | [Bubblewrap security policy](https://github.com/containers/bubblewrap/blob/main/SECURITY.md) | Caller owns sandbox policy; version-specific details must be checked separately. |
| R6 | [systemd resource-control source](https://github.com/systemd/systemd/blob/main/man/systemd.resource-control.xml) | Hierarchical cgroup resource controls. |
| R7 | [Landlock kernel documentation](https://docs.kernel.org/userspace-api/landlock.html) | Ambient-right restriction, feature detection and ABI-dependent coverage. |
| R8 | [Wasmtime interruption](https://github.com/bytecodealliance/wasmtime/blob/main/docs/examples-interrupting-wasm.md) | Fuel/epoch tradeoff; no local performance claim. |
| R9 | [Published JSON Schema validation source](https://github.com/json-schema-org/json-schema-spec/blob/2020-12/jsonschema-validation.xml) | Annotation/assertion distinction and equality semantics. |
| R10 | [Hyperfine upstream](https://github.com/sharkdp/hyperfine) | Warmup, export and no-shell measurement. |
| R11 | [jsonschema exact-release references](https://github.com/python-jsonschema/jsonschema/blob/v4.26.0/docs/referencing.rst) | Explicit in-memory reference registry. |
| R12 | [PyYAML stable release](https://github.com/yaml/pyyaml/releases/tag/6.0.3) | Stable status and Python compatibility declaration. |

## Current implementation evidence

| Deliverable | Status | Evidence and scope |
| --- | --- | --- |
| Generic names and portable dependency closure | implemented + verified | Current-source generation-label search, component/profile checker and semantic fixtures. |
| Precise tools and conditional Linux choices | implemented + verified | 51 metadata definitions, 13 initial operations, 22 software choices; schema references, effect and capability parity checked. This verifies specification structure, not handlers. |
| Strict JSON Schema acceptance | implemented, not currently verified | 15 schemas and the standard-validator test suite exist. Full check exits 2 with ENVIRONMENT_BLOCKED because jsonschema/referencing are absent. |
| Research and creative selection proposals | documentation only | Twelve inspected primary sources, version cross-checks, explicit limitations and follow-up experiment oracles. |
| Synthetic retrieval correctness and timing | implemented + verified | Six candidate/case records, 20 measured samples each; runner, executable, catalog and corpus bindings. Model tokens remain unavailable. |
| Kit integrity and Python quality | implemented + verified | Manifest/semantic check, 18 semantic regression tests, Ruff lint/format, local link check. Baseline scan: three Python rules, two source files, zero findings and parser errors; two test files excluded by baseline policy. |

The remaining completion dependency is the full standards-based validator and
its schema acceptance suite in a reviewed immutable repository toolchain.
No additional runtime feature or host deployment is part of this kit change.
The missing validator was not replaced with a hand-written approximation.
