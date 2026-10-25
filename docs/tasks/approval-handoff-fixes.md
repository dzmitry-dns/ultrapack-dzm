# Approval and handoff fixes

**Status:** verifying
**Branch:** main
**Goal:** The six owner-facing failures found in the 2026-10-24 audit of cccc sessions are closed by pack text the agent cannot misread: (1) only a yes to a question naming the plan counts as plan approval; (2) the pack offers the handoff itself and ends with whether the session can be closed; (3) the task file opens with a short owner summary that resume prints first, and (3a) the resume prompt loads `/up:make`; (4) `/up:make` assesses value before it creates a task file or branch; (5) a task-file commit is preceded by a mechanical Cyrillic check; (6) `up:uverify` asks before running more than the plan states. `/up:make` resume and existing commands keep working. Confirming it needs live cccc runs (validating).

## Design

Owner's ask (2026-10-24, translated): study upstream and the last one to two weeks of sessions, say what can or should be improved, propose changes. On 2026-10-25 he took items 1-6 of the proposal in full, as one task. Evidence: a 2026-10-24 keyword audit of 148 cccc main sessions and 14 worktree sessions (subagent notes, not full reads), plus the incident checks below run in this session.

Seven fixes (six approved by the owner, 3a added after the design review), each a rule with one home that other files point to:

