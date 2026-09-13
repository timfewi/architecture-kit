# Retire this build assistance

Retirement is an explicit reviewed change in an implemented clone. The reusable
template keeps its build assistance.

First complete all selected work items with current real checks. The platform-acceptance
work item must verify that permanent orientation, verification and resume
commands work without loading this directory, and that required evidence has
been transferred to the platform's durable store. Record paths and tests in that
work item's acceptance check before configuring it.

Run bootstrap retirement-check. It reports missing evidence and references from
permanent files; it never deletes anything or authenticates evidence. Expected
temporary integration references (the root instruction block, README entry,
Just recipes and manifest) still require removal. The helper's own tests live
inside this directory so permanent test suites need not import temporary code.

After review: remove temporary entry blocks and Just recipes, remove this exact
directory, retain the portable skills and their validator, and refresh the kit
manifest. Update the permanent instructions to the platform's own commands.
Run permanent checks and a fresh-session resume on the resulting clone.
Do not delete external records needed by unsettled tasks or accepted evidence.
