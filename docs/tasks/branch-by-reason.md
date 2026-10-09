# Branch only for a listed reason

**Status:** design
**Branch:** main
**Goal:** A task started with `/up:make` runs on the current branch (main) unless one of the project's listed reasons for a branch applies or the owner asks for one. In cccc a task with no listed reason gets no worktree and no branch; a task with a reason gets the worktree flow unchanged. Confirming it needs one live cccc `/up:make` run of each kind (owner's environment).

## Design

Owner's ask (2026-10-08): starting sessions in a worktree is slow and awkward; find the rule that maps task size to worktree use and improve it. Scope approved 2026-10-09 after a self-review that deferred the other options (Out of scope below).

Why it happens today: the pack has no size rule for branches. Size (`make.md` step 4) only decides which stages are skipped, and every task defaults to Medium. Step 6 suggests a branch for "complex / long-running / touches many files", which fits most Medium tasks. In cccc, `workflow.md` then puts every branch in a worktree, with a 6-step entry and a 6-step exit. Result in cccc: since 2026-10-05, 4 of 7 new tasks ran in a worktree; across all task files about half record `main` (151 of 292 on 2026-10-09) and the rest used feature branches in the shared checkout. The worktree rule itself (cccc `25a00b66a`, 2026-10-06) was written for concurrency, not size: "several sessions and the owner work there at once" (`workflow.md:42`). D3 reason 6 keeps that protection where it is visible. The worktree flow took 3 pack versions (0.3.49-0.3.51) of fixes in 3 days.

The ideal: the current branch is the default for every size. A branch is created only for a reason someone can name, and the reasons live in the project's rules, because only the project knows what its `main` triggers (in cccc a push to `main` deploys dev). The worktree machinery stays as it is; it simply runs far less often.

Decisions:
- **D1, pack `make.md` step 6:** replace the size-based suggestion. New rule: stay on the current branch unless (a) the project's rules list reasons for a branch and one applies, (b) the owner asks for a branch, or (c) the pack's own rule fires: a fix to a merged change whose task is still `validating` (already in make.md Rules). With no project list, the agent may still propose a branch, but only by naming a concrete reason, and asks. The project's worktree convention keeps deciding *how* a branch is made; it no longer decides *whether*. `uexecute`'s "Branch / worktree correctness" and make.md's Rules line say the same in one clause each. Timing: the branch decision runs once the Plan is approved (Trivial has no Plan: right after step 4), because a project reason can depend on how the plan splits the phases (cccc reason 3). The step keeps its number 6, since other files cite step numbers; step 6 opens with "runs after step 7's approval" and step 7 ends by pointing to it. Design and Plan commits before the decision go to the current branch, as for any task on `main` today; the 0.3.51 entry order then runs unchanged, only later. Two wording fixes in the same file: step 2 settles a checkout only for a `**Worktree:**` line that names a path (cccc's template writes `**Worktree:** none`, 200 files today, `task-files.md:20`), and step 3's "placeholder until step 5" points at step 6.
- **D2, record the reason:** a task that gets a branch carries one line `Branch reason: <the listed reason, by name>` in `## Design` (after a `Skipped` line when Design is skipped). Nothing is written for the default. The reviewer and the owner see why a worktree exists; the header stays a bare branch name, because `uexecute` compares it to `git branch --show-current`.
- **D3, cccc `.claude/rules/workflow.md`:** a new subsection "When to branch" before "Feature branches: git worktree". Everything goes to `main` in the shared checkout except:
  1. A change to a Dockerfile, a build arg, or a CI workflow file. The CI build on a GitHub runner (no layer cache, the runner's own packages) must pass before `main` deploys it; pull-request CI runs that build without deploying, a push to `main` builds and deploys dev (example: CATS-1776). A local build ("Local Docker builds") is not that check. Type-check and tests do not count: they run locally before every push to `main`.
  2. A fix to a merged feature whose task is still `validating` (the existing rule in "Commit and push", referenced, not copied).
  3. Phases that cannot each leave dev working. The ordering rule lives in the same cccc subsection: the plan orders phases so every phase commit leaves dev usable; only when that is impossible (example: a page that needs an API a later phase adds, with no way to hide it) does the task branch.
  4. The owner asks for a branch or a pull request.
  5. The task would push to `main` within 24 hours before a production release the owner has named (it starts in that window, or still has phases to push when the owner names the release; then the remaining phases move to a branch). The production dispatch builds from `main` by default, and the existing "no auto-merge before a release" exception in "Commit and push" only works on a pull request.
  6. At the branch decision the shared checkout shows another session's work: uncommitted changes to files this session did not edit, or commits in `git log origin/main..HEAD` this session did not make. A session that starts later cannot be seen at that moment; for that case the existing path-only staging and push check (`workflow.md:34`) stay the guard, as they were for the tasks on `main` before 2026-10-06.
  The worktree subsection's first sentence changes from "Branch work goes into a git worktree" to say it applies to the cases above.

Approaches considered:
- A (chosen): default current branch, project-listed reasons. Cheap (prose in 2 pack files plus the version bump, 1 cccc file), keeps every worktree rule untouched. Risk: reason 3 is a judgment call and could be stretched to cover any Medium task; the "every phase leaves dev usable" test narrows it.
- B: map size to branch (Large → branch). Rejected: size does not predict the need; CATS-1776 was a modest change that needed the pull-request Docker check, while a Large docs task needs no branch.
- C: tighten the "complex" wording only. Rejected: still agent judgment with no named reason, which is how 4 of 7 tasks got a worktree.

Out of scope (deferred after the 2026-10-09 self-review): task file kept only on the branch (a session started in `main` would not find it and would create a duplicate task file); Claude Code's built-in worktrees with `.worktreeinclude` (copies `.env` instead of linking; needs a probe run); deleting the disabled `git-worktrees` skill (owner's 2026-09 decision: disable, not delete). The 0.3.51 worktree entry/exit flow is not touched. Known side effect left as is: the merged-worktree sweep runs only when a worktree is created or its task resumes, so with fewer worktrees a merged one (with its `node_modules`) stays on disk longer; it costs disk space only.

