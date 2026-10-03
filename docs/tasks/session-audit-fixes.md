# Session audit fixes

**Status:** validating — pushed and installed 0.3.43 on 2026-10-03; one real `/up:make` run in cccc pending
**Branch:** main
**Goal:** The pack says on its own what the owner kept asking for in the 2026-09-18..10-02 sessions: whether the task can be closed, whether another review is needed, and what a question is about before asking it; plan-reviewer round 2 and the final up:reviewer dispatch run only where the audit showed they pay off. Confirmed by the diff, a reinstall, and one real `/up:make` run in cccc showing the approval line and the closing line (owner sign-off).

## Design

Source: audit of 129 sessions (124 cccc, 5 this repo), 2026-09-18..10-02, reconciled by a cross-check pass. Owner-approved scope, items 1-6 below; item 7 added 2026-10-03 from an owner question. Out of scope: the session-length checkpoint (discussed separately), the cccc `.env` helper (cccc task), the 2026-09-13 upstream commit `ff8cf41` (ML debugging and the disabled job-guardian; nothing to port).

1. **Closing line.** Owner asked "можно закрывать?" / "что осталось?" 25 times in ~20 sessions, still on 10-02. New single-home section `_principles.md` → Closing line: one line in the owner's chat language, three parts: what is done, what is left (or "nothing"), whether the task and the Jira ticket can be closed and why not. When a review ran in the same turn, a fourth part says whether another review is needed. Printed once, by whoever ends the workflow turn: `/up:make` step 12, a manual `up:ureview`, and `/up:summary` step 4 (replaces its current "one sentence for the owner").
2. **Approval line.** Owner asked "нужен ли еще ревью?" 9 times, usually at the approval pause. New section in `review-before-code.md` → Approval line: the design and plan approval requests carry one line: which pre-code review ran (rounds, fixed, rejected) or why none ran, and whether another round is needed, with the reason. The same request opens with a clickable `docs/tasks/<slug>.md:<line>` link to the section being approved and one plain line per design point or plan phase (owner, 2026-10-03: "план готов, а где этот план, мне непонятно"). `up:udesign` and `up:uplan` step 12 point to it.
3. **Round 2 rule.** 31 plan-reviewer runs: round 1 found an Important in 12 of 12 paired tasks, round 2 in 4 of 12, 4-6 min per round. `review-before-code.md` → Rounds changes from "an accepted Critical/Important that changed the document" to "an accepted Critical/Important that changed a design decision, the phase list, or the phase order". Corrected citations, line numbers, file paths, and wording do not trigger round 2. Owner can still ask for another round.
4. **Final up:reviewer on Small tasks.** 18 real dispatches, Important in 2, Critical never. `up:ureview` step 1 reads the size from the task file (same rule as review-before-code: decided from the file, never from session memory): a first `## Design` line opening with `Skipped` → no dispatch by default; one line offers it, no pause. Everything else dispatches as today. `up:ureview` itself still always runs and writes the Conclusion (`/up:make` → Rules "Never skip Review" stays true); `Verified by:` records the skipped dispatch. The requirements-reviewer offer (step 1b) is unchanged. Format slip: `agents/reviewer.md` gets the rule that a check that passed is not a finding and is never listed under a tier (5a674ad7 listed 8 "checked, OK" bullets under Important).
5. **Context before a question.** 15+ sessions where the owner could not follow, 4 rejected AskUserQuestion calls. New single-home section `_principles.md` → Questions to the owner: before each question (plain text or AskUserQuestion), 2-4 plain sentences in the owner's chat language: what the situation is, why the answer is needed now, what each option changes. `up:udesign` (step 3 and Rules) and `up:uplan` point to it.
6. **Close `pre-exec-review.md`.** Its Status waits on one live run; there have been 31 real plan-reviewer runs and 14 cccc task files carry a `Reviewed before code:` line. Status → `done`, a dated Follow-up records the evidence; the uncommitted 2026-09-22 Handoff block lands in the same commit.
7. **Findings the owner can judge.** Added by the owner's question 2026-10-03, approved by the owner the same day: after plan review round 1 the chat said "2 serious, 5 minor", then one compressed sentence for both Important findings ("marker format unstable, narrow rule catches 2 of 9 files"), and the minor ones were never named. `up:ureview` step 4 already asks for one line per finding; it does not ask for plain words. Step 4 (also used by review-before-code) now says: each Critical and Important finding gets its own line in the owner's chat language, naming what breaks and on what input, never the reviewer's label alone, then the verdict and its reason; `Below Important` findings are one line: how many, which were applied, in a few words each.

