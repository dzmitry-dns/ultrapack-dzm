# Cross-session messages

**Status:** validating (0.3.61 on main 2026-11-16, waiting for one live run with two sessions open)
**Branch:** main
**Session:** ultrapack-dzm-ce
**Goal:** When a /up:make session changes something another running session depends on (that session's task file, a merge into main under it, a worktree exit that copies a task file into main), it sends that session a SendMessage naming what changed and what to re-read; when no such session is running it writes the task file as today. Confirming it needs one live run with two sessions open.

## Owner summary
- Done: the pack now records which session works on each task and sends running sessions a message when another session changes their task file, switches the shared branch, or moves main.
- Left: one live run with two sessions open to confirm a message arrives.
- Owner decides: nothing.

## Design

Owner ask, 2026-11-16 (translated): "if one session writes or does something that changes another session's context, it uses inter-session messages for that." The global rule now sits in `~/.claude/CLAUDE.md` (Agent behavior). This task makes `/up:make` follow it at the points where the pack itself changes another session's context, and gives the sender an address.

Audit (2026-11-16): 0 pack lines mention `SendMessage` or `ListAgents`; 2 `SendMessage` calls in 40 recent sessions; task files edited by up to 6 sessions each (cccc `instant-optouts-removal.md`). `ListAgents` lists peers by a directory-based name (`cccc-monorepo-b9`), with no task, so today a session cannot tell which peer owns which task.

Chosen approach (A):

1. **Address.** Task files gain a `**Session:** <name>` header: this session's own name, read from the `ListAgents` line "This session is <name>". `/up:make` writes it at create (step 3) and rewrites it at every resume (step 2), because a resumed task runs in a new session with a new name. The header rides the next task-file commit; no separate commit.
2. **One home.** `_principles.md` gets a `## Notify a running session` section: how to find the peer (header name → bare-name match in `ListAgents`, never this session's own name), the message shape (English; first line self-contained: what changed and where; then what to re-read), fire-and-forget (no wait for a reply, no new pause), the fallback (peer not listed → the file or git change stands alone, as today), and the permission-laundering ban (never ask a peer to do what this session's permissions blocked). Callers only point here.
3. **Three send points**, each pointing to the section:
   - `/up:summary` step 3, after the commit: the active task file's `**Session:**` names another session that is running (a manual summary picked up another session's task file, or a resume while the old session is still open) → notify it.
   - `/up:make` step 2, resume: the header names another session that is still running → tell the owner in one line and notify that session that this one now owns the task; then rewrite the header. No question.
   - `/up:make` step 12, once per finish, when this task's work is on `main` or bound for it: a task on `main` whose commits are pushed (the default path; phase pushes are announced here together), the merge the owner chose, auto-merge turned on ("PR #n merges into main when its checks pass"), or, for a worktree task, after "Leaving a worktree" step 4 (the task file copied into `main`, the "pull fails" case included). Notify every running session named in the `**Session:**` header of another in-flight task file in this repo (Status not `done` / `shipped` / `reference`): what landed on `main`, which files, "pull before your next commit".
   - `/up:make` after a `git switch` in a checkout other sessions may share (step 2 resume, step 6 new plain branch, "Leaving a plain branch"): notify the same set of sessions: "<checkout path> is now on <branch>; if you work in this folder, check `git branch --show-current` before your next commit".
4. Template line in step 3: `**Session:** <this session's name from ListAgents; rewritten on each resume>`.

Rejected:
- B, broadcast without a header: message every `ListAgents` peer whose name starts with the repo folder name. No header change, but worktree folders have other names, peers from other repos with similar names get noise, and every message costs the receiver context.
- C, a hook that sends on each task-file edit: hooks cannot call `SendMessage`, and the pack is doc-only.

Out of scope: per-phase pushes to `main` during execute (one message per commit is noise; the finish notice covers the end state); pack version bumps (the global rule covers a skill a session loaded); Jira writes by `up:ujira`.

