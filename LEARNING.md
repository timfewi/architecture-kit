# Keep the kit current

This is an explicit maintenance workflow, not a background monitor or memory
service. Local changes become lessons only after source review. The kit remains
usable without the original workspace, private tools or host integration.

<a id="review"></a>
## Check before reusing a lesson

[research/harness-tools.json](research/harness-tools.json) records the reviewed
directory roles, selected source-file hashes, observations and adoption locations.
[research/HARNESS-REVIEW.md](research/HARNESS-REVIEW.md) explains coverage and limits.
Check the internal register in any clone:

```sh
just check-learning
```

With an explicitly selected local collection containing `public/` and `private/`,
check whether its directory inventory and selected evidence still match:

```sh
just check-tool-sources /path/to/tool-collection
```

This never runs project code, loads environments, reads credentials, fetches
repositories or writes source. The local root is not stored. Exit 0 means the
selected bytes match; exit 1 means drift; exit 2 means invalid or unavailable
evidence. Internal validation alone reports `external_sources_checked: false`.
Changes outside the selected files, nested release candidates, Git history and
runtime behavior are outside the freshness claim. Reopen relevant implementation
and tests for each lesson before claiming it still holds.

If the collection README is a symlink to a separately owned workspace guide,
the checker refuses to follow it. Supply the reviewed regular Markdown file
explicitly as the second recipe argument, or with `--source-map FILE` on the
Python command. That file is checked against the logical `README.md` receipt;
its absolute location is neither printed nor stored. Other evidence symlinks
remain unavailable. The checker assumes stable, operator-owned directories;
these read guards are not a sandbox against concurrent hostile filesystem changes.

## Review a changed tool or a new lesson

1. Read the collection's current source map and repository instructions. Classify
   canonical sources, mirrors, archives, preparation copies and empty directories.
   New immediate directories must be reviewed; do not silently omit them.
2. Inspect relevant source and meaningful tests. Record the concrete observation,
   scope and counterexample. Separate source review from executed checks, package
   builds, deployment and live use. Retain failed trials and unavailable evidence.
3. Decide whether to adopt, revise, defer or reject the lesson. Change its actual
   owning guide or contract; migrate consumers when an interface changes. Prefer
   removing redundant guidance to accumulating aliases, umbrella skills or
   another routing layer. Existing architecture decisions still govern authority.
4. Update the observation, lesson links, selected evidence files and review date
   together. To inspect candidate hashes without accepting them:

   ```sh
   python3 -B scripts/review_tools.py --sources-root /path/to/tool-collection --capture
   ```

   The output is a proposal. Copy only reviewed receipts into the register after
   updating the prose; never refresh hashes merely to silence drift. A missing,
   unsafe or unreviewed source cannot be accepted by this command.
5. Update CHANGELOG.md and the existing checkpoint. Run formatting, the learning
   regressions, the kit fast gate and the external source check where available.
   Refresh the manifest only for intentional changes. Do not replace behavioral
   expectations with generated output.

<a id="evidence"></a>
## Measure a hypothesis before promoting it

A useful checkpoint states: observed failure, source/evidence, proposed change,
comparison task, result, limits and next action. Use the same task and settings
for old/new behavior, inspect actual outputs and traces, and include errors and
cancellation in costs. Run model-backed experiments only within their separately
authorized workload. A successful start/answer smoke test, matching bytes, a
selected skill or a clean scanner cannot establish task quality or safety.

Only generalize a lesson as far as its evidence supports. Keep personal state,
raw traces, private endpoints, identity and host policy outside this public kit.
Summarize private implementations in original neutral prose; do not copy their
source or skill bodies. Candidate metadata and privacy checks grant no source
publication, history rewrite, dependency update or host activation authority.

## Development checkpoint — 2026-10-04

Reviewed the active collection's canonical tools and its nondevelopment roles.
Added a dedicated Devtool start path and a source-bound learning register, with
an explicit offline drift check. Existing platform contracts and pins remain the
reference; source observations are not newly executed runtime acceptance.
See CHANGELOG.md for the maintained change record. Future updates begin with
the drift report and the concrete task observation, not an automatic hash refresh.

Verification: the declared `project-check fast` passed in the pinned environment
with 70 regressions, including ten learning checks, plus lint, formatting, privacy,
integrity and semantics. Focused pinned JSON Schema validation accepted the new
register and rejected four malformed cases. The explicit local source check
matched all 26 directory roles and 78 selected files. The broader acceptance
suite and other repositories' runtime/build/deployment gates were not run.
