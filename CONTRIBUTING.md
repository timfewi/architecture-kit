# Contributing

Thank you for improving the architecture kit. Changes should keep the portable
core independent of a particular organization, person, machine, provider and
agent host.

## Before changing the kit

Read [AGENTS.md](AGENTS.md) and the instructions nearest to the files you will
change. Open an issue before a large contract or architecture change so its
scope, compatibility impact and evidence can be reviewed early.

Use English for reusable source, contracts, examples and documentation. Use
synthetic identities and data in examples. Never commit credentials, personal
data, private endpoints, absolute home-directory paths, production records or
organization-specific policy.

## Make and verify a change

Keep source changes separate from generated updates. When a contract changes,
add or update an independent semantic check that would fail for the old or
incorrect behavior. Do not weaken an expectation merely to make a check pass.

Use the pinned development environment described in
[DEVELOPMENT.md](DEVELOPMENT.md). The normal verification sequence is:

```sh
just format
just refresh-manifest
just check
```

Review every derived manifest change. If the pinned validator environment is
unavailable, run `just check-fast` and state clearly that full JSON Schema
acceptance was not run. Do not install dependencies or change the host merely
to obtain a green check. Both check recipes run `just privacy-check` to reject
common personal paths, email addresses, credentials and secret-bearing files.

## Submit a change

Keep commits focused and describe the behavior and evidence, including checks
that could not run. A contribution must follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
and may be accepted only after the repository has a release license and the
contributor confirms they have the right to submit the work under that license.
