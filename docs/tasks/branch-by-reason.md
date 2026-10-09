# Branch only for a listed reason, worktree only for a long-lived branch

**Status:** design
**Branch:** main
**Goal:** A task started with `/up:make` runs on the current branch (main) unless a listed reason for a branch applies or the owner asks for one; a task that branches uses a plain branch in the current checkout, and a worktree only when the project's rules call for one. In cccc that gives three observable outcomes: a task with no listed reason commits to `main`; a short branched task uses a plain branch in `cccc-monorepo` and returns the checkout to `main` before the session ends; a long-lived branch (or a crowded checkout) gets the worktree flow unchanged. Confirming it needs live cccc `/up:make` runs of each kind (owner's environment).

## Design

Owner's ask (2026-10-08): starting sessions in a worktree is slow and awkward; find the rule that maps task size to worktree use and improve it. Scope approved 2026-10-09. Owner's direction in review (2026-10-09): "workflow [worktree] нужны только для долгоиграющих веток. Все остальное можно пилить просто на бренчах."

Why it happens today: the pack has no size rule for branches. Size (`make.md` step 4) only decides which stages are skipped, and every task defaults to Medium. Step 6 suggests a branch for "complex / long-running / touches many files", which fits most Medium tasks. In cccc, `workflow.md` then puts every branch in a worktree, with a 6-step entry and a 6-step exit. Result in cccc: since 2026-10-05, 4 of 7 new tasks ran in a worktree; across all task files about half record `main` (151 of 292 on 2026-10-09) and the rest used feature branches in the shared checkout. The worktree rule itself (cccc `25a00b66a`, 2026-10-06) was written for concurrency, not size: "several sessions and the owner work there at once" (`workflow.md:42`). The worktree flow took 3 pack versions (0.3.49-0.3.51) of fixes in 3 days.

The ideal: two separate questions, each answered by a reason someone can name. First, does the task need a branch at all? The default is no; the reasons live in the project's rules, because only the project knows what its `main` triggers (in cccc a push to `main` deploys dev). Second, does the branch need its own folder? The default is no; a worktree is for a branch that outlives the session, or for a checkout other sessions are using right now. The worktree machinery of 0.3.51 stays as it is; it runs far less often.

Decisions:
- **D1, pack `make.md` step 6:** the step becomes two questions.
  - *Branch?* Stay on the current branch unless (a) the project's rules list reasons for a branch and one applies, (b) the owner asks for a branch, or (c) the pack's own rule fires: a fix to a merged change whose task is still `validating` (already in make.md Rules). With no project list, the agent may propose a branch only by naming a concrete reason, and asks.
  - *Worktree?* A branch is a plain branch in the current checkout, unless the project's rules say when a branch needs a worktree and that applies, or the owner asks. A project's worktree convention then decides *how* the worktree is made (0.3.51 entry order, unchanged); it no longer decides *whether*.
  - Timing: step 6 runs once the Plan is approved (Trivial has no Plan: right after step 4), because both answers can depend on the plan (cccc branch reason 3; the number of phases decides whether the branch outlives the session). The step keeps its number 6, since other files cite step numbers; step 6 opens with "runs after step 7's approval" and step 7 ends by pointing to it. Design and Plan commits before the decision go to the current branch.
  - `uexecute`'s "Branch / worktree correctness" and make.md's Rules line ("Never create a worktree without confirming...") say the same in one clause each.
