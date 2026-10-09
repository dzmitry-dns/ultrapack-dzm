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

Status format: new files write `<enum> (<optional annotation>)` or `<enum>: <annotation>`. When reading, the enum is the first word of the Status value, so older files written as `<enum> — <annotation>` still parse. The annotation is free text (dates, PR links, ship notes). Enum values: `design`, `planning`, `executing`, `verifying`, `reviewing`, `validating`, `done`, `shipped`, plus `reference` for epic overview files. Reopening a task = setting Status back to an earlier enum value with a dated annotation (e.g. `executing (reopened 2026-08-01, edge case PROJ-1204)`). Ignore header fields you don't recognize — older files may carry retired ones.

Branch guard, for a resumed task and before step 3's first commit alike: when `git branch --show-current` is neither the default branch nor this task's `**Branch:**`, stop and ask before any commit. Another task's plain branch (step 6) is checked out in this folder.

- Exists: if the header has a `**Worktree:**` line that names a path (`none` or an empty value is no worktree), settle the checkout before reading anything else, because the main branch's copy is frozen at entry. The folder is in `git worktree list` and its PR is not merged (or no PR exists yet) → `EnterWorktree` with that `path` and read the task file there. The PR is merged → stay in the main checkout, run step 12's "Leaving a worktree" step 5 without asking (only when the folder is still listed), and read the copy on the main branch. No worktree path and a `**Branch:**` that is not the default branch and exists (`git branch --list <branch>`, else `git ls-remote --heads origin <branch>`; free text such as `none yet` or a deleted branch is not one) → a plain branch. Its PR merged (`gh pr list --head <branch> --state merged`) → `git switch` to the default branch when the checkout is still on this branch, `git pull --ff-only`, then read the working copy. Not merged → read the task file from the branch, `git show <branch>:<task file path>` (`git fetch origin <branch>` and `origin/<branch>` when only the remote has it), because the copy on the current branch stops at the switch. That read decides how to continue, per the project's rules: `git switch <branch>`, or a worktree when they call for one; after a switch the working copy is the file. Then read `**Status:**` from the header. If the file ends with one or more Handoff blocks (`### Handoff: <date>`, or `### Handoff — <date>` in older files), read the latest one first — it holds what the previous session left uncommitted or undecided, and its first action. If it has an `Owner has not seen` line that is not "none", the first chat message of the session tells the owner those results in plain words, before any question and before any work step. Resume from the next stage:
  - `design` → continue design
  - `planning` → run `up:uplan`
  - `executing` → run `up:uexecute`
  - `verifying` → run `up:uverify` (step 9); the plan is already implemented, do not re-run execute
  - `reviewing` → run `up:ureview` and tell it `/up:make` invoked it (step 10)
  - `validating` → re-check the Goal with the user (step 11); on confirmation, step 11's `done` path (docs refresh included), then step 12, so the Closing line prints in the session that closes the task
  - `done` / `shipped` → ask the user what they want to do (start a follow-up, re-open, view conclusion)
  - `reference` → not a task — an epic overview; ask which child task the user means
  - anything else → ask the user how to proceed
- Doesn't exist: proceed to step 3.
- Multiple in-flight tasks: if more than one task file has Status ≠ `done` / `shipped` / `reference`, list them and ask which one the user means (or whether this is a new task).

### 3. Create task file

Create `docs/tasks/<slug>.md` from the template. Status = `design`. Branch = `main` (placeholder until step 6). Goal = a first draft of the observable success condition from the description; `up:udesign` finalizes it, or `up:make` sets it directly when Design is skipped (trivial/small). If the project's `CLAUDE.md` has a `## Jira adapter` section and the task has no `**Jira:**` header, prompt once for a ticket id or skip (`up:ujira`).

Template:

```markdown
# <Task Title>

**Status:** design
**Branch:** main
**Worktree:** <absolute path of the worktree folder, omit the line if none>
**Jira:** <ticket id/link (omit the line if none)>
**Depends on:** <task file or ticket (omit the line if none)>
**Goal:** <observable success condition that defines done (note if confirming it needs a real-world run or user sign-off beyond the diff)>

## Design
<empty: filled by up:udesign>

### Prior art
<empty: filled by up:udesign with file:line citations from docs/tasks/ and archive/, or "none found">

### Invariants
<empty: IV1, IV2, … are hard constraints that must hold>

### Principles
<empty: PC1, PC2, … are softer guidance>

### Assumptions
<empty: AS1, AS2, … are unverified premises the design rests on; conclusion must report whether each held>

### Unknowns
<empty: UK1, UK2, … are open questions left to plan / execute; conclusion must report whether each resolved>

## Plan
<empty: filled by up:uplan; gains ### Rollout / ### Rollback when the change ships to a live system>

## Verify
<empty: filled by up:uverify>

## Code smells
<empty: `- <file:line>: <one-line smell>` lines passed while exploring and left unfixed (out of scope, non-trivial); deleted if none>

## Conclusion
<empty: filled by up:ureview; after done/shipped grows dated ### Follow-up: <date> / ### Scope change: <date> entries and ### Deferred scope-parking>
```

