# ultrapack

A Claude Code plugin for spec-driven, git-centered development. It exists to stop one recurring failure mode: an agent that jumps straight to code, guesses at intent, and leaves you with a change nobody can review or resume. ultrapack forces the work through explicit stages — design, plan, execute, verify, review — and records each one in a single task file, so any fresh agent (or you, next week) can pick up exactly where the last left off. One conversation, one feature, frequently cleared context.

You drive it with one command:

```
/up:make fix the flaky login test
```

## Install (from this fork)

This is a fork. If you already have the upstream `ultrapack` marketplace installed, remove it first so the names don't collide:

```
/plugin marketplace remove ultrapack     # only if the upstream is present
/plugin marketplace add dzmitry-dns/ultrapack-dzm
/plugin install up@ultrapack
/reload-plugins
```

The plugin is named `up`; the marketplace is named `ultrapack` (hence `up@ultrapack`). Verify the install by running `/up:make` — if the command is recognized, you're set.

## Quickstart

```
/up:make fix the flaky login test
```

`/up:make` orchestrates the whole flow. It creates `docs/tasks/<slug>.md`, then walks the task through stages — each one a skill that reads the task file and writes its result back:

1. **Design** — a short interactive dialogue: tradeoffs, the observable Goal, and the constraints the work must respect. You approve before anything else happens.
2. **Plan** — the concrete delta: which files change, which line ranges, which interfaces, broken into ordered phases.
3. **Execute** — the plan is implemented phase by phase, each phase its own commit; a plan-declared interface graph runs independent phases in parallel.
4. **Verify** — the change is attacked, not confirmed: happy-path, negative, invariant, and interface checks, plus an end-to-end smoke. Any demonstrated break loops back to execute.
5. **Review** — an independent reviewer audits the diff against the plan and constraints, from the seat of whoever maintains this in six months.
6. **Validate the Goal** — the task is not done until its Goal is confirmed achieved, not merely verified and reviewed.

## The task file

Everything about a task lives in one markdown file, `docs/tasks/<slug>.md`. It is the single source of truth — the conversation is disposable, the file is not. It evolves through four sections:

- `## Design` — what we want and how it should work, with `### Prior art` citing related past tasks.
- `## Plan` — how we get there from the current code; gains `### Rollback` / `### Rollout` when the change ships to a live system.
- `## Verify` — what was attacked and what held.
- `## Conclusion` — the review outcome; after the task lands it grows a dated post-merge log (`### Follow-up — <date>`, `### Scope change — <date>`) and `### Deferred` scope-parking.

Optional `**Jira:**` and `**Depends on:**` headers link the task outward; every optional slot appears only when it carries content. A multi-task workstream nests as `docs/tasks/<epic>/` — an `overview.md` at Status `reference` linking normal child task files.

A `**Status:**` header tracks where the task is, and any agent resumes from it. The format is `<enum> — <optional annotation>` (`executing — reopened 2026-08-01`):

`design` → `planning` → `executing` → `reviewing` → `validating` → `done` → `shipped`

`shipped` is set once the merge/deploy is confirmed real, with the evidence in the annotation.

### Goal-gated done

Every task carries a `**Goal:**` header — the observable end state that means the work is finished, stated as an outcome, not an activity ("login test passes 100 runs in CI", not "fix the test"). `validating` sits between review and done: verified-and-reviewed code is *not* done until the Goal is confirmed achieved. If confirming it needs a full-scale run or an outcome only visible in your environment, the agent does what's safely in reach and hands you the rest.

### ID system

Entities in the task file get short IDs so later sections reference them without re-quoting. Each is defined once, in full, at first appearance:

- **IV** — Invariants: hard constraints that must hold, concrete enough to check against the code.
- **PC** — Principles: softer guidance, still concrete enough to audit.
- **AS** — Assumptions: unverified premises the design rests on; the Conclusion reports whether each held.
- **UK** — Unknowns: open questions left to plan or execute; the Conclusion reports how each resolved.
- **PH** — Phases: ordered implementation steps, one commit each.
- **RK** — Risks: a one-sentence risk plus its mitigation.
- **CK** — Checks: verify's attack hypotheses.

Design owns IV/PC/AS/UK, Plan owns PH/RK, Verify owns CK.

## Skills

Skills are the stages of the workflow and the disciplines they lean on. `/up:make` invokes the process skills in order; you rarely call them by hand.

Process skills (`u`-prefixed to dodge Claude Code built-ins):

- `up:udesign` — turn an idea into a validated spec: tradeoffs, the Goal, invariants/principles/assumptions/unknowns, and the TDD decision. The one interactive stage.
- `up:uplan` — turn the approved spec into a concrete plan: exact files and line ranges, interface signatures, phases, test strategy, execution order.
- `up:uexecute` — implement the plan phase by phase, inline and serial by default — a plan-declared interface graph dispatches parallel implementers; commit per phase; plan-diff and consistency checks after each.
- `up:uverify` — attack the change to prove it's broken; run each check freshly plus an end-to-end smoke; loop back to execute on any break.
- `up:ureview` — dispatch an independent reviewer, process its findings fairly, and fill the Conclusion.
- `up:udebug` — four-phase root-cause investigation (reproduce → pattern-match → hypothesize → fix); no symptom patches.
- `up:udocument` — discipline for writing docs: lead with why, kill stale content, lists over tables, no aspirational content.

Discipline skills:

- `up:test-driven-development` — red → green → refactor, with a rule for when TDD actually applies.
- `up:git-worktrees` — pick and create an isolated worktree, share the environment from main, run a baseline.
- `up:job-guardian` — babysit any long-running job — a deploy, migration, batch run, or training run — while you're away: launch contract, immediate-crash gate, stability polls, recoverable-vs-not triage, reversible teardown, and a notification when it's over.

## Commands

- `/up:make <description>` — orchestrate the full workflow end to end. Resumes an existing task by its status.
- `/up:try` — quick manual test of the latest change: one positive case, one negative, run both, report.
- `/up:step-back` — circuit breaker: stop, diagnose why attempts keep failing, propose a fundamentally new direction.
- `/up:summary` — draft a handoff summary so another session can continue with zero conversation context.
- `/up:reflect` — extract learnings from the session and route each to its home (CLAUDE.md, memory, or docs).
- `/up:e` — explain something the way one engineer explains to another: lede first, one core mechanism, deeper threads offered but not dumped.

## Agents

Stages delegate focused work to subagents, each with fresh context. Roles:

| Agent | Role |
|-------|------|
| `up:explorer` | Read-only codebase tracing: entry points, call chain, 3–5 essential files with `file:line` refs. |
| `up:implementer` | Per-phase implementer in parallel waves: code, tests, commit, self-review. |
| `up:reviewer` | Independent review against the Plan, Invariants, and Assumptions; confidence-filtered, severity-tiered. |
| `up:researcher` | General-purpose investigation across the web, library docs, and the current codebase. |
| `up:summarizer` | Drafts the handoff prose for `/up:summary`; gathers repo state, never writes to disk. |

Models are pinned in each agent's frontmatter — review-grade judgment runs on the top pinned tier, and the implementer inherits your session model, downshifted per-dispatch to a cheaper tier for trivial phases.

## Fork note

This is a fork of [btseytlin/ultrapack](https://github.com/btseytlin/ultrapack) — credit to the upstream author, Boris Tseitlin, for the original design. Fork policy (what gets PR'd upstream vs. stays in the fork) and versioning conventions live in [CLAUDE.md](CLAUDE.md).

## License

WTFPL — see [license.txt](license.txt).