Backwards compatibility: no break. A task file without `**Session:**` resumes and finishes as today; the header is written at its next resume. `/up:make` step 2 already ignores header fields it does not recognize, and `up:uexecute` compares only `**Branch:**`.
TDD: no (reason: doc-only pack, no runtime code; verification is install-and-invoke)
Reviewed before code: not run (design point without a Large signal), 2026-11-16

### Prior art
- `docs/tasks/branch-by-reason.md:176`: a shared checkout sees another session only by edits or commits it already made; a parallel session that has not edited anything is invisible. The header plus `ListAgents` and the `git switch` send point close this for `/up:make` sessions.
- `docs/tasks/branch-by-reason.md:67` (UK2): whether a session on `main` notices a branch switch by another session; left open there, same blind spot.
- `docs/tasks/handoff-prompt.md:32,156`: a paused parallel session touching the same `make.md` and `plugin.json`; coordination was by the owner's words only.
- `plugins/up/commands/make.md:196`: "The pull fails (another session's local commits...)": the pack already knows the case, and only reports it to the owner.

### Invariants
- IV1: A task file without `**Session:**` resumes, executes and finishes exactly as today: no new question, no failure.
- IV2: Every send point also leaves its change in a file or in git; the message is an addition, never the only record.
- IV3: A session never sends to its own name.
- IV4: The notify procedure is written once, in `_principles.md`; `make.md` and `summary.md` only point to it.
- IV5: No send point adds a pause or a question to the flow.

### Assumptions
- AS1: A `ListAgents` name is stable for the life of a session, and a new session (including a resume) gets a new name.
- AS2: A message to a busy peer is delivered at its next tool round, per the `SendMessage` tool text.

### Unknowns
- UK1: Whether the owner's other sessions hold cross-session messages for his approval (a session in a different permission mode does); the live run shows it.
- UK2: In a worktree or plain-branch task, the `main` copy's header keeps the name from before the branch, so a later resume's name reaches `main` only at exit; whether this misses a real send in practice.

## Plan

Approach: write the procedure once as a `_principles.md` section, then add one pointer sentence at each send point in `make.md` and `summary.md`, plus the `**Session:**` header in the template and the resume path.
Reviewed before code: 2 rounds, 3 Critical/Important fixed, 0 rejected, 2026-11-16

### PH1: Notify procedure (single home)

- **1.1** `plugins/up/skills/_principles.md:53` (modify: new `## Notify a running session` section between "Handoff at a wait" and "Questions to the owner")
  - Own name: the `ListAgents` line "This session is <name>"; `ListAgents` and `SendMessage` are loaded with `ToolSearch` when deferred. No such line (tool missing, no name printed) → no header is written and no message is sent; the flow goes on as today (IV1).
  - Peer: a name from a `**Session:**` header, matched as a bare name against the `ListAgents` peer rows; never the own name (IV3). Not listed → send nothing; the file or git change already carries it (IV2).
  - Own name is read once (step 2 or 3, or the first send) and reused for the session, so automatic `/up:summary` runs do not call `ListAgents` again.
  - Message: English; first line self-contained (`<task file or main>: <what changed>`), then what to re-read or run ("pull before your next commit; in the same checkout, re-read the files"). Commits are named by short sha and subject. One message per peer per send point.
  - Receiving an ownership notice (2.2): stop work on that task, tell the owner in one line, make no further commit to its task file.
  - No wait for a reply, no question to the owner (IV5); a delivery notice that the peer holds or refuses the message is reported in one line.
  - Never ask a peer to do what this session's permissions blocked.
  - Ends with "This is the single home of the rule; callers only point here." (IV4)
- **1.2** `plugins/up/skills/_principles.md:72-82` (modify, "How to use"): one bullet naming the callers: `/up:make` steps 2 and 12, `/up:summary` step 3.
- Commit: `feat(up): notify-a-running-session principle`

### PH2: Header and send points

