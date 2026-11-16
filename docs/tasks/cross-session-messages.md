# Cross-session messages

**Status:** design
**Branch:** main
**Session:** ultrapack-dzm-ce
**Goal:** When a /up:make session changes something another running session depends on (that session's task file, a merge into main under it, a worktree exit that copies a task file into main), it sends that session a SendMessage naming what changed and what to re-read; when no such session is running it writes the task file as today. Confirming it needs one live run with two sessions open.

## Owner summary
- Done: the design is written: each task file records which session works on it, and the pack sends that session a message when another session changes its file or merges into main.
- Left: plan, the edits to three pack files, a live check with two sessions open.
- Owner decides: approve the design.

## Design

Owner ask, 2026-11-16 (translated): "if one session writes or does something that changes another session's context, it uses inter-session messages for that." The global rule now sits in `~/.claude/CLAUDE.md` (Agent behavior). This task makes `/up:make` follow it at the points where the pack itself changes another session's context, and gives the sender an address.

Audit (2026-11-16): 0 pack lines mention `SendMessage` or `ListAgents`; 2 `SendMessage` calls in 40 recent sessions; task files edited by up to 6 sessions each (cccc `instant-optouts-removal.md`). `ListAgents` lists peers by a directory-based name (`cccc-monorepo-b9`), with no task, so today a session cannot tell which peer owns which task.

Chosen approach (A):

1. **Address.** Task files gain a `**Session:** <name>` header: this session's own name, read from the `ListAgents` line "This session is <name>". `/up:make` writes it at create (step 3) and rewrites it at every resume (step 2), because a resumed task runs in a new session with a new name. The header rides the next task-file commit; no separate commit.
2. **One home.** `_principles.md` gets a `## Notify a running session` section: how to find the peer (header name → bare-name match in `ListAgents`, never this session's own name), the message shape (English; first line self-contained: what changed and where; then what to re-read), fire-and-forget (no wait for a reply, no new pause), the fallback (peer not listed → the file or git change stands alone, as today), and the permission-laundering ban (never ask a peer to do what this session's permissions blocked). Callers only point here.
3. **Three send points**, each pointing to the section:
   - `/up:summary` step 3, after the commit: the active task file's `**Session:**` names another session that is running (a manual summary picked up another session's task file, or a resume while the old session is still open) → notify it.
   - `/up:make` step 2, resume: the header names another session that is still running → tell the owner in one line and notify that session that this one now owns the task; then rewrite the header. No question.
   - `/up:make` step 12, after a merge into `main` or the finish push, and "Leaving a worktree" step 4 (the task file copied into `main`, including the "pull fails" case): notify every running session named in the `**Session:**` header of another in-flight task file in this repo (Status not `done` / `shipped` / `reference`): what landed on `main`, which files, "pull before your next commit".
4. Template line in step 3: `**Session:** <this session's name from ListAgents; rewritten on each resume>`.

Rejected:
- B, broadcast without a header: message every `ListAgents` peer whose name starts with the repo folder name. No header change, but worktree folders have other names, peers from other repos with similar names get noise, and every message costs the receiver context.
- C, a hook that sends on each task-file edit: hooks cannot call `SendMessage`, and the pack is doc-only.

Out of scope: per-phase pushes to `main` during execute (one message per commit is noise; the finish notice covers the end state); pack version bumps (the global rule covers a skill a session loaded); Jira writes by `up:ujira`.

Backwards compatibility: no break. A task file without `**Session:**` resumes and finishes as today; the header is written at its next resume. `/up:make` step 2 already ignores header fields it does not recognize, and `up:uexecute` compares only `**Branch:**`.
TDD: no (reason: doc-only pack, no runtime code; verification is install-and-invoke)
Reviewed before code: not run (design point without a Large signal), 2026-11-16

### Prior art
- `docs/tasks/branch-by-reason.md:176`: a shared checkout sees another session only by edits or commits it already made; a parallel session that has not edited anything is invisible. The header plus `ListAgents` closes this for `/up:make` sessions.
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
- UK2: In a worktree task, the `main` copy's header is frozen at entry, so a later resume's name reaches `main` only at exit; whether this misses a real send in practice.

## Plan
<empty: filled by up:uplan; gains ### Rollout / ### Rollback when the change ships to a live system>

## Verify
<empty: filled by up:uverify>

## Code smells
<empty: `- <file:line>: <one-line smell>` lines passed while exploring and left unfixed (out of scope, non-trivial); deleted if none>

## Conclusion
<empty: filled by up:ureview; after done/shipped grows dated ### Follow-up: <date> / ### Scope change: <date> entries and ### Deferred scope-parking>

### Handoff: 2026-11-16
- Position: design written, waiting for the owner's design approval; branch: main; committed: 7217239 (implementer on sonnet, 0.3.58); uncommitted: none after this commit
- Decided: rule + pack (owner's pick in the /doctor run), because the global rule alone has no address for the peer session
- Decided: approach A (Session header + one home in _principles.md + three send points); B (broadcast) and C (hook) rejected, see Design
- Open: owner approval of ## Design
- Owner has not seen: none
- First action: on approval, run up:uplan on this file
