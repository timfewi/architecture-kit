# Benchmark and admission method

Run `python3 -B scripts/benchmark_retrieval.py` in the approved worker. The
script creates a private temporary synthetic corpus, checks exact expected
outputs for positive, negative and ambiguous literal queries, then collects
twenty measured samples per candidate/case after one warmup. It compares
ripgrep and grep over identical explicit files, including hidden and spaced
paths. Versions, executable digests, exact argv, corpus identity, raw samples,
output digests and byte counts are recorded. It emits JSON and does not write
the repository. An accepted receipt can be stored under `research/`.

The ambiguity case deliberately has the same word in definitions, comments and
strings. It tests lexical equality, not symbol-reference quality. No result
from this suite admits a semantic retrieval engine.

The receipt's metadata byte counts compare the actual catalog, its compact
discovery summaries and its initial subset. They exclude expanded schemas and
model conversations. Provider token usage is null because no model was called.
Do not convert bytes into claimed token savings.

## Admission beyond the smoke experiment

For each proposed tool freeze the task semantics, corpus, expected results,
candidate versions and package identities, argv, environment, authority,
resource ceilings, output contract and correctness oracle. Verify:

1. Positive, negative, ambiguous, malformed-input and inaccessible-file cases.
2. Encoding, ignore rules, links, partial scans and stable ordering.
3. Cancellation, timeouts, pipe closure, slow consumers and complete cleanup.
4. Cold start, warmed execution, index setup and incremental updates separately.
5. Whole task success, repair work, latency, peak memory, bytes, actual tokens
   when available, tool calls and external cost.

These are runtime admission requirements; the synthetic script covers only its
three literal-search cases. It does not simulate cgroup or process isolation.

Compare candidates only after the same quality and authority gates pass. Keep
raw measurements; report medians and dispersion for exploratory samples. A
small run does not establish p95/p99 or a universal ordering. Do not clear host
caches or change host scheduling to manufacture a cold measurement.

An index is justified when measured repeated-query savings exceed its build,
update, invalidation and memory costs. If build cost is B, baseline query cost
is Qb and indexed query cost is Qi, the simple break-even count is
B / (Qb - Qi), only when Qb > Qi. Include changed files and expected reuse before
using this approximation.

For context optimization, compare equal verified tasks with the same model and
harness: full catalog versus progressive discovery; full output versus
oracle-preserving projection; one agent versus bounded independent work. Include
failed attempts, rereads, compaction, coordination and verification. A shorter
answer that omits required evidence fails the quality gate.

Add optional fd/find, jq streaming/materialized, SQLite/DuckDB/Miller,
SCIP/LSP and native/Wasm experiments only when those exact candidates and
workloads are provisioned. Record unavailable metrics explicitly; zero is a
measurement, not a missing-value marker.
