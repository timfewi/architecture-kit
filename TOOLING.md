# Tool selection and operational contracts

The recommended starting point is a small typed capability surface over ordinary
Linux tools. The selection unit is a question plus corpus, authority, output
contract and correctness oracle. There is no universal fastest CLI.

## Choose by the question

| Question | Default engine | Escalation and admission condition |
| --- | --- | --- |
| Read one known file or directory | Native bounded file API | No child process needed; retain file identity and exact byte ranges. |
| Find text in current source | ripgrep; Git grep for tracked revisions | Explicit ignore/hidden/binary/symlink semantics; never substitute ranked retrieval for all matches. |
| Find paths | Native listing or `rg --files` | Add fd for repeated path queries; find for metadata predicates. |
| Match syntax | Tree-sitter or ast-grep | Select one adapter per supported language; same syntax oracle, malformed-source fixtures. |
| Resolve a symbol or references | Existing LSP or source-bound SCIP | Require language/build coverage and current overlays; amortize indexing before adding a resident service. |
| Find relevant documentation | SQLite FTS5 | Ranking is discovery; verify selected source. Embeddings require a measured semantic-recall gap. |
| Select JSON fields | jq or the existing language parser | Use streaming when required by memory; projection determines context volume. |
| Aggregate tables | SQLite | Trial DuckDB for columnar scans/large joins, Miller for streaming CSV, after equal-result tests. |
| Execute/check repository code | Repository-native tools in isolated argv worker | No network, credentials, ambient home or Git writes; exact declared toolchain. |
| Review source changes | Stable Git porcelain and canonical diff | Renderers are optional human views. Git writes and forge publication have separate authorities. |
| Fetch documents | Bounded HTTPS broker | Browser only for rendered/interactable state; PDF parsing/OCR in isolated workers. |
| Repeat pure transforms | Native function first | Trial digest-bound Wasmtime components if compilation/host-call costs amortize. |
| Bound Linux workers | Bubblewrap + supervisor + cgroups + seccomp | Add Landlock where supported; require configured boundaries, not a container marker. |
| Run hostile kernels/system workloads | VM or microVM | Separate guest kernel when threat model requires it; include startup, image and device costs. |
| Diagnose latency | Per-job monotonic time and resource counters | GNU time, then focused strace/perf as authorized. Avoid routine host-wide traces. |

This is a functional shortlist, not an installation manifest. Preserve a target
repository's pins. Before admission record exact release/revision, package and
executable digest, documentation date, supported platform, owner, oracle and
fallback. The kit adds no runtime packages. Optional candidates remain absent
until admitted. [Research](research/FINDINGS.md) gives evidence and caveats.

## Discovery and ownership

The source of reference tool metadata is `inventories/agent-tools.json`.
`schemas/tool-contracts.schema.json` owns its referenced payload contracts.
`inventories/capabilities.json` is a checked grouping of the same tools. A
runtime must generate its adapter view from these definitions and bind dispatch
to the definition digest and a separately registered handler identity.

The initial surface contains tools.search, tools.describe, workspace.list,
workspace.read, workspace.search, workspace.create, workspace.mkdir,
workspace.replace, workspace.environment, workspace.exec, workspace.verify,
workspace.git_status and workspace.git_diff. Thirteen is a tunable starter
configuration, not an empirically optimal universal count.

Optional families cover exact Git writes, code intelligence, library docs,
research, browser actions, artifacts, local data, compute, Wasm, reviewed builds,
guidance, memory proposals and forge operations. GitHub, GitLab, a docs service
or an MCP transport is an adapter choice, not a core name. The catalog is a
reference subset: add a capability only with a distinct question, typed contract
and acceptance fixtures. Do not expose synonyms with indistinguishable routing.

## Request and result semantics

The model supplies only the selected operation's input. The trusted dispatcher
adds call lineage, active grants, policy/schema digests, immutable handler and
toolchain identity, and an absolute deadline in its own monotonic clock domain.
A timeout requested by a caller can only lower the remaining host budget.
Across machines transmit remaining duration with a new local deadline; never
compare unrelated monotonic clocks.

All inputs and results must validate. Metadata byte ceilings are enforced over
encoded UTF-8 before parsing and before transport; JSON Schema maxLength counts
characters. Reject duplicate JSON keys, non-finite numbers, excess nesting,
unknown properties and unresolved references. A schema cannot establish grant
ownership, DNS safety, race-free path resolution or resource containment.

Results contain status, typed data/error, coverage, provenance, continuation
and an optional immutable artifact handle. Successful records and partial
records have data and no error; errors and uncertain outcomes carry a typed
error. outcome_uncertain requires reconciliation and forbids automatic retry.
A partial result cannot claim complete coverage. An empty exhaustive scan can
be no_match only if it completed. Ranked
top-k and unsupported/stale indexes do not prove absence.

