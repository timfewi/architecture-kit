# Development environment

The optional Flake supplies a hook-free development shell for x86_64-linux and
aarch64-linux. It does not make Nix or Example host part of the architecture's
portable runtime contract.

## Pinned inputs

The input is the exact Nixpkgs revision
`21a67dc470149f337cecafbe965d8d252a390518`, verified on 2026-09-13 against the
[NixOS 26.05 stable channel](https://channels.nixos.org/nixos-26.05/git-revision).
[NixOS's download page](https://nixos.org/download/) identified 26.05 as stable.
The revision is written into flake.nix, not a moving branch or latest alias.

The selected package set supplies Python 3.14.7, jsonschema 4.26.0, PyYAML 6.0.3,
Just 1.51.0, Direnv 2.37.1, Ruff 0.15.14 and Nixfmt 1.5.0. These are the stable
channel's package versions, not a claim that every component is upstream's
newest release. Additional tools are Bash, coreutils, Git, GNU grep, ripgrep
and ShellCheck, all selected from the same revision.

The Python environment uses `python314.withPackages`, so the validator and
its transitive dependencies are importable by the selected interpreter.
`requirements.txt` remains the validation requirement; no pip install or
network access occurs during tests. The Nix environment smoke check compares
the installed package versions against that file.

Exact-revision sources:

- [Python versions](https://github.com/NixOS/nixpkgs/blob/21a67dc470149f337cecafbe965d8d252a390518/pkgs/development/interpreters/python/default.nix)
- [jsonschema package and dependencies](https://github.com/NixOS/nixpkgs/blob/21a67dc470149f337cecafbe965d8d252a390518/pkgs/development/python-modules/jsonschema/default.nix)
- [PyYAML package](https://github.com/NixOS/nixpkgs/blob/21a67dc470149f337cecafbe965d8d252a390518/pkgs/development/python-modules/pyyaml/default.nix)
- [Python environment API](https://github.com/NixOS/nixpkgs/blob/21a67dc470149f337cecafbe965d8d252a390518/doc/languages-frameworks/python.section.md)
- [Direnv 2.37.1 standard library](https://github.com/direnv/direnv/blob/v2.37.1/man/direnv-stdlib.1.md)
- [Just 1.51.0 manual](https://github.com/casey/just/blob/1.51.0/README.md)

## First setup on your host

Nix with `nix-command` and `flakes` enabled, plus Direnv and its shell hook,
must already be available on the host. Including Direnv in the development
shell cannot bootstrap the host shell integration that loads that shell.
Use your existing declarative host configuration for installation.

Review flake.nix and .envrc first. Git-backed flakes omit untracked inputs, so
stage the explicitly reviewed entry files before generating the lock:

```sh
git add flake.nix .envrc justfile requirements.txt
nix flake lock
```

The initial lock generation and realization may download the pinned source
and packages. Run them only in your authorized provisioning environment.
Let Nix generate flake.lock and review it; do not invent a narHash or hand-edit
generated lock metadata. A later input update requires changing the reviewed
revision and regenerating the lock.

If the host hook is not yet configured, the shell-specific hook is
`eval "$(direnv hook bash)"` for Bash or `eval "$(direnv hook zsh)"` for Zsh.
Install the matching hook through your shell configuration, not both.

After reviewing the entry point, explicitly grant trust yourself:

```sh
direnv allow
```

At the next prompt the shell loads the default Flake environment. .envrc only
watches the declared inputs and calls `use flake .#default`; it does not fetch
or source an additional shell script. The agent does not grant this trust.
Generated .direnv state is excluded from Git and the kit manifest.

Once the environment is loaded:

```sh
just refresh-manifest
just check
nix flake check --no-update-lock-file
git add flake.lock manifest.json
```

Refreshing is intentional here because the generated lock adds a package
artifact. Normal `just check` never rewrites the manifest to hide drift.
Review and commit the complete intended changes according to your Git policy.

## Commands and scope

| Command | Scope |
| --- | --- |
| `just` | List recipes. |
| `just check` | Lint, format checks, all regression tests, full schema and manifest validation. |
| `just check-fast` | Lint, formatting, semantic tests and manifest checks; excludes full JSON Schema validation. |
| `just format` | Format Python, flake.nix and justfile; does not refresh the manifest. |
| `just refresh-manifest` | Refresh derived hashes after reviewing intentional changes. |
| `just benchmark` | Print a new synthetic measurement without replacing accepted research evidence. |
| `just baseline` | Optional host-provided project-check security scan; not silently included or installed by this generic Flake. |
| `nix flake check --no-update-lock-file` | Build the validator import/version smoke check for the current system; not the full kit acceptance suite. |
| `nix build --no-link .#validator` | Realize only the Python validator environment without creating a result symlink. |

The shell has no shellHook and never runs checks on entry. Recipes do not load
.env files. The formatter and checker commands operate on the current checkout,
not on a copied or implicitly rewritten source snapshot.

## Example host worker integration

This Flake defines an environment; it does not register or activate an agent
worker profile. Interactive Direnv trust does not grant broker execution rights.
The installed Example host local preparation path reads selected manifests and
package attributes; it does not evaluate this devShell or install requirements.txt.

A reviewed worker profile must explicitly include this Python environment and
the required command set. A project-exported profile can wrap the hook-free
default shell with Example host's toolchain helper in the operator's pinned
provisioning configuration. Bind every toolchain input, including flake.nix,
flake.lock and requirements.txt. Registration and activation remain host-owner
actions; a repository registered after launch requires a new agent session.

## Verification status

The source was parsed/formatted and the Just recipes were exercised using the
existing isolated worker tools. Lock generation could not fetch the uncached
Nixpkgs input in that no-network worker. Consequently flake.lock is not supplied
by this change; its exact revision is already pinned in flake.nix.

The pinned shell, environment smoke derivation and full schema suite still need
to run after authorized provisioning. Checks with the worker's base versions
do not prove the newly declared closure, nor either target platform's build.
