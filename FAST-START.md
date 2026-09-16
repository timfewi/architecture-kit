# Coding harness fast start

This guide describes the shortest useful implementation path through the
architecture kit. It contains no runtime, provider adapter, tool handler, model
loop or deployment configuration. Use it to scope work in a separate
implementation repository.

The fast start changes implementation order, not the contracts or the meaning
of conformance. A synthetic replay remains specification evidence. A harness is
usable only after its real adapter, broker, worker, storage and controller have
produced the required integration evidence.

## Choose the route

Use the `agent-starter` profile for both routes:

| Route | Loop owner | Use when |
| --- | --- | --- |
| Integrate an existing harness | External registered harness | The shortest path to a useful coding workflow. |
| Build a new harness | `agent.first-party-loop` extension | The model loop itself is the product under development. |

The first route is the default fast start. Both routes use the same model
gateway, tool registry, grants, workers, lifecycle, controller and receipts. A
harness's native tools must not bypass those owners.

Record the chosen route, exact adapter and provider revisions, host-service
bindings, initial tool set, workspace authority, budgets and deferred extensions
before implementation. Keep credentials and machine identity outside that
record.

## Initial coding slice

Start with one agent, one model binding, one repository workspace and these
canonical operations:

| Operation | Initial purpose |
| --- | --- |
| `tools.search` | Discover an optional operation without loading the full catalog. |
| `tools.describe` | Load one exact operation contract. |
| `workspace.read` | Read bounded source content. |
| `workspace.search` | Find files and text in the selected workspace. |
| `workspace.replace` | Apply a bounded, reviewable source change. |
| `workspace.exec` | Run one explicitly granted argv-based command. |
| `workspace.verify` | Run a registered verification command and retain evidence. |
| `workspace.git_status` | Inspect the workspace state. |
| `workspace.git_diff` | Review the resulting patch. |

Add file creation, directories, local Git writes, network access, browser tools,
forge mutations and reviewed builds only when a real task requires them. Tool
visibility never supplies authority. Every write and execution still needs the
exact grant, binding, input validation and receipt defined by the starter
contracts.

## Fast-start sequence

### 1. Freeze the implementation boundary

Select `profiles/agent-starter.yaml` and resolve its component closure. Map each
required `platform_services` capability to an existing host owner. If any owner
is absent, record it as implementation work; a service ID or synthetic fixture
does not satisfy the dependency.

Create a requirement-to-evidence matrix covering the selected profile, the nine
operations above and one coding scenario. Bind every planned check to its source,
toolchain and environment identity.

### 2. Bind one real adapter

Choose one harness and one model route. Specify message normalization, streaming,
tool-call correlation, usage accounting, cancellation, resume and error mapping.
Pin exact revisions and verify current provider behavior outside this kit.

The first milestone needs one real adapter. A portability claim still requires
two independent real adapters plus the synthetic contract adapter.

### 3. Prove a read-only path

Exercise a real request that searches and reads a bounded repository snapshot,
returns correlated results and stops within its deadline and budgets. Verify
credential isolation, default-deny authority, source identity, output bounds,
cancellation and process cleanup.

This milestone proves the adapter and worker path without granting mutation.

### 4. Prove the coding path

Run one representative scenario through the same owners:

1. accept a bounded coding objective and selected workspace identity;
2. inspect status, search and read relevant source;
3. request and consume an exact write grant;
4. apply one bounded replacement;
5. run a registered verification command;
6. inspect the final status and diff;
7. persist receipts and let the controller evaluate completion.

Test denial, changed input, timeout, cancellation, invalid tool output and
uncertain execution alongside the successful case. Model text or a zero exit
status alone cannot establish completion.

### 5. Prove durable control and resume

Persist task, run, event, reservation, approval, dispatch, result and completion
state with the identities required by the runtime contracts. Demonstrate restart
and replay without duplicate effects. External waits must consume no model turns,
and unknown usage or uncertain effects must remain unresolved until reconciled.

After this milestone, the implementation can claim the selected starter scope
only when every required source, focused-test, build and live gate has current
evidence.

## Defer from the first slice

Unless selected by the first real use case, defer:

- a new first-party model loop;
- additional adapters and provider fallback;
- semantic memory and reviewed knowledge capture;
- multi-agent coordination and peer discovery;
- research, browser, WASM and reviewed-build capabilities;
- terminal and web product clients;
- desktop, voice and virtual-machine profiles;
- distribution and public release automation.

Deferred capabilities remain absent. Do not implement no-op handlers, permissive
stubs or passing placeholders for them.

## Evidence levels

| Milestone | Minimum evidence | Claim permitted |
| --- | --- | --- |
| Selected slice | Source and schema validation | The design is internally consistent. |
| Real adapter | Focused integration tests | One adapter conforms under tested conditions. |
| Read-only path | Build and live worker evidence | Repository inspection works within the tested boundary. |
| Coding path | Live positive and negative scenario evidence | The tested coding workflow is usable. |
| Durable control | Crash, replay and resume evidence | The selected `agent-starter` implementation is conformant. |

The kit's own checks validate the specification and synthetic fixtures. They do
not advance an implementation through this table.

## Continue after fast start

Use `.agents/work-items.json` as the complete implementation backlog and
`REBUILD-GUIDE.md` for the broader dependency order. Replace every unconfigured
acceptance command in the implementation clone with a real behavioral check.
Continue to adapter parity, retrieval and skills, memory, coordination,
observation, clients and platform acceptance only when the selected product
scope requires them.