1. **What counts as approval.** Incident: cccc session 3c517160, 2026-10-21. At 07:33 the owner picked a design option and added "do everything else short of production". The agent took that as plan approval, committed, and created a worktree. At 07:42 the owner called it a critical breach. Cause: the merge has a definition of a valid yes (`plugins/up/commands/make.md:176`), the plan gate has none (`make.md:135`). Fix: a paragraph in `plugins/up/skills/uplan/review-before-code.md` → Approval line, which both the design and the plan approval requests already follow. Approval of the `## Design` or the `## Plan` is a yes in reply to that approval request (`up:udesign` / `up:uplan` step 12). It never comes from a choice between options, "continue" or "do the rest", a yes that answers another question in the same message (an option pick, a Jira draft, a Scope flag), an approval of the other one, or a yes given before the request was shown. The request's own yes still counts when the `up:ujira` draft (`make.md:133`) or a Scope flag (`review-before-code.md:61`) rides the same message. An unclear reply gets one question naming `## Design` or `## Plan`. Until approval: no Status move past it, no branch, no worktree, no code commit. Exceptions, unchanged: the plan-approval gate lets a Small plan proceed without a yes (`make.md:135`), and a stage skipped at step 4 has no request; a manual or resumed `up:uplan` always waits. `make.md:135` points there.
2. **A ready handoff at every wait (owner chose option A, 2026-10-25).** The owner asked for a handoff by hand 12+ times and asked whether the session can be closed several times. Auto Handoff appends already exist (`make.md:218`); what is missing is the resume line and the close answer. Fix: a new `_principles.md` section. When the flow waits for the owner and a task file exists, the message ends with the resume prompt of `/up:summary` step 4 and one line `Session: can close` or `Session: wait for <job still running in the background>`. The waits are: the design approval request, the plan approval request, `/up:make` step 12, and any question that stops the flow. At the two approval requests and at step 12, `/up:summary` steps 1-3 run first when decisions were taken since the latest Handoff block, so the prompt points at a current file. At other questions (design dialogue, blockers) only the prompt and a Session line print, no append and no commit; when decisions were taken in chat since the latest Handoff block, that Session line reads `Session: run /up:summary before closing`, never `can close`. `make.md:218` "Print no prompt at these points" gets the exception for these waits, and its Status-transition append is skipped when the latest Handoff block was written in the same turn. Pointers: `udesign/SKILL.md:42`, `uplan/SKILL.md:55`, `make.md` step 12, `_principles.md` → Questions to the owner and How to use. No new pause, no counting. The `/up:summary` description gains the owner's trigger words (handoff, hands-off, the voice spelling "khendzov", closing the session) and the command ends with the same Session line. The advisory checkpoint (`make.md:216`) stays as it is.
3. **Owner summary at the top of the task file.** Owner asked "I am lost / what is the status" 8+ times. Fix: the `/up:make` template gains `## Owner summary` right under the header: three bullets `Done:`, `Left:`, `Owner decides:`, plain English, no IDs. `/up:summary` step 3 (which the auto appends also run) rewrites it in place at every Handoff append; an older file without the section gets it inserted under the header at its first append. On resume (`make.md:27`) the first chat message opens with it in the owner's chat language, before the `Owner has not seen` results. The Status enum list in step 2 gains a plain meaning per value, and a Status value shown in chat always carries that meaning (for `validating`: merged or finished, waiting for a real-world check).
3a. **The resume prompt loads `/up:make`** (added after the 2026-10-25 design review). Probe 2026-10-25 over 14 days of cccc sessions: 39 sessions contain the resume prompt, 15 of them invoked `/up:make`, 29 invoked any `up:` skill, 10 none. So step 2's resume rules (Handoff read, `Owner has not seen`, worktree entry, and fix 3) are skipped in most resumed sessions. Fix: `/up:summary` step 4 prints `/up:make docs/tasks/<slug>.md` (the worktree path form likewise) instead of the Russian "continue" line; `/up:make` step 1 treats an argument that is an existing task-file path as that slug, so step 2 settles as Exists for that file; the Multiple in-flight bullet (`make.md:38`) does not fire when the argument named a file. `README.md:102` and the `summary.md:2` description move to the new prompt. The old prompt still works as before (no break): the agent reads the file without the pack's resume rules, as today.
4. **Value check before the task file.** By the audit, 5 of 7 `/up:make` runs opened with "is this worth doing", and 2 ended "close it, don't do it". Fix: in step 2's "Doesn't exist" branch, before step 3. When the ask names work without telling the agent to build it (a bare ticket id or link, "look at", "is it worth", "explain"), the agent answers in chat first: what it is, what it gives, rough cost, a recommendation. It creates no task file, branch, or Jira write. Step 3 runs on the owner's go. An ask that tells it to build ("fix", "do", "implement") is the go. Step numbers do not change.
5. **Agent-run Cyrillic check before a task-file commit.** Incident: cccc session 8c30c521, 2026-10-21, the agent pasted the owner's Russian quotes into a task file. The global rule existed and did not hold. Fix: `_principles.md` → Commits. Before any commit that includes a task file, grep the lines that commit adds to it (the staged diff) for the Cyrillic character range. Every hit is translated to English before the commit; old lines are left as they are. The only exception: a backticked literal that a code or pack file contains verbatim. Pointers: `/up:summary` step 3 (it commits the file that carries the owner's chat decisions, `summary.md:48`) and `_principles.md` → How to use → Commits. It is a grep the agent runs because the text says so, not a hook: the pack's `plugins/up/hooks/` is empty and the repo is doc-only. Probe 2026-10-25: the BSD grep on the owner's Mac finds the range, with hits in 6 old task files of this repo.
6. **Costly runs cap.** Incident: cccc session 08931744, 2026-10-13. The plan allowed one full eval run, the agent ran three (about $15 and an hour) in a "fix the prompt, rerun" loop with no stage skill invoked in that session. So the cap cannot live in `up:uverify` only. Fix: a new `_principles.md` section, pointed to from `up:uexecute`, `up:uverify` Phase 5, and `up:uplan`'s test strategy. A costly run is one the agent starts by command that costs money (paid API or model calls, cloud jobs) or takes over 10 minutes; CI that a push triggers is not counted. The plan names each costly run and how many. Each run beyond that count, or not in the plan, needs a yes to a question that names the run, its cost, and why one more run should change the result. Reach: `/up:make` Rules point to it as well, so a session resumed by the 3a prompt reads it. A bare session that loads no pack text is out of reach of any pack fix; the consumer project's `CLAUDE.md` line is a cccc follow-up, not claimed closed here.

Backwards compatibility: no break. A task file without `## Owner summary` resumes as on 0.3.53. Step numbers and every existing cross-reference keep their meaning. The approval and cost rules only add questions.
TDD: no (reason: doc-only pack, no deterministic code; repo CLAUDE.md "no unit tests").
Reviewed before code: 2 rounds, 8 Critical/Important fixed, 0 rejected, 2026-10-25

### Prior art
- `docs/tasks/session-audit-fixes.md:11-12`: the Closing line and the Approval line came from the previous audit; fixes 1 and 2 extend those homes instead of adding parallel ones.
- `docs/tasks/session-hygiene.md:26`: the checkpoint never pauses (IV2 there); option A keeps that decision.
- `docs/tasks/handoff-prompt.md:22`: resume reads the latest Handoff block first; fix 3 adds the Owner summary in front of it.
- `docs/tasks/branch-by-reason.md:184` and `docs/tasks/session-audit-2026-10-04.md:9`: owner quotes in Russian inside task files, the pattern fix 5 stops.

