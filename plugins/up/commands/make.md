---
description: Orchestrate the full ultrapack workflow — slug, task file, design, plan, execute, verify, review. Size-aware, resume-ready.
---

# /up:make

Drives a task through the full ultrapack workflow: one task file at `docs/tasks/<slug>.md`, evolving through Design → Plan → Conclusion. Each stage is a separate skill. You orchestrate; the skills do the work.

## Arguments

The user's description of the task follows the command. May be a one-liner ("fix the flaky login test") or a paragraph. Use it as the seed for the slug and the initial framing for `up:udesign`.

## Flow

### 1. Slug

Derive a kebab-case slug from the description, 3 words max (e.g. "flaky-login-test"), and proceed. If the work belongs to a named epic (the user says so, or a matching `docs/tasks/<epic>/` folder exists), place the file at `docs/tasks/<epic>/<slug>.md` — see "Epics" below.

### 2. Resume check

Before creating a new task file, check if the slug already exists — scan `docs/tasks/**/*.md` (tasks may live in epic folders).

Status format: `<enum> — <optional annotation>`. The enum is everything before the first ` — `; the annotation is free text (dates, PR links, ship notes). Enum values: `design`, `planning`, `executing`, `reviewing`, `validating`, `done`, `shipped`, plus `reference` for epic overview files. Reopening a task = setting Status back to an earlier enum value with a dated annotation (e.g. `executing — reopened 2026-08-01, edge case CATS-1204`). Ignore header fields you don't recognize — older files may carry retired ones.

- Exists: read `**Status:**` from the header. Resume from the next stage:
  - `design` → continue design
  - `planning` → run `up:uplan`
  - `executing` → run `up:uexecute`
  - `reviewing` → run `up:ureview`
  - `validating` → re-check the Goal with the user (step 11); on confirmation → `done`
  - `done` / `shipped` → ask the user what they want to do (start a follow-up, re-open, view conclusion)
  - `reference` → not a task — an epic overview; ask which child task the user means
  - anything else → ask the user how to proceed
- Doesn't exist: proceed to step 3.
- Multiple in-flight tasks: if more than one task file has Status ≠ `done` / `shipped` / `reference`, list them and ask which one the user means (or whether this is a new task).

### 3. Create task file

Create `docs/tasks/<slug>.md` from the template. Status = `design`. Branch = `main` (placeholder until step 5). Goal = a first draft of the observable success condition from the description; `up:udesign` finalizes it, or `up:make` sets it directly when Design is skipped (trivial/small).

Template:

```markdown
# <Task Title>

**Status:** design
**Branch:** main
**Jira:** <ticket id/link — omit the line if none>
**Depends on:** <task file or ticket — omit the line if none>
**Goal:** <observable success condition that defines done — note if confirming it needs a real-world run or user sign-off beyond the diff>

## Design
<empty — filled by up:udesign>

### Prior art
<empty — filled by up:udesign: file:line citations from docs/tasks/ and archive/, or "none found">

### Invariants
<empty — IV1, IV2, … : hard constraints that must hold>

### Principles
<empty — PC1, PC2, … : softer guidance>

### Assumptions
<empty — AS1, AS2, … : unverified premises the design rests on; conclusion must report whether each held>

### Unknowns
<empty — UK1, UK2, … : open questions left to plan / execute; conclusion must report whether each resolved>

## Plan
<empty — filled by up:uplan; gains ### Rollout / ### Rollback when the change ships to a live system>

## Verify
<empty — filled by up:uverify>

## Code smells
<empty — file:line + one-line smell passed while exploring and left unfixed (out of scope, non-trivial); deleted if none>

## Conclusion
<empty — filled by up:ureview; after done/shipped grows dated ### Follow-up — <date> / ### Scope change — <date> entries and ### Deferred scope-parking>
```

### Epics — folder convention

A multi-task workstream gets a folder: `docs/tasks/<epic>/` holding `overview.md` at `**Status:** reference` (what the epic is, links to its child task files) plus one normal task file per child. Children are designed, executed, and resumed individually; the overview is never resumed and never carries a Goal.

### 4. Size classification

Based on the task description, classify size:

- Trivial — one-line change, typo, rename. Skip Design and Plan. Go straight to Execute. Status file still created.
- Small — single file or single concept change. Skip Design. Plan runs.
- Medium / Large — full flow.

Default to Medium silently. Jump to Trivial/Small only when the user's wording signals it — e.g. "quickly", "fast", "just", "one-line", "typo", "rename". Confirm before skipping any stage. When genuinely ambiguous, ask.

### 5. Design stage (unless skipped)

