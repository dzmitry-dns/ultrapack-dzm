# Global Principles

GPC1–GPC8. Apply to every task unless clearly irrelevant. Deviations name the GPC and the reason in one line.

- **GPC1 — Explicit interfaces, no defaults, no hidden config.** Caller passes every argument. Each constant / config / magic value is defined in exactly one place and threaded explicitly to its use site. No reading config behind the caller's back.
- **GPC2 — One concern per unit.** One responsibility per function, class, file. Functions >~10 lines are a smell — split unless justified. Error handling is its own concern. Short files/classes follow from short functions; goal is fewer concerns per unit, not fewer symbols. Code reads top-to-bottom like prose.
- **GPC3 — Query/command separation.** Separate read-only queries from state-changing commands. Commands may return their result.
- **GPC4 — Single source of truth + boundaries.** If a value is used across train + eval + inference, it lives in the model config — saved on train, loaded on eval, never redefined in a second code path. Layering is explicit: declare what can import what (e.g. `Dataset` must not import `training/`). Cross-boundary leaks are a design bug, not a style nit.
- **GPC5 — Idempotent, atomic, observable writes.** Anything that writes to disk, DB, or a checkpoint must be re-runnable without corruption: write-to-temp-then-rename, transactional or retriable. Log inputs/outputs at seams (entry/exit of each unit), not inside hot loops — seams are what you grep when things break.
- **GPC6 — Fail fast, fewest moving parts.** Crash loud on unexpected state — no silent fallbacks, no defaulted-to-zero metrics. Parkinson's law: whatever can break will. Prefer the plan with fewer components, fewer code paths, fewer places a future bug can hide. Prefer reversible changes over clever ones.
- **GPC7 — Plan for debugging.** Assume every new piece of functionality will need to be debugged. Design it so future-you can diagnose without a rewrite: structured logs at seams, meaningful IDs threaded through (request id, run id, sample id), state-transition logging for long-running processes, deterministic-where-possible execution, and a way to reproduce a single failing case in isolation. "We'll add logging when it breaks" means you'll add logging in production at 2am.
- **GPC8 — DRY, reuse first.** Before writing new code, search for existing helpers, utilities, or patterns that already solve it — extend or call them rather than parallel-implementing. Duplicated logic across two call sites is a smell; three is a bug. Reuse wins over re-creation; the exception is when reuse would force a premature abstraction that mixes concerns (then prefer explicit over DRY per GPC2).

## Manual-only skills

A skill with `disable-model-invocation: true` (since 0.3.34: e, try, reflect, step-back, test-driven-development, git-worktrees, job-guardian, udocument) is invisible to the model and cannot be invoked through the Skill tool. A stage skill that needs its content reads the file at `${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md`; a stage that wants the user to run it says "type `/up:<name>`". Never write "invoke `up:<name>`" for one of these. This is the single home of the rule; callers only point here.

## Commits

Every commit made by any stage, or by `/up:make` at a Status transition, is English, `<type>: <concise>`, and carries no `Co-authored-by` or any other trailer.

Before a commit that includes a task file, check the lines it adds to that file for Cyrillic (the byte range needs a UTF-8 locale; under `LC_ALL=C` it also hits accents and dashes):

```bash
git diff --cached -U0 -- <task file> | grep -n $'^+.*[\xd0\x80-\xd3\xbf]'
```

Translate every hit to English, stage again, then commit. Lines the commit does not add stay as they are. The one exception: a backticked literal that a code or pack file contains verbatim.

This is the single home of the rule; callers only point here.

## Dispatch narration

Before dispatching a subagent (`Agent` tool call) and after it returns, state one line: what's being dispatched / what it returned. The user sees no tool calls, only text — an unannounced dispatch reads as silence. This is the single home of the rule; callers only point here.

## Closing line

Whoever ends the workflow turn prints one line, once, in the owner's chat language:

`Done: <what>. Left: <what, or nothing>. Close: <task yes/no; Jira yes/no, or no ticket> (<why not, when no>).`

