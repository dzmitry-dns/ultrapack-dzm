# Parallel phase dispatch — interfaces, waves, wiring

The optional parallel path for `up:uexecute`, and the declaration format `up:uplan` uses to enable it. Applies only when the task's `## Plan` declares `### Interfaces` and `### Interface graph`; without them, execute runs its serial per-phase loop and this file never applies.

## Declaring (plan side)

### Format

```markdown
### Interfaces
- IF1 — `<signature>` — <contract sentence>
- IF2 [blocks] — `<signature>` — <contract sentence, including why it blocks>

### Interface graph
- PH1              -> IF1, IF2   @ src/foo/parser.py
- PH2  IF1         -> IF3        @ src/bar/consumer.py
- PH3  IF2, IF3 ->               @ tests/test_wiring.py
```

### Semantics

- An interface is a cross-phase contract: a function/method signature, a shared SKILL.md section anchor, or any API shape that one phase produces and another phase consumes.
- The consume arrow (`IF<N> ->`) means runtime coupling — one phase's output is the other phase's input. Doc-only phases that merely reference a prior phase's plan text are sources, not consumers; leave the consume side empty.
- `@ <paths>` marks the filesystem boundary for each phase. Paths declared by phases in the same wave must be disjoint; the executor uses them to detect boundary violations after each commit.
- Waves are derived from the graph by topo-sort over `[blocks]` edges only — non-blocking IF edges (the default) do not create wave boundaries, since the IF declaration is sufficient context for the consumer. Phases linked only by non-blocking IFs land in the same wave and run in parallel. Do not hand-declare waves; declare the graph and the blocking flags, and let the executor derive them.
- Omit both subsections for single-phase plans — and for any plan the planner intends to run serially.

### Blocking interfaces

By default, an IF is non-blocking: its declared signature is the contract, and a consumer can be implemented in parallel with the producer (the wiring check reconciles any drift after the wave). Mark an IF `[blocks]` when:

- The consumer needs the producer's actual output, not just the signature — e.g. a generated config file, an applied DB migration, a fixture that must exist on disk, a doc anchor that must resolve at lint time.
- The producer is large, risky, or critical enough that the planner does not want dependent work running concurrently — better to land it, verify it, then build on top. Planner/dispatcher discretion.

Use `[blocks]` sparingly — every block reduces parallelism. Non-blocking is correct for ordinary code interfaces (function signatures, class shapes, SKILL.md anchors) where the declaration carries the contract.

### Planner self-review for the graph

Every phase declares `@ <paths>`; paths declared by phases in the same wave are disjoint; every IF consumed by any phase is defined in `### Interfaces`; every IF defined is produced by exactly one phase; every `[blocks]` annotation has a stated reason in the IF's contract sentence.

## Executing (dispatch side)

### Reading the graph

Parse each line of the form `PH<N>  <consumes-CSV> -> <produces-CSV>   @ <paths-CSV>`. Empty left of `->` = source (no consumed IFs). Empty right = sink. Collect Owns (`@`), Consumes (left), Produces (right) per phase. For each IF in Consumes, look up its kind in `### Interfaces`: `[blocks]` = blocking edge (creates wave boundary), bare = non-blocking (ignored by topo-sort).

### Wave derivation

- Wave 1: phases with no blocking Consumes (their consumed IFs are all non-blocking, or they consume nothing).
- Wave N+1: phases whose every blocking Consumes IF is produced by phases in waves 1..N.
- Repeat until all phases are assigned.

If a wave reduces to one phase, skip dispatch and edit inline via the serial loop in SKILL.md.

### Disjointness check

Before dispatching a wave, verify the `@` sets of all phases in that wave are pairwise disjoint. On overlap: halt, tell the user which paths conflict between which phases, and do not dispatch.

### Choosing the implementer agent

Two implementer agents are available:

- `up:implementer` — default. Use for any phase requiring judgment: multi-file changes, new logic, TDD, introducing or changing an interface, anything where reading multiple files informs the implementation.
- `up:implementer-sonnet` — trivial phases only. Use when the phase is unambiguously mechanical and well-localized: single-file typo or copy fix, mechanical rename, import/lint cleanup, version/changelog bump, doc edit with no behavioral claims.