Backwards compatibility: no break. Task files keep their format; the plan-point Record line gains an optional `round 2: <needed | not needed>` field that Resume reads, and a line without it (0.3.41 files) resumes by the old round-count rule. Small tasks lose the default final up:reviewer dispatch: deliberate, owner-approved, recorded in the Conclusion.

TDD: no (doc-only pack; verification is install-and-invoke).

### Prior art
- `docs/tasks/pre-exec-review.md` — built review-before-code.md, the round and record-line rules item 3 narrows.
- `docs/tasks/reviewer-calibration.md` — Severity definitions in reviewer.md; item 4 adds an output rule next to them, not a severity change.
- `docs/tasks/session-hygiene.md` — context checkpoint (out of scope here, item 5 of the audit).
- `docs/tasks/requirements-review.md` — ureview step 1b, kept unchanged.

### Invariants
- IV1 — `/up:make` resume and every existing command keep working; task files written by 0.3.41 resume the same way.
- IV2 — Each new rule has one home (`_principles.md` or `review-before-code.md`); callers point, never restate.
- IV3 — `up:ureview` runs and writes the Conclusion for every size; only the `up:reviewer` dispatch becomes conditional.
- IV4 — Size for item 4 is read from the task file alone.

### Principles
- PC1 — Owner-facing lines are in the owner's chat language; task-file and pack text stays English.

### Assumptions
- AS1 — A first `## Design` line opening with `Skipped` marks a Small or Trivial task. Checked 2026-10-02: all 9 skipped-design files in cccc `docs/tasks/` open with `Skipped`, spelled 4 ways.

## Plan

Approach: two new single-home sections in `_principles.md` (Closing line, Questions to the owner) and one in `review-before-code.md` (Approval line) plus its Rounds rule; callers get one pointer each. ureview gains a size gate on the `up:reviewer` dispatch read from the task file. Four phases, one commit each, all under `plugins/up/` except PH4.
Reviewed before code: 2 rounds, 3 Critical/Important fixed, 0 rejected, 2026-10-03

### PH1 — Closing line and Questions to the owner

- **1.1** `plugins/up/skills/_principles.md:26` (modify) — two new sections before `## Incidental code smells`, each ending "This is the single home of the rule; callers only point here." like `## Dispatch narration`:
  - `## Closing line` — one line in the owner's chat language, printed once by whoever ends the workflow turn: `Done: <what>. Left: <what, or nothing>. Close: <task yes/no; Jira yes/no, or no ticket> — <why not, when no>.` When a review ran in the same turn, append `Another review: <no | yes> — <why>.` Never a recap of the message above it.
  - `## Questions to the owner` — before each question (plain text or AskUserQuestion), 2-4 plain sentences in the owner's chat language: what the situation is, why the answer is needed now, what each option changes. Option labels name the consequence, never an internal ID. PC1.
  - `## How to use` (`:37-43`) — two bullets naming the callers.
  - Respects: IV2, PC1
- **1.2** `plugins/up/commands/make.md:150-158` (modify) — step 12: print the Closing line (`_principles.md` → Closing line) with the finish options. Respects: IV1
- **1.2a** `plugins/up/commands/make.md:31` (modify) — resume from `validating`: on the owner's confirmation → `done`, then step 12 (so the Closing line prints in the session that closes the task). Respects: IV1
- **1.3** `plugins/up/commands/summary.md:57,72` (modify) — replace "one sentence for the owner ... what happens next" with the Closing line pointer (task normally not closable at handoff; `Left` names the first action); `:72` "Same owner sentence" follows. Respects: IV1, IV2
- **1.4** `plugins/up/skills/udesign/SKILL.md:33,201` (modify) — step 3 and the "One question per message" rule point to `_principles.md` → Questions to the owner. Respects: IV2
- **1.5** `plugins/up/skills/uplan/SKILL.md:55` (modify) — step 12: a question to the owner (open question, simpler-way option) follows `_principles.md` → Questions to the owner. Respects: IV2
- Commit: `feat(pack): closing line and context before questions`

