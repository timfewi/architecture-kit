# Routing pilot

On 2026-09-13 an independent read-only agent reviewed the four full skill bodies
and five requests without reading the expected routing fixture. Its selections
matched routing-pilot.json: orientation; no skill; orientation then freshness;
verified-change; efficient-tool-use (since split, below).

It found no named-host dependency. It noted that orientation should be omitted
when context is already sufficient, and that verification/freshness share real
boundary checks but have distinct triggers. These are editorial observations,
not model-performance measurements or tests across all harnesses.

Re-run a focused independent pilot when activation descriptions or boundaries
change. The static validator checks the fixture's references, not model behavior.

## Addendum 2026-10-06: split of efficient-tool-use

efficient-tool-use was replaced by tool-call-discipline and context-budget, and
the pilot grew from five to eleven cases. The fifth case now expects
context-budget. The six added cases cover paging, an uncertain mutation outcome,
a repeated failure, a resume note, a request needing both skills and a trivial
single read that needs neither. The 2026-09-13 review above predates the split
and does not cover the new skills.

The new expectations are author-written. No independent agent has routed them,
and no model-token or task-quality comparison was made. Before treating routing
or savings as established, re-run an independent read-only pilot without the
fixture and a paired-task comparison (see BENCHMARKS.md).
