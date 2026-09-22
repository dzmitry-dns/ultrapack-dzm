# Pre-execution review: an independent reviewer on Design and Plan before any code

**Status:** validating — live run pending
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
   - After every round, one record line, updated in place: `Reviewed before code: <N> rounds, <n> Critical/Important fixed, <m> rejected, <date>`, or `Reviewed before code: skipped by owner, <date>`. Its slot is fixed: for the design point, the line right after `TDD:` in `## Design`; for the plan point, the line right after `Approach:` in `## Plan`. Never inside a subsection. A resumed stage reads the round count from it and runs another round only when the count is below 2 and the last round changed the document. A re-plan that `up:uexecute` invokes on a structural deviation is a new document: its line replaces the old one and the same rules apply. The line also gives UK1 its data.
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

Backwards compatibility: no break. No new Status value, no new required header; resume reads Status only. Behavior changes the owner accepted: tasks at `design` or `planning` in consumer repos get the review on their next stage run after install; each Medium task costs 1-2 extra opus dispatches; a behavior-changing fix at the final review always gets one re-review. Sessions started before the install keep the old skill text. Task files written before the change have no `Size:` line and seldom a `Backwards compatibility:` line with a hard break, so they mostly count as Medium and get only the after-plan review.

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

Approach: two new files carry the whole feature (the agent, and one procedure file that is the single home of when, how, and how often the review runs); udesign, uplan, make.md, and ureview gain pointer lines and the small text changes the Design names. UK3 resolved: the procedure lives at `plugins/up/skills/uplan/review-before-code.md` (reference file next to its main caller, the `uexecute/waves.md` pattern; `ureview/SKILL.md` is already 227 lines and triggers after verify); the agent is `up:plan-reviewer`.
Reviewed before code: 2 rounds, 3 Critical/Important fixed, 0 rejected, 2026-09-22.

### PH1 — Agent and procedure