- **D2, step 2 resume for a plain branch:** a task whose `**Branch:**` names a branch that is not merged and whose header has no `**Worktree:**` path is read from the branch first (`git show origin/<branch>:<task file path>`), because the copy on the current branch stops at the switch. Same wording pass: step 2 settles a worktree only for a `**Worktree:**` line that names a path (cccc's template writes `**Worktree:** none`, 200 files today, `task-files.md:20`); step 3's "placeholder until step 5" points at step 6.
- **D3, record the reasons:** a task that branches carries one line `Branch reason: <listed reason, by name>` in `## Design` (after a `Skipped` line when Design is skipped), plus `Worktree reason: <listed reason>` when it gets a worktree. Nothing is written for a default. The header stays a bare branch name, because `uexecute` compares it to `git branch --show-current`.
- **D4, cccc `.claude/rules/workflow.md`, new subsection "When to branch"** before the worktree subsection. Everything goes to `main` in the shared checkout except:
  1. A change to a Dockerfile, a build arg, or a CI workflow file. The CI build on a GitHub runner (no layer cache, the runner's own packages) must pass before `main` deploys it; pull-request CI runs that build without deploying, a push to `main` builds and deploys dev (example: CATS-1776). A local build ("Local Docker builds") is not that check. Type-check and tests do not count: they run locally before every push to `main`.
  2. A fix to a merged feature whose task is still `validating` (the existing rule in "Commit and push", referenced, not copied).
  3. Phases that cannot each leave dev working. The plan orders phases so every phase commit leaves dev usable; only when that is impossible (example: a page that needs an API a later phase adds, with no way to hide it) does the task branch.
  4. The owner asks for a branch or a pull request.
  5. The task would push to `main` within 24 hours before a production release the owner has named (it starts in that window, or still has phases to push when the owner names the release; the remaining phases then move to a branch). The production dispatch builds from `main` by default, and the "no auto-merge before a release" exception in "Commit and push" only works on a pull request.
- **D5, cccc, the worktree subsection gets a "When a branch needs a worktree" lead.** A branch is a plain branch in `cccc-monorepo` unless:
  1. It is long-lived: the work or its unmerged pull request is expected to outlive this session (the plan has more phases than one session finishes, or the PR waits for the owner: Status stops at `validating`, branch reason 2 or 5).
  2. The shared checkout shows another session's work at the decision: uncommitted changes to files this session did not edit, or commits in `git log origin/main..HEAD` this session did not make. `git switch` moves every session working in that folder, so a crowded checkout never switches.
  3. The owner asks for a worktree.
  A plain branch: `git switch -c <branch>` from an up-to-date `main`, phase commits and pushes to the branch, the PR per "Commit and push" (auto-merge rules unchanged), then `git switch main` and `git pull --ff-only` before the session ends. The local branch is deleted (`git branch -D`) once the PR is merged, by this session or the next one that sees it merged. A plain branch whose work turns out to outlive the session: commit, push, switch back to `main`; the next session continues it in a worktree made from the existing branch (`git worktree add <path> <branch>`) and records `Worktree reason: 1`.
  The worktree subsection's first sentence changes from "Branch work goes into a git worktree" to point at this list.

Approaches considered:
- A (chosen, owner's direction): default `main`; a plain branch for a listed reason; a worktree only for a long-lived branch or a crowded checkout. Prose in 2 pack files plus the version bump, 1 cccc file; every 0.3.51 worktree rule untouched. Risk: "expected to outlive the session" is a forecast; a wrong forecast is recovered by the switch-back rule in D5.
- B: default `main`, every branch in a worktree (this file's previous version). Rejected by the owner: keeps the worktree cost for short branches.
- C: map size to branch (Large → branch). Rejected: size does not predict the need; CATS-1776 was a modest change that needed the pull-request Docker check.

Out of scope (deferred after the 2026-10-09 self-review): task file kept only on the branch; Claude Code's built-in worktrees with `.worktreeinclude` (copies `.env` instead of linking; needs a probe run); deleting the disabled `git-worktrees` skill (owner's 2026-09 decision: disable, not delete). Known side effect left as is: the merged-worktree sweep runs only when a worktree is created or its task resumes, so with fewer worktrees a merged one stays on disk longer; it costs disk space only.

Backwards compatibility: no break for running tasks: a task whose header names a worktree path resumes and exits as in 0.3.51. Behavior change for new tasks in any project without a reasons list: the agent no longer suggests a branch from size alone, and a branch no longer implies a worktree. Fork-only change (opinionated workflow policy), not sent upstream.
TDD: no (doc-only plugin; verification is install-and-invoke)
Reviewed before code: 2 rounds, 4 Critical/Important fixed, 0 rejected, 2026-10-09

### Prior art
- `docs/tasks/t2-template-realignment.md:65`: step 6 became a branch-only decision and worktree handling was dropped from the pack; 0.3.47-0.3.51 brought worktree rules back for cccc's convention. This task keeps that convention and narrows when it fires.
- `docs/tasks/parallel-phase-exec.md:183`, `docs/tasks/interface-first-parallel.md:249`: earlier make runs chose "dedicated branch + worktree" as the safest default for hands-off work; the default this task replaces.

### Invariants
- IV1: A task file whose `**Worktree:**` line names a path resumes and exits exactly as in 0.3.51 (make.md step 2's worktree logic, step 6's entry order, step 12 "Leaving a worktree" unchanged; step 2 only stops reading `none` as a path).
- IV2: The pack's `validating` rule (a fix to a merged change whose task is still `validating` goes to a new branch and pull request) still forces a branch, in both pack and cccc wording.
- IV3: When the project's rules call for a worktree, the task follows the worktree convention without asking (no new question added to the flow).
- IV4: The shared checkout `cccc-monorepo` is on `main` whenever no session is mid-way through a plain branch: every plain branch ends with `git switch main`.

### Principles
- PC1: One home per rule: the reason lists live in the project's rules file; the pack only says "follow the project's list" and never copies cccc's lists.

### Assumptions
- AS1: In cccc, every pull-request run builds the Docker images without deploying, and a push to `main` builds and deploys dev (`.github/workflows/ci-np-*-dev.yml` triggers on both; checked 2026-10-09).
- AS2: Most cccc tasks can order their phases so each phase commit leaves dev usable, so branch reason 3 stays rare.
- AS3: Most branched cccc tasks finish within one session, with the PR merged by auto-merge, so worktree reason 1 stays rare.

### Unknowns
- UK1: Whether live cccc sessions pick `main`, a plain branch and a worktree in the cases above (the Goal's real check; needs the owner's next tasks).
- UK2: Whether a session that starts on `main` in the shared checkout while another session is on a plain branch notices it before its first commit (uexecute checks `git branch --show-current` against the header before every write; the plan confirms this covers it).

## Plan
<empty: filled by up:uplan; gains ### Rollout / ### Rollback when the change ships to a live system>

## Verify
<empty: filled by up:uverify>

## Code smells
<empty: `- <file:line>: <one-line smell>` lines passed while exploring and left unfixed (out of scope, non-trivial); deleted if none>

## Conclusion
<empty: filled by up:ureview; after done/shipped grows dated ### Follow-up: <date> / ### Scope change: <date> entries and ### Deferred scope-parking>
