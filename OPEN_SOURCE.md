# Open-source release policy

The kit is licensed under the [MIT License](LICENSE). This policy documents
release checks; it does not itself change repository visibility or create a
release.

## Release gates

Complete every gate against the exact revision proposed for publication:

- confirm ownership, third-party obligations and the intended patent and
  contribution terms for the MIT license recorded in the changelog;
- review the full Git history, branches, tags and large-file storage for secrets,
  personal data, private endpoints, internal names and non-redistributable files;
- remove sensitive history with a reviewed history-rewrite procedure when
  deletion from the current tree is insufficient;
- verify that examples contain only synthetic data and that research sources
  preserve their licenses and attribution requirements;
- run `just privacy-check` and manually review contextual details that pattern
  matching cannot classify;
- run `just check` with the pinned validator dependencies and
  `nix flake check --no-update-lock-file` on each supported system;
- review the rendered README, contribution, conduct and security policies;
- configure private vulnerability reporting, issue labels, branch protection,
  required checks and least-privilege automation on the chosen repository host;
- create a fresh release candidate from the reviewed revision and inspect its
  archive before changing visibility or publishing a release.

Run `just release-audit` to check the local, machine-verifiable subset. It does
not inspect repository-host settings, decide whether identity metadata may be
published, choose a license, modify Git state or perform publication. A passing
result supplements the manual gates above; it does not replace them.

## Local checkout boundary

A local checkout may retain Git metadata such as author identities and remote
URLs. Those values are outside the reusable kit artifacts, but they are part of
repository history and configuration and require explicit review before
publication. No runtime, host deployment, or private catalog is included in
the kit.