When a review ran in the same turn, append `Another review: <no | yes> (<why>).` The line is never a recap of the message above it. This is the single home of the rule; callers only point here.

## Handoff at a wait

When the flow waits for the owner and a task file exists, the message ends, after any Closing line, with:

1. The resume prompt of `/up:summary` step 4.
2. One line: `Session: can close`, or `Session: wait for <job still running in the background>`. A job counts while this session started it and has not seen it finish.

The waits: the design approval request, the plan approval request, `/up:make` step 12, and any other question that stops the flow. At the two approval requests and at step 12, run `/up:summary` steps 1-3 first when decisions were taken since the latest Handoff block, so the prompt points at a current file. At any other question print only the prompt and the Session line, with no append and no commit; when decisions were taken in chat since the latest Handoff block, the line reads `Session: run /up:summary before closing`, never `can close`. This adds no pause: it rides only waits that already exist. This is the single home of the rule; callers only point here.

## Questions to the owner

Before each question to the owner (plain text or AskUserQuestion), write 2-4 plain sentences in the owner's chat language: what the situation is, why the answer is needed now, what each option changes. Option labels name the consequence, never an internal ID (`IV2`, `PH3`, `UK1`). A question that stops the flow ends per Handoff at a wait. Task-file and pack text stays English. This is the single home of the rule; callers only point here.

## Costly runs

A costly run is one the agent starts by command that costs money (paid API or model calls, cloud jobs) or takes over 10 minutes. CI that a push triggers is not one. The plan's `### Test strategy` names each costly run and how many times it runs. Every run beyond that count, or not in the plan, needs a yes to a question that names the run, its cost, and why one more run should change the result. A "fix and rerun" loop is no exception: each rerun asks. This is the single home of the rule; callers only point here.

## Incidental code smells

While exploring code for a task you'll pass smells unrelated to the change — a 200-line function, a duplicated helper, a leaked layer boundary. Two outcomes, no third:

- In task scope, or a genuinely easy and low-risk win → fix it (Boy-Scout rule, GPC2/GPC8). The fix lands in the diff; nothing to record.
- Out of scope and non-trivial — a wide rename, a risky refactor, a new test surface → don't balloon the task. Record it, one line, in the task file's `## Code smells` section:

  `- <file:line>: <smell, one sentence> (<GPC it offends, if one fits>)`

A pointer plus a sentence; the next reader opens the line. Recorded smells are `Future work` candidates decided at review — recording one does not authorize fixing it now.

## How to use

- `up:udesign` — surface GPC tradeoffs (layering, SSOT, fail-fast, debuggability) as Design decisions; reference by ID. Task-specific PCs only when deviating from a GPC or adding a rule the GPCs don't cover.
- `up:uplan` — every phase consistent with GPCs; deviating bullets cite the GPC and why.
- Commits — `/up:make`, `up:uexecute`, `up:ureview`, `/up:summary` point here for every commit they make.
- Costly runs — `up:uplan` (Test strategy), `up:uexecute` (When to stop and ask), `up:uverify` (Phase 5), and `/up:make` (Rules) point here.
- Closing line — `/up:make` step 12, a manual `up:ureview`, and `/up:summary` print it.
- Handoff at a wait — `up:udesign` and `up:uplan` (step 12), `/up:make` (step 12, Context checkpoint), and `/up:summary` (step 4) point here.
- Questions to the owner — `up:udesign` (step 3, Rules) and `up:uplan` (step 12) follow it for every question they ask.
- `up:udebug` — anti-whack-a-mole: name the pattern behind a bug and grep for the same shape before closing (not a GPC, same family).
- Incidental code smells — `up:udesign` / `up:uplan` fold an in-scope or easy fix into the design/plan, else record to `## Code smells`; `up:uexecute` fixes in-scope/easy ones, records the rest; `up:explorer` / `up:implementer` report passed smells in their output for the dispatcher to act on.