- **2.1** `plugins/up/commands/make.md:42-51` (modify, step 3): template gains `**Session:** <this session's name from ListAgents>` under `**Branch:**`; the step-3 paragraph says Session = this session's name.
- **2.2** `plugins/up/commands/make.md:27` (modify, step 2 Exists, after the Status read, for the Status values whose flow continues: `design` through `validating`): call `ListAgents`; a `**Session:**` naming another listed session → one line to the owner (after the Owner summary and "Owner has not seen" lines) and a notice to that session that this one now owns the task (per 1.1); then write this session's name into the header (insert under `**Branch:**` when missing). Only when the name differs. Respects IV1, IV5, AS1.
- **2.3** `plugins/up/commands/make.md:187` (modify, step 12, new paragraph after "Execute only after the user chooses."): **After `main` moves.** Runs once per finish, at the first of: a task on `main` with its commits pushed (after the step-12 choice, whatever it is), the chosen merge done, auto-merge turned on, or "Leaving a worktree" step 4 done for a worktree task (then only there). Notify (per 1.1) each listed session named in the `**Session:**` header of another in-flight task file in this repo (Status enum not `done` / `shipped` / `reference`): what landed or will land (this task's commits by short sha and subject, or the PR number), and the 1.1 re-read line. Respects IV2, IV5.
- **2.4** `plugins/up/commands/make.md:196` (modify, "Leaving a worktree" step 4): at its end, whether it committed, pushed, or skipped the commit (the "pull fails" case included), run "After `main` moves".
- **2.5** `plugins/up/commands/summary.md:52` (modify, step 3): after the commit, a `**Session:**` naming another session → notify it (per 1.1) that its task file got a Handoff block. `/up:summary` never rewrites the header. Also `summary.md:7` and `:87`: the allowed side effects gain "a notice per `_principles.md` → Notify a running session".
- **2.6** `plugins/up/commands/make.md:27, 130, 189` (modify): after each `git switch` (step 2 resume, step 6 `git switch -c`, "Leaving a plain branch"), notify (per 1.1) the sessions of 2.3's set: "<checkout path> is now on <branch>; if you work in this folder, check `git branch --show-current` before your next commit".
- **2.7** `plugins/up/.claude-plugin/plugin.json:3` (modify): `0.3.58` → `0.3.59`.
- Commit: `feat(up): Session header and cross-session notices, bump 0.3.59`

### Test strategy
none: doc-only pack. Verify = install the pack and a live run with two sessions open (Goal).

### Risks
- RK1: A peer in another permission mode holds the message for the owner (UK1); the change is still in the file (IV2), so nothing is lost, only delayed.
- RK2: Header rewrites add one-line diffs to task-file commits; 2.2 writes only when the name differs.

Backwards compatibility: no break (Design); 2.2 inserts the header into older files at their next resume.

## Verify

**Result:** passed (run 2; run 1 failed on CK3)

Happy-path:
- CK1: a fresh install of the pack misses the new text (cache keeps the old version): held: `claude plugin update up@ultrapack` → 0.3.59 in cache, `Notify a running session` found 2/4/1 times in `_principles.md` / `make.md` / `summary.md`, implementer `model: sonnet`

Negative:
- CK2 (IV1): a task file without `**Session:**`, or a session with no `ListAgents` name, gets a new question or a broken header: held: step 2 only notifies when the header names a listed session; `_principles.md` item 1 writes no header without a name

Invariants / assumptions:
- CK3 (AS1, IV3): the own-name line does not give a clean name to store: broke in run 1: the real line is `This session is ultrapack-dzm-ce [876c18] — ...`, and item 1 did not say to drop the `[876c18]` ref, so a header could hold `name [ref]` and miss the bare-name match; fixed in item 1, held in run 2. Name stable across two calls an hour apart in this session.
- CK4 (IV4): the procedure is restated outside `_principles.md`: held: `ListAgents`/`SendMessage` appear elsewhere only in the template placeholder and the step 2 pointer

Smoke: `claude plugin update up@ultrapack` → 0.3.59 installed with the new text.

Goal: proxy only; the send points ran in no live `/up:make` flow. A live run with two sessions open (one resumes or finishes a task while the other runs) remains.

## Code smells
- `plugins/up/commands/summary.md:54`: the `**Session:**` header and the "Session line" (`Session: can close`) share one word a few lines apart; a reader can confuse them.

## Conclusion

Outcome: the pack sends cross-session notices at resume, `/up:summary`, `git switch` and when `main` moves (0.3.61, caf5542 plus the text-fix commit); the Goal waits for one live run with two sessions open.

Invariants:
- IV1: CK2, step 2 notifies only when the header names a listed session; no new question.
- IV2: every send point follows a file edit or a commit already in the flow (reviewer: no break).
- IV3: `_principles.md` item 2 "Never the own name"; the own-name line is excluded from the `ListAgents` peer rows.
- IV4: CK4, the procedure lives only in `_principles.md`.
- IV5: item 4 "No wait"; no send point adds a question.

### Assumptions check
- AS1: held in part; the own name stayed the same across this session; a resume getting a new name is unverified until the live run.
- AS2: unverifiable here; no message to a busy peer was observed this session.

### Unknowns outcome
- UK1: still-open; both 2026-11-16 notices reported delivery to the inbox, and whether a peer holds them for the owner shows in the live run.
- UK2: still-open; needs a worktree or branch task resumed in a second session.

Review findings:
- Text fixes: 3 applied (receiver ignores a notice for a task it is not working on, the receiver's automatic summary appends included, in-flight set points to `/up:make` step 2); 1 recorded in `## Code smells`.

Verified by: owner offered the optional requirements review (`up:requirements-reviewer`) at step 12.

### Deviations from plan
- PH2 2.3/2.6: the set of sessions to notify ("repo peers") is defined once in `_principles.md` → Notify a running session, item 2, not in `make.md` step 12: step 6's `git switch` notice needs it too, and step 6 comes before step 12 (GPC8).
- PH2 2.6: the `git switch` notice text lives once in `make.md` step 6 ("After a `git switch`"); step 2 and "Leaving a plain branch" point to it.

### Handoff: 2026-11-16
- Position: design written, waiting for the owner's design approval; branch: main; committed: 7217239 (implementer on sonnet, 0.3.58); uncommitted: none after this commit
- Decided: rule + pack (owner's pick in the /doctor run), because the global rule alone has no address for the peer session
- Decided: approach A (Session header + one home in _principles.md + three send points); B (broadcast) and C (hook) rejected, see Design
- Open: owner approval of ## Design
- Owner has not seen: none
- First action: on approval, run up:uplan on this file

### Handoff: 2026-11-16 (plan)
- Position: plan written, waiting for the owner's plan approval; branch: main; committed: 39f1f59 (design); uncommitted: none after this commit
- Decided: owner approved ## Design ("yes, do it")
- Decided: plan review round 1 added the send point for tasks on main (step 12 offers no merge there); round 2 added the git-switch send point and the summary.md side-effect lines
- Open: owner approval of ## Plan
- Owner has not seen: none
- First action: on approval, Status executing, run up:uexecute (PH1 then PH2)

### Handoff: 2026-11-16 (execute)
- Position: PH1 and PH2 committed, verify next; branch: main; committed: 4a381e3 (PH2, 0.3.59); uncommitted: none after this commit
- Decided: owner approved ## Plan ("yes, do it")
- Owner has not seen: none
- First action: run up:uverify on this file

### Handoff: 2026-11-16 (validating)
- Position: verified, reviewed, Status validating; branch: main; committed: review text fixes (0.3.61); uncommitted: none after this commit
- Decided: verify run 1 broke on the `[ref]` suffix of the own name, fixed in caf5542; final review 0 Critical/Important, 3 text fixes applied
- Open: none
- Owner has not seen: none
- First action: in a live run with two sessions open, resume or finish a task in one and check the other receives the notice; then set Status done