Backwards compatibility: no break for running tasks: the resume check (step 2) and the worktree entry/exit stay as they are, so a task that already has a `**Worktree:**` line resumes and exits unchanged. Behavior change for new tasks in any project without a reasons list: the agent no longer suggests a branch from size alone; it names a reason and asks. Fork-only change (opinionated workflow policy), not sent upstream.
TDD: no (doc-only plugin; verification is install-and-invoke)
Reviewed before code: 2 rounds, 4 Critical/Important fixed, 0 rejected, 2026-10-09

### Prior art
- `docs/tasks/t2-template-realignment.md:65`: step 6 became a branch-only decision and worktree handling was dropped from the pack; 0.3.47-0.3.51 brought worktree rules back for cccc's convention. This task keeps that convention and narrows when it fires.
- `docs/tasks/parallel-phase-exec.md:183`, `docs/tasks/interface-first-parallel.md:249`: earlier make runs chose "dedicated branch + worktree" as the safest default for hands-off work; the default this task replaces.

### Invariants
- IV1: A task file whose `**Worktree:**` line names a path resumes and exits exactly as in 0.3.51 (make.md step 2's checkout logic, step 6's entry order, step 12 "Leaving a worktree" unchanged; step 2 only stops reading `none` as a path).
- IV2: The pack's `validating` rule (a fix to a merged change whose task is still `validating` goes to a new branch and pull request) still forces a branch, in both pack and cccc wording.
- IV3: When a project's rules define a worktree convention, a task that branches still follows it without asking (no new question added to the flow).

### Principles
- PC1: One home per rule: the list of reasons lives in the project's rules file; the pack only says "follow the project's list" and never copies cccc's list.

### Assumptions
- AS1: In cccc, every pull-request run builds the Docker images without deploying, and a push to `main` builds and deploys dev (`.github/workflows/ci-np-*-dev.yml` triggers on both; checked 2026-10-09).
- AS2: Most cccc tasks can order their phases so each phase commit leaves dev usable, so reason 3 stays rare.

### Unknowns
- UK1: Whether live cccc sessions pick `main` for a task with no listed reason and a worktree for a task with one (the Goal's real check; needs the owner's next tasks of each kind).

## Plan
<empty: filled by up:uplan; gains ### Rollout / ### Rollback when the change ships to a live system>

## Verify
<empty: filled by up:uverify>

## Code smells
<empty: `- <file:line>: <one-line smell>` lines passed while exploring and left unfixed (out of scope, non-trivial); deleted if none>

## Conclusion
<empty: filled by up:ureview; after done/shipped grows dated ### Follow-up: <date> / ### Scope change: <date> entries and ### Deferred scope-parking>
