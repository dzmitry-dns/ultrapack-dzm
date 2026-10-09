# Branch only for a listed reason, worktree only for a long-lived branch

**Status:** verifying
**Branch:** main
**Goal:** A task started with `/up:make` runs on the current branch (main) unless a listed reason for a branch applies or the owner asks for one; a task that branches uses a plain branch in the current checkout, and a worktree only when the project's rules call for one. In cccc that gives three observable outcomes: a task with no listed reason commits to `main`; a short branched task uses a plain branch in `cccc-monorepo` and returns the checkout to `main` before the session ends; a long-lived branch (or a crowded checkout) gets the worktree flow unchanged. Confirming it needs live cccc `/up:make` runs of each kind (owner's environment).

## Design

Owner's ask (2026-10-08): starting sessions in a worktree is slow and awkward; find the rule that maps task size to worktree use and improve it. Scope approved 2026-10-09. Owner's direction in review (2026-10-09): "workflow [worktree] нужны только для долгоиграющих веток. Все остальное можно пилить просто на бренчах." Owner's answer 2026-10-09: a task with no listed reason goes to `main` (not a plain branch); Design approved the same day.

Why it happens today: the pack has no size rule for branches. Size (`make.md` step 4) only decides which stages are skipped, and every task defaults to Medium. Step 6 suggests a branch for "complex / long-running / touches many files", which fits most Medium tasks. In cccc, `workflow.md` then puts every branch in a worktree, with a 6-step entry and a 6-step exit. Result in cccc: of the 7 tasks added 2026-10-05..08, 4 ran in a worktree; across all task files about half record `main` and the rest used feature branches in the shared checkout. The worktree rule itself (cccc `25a00b66a`, 2026-10-06) was written for concurrency, not size: "several sessions and the owner work there at once" (`workflow.md:42`). The worktree flow took 3 pack versions (0.3.49-0.3.51) of fixes in 3 days.

The ideal: two separate questions, each answered by a reason someone can name. First, does the task need a branch at all? The default is no; the reasons live in the project's rules, because only the project knows what its `main` triggers (in cccc a push to `main` deploys dev). Second, does the branch need its own folder? The default is no; a worktree is for a branch that outlives the session, or for a checkout other sessions are using right now. The worktree machinery of 0.3.51 stays as it is; it runs far less often.

Decisions:
- **D1, pack `make.md` step 6:** the step becomes two questions.
  - *Branch?* Stay on the current branch unless (a) the project's rules list reasons for a branch and one applies, (b) the owner asks for a branch, or (c) the pack's own rule fires: a fix to a merged change whose task is still `validating` (already in make.md Rules). With no project list, the agent may propose a branch only by naming a concrete reason, and asks.
  - *Worktree?* A branch is a plain branch in the current checkout, unless the project's rules say when a branch needs a worktree and that applies, or the owner asks. A project's worktree convention then decides *how* the worktree is made (0.3.51 entry order, unchanged); it no longer decides *whether*.
  - Timing: step 6 runs once the Plan is approved (Trivial has no Plan: right after step 4), because both answers can depend on the plan (cccc branch reason 3; the number of phases decides whether the branch outlives the session). The step keeps its number 6, since other files cite step numbers; step 6 opens with "runs after step 7's approval" and step 7 ends by pointing to it. Design and Plan commits before the decision go to the current branch.
  - `uexecute`'s "Branch / worktree correctness" and make.md's Rules line ("Never create a worktree without confirming...") say the same in one clause each.
