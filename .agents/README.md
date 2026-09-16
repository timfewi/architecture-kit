# Build a platform from this clone

This directory is temporary development assistance. It neither implements an
agent runtime nor launches agents. Start any coding agent with permission to
work on this clone and ask it to read this guide. A subsequent agent can resume
from the same source and an external handoff. No broker, model SDK, private skill
catalog, Nix installation or particular harness is needed to read this kit.

Read [platform-build](skills/platform-build/SKILL.md), then only the references
needed for the selected work item. The target is the portable agent platform
with retrieval, skills, memory, coordination, observation, terminal and web
clients. The existing agent-starter is the first integration milestone, not
the final completion target. Host and Home Manager configuration stay external.

When the immediate target is a single useful coding workflow, read
[the coding harness fast start](../FAST-START.md) before the full backlog. It
defines the smallest vertical slice and the claims allowed at each milestone;
the backlog remains the source for complete platform work.

## Local commands

Use the existing Python environment declared in flake.nix and requirements.txt,
or an equivalently provisioned environment. Nix/Direnv are optional. The
bootstrap reader uses only the Python standard library; complete kit validation
also needs the existing pinned validator dependencies.

From the clone root:

```sh
python3 -B .agents/bootstrap.py doctor
python3 -B .agents/bootstrap.py next
python3 -B .agents/bootstrap.py resume
```

To retain local check records, choose a dedicated directory outside the clone.
Replace the example absolute directory below with that directory:

```sh
python3 -B .agents/bootstrap.py --state-dir /absolute/external/build-state verify kit-baseline acceptance
python3 -B .agents/bootstrap.py --state-dir /absolute/external/build-state next
python3 -B .agents/bootstrap.py --state-dir /absolute/external/build-state resume
python3 -B .agents/bootstrap.py --state-dir /absolute/external/build-state retirement-check
```

The commands print bounded JSON. Save the resume output with your environment's
normal file tool and add the decisions in [the handoff template](templates/handoff.md).
No automatic history import, agent restart or approval loop exists.

Only verify executes a selected check. Inspect its exact argv in work-items.json
first and run the helper inside your existing authorized execution boundary.
The helper is not a sandbox: it cannot enforce network, filesystem or resource
isolation against hostile code. On POSIX it bounds time/output and kills the
check process group; native non-POSIX execution reports unsupported. Read-only
planning commands remain usable there. Children that deliberately escape the
process group require host supervision. Do not run credential-bearing checks.

## Work items and evidence

[work-items.json](work-items.json) is the editable implementation backlog.
Tasks with null commands are intentionally unconfigured until an implementation
exists. Bind them to real behavioral tests and complete source/dependency inputs
before running them. Existing synthetic checks cannot satisfy live acceptance.
Do not reduce the target or replace missing integrations with passing placeholders.

The helper reports local check observations, not authenticated platform receipts.
A passed check means its exact command exited zero on unchanged declared inputs.
It does not prove the oracle, declared coverage or the truth of human/model notes.
Hashes detect differences, not correctness or authority.

Inputs include the work item, check declaration, helper implementation, declared
source trees, toolchain files, executable bytes and the sanitized environment.
New/deleted files in declared directories invalidate dependent results. Dependencies
must also have current passing checks. Host upgrades and omitted dynamic inputs
may still escape this boundary: declare a reviewed environment identity file for
each real integration check. Do not place secrets in that file.

State is optional for inspection and required for verify. A missing state
directory means no evidence. Malformed state is an error, never an empty success.
A directory is bound to one canonical clone path. Keep one writer per clone;
state is local convenience data, not a concurrent ledger or portable proof.
Records hold digests and result classes, not raw command output. Commands print
a bounded output tail for diagnosis; do not copy sensitive output into handoffs.

## Clone lifecycle

Keep the template's work items uncompleted. Each clone starts with new external
state, independently selected exact runtime/toolchain pins and its own integration
decisions. Read [implementation guidance](skills/platform-build/references/implementation.md)
before choosing components. Runtime build outputs need an explicit packaging
decision in the clone; do not hide source directories from kit validation.

Run the kit's existing checks plus `just test-bootstrap` and `just check-skills`.
Direct Python equivalents are declared in justfile. See
[retirement.md](retirement.md) before removing this directory.
