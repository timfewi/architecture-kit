# Portable operating skills

These independently authored operating skills are readable on any host. They
do not depend on the temporary implementation workflow or publish private skill
contents. Standard SKILL.md metadata is the source; catalog.json is a generated,
digest-bound metadata projection.

Read only names/descriptions first, select the smallest relevant skill, then load
its body. A host can offer this through search/load tools or ordinary file reads.
The catalog's capability names are descriptive routing hints, never grants:

| Capability | Permitted local equivalent | Optional dedicated capability |
| --- | --- | --- |
| source.read | Read an exact file/range | Bounded source reader |
| source.search | Filename/text search | Source index with freshness diagnostics |
| vcs.inspect | Status and focused diff | Typed Git inspection |
| execution.run | Declared project command | Isolated executor or verification service |

Validate actual availability and task authority before choosing either column.
No model, host vendor or particular tool transport is required.

## Public and private packaging

Use these portable sources as the common layer for harness-tools/public after
normal publication/license review. Keep private environment details in separately
named skills or references in harness-tools/private. A private extension records
the common skill name and digest; it must be reviewed when that digest changes.
Reject conflicting names instead of silently shadowing the public skill.
Do not duplicate whole common skill bodies or infer authorization from an overlay.

A host adapter resolves capability hints and projects a reviewed catalog into its
supported discovery mechanism. Generate compatibility views from the same source;
the kit forbids source symlinks. Private paths, service identities and credentials
must not enter the public catalog. This repository does not modify external skill
worktrees or implement a private skill loader.

## Validate

```sh
python3 -B scripts/check_skills.py
python3 -B scripts/check_skills.py --refresh
```

Refresh only after intentional skill edits; inspect the catalog and manifest
diffs. Checks reject drift, malformed metadata and escaping references. Format
checks do not establish routing quality. The routing pilot in routing-pilot.json
records realistic positive, negative and ambiguous requests for independent review.

The format follows the [Agent Skills specification](https://agentskills.io/specification),
consulted on 2026-09-13. Optional allowed-tools metadata is not used as authority.
