# Harness tool review — 2026-10-04

This review covers the local collection's 21 canonical tool repositories,
including this kit, plus one public mirror, two empty directories, the archive
inventory and publication preparation guidance. The collection README selects
development sources. A mirror or rewritten release candidate does not replace
its canonical checkout.

The machine-readable [register](harness-tools.json) contains each directory's
purpose, source observation and whole-file digests for selected evidence. Review
used README/interface guidance, relevant implementation excerpts and test
definitions. Other repositories' tests, builds, VMs, renderers and deployments
were not run for this architecture review. Historical verification notes are
reported observations; they are not acceptance evidence for today's revision.

Private source names and relative checkout locations identify local evidence;
there are no private remotes, machine paths, source bodies or session records.
No private dependency is added to the kit. A public clone can validate this
register and the kit without those sources. The optional external check needs
the original layout and explicitly reports unavailable or changed evidence.

<a id="L01"></a>
## L01 — Compose independent owners

The toolbox supplies pinned commands, the harness package repository supplies
native agents, and the runtimes supply different execution boundaries. Host
composition provides selected packages and service bindings. The lighter
operator runtime and a separate-account runtime are distinct products with
different limits. Do not turn a CLI or package into an implicit security boundary.
Adopted in [Devtool boundaries](../DEVTOOL-START.md#boundary).

<a id="L02"></a>
## L02 — Bootstrap declarations, then build one slice

The scaffolder adds missing declaring files with rollback and preserves existing
files; it does not migrate customized environments. The checker runs explicit
argv recipes from the owning repository. Use those tools when available, then
exercise one real operation before adding adapters or services. Templates and
a ready plan do not prove the product works.
Adopted in [DEVTOOL-START.md](../DEVTOOL-START.md).

<a id="L03"></a>
## L03 — Bind bounded retrieval to its corpus

The evidence reader binds pages to file/result digests and rejects stale pages.
Its search excludes ignored/hidden files and its diff excludes untracked files.
The AST index reports precision limits rather than guessing dynamic or ambiguous
edges. Use source-bound windows, continuation guards and explicit corpus limits;
an index edge remains a lead until confirmed in source.
Adopted in [tool contracts](../DEVTOOL-START.md#contract).

<a id="L04"></a>
## L04 — Repository context is an explanation with receipts

Tabula separates a small human-written entrypoint from hashes of its cited files.
Updating hashes cannot correct an explanation. Use exact source links and a
short ownership/flow map; matching bytes prove freshness only for cited evidence.
This kit applies that distinction to its own learning register.
Adopted in [learning checks](../LEARNING.md#review).

<a id="L05"></a>
## L05 — Derive repeated version facts from source

Project-docs renders reviewed templates from explicit JSON, TOML, Python literals
or an offline Nix attribute. Harness package pins also provide the authoritative
versions instead of duplicating them in prose. Keep version data derived and
interpretation human-reviewed. Installed runners and consuming pins can lag a
source checkout; new source behavior must not be assumed available on the host.
Adopted in [fresh documentation](../DEVTOOL-START.md#learning).

<a id="L06"></a>
## L06 — Measure privately and enforce budgets separately

The command meter records time, byte counts and status without argv or output
contents. System-health uses interval counters and aggregate-only private history;
missing metrics remain unavailable. Neither is an enforcement mechanism or proof
of task-quality improvement. Keep measurements private and relate them to task
outcomes; let the execution host enforce limits. Offline Nix comparison can
explain selected options and direct derivation inputs without building or activation,
but still requires cached inputs and trusted evaluation authority.
Adopted in [measurement](../DEVTOOL-START.md#measurement).

<a id="L07"></a>
## L07 — Handles and cleanup are part of the operation

The meter bounds blocked output consumers, log-lock waits and descendant cleanup.
Rendering has costly jobs and explicit status/cancel operations. The tmux cockpit
observes process state and task excerpts; those are not readiness or completion.
Retain a specific live handle, bound waits and settle owned descendants. Do not
start replacement work just because observation timed out.
Adopted in [tool lifecycle contracts](../DEVTOOL-START.md#contract).

<a id="L08"></a>
## L08 — Shared identity and publication need explicit scope

The swarm's task board does not infer agent completion, and fleet workers require
an explicit public Git profile. Runtime modules need host-owned identity and
activation. Current-file privacy scans exclude history; publication mirrors use
reviewed allowlists and digests. Archived histories and release preparation copies
remain separate from active development. Passing source checks cannot grant
publication authority or establish history privacy.
Adopted in [learning evidence](../LEARNING.md#evidence).

<a id="L09"></a>
## L09 — Research is an independent service with untrusted results

The Research client can be packaged independently of HTTP/browser/service
dependencies and communicates over a host-bound socket. Its source explicitly
leaves deployment acceptance open. Runtime wiring and browser fixtures cannot
substitute for service egress/isolation evidence. Preserve the existing kit's
host-owned research boundary and distinguish each evidence level.
Adopted in [tool boundaries](../DEVTOOL-START.md#boundary).

<a id="L10"></a>
## L10 — Remove redundant guidance and test actual delivery

The skill library now emphasizes short coherent jobs, on-demand references and
merging redundant guidance. The routing engine may abstain; a suggestion is not
proof a skill was read or applied. The harness package repository distinguishes
configuration delivery and start/answer smoke tests from paired task evaluation.
Keep policy, repository facts and optional skill routing with their owners.
Adopted in [the maintenance loop](../LEARNING.md#review).

<a id="L11"></a>
## L11 — Missing coverage and changed upstream bytes remain failures

The checker and scanner distinguish findings from incomplete coverage. Offline
Nix comparison reports evaluation errors rather than inventing partial success.
Never reuse historical runtime evidence for a changed pin, or update a checksum
merely to restore green checks. Treat offline option evaluation, package builds,
runtime integration and activation as different claims. An unused runtime lab
was removed from the local collection at the owner's request during this review;
it is not an active source or a dependency of the kit.
Adopted in [learning evidence](../LEARNING.md#evidence).

<a id="L12"></a>
## L12 — Recheck the evidence affected by a change

Visual QA shares a CLI/MCP service and recaptures selected findings' states;
baseline approval is explicit. ASCII rendering separates a cheap preview from
full rendering and reports loop-seam measurements. Use focused feedback before
costly workloads, preserve the actual visual evidence and record browser skips.
A deterministic metric alone cannot establish visual quality.
Adopted in [Devtool verification](../DEVTOOL-START.md#measurement).
