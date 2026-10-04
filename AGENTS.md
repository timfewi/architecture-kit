# Working in this kit

Keep reusable source and documentation in English. Preserve existing changes and
read the instructions governing each area before editing it. Kit examples and
synthetic checks do not prove that a platform or host service exists.

Inspect the declared environment and commands before execution. Use an authorized
isolated environment for repository code. Do not install dependencies, change host
configuration or expand permissions merely to run a check. Git publication and
deployment remain separate actions.

For kit changes, run the applicable recipes in justfile. Run full acceptance only
with the pinned validator dependencies; report unavailable coverage. Review
intentional derived catalog/manifest updates and do not refresh behavioral
expectations merely to restore passing checks.

When tool work yields a reusable lesson, follow [LEARNING.md](LEARNING.md): check
the canonical source map, review relevant source and evidence, update the owning
guide and learning register together, then refresh derived hashes deliberately.
Use [DEVTOOL-START.md](DEVTOOL-START.md) for standalone tools; do not require a
platform implementation for a CLI. External source checks are explicit and
optional for a standalone clone; internal register integrity is part of the fast
gate. Never treat matching source hashes as runtime or semantic acceptance.

<!-- bootstrap-start -->
When asked to implement a platform from this clone, start with
[the temporary build guide](.agents/README.md) and
[platform-build](.agents/skills/platform-build/SKILL.md).
When asked only to extend the kit, keep the work in the kit.
This block and the temporary directory are removed together at retirement.
<!-- bootstrap-end -->
