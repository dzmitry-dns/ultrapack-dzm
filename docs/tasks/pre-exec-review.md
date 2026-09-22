# Pre-execution review: an independent reviewer on Design and Plan before any code

**Status:** planning
**Branch:** main
**Goal:** In a Medium task, whether started through `/up:make` or by asking for a plan in plain words, an independent reviewer is dispatched automatically after the plan is written and before the plan-approval pause (announced in one line, skippable by the owner); a Large task (by the design signals below) also gets one after design; Small and Trivial get none; a round repeats only while it finds an accepted Critical or Important, at most twice without asking; `/up:make` resume from every Status still works. Confirming it needs one live run on a real Medium task (cccc or this repo), beyond the diff.

## Design

Purpose: add an independent review of the Design and the Plan before any code is written, so the problems the final `up:reviewer` finds today are found while a fix costs a paragraph, not a rewrite plus a new verify and review.

Evidence (owner's ad-hoc practice in cccc-monorepo, transcripts 2026-08-30 to 2026-09-22):
- With a review before code: CATS-1722 and CATS-1710 reached the final review with no Critical or Important (CATS-1722: text fixes only, cccc `docs/tasks/job-fair-vendor-approval.md:561-563`). CATS-1723 had not reached code yet.
- Without one: 5 of 6 tasks (CATS-1715, 1635, 1620, 1653, 1703) got 1-4 Critical or Important at the final review, two of them Critical; 4 of the 6 already ran the calibrated 0.3.39 reviewer, so calibration does not explain the gap.
- Second rounds: CATS-1722 plan round 2 found 5 Medium items, one became a new phase. After execution, `up:reviewer` round 2 ran twice (CATS-1617, CATS-1691, both before 0.3.39) and both times caught a bug that round 1's own fix introduced. A `/code-review` rerun on an unchanged PR found 1 new bug once (#372) and nothing new once (#391). Round 2 on the calibrated 0.3.39 reviewer has no data yet.
- Cost: 5 (CATS-1722) and 7 (CATS-1723) review dispatches before code, 2.5-10 minutes each. Verify still broke 3 checks on CATS-1722, so the review does not replace `up:uverify`.
- The sample is small, from one feature area (Job Fair), and the owner chose which tasks got the early review.
- The owner's reviewers were general-purpose agents, one angle each: code-citation accuracy, requirement coverage, what breaks phase by phase, a simpler alternative.

Why the final review catches these late: `up:reviewer` can flag a broken plan as a `Plan finding` (`plugins/up/agents/reviewer.md:37`), but it reads the plan only once code exists, and it never sees the owner's ask (`plugins/up/agents/reviewer.md:24`). A plan that is internally consistent but misreads the code or misses part of the ask passes as aligned, or is caught after the code is written.

Chosen approach (A of three): the review belongs to the design and plan stages, not to `/up:make`.

1. Trigger points.
   - After plan: in `up:uplan`, after the scope-creep check (step 10) and before presenting the plan for approval (step 11). Runs when `## Design` in the task file holds more than the template placeholder (`<empty — filled by up:udesign>`, `make.md:54`); a placeholder or no Design (Small, Trivial) means no review. Size is read from the task file, never from a size `/up:make` holds in memory.
   - After design: in `up:udesign`, after writing and self-review (step 10), before the final approval (step 11). Runs only when the written `## Design` text shows a Large signal: a DB migration, a backwards-compat break on its `Backwards compatibility:` line, or the line `Size: Large (owner)`. A new API surface alone is not a signal: it is the normal cccc feature change, and `make.md:115` already uses it for the Small boundary. The signals are read from the task file only, so a resumed session sees the same answer.
   - What the after-design point buys: the after-plan reviewer reads the whole task file and its checks cover the Design too, so the design point saves only a plan rewrite. It stays because the owner asked for two points on Large tasks.
   - Both points fire the same way under `/up:make` and when the stage is asked for in plain words.
   - Before each dispatch, one line per `_principles.md` Dispatch narration; no pause. The owner skips with "skip pre-code review" / "без ревью до кода" in the ask or at any point; said once, it covers every remaining review point of the task, and each slot reached records `skipped by owner`. The phrase is distinct from any wording about the final review, which `make.md:191` "Never skip Review" keeps mandatory.
2. The agent: a new read-only agent in `plugins/up/agents/` (name decided at plan). Tools Glob, Grep, Read, Bash (read-only commands). `model: opus`, `effort: high`; a per-run model override works as `up:ureview` documents.
   - Receives: the task file path; the review point (design | plan); the working directory; the owner's verbatim ask when the session has it; the Jira ticket text when the task has a `**Jira:**` header and the dispatcher can read it; on round 2, the text of the round-1 findings the dispatcher rejected, without the reasons, with the instruction to re-raise one only on new evidence. Never session history or rationale.
   - Four checks: (1) code citations: every file:line, symbol, and claim about current behavior matches the code; (2) requirement coverage: every clause of the ask, ticket, and Goal maps to a design decision or plan item, or is explicitly deferred; (3) what breaks, phase by phase: deploy order, migrations, callers of changed interfaces, data already in place; (4) simpler way: a materially simpler design or plan that still meets the Goal.
   - Severity: `agents/reviewer.md` Severity is the single home. The agent adds one mapping: for a document, the named input is executing the design or plan as written, and the Trigger line names what breaks when that phase runs.
3. Rounds and processing.
   - The main session processes findings with `up:ureview` steps 2-4: restate, verify against the code, re-grade, announce the verdict per finding before editing. Only the task file changes.
   - Round 2 runs only when round 1 produced an accepted Critical or Important that changed the document. Every round is a fresh agent. At most 2 automatic rounds per review point; a third only on the owner's request.
   - After every round, one record line, updated in place: `Reviewed before code: <N> rounds, <n> Critical/Important fixed, <m> rejected, <date>`, or `Reviewed before code: skipped by owner, <date>`. Its slot is fixed: for the design point, the line right after `TDD:` in `## Design`; for the plan point, the line right after `Approach:` in `## Plan`. Never inside a subsection. A resumed stage reads the round count from it and runs another round only when the count is below 2 and the last round changed the document. The line also gives UK1 its data.
4. One home for the dispatch procedure: one shared file that `up:udesign` and `up:uplan` point to (location decided at plan). `/up:make` steps 5 and 7 gain one pointer line each; step numbers stay.
5. Adjacent changes.
   - `plugins/up/skills/ureview/SKILL.md:142` "If fixes are substantial, re-dispatch the reviewer on the new diff" becomes: a fix that changes behavior (not only wording) gets one re-dispatch of `up:reviewer` on the full task range (`BASE_SHA` to the new `HEAD`), with the fix commit SHAs named in the prompt and, as in point 2, the text of the findings the dispatcher rejected, without reasons, re-raised only on new evidence. Not a fix-only range: the reviewer's Plan alignment step (`agents/reviewer.md:32-37`) would report every phase missing.
   - `plugins/up/skills/uplan/SKILL.md:126-137`: self-review stays inline; "No re-review loop" is replaced by a pointer to the review point.
   - `plugins/up/skills/udesign/SKILL.md`: the task-file output shape gains the `Backwards compatibility:` line (today the step 5 result lives only in chat) and the optional `Size: Large (owner)` line, so the Large signals are in the file.
   - `plugins/up/commands/make.md:191` "Never skip Review" gains a clause naming the final review, so the pre-code skip phrase cannot be read as permission to skip it.
   - README agents table gains a row; version 0.3.39 to 0.3.40.

Rejected alternatives:
- B, only in `/up:make`: fewest edits, but misses most sessions: stages mostly run outside make (`docs/audit-2026-09-05.md:11-12`, ureview in 16 sessions, 3 under make).
- C, a document mode in `up:reviewer`: one agent and no severity duplication, but the agent is built around a diff and was recalibrated on 2026-09-12; editing it risks the working final review.

Owner decisions (2026-09-22): Medium gets one review point, Large two; automatic, announced, skippable; opus pinned; Large detected by design signals; approach A; after the design review, a new API surface dropped from the Large signals.

Backwards compatibility: no break. No new Status value, no new required header; resume reads Status only. Behavior changes the owner accepted: tasks at `design` or `planning` in consumer repos get the review on their next stage run after install; each Medium task costs 1-2 extra opus dispatches; a behavior-changing fix at the final review always gets one re-review. Sessions started before the install keep the old skill text. Task files written before the change have no `Backwards compatibility:` or `Size:` line, so they count as Medium and get only the after-plan review.

TDD: no (reason: doc-only plugin, no runtime code; confirmed by a live run).
Reviewed before code: 2 rounds, 6 Critical/Important fixed, 0 rejected, 2026-09-22.

### Prior art
- `docs/tasks/audit-fixes.md:112` — a size-dependent gate relied on a size never stored; this design reads size from the task file instead.
- `docs/audit-2026-09-05.md:11-12` — stages mostly run outside `/up:make`; the reason for approach A over B.
- `docs/tasks/requirements-review.md:14-15,24` — how a second reviewer agent was added (fixed inputs, blind to rationale); its UK1, sourcing the verbatim ask in a later session, recurs here.
- `docs/tasks/reviewer-calibration.md:5` — the Severity definition and three-part Trigger line, reused by pointer.
- `docs/tasks/session-hygiene.md:113-115` — a second fresh reviewer pass caught an Important ordering finding the first missed.
- `plugins/up/skills/_principles.md:22-24` — Dispatch narration, the single-home pattern this design reuses.
- `docs/tasks/reviewer-model-override.md:5` — the per-dispatch model override pattern.
- `plugins/up/skills/uplan/SKILL.md:137` — "No re-review loop", from upstream commit eebdcb6 (2026-04-17), no evidence recorded.

### Invariants
- IV1 — `/up:make` resume from every Status value lands in the same stage as before; no new Status value and no new required header.
- IV2 — The review before code never runs for a task whose `## Design` is absent or holds only the template placeholder.
- IV3 — The new agent receives only the inputs listed in point 2, never session history or rationale; the round-2 list of rejected findings carries their text only, no reasons.
- IV4 — At most 2 automatic rounds per review point; a third needs the owner's request.
- IV5 — `agents/reviewer.md` and `agents/requirements-reviewer.md` are not modified.
- IV6 — The dispatch procedure has one home; `up:udesign`, `up:uplan`, and `make.md` point to it and never restate it.
- IV7 — The new agent is read-only.

### Principles
- PC1 — Severity text is not copied: the new agent points to `agents/reviewer.md` Severity and adds only the document mapping.

### Assumptions
- AS1 — The effect seen on the cccc Job Fair tasks (fewer serious final findings after a review before code) holds on other tasks.
- AS2 — Stage skills run in the main session with their text loaded, whether started by `/up:make` or by plain words.

### Unknowns
- UK1 — Whether round 2 before code still finds accepted Critical or Important often enough on the calibrated scale; counted from the `Reviewed before code` lines over the next five tasks.
- UK2 — Wall-clock cost per Medium task; measured in the live run.
- UK3 — Where the shared dispatch procedure lives (a new shared file, or a section of `ureview/SKILL.md`, whose steps 2-4 it reuses, so only the agent is a new file) and what the agent file is called; decided at plan.
- UK4 — Whether the Large signals fire on the tasks the owner would call Large and stay quiet on ordinary features; checked in the live run and against the next five cccc task files.

## Plan
<empty — filled by up:uplan; gains ### Rollout / ### Rollback when the change ships to a live system>

## Verify
<empty — filled by up:uverify>

## Code smells
<empty — file:line + one-line smell passed while exploring and left unfixed (out of scope, non-trivial); deleted if none>

## Conclusion
<empty — filled by up:ureview; after done/shipped grows dated ### Follow-up — <date> / ### Scope change — <date> entries and ### Deferred scope-parking>