### Invariants
- IV1: `/up:make` step numbers 1-12 and every existing pointer to them keep their meaning.
- IV2: A task file without `## Owner summary` resumes exactly as on 0.3.53.
- IV3: Each new rule has one home; every other file only points to it.
- IV4: No new pause: the handoff and Session line ride only waits that already exist (owner, 2026-10-25, option A).
- IV5: This task file and every pack file this task writes outside quoted trigger words hold no Cyrillic.

### Assumptions
- AS1: The agent can tell which background jobs it started and has not seen finish, from the notifications in its own context.
- AS2: The audit counts (12+ handoff asks, 5 of 7 value questions, 8+ status questions) come from keyword search, not full reads; no fix depends on the exact numbers.

### Unknowns
- UK1: Whether the Owner summary and the Closing line repeat each other so much that the owner reads one and skips the other; answered by live cccc runs.
- UK2: Whether `/up:summary`'s "one append, no other side effects" rule (`plugins/up/commands/summary.md:81`) needs only a one-clause change for the in-place Owner summary rewrite; the plan decides.

## Plan

Approach: one phase per fix, each adding the rule to its one home and pointers elsewhere (IV3). Line numbers are as of 017f71a; `make.md` shifts as phases add text, so later phases anchor on the quoted text.
Reviewed before code: 1 rounds, 1 Critical/Important fixed, 0 rejected, 2026-10-25, round 2: not needed

### PH1: Approval definition (fix 1)

- **1.1** `plugins/up/skills/uplan/review-before-code.md:84-96` (modify), `## Approval line`
  - New paragraph after item 3, before the "single home" line: what counts as approval of `## Design` / `## Plan`, what never counts, the riders that still count (`up:ujira` draft, Scope flag), one clarifying question naming the section, what is blocked until approval, the two exceptions (Small gate of `make.md` step 7, a stage skipped at step 4).
  - "single home" line now covers both the request format and the approval definition.
- **1.2** `plugins/up/commands/make.md:135` (modify), Plan-approval gate: one clause, "approval is defined in `review-before-code.md` → Approval line".
- Respects: IV1, IV3, IV4
- Commit: `feat(up): define what counts as design and plan approval`

### PH2: Costly runs and the Cyrillic check (fixes 5, 6)

- **2.1** `plugins/up/skills/_principles.md:18-20` (modify), `## Commits`: before a commit that includes a task file, run the check below on it; translate every hit on an added line to English; old lines stay; exception: a backticked literal a code or pack file contains verbatim.
- **2.2** `plugins/up/skills/_principles.md` (modify), new `## Costly runs` section after `## Questions to the owner`: definition (money, or over 10 minutes; push-triggered CI excluded), the plan names each run and its count, each extra run needs a yes to a question naming the run, its cost, and why one more run changes the result.
- **2.3** `plugins/up/skills/_principles.md:49-57` (modify), `## How to use`: Commits bullet adds `/up:summary`; new Costly runs bullet naming `up:uplan`, `up:uexecute`, `up:uverify`, `/up:make`.
- **2.4** Pointers, one line each:
  - `plugins/up/skills/uplan/SKILL.md:77`: Test strategy bullet adds "and each costly run with its count".
  - `plugins/up/skills/uexecute/SKILL.md:193-199`: new "When to stop and ask" bullet.
  - `plugins/up/skills/uverify/SKILL.md:182-187`: new Phase 5 bullet before the loop-back bullets.
  - `plugins/up/commands/make.md:228-238`: new Rules bullet.
  - `plugins/up/commands/summary.md:48`: the commit runs the `_principles.md` → Commits check first.
- Respects: IV3, IV5
- Commit: `feat(up): cap costly runs and check task-file commits for Cyrillic`

Check command, written with byte escapes so the pack and task files stay ASCII (IV5). Probed 2026-10-25 on the owner's Mac: it hits Cyrillic, not Latin accents, and dippy allows it:

```bash
git diff --cached -U0 -- <task file> | grep -n $'^+.*[\xd0\x80-\xd3\xbf]'
```