### PH2 — Approval line and round 2 rule

- **2.1** `plugins/up/skills/uplan/review-before-code.md:64` (modify) — Rounds: round 2 runs only when an accepted Critical or Important in round 1 changed a design decision, the phase list, or the phase order. Corrected citations, line numbers, file paths, and wording fixes do not count. The owner can still ask for another round (`:66` unchanged). Respects: IV1
- **2.1a** `plugins/up/skills/uplan/review-before-code.md:72,27` (modify) — the Record line after round 1 gains `, round 2: <needed | not needed>`; Resume `:27` runs round 2 only on `round 2: needed`. A line without the field (written by 0.3.41) keeps the old rule (`N` is 1 and `n` at least 1). The `N` is 1 guard stays on both branches; the round-2 write drops the field, so a resume after round 2 never runs a third round past the `:66` cap. Respects: IV1
- **2.2** `plugins/up/skills/uplan/review-before-code.md:79` (modify, append) — new `## Approval line`: the design and plan approval requests carry one line in the owner's chat language: `Review before code: <N rounds, n fixed, m rejected | not run — <reason>>. Another round: <no | yes> — <reason>.` Reasons drawn from this file: design point without a Large signal, Design skipped, skipped by owner, round 1 changed no decision or phase order, 2-round cap. Before that line, the request gives a clickable `docs/tasks/<slug>.md:<line>` link to the `## Design` or `## Plan` heading and one line per design point or phase in the owner's chat language: what it changes, in plain words. Respects: IV2, PC1
- **2.3** `plugins/up/skills/udesign/SKILL.md:42` and `plugins/up/skills/uplan/SKILL.md:55` (modify) — step 12 approval request includes the Approval line (`review-before-code.md` → Approval line). Respects: IV2
- Commit: `feat(review-before-code): approval line; round 2 only on a structural change`

### PH3 — Final reviewer size gate and reviewer output rule

- **3.1** `plugins/up/skills/ureview/SKILL.md:23` (modify) — "Never skipped, regardless of task size" stays for the skill and the Conclusion; add that the `up:reviewer` dispatch follows step 1's size gate. Respects: IV3
- **3.2** `plugins/up/skills/ureview/SKILL.md:51` (modify) — step 1 opens with the size gate: the first line of `## Design` opens with `Skipped` (the `review-before-code.md:9` rule, any case or punctuation after it) → no dispatch; print one line offering it ("final code review not run: Design was skipped; say so to run it"), no pause; skip steps 1b-5 and go to step 6. If the owner takes the offer after the Conclusion is written, run steps 1-5 then and rewrite `Verified by:` and `Review findings`. Any other `## Design` → dispatch as today. Decided from the task file alone. Respects: IV3, IV4, AS1
- **3.2a** `plugins/up/commands/make.md:133` and `plugins/up/skills/ureview/SKILL.md:3` (frontmatter description) (modify) — "dispatches `up:reviewer`" gains "(unless Design was skipped, step 1)"; `make.md:133` also tells `up:ureview` it was invoked by `/up:make` (precedent: `uplan/SKILL.md:55`, step 7 tells uplan), which 3.5 reads. Respects: IV2
- **3.3** `plugins/up/skills/ureview/SKILL.md:191` (modify) — `Verified by:` is required when the dispatch was skipped by the size gate: `no up:reviewer dispatch (Small; offered, not requested)`. Respects: IV3
- **3.4** `plugins/up/skills/ureview/SKILL.md:225` ("Never" list) — "Run review on yourself" reads: when a review runs, it is the subagent; the size gate skips it, never replaces it with a self-review. Respects: IV3
- **3.5** `plugins/up/skills/ureview/SKILL.md:229` (modify) — Terminal state: a manual invocation ends with the Closing line; when `/up:make` said it invoked the skill (3.2a), step 12 prints it instead, so it prints once. Respects: IV2
- **3.6** `plugins/up/agents/reviewer.md:116-124` (modify) — Rules: a check that passed is not a finding and is never listed under a tier; "nothing at ≥80" stays the one sentence in Findings. Respects: IV1
- **3.7** `plugins/up/skills/ureview/SKILL.md:113-131` (modify) — step 4 (Design item 7): one line per Critical and Important finding, never merged; the line is in the owner's chat language and says what breaks and on what input, then the verdict (fix / push back / defer) and its reason; `Below Important` gets one line: count, which were applied, a few words each. The good-example gains one such line. `:99` (step 2) and `:148` (step 5b) change with it: the Below Important block still skips the per-finding loop, but its one-line summary is printed in step 4 as the decision (apply or drop per line), and 5b carries it out. review-before-code.md `## Findings` already routes through step 4; no edit there. Respects: IV2, PC1
- Commit: `feat(ureview): final up:reviewer opt-in on Small tasks; passed checks are not findings; findings in plain words`

