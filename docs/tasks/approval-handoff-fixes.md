# Approval and handoff fixes

**Status:** design
**Branch:** main
**Goal:** The six owner-facing failures found in the 2026-10-24 audit of cccc sessions are closed by pack text the agent cannot misread: (1) only a yes to a question naming the plan counts as plan approval; (2) the pack offers the handoff itself and ends with whether the session can be closed; (3) the task file opens with a short owner summary that resume prints first, and (3a) the resume prompt loads `/up:make`; (4) `/up:make` assesses value before it creates a task file or branch; (5) a task-file commit is preceded by a mechanical Cyrillic check; (6) `up:uverify` asks before running more than the plan states. `/up:make` resume and existing commands keep working. Confirming it needs live cccc runs (validating).

## Design

Owner's ask (2026-10-24, translated): study upstream and the last one to two weeks of sessions, say what can or should be improved, propose changes. On 2026-10-25 he took items 1-6 of the proposal in full, as one task. Evidence: a 2026-10-24 keyword audit of 148 cccc main sessions and 14 worktree sessions (subagent notes, not full reads), plus the incident checks below run in this session.

Seven fixes (six approved by the owner, 3a added after the design review), each a rule with one home that other files point to:

1. **What counts as approval.** Incident: cccc session 3c517160, 2026-10-21. At 07:33 the owner picked a design option and added "do everything else short of production". The agent took that as plan approval, committed, and created a worktree. At 07:42 the owner called it a critical breach. Cause: the merge has a definition of a valid yes (`plugins/up/commands/make.md:176`), the plan gate has none (`make.md:135`). Fix: a paragraph in `plugins/up/skills/uplan/review-before-code.md` → Approval line, which both the design and the plan approval requests already follow. Approval of the `## Design` or the `## Plan` is a yes in reply to that approval request (`up:udesign` / `up:uplan` step 12). It never comes from a choice between options, "continue" or "do the rest", a yes to a message that bundles the approval request with other asks or options, an approval of the other one, or a yes given before the request was shown. An unclear reply gets one question naming `## Design` or `## Plan`. Until approval: no Status move past it, no branch, no worktree, no code commit. Exceptions, unchanged: the plan-approval gate lets a Small plan proceed without a yes (`make.md:135`), and a stage skipped at step 4 has no request; a manual or resumed `up:uplan` always waits. `make.md:135` points there.
2. **A ready handoff at every wait (owner chose option A, 2026-10-25).** The owner asked for a handoff by hand 12+ times and asked whether the session can be closed several times. Auto Handoff appends already exist (`make.md:218`); what is missing is the resume line and the close answer. Fix: a new `_principles.md` section. When the flow waits for the owner and a task file exists, the message ends with the resume prompt of `/up:summary` step 4 and one line `Session: can close` or `Session: wait for <job still running in the background>`. The waits are: the design approval request, the plan approval request, `/up:make` step 12, and any question that stops the flow. At the two approval requests and at step 12, `/up:summary` steps 1-3 run first when decisions were taken since the latest Handoff block, so the prompt points at a current file. At other questions (design dialogue, blockers) only the prompt and the Session line print: no append, no commit. `make.md:218` "Print no prompt at these points" gets the exception for these waits. Pointers: `udesign/SKILL.md:42`, `uplan/SKILL.md:55`, `make.md` step 12, `_principles.md` → Questions to the owner and How to use. No new pause, no counting. The `/up:summary` description gains the owner's trigger words (handoff, hands-off, the voice spelling "khendzov", closing the session) and the command ends with the same Session line. The advisory checkpoint (`make.md:216`) stays as it is.
3. **Owner summary at the top of the task file.** Owner asked "I am lost / what is the status" 8+ times. Fix: the `/up:make` template gains `## Owner summary` right under the header: three bullets `Done:`, `Left:`, `Owner decides:`, plain English, no IDs. `/up:summary` step 3 (which the auto appends also run) rewrites it in place at every Handoff append; an older file without the section gets it inserted under the header at its first append. On resume (`make.md:27`) the first chat message opens with it in the owner's chat language, before the `Owner has not seen` results. The Status enum list in step 2 gains a plain meaning per value, and a Status value shown in chat always carries that meaning (for `validating`: merged or finished, waiting for a real-world check).
3a. **The resume prompt loads `/up:make`** (added after the 2026-10-25 design review). Probe 2026-10-25 over 14 days of cccc sessions: 39 sessions contain the resume prompt, 15 of them invoked `/up:make`, 29 invoked any `up:` skill, 10 none. So step 2's resume rules (Handoff read, `Owner has not seen`, worktree entry, and fix 3) are skipped in most resumed sessions. Fix: `/up:summary` step 4 prints `/up:make docs/tasks/<slug>.md` (the worktree path form likewise) instead of the Russian "continue" line; `/up:make` step 1 treats an argument that is an existing task-file path as that slug, so step 2 resumes it. The old prompt still works as before (no break): the agent reads the file without the pack's resume rules, as today.
4. **Value check before the task file.** By the audit, 5 of 7 `/up:make` runs opened with "is this worth doing", and 2 ended "close it, don't do it". Fix: in step 2's "Doesn't exist" branch, before step 3. When the ask names work without telling the agent to build it (a bare ticket id or link, "look at", "is it worth", "explain"), the agent answers in chat first: what it is, what it gives, rough cost, a recommendation. It creates no task file, branch, or Jira write. Step 3 runs on the owner's go. An ask that tells it to build ("fix", "do", "implement") is the go. Step numbers do not change.
5. **Agent-run Cyrillic check before a task-file commit.** Incident: cccc session 8c30c521, 2026-10-21, the agent pasted the owner's Russian quotes into a task file. The global rule existed and did not hold. Fix: `_principles.md` → Commits. Before any commit that includes a task file, grep that file for the Cyrillic character range. Every hit is translated to English before the commit. The only exception: a backticked literal that a code or pack file contains verbatim. Pointers: `/up:summary` step 3 (it commits the file that carries the owner's chat decisions, `summary.md:48`) and `_principles.md` → How to use → Commits. It is a grep the agent runs because the text says so, not a hook: the pack's `plugins/up/hooks/` is empty and the repo is doc-only. Probe 2026-10-25: the BSD grep on the owner's Mac finds the range, with hits in 6 old task files of this repo.
6. **Costly runs cap.** Incident: cccc session 08931744, 2026-10-13. The plan allowed one full eval run, the agent ran three (about $15 and an hour) in a "fix the prompt, rerun" loop with no stage skill invoked in that session. So the cap cannot live in `up:uverify` only. Fix: a new `_principles.md` section, pointed to from `up:uexecute`, `up:uverify` Phase 5, and `up:uplan`'s test strategy. A costly run costs money (paid API or model calls, cloud jobs) or takes over 10 minutes. The plan names each costly run and how many. Each run beyond that count, or not in the plan, needs a yes to a question that names the run, its cost, and why one more run should change the result. Reach: `/up:make` Rules point to it as well, so a session resumed by the 3a prompt reads it. A bare session that loads no pack text is out of reach of any pack fix; the consumer project's `CLAUDE.md` line is a cccc follow-up, not claimed closed here.

Backwards compatibility: no break. A task file without `## Owner summary` resumes as on 0.3.53. Step numbers and every existing cross-reference keep their meaning. The approval and cost rules only add questions.
TDD: no (reason: doc-only pack, no deterministic code; repo CLAUDE.md "no unit tests").
Reviewed before code: 1 rounds, 5 Critical/Important fixed, 0 rejected, 2026-10-25, round 2: needed

### Prior art
- `docs/tasks/session-audit-fixes.md:11-12`: the Closing line and the Approval line came from the previous audit; fixes 1 and 2 extend those homes instead of adding parallel ones.
- `docs/tasks/session-hygiene.md:26`: the checkpoint never pauses (IV2 there); option A keeps that decision.
- `docs/tasks/handoff-prompt.md:22`: resume reads the latest Handoff block first; fix 3 adds the Owner summary in front of it.
- `docs/tasks/branch-by-reason.md:9` and `docs/tasks/session-audit-2026-10-04.md:9`: owner quotes in Russian inside task files, the pattern fix 5 stops.

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
<empty: filled by up:uplan>

## Verify
<empty: filled by up:uverify>

## Code smells
<empty>

## Conclusion
<empty: filled by up:ureview>
