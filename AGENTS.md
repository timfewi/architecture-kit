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

<!-- bootstrap-start -->
When asked to implement a platform from this clone, start with
[the temporary build guide](.agents/README.md) and
[platform-build](.agents/skills/platform-build/SKILL.md).
When asked only to extend the kit, keep the work in the kit.
This block and the temporary directory are removed together at retirement.
<!-- bootstrap-end -->