### PH4 — Close pre-exec-review, version

- **4.1** `docs/tasks/pre-exec-review.md:3` (modify) — Status `done — live use confirmed 2026-10-02`; append `### Follow-up — 2026-10-02` under Conclusion: 31 real plan-reviewer runs in cccc 09-22..10-02, 14 task files with `Reviewed before code:`, round-2 yield 4 of 12, reconciled in this task's Design; AS1 / AS2 / UK1 / UK2 / UK4 (`pre-exec-review.md:79,83,204,208`) recorded from that evidence or marked "not measured". The uncommitted 2026-09-22 Handoff block lands in this commit.
- **4.2** `plugins/up/.claude-plugin/plugin.json` (modify) — version 0.3.41 → 0.3.42 (patch, CLAUDE.md → Versioning).
- **4.3** `README.md` (modify only if it states that the final reviewer always runs or describes review rounds; one-line fix).
- Commit: `docs(pre-exec-review): done on live evidence; bump 0.3.42`

### Test strategy
none — doc-only pack. Verification: reinstall (`claude plugin update up@ultrapack`), grep that each new section has exactly one home and every caller points to it, then one real `/up:make` run in cccc for the Goal.

### Risks
- RK1 — A Medium task whose Design was skipped by owner request without the `Skipped (` prefix gets a dispatch it could have skipped; acceptable, the gate errs toward reviewing.
- RK2 — Approval and closing lines become boilerplate the owner skims; mitigated by the one-line cap and "never a recap".

## Verify

**Result:** passed (after one fix)

Happy-path:
- CK1 — Closing line: a caller in `_principles.md` → How to use that never points to it, or a double print under `/up:make` — held (make.md:31,152, summary.md:57,72, ureview Terminal state; make step 10 tells ureview who invoked it)
- CK2 — Approval line not reachable from both approval requests — held (udesign step 12, uplan step 12)
- CK3 — Resume table on hand-made Record lines (0.3.41 `1 rounds, 2 fixed`; `round 2: not needed`; `2 rounds`) — held, each lands on the intended branch

Negative:
- CK4 (AS1) — size gate on the 9 real skipped-Design files in cccc — broke: 7 of 9 have a blank line between `## Design` and `Skipped`, and the gate said "the first line"; fixed in a431186 ("first non-empty line"), re-probe matches 9 of 9
- CK5 — 19 real cccc Record lines (no `round 2:` field, `round`/`rounds`, `skipped, small task`) misread by the new Resume rule — held, same outcome as 0.3.41

Invariants / assumptions:
- CK6 (IV2) — Closing line, Questions, Approval line formats restated outside their home — held, grep finds each format once
- CK7 (IV3) — size gate path that skips the Conclusion or breaks make.md "Never skip Review" — held (gate goes to step 6; make.md:195 unchanged)
- CK8 (IV1) — old Below Important wording ("steps 2-4", "fair-evaluation loop") left contradicting step 4 — held, none left in `plugins/up`