### PH3: Handoff at every wait (fix 2)

- **3.1** `plugins/up/skills/_principles.md` (modify), new `## Handoff at a wait` section after `## Closing line`: the four waits; at the two approval requests and `/up:make` step 12, `/up:summary` steps 1-3 run first when decisions were taken since the latest Handoff block; the message ends with the `/up:summary` step 4 prompt and the line `Session: can close` / `Session: wait for <job>`; at other questions only prompt plus Session line, and `Session: run /up:summary before closing` when chat decisions are unrecorded. Relies on AS1.
- **3.2** `_principles.md` → `## Questions to the owner` (line 36) gets one pointer clause; `## How to use` gets a bullet.
- **3.3** `plugins/up/skills/udesign/SKILL.md:42` and `plugins/up/skills/uplan/SKILL.md:55`: step 12 adds "end with `_principles.md` → Handoff at a wait".
- **3.4** `plugins/up/commands/make.md` step 12 (line 170): same pointer after the Closing line sentence.
- **3.5** `plugins/up/commands/make.md:218`: "Print no prompt at these points" gains "except at the waits of `_principles.md` → Handoff at a wait"; the Status-transition append is skipped when the latest Handoff block was written in the same turn.
- **3.6** `plugins/up/commands/summary.md:2` description adds the trigger words (handoff, hands-off, the voice spelling in Russian, closing the session; the Russian word is the IV5 exception); step 4 (line 60) and the "No active task file" path (line 76) end with the Session line after the Closing line.
- Respects: IV3, IV4 (no new pause, no counting)
- Commit: `feat(up): end every owner wait with the resume prompt and a Session line`

### PH4: Owner summary and the /up:make resume prompt (fixes 3, 3a)

- **4.1** `plugins/up/commands/make.md:42-85` template (modify): `## Owner summary` right after the header, three bullets `Done:`, `Left:`, `Owner decides:`, plain English, no IDs. `plugins/up/agents/plan-reviewer.md:26` adds it to the sections the reviewer never reads (session state).
- **4.2** `make.md:23`: each Status enum value gets a plain meaning (`validating`: merged or finished, waiting for a real-world check); a Status shown in chat carries its meaning.
- **4.3** `make.md:27` Exists branch: when the file has `## Owner summary`, the first chat message opens with it in the owner's chat language, before the `Owner has not seen` results; a file without it resumes as before (IV2).
- **4.4** `make.md:9-11` Arguments and `make.md:17` step 1: an argument that is an existing task-file path is that task; step 2 settles as Exists. `make.md:38` Multiple in-flight: does not fire when the argument named a file.
- **4.5** `plugins/up/commands/summary.md:30-48` step 3: rewrite `## Owner summary` in place at each append, insert it under the header when absent. `summary.md:7` and `summary.md:81` Rules: "one append" / "one side effect" become "one append plus the Owner summary rewrite" (resolves UK2: one clause each).
- **4.6** `summary.md:50-58` step 4: prompt becomes `/up:make docs/tasks/<slug>.md` (worktree form `/up:make <worktree>/docs/tasks/<slug>.md`); `summary.md:2` description and `README.md:102` follow.
- Respects: IV1, IV2, IV5
- Commit: `feat(up): owner summary at the top of the task file, resume prompt loads /up:make`

### PH5: Value check before the task file (fix 4)

- **5.1** `plugins/up/commands/make.md:37` "Doesn't exist" (modify): an ask that names work without telling the agent to build it gets a chat answer first (what it is, what it gives, rough cost, recommendation), no task file, branch or Jira write; step 3 runs on the owner's go; a build verb is the go.
- Respects: IV1 (step numbers unchanged); relies on AS2 only for motivation, the rule holds without the counts
- Commit: `feat(up): assess value before creating a task file`

### PH6: Version

- **6.1** `plugins/up/.claude-plugin/plugin.json:3`: 0.3.53 → 0.3.54.
- Commit: `chore(up): 0.3.54`

### Test strategy
none: doc-only pack (repo `CLAUDE.md`). `up:uverify` checks by grep: each new rule has one home and its pointers resolve (IV3), the PH2 check command finds no Cyrillic in this task file and none in changed pack files outside the PH3.6 trigger word (IV5), and an old task file without `## Owner summary` reads unchanged under the new step 2 (IV2).