Default to `up:implementer`. Pick `up:implementer-sonnet` only when every criterion is met. If unsure, pick `up:implementer`.

If `up:implementer-sonnet` returns `NEEDS_CONTEXT` with `escalate: up:implementer`, re-dispatch the same phase to `up:implementer` — its scope check correctly bounced a non-trivial phase.

### Dispatch prompt

Pass:
- Full verbatim text of the phase from `## Plan`
- `### Invariants` (IV), `### Principles` (PC), `### Assumptions` (AS) from `## Design`
- TDD decision (from Design — `yes` or `no (reason)`)
- Absolute working directory (subagents do not inherit `cwd` reliably across harnesses)
- Expected git branch (from the task file `**Branch:**` header)
- `Commit mode: defer` — the dispatcher commits; implementers stage and report
- `Owns`, `Implements`, `Consumes` — sourced from the graph line

Do not pass: session history or prior-phase chatter; the full task file; later phases; rationale behind design decisions — the plan is the contract.

```
Phase: <verbatim PHN text from ## Plan>
Invariants: <IV1, IV2, ...>
Principles: <PC1, PC2, ...>
Assumptions: <AS1, AS2, ...>
TDD: <yes | no (reason)>
Working directory: <absolute path>
Branch: <expected branch from task file header>
Commit mode: defer
Owns: <comma-separated paths from the graph's @>
Implements: <IF<n>, ...>                                    (if this phase produces any)
Consumes: <IF<n>, ...>                                      (if this phase consumes any)
```

### Dispatching the wave

All implementer dispatches for the wave MUST occur in a single assistant response containing multiple concurrent `Agent` tool calls, each with `run_in_background: true`, so they fire concurrently and you receive notifications as each completes. Dispatching one implementer, waiting, then dispatching the next is sequential, not parallel — if a wave was announced, all its phases go out together.

A consumer is dispatched in parallel with its producer; the IF declaration in `### Interfaces` is the consumer's ground truth for the signatures it depends on.

### Serialized commit protocol

After all Agent calls return, process successful implementers in ascending PH order. For each phase whose implementer returned `DONE` or `DONE_WITH_CONCERNS`:

1. `git add <paths staged by the implementer>`.
2. `git commit -m "<proposed message from implementer report>"`.
3. **Boundary check:** run `git show <sha> --name-only`. Every changed path must be a member of the phase's declared `@` set. On trespass: halt the wave, tell the user which path was trespassed by which phase, then either re-dispatch with tightened scope or escalate to `up:uplan`.
4. Plan-diff check: every plan bullet reflected in the diff? every diff change covered?
5. Consistency pass: grep for sibling patterns; apply missing changes if any.

Implementer status handling: `DONE` → protocol above; `DONE_WITH_CONCERNS` → read the concerns, resolve or record them, then protocol; `NEEDS_CONTEXT` → supply missing context, re-dispatch; `BLOCKED` → diagnose — if the plan is wrong, invoke `up:uplan`; if context-only, re-dispatch. Do not retry identically.

### Failure handling

- On `BLOCKED` or `NEEDS_CONTEXT` from one phase: do not abort sibling phases mid-work. Wait for all siblings to return, commit their successful results per the protocol above, then diagnose the failure — re-dispatch with corrected context, invoke `up:uplan` if the plan is wrong, or stop and ask the user.
- A failure in one phase never rolls back a sibling's already-committed work.

### Wiring check

Runs once, after the final wave's phases commit. For non-blocking IFs, consumers were dispatched against the IF declaration rather than the producer's actual output — this is the reconciliation step, catching every place a producer drifted from the declared signature.

For each `IF<n>` declared in the Plan's `### Interfaces`:

1. Identify the IF's named symbol or anchor (the identifier named in the IF's signature bullet).
2. Grep the repo for callers or references of that symbol.
3. For code IFs: verify each call site matches the declared signature.
4. For doc IFs (where the "signature" is a section anchor or declared public contract of a SKILL.md): grep for the declared anchor or reference and verify it resolves.
5. On mismatch: log under `## Conclusion → ### Deviations from plan` with `IF<n>: <mismatch description>`. Decide whether to re-dispatch the offending phase (implementation error), invoke `up:uplan` (plan declared the wrong signature), or continue with a recorded deviation.