- **D2, step 2 resume for a plain branch:** a task whose `**Branch:**` names a branch that is not merged and whose header has no `**Worktree:**` path is read from the local branch first (`git show <branch>:<task file path>`; fetch only when no local branch exists), because the copy on the current branch stops at the switch. Step 2 also guards a shared checkout: when `git branch --show-current` is neither the default branch nor this task's branch, stop and ask before any commit (another task's plain branch was left checked out). Same wording pass: step 2 settles a worktree only for a `**Worktree:**` line that names a path (cccc's template writes `**Worktree:** none`, 176 files today, `task-files.md:20`); step 3's "placeholder until step 5" points at step 6.
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
  A plain branch, entry: write `**Branch:** <branch>` in the task file header, commit and push it on `main` (so a resume from `main` knows the branch, D2), then `git switch -c <branch>` from the up-to-date `main`. Work: phase commits and pushes to the branch, the PR per "Commit and push" (auto-merge rules unchanged). Exit: two places end with `git switch main && git pull --ff-only`: make.md step 12 (Finish) and every `/up:summary` Handoff append, so a session that hands off leaves the shared checkout on `main`. A session stopped without either leaves the branch checked out; the next `/up:make` catches it by D2's guard. When `git switch main` refuses (someone's uncommitted edits conflict with `main`), never stash or discard them: leave the checkout as it is and name the files in the report. The local branch is deleted (`git branch -D`) once the PR is merged, by this session or the next one that sees it merged. A plain branch whose work turns out to outlive the session: commit, push, switch back to `main`; the next session continues it in a worktree made from the existing branch (`git worktree add <path> <branch>`) and records `Worktree reason: 1`.
  The worktree subsection's first sentence changes from "Branch work goes into a git worktree" to point at this list.

