# Engine choice

Select by the question and the corpus. Default to the simplest engine that
answers it with an oracle you can check; escalate only when it answers something
the default cannot or repeated use amortizes the setup. These are functional
defaults, not an installed-tool list: use what the host provides and permits.

| Question | Default | Escalate when |
| --- | --- | --- |
| Read one known file | Bounded read of the needed range | Never needs a child process. |
| Find text in current source | ripgrep; git grep for a tracked revision | Ignore, hidden, binary and symlink rules matter; ranked retrieval never replaces an all-matches search. |
| Find paths | Native listing or `rg --files` | `fd` for repeated queries; `find` for metadata predicates. |
| Match syntax | ast-grep or tree-sitter | One adapter per language, with malformed-source cases. |
| Callers, definitions, impact | Existing language server or source index | Coverage includes the language, build and current edits; an ambiguous name is unresolved, not absent. |
| Find documentation | Full-text index | Ranking is discovery only; read the selected source. |
| Select JSON fields | `jq` or the language's parser | Stream when memory is the limit. |
| Aggregate tables | SQLite | A columnar or streaming engine only after an equal-result trial. |
| Run repository code | Declared project command in an authorized, isolated environment | Never with ambient credentials or network unless granted. |
| Review changes | Status plus a focused diff | Renderers are optional human views. |
| Fetch public documents | Bounded fetch through the host's research route | A browser only for rendered or interactive state. |

State the corpus covered and what was ignored or unsupported before trusting a
result. A missing executable is a blocker to report or work around with a
permitted equivalent, not a reason to install software.