### Risks
- RK1: `make.md` grows by about ten lines and every stage reads it; each addition is one clause or a pointer, and verify measures the line count against 242.
- RK2: Owner summary and Closing line may repeat each other (UK1); left to live cccc runs, Status stays `validating`.

### Rollout
Push to `main`, then `claude plugin update up@ultrapack`; a running session keeps the version it loaded at start, so the first live check is a new cccc session.

### Rollback
`git revert` the phase commits and bump the patch again; no data or state outside the repo.

## Verify

**Result:** passed

Happy-path:
- CK1 (3a): `/up:make <worktree>/docs/tasks/<slug>.md` and an epic-child path reach step 2 Exists without the Multiple in-flight question: held (step 1, Arguments, `make.md:38` read together)
- CK2 (fix 2): an approval request followed by the Status-transition append, and step 12 right after the `validating` append, write no duplicate Handoff block: held (same-turn skip at `make.md:223`, "decisions since the latest block" in `_principles.md` → Handoff at a wait)

Negative:
- CK3 (fix 1): "do the rest" after an option pick, or a yes to a Jira draft alone, reads as approval: held, both named as never counting
- CK4 (fix 4): an existing task-file path as the argument falls into the value check: held, it settles as Exists before "Doesn't exist" is reached
- CK10 (fix 5): the check command misses added Cyrillic or hits old lines or Latin accents: held, scratch repo with an old Cyrillic line, a staged `cafe` with accent, and a staged Cyrillic line hit only the last

Invariants / assumptions:
- CK5 (IV1): step headings 1-12 in `make.md` keep numbers and names: held
- CK6 (IV2): a file without `## Owner summary` resumes as before: held, `make.md:27` reads it only when present
- CK7 (IV3): one home each for Approval, Handoff at a wait, Costly runs; rule text not restated elsewhere: held
- CK8 (IV4): new text adds a pause: held, the only new "pause" word is "This adds no pause"
- CK9 (IV5): Cyrillic on added lines outside the trigger word: held, one hit (`summary.md:2` trigger word), task file 0
- CK11: old prompt text or old "one side effect" wording left in pack or README: held, none
- CK12: `## Owner summary` read as Design by a reviewer: held, `plan-reviewer.md:26` excludes it; `up:requirements-reviewer` never sees the task file
- CK13 (AS1): the agent knows its running background jobs: deferred, needs live cccc runs

Smoke: `claude plugin validate plugins/up` and `claude plugin validate .` → passed (two marketplace warnings predate this task)

Goal: proxy only; the smoke checks the plugin loads, not agent behavior. Live cccc sessions on 0.3.54 must show each of the seven fixes.

## Code smells
<empty>

## Conclusion
<empty: filled by up:ureview>

### Handoff: 2026-10-25
- Position: design written, two Fable design reviews applied, waiting for the owner's design approval; branch: main; committed: b9f8b92; uncommitted: none
- Decided: handoff rides only existing waits (option A), because the owner chose A over a size-triggered pause on 2026-10-25
- Decided: added 3a (resume prompt invokes `/up:make`), because a 2026-10-25 probe found 15 of 39 resumed cccc sessions loaded `/up:make`; owner has not approved 3a yet
- Open: owner approval of the Design, including 3a
- Owner has not seen: none
- First action: on approval, Status to planning and run `up:uplan`

### Handoff: 2026-10-25 (design approved)
- Position: owner approved the Design including 3a on 2026-10-25; Status planning; branch: main; uncommitted: none
- Decided: 3a is in scope, because the owner answered yes to the design approval request that named it
- Open: the Plan, then the owner's plan approval
- Owner has not seen: none
- First action: run `up:uplan`

### Handoff: 2026-10-25 (plan approved)
- Position: owner approved the Plan on 2026-10-25; Status executing; branch: main (no project rule asks for a branch); committed: 683dba9; uncommitted: none
- Open: none
- Owner has not seen: none
- First action: run `up:uexecute` from PH1

### Handoff: 2026-10-25 (executed)
- Position: PH1-PH6 committed (543e761, 92b76b0, a01f407, 2541018, 0d74b6d, 38b7a8d); Status verifying; branch: main; not pushed; uncommitted: none
- Decided: the Cyrillic check uses byte escapes, because the first plan draft wrote literal characters and the plan reviewer caught it
- Open: none
- Owner has not seen: none
- First action: run `up:uverify`