- **1.1** `plugins/up/agents/plan-reviewer.md` (create)
  - Frontmatter: `name: plan-reviewer`, description (reviews a task file's Design and Plan against the code and the ask before any code is written; dispatched from `up:uplan` and `up:udesign` per `review-before-code.md`), `tools: Glob, Grep, Read, Bash`, `model: opus`, `effort: high`.
  - Sections: stance; what you receive (task file path, review point `design | plan`, working directory, optional verbatim ask, optional Jira ticket text, optional round-2 list of rejected finding texts with "re-raise only on new evidence"); what to read (`**Goal:**`, `## Design` and its subsections, `## Plan` at the plan point; never `## Verify` or `## Conclusion`); the four checks; two passes, report ≥ 80; severity by pointer to `${CLAUDE_PLUGIN_ROOT}/agents/reviewer.md` → Severity plus the one document mapping; read-only Bash list; output format (Critical, Important with Trigger / Evidence / Fix, Below Important max 5, Scope flag, Verdict `ready for <planning | execution>: yes | no`); rules.
  - Respects: IV3, IV5, IV7, PC1.
- **1.2** `plugins/up/skills/uplan/review-before-code.md` (create)
  - `## When it runs`: plan point (Design holds more than the template placeholder); design point (Large signals read from the `## Design` text: a DB migration; a `Backwards compatibility:` line whose resolution is a hard break or a removal or rename without a shim, while "no break", "greenfield", deprecate-with-shim, and versioned do not fire; the line `Size: Large (owner)`); the skip phrase, covering every remaining point; resume rule from the record line, where a design slot reading `skipped by owner` also skips the plan point in a later session; a skip said during design is written to the design slot even when the design point did not fire; a re-plan invoked from `up:uexecute` (`uexecute/SKILL.md:177`) is a new document: the plan slot's line is replaced and the same rules apply, max 2 rounds.
  - `## Dispatch`: narration per `_principles.md` Dispatch narration; `up:plan-reviewer`; the prompt skeleton; Jira text only when the task has a `**Jira:**` header and an Atlassian read tool is available; model override by pointer to `up:ureview` step 1 "Model".
  - `## Findings`: by pointer to `up:ureview` steps 2-4, with the Important definition taken by pointer from `agents/plan-reviewer.md` Severity (which itself points to `agents/reviewer.md` and adds the document mapping); edits land in the task file only; Below Important wording entries applied when they check out, the rest dropped (not routed to `## Code smells` as ureview 5b does).
  - `## Rounds`: round 2 only after an accepted Critical or Important changed the document; fresh agent; max 2 automatic; third on owner request.
  - `## Record line`: format, the two fixed slots, updated in place after every round.
  - Respects: IV2, IV3, IV4, IV6.
- Commit: `feat(pack): plan-reviewer agent and review-before-code procedure`

### PH2 — Wire the stages

- **2.1** `plugins/up/skills/uplan/SKILL.md`
  - `:53` step 10: "This is the final step before handoff" becomes "the last self-check before the review".
  - `:54` new step 11: run the plan point of `${CLAUDE_PLUGIN_ROOT}/skills/uplan/review-before-code.md`; old step 11 becomes step 12.
  - `:137` "Fix issues inline. No re-review loop." becomes "Fix issues inline. The independent review is step 11."
  - `:183` terminal state: "step 11 exception" becomes "step 12 exception"; review named before presenting.
  - Respects: IV1, IV6.
- **2.2** `plugins/up/skills/udesign/SKILL.md`
  - `:35` step 5: the resolution is recorded on the `Backwards compatibility:` line.
  - `:39` step 9: the written Design carries the `Backwards compatibility:` line, and `Size: Large (owner)` when the owner called the task Large in the ask or the dialogue.
  - `:40-41` new step 11: run the design point of `${CLAUDE_PLUGIN_ROOT}/skills/uplan/review-before-code.md`; old step 11 becomes step 12.
  - `:171-174` output shape: `Backwards compatibility: <each break and its resolution | no break | greenfield>` and the optional `Size: Large (owner)` line, both before `TDD:`.
  - Respects: IV1, IV2, IV6.
- **2.3** `plugins/up/commands/make.md`
  - `:100` step 5: one pointer line (a Design with a Large signal, as the procedure defines it, not step 4's classification, is reviewed before approval, `${CLAUDE_PLUGIN_ROOT}/skills/uplan/review-before-code.md`).
  - `:113` step 7: one pointer line (the plan is reviewed before the approval pause when the task has a Design).
  - `:191` "Never skip Review" gains "(the final `up:ureview`; the pre-code skip phrase covers only the review before code)".
  - Respects: IV1, IV6.
- **2.4** `plugins/up/skills/ureview/SKILL.md`
  - `:142` "If fixes are substantial, re-dispatch the reviewer on the new diff." becomes: a fix that changes behavior (not only wording) gets one re-dispatch on the full `BASE_SHA`..new `HEAD` range, the prompt naming the fix SHAs as review fixes (not plan deviations) and carrying the text of rejected findings, without reasons, re-raised only on new evidence.
  - `:64-66` red flag gains the one exception: a re-dispatch prompt may carry those two fields; neither is session history or rationale.
  - `:70-75` prompt skeleton gains the two optional re-dispatch fields; they reach the agent only as prompt text, since `reviewer.md:19-24` stays unchanged (IV5).
  - Respects: IV5 (the reviewer agent file stays untouched; only the dispatch prompt changes).
- Commit: `feat(pack): review before code in udesign, uplan, make; concrete re-review rule in ureview`

### PH3 — README and version

- **3.1** `README.md:33` Plan stage line: one sentence on the review before code (Design too on Large tasks); `:110-116` agents table gains the `up:plan-reviewer` row, saying it reviews Design and Plan before code.
- **3.2** `plugins/up/.claude-plugin/plugin.json:3` version `0.3.39` to `0.3.40`.
- Commit: `chore(pack): document plan-reviewer, bump 0.3.40`

### Test strategy
none: doc-only plugin; uverify attacks the text, and the Goal needs a live run on a real Medium task after install.

### Risks
- RK1 — Medium is the default size, so most `/up:make` runs gain 1-2 opus dispatches of 2.5-10 minutes; accepted by the owner, measured by UK2.
- RK2 — The make.md context checkpoint (3+ subagents since the last one) fires more often at step 8; advisory only, it never pauses.
- RK3 — A session started before the install runs the old skill text, so the live run must start in a fresh session after `claude plugin update up@ultrapack`.

### Rollout
Owner pushes `main`; `claude plugin update up@ultrapack`; fresh session; one live run on a real Medium task (Goal). The live run checks AS2, UK2, UK4; AS1 and UK1 are counted from the record lines of the next five tasks. Compat: no Status or header change (IV1); task files written before the change carry no `Size:` line and seldom a hard-break compat line, so they mostly get only the plan point (1.2).

### Rollback
Revert the three phase commits and update the plugin; no data or state is touched.

## Verify

**Result:** passed (round 2, after fix 3570418)

Happy-path:
- CK1 — a Design or Plan written by the current udesign/uplan lacks the trigger text or a record-line slot (`TDD:`, `Approach:`) — held
- CK2 — a skip said during design, when the design point did not fire, is lost before a later plan point — held

Negative:
- CK3 (IV2) — a Small or Trivial task file whose skipped Design still fires the plan point — broke in round 1: every such file with a `## Design` section (5 here, e.g. `docs/tasks/verify-recipe.md`; 8 in cccc, e.g. `docs/tasks/archive/cats-1533-job-delete-authz.md`) replaces the placeholder with a note opening `Skipped`, which "holds more than the template placeholder". Held in round 2: the fixed rule, applied to all 247 task files with a Design in both repos, skips all 13 notes; the one skip-like opening it fires on (cccc `hide-open-positions-for-completed-events.md`) is a Trivial task with a deliberate Design, and Trivial skips Plan
- CK4 — the pre-code skip phrase read as leave to skip the final `up:ureview` — held
- CK5 (IV4) — a resume path that runs a third automatic round — held

Invariants / assumptions:
- CK6 (IV1) — make.md resume table or Status enum changed — held (hunks only at steps 5, 7, Rules)
- CK7 (IV3) — an input beyond Design point 2 reaches the agent — held (the smoke agent ignored the Handoff block and said so)
- CK8 (IV5) — held: `git diff ee14e00..HEAD` on both reviewer agent files is empty
- CK9 (IV6) — procedure rules restated outside `review-before-code.md` — held
- CK10 (IV7) — held: tools Glob, Grep, Read, Bash; Bash list read-only
- CK11 (PC1) — Severity text copied into `plan-reviewer.md` — held
- CK12 (AS2) — deferred: needs the live run

Interfaces:
- CK13 — a `→ Section` pointer in the new or edited files names a missing heading — held
- CK14 — the step 11/12 renumbering breaks a reference — held
- CK15 — the agent's output shape does not fit the procedure's processing (tier counts, verdict, Important by pointer) — held

Smoke: `claude plugin validate plugins/up` → passed; `plan-reviewer.md` text dispatched as a general-purpose agent (Fable) on snapshot `ee14e00`, plan point → report in format, 0 Critical/Important, 2 Below Important, 4.3 min.

Goal: proxy only — the registered `up:plan-reviewer`, fired by `up:uplan` on a real Medium task after push and plugin update, is not exercised.

Notes: round 2 re-ran CK3 only; the fix changed one line of `review-before-code.md` and `plan-reviewer.md` is unchanged since the smoke. Smoke Below Important, for review: a re-plan's round 1 reads already-committed phases as wrong citations; the unchanged `reviewer.md` may report review-fix commits as unplanned.

## Code smells
- `plugins/up/skills/uplan/review-before-code.md:9` — copies the `make.md:54` Design placeholder string; a template edit silently breaks the plan-point test (GPC4)

## Conclusion

Outcome: the review before code is built, verified, and reviewed (`ef3ace2`..`5cddf73`); the Goal still needs one live run on a real Medium task after push, `claude plugin update up@ultrapack`, and a fresh session.

Invariants:
- IV1 — make.md hunks only in steps 4, 5, 7 and Rules; resume table and Status enum untouched (CK6)
- IV2 — the plan point skips a missing, placeholder, or `Skipped` Design, checked on 247 task files (CK3); make step 4 now writes the `Skipped` line (`caba670`)
- IV3 — the prompt skeleton carries only the Design point 2 inputs; the smoke agent ignored the Handoff block (CK7)
- IV4 — round 2 only when N is 1 and n ≥ 1; a third only on the owner's request (CK5)
- IV5 — both reviewer agent files unchanged over `ee14e00`..`5cddf73` (CK8, both review rounds)
- IV6 — the rules live only in `review-before-code.md`; make.md steps 5 and 7 reduced to pointers in review (CK9)
- IV7 — tools Glob, Grep, Read, Bash with a read-only Bash list (CK10)

### Assumptions check
- AS1 — unverifiable yet: counted from the `Reviewed before code` lines of the next five tasks
- AS2 — unverifiable yet: needs the live run in a fresh session after install

### Unknowns outcome
- UK1 — still-open: counted from the record lines of the next five tasks
- UK2 — still-open: measured in the live run; the proxy smoke took 4.3 min on Fable
- UK3 — resolved: procedure at `plugins/up/skills/uplan/review-before-code.md`, agent `up:plan-reviewer`
- UK4 — still-open: the live run and the next five cccc task files

### Deviations from plan
- 1.2 plan point: a Design whose text opens with `Skipped` also means no review, beyond the placeholder the plan named — verify CK3 found that every Small or Trivial task file with a `## Design` section (5 here, 8 in cccc) replaces the placeholder with such a note, so the placeholder test alone fired the review on Small tasks.

### Known risks
- A structural re-plan restarts the plan point at round 1 while HEAD already holds the finished phases, so `up:plan-reviewer` reports their citations as wrong and the dispatcher has to reject that noise — raised by the smoke and by the re-review; the fix, an `Executed so far: <phases, SHAs>` prompt field, changes the IV3 input list, so it waits for an owner decision.
- `agents/reviewer.md` stays frozen (IV5), so the `ureview` step 5 re-dispatch fields work as prompt text only and the reviewer may still list review-fix commits as unplanned — accepted in Design point 5.

Review findings:
- Important: the `Skipped` exemption rested on no written rule, fixed in `caba670` (make step 4 writes `Skipped (<size>): <reason>`); the final-review re-dispatch had no cap, fixed in `55232e7` (one per review). The re-review's one Important (re-plan noise) is deferred to Known risks: it yields noise the dispatcher rejects, not a wrong edit, and its fix changes IV3.
- Text fixes: 3 applied (`e28d1f7`), 1 applied (`5cddf73`)

### Handoff — 2026-09-22
- Position: executing, PH1 not started; committed: ea1626a (plan approved, status executing); uncommitted: none (untracked `.claude/` is unrelated to this task, leave it)
- Decided: the owner approved Design and Plan after two independent review rounds each; all four rounds ran as general-purpose agents on Fable, because `up:plan-reviewer` does not exist yet and the Agent tool has no effort parameter
- Decided: reviewer dispatches in this task (final `up:ureview` included) use `model: fable` as a dispatch-time override, announced in one line first; the new agent's frontmatter still pins `opus` per Design point 2
- Decided: work on `main`, one commit per phase (PH1, PH2, PH3), no push until the owner says so
- First action: `/up:make` resumes into `up:uexecute`; PH1 creates `plugins/up/agents/plan-reviewer.md` and `plugins/up/skills/uplan/review-before-code.md`
