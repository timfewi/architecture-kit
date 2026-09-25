# Architecture kit

A specification and verification kit for portable agent systems. It defines
profiles, tool contracts, runtime boundaries and evidence requirements. It does
not implement or deploy an agent runtime.

## Start here

Want a coding harness? Read [FAST-START.md](FAST-START.md).

Want the complete single-agent contract? Read [STARTER.md](STARTER.md).

Building the full platform? Use [the build guide](.agents/README.md).

The kit supplies no provider SDK, model loop, tool handler, worker or database.
Those belong in a separate implementation repository.

## What you get

- 51 transport-neutral tool contracts;
- launch, adapter, task, event, grant, receipt and resume schemas;
- portable agent, Linux host and workstation profiles;
- synthetic examples and negative contract tests;
- integrity, privacy and JSON Schema checks;
- architecture, tooling and verification guidance.

Synthetic fixtures prove contract consistency only. They do not prove a
runtime, deployment, security boundary or performance result.

## Choose a profile

| Profile | Use |
| --- | --- |
| `agent-starter` | One adapter and one bounded coding workflow. |
| `agent-platform` | Portable platform on an existing conforming host. |
| `host-foundation` | Declarative Linux host without an agent runtime. |
| `greenfield-minimal` | Minimal reference laptop and agent core. |
| `full-workstation` | Complete reference workstation and optional surfaces. |

Profiles select requirements. They do not install software, grant authority or
prove that a service exists.

## Check it

Use the pinned environment described in [DEVELOPMENT.md](DEVELOPMENT.md).

```sh
just check-fast
just check
```

## Read more when needed

- [ARCHITECTURE.md](ARCHITECTURE.md) — decisions and ownership
- [TOOLING.md](TOOLING.md) — tool contracts
- [REBUILD-GUIDE.md](REBUILD-GUIDE.md) — complete implementation order
- [VERIFICATION.md](VERIFICATION.md) — evidence and acceptance
- [research/FINDINGS.md](research/FINDINGS.md) — sources and limits

Keep credentials, personal data, machine paths and environment-specific policy
outside the kit. Reusable source and documentation are English.

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) and
[OPEN_SOURCE.md](OPEN_SOURCE.md) for project policies. The kit is licensed under
the [MIT License](LICENSE); its optional development environment uses public,
pinned Nixpkgs and does not depend on a private agent runtime or skill catalog.

<!-- bootstrap-start -->
The temporary [build assistance](.agents/README.md) is removed when an
implementation completes its retirement checks.
<!-- bootstrap-end -->