Byte coordinates are zero-based UTF-8 offsets with an exclusive end; converted
LSP coordinates must preserve their declared encoding. Invalid UTF-8 paths or
content are unsupported in the text interface and require an artifact/byte
adapter. Do not silently replace bytes with replacement characters.

Inputs with a cursor property accept the exact returned continuation object on
the next call; omit it or use null on the first page. Keep all other input
values unchanged. The host computes the query digest over normalized inputs
excluding cursor, then binds the cursor to caller/grant, corpus, source
generation, schema, ordering, scope and expiry. It reauthorizes every page.
The visible digests are evidence, not authentication; a cursor must be backed
by host-owned state or an authenticated token. A stale or changed query fails.
Cursor reads resume the saved snapshot; they never repeat a mutation or job.
workspace.list and workspace.git_status default to 10 records, capped at 100;
the host applies these defaults, not a schema validator.

Byte-read inputs without cursor resume with offset_bytes against the same
expected digest or immutable artifact. Other non-paged outputs cannot promise
a cursor. Truncated data must provide a usable cursor or immutable artifact;
otherwise return a resource_limit error requiring a narrower request. Stable
order includes a deterministic tie-breaker. Full artifacts stay outside prompt
context. Completion refers to the requested remaining selection; a last page
does not retroactively prove that the caller inspected earlier pages.

coverage.returned counts array entries/rows for hits, listing, git_status and
table, one for other non-null payloads, and zero for absent data. A known total
counts the whole query selection, not just the current page, and cannot be
smaller than the page. Text sha256 identifies the full byte source, while
offset_bytes plus encoded chunk length cannot exceed total_bytes. Anchors must
have ordered byte endpoints, and every table row must match its column count.
These relationships require semantic checks in addition to schema validation.
The synthetic [result examples](examples/tool-results.json) cover all ten
shared output shapes; they are not execution receipts.

## Execution, mutations and retries

workspace.exec accepts a registered immutable command ID plus argv. The host
resolves it without ambient PATH/configuration and enforces total argv/stdin,
stdout/stderr, wall time, memory, CPU and process limits. A shell interpreter,
plugin, build script or compiler macro executes code even when invoked via argv.
Inputs from a repository therefore run only inside a disposable worker.

workspace.replace binds the expected file digest and match count; create is
exclusive; mkdir creates one level. Validate relative paths and securely resolve
beneath the grant using directory handles and symlink restrictions. A regex on a
path is an input filter, not the filesystem boundary. Use a temporary sibling
and atomic replacement only after rechecking source identity; report conflicts.

Git fetch changes local metadata and uses network. Push and forge publication
may change remote state. Memory proposals write state but cannot approve claims.
Approval is required only when current task authority does not already cover an
exact operation. Scope, expected state, expiry and replay checks still apply.

Reads may retry after a changed condition. Mutations and execution reconcile
dispatch before retrying. A lost response never means nothing happened.
Idempotency keys are scoped to operation, inputs and caller, and mismatched
replays fail. Build state is held by the supervisor; status/result calls do not
restart jobs. A succeeded job must expose its immutable result artifact;
other job states have result null, with diagnostics in the outer artifact when
needed. A settled process reports exactly one of exit_code or signal.
Cancellation settles the owned process tree before releasing capacity.

## Linux implementation recipe

Use native bounded reads for simple evidence. Send repository code to fresh
user/mount/PID/network namespaces with private procfs, explicit source/output
mounts, minimal devices, no credentials and no broker sockets. Drop capabilities,
set no_new_privs, apply a reviewed child seccomp policy and supervise the entire
owned cgroup. Set memory/CPU/PID limits and a deadline; verify cancellation,
disconnect, fork pressure and descendant cleanup.

Landlock is an additional restriction layer. Probe the running ABI and compare
its enforced rights against the profile's required rights. A mandatory boundary
that is unavailable blocks support; do not silently downgrade it. systemd scopes
can own resource accounting/lifetimes on systemd hosts; another supervisor can
implement the same contract. Rootless OCI packaging does not prove these
properties. No runnable privileged sandbox recipe is claimed by this kit.

## Quality and cost experiments

Use the benchmark schema and [BENCHMARKS.md](BENCHMARKS.md). First validate
positive, negative and ambiguous routing cases. Then compare:

- Full catalogs versus compact search plus one loaded schema.
- Full tool output versus oracle-preserving projection and artifact handles.
- Unindexed reads versus warmed syntax/semantic indexes, including build/update.
- One agent versus bounded independent investigation, including coordination.
- Native transforms versus cached Wasm only for repeated pure workloads.

A candidate must pass the same correctness and authority gates. Reject
dominated candidates before selecting workload-specific latency/token tradeoffs.
Unknown provider token usage stays null; bytes are separately measurable.