Approaches considered:
- A (chosen, owner's direction): default `main`; a plain branch for a listed reason; a worktree only for a long-lived branch or a crowded checkout. Prose in 2 pack files plus the version bump, 1 cccc file; every 0.3.51 worktree rule untouched. Risk: "expected to outlive the session" is a forecast; a wrong forecast is recovered by the switch-back rule in D5.
- B: default `main`, every branch in a worktree (this file's previous version). Rejected by the owner: keeps the worktree cost for short branches.
- C: map size to branch (Large → branch). Rejected: size does not predict the need; CATS-1776 was a modest change that needed the pull-request Docker check.

Out of scope (deferred after the 2026-10-09 self-review): task file kept only on the branch; Claude Code's built-in worktrees with `.worktreeinclude` (copies `.env` instead of linking; needs a probe run); deleting the disabled `git-worktrees` skill (owner's 2026-09 decision: disable, not delete). Known side effect left as is: the merged-worktree sweep runs only when a worktree is created or its task resumes, so with fewer worktrees a merged one stays on disk longer; it costs disk space only.

Backwards compatibility: no break for running tasks: a task whose header names a worktree path resumes and exits as in 0.3.51. Behavior change for new tasks in any project without a reasons list: the agent no longer suggests a branch from size alone, and a branch no longer implies a worktree. Fork-only change (opinionated workflow policy), not sent upstream.
TDD: no (doc-only plugin; verification is install-and-invoke)
Reviewed before code: 3 rounds (round 3 at owner request), 6 Critical/Important fixed, 0 rejected, 2026-10-09

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
- AS1: In cccc, every pull-request run builds the Docker images without deploying, and a push to `main` builds and deploys dev (`.github/workflows/ci-np-*-dev.yml` triggers on both; checked 2026-10-09). Known gap: the cron-api PR path filter (`ci-np-cron-api-next-dev.yml:15-19`) does not list its own workflow file, so a PR changing only that file runs no cron build.
- AS2: Most cccc tasks can order their phases so each phase commit leaves dev usable, so branch reason 3 stays rare.
- AS3: Most branched cccc tasks finish within one session, with the PR merged by auto-merge, so worktree reason 1 stays rare.

### Unknowns
- UK1: Whether live cccc sessions pick `main`, a plain branch and a worktree in the cases above (the Goal's real check; needs the owner's next tasks).
- UK2: Whether a session already running on `main` in the shared checkout notices a branch switch made by another session after it started. D2's guard runs only at `/up:make` start and `uexecute` checks only before code writes; task-file commits in make.md and `/up:summary` have no branch check. The plan decides whether one more check is worth it.

## Plan

Approach: rewrite pack `make.md` step 6 as the two questions and move it after plan approval, teach step 2 to resume a plain branch, align `uexecute`, `summary.md` and the Rules line in one clause each (PH1, pack 0.3.52); then give cccc `workflow.md` the reason lists, the plain-branch flow and a commit-time branch check (PH2). PH2 resolves UK2: a session on `main` in the shared checkout re-checks the branch before every commit, which covers task-file commits that step 2's guard and `uexecute` never see.
Reviewed before code: 1 rounds, 3 Critical/Important fixed, 0 rejected, 2026-10-09, round 2: not needed

### PH1: pack 0.3.52

- **1.1** `plugins/up/commands/make.md:107-122` (modify), step 6 "Branch decision", D1 + D3
  - Opening line: runs at the end of step 7, once the Plan is approved; Trivial (no Plan) runs it right after step 4; Design and Plan commits before it go to the current branch. Heading and number stay 6.
  - Replace the two size bullets (`:111-112`) and "Otherwise always confirm with the user" (`:120`) with **Branch?**: stay on the current branch unless (a) the project's rules list reasons for a branch and one applies, (b) the user asks, (c) a fix to a merged change whose task is still `validating` (Rules). No project list: propose a branch only by naming a concrete reason, and ask.
  - **Worktree?**: a branch is a plain branch in the current checkout (`git switch -c <branch>`) unless the project's rules say when a branch needs a worktree and that applies, or the user asks. Then the project's worktree convention runs without asking (IV3) and decides how; `**Worktree:** <path>` goes in the header. A worktree the user asks for in a project with no convention: suggest `/up:git-worktrees` (kept from `:120`).
  - D3 record: `Branch reason: <reason, by name>` in `## Design` (after a `Skipped` line), plus `Worktree reason: <reason>`; nothing for a default.
  - Plain-branch entry (generic, D2 needs it): write `**Branch:**`, commit the task file on the current branch, then switch. Replaces "Either way..." (`:122`).
  - The env-link paragraph (`:116`) and "Order of entry" (`:118`) stay word for word under the worktree case (IV1).
- **1.2** `plugins/up/commands/make.md:126` (modify), step 7: after "Status → `executing`." add "Then run step 6, before step 8."
- **1.3** `plugins/up/commands/make.md:25` (modify), step 2, D2
  - The worktree branch of the resume fires only for a `**Worktree:**` line that names a path (`none` is no worktree).
  - New sentence: no worktree path, `**Branch:**` is not the default branch, and no merged PR for it (`gh pr list --head <branch> --state merged`) → read Status and the Handoff from the local branch, `git show <branch>:<task file path>` (a plain branch lives in this checkout and may not be pushed yet; `git fetch origin <branch>` first only when no local branch exists). That read decides how to continue per the project's rules (switch, or a worktree when they call for one); after a switch the working copy is the file.
  - Guard, on both the "Exists" path and before step 3's first commit: `git branch --show-current` is neither the default branch nor this task's `**Branch:**` → stop and ask before any commit.
- **1.4** `plugins/up/commands/make.md:40` (modify), step 3: "placeholder until step 5" → "placeholder until step 6".
- **1.5** `plugins/up/commands/make.md:222` (modify), Rules: "Never create a branch or a worktree without a reason step 6 accepts (a project rule that applies, the user's request, or the `validating` rule above)." The `validating` sentence at `:220` stays (IV2).
- **1.6** `plugins/up/skills/uexecute/SKILL.md:41` (modify), "Branch / worktree correctness": the checkout is the main repo or the worktree named by a `**Worktree:**` path; branch and worktree are decided by `/up:make` step 6, never here. Drops the convention/confirm sentence.
- **1.7** `plugins/up/commands/summary.md:58` (modify): the prompt names the checkout path only when the task file has a `**Worktree:**` path (a plain branch resumes from the shared checkout through step 2). `summary.md:81` "One append, no other side effects" gains "plus the checkout step the project's rules require after a handoff (for example returning a shared checkout to its default branch)", so cccc's switch-back (2.3) does not contradict the command (IV4).
- **1.8** `plugins/up/.claude-plugin/plugin.json:3`: 0.3.51 → 0.3.52.
- Respects: IV1, IV2, IV3, PC1 (no cccc reason list in the pack).
- Commit: `feat(make): branch only for a listed reason, plain branch before worktree` (ultrapack `main`, push).

### PH2: cccc `.claude/rules/workflow.md`

- **2.1** `.claude/rules/workflow.md:34` (modify), "Commit and push": the shared-checkout bullet gains "Before every commit there, `git branch --show-current` must be `main` or this task's `**Branch:**`; anything else stops the commit and goes to the owner (another session switched the folder)." Resolves UK2.
- **2.2** `.claude/rules/workflow.md:36-39` (insert before `:40`): new section `## When to branch`, D4's five reasons, item 2 pointing at `:31`, plus the D3 record lines.
- **2.3** `.claude/rules/workflow.md:40-42` (modify): heading → `## Feature branches: plain branch or worktree`; `:42` becomes the D5 lead: the three worktree reasons, then the plain-branch entry/work/exit paragraph (switch back at make step 12 and every `/up:summary`, never stash on a refused switch, `git branch -D` after merge, continue in a worktree from the existing branch with `Worktree reason: 1`; inside that worktree, first add the same `**Worktree:** <path>` line to the branch's copy and commit it, because exit step 4 copies the branch's file over `main`'s and would otherwise drop the line while the worktree still exists). The existing worktree bullets `:44-57` stay unchanged, introduced by "A worktree branch:" (IV1, IV4).
- Respects: IV2, IV4, AS1.
- Commit: `docs(rules): branch only for a listed reason, worktree only for long-lived branches` (cccc `main`, by path, after the `git log origin/main..HEAD` check; push).

### Test strategy
none (doc-only; Verify reads the edited steps end to end for each of the Goal's three outcomes; the live cccc runs check UK1, AS2 and AS3 at `validating`).

### Order & dependencies
PH1 before PH2: cccc text cites the pack's step 6 order. A cccc session still on 0.3.51 already follows a project branch convention without asking (`make.md:114`), so the window between the two pushes and the owner's plugin update breaks nothing.

### Risks
- RK1: a session on `main` in `cccc-monorepo` that commits right after another session's `git switch -c` lands its commit on that branch; 2.1's check catches it at commit time, and D5's crowded-checkout reason lowers how often the switch happens at all.

### Rollout
PH1 push, owner installs 0.3.52 the usual way (sessions keep the version loaded at start); PH2 push goes live for every new cccc session at once.

### Rollback
Revert the PH2 commit in cccc and the PH1 commit in ultrapack; no data touched.

## Verify
<empty: filled by up:uverify>

## Code smells
- cccc `.github/workflows/ci-np-cron-api-next-dev.yml:15-19`: the PR path filter does not list its own workflow file, so a PR changing only that file runs no cron build (AS1).

## Conclusion
<empty: filled by up:ureview; after done/shipped grows dated ### Follow-up: <date> / ### Scope change: <date> entries and ### Deferred scope-parking>

### Deviations from plan
- PH2 commit scope `docs(agents)` instead of `docs(rules)`: cccc commitlint allows only `main-app, job-api, cron-api, db, utils, email, scripts, env, ci, deps, agents`.

### Handoff: 2026-10-09
- Position: design, round 3 review done and applied (1 Critical, 1 Important fixed); awaiting owner approval; branch: main; uncommitted: none
- Decided: Medium size, not Small, because with Design skipped the plan point of review-before-code does not run
- Decided: worktree only for a long-lived branch or a crowded shared checkout, short branches as plain branches in cccc-monorepo, because the owner said so in review on 2026-10-09 (Design quotes it)
- Decided: plain-branch guard (crowded checkout → worktree) added on my judgment; the owner was told he can drop it
- Open: default for a task with no listed reason: `main` (current Design) or a plain branch (one reading of the owner's "все остальное можно пилить просто на бренчах")
- Owner has not seen: none (round 3 results reported in chat 2026-10-09)
- First action: get the owner's answer to Open and his Design approval, then run up:uplan

### Handoff: 2026-10-09
- Position: planning, Design approved; branch: main; uncommitted: none
- Decided: a task with no listed reason goes to `main`, not a plain branch, because the owner chose it on 2026-10-09 (recorded in Design)
- Decided: this task itself runs on `main`, because the pack repo has no branch reasons and it is doc-only
- Owner has not seen: none
- First action: run up:uplan

### Handoff: 2026-10-09
- Position: executing, plan approved 2026-10-09, PH1 next; branch: main; uncommitted: none
- First action: run up:uexecute from PH1

### Handoff: 2026-10-09
- Position: verifying; PH1 ultrapack `0f5ad58` (0.3.52, pushed), PH2 cccc `55267b4e8` (pushed); branch: main; uncommitted: none
- First action: run up:uverify