Invoke `up:udesign`. It populates `## Design`, `### Invariants` (IV), `### Principles` (PC), `### Assumptions` (AS), `### Unknowns` (UK), and records `TDD: yes / no (reason)`. Status → `planning`.

### 6. Branch decision

After Design (or immediately for trivial/small tasks), decide:

- Complex / long-running / touches many files → suggest a dedicated branch.
- Easy fix / small scope → suggest working on the current branch (usually `main`).

Always confirm with the user. If a branch is created, update the task file's `**Branch:**` header. When the work additionally needs filesystem isolation (a second live checkout), `up:git-worktrees` covers it on demand.

### 7. Plan stage (unless skipped)

Invoke `up:uplan`. It populates `## Plan`. Status → `executing`.

### 8. Execute stage

Invoke `up:uexecute`. Implements the plan, commits incrementally.

### 9. Verify loop

Invoke `up:uverify`. On failure: `up:uverify` describes how each failure *should* have worked, control returns to `up:uexecute`. Loop until verify passes.

### 10. Review stage

Status → `reviewing`. Invoke `up:ureview`. It dispatches `up:reviewer`, processes findings, fills `## Conclusion`. Status → `validating` — code is verified and reviewed, but the task is not `done` until its Goal is confirmed achieved (step 11).

### 11. Validate the goal

`done` means the Goal is achieved — not merely that code verified and review cleared. Check the Goal against reality:

- The verified diff already demonstrates the full Goal (verify's smoke exercised the real end state, nothing out-of-band remains) → state the evidence; the Goal is met.
- The Goal needs steps the agent can't or shouldn't finish alone — a run at full scale, an expensive / remote / paid job, or an outcome only observable in the user's environment ("training works on the dataset") → do what's safely in reach (the small or local proxy, captured in `## Verify`), then list the remaining steps and hand them to the user. Status stays `validating`.

Set Status → `done` only once the Goal is confirmed: by the agent's own end-to-end evidence when it could observe it, or by the user when it couldn't. Never declare `done` off "verified + reviewed" alone.

If the Goal is still pending, proceed to step 12 to offer finish actions — the verified code can still merge — but keep Status `validating` and state that the task is not done until the Goal is confirmed; a later session resumes from `validating` to re-check it.

Once `done`, run the docs-refresh check (see below).

`shipped` comes after `done`: set it when the merge/deploy is confirmed real, with the evidence in the annotation (e.g. `shipped — merged PR #294, prod 2026-08-03`). If the finish action chosen at step 12 completes the merge and nothing else gates the ship, set it there; otherwise a later session (or the owner) flips it when reality catches up.

### 12. Finish

Present options to the user:
- Merge / open PR (if on a branch)
- Move on

Execute only after the user chooses.

## After task is done — docs refresh

Run this once, after the Goal is confirmed and Status is `done` (step 11) — not after every stage. Scan the project docs and update them if the work surfaced something they should reflect. Cheap, light-touch; not a full doc pass.

Files to scan:
- `CLAUDE.md` (project-wide agent guidance)
- `README.md`
- `docs/**/*.md` (project documentation, excluding the task file itself and archived tasks)

What to look for:
- New conventions, invariants, or principles that should be global → update `CLAUDE.md`
- New components, commands, or features the README should mention
- Stale content contradicted by the stage's work → delete or correct
- Pointers to the task file if future contributors would benefit

Rules:
- If nothing needs updating: say so in one line and move on. Do not invent edits.
- If updates are needed: make them directly, then summarize what changed in 1-3 lines (e.g. "README: fixed install instructions; CLAUDE.md: no change"). Do not prompt for approval first. Do not produce a detailed diff — the user will git-diff if they want.
- Follow `up:udocument`: lead with why, lists over tables, no aspirational content, kill stale content.
- Do not duplicate content across task file and project docs — pick one home per fact.

## Stop conditions

Stop and ask the user when:

- Size classification is genuinely unclear
- User has expressed a preference (branch, scope, TDD) that conflicts with the auto-inference
- Any stage's skill returns a blocker

## Rules

- Never skip Review
- Never auto-merge or auto-push — the user chooses at step 12
- Never mark `done` until the Goal is confirmed achieved (step 11) — verified + reviewed is not done
- Never create a worktree without confirming with the user
- Keep the task file as the single source of truth — each stage reads it, each stage writes to it
- External spec / design docs (e.g. anything under `docs/specs/`) are read-only during execute. If a stage finds the spec is wrong, surface it to the user — don't mutate it silently
- Don't assume prior session memory — the next agent may be a fresh context reading only the task file

## Terminal state

Task file Status = `done` (Goal confirmed achieved, step 11), Conclusion filled, user has chosen a finish action (merge, PR, cleanup, or defer).