### Epics — folder convention

A multi-task workstream gets a folder: `docs/tasks/<epic>/` holding `overview.md` at `**Status:** reference` (what the epic is, links to its child task files) plus one normal task file per child. Children are designed, executed, and resumed individually; the overview is never resumed and never carries a Goal.

### 4. Size classification

Based on the task description, classify size:

- Trivial — one-line change, typo, rename. Skip Design and Plan. Go straight to Execute. Status file still created.
- Small — single file or single concept change. Skip Design. Plan runs.
- Medium / Large — full flow.

A skipped Design leaves one line in `## Design`: `Skipped (<size>): <reason>`.

Default to Medium silently. Jump to Trivial/Small only when the user's wording signals it — e.g. "quickly", "fast", "just", "one-line", "typo", "rename". Confirm before skipping any stage. When genuinely ambiguous, ask.

### 5. Design stage (unless skipped)

Invoke `up:udesign`. It populates `## Design`, `### Invariants` (IV), `### Principles` (PC), `### Assumptions` (AS), `### Unknowns` (UK), and records `TDD: yes / no (reason)`. Status → `planning`.

Before approval the Design goes through the design point of `${CLAUDE_PLUGIN_ROOT}/skills/uplan/review-before-code.md`, the single home of when it runs (not step 4's classification).

### 6. Branch decision

Runs at the end of step 7, once the Plan is approved; Trivial (no Plan) runs it right after step 4. Both answers can depend on the plan (what each phase pushes, whether the work outlives the session), so Design and Plan commits before this step go to the current branch.

**Branch?** Stay on the current branch (usually `main`) unless:

- the project's rules list reasons for a branch and one applies;
- the user asks for a branch;
- the task fixes a merged change whose task is still `validating` (Rules).

With no such list in the project's rules, propose a branch only by naming a concrete reason, and ask. Task size alone is not a reason.

**Worktree?** A branch is a plain branch in the current checkout unless the project's rules say when a branch needs a worktree and that applies, or the user asks. Then the project's worktree convention decides how the worktree is made, without asking; record the folder as `**Worktree:** <path>` in the task file header. A user who asks for a worktree in a project with no convention runs `/up:git-worktrees` (manual-only skill); suggest it, never invoke it.

A task that branches records why in `## Design` (after the `Skipped` line when Design was skipped): `Branch reason: <the reason, by name>`, plus `Worktree reason: <the reason>` when it gets a worktree. Nothing is written for a default. The `**Branch:**` header stays a bare branch name, because `up:uexecute` compares it to `git branch --show-current`.

A plain branch: write the `**Branch:**` header line, commit the task file on the current branch (by path), then `git switch -c <branch>`. A resume reads the task from the branch (step 2). The project's rules say how the checkout returns to its default branch.

A new worktree has none of the main checkout's git-ignored env files, and the first check run fails without them. Before the first command in it, symlink each one from the main checkout: use the list in the project's rules, or else `git -C <main checkout> ls-files --others --ignored --exclude-standard | grep -E '(^|/)\.env'`, then `ln -s <main checkout>/<f> <worktree>/<f>` per file. Symlinks, not copies: an env change in the main checkout reaches every worktree.

Order of entry: first sweep stale worktrees: for each entry of `git worktree list` other than the main checkout whose PR is `MERGED`, run step 12's "Leaving a worktree" step 5 without asking. Then write the `**Branch:**` and `**Worktree:**` header lines, commit the new task file in the main checkout (by path), then `git worktree add`, the env links, then the `EnterWorktree` tool with `path: <worktree folder>`. Once inside, Claude Code refuses any git command that targets the main checkout (`cd <main checkout> && git ...` included), so every commit goes to the branch. Never build a temporary extra worktree to commit to the main branch from inside one. When something must reach the main branch mid-work: `ExitWorktree` with `action: keep`, commit in the main checkout, `EnterWorktree` with the same `path` again.

### 7. Plan stage (unless skipped)

Invoke `up:uplan`. It populates `## Plan`. Before the approval pause the plan goes through the plan point of `${CLAUDE_PLUGIN_ROOT}/skills/uplan/review-before-code.md`, the single home of when it runs. Status → `executing`. If Jira is configured, invoke `up:ujira` at this transition — the start draft rides the plan-approval pause, minus whatever the project set `auto` to, which `up:ujira` has already applied.

Plan-approval gate (single home; `up:uplan` defers to it): `up:uplan` waits for the user's approval unless you tell it, in the invocation, that the task is Small and the plan touches fewer than 3 files, no DB migration, and no new API surface; then it presents the highlights and proceeds. Medium / Large always pause. Trivial skips Plan entirely (step 4). A manual or resumed `up:uplan` has no size and always waits.

If the gate does not pause and Jira is configured, `up:ujira` still runs at this transition: auto items post as usual, and anything needing approval is carried to the terminal draft (step 12) instead of a pause the flow no longer has.

Once the plan is approved (or the gate lets it proceed), run step 6, then step 8.

### 8. Execute stage

Run the context checkpoint (see below). Invoke `up:uexecute`. Implements the plan, commits incrementally.

### 9. Verify loop

Status → `verifying` once every plan phase is committed. Run the context checkpoint (see below). Invoke `up:uverify`. On failure: `up:uverify` describes how each failure *should* have worked, control returns to `up:uexecute` (Status stays `verifying`; the plan is implemented, only the fix is pending). Loop until verify passes.

### 10. Review stage

Status → `reviewing`. Run the context checkpoint (see below). Invoke `up:ureview` and tell it `/up:make` invoked it. It dispatches `up:reviewer` (unless Design was skipped, step 1), processes findings, fills `## Conclusion`. Status → `validating` — code is verified and reviewed, but the task is not `done` until its Goal is confirmed achieved (step 11).

### 11. Validate the goal

`done` means the Goal is achieved — not merely that code verified and review cleared. Check the Goal against reality:

- The verified diff already demonstrates the full Goal (verify's smoke exercised the real end state, nothing out-of-band remains) → state the evidence; the Goal is met.
- The Goal needs steps the agent can't or shouldn't finish alone — a run at full scale, an expensive / remote / paid job, or an outcome only observable in the user's environment ("training works on the dataset") → do what's safely in reach (the small or local proxy, captured in `## Verify`), then list the remaining steps and hand them to the user. Status stays `validating`.

Set Status → `done` only once the Goal is confirmed: by the agent's own end-to-end evidence when it could observe it, or by the user when it couldn't. Never declare `done` off "verified + reviewed" alone.

If the Goal is still pending, proceed to step 12 to offer finish actions — the verified code can still merge — but keep Status `validating` and state that the task is not done until the Goal is confirmed; a later session resumes from `validating` to re-check it.

Once `done`, run the docs-refresh check (see below).

`shipped` comes after `done`: set it when the merge/deploy is confirmed real, with the evidence in the annotation (e.g. `shipped (merged PR #294, prod 2026-08-03)`). If the finish action chosen at step 12 completes the merge and nothing else gates the ship, set it there; otherwise a later session (or the owner) flips it when reality catches up.

### 12. Finish

Print the Closing line (`${CLAUDE_PLUGIN_ROOT}/skills/_principles.md` → Closing line), then present options to the user:
- Merge / open PR (if on a branch)
- Move on

When the project's policy file says to open PRs with auto-merge (`gh pr merge --auto`, which merges once the required checks pass), turn it on only once Status is `done`; a PR already opened that way is reported, not offered for merge. While Status is `validating` the user is still checking the result: open the PR without auto-merge and offer the merge here as its own question. With no such policy, the merge waits for the user's choice here.

A merge into `main` needs a yes to a question that names only the merge: the PR, the target branch, and the release that will ship it when one is known ("this goes into tomorrow's release"). A plan approval, a yes to a list, or a merge line inside a longer message never counts. Turning auto-merge back on after it was turned off (the user found a problem, a fix followed) needs that same separate yes.

If Jira is configured, present the `up:ujira` terminal draft alongside these options. Items `up:ujira` auto-applied appear there as receipts, not as choices.

Execute only after the user chooses.

**Leaving a plain branch.** The finish ends with the checkout step the project's rules require (for example returning a shared checkout to its default branch).

**Leaving a worktree.** When the task file has a `**Worktree:**` line that names a path (not `none`), the finish ends with this sequence. It asks no questions: the project's rule that put the work in a worktree already covers removing it. The merge question above stays.

1. Stop the processes this session started in the worktree (dev servers, containers), by the ids it got when it started them. No `lsof` / `ps` hunt.
2. Still inside the worktree, read `gh pr view <n> --json state`. Not `MERGED` (auto-merge pending, or Status `validating`): write the Handoff line "worktree <path> stays until PR #<n> merges" in the task file on the branch, commit, push. Every task-file edit happens here, before the copy, so the main branch and the feature branch end up with identical files and the PR merges without a conflict.
3. `ExitWorktree` with `action: keep`. A worktree entered by `path` cannot be removed by the tool; `remove` fails with "not the owner", so never try it. A session that never called `EnterWorktree` (it was launched with the worktree folder as its directory) skips this step and runs every step 4 command as `cd <main checkout> && git ...`.
4. In the main checkout: `git pull --ff-only`, then `git checkout <branch> -- <task file path on the branch>`; when the branch moved the file to `archive/`, also `git rm --ignore-unmatch <old path>` (a merged PR already removed it). Commit those paths only, and only if `git diff --cached --quiet` fails (a merged PR already brought them). Push per the project's policy. The pull fails (another session's local commits or edits in a shared checkout): commit anyway, push only when `git log origin/main..HEAD` shows this session's commits alone, otherwise name the foreign commit in the report and do not push.
5. PR `MERGED`: `git worktree remove <path>`, `git branch -D <branch>` (`-d` refuses after a squash merge; the merge is already confirmed), `git push origin --delete <branch>` unless GitHub already deleted it. Then delete the `**Worktree:**` header line in the main branch's copy of the task file and commit it, so no later resume looks for the folder. Not merged: keep the worktree; it is removed by the next resume of this task (flow step 2) or by the stale sweep of the next worktree created (flow step 6).
6. Report in one line. No checks after removal (`ls` of the deleted folder, `git branch -a`, `merge-base`): `git worktree remove` either succeeded or printed an error. It refuses on a leftover untracked file: delete that file (a `__probe*` or scratch output) and rerun, without asking.

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
- Follow the rules in `${CLAUDE_PLUGIN_ROOT}/skills/udocument/SKILL.md` (read the file; the skill is manual-only): lead with why, lists over tables, no aspirational content, kill stale content.
- Do not duplicate content across task file and project docs — pick one home per fact.

## Context checkpoint

Runs right before invoking the stage skill at steps 8, 9, and 10 — one check per transition, covering everything since the previous checkpoint (step 8's check covers steps 5–7). Count subagents dispatched and tool outputs long enough to fill roughly a screen. Either count at 3+ subagents or 2+ large outputs → print one line: "This session has grown large — consider `/up:summary` before continuing." Then proceed to the stage regardless; advisory only, never a pause.

At each phase commit of a Medium or Large task, and at every Status transition, append the Handoff block by `/up:summary` steps 1-3 without asking. Print no prompt at these points. This is never a pause either. Inside a worktree these commits go to the branch only; the main branch gets the task file at entry and at exit (step 6, step 12).

## Stop conditions

Stop and ask the user when:

- Size classification is genuinely unclear
- User has expressed a preference (branch, scope, TDD) that conflicts with the auto-inference
- Any stage's skill returns a blocker

## Rules

- Never skip Review (the final `up:ureview`; the pre-code skip phrase covers only the review before code)
- Never merge on your own initiative. Under a project auto-merge policy, auto-merge goes on only at Status `done`; any other merge into `main` needs the separate yes of step 12, never a plan approval. With no such policy, the user chooses at step 12. Fixes to a merged change whose task is still `validating` go to a new branch and PR, never straight to `main`, even where the policy allows pushing to `main`. Push follows the project's policy file when it allows pushing (for example a `workflow.md` that says push without asking). With no such policy, the user chooses at step 12
- Never mark `done` until the Goal is confirmed achieved (step 11) — verified + reviewed is not done
- Never create a branch or a worktree without a reason step 6 accepts: a project rule that applies, the user's request, or the `validating` rule above
- Keep the task file as the single source of truth — each stage reads it, each stage writes to it
- External spec / design docs (e.g. anything under `docs/specs/`) are read-only during execute. If a stage finds the spec is wrong, surface it to the user — don't mutate it silently
- Don't assume prior session memory — the next agent may be a fresh context reading only the task file
- Scope move at any stage (part of the work goes to another ticket, or comes in from one): if Jira is configured, invoke `up:ujira` in the same step, before reporting; its "Scope move" paragraph drafts the source ticket's description item. The Status-transition triggers never see a scope move
- Every commit this flow makes (task file, Status transitions) follows `${CLAUDE_PLUGIN_ROOT}/skills/_principles.md` → Commits: no trailer of any kind

## Terminal state

Task file Status = `done` (Goal confirmed achieved, step 11), Conclusion filled, user has chosen a finish action (merge, PR, or move on).