Interfaces:
- CK9 — new reviewer.md rule contradicts the Output format — held (`nothing at ≥80` sentence unchanged)

Smoke: `claude plugin validate plugins/up` and `.` → passed (marketplace description warning is old)

Goal: proxy only — reinstall needs a push to GitHub; the real `/up:make` run in cccc showing the approval line and the closing line is the owner's step

## Conclusion

Outcome: all seven Design items are in the pack as 0.3.42 (`2d8925c`..`c04c46d`); the Goal still needs a push, `claude plugin update up@ultrapack`, and one real `/up:make` run in cccc showing the approval line and the closing line.

Invariants:
- IV1 — verify CK3, CK5: 19 real cccc Record lines and hand-made 0.3.41 lines resume as before; make.md resume table only gained the step-12 tail
- IV2 — verify CK6 plus review: each format has one home; the skipped-Design test moved to `review-before-code.md` only (c04c46d)
- IV3 — verify CK7: the size gate goes to step 6, make.md "Never skip Review" unchanged
- IV4 — the gate reads the first non-empty line under `## Design`, nothing from session memory

### Assumptions check
- AS1 — held: 9 of 9 skipped-Design files in cccc match the gate after a431186

### Deviations from plan
- 3.2 said "the first line of `## Design`"; the gate reads the first non-empty line — verify CK4 found a blank line after the heading in 7 of 9 real files (a431186)

Review findings:
- Text fixes: 5 applied (c04c46d)

Verified by: `up:reviewer` (Fable) merge-ready, no Critical or Important; `up:requirements-reviewer` (Fable) on the owner's 2026-10-02 and 2026-10-03 words, delivers-the-ask: yes, all 8 clauses met; a second `up:requirements-reviewer` run on the owner's request (`c680ab0`..`b71056f`, reachability on resume, manual, Small, Goal-pending paths) also yes; its below-threshold note that a resume at `reviewing` could print the Closing line twice was fixed in make.md's resume table (0.3.43)

### Handoff — 2026-10-02
- Position: planning, plan written, plan review round 1 done, owner approval pending; committed: c680ab0 (design and plan); uncommitted: `docs/tasks/pre-exec-review.md` (2026-09-22 Handoff block, lands in the PH4 commit per plan 4.1), untracked `.claude/` is unrelated, leave it
- Decided: Design approved by the owner 2026-10-02 in chat; no design-point review (no Large signal), owner agreed
- Decided: round 1 had 2 accepted Important (size gate spelling, Resume vs round-2 rule), both changed a Design statement, so round 2 is due under both the 0.3.41 rule and the new one; resume runs it automatically from the Record line
- Decided: owner wants `up:requirements-reviewer` after all edits (ureview step 1b); his verbatim ask is in transcript `~/.claude/projects/-Users-svirins-dev-current-ultrapack-dzm/70bee2c7-bd80-4745-aa3e-d1f6da030965.jsonl` (first user message, "Делаем 1, 2, 3, 4, 5 обсуждаем отдельно", the AskUserQuestion answers, "после заврешения всех правок сделай requirements review")
- Decided: out of scope, tracked elsewhere: cccc `.env` helper (owner chose a script that prints host and DB name without the password; a separate cccc task) and the session-length checkpoint (to discuss); cccc commit/push rule already landed as cccc 719e77731
- First action: `/up:make` resumes `planning` → plan review round 2 (`up:plan-reviewer`), then the plan approval request with the Approval line

### Handoff — 2026-10-03
- Position: validating; all phases, verify, review, and two requirements reviews done; 0.3.43 pushed (446993d) and installed; uncommitted: none (untracked `.claude/` is unrelated, leave it)
- Decided: the 2026-10-02 Handoff above is superseded; nothing in it is open
- Open: the owner's choice whether the context-before-questions rule also covers `/up:make` step 4 and step 6 questions (offered, not requested)
- First action: ask the owner whether the real `/up:make` run in a fresh cccc session showed the approval request with a link and one line per phase, plain per-finding lines, and the closing line; on yes, Status `done`, then step 12
